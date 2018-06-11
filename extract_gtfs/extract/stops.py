from extract_gtfs.data import Data
from extract_gtfs.utils import read_csv


def coor_to_int(coor):
    """
    Convert the latitude/longitute from float to integer by multiplying to 1e6,
    then rounding off
    """
    return round(coor * 1000000)


class ExtractCoordinates:
    @classmethod
    def extract(cls):
        print('\nGetting the coordinates of the stops served in the timetable...')

        # We consider only the stops served by at least one route. Thus the stops are taken
        # from Data.stop_times only, without the stops from Data.transfers
        stop_times = Data.stop_times
        served_stops = set(stop_times['stop_id'])

        stop_df = read_csv('stops.txt',
                           usecols=['stop_id', 'stop_lat', 'stop_lon'],
                           dtype={'stop_id': str, 'stop_lat': float, 'stop_lon': float})

        # Keep only the stops in the timetable
        stop_df = stop_df[stop_df['stop_id'].isin(served_stops)]

        # Convert the coordinates
        stop_df['stop_lat'] = stop_df['stop_lat'].apply(coor_to_int)
        stop_df['stop_lon'] = stop_df['stop_lon'].apply(coor_to_int)

        # Sort by stop_id and reorder the columns
        stop_df = stop_df.sort_values(by=['stop_id'])
        stop_df = stop_df[['stop_id', 'stop_lon', 'stop_lat']]

        Data.stops = stop_df
