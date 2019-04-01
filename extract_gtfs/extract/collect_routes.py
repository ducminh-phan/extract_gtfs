from collections import defaultdict

import pandas as pd
from tqdm import tqdm

from extract_gtfs.data import Data
from extract_gtfs.extract.split_trips import SplitTrip
from extract_gtfs.utils import LogAttribute, load_attr


class CollectRoute(metaclass=LogAttribute):
    __slots__ = ("trip_to_route",)

    @classmethod
    @load_attr({Data: "trips", None: "trip_to_route"})
    def collect_trips(cls):
        print("\nAssigning a route id to each of the trip groups...")

        trips = []
        trip_to_route = {}

        for idx, trip_group in enumerate(SplitTrip.trip_groups):
            for trip in trip_group:
                trips.append([idx, trip])
                trip_to_route[trip] = idx

        Data.trips = pd.DataFrame(trips, columns=["route_id", "trip_id"])
        cls.trip_to_route = trip_to_route

    @classmethod
    @load_attr({Data: "stop_routes"})
    def collect_stop_routes(cls):
        stop_times_grouped = Data.stop_times.groupby("stop_id")

        print("\nFinding the routes serving each stop...")

        # Map each stops to the set of routes it serves
        stop_routes = defaultdict(set)

        for stop, group in tqdm(stop_times_grouped):
            serving_trips = group["trip_id"].unique()

            for trip in serving_trips:
                route = cls.trip_to_route[trip]
                stop_routes[stop].add(route)

        # Convert the dict (stop_id -> set of routes) to a DataFrame
        Data.stop_routes = pd.DataFrame(
            [[k, vi] for k, v in stop_routes.items() for vi in v],
            columns=["stop_id", "route_id"],
        )

    @classmethod
    def collect(cls):
        cls.collect_trips()
        cls.collect_stop_routes()
