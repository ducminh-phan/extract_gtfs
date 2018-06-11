from extract_gtfs.data import Data, labels


class Relabel:
    @classmethod
    def label_trips(cls):
        trip_label = {}

        selected_trips = sorted(Data.selected_trips)
        for idx, trip in enumerate(selected_trips):
            trip_label[trip] = idx

        labels.trip_label = trip_label

    @classmethod
    def label_stops(cls):
        transfers = Data.transfers
        stop_times = Data.stop_times

        # The available stops in transfers and stop_times might be different,
        # so we need to find the union of these sets to have consistent labels
        stops = set(transfers['from_stop_id']) | set(transfers['to_stop_id']) | set(stop_times['stop_id'])
        stops = sorted(stops)

        stop_label = {}

        for idx, stop in enumerate(stops):
            stop_label[stop] = idx

        labels.stop_label = stop_label

    @classmethod
    def create_label(cls):
        print('\nCreating new labels for trips and stops...')
        cls.label_trips()
        cls.label_stops()

    @classmethod
    def relabel_trips(cls):
        print('\nRelabelling the trips...')

        trips = Data.trips

        trips['trip_id'] = trips['trip_id'].map(labels.trip_label)

        Data.trips = trips

    @classmethod
    def relabel_stop_times(cls):
        print('\nRelabelling the timetable...')

        stop_times = Data.stop_times

        stop_times['trip_id'] = stop_times['trip_id'].map(labels.trip_label)
        stop_times['stop_id'] = stop_times['stop_id'].map(labels.stop_label)

        Data.stop_times = stop_times

    @classmethod
    def relabel_transfers(cls):
        print('\nRelabelling the transfers...')

        transfers = Data.transfers

        transfers['from_stop_id'] = transfers['from_stop_id'].map(labels.stop_label)
        transfers['to_stop_id'] = transfers['to_stop_id'].map(labels.stop_label)

        Data.transfers = transfers

    @classmethod
    def relabel_stop_routes(cls):
        print('\nRelabelling the stops...')

        stop_routes = Data.stop_routes

        stop_routes['stop_id'] = stop_routes['stop_id'].map(labels.stop_label)

        Data.stop_routes = stop_routes

    @classmethod
    def relabel_coordinates(cls):
        print('\nRelabelling the coordinates table...')

        stops = Data.stops

        stops['id'] = stops['id'].map(labels.stop_label)

        Data.stops = stops

    @classmethod
    def relabel(cls):
        cls.relabel_trips()
        cls.relabel_stop_times()
        cls.relabel_transfers()
        cls.relabel_stop_routes()
        cls.relabel_coordinates()
