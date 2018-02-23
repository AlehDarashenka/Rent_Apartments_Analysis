import pandas as pd

from helpers.geo_helper import GeoPoint


def fetch_geo_inform(row):
    try:
        print(row['latitude'], row['longitude'])

        geo_point = GeoPoint(row['latitude'], row['longitude'])
        station, distance = geo_point.get_nearest_station_name_and_distance()

        return pd.Series([geo_point.get_distance_to_city_center(),
                          station,
                          distance], index=['До центра', 'Метро', 'До метро'])
    except Exception:
        return pd.Series([])

if __name__ == '__main__':
    data = pd.read_csv('../data/realt.csv')
    geo_columns = data.apply(fetch_geo_inform, axis='columns')
    result = pd.concat([data, geo_columns], axis=1)

    result.to_csv('../data/realt_updated.csv')
