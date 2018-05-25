import pandas as pd


class Data:
    __slots__ = ('in_folder', 'out_folder',
                 'calendar_dates_df', 'trips_df')


def setup(args):
    Data.in_folder = args.folder
    Data.out_folder = args.output

    Data.calendar_dates_df = pd.read_csv('{}/calendar_dates.txt'.format(Data.in_folder))
    Data.trips_df = pd.read_csv('{}/trips.txt'.format(Data.in_folder))
