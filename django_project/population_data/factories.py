"""Test factories for population data package.
"""
import factory
from random import randint
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationAbstract,
    AnnualPopulationPerActivity,
    Certainty,
    OpenCloseSystem,
    PopulationEstimateCategory,
    PopulationStatus,
    SamplingEffortCoverage
)


class AnnualPopulationAbstractFactory(factory.django.DjangoModelFactory):
    """Population count abstract factory."""

    class Meta:
        model = AnnualPopulationAbstract
        abstract = True

    year = factory.Sequence(lambda n: f"{n}")
    total = 100
    adult_male = 50
    adult_female = 50
    juvenile_male = 30
    juvenile_female = 30


class AnnualPopulationF(AnnualPopulationAbstractFactory):
    """Population count factory."""

    class Meta:
        model = AnnualPopulation

    user = factory.SubFactory('species.factories.UserFactory')
    taxon = factory.SubFactory('species.factories.TaxonFactory')
    property = factory.SubFactory('property.factories.PropertyFactory')
    area_available_to_species = 10
    sub_adult_total = 20
    sub_adult_male = 10
    sub_adult_female = 10
    juvenile_total = 40

    @factory.post_generation
    def create_annual_population_per_activity(self, create, *args):
        year = randint(1960, 2000)
        if len(AnnualPopulation.objects.filter(year=year)) > 0:
            year = randint(2001, 2023)
        AnnualPopulationPerActivityFactory.create(
            year=self.year,
            annual_population=self,
            total=100,
            adult_male=50,
            adult_female=50,
            juvenile_male=30,
            juvenile_female=30,
        )


class AnnualPopulationPerActivityFactory(AnnualPopulationAbstractFactory):
    """Population count per activity factory."""

    class Meta:
        model = AnnualPopulationPerActivity

    annual_population = factory.SubFactory(AnnualPopulationF)
    activity_type = factory.SubFactory(
        "activity.factories.ActivityTypeFactory"
    )
    founder_population = True
    reintroduction_source = factory.Sequence(
        lambda n: f"reintroduction source-{n}"
    )
    intake_permit = factory.Faker("random_int")



class CertaintyF(factory.django.DjangoModelFactory):
    """Certainty factory."""

    class Meta:
        """meta"""

        model = Certainty


class OpenCloseSystemF(factory.django.DjangoModelFactory):
    """Open Close System factory."""

    class Meta:
        """meta"""

        model = OpenCloseSystem


class PopulationStatusF(factory.django.DjangoModelFactory):
    """Population Status factory."""

    class Meta:
        """meta"""

        model = PopulationStatus


class PopulationEstimateCategoryF(factory.django.DjangoModelFactory):
    """Population Status factory."""

    class Meta:
        """meta"""

        model = PopulationEstimateCategory


class SamplingEffortCoverageF(factory.django.DjangoModelFactory):
    """SamplingEffortCoverage factory."""

    class Meta:
        """meta"""

        model = SamplingEffortCoverage
