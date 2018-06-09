from merge_graph.settings import data
from merge_graph.utils import read_co_file, write_data_files


class Relabel:
    __slots__ = ('label',)

    @classmethod
    def create_label(cls, args):
        stops_co = read_co_file(args.stops_file)
        num_stops = max(stops_co['node_id']) + 1

        # Relabel the nodes starting from num_stops to avoid id conflict
        cls.label = {node_id: idx
                     for idx, node_id in enumerate(sorted(data.nodes_co['node_id'].unique()),
                                                   start=num_stops)}

        data.stops_co = stops_co

    @classmethod
    def relabel_co(cls):
        nodes_co = data.nodes_co

        nodes_co['node_id'] = nodes_co['node_id'].map(cls.label)

        data.nodes_co = nodes_co

    @classmethod
    def relabel_gr(cls):
        nodes_gr = data.nodes_gr

        nodes_gr['source'] = nodes_gr['source'].map(cls.label)
        nodes_gr['target'] = nodes_gr['target'].map(cls.label)

        data.nodes_gr = nodes_gr

    @classmethod
    def relabel(cls, args):
        print('\nRelabeling the nodes in the graph files...')

        cls.create_label(args)

        cls.relabel_co()
        cls.relabel_gr()

        write_data_files()
