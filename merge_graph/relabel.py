from merge_graph.settings import config
from merge_graph.utils import read_co_file, read_gr_file, write_co_file, write_gr_file


class Relabel:
    __slots__ = ('nodes_co', 'nodes_gr', 'label')

    @classmethod
    def filter_nodes(cls, args):
        nodes_co = read_co_file(args.nodes_file)
        nodes_gr = read_gr_file(args.graph_file)

        # Filter the coordinates to keep only the nodes appear in the graph
        nodes = set(nodes_gr['source']) | set(nodes_gr['target'])
        nodes_co = nodes_co[nodes_co['node_id'].isin(nodes)]

        cls.nodes_co = nodes_co
        cls.nodes_gr = nodes_gr

    @classmethod
    def create_label(cls, args):
        stops_co = read_co_file(args.stops_file)
        num_stops = max(stops_co['node_id']) + 1

        # Relabel the nodes starting from num_stops to avoid id conflict
        cls.label = {node_id: idx
                     for idx, node_id in enumerate(sorted(cls.nodes_co['node_id'].unique()),
                                                   start=num_stops)}

    @classmethod
    def relabel_co(cls):
        nodes_co = cls.nodes_co

        nodes_co['node_id'] = nodes_co['node_id'].map(cls.label)

        cls.nodes_co = nodes_co

    @classmethod
    def relabel_gr(cls):
        nodes_gr = cls.nodes_gr

        nodes_gr['source'] = nodes_gr['source'].map(cls.label)
        nodes_gr['target'] = nodes_gr['target'].map(cls.label)

        cls.nodes_gr = nodes_gr

    @classmethod
    def write_files(cls):
        write_co_file(cls.nodes_co, config.nodes_file)
        write_gr_file(cls.nodes_gr, config.graph_file)

    @classmethod
    def relabel(cls, args):
        print('\nRelabeling the nodes in the graph files...')

        cls.filter_nodes(args)
        cls.create_label(args)

        cls.relabel_co()
        cls.relabel_gr()

        cls.write_files()
