''' This module contains utility functions for the visualization module. '''
from datetime import datetime
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests

WARSAW_CENTER = (52.22977, 21.01178)
API_KEY = os.environ.get('WARSAW_DATA_API_KEY')
URL = f'https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id= \
        f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={API_KEY}&type=1'

def calculate_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    ''' Calculate distance between two coordinates.'''
    return geodesic(coord1, coord2).kilometers

def coordinates_to_street(latitude, longitude):
    ''' Get street name from coordinates. '''
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    address = location.address
    return address

def date_to_seconds(date: str) -> float:
    ''' Convert date to seconds. '''
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp()

def get_address_components(latitude, longitude):
    ''' Get street name, district and city from coordinates. '''
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    address = location.address
    address_components = address.split(', ')

    street_name = address_components[0] if len(address_components) > 1 else ''
    district = address_components[-5] if len(address_components) > 4 else ''
    city = address_components[-4] if len(address_components) > 3 else ''

    return street_name, district, city

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
