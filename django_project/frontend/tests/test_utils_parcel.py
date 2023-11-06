import json
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from core.settings.utils import absolute_path

from property.factories import (
    ProvinceFactory,
    PropertyFactory
)
from stakeholder.factories import organisationFactory
from frontend.tests.model_factories import UserF
from frontend.utils.parcel import find_province
from frontend.tasks.patch_province import patch_province_in_properties


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
        self.user_1 = UserF.create(username='test_1')
        self.organisation_1 = organisationFactory.create()
        self.province1 = ProvinceFactory.create(name='ProvinceA')
        self.province2 = ProvinceFactory.create(name='ProvinceB')
        self.province3 = ProvinceFactory.create(name='ProvinceC')
        self.province4 = ProvinceFactory.create(name='ProvinceD')
        # insert provinces to layer.zaf_provinces_small_scale
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'geom_1.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][0]['geometry'])
            geom = GEOSGeometry(geom_str, srid=3857)
            populate_layer_province_table(geom, self.province1.name)
            geom_str = json.dumps(data['features'][1]['geometry'])
            geom = GEOSGeometry(geom_str, srid=3857)
            populate_layer_province_table(geom, self.province2.name)
        geom_path_subset1 = absolute_path(
            'frontend', 'tests',
            'geojson', 'province_subset_1.geojson')
        with open(geom_path_subset1) as geojson_subset1:
            data_subset1 = json.load(geojson_subset1)
            geom_str_subset1 = json.dumps(data_subset1['features'][0]['geometry'])
            geom_subset1 = GEOSGeometry(geom_str_subset1, srid=3857)
            populate_layer_province_table(geom_subset1, self.province4.name)
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

    def test_patch_province(self):
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'property_geom_1.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][0]['geometry'])
        property_1 = PropertyFactory.create(
            geometry=GEOSGeometry(geom_str, srid=4326),
            name='Property ABC',
            created_by=self.user_1,
            organisation=self.organisation_1,
            centroid=self.geom1.point_on_surface,
            province=self.province3
        )
        patch_province_in_properties()
        property_1.refresh_from_db()
        self.assertEqual(property_1.province.id, self.province4.id)
