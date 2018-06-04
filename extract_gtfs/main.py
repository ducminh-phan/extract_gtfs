import os
import shutil

import pandas as pd

from extract_gtfs.collect_routes import CollectRoute
from extract_gtfs.data import setup, Data
from extract_gtfs.extract_dates import ExtractDate
from extract_gtfs.relabel import Relabel
from extract_gtfs.split_trips import SplitTrip
from extract_gtfs.transfers import ExtractTransfer
from extract_gtfs.utils import parse_args, measure_time, query_yes_no
from extract_gtfs.walking_graph import ExtractCoordinates


def main():
    args = parse_args()
    setup(args)

    extract(args)
    summary()
    clean_up(args)


@measure_time
def extract(args):
    ExtractDate.extract()
    SplitTrip.split()
    ExtractTransfer.extract()
    CollectRoute.collect()
    ExtractCoordinates.extract()

    if args.relabel:
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

    ExtractCoordinates.write_table(Data.out_folder)


def summary():
    n_trips = len(Data.trips['trip_id'].unique())
    n_routes = len(Data.trips['route_id'].unique())
    n_events = len(Data.stop_times)
    n_stops = len(Data.stop_times['stop_id'].unique())
    n_transfers = len(Data.transfers)

    print('Summary:')
    print('\t{} routes'.format(n_routes))
    print('\t{} trips'.format(n_trips))
    print('\t{} stops'.format(n_stops))
    print('\t{} events'.format(n_events))
    print('\t{} transfers'.format(n_transfers))

    print('-' * 50)


def clean_up(args):
    if query_yes_no('Delete the temporary files?'):
        shutil.rmtree('{}_tmp'.format(Data.in_folder))

    if args.relabel and query_yes_no('Save the labels?'):
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
