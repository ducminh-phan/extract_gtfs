import argparse
from math import cos, pi, sqrt

import pandas as pd


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


R = 6371


def distance(p1, p2):
    """
    Approximate the great-circle distance given the coordinates of two points.
    Reference: https://www.movable-type.co.uk/scripts/latlong.html
    """
    x1, y1 = p1
    x2, y2 = p2

    phi_m = (y1 + y2) / 2 / 1000000
    x = (x2 - x1) * cos(pi * phi_m / 180)
    y = y2 - y1

    return round(sqrt(x * x + y * y) * R * pi / 180 / 100.0)
