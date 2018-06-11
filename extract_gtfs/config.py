import os
from types import SimpleNamespace

config = SimpleNamespace()


def setup(args):
    global config

    config.in_folder = args.in_folder
    config.out_folder = args.out_folder

    config.tmp_folder = '{}_tmp'.format(args.in_folder)
    config.labels_folder = '{}_labels'.format(args.in_folder)

    config.nodes_file = '{}/nodes.co'.format(config.out_folder)
    config.edges_file = '{}/edges.gr'.format(config.out_folder)

    if not os.path.exists(config.out_folder):
        os.makedirs(config.out_folder)

    if not os.path.exists(config.tmp_folder):
        os.makedirs(config.tmp_folder)
