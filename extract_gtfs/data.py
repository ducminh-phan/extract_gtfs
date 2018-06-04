from extract_gtfs.utils import LogAttribute


class Data(metaclass=LogAttribute):
    __slots__ = ('in_folder', 'out_folder',
                 'selected_date', 'selected_trips',
                 'stop_times', 'transfers', 'trips', 'stop_routes')


def setup(args):
    Data.in_folder = args.folder
    Data.out_folder = args.output
