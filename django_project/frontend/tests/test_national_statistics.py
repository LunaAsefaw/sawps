import base64
import datetime
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from unittest.mock import patch
from activity.models import ActivityType
from population_data.models import AnnualPopulationPerActivity
from frontend.api_views.map import User
from stakeholder.factories import organisationFactory
from species.models import OwnedSpecies, Taxon, TaxonRank
from frontend.serializers.national_statistics import (
    SpeciesListSerializer,
    NationalStatisticsSerializer
)
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django_otp.plugins.otp_totp.models import TOTPDevice
import json
from django.test import TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from property.models import Property, PropertyType, Province
from frontend.api_views.national_statistic import (
    NationalPropertiesView,
    NationalActivityCountView,
    NationalSpeciesView
)
from rest_framework.response import Response

class NationalSpeciesViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('species_list_national')

    def test_get_species_list_via_view(self):

        taxon_rank1 = TaxonRank.objects.create(name="Species")
        Taxon.objects.create(
            common_name_varbatim='Species 1',
             icon='images/tiger.png',
            taxon_rank=taxon_rank1
        )

        view = NationalSpeciesView()

        results = view.get_species_list()

        self.assertEqual(len(results),1)

    @patch('frontend.api_views.national_statistic.NationalSpeciesView.get_species_list')
    def test_get_species_list(self, mock_get_species_list):
        # Create mock Taxon objects
        taxon_rank1 = TaxonRank.objects.create(name="Species")
        taxon_rank2 = TaxonRank.objects.create(name="Genus")
        Taxon.objects.create(
            common_name_varbatim='Species 5',
             icon='images/tiger.png',
            taxon_rank=taxon_rank1
        )
        taxon1 = Taxon(
            common_name_varbatim='Species 1',
             icon='images/tiger.png',
            taxon_rank=taxon_rank1
        )
        taxon2 = Taxon(
            common_name_varbatim='Species 2',
            icon='images/tiger.png',
            taxon_rank=taxon_rank2
        )
        test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        device = TOTPDevice(
            user=test_user,
            name='device_name'
        )
        device.save()
        client = Client()
        resp = client.login(username='testuser', password='testpassword')

        self.assertEqual(resp, True)


        # Mock the get_species_list method to return the mock Taxon objects
        mock_get_species_list.return_value = [taxon1, taxon2]

        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        serializer = SpeciesListSerializer([taxon1, taxon2], many=True)
        serializer1 = SpeciesListSerializer(taxon2)
        
        icon_url_1 = serializer1.get_species_icon(taxon2)
        expected_url_1 = '/media/images/tiger.png'
        self.assertEqual(icon_url_1, expected_url_1)

    @patch('frontend.api_views.national_statistic.NationalSpeciesView.get_species_list')
    def test_get_species_list_empty(self, mock_get_species_list):
        # Mock the get_species_list method to return an empty list
        mock_get_species_list.return_value = []
        test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        device = TOTPDevice(
            user=test_user,
            name='device_name'
        )
        device.save()
        client = Client()
        resp = client.login(username='testuser', password='testpassword')

        self.assertEqual(resp,True)

        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)



class NationalStatisticsViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('statistics_national')
        self.test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.device = TOTPDevice(
            user=self.test_user,
            name='device_name'
        )
        self.device.save()
        self.client = Client()

    @patch('property.models.Property.objects.filter')
    @patch('species.models.OwnedSpecies.objects.filter')
    def test_get_statistics(self, mock_owned_species_filter, mock_property_filter):
        # Mock Property objects and aggregate result
        mock_property_filter.return_value.count.return_value = 5
        mock_property_filter.return_value.aggregate.return_value = {'total_area': 100}

        # Mock OwnedSpecies objects and aggregate result
        mock_owned_species_filter.return_value.aggregate.return_value = {'total_area_to_species': 50}

        client = self.client
        client.login(username='testuser', password='testpassword')
        response = client.get(self.url)

        self.assertIsNotNone(response)

    @patch('property.models.Property.objects.filter')
    @patch('species.models.OwnedSpecies.objects.filter')
    def test_get_statistics_empty(self, mock_owned_species_filter, mock_property_filter):
        # Mock Property objects and aggregate result
        mock_property_filter.return_value.count.return_value = 0

        # Mock OwnedSpecies objects and aggregate result
        mock_owned_species_filter.return_value.aggregate.return_value = {'total_area_to_species': 0}

        client = self.client
        client.login(username='testuser', password='testpassword')
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response)


