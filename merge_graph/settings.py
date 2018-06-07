import os
from types import SimpleNamespace

config = SimpleNamespace()
data = SimpleNamespace()


def setup():
    config.tmp_folder = 'merge_graph_tmp'
    config.out_folder = 'merge_graph_output'

    config.nodes_file = '{}/nodes.co'.format(config.out_folder)
    config.graph_file = '{}/nodes.gr'.format(config.out_folder)

    if not os.path.exists(config.tmp_folder):
        os.makedirs(config.tmp_folder)

    if not os.path.exists(config.out_folder):
        os.makedirs(config.out_folder)

    return config
