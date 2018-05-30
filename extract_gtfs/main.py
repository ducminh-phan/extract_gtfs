import os
import shutil

import pandas as pd

from .collect_routes import CollectRoute
from .data import setup, Data
from .extract_dates import ExtractDate
from .relabel import Relabel
from .split_trips import SplitTrip
from .transfers import ExtractTransfer
from .utils import parse_args, measure_time, query_yes_no


def main():
    extract()
    summary()
    clean_up()


@measure_time
def extract():
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


def clean_up():
    if query_yes_no('Delete the temporary files?'):
        shutil.rmtree('{}_tmp'.format(Data.in_folder))

    if query_yes_no('Save the labels?'):
        directory = '{}_labels'.format(Data.in_folder)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create the DataFrames for the labels, sorted by the newly assigned labels,
        # then save them to the label folder
        pd.DataFrame(sorted(Relabel.trip_label.items(), key=lambda x: x[1])).to_csv(
            '{}/trip_label.csv'.format(directory), index=False, header=['old_id', 'new_id']
        )
        pd.DataFrame(sorted(Relabel.stop_label.items(), key=lambda x: x[1])).to_csv(
            '{}/stop_label.csv'.format(directory), index=False, header=['old_id', 'new_id']
        )
