import json
import requests
import os
from datetime import datetime, timedelta
import time

API_KEY = os.environ.get('WARSAW_DATA_API_KEY')
URL = f'https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1'

def get_new_data():
    response = requests.get(URL)
    if response.status_code != 200:
        print('Error:', response.status_code)
        return []
    data = response.json()
    data = data['result']
    if type(data) == str: # why status code is 200 in this case?
        return []
    return data

def main():
    buses = []
    beginning = datetime.now()

    now = datetime.now()
    while now - beginning < timedelta(hours=1):
        buses = buses + get_new_data()
        time.sleep(15 - (datetime.now() - now).seconds)
        now = datetime.now()

    with open(f'buses-{beginning.date()}_{beginning.time()}.json', 'w') as f:
        json.dump(buses, f)

if __name__ == "__main__":
    main()
    