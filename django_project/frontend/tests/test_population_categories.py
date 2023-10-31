from regulatory_permit.models import DataUsePermission
from stakeholder.models import Organisation
from frontend.tests.model_factories import UserF
from property.factories import PropertyFactory
from population_data.factories import AnnualPopulationF
from population_data.models import AnnualPopulation
from frontend.utils.metrics import calculate_population_categories
import unittest
from species.factories import (
    TaxonRankFactory
)
from species.models import Taxon, TaxonRank
from unittest.mock import patch
from property.models import Property
from django.db.models.query import QuerySet
from django.test import TestCase

class TestCalculatePopulationCategories(TestCase):
    def setUp(self):
        taxon_rank = TaxonRank.objects.filter(name="Species").first()
        if not taxon_rank:
            taxon_rank = TaxonRankFactory.create(name="Species")

        self.taxon = Taxon.objects.create(
            taxon_rank=taxon_rank, common_name_varbatim="Lion",
            scientific_name = "Penthera leo"
        )

        self.taxon1 = Taxon.objects.create(
            taxon_rank=taxon_rank, common_name_varbatim="Cheetah",
            scientific_name = "Cheetah"
        )

        self.user = UserF.create()

        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )

        self.property = PropertyFactory.create(
            organisation=self.organisation, name="PropertyA"
        )

        AnnualPopulationF.create(
            taxon=self.taxon,
            user=self.user,
            property=self.property,
            year=2020,
            total=100,
            adult_male=50,
            adult_female=50,
            juvenile_male=30,
            juvenile_female=30,
            sub_adult_total=20,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=40,
            area_available_to_species=100
        )

        AnnualPopulationF.create(
            taxon=self.taxon,
            user=self.user,
            property=self.property,
            year=2021,
            total=200,
            adult_male=50,
            adult_female=50,
            juvenile_male=30,
            juvenile_female=30,
            sub_adult_total=20,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=40,
            area_available_to_species=300
        )

        AnnualPopulationF.create(
            taxon=self.taxon1,
            user=self.user,
            property=self.property,
            year=2021,
            total=300,
            adult_male=50,
            adult_female=50,
            juvenile_male=30,
            juvenile_female=30,
            sub_adult_total=20,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=40,
            area_available_to_species=200
        )


    def test_empty_queryset(self):
        # Test when the queryset is empty
        queryset = Property.objects.none()
        species_name = "Penthera leo"
        result = calculate_population_categories(queryset, species_name)
        self.assertEqual(result, {})

    def test_no_annual_population_data(self):
        # Test when there is no annual population data
        queryset = Property.objects.filter(
            id__in=[1, 2]
        )
        species_name = "Pleo"
        result = calculate_population_categories(queryset, species_name)
        self.assertEqual(result, {})

    @patch('population_data.models.AnnualPopulation.objects.filter')
    def test_population_categories_calculation(self, mock_filter):
        # Test the calculation of population categories
        # Create mock annual population data
        annual_population_data = [
            {'year': 2020, 'population_total': 100},
            {'year': 2020, 'population_total': 200},
            {'year': 2020, 'population_total': 200},
            {'year': 2021, 'population_total': 400},
            {'year': 2022, 'population_total': 300},
            {'year': 2023, 'population_total': 200},
        ]

        # Create a mock queryset and set its return value
        mock_queryset = QuerySet(model=AnnualPopulation)
        mock_queryset._result_cache = annual_population_data
        mock_filter.return_value = mock_queryset

        queryset = Property.objects.filter(
            id__in=[1, 2]
        )
        species_name = "Panthera Leo"
        result = calculate_population_categories(queryset, species_name)

        # Confirm it contains data
        self.assertIsNotNone(result)

        self.assertTrue(
            result['category_labels'],
            ['100-133', '133-166', '166-200', '200-233', '233-266', '>266']
        )

        self.assertTrue(
            result['data'][0]['area'],
            100
        )


if __name__ == '__main__':
    unittest.main()
