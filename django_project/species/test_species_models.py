import base64
from unittest import mock

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from occurrence.models import SurveyMethod
from population_data.factories import AnnualPopulationF
from property.factories import PropertyFactory
from rest_framework import status
from species.factories import (
    OwnedSpeciesFactory,
    TaxonFactory,
    TaxonRankFactory,
    TaxonSurveyMethodF,
)
from species.models import OwnedSpecies, Taxon, TaxonRank, TaxonSurveyMethod
from species.serializers import TaxonSerializer
from stakeholder.factories import organisationFactory


def mocked_clear_cache(self, *args, **kwargs):
    return 1


class TaxonRankTestCase(TestCase):
    """Taxon rank test case."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for taxon rank test case."""
        cls.taxonRank = TaxonRankFactory()

    def test_create_taxon_rank(self):
        """Test create taxon rank."""
        self.assertTrue(isinstance(self.taxonRank, TaxonRank))
        self.assertEqual(
            self.taxonRank.name,
            TaxonRank.objects.get(id=self.taxonRank.id).name
        )

    def test_update_taxon_rank(self):
        """Test update taxon rank."""
        self.taxonRank.name = 'taxon_rank_1'
        self.taxonRank.save()
        self.assertEqual(
            TaxonRank.objects.get(id=self.taxonRank.id).name,
            'taxon_rank_1'
        )

    def test_unique_taxon_rank_name_constraint(self):
        """Test unique taxon rank name constraint."""
        with self.assertRaises(Exception) as raised:
            TaxonRankFactory(name='taxon_rank_1')
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_delete_taxon_rank(self):
        """Test delete taxon rank."""
        self.taxonRank.delete()
        self.assertEqual(TaxonRank.objects.count(), 0)


