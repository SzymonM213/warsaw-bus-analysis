import unittest
from fetch.fetch_schedules import get_bus_stops, get_lines, get_schedule
from fetch.fetch_day import get_current_localization
import pandas as pd

class TestSchedulesFetch(unittest.TestCase):
    ''' Test fetch_schedules.py module. '''
    def test_get_bus_stops(self):
        ''' Test get_bus_stops function. '''
        bus_stops = get_bus_stops()
        bus_stops = pd.DataFrame(bus_stops)
        self.assertTrue(len(bus_stops) > 0)
        self.assertTrue('BusstopID' in bus_stops.columns)
        self.assertTrue('BusstopNr' in bus_stops.columns)
        self.assertTrue('Latitude' in bus_stops.columns)
        self.assertTrue('Longitude' in bus_stops.columns)
        self.assertTrue('Direction' in bus_stops.columns)
        self.assertTrue('BusstopName' in bus_stops.columns)
        self.assertTrue('Saska' in bus_stops['BusstopName'].values)

    def test_get_lines(self):
        ''' Test get_lines function. '''
        lines = get_lines('2140', '01')
        self.assertTrue(len(lines) > 0)
        self.assertTrue('509' in lines)
        self.assertTrue('507' in lines)

    def test_get_schedule(self):
        ''' Test get_schedule function. '''
        schedule = get_schedule('509', '2140', '01')
        schedule = pd.DataFrame(schedule)
        self.assertTrue(len(schedule) > 0)
        self.assertTrue('509' in schedule['Line'].values)
        self.assertTrue('2140' in schedule['BusstopID'].values)
        self.assertTrue('01' in schedule['BusstopNr'].values)
        self.assertTrue('15:12:00' in schedule['Time'].values)
        self.assertTrue('23:42:00' in schedule['Time'].values)

class TestDayFetch(unittest.TestCase):
    ''' Test fetch_day.py module. '''
    def test_get_current_localization(self):
        ''' Test get_current_localization function. '''
        localization = get_current_localization()
        self.assertTrue(len(localization) > 0)
        self.assertTrue('Lines' in localization[0])
        self.assertTrue('Lon' in localization[0])
        self.assertTrue('Lat' in localization[0])
        self.assertTrue('Time' in localization[0])
        self.assertTrue('Brigade' in localization[0])
        for bus in localization:
            self.assertTrue(bus['Lines'].isdigit() or bus['Lines'][0] in ['N', 'E', 'L', 'Z'])

if __name__ == '__main__':
    unittest.main()