import unittest
from django.http import HttpRequest
from population_data.models import PopulationEstimateCategory
from frontend.serializers.metrics import TotalCountPerPopulationEstimateSerializer
from django.test import TestCase, Client
from regulatory_permit.models import DataUsePermission
from stakeholder.models import Organisation
from property.factories import PropertyFactory
from species.factories import (
    TaxonRankFactory
)
from species.models import Taxon, TaxonRank
from population_data.factories import AnnualPopulationF
import base64
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

class TotalCountPerPopulationEstimateSerializerTestCase(TestCase):
    def setUp(self):
        # Create and set up test data, such as AnnualPopulation records
        self.species_name = "TestSpecies"
        self.property_ids = [1, 2]
        self.start_year = 2020
        self.end_year = 2022

        # Create an instance of the serializer
        self.serializer = TotalCountPerPopulationEstimateSerializer(
            context={
                "request": HttpRequest(),
            }
        )

    def test_get_total_counts_per_population_estimate(self):
        data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=data_use_permission
        )

        taxon_rank = TaxonRank.objects.filter(name="Species").first()
        if not taxon_rank:
            taxon_rank = TaxonRankFactory.create(name="Species")

        taxon = Taxon.objects.create(
            taxon_rank=taxon_rank, common_name_varbatim="Lion",
            scientific_name="Penthera leo"
        )

        self.user = User.objects.create_user(
            username="testuserd",
            password="testpasswordd"
        )

        # Create test data, including properties and owned species
        property1 = PropertyFactory.create(name="Property 1", organisation=organisation)
        property2 = PropertyFactory.create(name="Property 2", organisation=organisation)
        property3 = PropertyFactory.create(name="Property 3", organisation=organisation)

        category_a = PopulationEstimateCategory.objects.create(name="Category A")
        category_b = PopulationEstimateCategory.objects.create(name="Category B")

        AnnualPopulationF.create(
            year=2020,
            property=property1,
            user=self.user,
            taxon=taxon,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=category_a
        )

        AnnualPopulationF.create(
            year=2022,
            property=property1,
            user=self.user,
            taxon=taxon,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=category_a
        )

        AnnualPopulationF.create(
            year=2020,
            property=property2,
            user=self.user,
            taxon=taxon,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=category_a
        )

        AnnualPopulationF.create(
            year=2022,
            property=property3,
            user=self.user,
            taxon=taxon,
            total=200,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=category_a
        )

        AnnualPopulationF.create(
            year=2022,
            property=property2,
            user=self.user,
            taxon=taxon,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=category_b
        )

        auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
                                  + base64.b64encode(b"testuserd:testpasswordd").decode("ascii"),
        }
        client = Client()

        session = client.session
        session.save()

        url = reverse("total-count-per-population-estimate")
        data = {
            'species': "Penthera leo",
            'property': f"{property1.id},{property2.id},{property3.id}",
            'start_year': "2020",
            'end_year': "2022"
        }
        response = client.get(url, data, **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Call the method you want to test
        result = response.data

        # Define the expected result
        expected_result = {
            'Category A': {
                'count': 2,
                'percentage': 0.66,
                'total': 300,
                'years': [2022],
            },
            'Category B': {
                'count': 1,
                'percentage': 1.0,
                'total': 100,
                'years': [2022],
            },
        }

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_empty_data(self):
        # Test when there's no data
        result = self.serializer.get_total_counts_per_population_estimate()
        self.assertEqual(result, {}) 

    def test_invalid_species_name(self):
        # Test with an invalid species name
        self.serializer.context["request"].GET["species"] = "NonExistentSpecies"
        result = self.serializer.get_total_counts_per_population_estimate()
        self.assertEqual(result, {})

    def test_invalid_property_ids(self):
        # Test with invalid property IDs
        self.serializer.context["request"].GET["property"] = "100,200,300"
        result = self.serializer.get_total_counts_per_population_estimate()
        self.assertEqual(result, {})

if __name__ == "__main__":
    unittest.main()
