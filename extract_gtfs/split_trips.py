from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

from .data import Data
from .utils import LogAttribute, load_attr


def hms_to_s(s):
    """
    Convert the time formatting from a string of the form "hh:mm:ss"
    to an integer representing the number of seconds counting from 00:00:00
    """
    h, m, s = list(map(int, s.split(':')))
    return 3600 * h + 60 * m + s


class SplitTrip(metaclass=LogAttribute):
    __slots__ = ('stop_times_grouped', 'trip_groups_by_pattern', 'trip_groups_sorted', 'trip_groups')

    @classmethod
    @load_attr({Data: 'stop_times'})
    def extract_stop_times(cls):
        print('\nExtracting the selected dates from the timetable...')

        stop_times_df = pd.read_csv('{}/stop_times.txt'.format(Data.in_folder),
                                    usecols=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'],
                                    dtype={'trip_id': str, 'arrival_time': str, 'departure_time': str,
                                           'stop_id': str, 'stop_sequence': np.uint16})

        # Keep only the events associating with the selected trips
        stop_times_filtered = stop_times_df[stop_times_df['trip_id'].isin(Data.trips)]

        # Remove events containing NaN
        stop_times_filtered = stop_times_filtered.dropna()

        # Sort by stop_sequence to make sure the stop sequences are in correct order
        stop_times_filtered = stop_times_filtered.sort_values(by=['trip_id', 'stop_sequence'])

        # Convert the time format
        stop_times_filtered['arrival_time'] = stop_times_filtered['arrival_time'].apply(hms_to_s)
        stop_times_filtered['departure_time'] = stop_times_filtered['departure_time'].apply(hms_to_s)

        Data.stop_times = stop_times_filtered

    @classmethod
    @load_attr('stop_times_grouped', 'trip_groups_by_pattern')
    def split_by_pattern(cls):
        cls.extract_stop_times()

        print('\nCollecting the stop patterns...')

        cls.stop_times_grouped = Data.stop_times.groupby('trip_id')
        pattern_to_trips = defaultdict(list)

        for trip, group in tqdm(cls.stop_times_grouped):
            stop_pattern = tuple(group['stop_id'])
            pattern_to_trips[stop_pattern].append(trip)

        cls.trip_groups_by_pattern = list(pattern_to_trips.values())

    @classmethod
    @load_attr('trip_groups_sorted')
    def sort_trip(cls):
        cls.split_by_pattern()

        print('\nGetting the departure times for every trip...')

        trip_to_deps = {trip: group['departure_time'].tolist()
                        for trip, group in tqdm(cls.stop_times_grouped)}

        print('\nSorting the trips in each stop pattern by the departure time at the first stop...')

        cls.trip_groups_sorted = [sorted(gr, key=lambda t: trip_to_deps[t][0])
                                  for gr in tqdm(cls.trip_groups_by_pattern)]
