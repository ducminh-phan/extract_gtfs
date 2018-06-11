from extract_gtfs.data import Data, labels
from extract_gtfs.utils import write_graph_files


class Relabel:
    @classmethod
    def create_label(cls):
        stops_df = Data.stops
        num_stops = max(stops_df['id']) + 1

        # Relabel the nodes starting from num_stops to avoid id conflict
        labels.node_label = {node_id: idx
                             for idx, node_id in enumerate(sorted(Data.nodes['id'].unique()),
                                                           start=num_stops)}

    @classmethod
    def relabel_nodes(cls):
        nodes_df = Data.nodes

        nodes_df['id'] = nodes_df['id'].map(labels.node_label)

        Data.nodes = nodes_df

    @classmethod
    def relabel_edges(cls):
        edges_df = Data.edges

        edges_df['source'] = edges_df['source'].map(labels.node_label)
        edges_df['target'] = edges_df['target'].map(labels.node_label)

        Data.edges = edges_df

    @classmethod
    def relabel(cls):
        print('\nRelabeling the nodes in the graph files...')

        cls.create_label()

        cls.relabel_nodes()
        cls.relabel_edges()

        # Write the graph files to use with the C++ part
        write_graph_files()
