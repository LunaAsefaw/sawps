"""Test case for population data models.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from population_data.factories import (
    AnnualPopulationF,
    AnnualPopulationPerActivityFactory,
    CertaintyF,
    OpenCloseSystemF,
    PopulationEstimateCategoryF,
    PopulationStatusF,
    SamplingEffortCoverageF
)
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    Certainty,
    OpenCloseSystem,
    PopulationEstimateCategory,
    PopulationStatus,
    SamplingEffortCoverage
)
from species.factories import TaxonFactory, TaxonRankFactory
from species.models import Taxon


class PopulationCountTestCase(TestCase):
    """Population count test case."""
    @classmethod
    def setUpTestData(cls):
        """SetUpTestData for population count test case."""
        taxon = TaxonFactory.create(
            scientific_name='taxon_0',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=TaxonRankFactory(),
        )
        user = User.objects.create_user(username='testuser', password='12345')
        cls.population_count = AnnualPopulationF(
            taxon=taxon,
            user=user,
            total=120,
            adult_male=19,
            adult_female=100
        )

    def test_create_population_count(self):
        """Test create population count."""
        self.assertTrue(
            isinstance(self.population_count, AnnualPopulation)
        )
        self.assertTrue(
            AnnualPopulation.objects.filter(
                id=self.population_count.id
            ).exists()
        )


    def test_update_population_count(self):
        """Test update population count."""
        self.population_count.total = 125
        self.population_count.save()
        self.assertEqual(
            AnnualPopulation.objects.get(year=self.population_count.year).total, 125
        )

    def test_delete_population_count(self):
        """Test delete population count."""
        self.population_count.delete()
        self.assertFalse(
            AnnualPopulation.objects.filter(id=self.population_count.id).exists()
        )

    def test_adult_population_validation(self):
        """
        Test that a ValidationError is raised when the sum of adult_male and
        adult_female exceeds the total.
        """
        data = {
            'year': 2023,
            'total': 100,
            'adult_male': 60,
            'adult_female': 50,
        }
        with self.assertRaises(ValidationError):
            population_instance = AnnualPopulation(**data)
            population_instance.clean()


class AnnualPopulationPerActivityTestCase(TestCase):
    """Population count test case."""
    @classmethod
    def setUpTestData(cls):
        """SetUpTestData for population count test case."""
        taxon = Taxon.objects.create(
            scientific_name='taxon_0',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=TaxonRankFactory(),
        )
        user = User.objects.create_user(username='testuser', password='12345')
        population = AnnualPopulationF(
            taxon=taxon,
            user=user,
            total=120,
            adult_male=19,
            adult_female=100
        )
        cls.population_count = AnnualPopulationPerActivityFactory(
            annual_population=population,
            intake_permit='1',
            offtake_permit='1'
        )

    def test_create_population_count(self):
        """Test create population count."""
        self.assertTrue(
            isinstance(self.population_count, AnnualPopulationPerActivity)
        )
        self.assertTrue(
            AnnualPopulationPerActivity.objects.filter(
                id=self.population_count.id
            ).exists()
        )


    def test_update_population_count(self):
        """Test update population count."""
        self.population_count.total = 100
        self.population_count.save()
        self.assertEqual(
            AnnualPopulationPerActivity.objects.get(year=self.population_count.year).total, 100
        )

    def test_year_activity_type_fields_unique_toghter_constraint(self):
        """Test year, annual population, and activity_type are unique togther."""
        with self.assertRaises(IntegrityError) as raised:
            AnnualPopulationPerActivityFactory(
                annual_population=self.population_count.annual_population,
                year=self.population_count.year,
                activity_type=self.population_count.activity_type,
                intake_permit='1',
                offtake_permit='1'
            )

    def test_delete_population_count(self):
        """Test delete population count."""
        initial_count = AnnualPopulationPerActivity.objects.count()
        self.population_count.delete()
        with self.assertRaises(AnnualPopulationPerActivity.DoesNotExist):
            AnnualPopulationPerActivity.objects.get(pk=self.population_count.pk)
        self.assertEqual(
            AnnualPopulationPerActivity.objects.count(),
            initial_count - 1,
            msg="The count of AnnualPopulationPerActivity"
            "instances did not decrease by 1 after deletion."
        )


class TestCertainty(TestCase):
    """Test for certainty model."""

    def setUp(self) -> None:
        """setup test data"""
        self.Certainty = CertaintyF(name='name', description='text')

    def test_create_certainty(self):
        """test create certainty."""
        self.assertEqual(self.Certainty.name, 'name')
        self.assertEqual(self.Certainty.description, 'text')
        self.assertEqual(Certainty.objects.count(), 1)
        self.assertEqual(str(self.Certainty), self.Certainty.name)

    def test_update_Certainty(self):
        """test update certainty."""
        self.Certainty.name = 'Certainty'
        self.Certainty.description = 'Certainty description'
        self.Certainty.save()
        self.assertEqual(self.Certainty.name, 'Certainty')
        self.assertEqual(self.Certainty.description, 'Certainty description')

    def test_delete_certainty(self):
        """test delete certainty."""
        self.Certainty.delete()
        self.assertEqual(Certainty.objects.count(), 0)


class TestOpenCloseSystem(TestCase):
    """Test for open close system model."""

    def setUp(self) -> None:
        """setup test data"""
        self.open_close_sustem = OpenCloseSystemF(name='name')

    def test_create_open_close_system(self):
        """test create open close system."""
        self.assertEqual(self.open_close_sustem.name, 'name')
        self.assertEqual(OpenCloseSystem.objects.count(), 1)

    def test_update_open_close_system(self):
        """test update open close system."""
        self.open_close_sustem.name = 'OpenCloseSystem'
        self.open_close_sustem.save()
        self.assertEqual(self.open_close_sustem.name, 'OpenCloseSystem')

    def test_delete_open_close_system(self):
        """test delete open close system."""
        self.open_close_sustem.delete()
        self.assertEqual(OpenCloseSystem.objects.count(), 0)


class TestPopulationEstimateCategory(TestCase):
    """Test for population estimate category model."""

    def setUp(self) -> None:
        """setup test data."""
        self.population_estimate_category = PopulationEstimateCategoryF(
            name='name'
            )

    def test_create_population_estimate(self):
        """test create population estimate category."""
        self.assertEqual(self.population_estimate_category.name, 'name')
        self.assertEqual(str(self.population_estimate_category), 'name')
        self.assertEqual(PopulationEstimateCategory.objects.count(), 1)

    def test_update_population_estimate(self):
        """test update population estimate category."""
        self.population_estimate_category.name = 'PopulationEstimateCategory'
        self.population_estimate_category.save()
        self.assertEqual(
            self.population_estimate_category.name,
            'PopulationEstimateCategory'
        )

    def test_delete_population_estimate(self):
        """test delete population estimate category."""
        self.population_estimate_category.delete()
        self.assertEqual(PopulationEstimateCategory.objects.count(), 0)

    def test_population_estimate_name_constraint(self):
        """Test population estimate category name contraint."""
        another = PopulationEstimateCategoryF(name='Population estimate')
        self.assertEqual(PopulationEstimateCategory.objects.count(), 2)
        self.assertNotEqual(
            self.population_estimate_category.name,
            another.name
        )
        with self.assertRaises(Exception) as raised:
            PopulationEstimateCategoryF(name='name')


class TestPopulationSatatus(TestCase):
    """Test for population status model."""

    def setUp(self) -> None:
        """setup test data."""
        self.population_status = PopulationStatusF(
            name='name'
            )

    def test_create_population_status(self):
        """test create population status."""
        self.assertEqual(self.population_status.name, 'name')
        self.assertEqual(str(self.population_status), 'name')
        self.assertEqual(PopulationStatus.objects.count(), 1)

    def test_update_population_status(self):
        """test update population status."""
        self.population_status.name = 'PopulationSatatus'
        self.population_status.save()
        self.assertEqual(
            self.population_status.name,
            'PopulationSatatus'
        )

    def test_delete_population_status(self):
        """test delete population status."""
        self.population_status.delete()
        self.assertEqual(PopulationStatus.objects.count(), 0)

    def test_population_status_name_constraint(self):
        """Test population status name contraint."""
        another = PopulationStatusF(name='Population Status')
        self.assertEqual(PopulationStatus.objects.count(), 2)
        self.assertNotEqual(self.population_status.name, another.name)

        with self.assertRaises(Exception) as raised:
            PopulationStatusF(name='name')


class TestSamplingEffortCoverage(TestCase):
    """Test for sampling effort coverage model."""

    def setUp(self) -> None:
        """setup test data."""
        self.coverage = SamplingEffortCoverageF(
            name='name'
            )

    def test_create_sampling_effort_cov(self):
        """test create sampling effort coverage."""
        self.assertEqual(self.coverage.name, 'name')
        self.assertEqual(str(self.coverage), 'name')
        self.assertEqual(SamplingEffortCoverage.objects.count(), 1)

    def test_update_sampling_effort_cov(self):
        """test update sampling effort coverage."""
        self.coverage.name = 'Test1'
        self.coverage.save()
        self.assertEqual(
            self.coverage.name,
            'Test1'
        )

    def test_delete_sampling_effort_cov(self):
        """test delete sampling effort coverage."""
        self.coverage.delete()
        self.assertEqual(SamplingEffortCoverage.objects.count(), 0)

    def test_sampling_effort_cov_name_constraint(self):
        """Test sampling effort coverage name contraint."""
        another = SamplingEffortCoverageF(name='Coverage2')
        self.assertEqual(SamplingEffortCoverage.objects.count(), 2)
        self.assertNotEqual(self.coverage.name, another.name)

        with self.assertRaises(Exception) as raised:
            SamplingEffortCoverageF(name='name')
