''' This module contains functions for counting overspeeding vehicles and plotting the results. '''
import json
import time
from typing import Dict, Set, Tuple
import pandas as pd
import folium
import matplotlib.pyplot as plt
from tqdm import tqdm
from .utils import calculate_distance, get_address_components
from .utils import WARSAW_CENTER, date_to_seconds

class Street:
    ''' Class representing a street. '''
    def __init__(self, name: str, district: str, city: str):
        self.name = name
        self.district = district
        self.city = city

    def __str__(self):
        return f'{self.name}, {self.district}, {self.city}'

    def __repr__(self):
        return f'{self.name}, {self.district}, {self.city}'

    def __eq__(self, other):
        return self.name == other.name and self.district == other.district \
               and self.city == other.city

    def __hash__(self):
        return hash((self.name, self.district, self.city))

def calculate_speed(coord1: tuple[float, float], coord2: tuple[float, float],
                    time1: float, time2: float) -> float:
    ''' Calculate the speed between two coordinates. '''
    distance = calculate_distance(coord1, coord2)
    if distance == 0:
        return 0
    time_delta = (date_to_seconds(time2) - date_to_seconds(time1)) / 3600
    return distance / time_delta

def calculate_speeds(group: pd.DataFrame) -> pd.DataFrame:
    group['PrevLon'] = group['Lon'].shift(1)
    group['PrevLat'] = group['Lat'].shift(1)
    group['PrevTime'] = group['Time'].shift(1)

    # fill first rows with actual values
    group['PrevLon'].fillna(group['Lon'].iloc[0], inplace=True)
    group['PrevLat'].fillna(group['Lat'].iloc[0], inplace=True)
    group['PrevTime'].fillna(group['Time'].iloc[0], inplace=True)

    group['Speed'] = group.apply(lambda row: calculate_speed((row['PrevLat'], row['PrevLon']),
                                                                (row['Lat'], row['Lon']),
                                                                row['PrevTime'], row['Time']),
                                                                axis=1)
    return group

def get_street(Lat: float, Lon: float) -> Street:
    ''' Get street from coordinates. '''
    return Street(*get_address_components(Lat, Lon))

def count_overspeeding_vehicles(path_to_localizations: str, save_map: bool) -> Tuple[int, Dict[str, int]]:
    ''' Count overspeeding vehicles and their number on each street. '''
    result: Dict[str, Set[str]] = {}
    overspeeding_vehicles: Set[str] = set()

    with open(path_to_localizations, 'r', encoding='utf-8') as f:
        data = json.load(f)
    localizations = pd.DataFrame(data)

    if save_map:
        m = folium.Map(location=WARSAW_CENTER, zoom_start=12)

    grouped = localizations.groupby('VehicleNumber')
    for vehicle, group in tqdm(grouped):
        group = group.sort_values('Time')
        # drop rows with the same time (because of duplicates or some inaccuracy)
        group = group.drop_duplicates('Time')
        group = calculate_speeds(group)
        for i in range(1, len(group)):
            if group['Speed'].iloc[i] > 50:
                overspeeding_vehicles.add(vehicle)
                street = get_street(group['Lat'].iloc[i], group['Lon'].iloc[i])
                if street not in result and street.name != '':
                    result[street] = {vehicle}
                elif street.name != '':
                    result[street].add(vehicle)

                if save_map:
                    folium.Marker([group['Lat'].iloc[i], group['Lon'].iloc[i]],
                                 popup=f'Speed: {group["Speed"].iloc[i]}').add_to(m)

    result = dict(sorted(result.items(), key=lambda item: len(item[1]), reverse=True))

    if save_map:
        m.save('maps/overspeed.html')

    return len(overspeeding_vehicles), result

def count_overspeeding_vehicles_from_hour(hour: int) -> Tuple[int, Dict[str, int]]:
    ''' Count overspeeding vehicles from the given hour. '''
    return count_overspeeding_vehicles(f'data/buses-{hour}.json', True)
