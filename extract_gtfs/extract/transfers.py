import networkx as nx
import pandas as pd

from extract_gtfs.data import Data
from extract_gtfs.utils import LogAttribute, load_attr, read_csv


class ExtractTransfer(metaclass=LogAttribute):
    __slots__ = ()

    @classmethod
    @load_attr({Data: "transfers"})
    def extract(cls):
        try:
            transfers_df = read_csv(
                "transfers.txt",
                usecols=["from_stop_id", "to_stop_id", "min_transfer_time"],
                dtype={"from_stop_id": str, "to_stop_id": str},
            )
        except FileNotFoundError:
            # Create a dummy transfer_df in case of absence of the optional file transfers.txt
            transfers_df = pd.DataFrame(
                [], columns=["from_stop_id", "to_stop_id", "min_transfer_time"]
            )

        # There might be NaN values in the file, thus we can only change the dtype of min_transfer_time
        # to int after removing NaN values
        transfers_df = transfers_df.dropna()
        transfers_df["min_transfer_time"] = transfers_df["min_transfer_time"].astype(
            int
        )

        g = nx.from_pandas_edgelist(
            transfers_df,
            "from_stop_id",
            "to_stop_id",
            "min_transfer_time",
            create_using=nx.DiGraph(),
        )

        print("\nFinding the transitive closure of the transfer graph...")

        gt = nx.transitive_closure(g)

        dijkstra_lengths = dict(
            nx.all_pairs_dijkstra_path_length(g, weight="min_transfer_time")
        )

        # If u and v are the same node, the path length will be 0. In that case,
        # we need to take the transfer time from the original graph
        transfers = [
            [u, v, dijkstra_lengths[u][v] if u != v else data["min_transfer_time"]]
            for u, v, data in gt.edges(data=True)
        ]

        Data.transfers = pd.DataFrame(
            transfers, columns=["from_stop_id", "to_stop_id", "min_transfer_time"]
        )
