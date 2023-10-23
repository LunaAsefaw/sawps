from django.test import TestCase

from frontend.serializers.report import (
    SamplingReportSerializer,
    PropertyReportSerializer,
    SpeciesReportSerializer
)
from frontend.tests.test_data_table import OwnedSpeciesTestMixins
from population_data.factories import AnnualPopulationF
from population_data.models import (
    AnnualPopulation
)
from species.models import OwnedSpecies


class TestReportSerializer(OwnedSpeciesTestMixins, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.owned_species_obj: OwnedSpecies = self.owned_species[0]
        self.annual_population: AnnualPopulation = AnnualPopulationF(
            owned_species=self.owned_species_obj, year=2021, total=30,
            adult_male=10, adult_female=10
        )

    def test_species_report_serializer(self):
        annual_population = AnnualPopulation.objects.first()
        serializer = SpeciesReportSerializer(annual_population)
        expected_value = {
            "property_name": self.property.name,
            "property_short_code": self.property.short_code,
            "organisation_name": self.organisation_1.name,
            "organisation_short_code": self.organisation_1.short_code,
            "scientific_name": self.taxon.scientific_name,
            "common_name": self.taxon.common_name_varbatim,
            "year": annual_population.year,
            "group": None,
            "total": annual_population.total,
            "adult_male": annual_population.adult_male,
            "adult_female": annual_population.adult_female,
            "juvenile_male": annual_population.juvenile_male,
            "juvenile_female": annual_population.juvenile_female,
            "sub_adult_male": annual_population.sub_adult_male,
            "sub_adult_female": annual_population.sub_adult_female,
        }
        self.assertEqual(
            serializer.data,
            expected_value
        )

    def test_property_report_serializer(self):
        serializer = PropertyReportSerializer(self.owned_species_obj)
        expected_value = {
            "property_name": self.owned_species_obj.property.name,
            "property_short_code": self.owned_species_obj.property.short_code,
            "organisation_name": self.owned_species_obj.property.organisation.name,
            "organisation_short_code": self.owned_species_obj.property.organisation.short_code,
            "scientific_name": self.owned_species_obj.taxon.scientific_name,
            "common_name": self.owned_species_obj.taxon.common_name_varbatim,
            "owner": "",
            "owner_email": self.owned_species_obj.property.owner_email,
            "property_type": self.owned_species_obj.property.property_type.name,
            "province": self.owned_species_obj.property.province.name,
            "property_size_ha": 200,
            "area_available_to_species": 10.0,
            "open_close_systems": "",
        }

        self.assertEqual(
            serializer.data,
            expected_value
        )

    def test_sampling_report_serializer(self):
        annual_population = AnnualPopulation.objects.first()
        serializer = SamplingReportSerializer(annual_population)
        expected_value = {
            "property_name": self.property.name,
            "property_short_code": self.property.short_code,
            "organisation_name": self.organisation_1.name,
            "organisation_short_code": self.organisation_1.short_code,
            "scientific_name": self.taxon.scientific_name,
            "common_name": self.taxon.common_name_varbatim,
            "population_status": "",
            "population_estimate_category": "",
            "survey_method": "",
            "sampling_effort_coverage": "",
            "population_estimate_certainty": None,
        }

        self.assertEqual(
            serializer.data,
            expected_value
        )
