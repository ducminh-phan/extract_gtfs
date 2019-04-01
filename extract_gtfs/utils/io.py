import pandas as pd

from extract_gtfs.config import config


def read_co_file(file_path):
    df = pd.read_csv(file_path, sep="\s+", header=None, usecols=[1, 2, 3])
    df.columns = ["id", "lon", "lat"]

    return df


def write_co_file(df, file_path):
    with open(file_path, "w") as f:
        for row in df.itertuples(index=False):
            f.write("v " + " ".join(map(str, row)) + "\n")


def read_gr_file(file_path):
    df = pd.read_csv(file_path, sep="\s+", header=None, usecols=[1, 2, 3])
    df.columns = ["source", "target", "weight"]

    return df


def write_gr_file(df, file_path):
    with open(file_path, "w") as f:
        for row in df.itertuples(index=False):
            f.write("a " + " ".join(map(str, row)) + "\n")


def write_graph_files():
    from extract_gtfs.data import Data

    write_co_file(Data.nodes, config.nodes_file)
    write_gr_file(Data.edges, config.edges_file)


def read_csv(file_name, **kwargs):
    return pd.read_csv("{}/{}".format(config.in_folder, file_name), **kwargs)
