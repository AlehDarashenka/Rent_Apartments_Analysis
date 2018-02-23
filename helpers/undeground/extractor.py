import configparser
import json
import time
import os

from geopy import Yandex

# constants
STATION_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'undeground_stations.ini')
DUMP_JSON_FILE = os.path.join(os.path.dirname(__file__), 'stations.json')

geolocator = Yandex()


def dump_coordinates_to_file(path):
    config = configparser.ConfigParser()
    config.read(STATION_NAMES_PATH)

    lines = {'blue': config['STATIONS']['BLUE_LINE'].split(','),
             'red': config['STATIONS']['RED_LINE'].split(',')}

    # dump lines as json object
    data = {}
    for line_name, line_stations in lines.items():
        # initialize with empty array
        data[line_name] = []
        for station in line_stations:
            # get coordinates for a station
            # time - have to wait some time due to service requirements
            time.sleep(3)
            location = geolocator.geocode("{} метро Минск".format(station))

            data[line_name].append({
                'name': station,
                'longitude': location.longitude,
                'latitude': location.latitude
            })

    # dump python dict into json
    with open(path, 'w') as dump_file:
        json.dump(data, dump_file)


def get_stations():
    if not os.path.isfile(DUMP_JSON_FILE):
        dump_coordinates_to_file(DUMP_JSON_FILE)

    with open(DUMP_JSON_FILE, 'r') as source_file:
        return json.load(source_file)