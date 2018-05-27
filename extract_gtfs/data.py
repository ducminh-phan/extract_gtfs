import pandas as pd

from .utils import measure_time, LogAttribute


class Data(metaclass=LogAttribute):
    __slots__ = ('in_folder', 'out_folder',
                 'dates', 'date_to_trips',
                 'calendar_dates_df', 'trips_df',
                 'stop_times')


@measure_time
def setup(args):
    print("Reading the GTFS files...")
    Data.in_folder = args.folder
    Data.out_folder = args.output

    Data.calendar_dates_df = pd.read_csv('{}/calendar_dates.txt'.format(Data.in_folder), dtype=str,
                                         usecols=['service_id', 'date'])

    Data.trips_df = pd.read_csv('{}/trips.txt'.format(Data.in_folder), dtype=str,
                                usecols=['service_id', 'trip_id'])
