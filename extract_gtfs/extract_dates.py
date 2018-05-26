from datetime import date, timedelta

from tqdm import tqdm

from .data import Data
from .utils import LogAttribute, load_attr


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


class CalendarDates(metaclass=LogAttribute):
    __slots__ = ('date_to_services', 'date_to_trips')

    @classmethod
    def extract(cls):
        cls.get_services_by_date()
        cls.get_trips_by_date()

    @classmethod
    @load_attr('date_to_services')
    def get_services_by_date(cls):
        print("\nFinding the services available for each day...")

        d2s = {}
        date_groups = Data.calendar_dates_df.groupby('date')
        for date_str in tqdm(Data.calendar_dates_df['date'].unique()):
            df = date_groups.get_group(date_str)
            d2s[date_str] = set(df['service_id'])

        cls.date_to_services = d2s

    @classmethod
    @load_attr('date_to_trips')
    def get_trips_by_date(cls):
        print("\nFinding the trips available for each day...")

        d2t = {}
        service_groups = Data.trips_df.groupby('service_id')
        for date_str, services in tqdm(cls.date_to_services.items()):
            trips_set = set()
            for service in services:
                df = service_groups.get_group(service)
                trips_set |= set(df['trip_id'])

            d2t[date_str] = trips_set

        cls.date_to_trips = d2t

    @classmethod
    @load_attr({Data: ['dates', 'date_to_trips']})
    def get_dates(cls):
        cls.extract()

        print("\nFinding the two consecutive busiest days...")

        first_day = None
        second_day = None
        max_trip_count = 0

        for date_str in tqdm(cls.date_to_trips):
            # Get the string representing the next date
            date_obj = str_to_date(date_str)
            next_date_str = date_to_str(date_obj + timedelta(1))

            # If the next date is also in the timetable, find the total number of trips
            if next_date_str in cls.date_to_trips:
                trips_set = cls.date_to_trips[date_str] | cls.date_to_trips[next_date_str]

                if len(trips_set) > max_trip_count:
                    first_day = date_str
                    second_day = next_date_str
                    max_trip_count = len(trips_set)

        Data.dates = (first_day, second_day)
        Data.date_to_trips = {d: cls.date_to_trips[d] for d in Data.dates}
