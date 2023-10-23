import base64
import json
import mock

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.test import Client, TestCase
from django.urls import reverse
from core.settings.utils import absolute_path
from frontend.models.places import (
    PlaceNameSmallScale,
    PlaceNameMidScale,
    PlaceNameLargerScale,
    PlaceNameLargestScale
)
from frontend.api_views.property import (
    CreateNewProperty,
    PropertyList,
    PropertyMetadataList,
    UpdatePropertyBoundaries,
    PropertyDetail,
    PropertySearch,
    UpdatePropertyInformation,
)
from frontend.models.parcels import Erf, Holding
from frontend.tests.model_factories import UserF
from frontend.tests.request_factories import OrganisationAPIRequestFactory
from property.factories import PropertyFactory, ProvinceFactory
from property.models import Parcel, Property, PropertyType
from population_data.models import OpenCloseSystem
from stakeholder.factories import (
    organisationFactory,
    organisationUserFactory,
)


class TestPropertyAPIViews(TestCase):
    fixtures = [
        'open_close_systems.json',
        'property_type.json',
        'parcel_types.json'
    ]

    def setUp(self) -> None:
        # insert organisation
        self.organisation = organisationFactory.create()
        self.factory = OrganisationAPIRequestFactory(self.organisation)
        self.user_1 = UserF.create(username='test_1')
        self.user_2 = UserF.create(username='test_2')
        # insert province
        self.province = ProvinceFactory.create()
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

    @mock.patch('frontend.api_views.property.find_province')
    def test_create_new_property(self, mocked_find_province):
        mocked_find_province.return_value = self.province
        property_type = PropertyType.objects.all().first()
        open_close_system = OpenCloseSystem.objects.all().first()
        data = {
            'name': 'Property A',
            'owner_email': 'test@test.com',
            'property_type_id': property_type.id,
            'organisation_id': self.organisation.id,
            'open_id': open_close_system.id,
            'parcels': [
                {
                    'id': self.erf_1.id,
                    'layer': 'erf',
                    'cname': self.erf_1.cname,
                    'type': 'urban'
                },
                {
                    'id': self.holding_1.id,
                    'layer': 'holding',
                    'cname': self.holding_1.cname,
                    'type': 'urban'
                },
            ]
        }
        request = self.factory.post(
            reverse('property-create'), data=data,
            format='json'
        )
        # without adding to organisation, should return 403
        self.user_1.user_profile = self.user_1.user_profile
        self.user_1.user_profile.current_organisation = self.organisation
        self.user_1.save()

        request.user = self.user_1
        view = CreateNewProperty.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)
        # add to organisation, should return 201
        organisationUserFactory.create(
            user=self.user_1,
            organisation=self.organisation
        )
        request = self.factory.post(
            reverse('property-create'), data=data,
            format='json'
        )
        request.user = self.user_1
        view = CreateNewProperty.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        property = Property.objects.get(id=response.data['id'])
        self.assertEqual(property.name, data['name'])
        self.assertEqual(property.property_type.id, data['property_type_id'])
        self.assertEqual(property.province.id, self.province.id)
        self.assertEqual(property.organisation.id, data['organisation_id'])
        self.assertEqual(property.open.id, data['open_id'])
        self.assertEqual(
            Parcel.objects.filter(property=property).count(),
            2
        )
        # get property
        kwargs = {
            'id': property.id
        }
        request = self.factory.get(
            reverse('property-detail', kwargs=kwargs)
        )
        request.user = self.user_1
        view = PropertyDetail.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['bbox']), 4)
        self.assertEqual(len(response.data['parcels']), 2)

    def test_metadata_list(self):
        request = self.factory.get(
            reverse('property-metadata')
        )
        request.user = self.user_1
        view = PropertyMetadataList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_property_list(self):
        property = PropertyFactory.create(
            geometry=self.holding_1.geom,
            name='Property C',
            created_by=self.user_2,
            organisation=self.organisation
        )
        request = self.factory.get(
            reverse('property-list')
        )
        self.user_2.user_profile = self.user_2.user_profile
        self.user_2.user_profile.current_organisation = self.organisation
        self.user_2.save()

        request.user = self.user_2
        view = PropertyList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        _property = response.data[0]
        self.assertEqual(_property['id'], property.id)
        self.assertEqual(_property['name'], property.name)

    def test_get_property_list_for_organisations(self):
        """Taxon list API test for organisations."""
        organisation = organisationFactory.create(national=True)

        user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd'
        )

        user.user_profile.current_organisation = organisation
        user.save()

        property = PropertyFactory.create(
            organisation=organisation,
            name='PropertyA'
        )

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
            base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }

        url = reverse("property-list")
        client = Client()
        data = {"organisation":organisation.id}
        response = client.get(url, data, **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "PropertyA")

    def test_property_list_with_organisation_id(self):
        organisation = organisationFactory.create(national=True)

        user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd'
        )

        user.user_profile.current_organisation = organisation
        user.save()
        # Create properties related to the organisation
        property1 = PropertyFactory.create(
            organisation=organisation,
            name='PropertyA'
        )
        property2 = PropertyFactory.create(
            organisation=organisation,
            name='PropertyB'
        )

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
            base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }

        url = reverse("property-list", kwargs={'organisation_id': organisation.id})
        client = Client()
        response = client.get(url, **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "PropertyA")
        self.assertEqual(response.data[1]['name'], "PropertyB")

    def test_property_list_without_organisation_id(self):
        organisation = organisationFactory.create(national=True)

        user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd'
        )

        user.user_profile.current_organisation = organisation
        user.save()

        # Create properties related to the organisation
        property1 = PropertyFactory.create(
            organisation=organisation,
            name='PropertyA'
        )
        property2 = PropertyFactory.create(
            organisation=organisation,
            name='PropertyB'
        )
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
            base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }

        url = reverse("property-list")
        client = Client()
        response = client.get(url, **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "PropertyA")
        self.assertEqual(response.data[1]['name'], "PropertyB")

    @mock.patch('frontend.api_views.property.find_province')
    def test_update_property(self, mocked_find_province):
        mocked_find_province.return_value = self.province
        property_type = PropertyType.objects.all().first()
        property = PropertyFactory.create(
            geometry=self.holding_1.geom,
            name='Property D',
            created_by=self.user_1
        )
        open_close_system = OpenCloseSystem.objects.first()
        data = {
            'id': property.id,
            'name': 'Property D-1',
            'owner_email': 'test@test.com',
            'property_type_id': property_type.id,
            'organisation_id': self.organisation.id,
            'open_id': open_close_system.id,
            'parcels': []
        }
        request = self.factory.post(
            reverse('property-update-detail'), data=data,
            format='json'
        )
        request.user = self.user_1
        view = UpdatePropertyInformation.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 204)
        updated = Property.objects.get(id=property.id)
        self.assertEqual(updated.name, data['name'])
        self.assertEqual(updated.open_id, data['open_id'])

    def test_update_boundaries(self):
        property_type = PropertyType.objects.all().first()
        data = {
            'name': 'Property A',
            'owner_email': 'test@test.com',
            'property_type_id': property_type.id,
            'province_id': self.province.id,
            'organisation_id': self.organisation.id,
            'parcels': [
                {
                    'id': self.erf_1.id,
                    'layer': 'erf',
                    'cname': self.erf_1.cname,
                    'type': 'urban'
                },
                {
                    'id': self.holding_1.id,
                    'layer': 'holding',
                    'cname': self.holding_1.cname,
                    'type': 'urban'
                },
            ]
        }
        request = self.factory.post(
            reverse('property-create'), data=data,
            format='json'
        )
        self.user_1.user_profile = self.user_1.user_profile
        self.user_1.user_profile.current_organisation = self.organisation
        self.user_1.save()

        request.user = self.user_1
        organisationUserFactory.create(
            user=self.user_1,
            organisation=self.organisation
        )
        view = CreateNewProperty.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 201)
        property_id = response.data['id']
        data = {
            'id': property_id,
            'parcels': [
                {
                    'id': self.holding_1.id,
                    'layer': 'holding',
                    'cname': self.holding_1.cname,
                    'type': 'urban'
                }
            ]
        }
        request = self.factory.post(
            reverse('property-update-boundaries'), data=data,
            format='json'
        )
        request.user = self.user_1
        view = UpdatePropertyBoundaries.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Parcel.objects.filter(property_id=property_id).count(),
            1
        )

    def test_search_property(self):
        # insert place names
        place_1 = PlaceNameSmallScale.objects.create(
            geom=self.holding_1.geom.centroid,
            fclass='suburb',
            name='Seaview'
        )
        place_2 = PlaceNameMidScale.objects.create(
            geom=self.holding_1.geom.centroid,
            fclass='suburb',
            name='Seaview'
        )
        place_3 = PlaceNameLargerScale.objects.create(
            geom=self.holding_1.geom.centroid,
            fclass='hamlet',
            name='Sea Glade'
        )
        place_4 = PlaceNameLargestScale.objects.create(
            geom=self.holding_1.geom.centroid,
            fclass='town',
            name='SeaCow Lake'
        )
        # insert property
        property = PropertyFactory.create(
            geometry=self.holding_1.geom,
            name='Seafields',
            created_by=self.user_2,
            organisation=self.organisation
        )
        request = self.factory.get(
            reverse('property-search') + f'?search_text=sea'
        )
        self.user_2.user_profile = self.user_2.user_profile
        self.user_2.user_profile.current_organisation = self.organisation
        self.user_2.save()

        request.user = self.user_2
        view = PropertySearch.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
