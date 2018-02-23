import unittest

from helpers.geo_helper import GeoPoint


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.point = GeoPoint(53.847522, 27.482108)

    def test_city_region(self):
        self.assertEqual(self.point.get_city_region(), 'Московский')

    def test_city_sub_region(self):
        sub_region = self.point.get_city_sub_region()
        self.assertEqual(sub_region, 'Брилевичи')

    def test_nearest_station(self):
        station, distance = self.point.get_nearest_station_name_and_distance()

        self.assertEqual(station, 'Малиновка')

if __name__ == '__main__':
    unittest.main()