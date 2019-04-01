from extract_gtfs.config import config
from extract_gtfs.data import Data, stats
from extract_gtfs.extract.collect_routes import CollectRoute
from extract_gtfs.extract.extract_dates import ExtractDate
from extract_gtfs.extract.relabel import Relabel
from extract_gtfs.extract.split_trips import SplitTrip
from extract_gtfs.extract.stops import ExtractCoordinates
from extract_gtfs.extract.transfers import ExtractTransfer
from extract_gtfs.utils import measure_time, write_co_file


def extract(args):
    _extract(args)
    summary()


@measure_time
def _extract(args):
    ExtractDate.extract()
    SplitTrip.split()
    ExtractTransfer.extract()
    CollectRoute.collect()
    ExtractCoordinates.extract()

    if args.relabel:
        Relabel.create_label()
        Relabel.relabel()

    write_co_file(Data.stops, config.stops_file)


def summary():
    stats.n_trips = len(Data.trips["trip_id"].unique())
    stats.n_routes = len(Data.trips["route_id"].unique())
    stats.n_events = len(Data.stop_times)
    stats.n_stops = len(Data.stop_times["stop_id"].unique())
    stats.n_transfers = len(Data.transfers)
