import os
import shutil
from glob import glob

import networkx as nx
import pandas as pd

from merge_graph.connect_stops import MergeGraph
from merge_graph.nearby_nodes import find_nearby_nodes
from merge_graph.relabel import Relabel
from merge_graph.settings import setup, config, data
from merge_graph.utils import parse_args, write_data_files, query_yes_no


def main():
    args = parse_args()

    setup()
    read_data(args)

    Relabel.relabel(args)
    find_nearby_nodes(args)
    MergeGraph.merge()

    stats()
    write_data_files()
    clean_up()


def read_data(args):
    from merge_graph.utils import read_co_file, read_gr_file

    nodes_co = read_co_file(args.nodes_file)
    nodes_gr = read_gr_file(args.graph_file)

    # Filter the coordinates to keep only the nodes appear in the graph
    nodes = set(nodes_gr['source']) | set(nodes_gr['target'])
    nodes_co = nodes_co[nodes_co['node_id'].isin(nodes)]

    # Remove self-loops
    nodes_gr = nodes_gr[nodes_gr['source'] != nodes_gr['target']]

    # Remove duplicated edges
    nodes_gr = nodes_gr.drop_duplicates(subset=['source', 'target'], keep='last')

    data.nodes_co = nodes_co
    data.nodes_gr = nodes_gr


def stats():
    g = nx.from_pandas_edgelist(data.nodes_gr, create_using=nx.DiGraph())

    with open('{}/isolated_stops.csv'.format(config.tmp_folder), 'r') as f:
        num_isolated_stops = 0
        for num_isolated_stops, _ in enumerate(f, 1):
            pass

    print()

    print('Statistics of the walking graph after merging:')
    print('\t', len(g.nodes), 'nodes')
    print('\t', len(g.edges), 'edges')
    print('\t', num_isolated_stops, 'isolated stops (not connected to the walking graph)')
    print('\t', nx.number_strongly_connected_components(g), 'strongly connected components')

    cc_sizes = sorted(map(len, nx.strongly_connected_components(g)), reverse=True)[:10]
    print('\t', 'The size of {} largest components: {}'.format(
        len(cc_sizes), ' '.join(map(str, cc_sizes))
    ))

    print()


def clean_up():
    # Remove the compiled C++ executable
    file_paths = glob('./close_nodes*')

    for file_path in file_paths:
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            os.remove(file_path)

    # Write the labels
    pd.DataFrame(sorted(Relabel.label.items(), key=lambda x: x[1])).to_csv(
        '{}/label.csv'.format(config.out_folder), index=False, header=['old_id', 'new_id']
    )

    if query_yes_no('Delete the temporary files?'):
        shutil.rmtree(config.tmp_folder)
