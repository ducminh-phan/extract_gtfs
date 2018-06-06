from merge_graph.nearby_nodes import find_nearby_nodes
from merge_graph.settings import setup
from merge_graph.utils import parse_args


def main():
    args = parse_args()

    setup()

    find_nearby_nodes(args)
