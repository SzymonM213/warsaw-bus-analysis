from fetch_data import get_new_data
import folium
from geopy.distance import geodesic
import geocoder

RADIUS = 2  # in kilometers

def get_current_location():
    g = geocoder.ip('me')
    return g.latlng 

def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

def main():
    buses = get_new_data()
    user_location = get_current_location()
    bus_map = folium.Map(location=user_location, zoom_start=15)
    for bus in buses:
        if calculate_distance(user_location, (bus['Lat'], bus['Lon'])) < RADIUS:
            # icon_html = f'''
            #             <div style="background-color: white; border: 2px solid blue; border-radius: 5px; width: 30px; height: 10px;">
            #                 <span style="color: blue; font-weight: bold;">{bus['Lines']}</span>
            #             </div>
            #             '''
            
            icon_html = f'''
                        <div style="background-color: white; border: 2px solid blue; border-radius: 5px; width: 30px; height: 20px; display: flex; justify-content: center; align-items: center;">
                            <span style="color: blue; font-weight: bold;">{bus['Lines']}</span>
                        </div>
                        '''

            folium.Marker((bus['Lat'], bus['Lon']), icon=folium.DivIcon(html=icon_html)).add_to(bus_map)
    bus_map.save('bus_map.html')

if __name__ == "__main__":
    main()