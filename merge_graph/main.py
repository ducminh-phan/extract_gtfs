import os

from merge_graph.close_nodes import find_close_nodes
from merge_graph.utils import parse_args


def main():
    args = parse_args()

    setup()

    find_close_nodes(args)


def setup():
    if not os.path.exists('merge_graph_tmp'):
        os.makedirs('merge_graph_tmp')
