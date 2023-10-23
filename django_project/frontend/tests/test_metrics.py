import base64

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from property.factories import PropertyFactory
from rest_framework import status
from species.factories import (
    OwnedSpeciesFactory,
    TaxonFactory,
    TaxonRankFactory,
)
from species.models import TaxonRank
from stakeholder.factories import organisationFactory, organisationUserFactory


class BaseTestCase(TestCase):
    def setUp(self):
        """
        Set up test data and environment for the test cases.

        This method creates necessary test objects like TaxonRank, Taxon, User, Organisation,
        Property, and OwnedSpecies. It also sets up the client and session for testing.
        """
        taxon_rank = TaxonRank.objects.filter(name="Species").first()
        if not taxon_rank:
            taxon_rank = TaxonRankFactory.create(name="Species")

        self.taxon = TaxonFactory.create(
            taxon_rank=taxon_rank, common_name_varbatim="Lion",
            scientific_name = "Penthera leo"
        )

        self.user = User.objects.create_user(
            username="testuserd",
            password="testpasswordd"
        )

        self.organisation_1 = organisationFactory.create()
        organisationUserFactory.create(
            user=self.user,
            organisation=self.organisation_1
        )

        self.user.user_profile.current_organisation = self.organisation_1
        self.user.save()

        self.property = PropertyFactory.create(
            organisation=self.organisation_1, name="PropertyA"
        )

        self.owned_species = OwnedSpeciesFactory.create_batch(
            5, taxon=self.taxon, user=self.user, property=self.property
        )

        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuserd:testpasswordd").decode("ascii"),
        }
        self.client = Client()

        session = self.client.session
        session.save()

class PopulationEstimateCategoryTestCase(BaseTestCase):
    """
    This is to test if the API is reachable
    and returns a success response.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("total-count-per-population-estimate")

    def test_population_estimate_category_api_view(self) -> None:
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SpeciesPopuationCountPerProvinceTestCase(BaseTestCase):
    """
    This is to test if the API is reachable
    and returns a success response.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("species_count_per_province")

    def test_species_population_count_api_view(self) -> None:
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SpeciesPopuationCountPerYearTestCase(BaseTestCase):
    """
    Test the species population count API endpoint.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("species_population_count")

    def test_species_population_count(self) -> None:
        """
        Test species population count.
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get('species_name'), 'Lion')
        self.assertEqual(
            response.data[0]['annualpopulation_count'][0].get('year_total'),
            response.data[0]['annualpopulation_count'][4]['year_total']
        )

    def test_species_population_count_filter_by_name(self) -> None:
        """
        Test species population count filtered by species name.
        """
        data = {'species': 'Penthera leo'}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['species_name'], 'Lion')

    def test_species_population_count_filter_by_property(self) -> None:
        """
        Test species population count filtered by property.
        """
        id = self.owned_species[0].property_id
        data = {'property':id}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['annualpopulation_count'][0].get('year_total'),
            response.data[0]['annualpopulation_count'][4]['year_total']
        )

    def test_species_population_count_filter_by_year(self) -> None:
        """
        Test species population count filtered by year.
        """
        year = self.owned_species[1].annualpopulation_set.first().year
        data = {'start_year': year, "end_year":year}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['annualpopulation_count'][0].get('year'),
            year
        )


class ActivityPercentageTestCase(BaseTestCase):
    """
    Test the activity percentage API endpoint.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("activity_percentage")

    def test_activity_percentage(self) -> None:
        """
        Test activity percentage calculation.
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]['total'], 500)
        self.assertEqual(
            list(response.data['data'][0]['activities'][0].values())[0], 20.0
        )

    def test_activity_percentage_filter_by_year(self) -> None:
        """
        Test activity percentage calculation with year-based filters.
        """
        year = self.owned_species[1].annualpopulationperactivity_set.first().year
        data = {'start_year': year, "end_year":year}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('data')[0].get('total'), 500)


