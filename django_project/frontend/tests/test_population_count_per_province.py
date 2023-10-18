from django.test import TestCase
from frontend.utils.metrics import calculate_species_count_per_province
from species.models import OwnedSpecies
from property.models import Property, Province
from regulatory_permit.models import DataUsePermission
from stakeholder.models import Organisation
from frontend.tests.model_factories import UserF
from property.factories import PropertyFactory
from species.factories import (
    OwnedSpeciesFactory,
    TaxonRankFactory
)
from species.models import Taxon, TaxonRank
from population_data.factories import AnnualPopulationF


class SpeciesCountPerProvinceTest(TestCase):
    def setUp(self):

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

        self.user = UserF.create()

        self.province1 = Province.objects.create(name="Province1")
        self.province2 = Province.objects.create(name="Province2")

        # Create test data, including properties and owned species
        self.property1 = PropertyFactory.create(name="Property 1", province=self.province1, organisation=self.organisation)
        self.property2 = PropertyFactory.create(name="Property 2", province=self.province2, organisation=self.organisation)

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

        AnnualPopulationF.create(
            year=2023,
            owned_species=self.owned_species_two,
            total=60,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
        )

        AnnualPopulationF.create(
            year=2022,
            owned_species=self.owned_species_one,
            total=20,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
        )

        AnnualPopulationF.create(
            year=2022,
            owned_species=self.owned_species_one,
            total=30,
            adult_male=10,
            adult_female=10,
            juvenile_male=10,
            juvenile_female=10,
            sub_adult_total=10,
            sub_adult_male=10,
            sub_adult_female=10,
            juvenile_total=10,
        )

    def test_calculate_species_count_per_province(self):
        # Call the function with test data
        queryset = Property.objects.all()
        species_name = "Penthera leo"
        result_data = calculate_species_count_per_province(queryset, species_name)

        # Perform assertions based on the expected results
        self.assertEqual(len(result_data), 3)  # We have two provinces
        self.assertEqual(result_data[0]["province"], "Province1")
        self.assertEqual(result_data[0]["species"], "Penthera leo")
        self.assertEqual(result_data[0]["year"], 2022)
        self.assertEqual(result_data[0]["count"], 50)

        self.assertEqual(result_data[2]["province"], "Province2")
        self.assertEqual(result_data[2]["species"], "Penthera leo")
        self.assertEqual(result_data[2]["year"], 2023)
        self.assertEqual(result_data[2]["count"], 60)
