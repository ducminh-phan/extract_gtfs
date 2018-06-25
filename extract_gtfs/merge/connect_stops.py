import pandas as pd
from tqdm import tqdm

from extract_gtfs.config import config
from extract_gtfs.data import Data


class MergeGraph:
    __slots__ = ('merge_labels',)

    @classmethod
    def connect_nodes(cls):
        print('\nConnecting stops to the nearby nodes...')

        nearby_nodes = pd.read_csv('{}/nearby_nodes.csv'.format(config.tmp_folder), header=None)

        # Each row in nearby_nodes is an edge (stop_id, node_id, weight),
        # here we create the edges in the reverse direction with the same weight
        # by swapping the first two columns
        reverse_edges = nearby_nodes.copy()
        reverse_edges[[0, 1]] = reverse_edges[[1, 0]]

        edges_df = Data.edges

        # Appending the new edges into the graph, we need to rename the columns
        # to have the same columns in all DataFrames
        for df in (nearby_nodes, reverse_edges):
            edges_df = edges_df.append(df.rename(columns={0: 'source', 1: 'target', 2: 'weight'}))

        Data.edges = edges_df

    @classmethod
    def identify_nodes(cls):
        print('\nMerging stops to proximate nodes...')

        edges_df = Data.edges
        identical_nodes = pd.read_csv('{}/identical_nodes.csv'.format(config.tmp_folder), header=None)

        # stop -> node to merge
        merge_labels = dict(zip(identical_nodes[0], identical_nodes[1]))
        nodes = set(merge_labels.values())

        for node in tqdm(nodes):
            # Extract the edges incident to the current node and their indices
            extracted = edges_df[(edges_df['source'] == node) | (edges_df['target'] == node)]
            idx = extracted.index

            # Get the list of stops that node is mapped to
            s = list(x for x in merge_labels.keys() if merge_labels[x] == node)

            # Remove extracted from the original df
            # Currently, there is a bug with drop when the index is not unique and idx is empty
            # https://github.com/pandas-dev/pandas/issues/21494
            # Thus we need to explicitly check if idx is not empty
            if len(idx):
                edges_df = edges_df.drop(idx)

            # Add mapped edges
            for si in s:
                tmp = extracted.replace({'source': {node: si}, 'target': {node: si}})
                edges_df = edges_df.append(tmp, ignore_index=True)

        Data.edges = edges_df
        cls.merge_labels = merge_labels

    @classmethod
    def merge_nodes(cls):
        print('\nAdding the stops to the list of nodes in the graph...')

        nodes_df = Data.nodes

        # Remove the merged nodes
        nodes_df = nodes_df[~nodes_df['id'].isin(cls.merge_labels.values())]

        Data.nodes = Data.stops.append(nodes_df)

    @classmethod
    def merge(cls):
        cls.connect_nodes()
        cls.identify_nodes()
        cls.merge_nodes()
