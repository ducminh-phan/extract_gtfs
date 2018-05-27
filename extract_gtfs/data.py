from .utils import LogAttribute


class Data(metaclass=LogAttribute):
    __slots__ = ('in_folder', 'out_folder',
                 'date', 'trips', 'stop_times')


def setup(args):
    Data.in_folder = args.folder
    Data.out_folder = args.output
