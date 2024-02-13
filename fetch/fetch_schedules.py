import json
import requests
import os
from typing import List, Dict
import pandas as pd
from tqdm import tqdm

API_KEY = os.environ.get('WARSAW_DATA_API_KEY')
URL1 = f'https://api.um.warszawa.pl/api/action/dbtimetable_get'
URL2 = f'https://api.um.warszawa.pl/api/action/dbstore_get'

def get_bus_stops() -> List[Dict[str, str]]:
    params = {
        'id': 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3',
        'apikey': API_KEY,
    }
    response = requests.get(URL2, params=params)
    data = response.json()
    data = data['result']

    result: List[Dict[str, str]] = []
    for bus_stop in data:
        bus_stop = bus_stop['values']
        result.append({'BusstopID': bus_stop[0]['value'], 
                       'BusstopNr': bus_stop[1]['value'],
                       'BusstopName': bus_stop[2]['value'], 
                       'Latitude': bus_stop[4]['value'], 
                       'Longitude': bus_stop[5]['value'], 
                       'Direction': bus_stop[6]['value']})
    return result

def get_lines(busstopId: str, busstopNr: str) -> List[str]:
    params = {
        'id': '88cd555f-6f31-43ca-9de4-66c479ad5942',
        'apikey': API_KEY,
        'busstopId': busstopId,
        'busstopNr': busstopNr,
    }
    response = requests.get(URL1, params=params)
    data = response.json()
    data = data['result']

    result: List[str] = []
    for line in data:
        line = line['values']
        result.append(line[0]['value'])
    return result

def get_schedule(line: str, busstopId: str, busstopNr: str) -> List[Dict[str, str]]:
    params = {
        'id': 'e923fa0e-d96c-43f9-ae6e-60518c9f3238',
        'apikey': API_KEY,
        'busstopId': busstopId,
        'busstopNr': busstopNr,
        'line': line,
    }
    response = requests.get(URL1, params=params)
    data = response.json()

    result: List[Dict[str, str]] = []
    for event in data['result']:
        event = event['values']
        result.append({'Line': line,
                       'BusstopID': busstopId, 
                       'BusstopNr': busstopNr, 
                       'Brigade': event[2]['value'], 
                       'Direction': event[3]['value'], 
                       'Time': event[5]['value']})
    return result

def save_bus_stops():
    with open('../data/bus_stops.json', 'w') as f:
        json.dump(get_bus_stops(), f)

def main():
    with open('../data/bus_stops.json', 'r') as f:
        bus_stops = json.load(f)

    result = []
    for bus_stop in tqdm(bus_stops):
        lines = get_lines(bus_stop['BusstopID'], bus_stop['BusstopNr'])
        for line in lines:
            result = result + get_schedule(line, bus_stop['BusstopID'], bus_stop['BusstopNr'])
    df = pd.DataFrame(result)
    df.to_csv('../data/schedule.csv')
        

if __name__ == "__main__":
    main()