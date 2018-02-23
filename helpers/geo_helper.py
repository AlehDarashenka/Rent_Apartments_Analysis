import time

from geopy.geocoders import Yandex
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.distance import great_circle

from .undeground.extractor import get_stations

MINSK_CENTER = "53.9045, 27.5615"

geolactor = Yandex()
stations = get_stations()


class GeoPoint:
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude

        location = None
        while location is None:
            try:
                location = geolactor.reverse((latitude, longitude))
            except GeocoderTimedOut:
                time.sleep(10)
            except GeocoderUnavailable:
                time.sleep(10)

        if location is not None and len(location) > 0:
            longest_location = max(location, key=lambda row: len(row.address or ''))
            self.address = longest_location.address.split(',') or []

    def get_city_region(self):
        for item in self.address:
            if 'микрорайон' not in item and 'район' in item:
                return item.replace('район', '').strip()

    def get_city_sub_region(self):
        for item in self.address:
            if 'микрорайон' in item:
                return item.replace('микрорайон', '').strip()

    def get_distance_to_city_center(self):
        return int(great_circle(MINSK_CENTER, (self.latitude, self.longitude)).meters)

    def get_nearest_station_name_and_distance(self):
        nearest_station, min_distance = None, float('inf')

        for line in stations:
            line_nearest_station, line_min_distance = None, float('inf')

            for station in stations[line]:
                distance = int(great_circle((station['latitude'], station['longitude']),
                                            (self.latitude, self.longitude)).meters)

                if distance < line_min_distance:
                    line_nearest_station = station['name']
                    line_min_distance = distance
                else:
                    break

            if line_min_distance < min_distance:
                min_distance = line_min_distance
                nearest_station = line_nearest_station

        return nearest_station, min_distance


