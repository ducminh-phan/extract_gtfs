from types import SimpleNamespace

from extract_gtfs.utils import LogAttribute


class Data(metaclass=LogAttribute):
    __slots__ = ('selected_date', 'selected_trips',
                 'stop_times', 'transfers', 'trips', 'stop_routes',
                 'stops', 'nodes', 'edges')


stats = SimpleNamespace()
labels = SimpleNamespace()
