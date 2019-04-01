from collections import defaultdict
from datetime import date, timedelta

from tqdm import tqdm, trange

from extract_gtfs.data import Data
from extract_gtfs.utils import LogAttribute, load_attr, read_csv

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def str_to_date(date_string):
    """
    Convert string storing the date in calendar_dates to a date object
    """
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:])

    return date(year, month, day)


def date_to_str(date_obj):
    """
    Convert a date object to the string form used in GTFS files.

    >>> date_to_str(date(2018, 8, 25))
    '20180825'

    It is the inverse of the str_to_date function.

    >>> date_to_str(str_to_date("20180825"))
    '20180825'

    >>> str_to_date(date_to_str(date(2018, 8, 25)))
    datetime.date(2018, 8, 25)
    """
    return "{0.year}{0.month:0>2}{0.day:0>2}".format(date_obj)


class ExtractDate(metaclass=LogAttribute):
    __slots__ = (
        "calendar_df",
        "calendar_dates_df",
        "trips_df",
        "start_date_str",
        "end_date_str",
        "date_to_services",
        "date_to_trips",
    )

    @classmethod
    def setup(cls):
        print("Reading the GTFS files...")

        cls.calendar_df = read_csv("calendar.txt", dtype=str)

        # Convert the day columns from str to int
        cls.calendar_df[DAYS] = cls.calendar_df[DAYS].applymap(int)

        try:
            cls.calendar_dates_df = read_csv(
                "calendar_dates.txt",
                dtype={"service_id": str, "date": str, "exception_type": int},
            )
        except FileNotFoundError:
            # We need to check if the optional calendar_dates.txt file does not exist
            cls.calendar_dates_df = None

        cls.trips_df = read_csv(
            "trips.txt", dtype=str, usecols=["service_id", "trip_id"]
        )

    @classmethod
    @load_attr("start_date_str", "end_date_str")
    def find_date_range(cls):
        print("\nFinding the date range of the timetable...")

        # The date strings are in the format YYMMDD, so we can compare the actual dates
        # by simply comparing the strings
        cls.start_date_str = min(cls.calendar_df["start_date"])
        cls.end_date_str = max(cls.calendar_df["end_date"])

        if cls.calendar_dates_df is not None:
            cls.start_date_str = min(
                cls.start_date_str, min(cls.calendar_dates_df["date"])
            )
            cls.end_date_str = max(cls.end_date_str, max(cls.calendar_dates_df["date"]))

    @classmethod
    @load_attr("date_to_services")
    def get_services_by_date(cls):
        print("\nFinding the services available for each day...")

        start_date = str_to_date(cls.start_date_str)
        end_date = str_to_date(cls.end_date_str)

        # Remove all zeros services for faster iteration
        # calendar_df = cls.calendar_df[(cls.calendar_df[DAYS] != 0).any(axis=1)]
        calendar_df = cls.calendar_df

        d2s = defaultdict(set)

        # Iterate over the first 7 dates in the timetable and search in the calendar_df
        # to look for available services
        for d in trange(7):
            current_date = start_date + timedelta(d)
            weekday_idx = current_date.weekday()
            weekday_str = DAYS[weekday_idx]

            # Get the availabe services for this weekday
            services_set = set(calendar_df[calendar_df[weekday_str] == 1]["service_id"])

            # Skip to the next day if there is no service for this day
            if not services_set:
                continue

            # The data from calendar_df is periodic over the course of a week,
            # thus we add a timedelta of 7 days to add the available services
            # to the same day in the next week
            while True:
                current_date_str = date_to_str(current_date)
                d2s[current_date_str] = services_set

                current_date += timedelta(7)
                if current_date > end_date:
                    break

        # Modify the available services with the exceptions from calendar_dates
        if cls.calendar_dates_df is not None:
            date_groups = cls.calendar_dates_df.groupby("date")
            for date_str in tqdm(cls.calendar_dates_df["date"].unique()):
                df = date_groups.get_group(date_str)

                # From the GTFS reference, for the field exception_type,
                # a value of 1 indicates that service has been added for the specified date
                # a value of 2 indicates that service has been removed for the specified date
                # Reference: https://developers.google.com/transit/gtfs/reference/#calendar_datestxt
                services_to_add = set(df[df["exception_type"] == 1]["service_id"])
                services_to_remove = set(df[df["exception_type"] == 2]["service_id"])

                d2s[date_str] |= services_to_add
                d2s[date_str] -= services_to_remove

        cls.date_to_services = d2s

    @classmethod
    @load_attr("date_to_trips")
    def get_trips_by_date(cls):
        print("\nFinding the trips available for each day...")

        d2t = {}
        service_groups = cls.trips_df.groupby("service_id")
        for date_str, services in tqdm(cls.date_to_services.items()):
            trips_set = set()
            for service in services:
                try:
                    df = service_groups.get_group(service)
                    trips_set |= set(df["trip_id"])
                except KeyError:
                    # service is obtained from calendar.txt and calendar_dates.txt,
                    # but there is no trip with such service_id in trips.txt
                    pass

            d2t[date_str] = trips_set

        cls.date_to_trips = d2t

    @classmethod
    @load_attr({Data: ["selected_date", "selected_trips"]})
    def extract(cls):
        cls.setup()
        cls.find_date_range()
        cls.get_services_by_date()
        cls.get_trips_by_date()

        print("\nFinding the busiest day in the timetable...")

        # Iterate over the tuples (date, trips) and find the trips set of max size
        selected_date, trips = max(cls.date_to_trips.items(), key=lambda x: len(x[1]))

        Data.selected_date = selected_date
        Data.selected_trips = trips
