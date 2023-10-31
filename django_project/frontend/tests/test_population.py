from django.test import TestCase
from django.urls import reverse
import mock
from frontend.tests.model_factories import UserF
from stakeholder.models import (
    OrganisationUser
)
from stakeholder.factories import (
    organisationFactory
)
from frontend.tests.request_factories import OrganisationAPIRequestFactory
from frontend.api_views.population import (
    PopulationMetadataList,
    UploadPopulationAPIVIew,
    FetchDraftPopulationUpload,
    DraftPopulationUpload
)
from property.factories import (
    PropertyFactory
)
from species.factories import TaxonF

from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    PopulationStatus,
    PopulationEstimateCategory,
    SamplingEffortCoverage
)
from population_data.factories import (
    CertaintyF
)


def mocked_clear_cache(self, *args, **kwargs):
    return 1


class TestPopulationAPIViews(TestCase):
    fixtures = [
        'open_close_systems.json',
        'survey_methods.json',
        'sampling_size_units.json',
        'activity_type.json'
    ]

    def setUp(self) -> None:
        # insert organisation
        self.organisation = organisationFactory.create()
        self.factory = OrganisationAPIRequestFactory(self.organisation)
        self.user_1 = UserF.create(username='test_1')
        OrganisationUser.objects.create(
            user=self.user_1,
            organisation=self.organisation
        )
        self.population_status = PopulationStatus.objects.create(
            name='Status 1'
        )
        self.estimate = PopulationEstimateCategory.objects.create(
            name='Estimate 1'
        )
        self.coverage = SamplingEffortCoverage.objects.create(
            name='Coverage 1'
        )
        self.certainty = CertaintyF.create(
            description='Certainty1',
            name='1'
        )

    def test_get_metadata_list(self):
        request = self.factory.get(
            reverse('population-metadata')
        )
        request.user = self.user_1
        view = PopulationMetadataList.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.data.keys()),
            [
                'taxons',
                'survey_methods',
                'intake_events',
                'offtake_events',
                'sampling_effort_coverages',
                'population_statuses',
                'population_estimate_categories'
            ]
        )

    @mock.patch(
        'frontend.api_views.population.'
        'clear_statistical_model_output_cache',
        mock.Mock(side_effect=mocked_clear_cache)
    )
    def test_upload_population_data(self):
        property = PropertyFactory.create(
            organisation=self.organisation
        )
        taxon = TaxonF.create()
        data = {
            'taxon_id': taxon.id,
            'year': 2023,
            'property_id': property.id,
            'month': 7,
            'annual_population': {
                'present': True,
                'total': 20,
                'adult_male': 5,
                'adult_female': 7,
                'sub_adult_male': 8,
                'group': 1,
                'open_close_id': 1,
                'area_available_to_species': 5.5,
                'survey_method_id': 1,
                'area_covered': 1.2,
                'note': 'This is notes',
                'sampling_effort_coverage_id': self.coverage.id,
                'population_status_id': self.population_status.id,
                'population_estimate_category_id': self.estimate.id
            },
            'intake_populations': [{
                'activity_type_id': 1,
                'total': 12,
                'adult_male': 5,
                'adult_female': 7,
                'founder_population': True,
                'reintroduction_source': 'Source A',
                'permit': 900,
                'note': 'This is intake notes'
            },
            {
                'activity_type_id': 100,
                'total': 12,
                'adult_male': 5,
                'adult_female': 7,
                'founder_population': True,
                'reintroduction_source': 'Source A',
                'permit': 900,
                'note': 'This is intake notes'
            }],
            'offtake_populations': [{
                'activity_type_id': 2,
                'total': 6,
                'adult_male': 4,
                'adult_female': 2,
                'translocation_destination': 'Dest A',
                'permit': 900,
                'note': 'This is invalid notes'
            },
            {
                'activity_type_id': 100,
                'total': 6,
                'adult_male': 4,
                'adult_female': 2,
                'translocation_destination': 'Dest A',
                'permit': 900,
                'note': 'This is invalid notes'
            },
            {
                'activity_type_id': 3,
                'total': 6,
                'adult_male': 4,
                'adult_female': 2,
                'reintroduction_source': 'Source A',
                'permit': 900,
                'note': 'This is invalid notes'
            }]
        }
        kwargs = {
            'property_id': property.id
        }
        request = self.factory.post(
            reverse('population-upload', kwargs=kwargs),
            data=data, format='json'
        )
        request.user = self.user_1
        view = UploadPopulationAPIVIew.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 204)
        # assert annual population data
        annual_population = AnnualPopulation.objects.filter(
            taxon=taxon,
            property=property,
            year=2023
        ).first()
        self.assertTrue(annual_population)
        self.assertEqual(annual_population.area_available_to_species, 5.5)
        # assert annual population per activity - intake
        annual_intake = AnnualPopulationPerActivity.objects.filter(
            annual_population=annual_population,
            year=2023,
            activity_type_id=1
        ).first()
        self.assertTrue(annual_intake)
        # assert annual population per activity - offtake
        annual_offtake = AnnualPopulationPerActivity.objects.filter(
            annual_population=annual_population,
            year=2023,
            activity_type_id=2
        ).first()
        self.assertTrue(annual_offtake)

    def test_save_draft(self):
        # save draft
        property = PropertyFactory.create(
            organisation=self.organisation
        )
        taxon = TaxonF.create()
        form_data = {
            'taxon_id': taxon.id,
            'year': 2023,
            'property_id': property.id,
            'month': 7,
            'annual_population': {
                'present': True,
                'total': 20,
                'adult_male': 5,
                'adult_female': 7,
                'sub_adult_male': 8,
                'group': 1,
                'open_close_id': 1,
                'area_available_to_species': 5.5,
                'survey_method_id': 1,
                'area_covered': 1.2,
                'note': 'This is notes'
            },
            'intake_populations': [{
                'activity_type_id': 1,
                'total': 12,
                'adult_male': 5,
                'adult_female': 7,
                'founder_population': True,
                'reintroduction_source': 'Source A',
                'permit': 900,
                'note': 'This is intake notes'
            }],
            'offtake_populations': [{
                'activity_type_id': 2,
                'total': 6,
                'adult_male': 4,
                'adult_female': 2,
                'translocation_destination': 'Dest A',
                'permit': 900,
                'note': 'This is intake notes'
            }]
        }
        kwargs = {
            'property_id': property.id
        }
        request = self.factory.post(
            reverse('draft-upload-species', kwargs=kwargs),
            data={
                'name': 'save draft test',
                'last_step': 1,
                'form_data': form_data
            },
            format='json'
        )
        request.user = self.user_1
        view = DraftPopulationUpload.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.data)
        draft_uuid = response.data['uuid']
        # fetch draft
        kwargs = {
            'draft_uuid': draft_uuid
        }
        request = self.factory.get(
            reverse('fetch-draft-upload-species', kwargs=kwargs)
        )
        request.user = self.user_1
        view = FetchDraftPopulationUpload.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        # fetch list of draft
        kwargs = {
            'property_id': property.id
        }
        request = self.factory.get(
            reverse('draft-upload-species', kwargs=kwargs)
        )
        request.user = self.user_1
        view = DraftPopulationUpload.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        # delete draft
        kwargs = {
            'draft_uuid': draft_uuid
        }
        request = self.factory.delete(
            reverse('fetch-draft-upload-species', kwargs=kwargs)
        )
        request.user = self.user_1
        view = FetchDraftPopulationUpload.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 204)
