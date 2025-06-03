#project3_methods.py

import json
import urllib.request
import urllib.parse
from geopy.geocoders import Nominatim
import datetime

def read_input() -> str:
    'reads the input'
    return input()

def get_location_name(terms: list[str]) -> str:
    'gets the name of the location who\'s weather we\'re considering'
    return_string = ''
    for term in terms:
        return_string += term + ' '
    return return_string[:len(return_string) - 1]

def air_temp_query(info: list[str]) -> list[str]:
    'returns the query info for air temp queries'
    q = ['air_temp']
    q.extend(info)
    return q

def feel_temp_query(info: list[str]) -> list[str]:
    'returns the query info for feel temp queries'
    q = ['feel_temp']
    q.extend(info)
    return q

def humidity_query(info: list[str]) -> list[str]:
    'returns the query info for humidity queries'
    q = ['humidity']
    q.extend(info)
    return q

def wind_query(info: list[str]) -> list[str]:
    'returns the query info for wind queries'
    q = ['wind']
    q.extend(info)
    return q

def precipitation_query(info: list[str]) -> list[str]:
    'returns the query info for precipitation queries'
    q = ['precipitation']
    q.extend(info)
    return q

def query_action(queries: list[str]) -> list[str]:
    'determines the info for each query'
    if queries[0] == 'TEMPERATURE':
        if queries[1] == 'AIR':
            return air_temp_query(queries[2:])
        elif queries[1] == 'FEEL':
            return feel_temp_query(queries[2:])
    elif queries[0] == 'HUMIDITY':
        return humidity_query(queries[1:])
    elif queries[0] == 'WIND':
        return wind_query(queries[1:])
    elif queries[0] == 'PRECIPITATION':
        return precipitation_query(queries[1:])

def create_query_list() -> list[str]:
    'creates a list of lists, with each internal list containing each query and its info'
    output = []
    while True:
        query = read_input()
        if query == 'NO MORE QUERIES':
            query = read_input()
            output.append(query)
            break
        queries = query_action(query.split())
        output.append(queries)
    return output

def handle_input(response: str) -> list[str]:
    'reads the queries\' input input'
    if response.split()[1] == 'NOMINATIM':
        response = read_input()
        if response.split()[1] == 'NWS':
            return create_query_list()
        elif response.split()[1] == 'FILE':
            return create_query_list()
    elif response.split()[1] == 'FILE':
        if response.split()[1] == 'NWS':
            return create_query_list()
        elif response.split()[1] == 'FILE':
            return create_query_list()

def unit_conversion(cur_temp: float, cur_temp_unit: str, temp_unit: str) -> float:
    'converts temperature to the correct unit'
    if cur_temp_unit == temp_unit:
        return cur_temp
    elif temp_unit == 'F':
        return cur_temp * 1.8 + 32
    elif temp_unit == 'C':
        return (cur_temp - 32) * 5 / 9

def format_rounding(x: float) -> str:
    'rounds all numbers to 4 digits'
    x = round(x, 4)
    s = str(x)
    parts = s.split('.')
    if len(parts[1]) ==  4:
        return str(x)
    else:
        extra_zeros = ''
        for i in range(4-len(parts[1])):
            extra_zeros += '0'
        return parts[0] + '.' + parts[1] + extra_zeros

def process_air_temp(info: list[str], forecast_json: dict) -> str:
    'determines the response to the air temp query'
    return_temp = 0
    if info[2] == 'MAX':
        return_temp = -10000
    elif info[2] == 'MIN':
        return_temp = 10000
    time = ''
    index = 0
    for i in range(int(info[1])):
        cur_temp = forecast_json['properties']['periods'][i]['temperature']
        cur_temp_unit = forecast_json['properties']['periods'][i]['temperatureUnit']
        cur_temp = unit_conversion(cur_temp, cur_temp_unit, info[0])
        if info[2] == 'MAX':
            if cur_temp > return_temp:
                return_temp = cur_temp
                time = forecast_json['properties']['periods'][i]['endTime']
        elif info[2] == 'MIN':
            if cur_temp < return_temp:
                return_temp = cur_temp
                time = forecast_json['properties']['periods'][i]['endTime']
    return_time = datetime.datetime.fromisoformat(time)
    return_time = return_time.astimezone(datetime.timezone.utc)
    return_time = return_time.isoformat().replace('+00:00', 'Z')
    return return_time + ' ' + format_rounding(float(return_temp))

