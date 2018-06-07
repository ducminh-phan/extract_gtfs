import os
import shutil
from glob import glob

from merge_graph.connect_stops import MergeGraph
from merge_graph.nearby_nodes import find_nearby_nodes
from merge_graph.relabel import Relabel
from merge_graph.settings import setup, config
from merge_graph.utils import parse_args, write_data_files, query_yes_no


def main():
    args = parse_args()

    setup()

    Relabel.relabel(args)
    find_nearby_nodes(args)
    MergeGraph.merge()

    write_data_files()
    clean_up()


def clean_up():
    # Remove the compiled C++ executable
    file_paths = glob('./close_nodes*')

    for file_path in file_paths:
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            os.remove(file_path)

    print()
    if query_yes_no('Delete the temporary files?'):
        shutil.rmtree(config.tmp_folder)
