import unittest
import datetime
from visualization.overspeed import calculate_speed, count_overspeeding_vehicles
from visualization.overspeed import Street
from visualization.punctuality import get_line_schedule, get_line_bus_stops, get_line_stops, \
                                      get_stop_schedule, get_delays
from visualization.utils import calculate_distance, date_to_seconds, get_address_components, \
                                get_current_localization
import pandas as pd

PATH_TO_LOCALIZATIONS = 'tests/test_data/test-buses.json'
PATH_TO_BUS_STOPS = 'tests/test_data/test-bus-stops.json'
PATH_TO_SCHEDULE = 'tests/test_data/test-schedule.csv'

class TestUtils(unittest.TestCase):
    ''' Test utils.py module. '''

    def test_calculate_distance(self):
        ''' Test calculate_distance function. '''
        distance = calculate_distance(
            (52.21244498628319, 20.982054528763946),
            (52.21121798800691, 20.982040191304982))
        self.assertTrue(distance > 0)
        distance = calculate_distance(
            (52.21244498628319, 20.982054528763946),
            (52.21244498628319, 20.982054528763946))
        self.assertEqual(distance, 0)

    def test_date_to_seconds(self):
        ''' Test date_to_seconds function. '''
        seconds = date_to_seconds('1970-01-01 01:00:00')
        self.assertEqual(seconds, 0)
        seconds = date_to_seconds('1970-01-01 02:00:00')
        self.assertEqual(seconds, 3600)

    def test_get_address_components(self):
        ''' Test get_address_components function. '''
        street, district, city = get_address_components(52.21185112179191, 20.982080090108504)
        self.assertEqual(street, 'Ludwika Pasteura')
        self.assertEqual(district, 'Ochota')
        self.assertEqual(city, 'Warszawa')

    def test_get_current_localization(self):
        ''' Test get_current_localization function. '''
        localizations = get_current_localization()
        self.assertTrue(len(localizations) > 0)
        localizations = pd.DataFrame(localizations)
        self.assertEqual(localizations.columns.tolist(),
                         ['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat', 'Brigade'])

class TestOverspeed(unittest.TestCase):
    ''' Test overspeed.py module. '''

    def test_street(self):
        ''' Test Street class. '''
        s1 = Street('Wawelska',  'Ochota', 'Warszawa')
        s2 = Street('Banacha',  'Ochota', 'Warszawa')
        self.assertEqual(s1, s1)
        self.assertNotEqual(s1, s2)
        self.assertEqual(hash(s1), hash(s1))
        self.assertEqual(str(s1), 'Wawelska, Ochota, Warszawa')
        self.assertEqual(repr(s1), 'Wawelska, Ochota, Warszawa')

    def test_calculate_speed(self):
        ''' Test calculate_speed function. '''
        speed = calculate_speed((52.2296756, 21.0122287),
                                (52.2296756, 21.0122287),
                                '2024-02-12 19:15:40',
                                '2024-02-12 19:15:40')
        self.assertEqual(speed, 0)
        speed = calculate_speed((52.21190914534448, 20.982078390765047),
                                (52.2137110192737, 20.98487127088543),
                                '2024-02-12 10:00:00',
                                '2024-02-12 10:01:00')
        self.assertTrue(speed > 0)
        speed = calculate_speed((52.21190914534448,
                                 20.982078390765047),
                                 (52.21328907915247,
                                  20.980948099861905),
                                  '2024-02-12 13:45:00',
                                  '2024-02-12 13:46:00')
        self.assertTrue(speed > 0)

    def test_count_overspeeding_vehicles(self):
        ''' Test count_overspeeding_vehicles function. '''
        overspeeding_vehicles, result = count_overspeeding_vehicles(PATH_TO_LOCALIZATIONS,
                                                                    False)
        self.assertTrue(overspeeding_vehicles > 0)
        self.assertEqual(list(result.keys()), [Street('Kolonia Lubeckiego',  'Ochota', 'Warszawa')])
        self.assertEqual(len(result[Street('Kolonia Lubeckiego',  'Ochota', 'Warszawa')]), 1)

class TestPunctuality(unittest.TestCase):
    ''' Test punctuality.py module. '''

    def test_get_line_schedule(self):
        ''' Test get_line_schedule function. '''
        schedule = get_line_schedule('182', PATH_TO_SCHEDULE)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule['BusstopID'].values[0], 4121)
        self.assertEqual(schedule['BusstopNr'].values[0], 5)
        self.assertEqual(schedule['Time'].values[0], '09:10:00')

    def test_get_line_bus_stops(self):
        ''' Test get_line_bus_stops function. '''
        bus_stops = get_line_bus_stops('182',
                                       PATH_TO_BUS_STOPS,
                                       PATH_TO_SCHEDULE)
        self.assertEqual(len(bus_stops), 1)
        self.assertEqual(bus_stops['BusstopID'].values[0], 4121)
        self.assertEqual(bus_stops['BusstopNr'].values[0], 5)
        self.assertEqual(bus_stops['Latitude'].values[0], 52.21599054475676)
        self.assertEqual(bus_stops['Longitude'].values[0], 20.982646082482425)

    def get_line_stops(self):
        ''' Test get_line_stops function. '''
        localizations = pd.read_json(PATH_TO_LOCALIZATIONS)
        line_stops = get_line_stops('182',
                                    localizations,
                                    PATH_TO_BUS_STOPS,
                                    PATH_TO_SCHEDULE)
        self.assertEqual(len(line_stops), 1)
        self.assertEqual(line_stops['BusstopID'].values[0], 4121)
        self.assertEqual(line_stops['BusstopNr'].values[0], 5)
        self.assertEqual(line_stops['Latitude'].values[0], 52.21599054475676)
        self.assertEqual(line_stops['Longitude'].values[0], 20.982646082482425)
        self.assertEqual(line_stops['Time'].values[0], '2024-02-16 09:15:41')

    def test_get_stop_schedule(self):
        ''' Test get_stop_schedule function. '''
        localizations = pd.read_json(PATH_TO_LOCALIZATIONS)

        localizations['Time'] = localizations['Time'].apply(
                                    lambda x: '00' + x[2:] if int(x[:2]) >= 24 else x
                                )
        localizations['Time'] = pd.to_datetime(localizations['Time'],
                                               format='%Y-%m-%d %H:%M:%S').dt.time

        localizations['LatRound'] = localizations['Lat'].round(4)
        localizations['LonRound'] = localizations['Lon'].round(4)

        line_stops = get_line_stops('182',
                                    localizations,
                                    PATH_TO_BUS_STOPS,
                                    PATH_TO_SCHEDULE)
        schedule = get_stop_schedule('182', line_stops, PATH_TO_SCHEDULE)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule['BusstopID'].values[0], 4121)
        self.assertEqual(schedule['BusstopNr'].values[0], 5)
        self.assertEqual(schedule['Time'].values[0], datetime.time(9, 15, 40))

    def test_get_delays(self):
        ''' Test get_delays function. '''
        delays = get_delays(PATH_TO_LOCALIZATIONS,
                            PATH_TO_BUS_STOPS,
                            PATH_TO_SCHEDULE)
        self.assertEqual(len(delays), 4)
        self.assertEqual(delays['BusstopID'].values[0], 4121)
        self.assertEqual(delays['BusstopNr'].values[0], 5)
        self.assertEqual(delays['Time'].values[0], datetime.time(9, 15, 40))
        self.assertEqual(delays['ScheduledTime'].values[0], datetime.time(9, 10, 0))
        self.assertEqual(int(delays['Delay'].values[0]), 5)
