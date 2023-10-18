import json
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from core.settings.utils import absolute_path

from property.factories import (
    ProvinceFactory
)
from frontend.utils.parcel import find_province


def populate_layer_province_table(geom, name):
    query = (
        """
        INSERT INTO layer.zaf_provinces_small_scale
        (geom, adm1_en)
        VALUES(%s, %s);
        """
    )
    query_values = [geom.ewkt, name]
    with connection.cursor() as cursor:
        cursor.execute(query, query_values)


class TestParcelUtils(TestCase):

    def setUp(self):
        self.province1 = ProvinceFactory.create(name='ProvinceA')
        self.province2 = ProvinceFactory.create(name='ProvinceB')
        self.province3 = ProvinceFactory.create(name='ProvinceC')
        # insert provinces to layer.zaf_provinces_small_scale
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'geom_1.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][0]['geometry'])
            geom = GEOSGeometry(geom_str, srid=3857)
            populate_layer_province_table(geom, 'ProvinceA')
            geom_str = json.dumps(data['features'][1]['geometry'])
            geom = GEOSGeometry(geom_str, srid=3857)
            populate_layer_province_table(geom, 'ProvinceB')
        # get polygon to be searched
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'search_property.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][0]['geometry'])
            self.geom1 = GEOSGeometry(geom_str)
            geom_str = json.dumps(data['features'][1]['geometry'])
            self.geom2 = GEOSGeometry(geom_str)
        self.geom3 = GEOSGeometry("MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))", srid=3857)

    def test_find_province(self):
        # find exact match
        province = find_province(self.geom1, self.province3)
        self.assertEqual(province.id, self.province1.id)
        # find inside other province
        province = find_province(self.geom2, self.province3)
        self.assertEqual(province.id, self.province2.id)
        # find no match
        province = find_province(self.geom3, self.province3)
        self.assertEqual(province.id, self.province3.id)
