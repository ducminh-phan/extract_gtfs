from .data import setup
from .extract_dates import ExtractDate
from .utils import parse_args


def main():
    args = parse_args()
    setup(args)

    ExtractDate.extract()


if __name__ == "__main__":
    main()
