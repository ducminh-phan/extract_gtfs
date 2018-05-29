import os

from .collect_routes import CollectRoute
from .data import setup, Data
from .extract_dates import ExtractDate
from .relabel import Relabel
from .split_trips import SplitTrip
from .transfers import ExtractTransfer
from .utils import parse_args, measure_time


@measure_time
def main():
    args = parse_args()
    setup(args)

    ExtractDate.extract()
    SplitTrip.split()
    ExtractTransfer.extract()
    CollectRoute.collect()
    Relabel.create_label()
    Relabel.relabel()

    write_files()


def write_files():
    # Create the folder containing the output files
    if not os.path.exists(Data.out_folder):
        os.makedirs(Data.out_folder)

    print('\nWriting the output files...')

    for attr in ('stop_times', 'transfers', 'trips', 'stop_routes'):
        df = getattr(Data, attr)
        df.to_csv('{}/{}.csv.gz'.format(Data.out_folder, attr), index=False, compression='gzip')


def summary():
    print('Summary:')
    print('\t{} routes'.format(Data.stats['n_routes']))
    print('\t{} trips'.format(Data.stats['n_trips']))
    print('\t{} stops'.format(Data.stats['n_stops']))
    print('\t{} events'.format(Data.stats['n_events']))
    print('\t{} transfers'.format(Data.stats['n_transfers']))

    print('-' * 50)
