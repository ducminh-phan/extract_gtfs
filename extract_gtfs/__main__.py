from .data import setup
from .extract_dates import CalendarDates
from .utils import parse_args


def main():
    args = parse_args()
    setup(args)

    CalendarDates.get_dates()


if __name__ == "__main__":
    main()
