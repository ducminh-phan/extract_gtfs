import argparse

import pandas as pd

from merge_graph.settings import config, data


def parse_args():
    parser = argparse.ArgumentParser(prog="python3 -m merge_graph",
                                     description="Merge the stops from the timetable to the walking graph")

    parser.add_argument("stops_file", help="The file containing the coordinates of the stops")
    parser.add_argument("nodes_file", help="The file containing the coordinates of the nodes "
                                           "of the walking graph")
    parser.add_argument('graph_file', help="The file containing the edges of the walking graph")

    args = parser.parse_args()

    return args


def read_co_file(file_path):
    df = pd.read_csv(file_path, sep='\s+', header=None, usecols=[1, 2, 3])
    df.columns = ['node_id', 'node_lon', 'node_lat']

    return df


def write_co_file(df, file_path):
    with open(file_path, 'w') as f:
        for row in df.itertuples(index=False):
            f.write('v ' + ' '.join(map(str, row)) + '\n')


def read_gr_file(file_path):
    df = pd.read_csv(file_path, sep='\s+', header=None, usecols=[1, 2, 3])
    df.columns = ['source', 'target', 'weight']

    return df


def write_gr_file(df, file_path):
    with open(file_path, 'w') as f:
        for row in df.itertuples(index=False):
            f.write('a ' + ' '.join(map(str, row)) + '\n')


def write_data_files():
    write_co_file(data.nodes_co, config.nodes_file)
    write_gr_file(data.nodes_gr, config.graph_file)


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question using input() and return the answer.
    :param question: a string that is presented to the user
    :param default: the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user)
    :return: True for "yes" or False for "no"
    """
    valid = {"yes": True, "y": True,
             "no": False, "n": False}

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
