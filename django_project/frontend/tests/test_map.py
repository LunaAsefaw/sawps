import json
import mock
import datetime
from importlib import import_module
from django.db import connection
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.settings.utils import absolute_path
from frontend.utils.map import get_map_template_style
from activity.factories import ActivityTypeFactory
from property.factories import PropertyFactory, ProvinceFactory
from stakeholder.models import OrganisationUser
from stakeholder.factories import (
    organisationFactory,
    userRoleTypeFactory,
    organisationUserFactory
)
from species.factories import TaxonF
from frontend.models.map_session import MapSession
from frontend.models.parcels import (
    Erf,
    Holding
)
from frontend.tests.model_factories import UserF
from frontend.api_views.map import (
    ContextLayerList,
    MapStyles,
    DefaultPropertiesLayerMVTTiles,
    FindParcelByCoord,
    FindPropertyByCoord,
    MapAuthenticate,
    SessionPropertiesLayerMVTTiles,
    PopulationCountLegends
)
from frontend.tests.request_factories import OrganisationAPIRequestFactory
from sawps.models import ExtendedGroup
from sawps.tests.model_factories import GroupF
from frontend.utils.map import (
    generate_population_count_categories_base,
    get_query_condition_for_properties_query,
    get_query_condition_for_population_query,
    get_province_population_query,
    get_properties_population_query,
    get_properties_query,
    delete_expired_map_materialized_view,
    generate_map_view,
    generate_population_count_categories
)


def mocked_spatial_filter_task(cache_key, allowed, redis_time_cache):
    return True


def mocked_set_cache(cache_key, allowed, redis_time_cache):
    return True


def is_materialized_view_exists(view_name):
    sql = (
        """
        select exists(
            select 1 from pg_matviews where matviewname=%s
        )
        """
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [view_name])
        row = cursor.fetchone()
        return row[0]


def insert_province_geom(id, province_name, geom):
    sql = (
        """
        INSERT INTO layer.zaf_provinces_small_scale
        (id, geom, adm1_en) VALUES(%s, %s, %s)
        """
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [id, geom, province_name])


