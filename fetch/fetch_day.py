''' Fetch bus localization data from all the day. '''
import json
import os
from datetime import datetime
import time
import pandas as pd
import requests

API_KEY = os.environ.get('WARSAW_DATA_API_KEY')
URL = f'https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id= \
        f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1'

def get_current_localization():
    ''' Get current bus localization data from Warsaw Data API.'''
    response = requests.get(URL, timeout=10)
    if response.status_code != 200:
        print('Error:', response.status_code)
        return []
    data = response.json()
    data = data['result']
    if isinstance(data, str): # why status code is 200 in this case?
        return []
    return data

def fetch_hour():
    ''' Fetch data for one hour and save it to a file. '''
    buses = []
    hour = datetime.now().hour

    now = datetime.now()
    while now.hour == hour:
        buses = buses + get_current_localization()
        time.sleep(15 - (datetime.now() - now).seconds)
        now = datetime.now()

    data = pd.DataFrame(buses)
    data = data.drop_duplicates()

    with open(f'../data/buses-{hour}.json', 'w', encoding='utf-8') as f:
        f.write(data.to_json(orient='records'))

def fetch_day():
    ''' Fetch data for all the day. '''
    for _ in range(24):
        fetch_hour()

def main():
    ''' Main function. '''
    fetch_day()

if __name__ == "__main__":
    main()
    