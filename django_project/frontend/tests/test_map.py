import json
import mock
from importlib import import_module
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from core.settings.utils import absolute_path
from frontend.utils.map import get_map_template_style
from property.factories import PropertyFactory
from stakeholder.factories import (
    organisationFactory,
    userRoleTypeFactory
)
from frontend.models.parcels import (
    Erf,
    Holding
)
from frontend.tests.model_factories import UserF
from frontend.api_views.map import (
    ContextLayerList,
    MapStyles,
    PropertiesLayerMVTTiles,
    FindParcelByCoord,
    FindPropertyByCoord,
    MapAuthenticate
)
from frontend.tests.request_factories import OrganisationAPIRequestFactory


def mocked_set_cache(cache_key, allowed, redis_time_cache):
    return True


class TestMapAPIViews(TestCase):

    def setUp(self) -> None:
        self.organisation_1 = organisationFactory.create()
        self.factory = OrganisationAPIRequestFactory(self.organisation_1)
        self.middleware = SessionMiddleware(lambda x: None)
        self.user_1 = UserF.create(username='test_1')
        self.superuser = UserF.create(
            username='test_2',
            is_superuser=True
        )
        self.user_2 = UserF.create(username='test_3')
        # insert geom 1 and 2
        geom_path = absolute_path(
            'frontend', 'tests',
            'geojson', 'geom_1.geojson')
        with open(geom_path) as geojson:
            data = json.load(geojson)
            geom_str = json.dumps(data['features'][1]['geometry'])
            self.erf_1 = Erf.objects.create(
                geom=GEOSGeometry(geom_str),
                cname='C1234ABC'
            )
            geom_str = json.dumps(data['features'][0]['geometry'])
            self.holding_1 = Holding.objects.create(
                geom=GEOSGeometry(geom_str),
                cname='C1235DEF'
            )

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
        get_map_template_style(request,1)

    def test_map_styles_with_different_role(self):
        request = self.factory.get(
            reverse('map-style')
        )
        request.user = self.user_1
        response = get_map_template_style(request,1)
        self.assertIsNotNone(response['layers'])

    def test_get_properties_map_tile(self):
        kwargs = {
            'z': 14,
            'x': 9455,
            'y': 9454
        }
        request = self.factory.get(
            reverse('properties-map-layer', kwargs=kwargs)
        )
        request.user = self.user_1
        view = PropertiesLayerMVTTiles.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        # test superuser
        request = self.factory.get(
            reverse('properties-map-layer', kwargs=kwargs)
        )
        request.user = self.superuser
        view = PropertiesLayerMVTTiles.as_view()
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

        # insert property
        property = PropertyFactory.create(
            geometry=self.holding_1.geom,
            name='Property A',
            created_by=self.user_1,
            organisation=self.organisation_1
        )
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
        self.assertEqual(response.data['name'], property.name)
        # set current organisation_2 in the request
        request = self.factory.get(
            reverse('find-property') + (
                f'/?lat={lat}&lng={lng}'
            ),
            organisation_id=self.organisation_1.id
        )
        property.organisation.id=55
        request.user = self.user_1
        # should find 0
        response = view(request)
        self.assertEqual(response.status_code, 404)

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
