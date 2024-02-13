import json
import pandas as pd
from utils import calculate_distance, get_address_components, date_to_seconds
from utils import WARSAW_CENTER
from datetime import datetime
import folium
from typing import Dict, Set
from tqdm import tqdm

class Street:
    def __init__(self, name: str, district: str, city: str):
        self.name = name
        self.district = district
        self.city = city

    def __str__(self):
        return f'{self.name}, {self.district}, {self.city}'
    
    def __repr__(self):
        return f'{self.name}, {self.district}, {self.city}'
    
    def __eq__(self, other):
        return self.name == other.name and self.district == other.district and self.city == other.city
    
    def __hash__(self):
        return hash((self.name, self.district, self.city))

def calculate_speed(coord1: tuple[float, float], coord2: tuple[float, float], time1: float, time2: float) -> float:
    distance = calculate_distance(coord1, coord2)
    if distance == 0:
        return 0
    
    time = (date_to_seconds(time2) - date_to_seconds(time1)) / 3600
    return distance / time

def main():

    result: Dict[str, Set[str]] = {}

    with open('buses-2024-02-12_19:15:40.464347.json') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    grouped = df.groupby('VehicleNumber')

    m = folium.Map(location=WARSAW_CENTER, zoom_start=12)
    for vehicle, group in tqdm(grouped):
        group = group.sort_values('Time')

        # drop rows with the same time (because of duplicates or some inaccuracy)
        group = group.drop_duplicates('Time')

        group['PrevLon'] = group['Lon'].shift(1)
        group['PrevLat'] = group['Lat'].shift(1)
        group['PrevTime'] = group['Time'].shift(1)

        # fill first rows with actual values
        group['PrevLon'].fillna(group['Lon'].iloc[0], inplace=True)
        group['PrevLat'].fillna(group['Lat'].iloc[0], inplace=True)
        group['PrevTime'].fillna(group['Time'].iloc[0], inplace=True)

        group['Speed'] = group.apply(lambda row: calculate_speed((row['PrevLat'], row['PrevLon']), (row['Lat'], row['Lon']), row['PrevTime'], row['Time']), axis=1)

        for i in range(1, len(group)):
            if group['Speed'].iloc[i] > 50:
                try:
                    street = Street(*get_address_components(group['Lat'].iloc[i], group['Lon'].iloc[i]))
                except:
                    continue
                if street not in result:
                    result[street] = {vehicle}
                else:
                    result[street].add(vehicle)
                folium.Marker([group['Lat'].iloc[i], group['Lon'].iloc[i]], popup=f'Speed: {group["Speed"].iloc[i]}').add_to(m)
    
    # sort the result by the size of the set
    result = dict(sorted(result.items(), key=lambda item: len(item[1]), reverse=True))

    m.save('maps/overspeed.html')

    # print first 10 streets with the most overspeeding vehicles
    for street, vehicles in list(result.items())[:10]:
        print(f'{street}: {len(vehicles)} vehicles: {vehicles}')

if __name__ == '__main__':
    main()