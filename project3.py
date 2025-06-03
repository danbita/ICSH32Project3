#project3.py

from project3_methods import *

def run() -> None:
    'runs the code'
    response = read_input()
    location = get_location_name(response.split(' ')[2:])
    coords = get_location_coords(location)
    forecast_url = 'https://api.weather.gov/points/' + str(coords[0]) + ',' + str(coords[1])
    forecast_json = get_json_text(forecast_url)
    data_url = forecast_json['properties']['forecastHourly']
    forecast_json = get_json_text(data_url)
    avg_coords = find_avg_coords(forecast_json)
    output = 'TARGET ' + get_lat_str(coords[0]) + get_long_str(coords[1]) + '\n'
    output += 'FORECAST ' + get_lat_str(avg_coords[0]) + get_long_str(avg_coords[1]) + '\n'
    output += str(get_reverse_geocoding(avg_coords))
    queries = handle_input(response)
    queries_output = process_queries(location, coords, queries, forecast_json)
    print(output)
    for line in queries_output:
        print(line)
    print('**Forward geocoding data from OpenStreetMap')
    print('**Reverse geocoding data from OpenStreetMap')
    print('**Real-time weather data from National Weather Service, United States Department of Commerce')

if __name__ == '__main__':
    run()
