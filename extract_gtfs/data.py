from types import SimpleNamespace

import pandas as pd

from extract_gtfs.config import config
from extract_gtfs.utils import LogAttribute


class Data(metaclass=LogAttribute):
    __slots__ = (
        "selected_date",
        "selected_trips",
        "stop_times",
        "transfers",
        "trips",
        "stop_routes",
        "stops",
        "nodes",
        "edges",
    )


stats = SimpleNamespace()


class LabelContainer:
    __slots__ = ("trip_label", "stop_label", "node_label")

    def save(self):
        for name in self.__slots__:
            # Create the DataFrames for the labels, sorted by the newly assigned labels,
            # then save them to the label folder
            pd.DataFrame(
                sorted(getattr(self, name).items(), key=lambda x: x[1])
            ).to_csv(
                "{}/{}.csv".format(config.labels_folder, name),
                index=False,
                header=["old_id", "new_id"],
            )


labels = LabelContainer()
