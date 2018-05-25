import pandas as pd


class Data:
    __slots__ = ('in_folder', 'out_folder',
                 'calendar_dates_df', 'trips_df')


def setup(args):
    print("Reading the GTFS files...")
    Data.in_folder = args.folder
    Data.out_folder = args.output

    calendar_dates_df = pd.read_csv('{}/calendar_dates.txt'.format(Data.in_folder))
    calendar_dates_df = calendar_dates_df.drop(['exception_type'], axis=1)
    Data.calendar_dates_df = calendar_dates_df

    trips_df = pd.read_csv('{}/trips.txt'.format(Data.in_folder))
    trips_df = trips_df.drop(['trip_headsign', 'trip_short_name', 'direction_id', 'shape_id'], axis=1)
    Data.trips_df = trips_df
