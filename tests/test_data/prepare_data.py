import json
import pandas as pd

LINES = ['182', '187', '523', 'N22']
BUSSTOP_ID = '4121'
BUSSTOP_NR = 5

def prepare_test_buses():
    ''' Prepare mock data for buses location. '''
    buses = []
    for line in LINES:
        loc = {}
        loc['Lines'] = line
        loc['Lat'] = 52.21599054475676
        loc['Lon'] = 20.982646082482425
        loc['Time'] = '2024-02-16 09:15:40'
        loc['Brigade'] = '1'
        loc['VehicleNumber'] = line[-2]
        buses.append(loc)

    # overspeeding lines
    for line in LINES[:len(LINES) // 2]:
        loc = {}
        loc['Lines'] = line
        loc['Lat'] = 52.2163576442883
        loc['Lon'] = 20.99128337964515
        loc['Time'] = '2024-02-16 09:15:41'
        loc['Brigade'] = '1'
        loc['VehicleNumber'] = line[-2]
        buses.append(loc)

    # not overspeeding lines
    for line in LINES[len(LINES) // 2:]:
        loc = {}
        loc['Lines'] = line
        loc['Lat'] = 52.21599054475676
        loc['Lon'] = 20.982646082482425
        loc['Time'] = '2024-02-16 09:15:41'
        loc['Brigade'] = '1'
        loc['VehicleNumber'] = line[-2]
        buses.append(loc)

    with open('test-buses.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(buses))

def prepare_test_schedule():
    ''' Prepare mock data for bus schedule. '''
    schedule = []
    for line in LINES[len(LINES) // 2:]:
        schedule.append({
            'Line': line,
            'BusstopID': BUSSTOP_ID,
            'BusstopNr': 5,
            'Time': '09:15:00',
            'Brigade': 1,
            'Direction': 'Pomnik Lotnika' 
        })

    for line in LINES[:len(LINES) // 2]:
        schedule.append({
            'Line': line,
            'BusstopID': BUSSTOP_ID,
            'BusstopNr': 5,
            'Time': '09:10:00',
            'Brigade': 1,
            'Direction': 'Pomnik Lotnika'
        })

    schedule = pd.DataFrame(schedule)
    schedule['Line'] = schedule['Line'].astype(str)
    schedule.to_csv('test-schedule.csv', index=False)

def prepare_test_bus_stops():
    ''' Prepare mock data for bus stops.'''
    bus_stop = {
        'BusstopID': BUSSTOP_ID,
        'BusstopNr': 5,
        'Latitude': 52.21599054475676,
        'Longitude': 20.982646082482425,
        'Direction': 'Pomnik Lotnika'
    }

    with open('test-bus-stops.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps([bus_stop]))

if __name__ == '__main__':
    prepare_test_buses()
    prepare_test_schedule()
    prepare_test_bus_stops()
