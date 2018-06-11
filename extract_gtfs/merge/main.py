import networkx as nx

from extract_gtfs.config import config
from extract_gtfs.data import Data, stats
from extract_gtfs.merge.connect_stops import MergeGraph
from extract_gtfs.merge.nearby_nodes import find_nearby_nodes
from extract_gtfs.merge.relabel import Relabel


def merge(args):
    read_graph(args)

    Relabel.relabel()
    find_nearby_nodes()
    MergeGraph.merge()

    summary()


def read_graph(args):
    from extract_gtfs.utils import read_co_file, read_gr_file

    nodes_df = read_co_file(args.nodes_file)
    edges_df = read_gr_file(args.graph_file)

    # Filter the coordinates to keep only the nodes appear in the graph
    nodes = set(edges_df['source']) | set(edges_df['target'])
    nodes_df = nodes_df[nodes_df['id'].isin(nodes)]

    # Remove self-loops
    edges_df = edges_df[edges_df['source'] != edges_df['target']]

    # Remove duplicated edges
    edges_df = edges_df.drop_duplicates(subset=['source', 'target'], keep='last')

    Data.nodes = nodes_df
    Data.edges = edges_df


def summary():
    g = nx.from_pandas_edgelist(Data.edges, create_using=nx.DiGraph())

    with open('{}/isolated_stops.csv'.format(config.tmp_folder), 'r') as f:
        num_isolated_stops = 0
        for num_isolated_stops, _ in enumerate(f, 1):
            pass

    stats.n_nodes = len(g.nodes)
    stats.n_edges = len(g.edges)
    stats.n_isolated_stops = num_isolated_stops
    stats.n_scc = nx.number_strongly_connected_components(g)
    stats.cc_sizes = sorted(map(len, nx.strongly_connected_components(g)), reverse=True)[:10]