class NationalPropertiesViewTest(TestCase):

    def setUp(self):
        self.url = reverse('properties_population_category')
        self.test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.device = TOTPDevice(
            user=self.test_user,
            name='device_name'
        )
        self.device.save()
        self.client = Client()

    def test_get_properties_per_population_category(self):
        # Create a test organization and properties
        self.organisation = organisationFactory.create()
        Province.objects.create(name='Gauteng')
        organisation_id = self.organisation.pk
        PropertyType.objects.create(name='national')
        PropertyType.objects.create(name='private')
        Property.objects.create(
            organisation_id=organisation_id,
            property_type=PropertyType.objects.filter(name='national').first(),
            created_at=datetime.datetime.now(),
            created_by=self.test_user,
            province=Province.objects.filter(name='Gauteng').first()
        )
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuser:testpassword").decode("ascii"),
        }

        session = self.client.session
        session.save()
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class NationalActivityCountViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('activity_count')
        self.test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.device = TOTPDevice(
            user=self.test_user,
            name='device_name'
        )
        self.device.save()
        self.client = Client()

    def test_get_activity_count(self):
        self.organisation = organisationFactory.create()
        Province.objects.create(name='Gauteng')
        organisation_id = self.organisation.pk
        PropertyType.objects.create(name='national')
        PropertyType.objects.create(name='private')
        property = Property.objects.create(
            organisation_id=organisation_id,
            property_type=PropertyType.objects.filter(name='national').first(),
            created_at=datetime.datetime.now(),
            created_by=self.test_user,
            province=Province.objects.filter(name='Gauteng').first()
        )
        taxon = Taxon.objects.create(
            scientific_name='Lion',
            common_name_varbatim='Lion'
        )
        specie = OwnedSpecies.objects.create(
            user=self.test_user,
            taxon=taxon,
            property= property
        )
        ActivityType.objects.create(
            name='unplanned'
        )
        activity = ActivityType.objects.create(
            name='hunting'
        )
        AnnualPopulationPerActivity.objects.create(
            activity_type=activity,
            owned_species=specie,
            year=2023,
            total=50
        )
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuser:testpassword").decode("ascii"),
        }

        session = self.client.session
        session.save()
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the data from the response
        data = response.data
        
        # Ensure that the queryset is not empty
        self.assertGreater(len(data), 0)



class NationalActivityCountPerProvinceViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('activity_count_per_province')
        self.test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.device = TOTPDevice(
            user=self.test_user,
            name='device_name'
        )
        self.device.save()
        self.client = Client()

    def test_get_activity_count(self):
        self.organisation = organisationFactory.create()
        Province.objects.create(name='Gauteng')
        organisation_id = self.organisation.pk
        PropertyType.objects.create(name='national')
        PropertyType.objects.create(name='private')
        property = Property.objects.create(
            organisation_id=organisation_id,
            property_type=PropertyType.objects.filter(name='national').first(),
            created_at=datetime.datetime.now(),
            created_by=self.test_user,
            province=Province.objects.filter(name='Gauteng').first()
        )
        taxon = Taxon.objects.create(
            scientific_name='Lion',
            common_name_varbatim='Lion'
        )
        specie = OwnedSpecies.objects.create(
            user=self.test_user,
            taxon=taxon,
            property= property
        )
        ActivityType.objects.create(
            name='unplanned'
        )
        activity = ActivityType.objects.create(
            name='hunting'
        )
        AnnualPopulationPerActivity.objects.create(
            activity_type=activity,
            owned_species=specie,
            year=2023,
            total=50
        )
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuser:testpassword").decode("ascii"),
        }

        session = self.client.session
        session.save()
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the data from the response
        data = response.data

        # Define the expected result dictionary
        expected_result = {
            'Lion': {
                'Gauteng': {
                    'total_area': 0.0,
                    'species_area': 0.0,
                    'percentage': '0.00%',
                }
            }
        }

        self.assertEqual(data, expected_result)



class NationalActivityCountPerPropertyTypeViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('activity_count_per_property')
        self.test_user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.device = TOTPDevice(
            user=self.test_user,
            name='device_name'
        )
        self.device.save()
        self.client = Client()

    def test_get_activity_count(self):
        self.organisation = organisationFactory.create()
        Province.objects.create(name='Gauteng')
        organisation_id = self.organisation.pk
        PropertyType.objects.create(name='national')
        PropertyType.objects.create(name='private')
        property = Property.objects.create(
            organisation_id=organisation_id,
            property_type=PropertyType.objects.filter(name='national').first(),
            created_at=datetime.datetime.now(),
            created_by=self.test_user,
            province=Province.objects.filter(name='Gauteng').first()
        )
        taxon = Taxon.objects.create(
            scientific_name='Lion',
            common_name_varbatim='Lion'
        )
        specie = OwnedSpecies.objects.create(
            user=self.test_user,
            taxon=taxon,
            property= property
        )
        ActivityType.objects.create(
            name='unplanned'
        )
        activity = ActivityType.objects.create(
            name='hunting'
        )
        AnnualPopulationPerActivity.objects.create(
            activity_type=activity,
            owned_species=specie,
            year=2023,
            total=50
        )
        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuser:testpassword").decode("ascii"),
        }

        session = self.client.session
        session.save()
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the data from the response
        data = response.data

        # Define the expected result dictionary
        expected_result = {
            'Lion': {'national': {'total_area': 0.0, 'species_area': 0.0, 'percentage': '0.00%'}}
        }

        self.assertEqual(data, expected_result)