def get_feel_temp(t: float, h: float, w: float) -> float:
    'calculates the feel temp based on air temp, humidity and wind'
    if t >= 68:
        feel_temp = -42.379 + 2.04901523 * t + 10.14333127 * h -0.22475541 * t * h - 0.00683783 * t * t \
                    - 0.05481717 * h * h + 0.00122874 * t * t * h + 0.00085282 * t * h * h \
                    - 0.00000199 * t * t * h * h
        return feel_temp
    elif t <= 50 and w > 3:
        feel_temp = 35.74 + 0.6215 * t -35.75 * pow(w, 0.16) + 0.4275 * t * pow(w, 0.16)
        return feel_temp
    else:
        return t

def process_feel_temp(info: list[str], forecast_json: dict) -> str:
    'determines the response to the air feel query'
    return_temp = 0
    if info[2] == 'MAX':
        return_temp = -10000
    elif info[2] == 'MIN':
        return_temp = 10000
    time = ''
    index = 0
    for i in range(int(info[1])):
        cur_temp = forecast_json['properties']['periods'][i]['temperature']
        cur_temp_unit = forecast_json['properties']['periods'][i]['temperatureUnit']
        feel_temp = unit_conversion(cur_temp, cur_temp_unit, 'F')
        cur_humidity = forecast_json['properties']['periods'][i]['relativeHumidity']['value']
        cur_wind = forecast_json['properties']['periods'][i]['windSpeed']
        cur_wind = float(cur_wind.split(' ')[0])
        feel_temp = get_feel_temp(feel_temp, cur_humidity, cur_wind)
        cur_temp = unit_conversion(feel_temp, cur_temp_unit, info[0])
        if info[2] == 'MAX':
            if cur_temp > return_temp:
                return_temp = cur_temp
                time = forecast_json['properties']['periods'][i]['endTime']
        elif info[2] == 'MIN':
            if cur_temp < return_temp:
                return_temp = cur_temp
                time = forecast_json['properties']['periods'][i]['endTime']
    return_time = datetime.datetime.fromisoformat(time)
    return_time = return_time.astimezone(datetime.timezone.utc)
    return_time = return_time.isoformat().replace('+00:00', 'Z')
    return return_time + ' ' + format_rounding(float(return_temp))


def process_humidity(info: list[str], forecast_json: dict) -> str:
    'determines the response to the humidity query'
    return_humidity = 0
    if info[1] == 'MAX':
        return_humidity = -1
    elif info[1] == 'MIN':
        return_humidity = 101
    time = ''
    index = 0
    for i in range(int(info[0])):
        cur_humidity = forecast_json['properties']['periods'][i]['relativeHumidity']['value']
        if info[1] == 'MAX':
            if cur_humidity > return_humidity:
                return_humidity = cur_humidity
                time = forecast_json['properties']['periods'][i]['endTime']
        elif info[1] == 'MIN':
            if cur_humidity < return_humidity:
                return_humidity = cur_humidity
                time = forecast_json['properties']['periods'][i]['endTime']
    return_time = datetime.datetime.fromisoformat(time)
    return_time = return_time.astimezone(datetime.timezone.utc)
    return_time = return_time.isoformat().replace('+00:00', 'Z')
    return return_time + ' ' + format_rounding(float(return_humidity)) + '%'

def process_wind(info: list[str], forecast_json: dict) -> str:
    'determines the response to the wind query'
    return_wind = 0
    if info[1] == 'MAX':
        return_wind = -1
    elif info[1] == 'MIN':
        return_wind = 1000
    time = ''
    index = 0
    for i in range(int(info[0])):
        cur_wind = forecast_json['properties']['periods'][i]['windSpeed']
        cur_wind = float(cur_wind.split(' ')[0])
        if info[1] == 'MAX':
            if cur_wind > return_wind:
                return_wind = cur_wind
                time = forecast_json['properties']['periods'][i]['endTime']
        elif info[1] == 'MIN':
            if cur_wind < return_wind:
                return_wind = cur_wind
                time = forecast_json['properties']['periods'][i]['endTime']
    return_time = datetime.datetime.fromisoformat(time)
    return_time = return_time.astimezone(datetime.timezone.utc)
    return_time = return_time.isoformat().replace('+00:00', 'Z')
    return return_time + ' ' + format_rounding(float(return_wind)) + ' MPH'

