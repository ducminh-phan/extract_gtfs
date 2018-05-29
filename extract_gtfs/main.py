import os

from .collect_routes import CollectRoute
from .data import setup, Data
from .extract_dates import ExtractDate
from .relabel import Relabel
from .split_trips import SplitTrip
from .transfers import ExtractTransfer
from .utils import parse_args


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
