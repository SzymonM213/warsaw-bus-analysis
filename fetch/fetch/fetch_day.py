''' Fetch bus localization data from all the day. '''
import json
import os
from datetime import datetime
import time
from .utils import get_current_localization

API_KEY = os.environ.get('WARSAW_DATA_API_KEY')
URL = f'https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id= \
        f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1'

def fetch_hour():
    ''' Fetch data for one hour and save it to a file. '''
    buses = []
    hour = datetime.now().hour

    now = datetime.now()
    while now.hour == hour:
        buses = buses + get_current_localization()
        time.sleep(15 - (datetime.now() - now).seconds)
        now = datetime.now()

    with open(f'../data/buses-{hour}.json', 'w', encoding='utf-8') as f:
        json.dump(buses, f)

def fetch_day():
    ''' Fetch data for all the day. '''
    for _ in range(24):
        fetch_hour()

def main():
    ''' Main function. '''
    fetch_day()

if __name__ == "__main__":
    main()
    