class TaxonTestCase(TestCase):
    """Taxon model test case."""
    @classmethod
    def setUpTestData(cls):
        """Taxon model test data."""
        cls.taxonRank = TaxonRankFactory.create(
            name='Species'
        )
        cls.taxon = TaxonFactory.create(
            scientific_name='taxon_0',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=cls.taxonRank,
            show_on_front_page=False
        )
        cls.url = reverse('species')

    def test_get_taxon_list(self):
        """Taxon list API test within the organisation"""
        organisation = organisationFactory.create()

        user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd'
        )

        user.user_profile.current_organisation = organisation
        user.save()

        property = PropertyFactory.create(
            organisation=organisation,
            name='PropertyA'
        )

        owned_species = OwnedSpeciesFactory.create_batch(
            1, taxon=self.taxon, user=user, property=property)

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
            base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }
        client = Client()
        response = client.get(self.url, **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = TaxonSerializer([self.taxon], many=True).data
        self.assertEqual(expected_data, response.data)

    def test_get_taxon_list_for_organisations(self):
        """Taxon list API test for organisations."""
        organisation = organisationFactory.create(national=True)

        user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd'
        )

        user.user_profile.current_organisation = organisation
        user.save()

        property = PropertyFactory.create(
            organisation=organisation,
            name='PropertyA'
        )

        owned_species = OwnedSpeciesFactory.create_batch(
            1, taxon=self.taxon, user=user, property=property)

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
            base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }
        client = Client()
        data = {"organisation":organisation.id}
        response = client.get(self.url, data, **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['scientific_name'], "taxon_0")

    def test_get_taxon_frontpage_list(self):
        """Test fetch taxon list for frontpage."""
        taxon = TaxonFactory.create(
            scientific_name='taxon_1',
            common_name_varbatim='taxon_1',
            colour_variant=False,
            taxon_rank=self.taxonRank,
            show_on_front_page=True
        )
        property_1 = PropertyFactory.create()
        property_2 = PropertyFactory.create()
        client = Client()
        response = client.get(reverse('species-front-page'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        taxon_1 = [d for d in response.data if d['id'] == taxon.id]
        self.assertTrue(taxon_1)
        self.assertEqual(taxon_1[0]['total_population'], 0)
        self.assertEqual(taxon_1[0]['species_name'], taxon.scientific_name)
        user_1 = User.objects.create_user(username='testuser_taxon_1', password='12345')
        owned_species_1 = OwnedSpeciesFactory(
            taxon=taxon,
            user=user_1,
            property=property_1,
            area_available_to_species=2
        )
        user_2 = User.objects.create_user(username='testuser_taxon_2', password='12345')
        owned_species_2 = OwnedSpeciesFactory(
            taxon=taxon,
            user=user_2,
            property=property_2,
            area_available_to_species=1
        )
        # create two years of data
        AnnualPopulationF(owned_species=owned_species_1, year=2021, total=30,
                          adult_male=10, adult_female=10)
        AnnualPopulationF(owned_species=owned_species_1, year=2022, total=35,
                          adult_male=10, adult_female=10)
        AnnualPopulationF(owned_species=owned_species_2, year=2020, total=15,
                          adult_male=10, adult_female=5)
        AnnualPopulationF(owned_species=owned_species_2, year=2022, total=22,
                          adult_male=10, adult_female=10)
        response = client.get(reverse('species-front-page'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        taxon_1 = [d for d in response.data if d['id'] == taxon.id]
        self.assertTrue(taxon_1)
        self.assertEqual(taxon_1[0]['total_population'], 57)
        self.assertEqual(taxon_1[0]['total_area'], 3)

    def test_get_taxon_trend_page(self):
        """Test fetch taxon detil for trend page."""
        taxon = TaxonFactory.create(
            scientific_name='taxon_1',
            common_name_varbatim='taxon_1',
            colour_variant=False,
            taxon_rank=self.taxonRank,
            show_on_front_page=True
        )
        property_1 = PropertyFactory.create()
        property_2 = PropertyFactory.create()
        client = Client()
        response = client.get(
            reverse('taxon-trend-page'),
            {
                'species': taxon.scientific_name
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['total_population'], 0)
        self.assertEqual(response.json()['species_name'], taxon.scientific_name)
        self.assertIsNone(response.json()['graph_icon'])
        user_1 = User.objects.create_user(username='testuser_taxon_1', password='12345')
        owned_species_1 = OwnedSpeciesFactory(
            taxon=taxon,
            user=user_1,
            property=property_1,
            area_available_to_species=2
        )
        user_2 = User.objects.create_user(username='testuser_taxon_2', password='12345')
        owned_species_2 = OwnedSpeciesFactory(
            taxon=taxon,
            user=user_2,
            property=property_2,
            area_available_to_species=1
        )
        # create two years of data
        AnnualPopulationF(owned_species=owned_species_1, year=2021, total=30,
                          adult_male=10, adult_female=10)
        AnnualPopulationF(owned_species=owned_species_1, year=2022, total=35,
                          adult_male=10, adult_female=10)
        AnnualPopulationF(owned_species=owned_species_2, year=2020, total=15,
                          adult_male=10, adult_female=5)
        AnnualPopulationF(owned_species=owned_species_2, year=2022, total=22,
                          adult_male=10, adult_female=10)
        response = client.get(
            reverse('taxon-trend-page'),
            {
                'species': taxon.scientific_name
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())
        self.assertEqual(response.json()['total_population'], 57)
        self.assertEqual(response.json()['total_area'], 3)
        self.assertIsNone(response.json()['graph_icon'])

    def test_create_taxon(self):
        """Test create taxon."""
        self.assertTrue(isinstance(self.taxon, Taxon))
        self.assertEqual(Taxon.objects.count(), 1)
        self.assertEqual(
            self.taxon.scientific_name,
            Taxon.objects.get(id=self.taxon.id).scientific_name
        )

    def test_update_taxon(self):
        """Test update taxon objects."""
        self.taxon.scientific_name = 'taxon_1'
        self.taxon.infraspecific_epithet = 'infra_1'
        self.taxon.save()
        self.assertEqual(
            Taxon.objects.get(id=self.taxon.id).scientific_name,
            'taxon_1'
        )
        self.assertEqual(
            Taxon.objects.get(id=self.taxon.id).infraspecific_epithet,
            'infra_1'
        )

    def test_taxon_unique_scientific_name_constraint(self):
        """Test taxon unique scientific name constraint."""
        with self.assertRaises(Exception) as raised:
            Taxon.objects.create(
                scientific_name='taxon_1',
                common_name_varbatim='taxon_0',
                colour_variant=False,
                taxon_rank=self.taxonRank,
            )
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_taxon_unique_infraspecific_epithet_constraint(self):
        """Test taxon unique infraspecific epithet constraint."""

        Taxon.objects.create(
            scientific_name='taxon_2',
            common_name_varbatim='taxon_2',
            colour_variant=False,
            infraspecific_epithet='infra_2',
            taxon_rank=self.taxonRank,
        )
        self.assertEqual(
            Taxon.objects.filter(infraspecific_epithet='infra_2').count(),
            1
        )

        with self.assertRaises(Exception) as raised:
            Taxon.objects.create(
                scientific_name='taxon_0',
                common_name_varbatim='taxon_0',
                colour_variant=False,
                infraspecific_epithet='infra_1',
                taxon_rank=self.taxonRank,
            )

    def test_taxon_relation_to_self(self):
        """Test taxon relation to self."""
        self.taxon2 = Taxon.objects.create(
            scientific_name='taxon_1',
            common_name_varbatim='taxon_1',
            colour_variant=False,
            taxon_rank=self.taxonRank,
            parent=self.taxon,
        )
        self.assertEqual(self.taxon2.parent, self.taxon)


    def test_delete_taxon(self):
        """Test delete taxon."""
        self.taxon.delete()
        self.assertEqual(Taxon.objects.count(), 0)
        """Test delete taxon rank."""
        self.taxonRank.delete()
        self.assertEqual(TaxonRank.objects.count(), 0)

    @mock.patch(
        'frontend.utils.statistical_model.'
        'clear_statistical_model_output_cache',
        mock.Mock(side_effect=mocked_clear_cache)
    )
    def test_taxon_admin_list(self):
        taxon2 = Taxon.objects.create(
            scientific_name='taxon_1',
            common_name_varbatim='taxon_1',
            colour_variant=False,
            taxon_rank=self.taxonRank
        )
        user = User.objects.create(
            username='admin123', is_superuser=True, is_staff=True,
            is_active=True)
        TOTPDevice.objects.create(
            user=user, name='Test Device', confirmed=True)
        client = Client()
        client.force_login(user)
        response = client.get(reverse('admin:species_taxon_changelist'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Colour')
        response = client.post(
            reverse('admin:species_taxon_changelist'),
            {
                'action': 'clean_output_caches',
                '_selected_action': [taxon2.id]
            },
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'cache has been cleared')


class OwnedSpeciesTestCase(TestCase):
    """Owned species test case."""
    @classmethod
    def setUpTestData(cls):
        """Set up test data for owned species test case."""
        user = User.objects.create_user(username='testuser', password='12345')
        taxon = Taxon.objects.create(
            scientific_name='taxon_0',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=TaxonRankFactory(),
        )
        cls.ownedSpecies = OwnedSpeciesFactory(taxon=taxon, user=user)

    def test_create_owned_species(self):
        """Test create owned species."""
        self.assertTrue(isinstance(self.ownedSpecies, OwnedSpecies))
        self.assertEqual(OwnedSpecies.objects.count(), 1)

    def test_update_owned_species(self):
        """Test update owned species."""
        self.ownedSpecies.area_available_to_species = 45.67
        self.ownedSpecies.save()
        self.assertEqual(
            OwnedSpecies.objects.get(
            id=self.ownedSpecies.id).area_available_to_species,
            45.67
        )

    def test_delete_owned_species(self):
        """Test delete owned species."""
        self.ownedSpecies.delete()
        self.assertEqual(OwnedSpecies.objects.count(), 0)


class TaxonSurveyMethodTestCase(TestCase):
    """Taxon survey method count test case."""
    @classmethod
    def setUpTestData(cls):
        """SetUpTestData for Taxon survey method count test case."""
        cls.taxon = Taxon.objects.create(
            scientific_name='taxon_0',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=TaxonRankFactory(),
        )
        cls.survey_method = SurveyMethod.objects.create(
            name='Unknown',
        )
        cls.taxon_survey_method = TaxonSurveyMethodF(
            taxon=cls.taxon,
            survey_method=cls.survey_method
        )

    def test_create_taxon_survey_method(self):
        """Test create Taxon survey method count."""
        self.assertTrue(
            isinstance(self.taxon_survey_method, TaxonSurveyMethod)
        )
        self.assertEqual(TaxonSurveyMethod.objects.count(), 1)
        self.assertEqual(
            TaxonSurveyMethod.objects.filter(
            taxon__scientific_name=self.taxon.scientific_name
            ).count(), 1
        )
        self.assertEqual(
            TaxonSurveyMethod.objects.filter(
            survey_method__name=self.survey_method.name
            ).count(), 1
        )

    def test_update_taxon_survey_method(self):
        """Test update Taxon survey method count."""
        taxon = TaxonFactory.create(
            scientific_name='taxon',
            common_name_varbatim='taxon_0',
            colour_variant=False,
            taxon_rank=TaxonRankFactory(),
        )
        self.taxon_survey_method.taxon = taxon
        self.taxon_survey_method.save()
        self.assertEqual(
            TaxonSurveyMethod.objects.filter(
            taxon__scientific_name='taxon').count(),
            1
        )


    def test_delete_taxon_survey_method(self):
        """Test delete Taxon survey method count."""
        self.taxon.delete()
        self.assertEqual(TaxonSurveyMethod.objects.count(), 0)
