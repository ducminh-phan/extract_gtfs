from datetime import date

from tqdm import tqdm

from .data import Data
from .utils import LogAttribute, load_attr, read_csv


def str_to_date(date_string):
    """
    Convert string storing the date in calendar_dates to a date object
    """
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:])

    return date(year, month, day)


def date_to_str(date_obj):
    """
    Convert a date object to the string form used in GTFS files.

    >>> date_to_str(date(2018, 8, 25))
    '20180825'

    It is the inverse of the str_to_date function.

    >>> date_to_str(str_to_date("20180825"))
    '20180825'

    >>> str_to_date(date_to_str(date(2018, 8, 25)))
    datetime.date(2018, 8, 25)
    """
    return '{0.year}{0.month:0>2}{0.day}'.format(date_obj)


class ExtractDate(metaclass=LogAttribute):
    __slots__ = ('calendar_dates_df', 'trips_df',
                 'date_to_services', 'date_to_trips')

    @classmethod
    def setup(cls):
        print("Reading the GTFS files...")

        cls.calendar_dates_df = read_csv('calendar_dates', dtype=str,
                                         usecols=['service_id', 'date'])

        cls.trips_df = read_csv('trips.txt', dtype=str,
                                usecols=['service_id', 'trip_id'])

    @classmethod
    @load_attr('date_to_services')
    def get_services_by_date(cls):
        print("\nFinding the services available for each day...")

        d2s = {}
        date_groups = cls.calendar_dates_df.groupby('date')
        for date_str in tqdm(cls.calendar_dates_df['date'].unique()):
            df = date_groups.get_group(date_str)
            d2s[date_str] = set(df['service_id'])

        cls.date_to_services = d2s

    @classmethod
    @load_attr('date_to_trips')
    def get_trips_by_date(cls):
        print("\nFinding the trips available for each day...")

        d2t = {}
        service_groups = cls.trips_df.groupby('service_id')
        for date_str, services in tqdm(cls.date_to_services.items()):
            trips_set = set()
            for service in services:
                df = service_groups.get_group(service)
                trips_set |= set(df['trip_id'])

            d2t[date_str] = trips_set

        cls.date_to_trips = d2t

    @classmethod
    @load_attr({Data: ['date', 'trips']})
    def extract(cls):
        cls.setup()
        cls.get_services_by_date()
        cls.get_trips_by_date()

        print("\nFinding the busiest day in the timetable...")

        # Iterate over the tuples (date, trips) and find the trips set of max size
        selected_date, trips = max(cls.date_to_trips.items(), key=lambda x: len(x[1]))

        Data.date = selected_date
        Data.trips = trips
