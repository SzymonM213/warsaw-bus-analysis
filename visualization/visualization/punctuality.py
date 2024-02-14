''' Module for calculating the punctuality of the buses. '''
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from .utils import calculate_distance

def get_line_schedule(line: str) -> pd.DataFrame:
    ''' Get the schedule for the given line. '''
    schedule = pd.read_csv('../data/schedule.csv', low_memory=False)
    schedule['BusstopID'] = schedule['BusstopID'].astype(str)
    schedule['Brigade'] = schedule['Brigade'].astype(int)
    return schedule[schedule['Line'] == line]

def get_line_bus_stops(line: str) -> pd.DataFrame:
    ''' Get all the bus stops for the given line.'''

    bus_stops = pd.read_json('../data/bus_stops.json')
    line_schedule = get_line_schedule(line)
    line_bus_stops = line_schedule[['BusstopID', 'BusstopNr']].drop_duplicates()
    line_bus_stops['BusstopID'] = line_bus_stops['BusstopID'].astype(str)
    line_bus_stops = pd.merge(line_bus_stops, bus_stops, on=['BusstopID', 'BusstopNr'], how='left')
    return line_bus_stops

def get_line_stops(line: str, localizations: pd.DataFrame) -> pd.DataFrame:
    ''' For given line and localizations, get all the stops and the time. '''
    localizations = localizations[localizations['Lines'] == line]
    localizations = localizations.drop_duplicates()

    bus_stops = pd.read_json('../data/bus_stops.json')
    bus_stops = get_line_bus_stops(line).drop_duplicates()

    if bus_stops.empty:
        return pd.DataFrame()

    # merge localizations with the minimal distance to the bus stop
    result = []
    for _, row in localizations.iterrows():
        distances = bus_stops.apply(lambda x, r=row:
                                    calculate_distance((x['Latitude'], x['Longitude']),
                                                       (r['Lat'], r['Lon'])), axis=1)
        min_distance = distances.min()
        min_distance_index = distances.idxmin()
        min_distance_bus_stop = bus_stops.loc[min_distance_index]
        result.append({'Line': line,
                       'Latitude': row['Lat'],
                       'Longitude': row['Lon'],
                       'BusstopID': min_distance_bus_stop['BusstopID'],
                       'BusstopNr': min_distance_bus_stop['BusstopNr'],
                       'Brigade': row['Brigade'],
                       'Time': row['Time'].split(' ')[1], # time without date
                       'Distance': min_distance})

    result = pd.DataFrame(result)
    result = result[result['Distance'] < 0.025]
    result['Time'] = pd.to_datetime(result['Time'], format='%H:%M:%S').dt.time
    result['Brigade'] = result['Brigade'].astype(int)
    return result.sort_values(by='Time')

def get_stop_schedule(line: str, line_stops: pd.DataFrame) -> pd.DataFrame:
    '''for each stop, get the scheduled time and the actual time'''
    schedule = get_line_schedule(line)
    schedule = schedule.sort_values(by='Time')

    schedule['Time'] = schedule['Time'].apply(lambda x: '00' + x[2:] if int(x[:2]) >= 24 else x)
    schedule['Time'] = pd.to_datetime(schedule['Time'], format='%H:%M:%S').dt.time

    result = []
    for _, stop in line_stops.iterrows():
        scheduled_stop = schedule[(schedule['Brigade'] == stop['Brigade']) \
                                  & (schedule['Time'] < stop['Time']) \
                                  & (schedule['BusstopID'] == stop['BusstopID']) \
                                  & (schedule['BusstopNr'] == stop['BusstopNr'])]
        if scheduled_stop.empty:
            continue
        scheduled_stop = scheduled_stop.iloc[-1]
        scheduled_stop['ScheduledTime'] = scheduled_stop['Time']
        scheduled_stop['Time'] = stop['Time']

        delay = datetime.combine(datetime.today(), scheduled_stop['Time']) - \
                datetime.combine(datetime.today(), scheduled_stop['ScheduledTime'])
        scheduled_stop['Delay'] = delay.seconds / 60
        scheduled_stop.drop(['Unnamed: 0'], inplace=True)
        if scheduled_stop['Delay'] < 30:
            # big delays results from the fact that the bus was
            # near the bus stop in different direction
            result.append(scheduled_stop)

    result = pd.DataFrame(result)
    result.drop_duplicates(subset=['BusstopID', 'BusstopNr', 'Brigade', 'ScheduledTime'],
                           keep='first', inplace=True)
    return result

def get_delays(hour: int) -> pd.DataFrame:
    ''' Find all the delays for the given hour. '''
    localizations = pd.read_json(f'../data/buses-{hour}.json')
    lines = localizations['Lines'].unique()
    delays = []
    for line in tqdm(lines):
        line_stops = get_line_stops(line, localizations)
        line_delays = get_stop_schedule(line, line_stops)
        delays.append(line_delays)
    delays = pd.concat(delays)
    return delays

def filter_delays(delays: pd.DataFrame, threshold: int) -> pd.DataFrame:
    ''' Filter delays that are greater than the threshold. '''
    return delays[delays['Delay'] > threshold]
