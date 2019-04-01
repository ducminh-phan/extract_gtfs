from collections import defaultdict

from tqdm import tqdm

from extract_gtfs.data import Data
from extract_gtfs.utils import LogAttribute, load_attr, read_csv


def hms_to_s(s):
    """
    Convert the time formatting from a string of the form "hh:mm:ss"
    to an integer representing the number of seconds counting from 00:00:00
    """
    h, m, s = list(map(int, s.split(":")))
    return 3600 * h + 60 * m + s


class SplitTrip(metaclass=LogAttribute):
    __slots__ = (
        "stop_times_grouped",
        "trip_groups_by_pattern",
        "trip_groups_sorted",
        "trip_to_deps",
        "trip_groups",
    )

    @classmethod
    @load_attr({Data: "stop_times"})
    def extract_stop_times(cls):
        print("\nExtracting the selected date from the timetable...")

        stop_times_df = read_csv(
            "stop_times.txt",
            usecols=[
                "trip_id",
                "arrival_time",
                "departure_time",
                "stop_id",
                "stop_sequence",
            ],
            dtype={
                "trip_id": str,
                "arrival_time": str,
                "departure_time": str,
                "stop_id": str,
                "stop_sequence": int,
            },
        )

        # Keep only the events associating with the selected trips
        stop_times_filtered = stop_times_df[
            stop_times_df["trip_id"].isin(Data.selected_trips)
        ]

        # Remove events containing NaN
        stop_times_filtered = stop_times_filtered.dropna()

        # Sort by stop_sequence to make sure the stop sequences are in correct order
        stop_times_filtered = stop_times_filtered.sort_values(
            by=["trip_id", "stop_sequence"]
        )

        # Convert the time format
        stop_times_filtered["arrival_time"] = stop_times_filtered["arrival_time"].apply(
            hms_to_s
        )
        stop_times_filtered["departure_time"] = stop_times_filtered[
            "departure_time"
        ].apply(hms_to_s)

        Data.stop_times = stop_times_filtered

    @classmethod
    @load_attr("stop_times_grouped", "trip_groups_by_pattern")
    def split_by_pattern(cls):
        print("\nCollecting the stop patterns...")

        cls.stop_times_grouped = Data.stop_times.groupby("trip_id")
        pattern_to_trips = defaultdict(list)

        for trip, group in tqdm(cls.stop_times_grouped):
            stop_pattern = tuple(group["stop_id"])
            pattern_to_trips[stop_pattern].append(trip)

        cls.trip_groups_by_pattern = list(pattern_to_trips.values())

    @classmethod
    @load_attr("trip_to_deps", "trip_groups_sorted")
    def sort_trip(cls):
        print("\nGetting the departure times for every trip...")

        cls.trip_to_deps = {
            trip: group["departure_time"].tolist()
            for trip, group in tqdm(cls.stop_times_grouped)
        }

        print(
            "\nSorting the trips in each stop pattern "
            "by the departure time at the first stop..."
        )

        cls.trip_groups_sorted = [
            sorted(gr, key=lambda t: cls.trip_to_deps[t][0])
            for gr in tqdm(cls.trip_groups_by_pattern)
        ]

    @classmethod
    @load_attr("trip_groups")
    def split_by_time(cls):
        """
        In each trip group, the following two conditions need to be satisfied:
        1. Every trip having the same stop pattern, this is already guaranteed
           by the classmethod split_by_pattern
        2. Every column of the timetable belonging to the route (trip group) are in
           ascending order.

        This classmethod splits each group in cls.trip_groups_sorted, if necessary,
        into smaller groups to guarantee the second condition.
        """
        print("\nCollecting the trips preserving the stop times order...")

        # The final trip groups, for which the two conditions above are guaranteed
        trip_groups = []

        for trip_group in tqdm(cls.trip_groups_sorted):
            current_groups = []

            for trip in trip_group:
                # Check if we can insert this trip into one of the current groups
                for group in current_groups:
                    # Get the last trip in this group
                    last_trip = group[-1]

                    # Add this trip to this group if all the departure times are at least
                    # those of the last trip in this group, element-wise
                    if all(
                        last_dep <= dep
                        for last_dep, dep in zip(
                            cls.trip_to_deps[last_trip], cls.trip_to_deps[trip]
                        )
                    ):
                        group.append(trip)
                        break
                else:
                    # This trip cannot be added to any of the current groups,
                    # we need to create a new group
                    current_groups.append([trip])

            trip_groups.extend(current_groups)

        cls.trip_groups = trip_groups

    @classmethod
    def split(cls):
        cls.extract_stop_times()

        cls.split_by_pattern()
        cls.sort_trip()
        cls.split_by_time()
