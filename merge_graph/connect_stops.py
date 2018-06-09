import pandas as pd

from merge_graph.settings import config, data


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

        nodes_gr = data.nodes_gr

        # Appending the new edges into the graph, we need to rename the columns
        # to have the same columns in all DataFrames
        for df in (nearby_nodes, reverse_edges):
            nodes_gr = nodes_gr.append(df.rename(columns={0: 'source', 1: 'target', 2: 'weight'}))

        data.nodes_gr = nodes_gr

    @classmethod
    def identify_nodes(cls):
        print('\nMerging stops to proximate nodes...')

        nodes_gr = data.nodes_gr
        identical_nodes = pd.read_csv('{}/identical_nodes.csv'.format(config.tmp_folder), header=None)

        # stop -> node to merge
        merge_labels = dict(zip(identical_nodes[0], identical_nodes[1]))
        nodes = set(merge_labels.values())

        # A temporary DataFrame holding the edges between a stop and neighbors of the node to merge
        tmp_df = pd.DataFrame([])

        for node in nodes:
            # Extract the edges incident to the current node and their indices
            extracted = nodes_gr[(nodes_gr['source'] == node) | (nodes_gr['target'] == node)]
            idx = extracted.index

            # Get the list of stops that node is mapped to
            s = list(x for x in merge_labels.keys() if merge_labels[x] == node)

            # Remove extracted from the original df
            nodes_gr = nodes_gr.drop(idx)

            # Add mapped edges
            for si in s:
                tmp = extracted.replace({'source': {node: si}, 'target': {node: si}})
                tmp_df = tmp_df.append(tmp)

        data.nodes_gr = nodes_gr.append(tmp_df)

        data.nodes_gr = nodes_gr
        cls.merge_labels = merge_labels

    @classmethod
    def merge_nodes(cls):
        print('\nAdding the stops to the list of nodes in the graph...')

        nodes_co = data.nodes_co

        # Remove the merged nodes
        nodes_co = nodes_co[~nodes_co['node_id'].isin(cls.merge_labels.values())]

        data.nodes_co = data.stops_co.append(nodes_co)

    @classmethod
    def merge(cls):
        cls.connect_nodes()
        cls.identify_nodes()
        cls.merge_nodes()
