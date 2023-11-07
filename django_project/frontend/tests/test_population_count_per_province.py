from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from frontend.tests.model_factories import UserF
from django.test import Client, TestCase
from frontend.utils.data_table import get_taxon_queryset, common_filters
from frontend.utils.metrics import (
    calculate_species_count_per_province
)
from django.shortcuts import reverse
from frontend.utils.user_roles import get_user_roles
from population_data.factories import AnnualPopulationF
from property.factories import PropertyFactory
from property.models import Property, Province
from regulatory_permit.models import DataUsePermission
from species.factories import (
    TaxonRankFactory
)
import base64
from species.models import Taxon, TaxonRank
from stakeholder.models import Organisation
import base64
import csv
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from frontend.static_mapping import (
    NATIONAL_DATA_SCIENTIST,
    REGIONAL_DATA_SCIENTIST,
    REGIONAL_DATA_CONSUMER
)
from population_data.models import AnnualPopulation, AnnualPopulationPerActivity
from population_data.factories import (
    AnnualPopulationF,
    AnnualPopulationPerActivityFactory
)
from property.factories import PropertyFactory
from rest_framework import status

from activity.models import ActivityType
from sawps.tests.models.account_factory import GroupF
from species.factories import (
    TaxonFactory,
    TaxonRankFactory
)
from species.models import TaxonRank
from stakeholder.factories import (
    organisationFactory,
    organisationUserFactory,
    userRoleTypeFactory,
)
from property.factories import ProvinceFactory
from frontend.tests.model_factories import (
    SpatialDataModelF,
    SpatialDataModelValueF
)
from stakeholder.models import OrganisationInvites, MANAGER


class SpeciesCountPerProvinceTest(APITestCase):
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
            scientific_name="Penthera leo"
        )

        self.user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd',
            is_superuser=True
        )
        self.auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' +
                                  base64.b64encode(b'testuserd:testpasswordd').decode('ascii'),
        }
        self.client = Client()
        session = self.client.session
        session.save()

        # add user 1 to organisation 1 and 3
        organisationUserFactory.create(
            user=self.user,
            organisation=self.organisation
        )
        group = GroupF.create(name=NATIONAL_DATA_SCIENTIST)
        self.user.groups.add(group)
        self.user.user_profile.current_organisation = self.organisation
        self.user.save()

        self.province1 = Province.objects.create(name="Province1")
        self.province2 = Province.objects.create(name="Province2")

        # Create test data, including properties and owned species
        self.property1 = PropertyFactory.create(name="Property 1", province=self.province1, organisation=self.organisation)
        self.property2 = PropertyFactory.create(name="Property 2", province=self.province2, organisation=self.organisation)

        AnnualPopulationF.create(
            year=2023,
            property=self.property2,
            user=self.user,
            taxon=self.taxon,
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
            year=2023,
            property=self.property1,
            user=self.user,
            taxon=self.taxon,
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
            property=self.property1,
            user=self.user,
            taxon=self.taxon,
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
            year=1960,
            property=self.property1,
            user=self.user,
            taxon=self.taxon,
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

        self.url = reverse('species_count_per_province')

    def test_calculate_species_count_per_province(self):
        data = {
            'species': "Penthera leo"
        }
        # self.client.force_login(self.user)
        response = self.client.get(self.url, data, **self.auth_headers)
        result_data = response.json()

        # Perform assertions based on the expected results
        # We have two provinces with 3 years of data
        # For 2023, there are data for Province1 and Province2
        self.assertEqual(
            result_data,
            [
                {"year": 2023, "count": 60, "province": "Province1", "species": "Penthera leo"},
                {"year": 2023, "count": 60, "province": "Province2", "species": "Penthera leo"},
                {"year": 2022, "count": 20, "province": "Province1", "species": "Penthera leo"},
                {"year": 1960, "count": 30, "province": "Province1", "species": "Penthera leo"},
            ]
        )

    def test_calculate_species_count_per_province_year_filter(self):
        data = {
            'species': "Penthera leo",
            'start_year': 2022,
            'end_year': 2022
        }
        # self.client.force_login(self.user)
        response = self.client.get(self.url, data, **self.auth_headers)
        result_data = response.json()

        # Perform assertions based on the expected results
        self.assertEqual(len(result_data), 1)  # We have two provinces with 3 years of data

        self.assertEqual(
            result_data,
            [{"year": 2022, "count": 20, "province": "Province1", "species": "Penthera leo"}],
        )
