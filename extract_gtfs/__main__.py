from .data import setup
from .extract_dates import ExtractDate
from .split_trips import SplitTrip
from .transfers import ExtractTransfer
from .utils import parse_args


def main():
    args = parse_args()
    setup(args)

    ExtractDate.extract()
    SplitTrip.split_by_time()
    ExtractTransfer.extract()


if __name__ == "__main__":
    main()
