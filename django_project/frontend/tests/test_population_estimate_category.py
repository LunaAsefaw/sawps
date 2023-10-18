import unittest
from django.http import HttpRequest
from population_data.models import PopulationEstimateCategory
from frontend.serializers.metrics import TotalCountPerPopulationEstimateSerializer
from django.test import TestCase, Client
from species.models import OwnedSpecies
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
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )

        taxon_rank = TaxonRank.objects.filter(name="Species").first()
        if not taxon_rank:
            taxon_rank = TaxonRankFactory.create(name="Species")

        self.taxon = Taxon.objects.create(
            taxon_rank=taxon_rank, common_name_varbatim="Lion",
            scientific_name = "Penthera leo"
        )

        self.user = User.objects.create_user(
            username="testuserd",
            password="testpasswordd"
        )

        # Create test data, including properties and owned species
        self.property1 = PropertyFactory.create(name="Property 1", organisation=self.organisation)
        self.property2 = PropertyFactory.create(name="Property 2", organisation=self.organisation)

        self.owned_species_one = OwnedSpecies.objects.create(
            property=self.property1,
            user=self.user,
            taxon=self.taxon
        )
        self.owned_species_two = OwnedSpecies.objects.create(
            property=self.property2,
            user=self.user,
            taxon=self.taxon
        )
        OwnedSpecies.objects.create(
            property=self.property1,
            user=self.user,
            taxon=self.taxon
        )

        self.category_a = PopulationEstimateCategory.objects.create(name="Category A")
        self.category_b = PopulationEstimateCategory.objects.create(name="Category B")

        AnnualPopulationF.create(
            year=2020,
            owned_species=self.owned_species_two,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=self.category_a
        )

        AnnualPopulationF.create(
            year=2020,
            owned_species=self.owned_species_two,
            total=200,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=self.category_a
        )
        
        AnnualPopulationF.create(
            year=2020,
            owned_species=self.owned_species_two,
            total=100,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
            population_estimate_category=self.category_b
        )

        self.auth_headers = {
            "HTTP_AUTHORIZATION": "Basic "
            + base64.b64encode(b"testuserd:testpasswordd").decode("ascii"),
        }
        self.client = Client()

        session = self.client.session
        session.save()

        self.url = reverse("total-count-per-population-estimate")

        url = self.url
        data = {
                'species':"Penthera leo",
                'property':[str(self.property1.id),str(self.property2.id)],
                'start_year':"2020",
                'end_year':"2020"
        }
        response = self.client.get(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Call the method you want to test
        result = response.data

        # Calculate the expected percentages
        expected_percentage_a = (2 / 3) * 100
        expected_percentage_b = (1 / 3) * 100

        # Define the expected result
        expected_result = {
            'Category A': {
                'count': 2,
                'percentage': 0.6666666666666667,
                'total': 300,
                'years': [2020],
            },
            'Category B': {
                'count': 1,
                'percentage': 1.0,
                'total': 100,
                'years': [2020],
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
