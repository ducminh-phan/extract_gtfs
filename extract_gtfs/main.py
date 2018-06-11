import argparse
import glob
import os
import shutil

import pandas as pd

from extract_gtfs.config import config, setup as config_setup
from extract_gtfs.data import Data, labels
from extract_gtfs.extract import extract
from extract_gtfs.merge import merge
from extract_gtfs.utils import SaveLoadDescriptor, query_yes_no, write_graph_files


def parse_args():
    parser = argparse.ArgumentParser(prog="python3 -m extract_gtfs",
                                     description="Extract information from GTFS files "
                                                 "to use with RAPTOR algorithm")

    parser.add_argument("in_folder", help="The folder containing the GTFS files to extract")
    parser.add_argument("out_folder", help="The folder to write the outout files")
    parser.add_argument("nodes_file", help="The file containing the coordinates of the nodes "
                                           "of the walking graph")
    parser.add_argument('graph_file', help="The file containing the edges of the walking graph")
    parser.add_argument('--no-relabel', dest='relabel', action='store_false',
                        help="Do not relabel the stops and trips.")

    args = parser.parse_args()
    args = check_args(parser, args)

    return args


def check_args(parser, args):
    if args.out_folder == args.in_folder:
        parser.error("The input and output folders' names must be different")

    return args


def setup(args):
    config_setup(args)

    SaveLoadDescriptor.directory = config.tmp_folder


def write_files():
    print('\nWriting the output files...')

    for attr in ('stop_times', 'transfers', 'trips', 'stop_routes'):
        df = getattr(Data, attr)
        df.to_csv('{}/{}.csv.gz'.format(config.out_folder, attr), index=False, compression='gzip')

    write_graph_files()


def clean_up(args):
    # Remove the compiled C++ executable
    file_paths = glob.glob('./close_nodes*')

    for file_path in file_paths:
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            os.remove(file_path)

    if query_yes_no('Delete the temporary files?'):
        shutil.rmtree(config.tmp_folder)

    if args.relabel and query_yes_no('Save the labels?'):
        if not os.path.exists(config.labels_folder):
            os.makedirs(config.labels_folder)

        # Create the DataFrames for the labels, sorted by the newly assigned labels,
        # then save them to the label folder
        pd.DataFrame(sorted(labels.trip_label.items(), key=lambda x: x[1])).to_csv(
            '{}/trip_label.csv'.format(config.labels_folder), index=False, header=['old_id', 'new_id']
        )
        pd.DataFrame(sorted(labels.stop_label.items(), key=lambda x: x[1])).to_csv(
            '{}/stop_label.csv'.format(config.labels_folder), index=False, header=['old_id', 'new_id']
        )
        pd.DataFrame(sorted(labels.node_label.items(), key=lambda x: x[1])).to_csv(
            '{}/node_label.csv'.format(config.labels_folder), index=False, header=['old_id', 'new_id']
        )


def main():
    args = parse_args()
    setup(args)

    extract(args)
    merge(args)

    write_files()
    clean_up(args)
