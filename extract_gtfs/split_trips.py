from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

from .data import Data
from .utils import LogAttribute, load_attr


class SplitTrip(metaclass=LogAttribute):
    __slots__ = ('trip_groups_by_pattern',)

    @classmethod
    @load_attr({Data: 'stop_times'})
    def extract_stop_times(cls):
        print('\nExtracting the selected dates from the timetable...')

        stop_times_df = pd.read_csv('{}/stop_times.txt'.format(Data.in_folder),
                                    usecols=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'],
                                    dtype={'trip_id': str, 'arrival_time': str, 'departure_time': str,
                                           'stop_id': str, 'stop_sequence': np.uint16})

        stop_times_filtered = stop_times_df[stop_times_df['trip_id'].isin(Data.trips)]

        # Sort by stop_sequence to make sure the stop sequences are in correct order
        stop_times_filtered = stop_times_filtered.sort_values(by=['trip_id', 'stop_sequence'])

        Data.stop_times = stop_times_filtered

    @classmethod
    @load_attr('trip_groups_by_pattern')
    def split_by_pattern(cls):
        cls.extract_stop_times()

        print('\nCollecting the stop patterns...')

        trip_groups = Data.stop_times.groupby('trip_id')
        pattern_to_trips = defaultdict(list)

        for trip, group in tqdm(trip_groups):
            stop_pattern = tuple(group['stop_id'])
            pattern_to_trips[stop_pattern].append(trip)

        cls.trip_groups_by_pattern = list(pattern_to_trips.values())
