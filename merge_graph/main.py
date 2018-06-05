from merge_graph.close_nodes import find_close_nodes
from merge_graph.utils import parse_args


def main():
    args = parse_args()

    find_close_nodes(args)
