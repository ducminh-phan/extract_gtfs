from datetime import date

from tqdm import tqdm

from .data import Data


def str_to_date(date_string):
    """
    Convert string storing the date in calendar_dates to a date object
    """
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[6:])

    return date(year, month, day)


class CalendarDates:
    __slots__ = ('date_to_services', 'date_to_trips')

    @classmethod
    def extract(cls):
        cls.get_services_by_date()
        cls.get_trips_by_date()

    @classmethod
    def get_services_by_date(cls):
        print("Finding the services available for each day...")

        d2s = {}
        for date_str in tqdm(Data.calendar_dates_df['date'].unique()):
            d2s[date_str] = set(
                Data.calendar_dates_df[
                    Data.calendar_dates_df['date'] == date_str
                    ]['service_id']
            )

        cls.date_to_services = d2s

    @classmethod
    def get_trips_by_date(cls):
        print("\nFinding the trips available for each day...")

        d2t = {}
        for date_str, services in tqdm(cls.date_to_services.items()):
            trips = set(trip for service in services
                        for trip in set(Data.trips_df[Data.trips_df['service_id'] == service]['trip_id'])
                        )
            d2t[date_str] = trips

        cls.date_to_trips = d2t
