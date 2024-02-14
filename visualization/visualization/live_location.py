''' This script is used to visualize the current location of buses in Warsaw. '''
import argparse
import folium
import geocoder
from utils import calculate_distance, get_current_localization, WARSAW_CENTER

RADIUS = 1  # in kilometers

def get_current_location():
    ''' Get the approximated location of the user. '''
    g = geocoder.ip('me')
    return g.latlng

def main():
    ''' Main function to visualize the buses. '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--coordinates", help="user's location",
                        default=WARSAW_CENTER[0], required=False)
    args = parser.parse_args()

    user_location = (float(args.coordinates.split(',')[0]), float(args.coordinates.split(',')[1]))
    print(f"User location: {user_location}")

    buses = get_current_localization()
    bus_map = folium.Map(location=user_location, zoom_start=15)
    for bus in buses:
        if calculate_distance(user_location, (bus['Lat'], bus['Lon'])) < RADIUS:
            icon_html = f'''
                        <div style="background-color: white; border: 2px solid blue; border-radius: 5px; width: 30px; height: 20px; display: flex; justify-content: center; align-items: center;">
                            <span style="color: blue; font-weight: bold;">{bus['Lines']}</span>
                        </div>
                        '''

            folium.Marker((bus['Lat'], bus['Lon']),
                          icon=folium.DivIcon(html=icon_html)).add_to(bus_map)
    bus_map.save('../maps/bus_map.html')

if __name__ == "__main__":
    main()
