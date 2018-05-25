import argparse

from .data import setup
from .extract_dates import CalendarDates


def parse_args():
    parser = argparse.ArgumentParser(description="Extract information from GTFS files "
                                                 "to use with RAPTOR algorithm")

    parser.add_argument("folder", help="The folder containing the GTFS files to extract")
    parser.add_argument("-o", "--output", default=None, help="The name of the output folder. "
                                                             "The default name is obtained by appending "
                                                             "'_out' to the input folder name")

    args = parser.parse_args()
    args = check_args(parser, args)

    return args


def check_args(parser, args):
    if args.output is None:
        args.output = args.folder + "_out"
    elif args.output == args.folder:
        parser.error("The input and output folders' names must be different")

    return args


def main():
    args = parse_args()
    setup(args)

    CalendarDates.extract()


if __name__ == "__main__":
    main()