def process_precipitation(info: list[str], forecast_json: dict) -> str:
    'determines the response to the precipitation query'
    return_precipitation = 0
    if info[1] == 'MAX':
        return_precipitation = -1
    elif info[1] == 'MIN':
        return_precipitation = 101
    time = ''
    index = 0
    for i in range(int(info[0])):
        cur_precipitation = forecast_json['properties']['periods'][i]['probabilityOfPrecipitation']['value']
        if info[1] == 'MAX':
            if cur_precipitation > return_precipitation:
                return_precipitation = cur_precipitation
                time = forecast_json['properties']['periods'][i]['endTime']
        elif info[1] == 'MIN':
            if cur_precipitation < return_precipitation:
                return_precipitation = cur_precipitation
                time = forecast_json['properties']['periods'][i]['endTime']
    return_time = datetime.datetime.fromisoformat(time)
    return_time = return_time.astimezone(datetime.timezone.utc)
    return_time = return_time.isoformat().replace('+00:00', 'Z')
    return return_time + ' ' + format_rounding(float(return_precipitation)) + '%'

def get_lat_str(lat) -> str:
    'converts the latitude to its string output form'
    if lat < 0:
        return str(0 - lat) + '/S '
    else:
        return str(lat) + '/N '

def get_long_str(long) -> str:
    'converts the longitude to its string output form'
    if long < 0:
        return str(0 - long) + '/W'
    else:
        return str(long) + '/E'

def get_json_text(url: str) -> dict:
    'returns json text from a url'
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    json_text = response.read().decode(encoding = 'utf-8')
    return json.loads(json_text)

def get_location_coords(location: str) -> list[float]:
    'determines the longitutde and latitude for a certain location'
    locator = Nominatim(user_agent = 'https://www.ics.uci.edu/~thornton/icsh32/ProjectGuide/Project3, dbita@uci.edu')
    loc = locator.geocode(location)
    request = urllib.request.Request('https://nominatim.openstreetmap.org/status')
    response = urllib.request.urlopen(request)
    json_text = response.read().decode(encoding = 'utf-8')
    if not json_text == 'OK':
        print('FAILED')
        print('NOT 200')
        quit()
    return [loc.latitude, loc.longitude]

def get_reverse_geocoding(coords: list[float]) -> str:
    'determines the location name based on the longitude and latitude'
    locator = Nominatim(user_agent = 'https://www.ics.uci.edu/~thornton/icsh32/ProjectGuide/Project3, dbita@uci.edu')
    loc = locator.reverse(coords)
    return loc

def process_queries(location: str, coords: list[float], queries: list[str], forecast_json: dict) -> list[str]:
    'creates the string with the results of each query'
    output = []
    for query in queries:
        if query[0] == 'air_temp':
            output.append(process_air_temp(query[1:], forecast_json))
        elif query[0] == 'feel_temp':
            output.append(process_feel_temp(query[1:], forecast_json))
        elif query[0] == 'humidity':
            output.append(process_humidity(query[1:], forecast_json))
        elif query[0] == 'wind':
            output.append(process_wind(query[1:], forecast_json))
        elif query[0] == 'precipitation':
            output.append(process_precipitation(query[1:], forecast_json))
    return output

def find_avg_coords(forecast_json: dict) -> list[float]:
    'determines the average coordinates of the forecast locations'
    coord_list = forecast_json['geometry']['coordinates']
    latitude = 0
    longitude = 0
    divisor = 0
    points = {}
    for l in coord_list:
        for coord_pair in l:
            cur_lat = coord_pair[0]
            cur_long = coord_pair[1]
            if not (cur_long, cur_lat) in points:
                latitude += cur_lat
                longitude += cur_long
                divisor += 1
                points[cur_long, cur_lat] = True
    return [longitude/divisor, latitude/divisor]
