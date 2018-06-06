import os
from types import SimpleNamespace

config = SimpleNamespace()


def setup():
    config.tmp_folder = 'merge_graph_tmp'
    config.nodes_file = '{}/nodes.co'.format(config.tmp_folder)
    config.graph_file = '{}/nodes.gr'.format(config.tmp_folder)

    if not os.path.exists(config.tmp_folder):
        os.makedirs(config.tmp_folder)

    return config