class TotalCountPerActivityTestCase(BaseTestCase):
    """
    Test the total count per activity API endpoint.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("total_count_per_activity")

    def test_total_count_per_activity(self) -> None:
        """
        Test total count per activity calculation.
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data[0]['activities']), 5)
        self.assertGreater(len(response.data), 0)
        # test with property id
        data = { 'property': self.property.id }
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SpeciesPopulationDensityPerPropertyTestCase(BaseTestCase):
    """
    Test the species population total density API endpoint.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("species_population_total_density")

    def test_species_population_density_per_property(self) -> None:
        """
        Test species population density per property.
        """
        url = self.url
        data = {"species": "Penthera leo"}
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # test with no species or property
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # test with non existent owned species
        data = {"species": "leo"}
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_species_population_density_filter_by_year(self) -> None:
        """
        Test species population density per property filtered by year.
        """
        year = self.owned_species[1].annualpopulation_set.first().year
        data = {'start_year': year, "end_year":year, "species": "Penthera leo"}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_item = response.data[0]
        # Check if the 'density' property exists and is a list
        if 'density' in first_item and isinstance(first_item['density'], list):
            # Access property name
            if first_item['density'] and isinstance(first_item['density'][0], dict):
                property_name = first_item['density'][0].get('property_name')

                self.assertEqual(property_name, 'Propertya')


class PropertiesPerPopulationCategoryTestCase(BaseTestCase):
    """
    Test case for the endpoint that retrieves
    properties population categories.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("properties_per_population_category")

    def test_properties_per_population_category(self) -> None:
        """
        Test properties per population category.
        """
        url = self.url
        # test without species name
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test with property id only to check if response is oke
        id = self.owned_species[0].property_id
        data = {'property':id}
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # test property id
        id = self.owned_species[0].property_id
        data = {'property':id, 'species': 'Penthera leo'}
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TotalAreaAvailableToSpeciesTestCase(BaseTestCase):
    """
    Test case for the endpoint that retrieves
    total area available to species.
    """
    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("total_area_available_to_species")

    def test_total_area_available_to_species(self) -> None:
        """
        Test total area available to species.
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['area'], 50.0)
        
        data = {'property': self.owned_species[0].property_id, 'species': "Penthera leo"}
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['area'], 50.0)


    def test_total_area_available_to_species_filter_by_property(self) -> None:
        """
        Test total area available to species filtered by property.
        """
        id = self.owned_species[0].property_id
        data = {'property':id}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['property_name'], 'Propertya')


class TotalAreaPerPropertyTypeTestCase(BaseTestCase):
    """
    Test case for the endpoint that retrieves
    total area per property type.
    """

    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("total_area_per_property_type")

    def test_total_area_per_property_type(self) -> None:
        """
        Test total area per property type
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        property_type = self.property.property_type.name
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['total_area'], 200)
        self.assertEqual(
            response.data[0]['property_type__name'],
            property_type
        )

    def test_total_area_per_property_type_filter_by_property(self):
        """
        Test total area per property type filtered by property.
        """
        id = self.owned_species[0].property_id
        data = {'property':id}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['total_area'], 200)


class PopulationPerAgeGroupTestCase(BaseTestCase):
    """
    Test case for the endpoint that retrieves
    population per age group.
    """

    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("population_per_age_group")

    def test_total_area_per_property_type(self) -> None:
        """
        Test population per age group
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['age_group'][0]['total_adult_male'], 50
        )
        self.assertEqual(
            response.data[0]['age_group'][0]['total_adult_female'], 50
        )
        self.assertEqual(
            response.data[0]['age_group'][0]['total_sub_adult_male'], 10
        )
        self.assertEqual(
            response.data[0]['age_group'][0]['total_sub_adult_female'], 10
        )

    def test_total_area_per_property_type_filter_by_property(self):
        """
        Test population per age group filtered by property.
        """
        id = self.owned_species[0].property_id
        data = {'property':id}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['age_group'][0]['total_juvenile_female'], 30
        )
        self.assertEqual(
            response.data[0]['age_group'][0]['total_juvenile_female'], 30
        )


    def test_species_population_count_filter_by_year(self) -> None:
        """
        Test spopulation per age group filtered by year.
        """
        year = self.owned_species[1].annualpopulation_set.first().year
        data = {'start_year': year, "end_year":year}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
        response.data[0]['age_group'][0]['total_sub_adult_male'], 10
        )
        self.assertEqual(
            response.data[0]['age_group'][0]['total_sub_adult_female'], 10
        )


class TotalAreaVSAreaAvailableTestCase(BaseTestCase):
    """
    Test case for the endpoint that retrieves
    total area versus area available to species.
    """

    def setUp(self) -> None:
        """
        Set up the test case.
        """
        super().setUp()
        self.url = reverse("total_area_vs_available_area")

    def test_total_area_vs_area_available(self) -> None:
        """
        Test total area versus area available.
        """
        url = self.url
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['area']['owned_species'][0]['area_total'], 200
        )
        self.assertEqual(
            response.data[0]['area']['owned_species'][0]['area_available'], 10
        )

    def test_total_area_vs_area_available_filter_by_property(self) -> None:
        """
        Test total area versus area available filtered by property.
        """
        id = self.owned_species[0].property_id
        data = {'property':id}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['area']['owned_species'][0]['area_total'], 200
        )

    def test_total_area_vs_area_available_filter_by_year(self) -> None:
        """
        Test total area versus area available filtered by year.
        """
        year = self.owned_species[1].annualpopulation_set.first().year
        data = {'start_year': year, "end_year":year}
        url = self.url
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]['area']['owned_species'][0] \
                ['annualpopulation__year'],
            year
        )