class TestMapAPIViews(TestCase):

    def setUp(self) -> None:
        self.province_1 = ProvinceFactory.create(name='ProvinceA')
        self.group_1 = GroupF.create()
        self.group_2 = GroupF.create()
        self.organisation_1 = organisationFactory.create()
        self.factory = OrganisationAPIRequestFactory(self.organisation_1)
        self.middleware = SessionMiddleware(lambda x: None)
        self.user_1 = UserF.create(username='test_1')
        # add user_1 to org_1
        self.user_1.user_profile.current_organisation = self.organisation_1
        self.user_1.user_profile.save()
        organisationUserFactory.create(
            user=self.user_1,
            organisation=self.organisation_1
        )
        # assign perm user_1 with can_view_map_properties_layer
        self.group_1.user_set.add(self.user_1)
        content_type = ContentType.objects.get_for_model(ExtendedGroup)
        view_properties_perm = Permission.objects.filter(
            content_type=content_type,
            codename='can_view_map_properties_layer'
        ).first()
        self.group_1.permissions.add(view_properties_perm)
        self.superuser = UserF.create(
            username='test_2',
            is_superuser=True
        )
        # set active org for superuser
        self.superuser.user_profile.current_organisation = self.organisation_1
        self.superuser.user_profile.save()
        self.user_2 = UserF.create(username='test_3')
        # add user_2 to org_1 and add perm province layer
        self.user_2.user_profile.current_organisation = self.organisation_1
        self.user_2.user_profile.save()
        organisationUserFactory.create(
            user=self.user_2,
            organisation=self.organisation_1
        )
        self.group_2.user_set.add(self.user_2)
        view_province_perm = Permission.objects.filter(
            content_type=content_type,
            codename='can_view_map_province_layer'
        ).first()
        self.group_2.permissions.add(view_province_perm)
        # insert geom 1 and 2
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'geom_1.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][1]['geometry'])
            geom_obj = GEOSGeometry(geom_str)
            self.erf_1 = Erf.objects.create(
                geom=geom_obj,
                cname='C1234ABC'
            )
            geom_str = json.dumps(data['features'][0]['geometry'])
            self.holding_1 = Holding.objects.create(
                geom=GEOSGeometry(geom_str),
                cname='C1235DEF'
            )
            self.property_1 = PropertyFactory.create(
                geometry=self.holding_1.geom,
                name='Property ABC',
                created_by=self.user_1,
                organisation=self.organisation_1,
                centroid=self.holding_1.geom.point_on_surface,
                province=self.province_1
            )
            # insert province layer
            insert_province_geom(1, self.province_1.name, geom_obj.ewkt)

    def test_get_context_layers(self):
        request = self.factory.get(
            reverse('context-layer-list')
        )
        request.user = self.user_1
        view = ContextLayerList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    @mock.patch('frontend.api_views.map.cache.set',
                mock.Mock(side_effect=mocked_set_cache))
    def test_get_map_styles(self):
        request = self.factory.get(
            reverse('map-style')
        )
        request.user = self.user_1
        # add session
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        view = MapStyles.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_map_styles_with_theme_value_for_role(self):
        # test with user role as decision maker
        role = userRoleTypeFactory.create(
            id=1,
            name='Decision Maker',
        )
        self.user_1.user_profile.user_role_type_id = role
        self.user_1.save()

        request = self.factory.get(
            reverse('map-style')
        )
        request.user = self.user_1
        get_map_template_style(request, 'session-test', 1)

    def test_map_styles_with_different_role(self):
        request = self.factory.get(
            reverse('map-style')
        )
        request.user = self.user_1
        response = get_map_template_style(request, 'session-test', 1)
        self.assertIsNotNone(response['layers'])

    def test_get_properties_map_tile(self):
        kwargs = {
            'z': 14,
            'x': 9455,
            'y': 9454
        }
        request = self.factory.get(
            reverse('default-properties-map-layer', kwargs=kwargs)
        )
        request.user = self.user_1
        view = DefaultPropertiesLayerMVTTiles.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        # test superuser
        request = self.factory.get(
            reverse('default-properties-map-layer', kwargs=kwargs)
        )
        request.user = self.superuser
        view = DefaultPropertiesLayerMVTTiles.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)

    def test_find_parcel_by_coord(self):
        lat = -26.71998940486352
        lng = 27.763781680455708
        request = self.factory.get(
            reverse('find-parcel') + (
                f'/?lat={lat}&lng={lng}'
            )
        )
        request.user = self.user_1
        view = FindParcelByCoord.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['layer'], 'holding')
        self.assertEqual(response.data['cname'], self.holding_1.cname)

    def test_find_property_by_coord(self):
        self.user_1.user_profile.current_organisation = self.organisation_1
        self.user_1.save()

        lat = -26.71998940486352
        lng = 27.763781680455708
        request = self.factory.get(
            reverse('find-property') + (
                f'/?lat={lat}&lng={lng}'
            ),
            organisation_id=self.organisation_1.id
        )
        # should find 1
        request.user = self.user_1
        view = FindPropertyByCoord.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.property_1.name)
        self.assertEqual(response.data['short_code'],
                         self.property_1.short_code)
        # remove org1 from user1
        OrganisationUser.objects.filter(
            organisation=self.organisation_1,
            user=self.user_1
        ).delete()
        request = self.factory.get(
            reverse('find-property') + (
                f'/?lat={lat}&lng={lng}'
            ),
            organisation_id=self.organisation_1.id
        )
        request.user = self.user_1
        # should find 0
        response = view(request)
        self.assertEqual(response.status_code, 404)
        # superuser should be able to access it
        request = self.factory.get(
            reverse('find-property') + (
                f'/?lat={lat}&lng={lng}'
            ),
            organisation_id=self.organisation_1.id
        )
        request.user = self.superuser
        response = view(request)
        self.assertEqual(response.status_code, 200)

    @mock.patch('frontend.api_views.map.cache.get')
    def test_map_authenticate(self, mocked_cache):
        token = 'test_token'
        # no record in cache, 403
        mocked_cache.return_value = None
        request = self.factory.get(
            reverse('map-authenticate') + (
                f'/?token={token}'
            )
        )
        view = MapAuthenticate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)
        # has record in cache, 200
        mocked_cache.return_value = True
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_get_properties_map_tile_by_session(self):
        taxon = TaxonF.create(
            scientific_name='Loxodonta africana',
            colour='#a9a9aa'
        )
        filter_organisation = 'all'
        filter_spatial = ''
        filter_property = 'all'
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = taxon.scientific_name
        filter_activity = ''
        session = MapSession.objects.create(
            user=self.user_1,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            species=filter_species_name
        )
        # generate materialized view for properties layer
        generate_map_view(session, False, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        self.assertTrue(
            is_materialized_view_exists(session.properties_view_name))
        kwargs = {
            'z': 14,
            'x': 9455,
            'y': 9454
        }
        request = self.factory.get(
            reverse('session-properties-map-layer', kwargs=kwargs) +
            f'?session={str(session.uuid)}'
        )
        request.user = self.user_1
        view = SessionPropertiesLayerMVTTiles.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        # test using user_2, should return 404
        session = MapSession.objects.create(
            user=self.user_2,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            species=filter_species_name
        )
        # generate materialized view for properties layer
        generate_map_view(session, True, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        self.assertTrue(
            is_materialized_view_exists(session.province_view_name))
        request = self.factory.get(
            reverse('session-properties-map-layer', kwargs=kwargs) +
            f'?session={str(session.uuid)}'
        )
        request.user = self.user_2
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 404)
        # test using province zoom level, should return 200
        kwargs = {
            'z': 5,
            'x': 18,
            'y': 18
        }
        request = self.factory.get(
            reverse('session-properties-map-layer', kwargs=kwargs) +
            f'?session={str(session.uuid)}'
        )
        request.user = self.user_2
        response = view(request, **kwargs)
        # query returns a result, but ST_AsMVTGeom returns null geom
        self.assertEqual(response.status_code, 404)

    def test_population_count_legends(self):
        taxon = TaxonF.create(
            scientific_name='Loxodonta africana',
            colour='#a9a9aa'
        )
        data = {
            'start_year': 1960,
            'end_year': 2023,
            'species': taxon.scientific_name,
            'organisation': str(self.organisation_1.id),
            'activity': '',
            'spatial_filter_values': '',
            'property': 'all'
        }
        request = self.factory.post(
            reverse('properties-map-legends'),
            data=data, format='json'
        )
        # the user does not have privilege to view province layer
        request.user = self.user_1
        view = PopulationCountLegends.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['session'])
        session = MapSession.objects.filter(
            uuid=response.data['session']
        ).first()
        self.assertTrue(session)
        self.assertTrue(
            is_materialized_view_exists(session.properties_view_name))
        self.assertFalse(
            is_materialized_view_exists(session.province_view_name))
        self.assertTrue(len(response.data['properties']) > 0)
        self.assertTrue(len(response.data['province']) == 0)
        # test using superuser
        request = self.factory.post(
            reverse('properties-map-legends'),
            data=data, format='json'
        )
        request.user = self.superuser
        view = PopulationCountLegends.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['session'])
        session = MapSession.objects.filter(
            uuid=response.data['session']
        ).first()
        self.assertTrue(session)
        self.assertTrue(
            is_materialized_view_exists(session.properties_view_name))
        self.assertTrue(
            is_materialized_view_exists(session.province_view_name))
        self.assertTrue(len(response.data['properties']) > 0)
        self.assertTrue(len(response.data['province']) > 0)

    def test_generate_population_count_categories_base(self):
        base_color = '#a9a9aa'
        # test with normal case
        breaks = generate_population_count_categories_base(0, 125, base_color)
        self.assertEqual(len(breaks), 5)
        self.assertListEqual(breaks, [
            {
                "minLabel": 0,
                "maxLabel": 25,
                "value": 0,
                "color": "#ffffff"
            },
            {
                "minLabel": 25,
                "maxLabel": 50,
                "value": 25,
                "color": "#e9e9e9"
            },
            {
                "minLabel": 50,
                "maxLabel": 75,
                "value": 50,
                "color": "#d4d4d4"
            },
            {
                "minLabel": 75,
                "maxLabel": 100,
                "value": 75,
                "color": "#bebebf"
            },
            {
                "minLabel": 100,
                "maxLabel": 125,
                "value": 100,
                "color": "#a9a9aa"
            }
        ])
        # test with min=max > 0
        breaks = generate_population_count_categories_base(10, 10, base_color)
        self.assertEqual(len(breaks), 5)
        self.assertListEqual(breaks, [
            {
                "minLabel": 10,
                "maxLabel": 30,
                "value": 10,
                "color": "#ffffff"
            },
            {
                "minLabel": 30,
                "maxLabel": 50,
                "value": 30,
                "color": "#e9e9e9"
            },
            {
                "minLabel": 50,
                "maxLabel": 70,
                "value": 50,
                "color": "#d4d4d4"
            },
            {
                "minLabel": 70,
                "maxLabel": 90,
                "value": 70,
                "color": "#bebebf"
            },
            {
                "minLabel": 90,
                "maxLabel": 110,
                "value": 90,
                "color": "#a9a9aa"
            }
        ])
        # test with min=max = 0
        breaks = generate_population_count_categories_base(0, 0, base_color)
        self.assertEqual(len(breaks), 5)
        self.assertListEqual(breaks, [
            {
                "minLabel": 0,
                "maxLabel": 20,
                "value": 0,
                "color": "#ffffff"
            },
            {
                "minLabel": 20,
                "maxLabel": 40,
                "value": 20,
                "color": "#e9e9e9"
            },
            {
                "minLabel": 40,
                "maxLabel": 60,
                "value": 40,
                "color": "#d4d4d4"
            },
            {
                "minLabel": 60,
                "maxLabel": 80,
                "value": 60,
                "color": "#bebebf"
            },
            {
                "minLabel": 80,
                "maxLabel": 100,
                "value": 80,
                "color": "#a9a9aa"
            }
        ])

    def test_get_query_condition_for_properties_query(self):
        filter_organisation = '1,2,3'
        filter_spatial = 'Critical Biodiversity Area 1'
        filter_property = '1'
        conds, values = get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
        self.assertEqual(len(conds), 3)
        self.assertIn('p.organisation_id IN %s', conds[0])
        self.assertIn('p.id IN %s', conds[1])
        self.assertIn(
            'select 1 from frontend_spatialdatavaluemodel fs2',
            conds[2])
        self.assertEqual(len(values), 3)
        filter_organisation = ''
        filter_spatial = ''
        filter_property = ''
        conds, values = get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property,
            property_alias_name='p2'
        )
        self.assertEqual(len(conds), 2)
        self.assertIn('p2.organisation_id = any(ARRAY[]::bigint[])', conds[0])
        self.assertIn('p2.id = any(ARRAY[]::bigint[])', conds[1])
        self.assertEqual(len(values), 0)
        # using all
        filter_organisation = 'all'
        filter_spatial = ''
        filter_property = 'all'
        conds, values = get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
        self.assertEqual(len(conds), 0)
        self.assertEqual(len(values), 0)

    def test_get_query_condition_for_population_query(self):
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = 'Loxodonta africana'
        activity_type_1 = ActivityTypeFactory.create()
        activity_type_2 = ActivityTypeFactory.create()
        filter_activity = f'{activity_type_1.id},{activity_type_2.id}'
        conds, values = get_query_condition_for_population_query(
            filter_start_year, filter_end_year,
            filter_species_name, filter_activity
        )
        self.assertEqual(len(conds), 2)
        self.assertIn('t.scientific_name=%s', conds[0])
        self.assertIn('ap.year between %s and %s', conds[1])
        self.assertEqual(len(values), 3)
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = 'Loxodonta africana'
        filter_activity = f'{activity_type_1.id}'
        conds, values = get_query_condition_for_population_query(
            filter_start_year, filter_end_year,
            filter_species_name, filter_activity
        )        
        self.assertEqual(len(conds), 3)
        self.assertIn('t.scientific_name=%s', conds[0])
        self.assertIn('SELECT 1 FROM annual_population_per_activity appa',
                      conds[1])
        self.assertIn('ap.year between %s and %s', conds[2])
        self.assertEqual(len(values), 6)

    def test_get_province_population_query(self):
        filter_organisation = '1,2,3'
        filter_spatial = ''
        filter_property = '1'
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = 'Loxodonta africana'
        filter_activity = ''
        sql_view, query_values = get_province_population_query(
            filter_start_year, filter_end_year,
            filter_species_name, filter_organisation,
            filter_activity, filter_spatial, filter_property
        )
        self.assertIn('select p.province_id as id, sum(ap.total) as count',
                      sql_view)
        self.assertIn('p.organisation_id IN %s',
                      sql_view)
        self.assertIn('p.id IN %s',
                      sql_view)
        self.assertIn('t.scientific_name=%s',
                      sql_view)
        self.assertIn('ap.year between %s and %s',
                      sql_view)
        self.assertIn(
            'select p2.id, p2.name, COALESCE(population_summary.count, 0) '
            'as count',
            sql_view
        )
        self.assertIn(
            'from province p2 left join', sql_view)
        self.assertEqual(len(query_values), 5)

    def test_get_properties_population_query(self):
        filter_organisation = '1,2,3'
        filter_spatial = ''
        filter_property = '1'
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = 'Loxodonta africana'
        filter_activity = ''
        sql_view, query_values = get_properties_population_query(
            filter_start_year, filter_end_year,
            filter_species_name, filter_organisation,
            filter_activity, filter_spatial, filter_property
        )
        self.assertIn('select ap.property_id as id, sum(ap.total) as count',
                      sql_view)
        self.assertIn('p2.organisation_id IN %s',
                      sql_view)
        self.assertIn('p2.id IN %s',
                      sql_view)
        self.assertIn('t.scientific_name=%s',
                      sql_view)
        self.assertIn('ap.year between %s and %s',
                      sql_view)
        self.assertIn(
            'select p2.id, p2.name, COALESCE(population_summary.count, 0) '
            'as count',
            sql_view
        )
        self.assertIn(
            'from property p2 left join', sql_view)
        self.assertEqual(len(query_values), 5)

    def test_get_properties_query(self):
        filter_organisation = '1,2,3'
        filter_spatial = ''
        filter_property = '1'
        sql_view, query_values = get_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
        self.assertIn('select p.id, p.name, 0 as count',
                      sql_view)
        self.assertIn('p.organisation_id IN %s',
                      sql_view)
        self.assertIn('p.id IN %s',
                      sql_view)
        self.assertIn(
            'from property p', sql_view)
        self.assertEqual(len(query_values), 2)

    def test_generate_population_count_categories(self):
        taxon = TaxonF.create(
            scientific_name='Loxodonta africana',
            colour='#a9a9aa'
        )
        filter_organisation = 'all'
        filter_spatial = ''
        filter_property = 'all'
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = taxon.scientific_name
        filter_activity = ''
        session = MapSession.objects.create(
            user=self.user_1,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8)
        )
        generate_map_view(session, False, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        generate_map_view(session, True, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        expected_breaks = [
            {
                "minLabel": 0,
                "maxLabel": 20,
                "value": 0,
                "color": "#ffffff"
            },
            {
                "minLabel": 20,
                "maxLabel": 40,
                "value": 20,
                "color": "#e9e9e9"
            },
            {
                "minLabel": 40,
                "maxLabel": 60,
                "value": 40,
                "color": "#d4d4d4"
            },
            {
                "minLabel": 60,
                "maxLabel": 80,
                "value": 60,
                "color": "#bebebf"
            },
            {
                "minLabel": 80,
                "maxLabel": 100,
                "value": 80,
                "color": "#a9a9aa"
            }
        ]
        breaks = generate_population_count_categories(
            True, session, filter_species_name)
        self.assertEqual(len(breaks), 5)
        self.assertListEqual(breaks, expected_breaks)
        breaks = generate_population_count_categories(
            False, session, filter_species_name)
        self.assertEqual(len(breaks), 5)
        self.assertListEqual(breaks, expected_breaks)

    def test_map_materialized_view(self):
        filter_organisation = 'all'
        filter_spatial = ''
        filter_property = 'all'
        filter_start_year = 1960
        filter_end_year = 2023
        filter_species_name = ''
        filter_activity = ''
        session = MapSession.objects.create(
            user=self.user_1,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8)
        )
        # generate materialized view for properties layer
        generate_map_view(session, False, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        self.assertTrue(
            is_materialized_view_exists(session.properties_view_name))
        self.assertFalse(
            is_materialized_view_exists(session.province_view_name))
        total_count = delete_expired_map_materialized_view()
        self.assertEqual(total_count, 1)
        self.assertFalse(MapSession.objects.exists())
        self.assertFalse(
            is_materialized_view_exists(session.properties_view_name))
        self.assertFalse(
            is_materialized_view_exists(session.province_view_name))
        session = MapSession.objects.create(
            user=self.user_1,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8)
        )
        # generate view for population province+properties
        filter_species_name = 'Loxodonta africana'
        generate_map_view(session, False, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        generate_map_view(session, True, filter_start_year, filter_end_year,
                          filter_species_name, filter_organisation,
                          filter_activity, filter_spatial, filter_property)
        self.assertTrue(
            is_materialized_view_exists(session.properties_view_name))
        self.assertTrue(
            is_materialized_view_exists(session.province_view_name))
        # delete session obj to drop the views
        session.delete()
        self.assertFalse(MapSession.objects.exists())
        self.assertFalse(
            is_materialized_view_exists(session.properties_view_name))
        self.assertFalse(
            is_materialized_view_exists(session.province_view_name))
