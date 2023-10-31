from django.test import TestCase
from population_data.factories import AnnualPopulationF, AnnualPopulationPerActivityFactory
from sawps.tests.models.account_factory import (
    UserF,
    GroupF,
)
from population_data.models import AnnualPopulation, AnnualPopulationPerActivity
from species.models import OwnedSpecies
from species.factories import TaxonFactory
from property.factories import PropertyFactory
from activity.factories import ActivityTypeFactory
from population_data.utils import (
    copy_owned_species_fields,
    assign_annual_population
)


class TestMigrationFunction(TestCase):
    """
    Test migration function.
    """

    def setUp(self) -> None:
        taxon = TaxonFactory.create()
        property_obj = PropertyFactory.create()
        user = UserF.create()
        self.activity_type = ActivityTypeFactory.create()
        self.owned_species = OwnedSpecies.objects.create(
            taxon=taxon,
            property=property_obj,
            user=user,
            area_available_to_species=10
        )
        self.annual_population = AnnualPopulation.objects.create(
            year=2023,
            owned_species=self.owned_species,
            total=100
        )
        AnnualPopulation.objects.create(
            year=2022,
            owned_species=self.owned_species,
            total=50
        )
        self.annual_population_per_activity = AnnualPopulationPerActivity.objects.create(
            year=2023,
            owned_species=self.owned_species,
            total=100,
            activity_type=self.activity_type
        )

    def test_copy_owned_species_fields(self):
        fields = [
            'user',
            'taxon',
            'property',
            'area_available_to_species'
        ]
        for field in fields:
            if field == 'area_available_to_species':
                self.assertEqual(
                    getattr(self.annual_population, field),
                    0.0
                )
            else:
                self.assertIsNone(
                    getattr(self.annual_population, field)
                )
        copy_owned_species_fields(self.annual_population)
        self.annual_population.refresh_from_db()
        for field in fields:
            self.assertEqual(
                getattr(self.annual_population, field),
                getattr(self.owned_species, field)
            )


    def test_assign_annual_population(self):
        assign_annual_population(self.annual_population_per_activity)
        self.annual_population_per_activity.refresh_from_db()
        self.assertEqual(
            self.annual_population_per_activity.annual_population,
            self.annual_population,
        )

    def test_assign_annual_population_not_exist(self):
        taxon = TaxonFactory.create()
        property_obj = PropertyFactory.create()
        user = UserF.create()
        activity_type = ActivityTypeFactory.create()
        owned_species = OwnedSpecies.objects.create(
            taxon=taxon,
            property=property_obj,
            user=user,
            area_available_to_species=5
        )
        an_pop_pa = AnnualPopulationPerActivity.objects.create(
            year=2023,
            owned_species=owned_species,
            total=10,
            activity_type=self.activity_type
        )
        AnnualPopulationPerActivity.objects.create(
            year=2023,
            owned_species=owned_species,
            total=20,
            activity_type=activity_type
        )
        assign_annual_population(an_pop_pa)

        # The annual population total would be 30, coming from 20 + 10
        self.assertEqual(an_pop_pa.annual_population.total, 30)
