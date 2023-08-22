from unittest import mock

from activity.models import ActivityType
from core.settings.utils import absolute_path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from frontend.models.upload import UploadSpeciesCSV
from frontend.tests.model_factories import UserF
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    CountMethod,
    OpenCloseSystem,
)
from property.factories import PropertyFactory
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from species.api_views.upload_species import SaveCsvSpecies, SpeciesUploader
from species.models import OwnedSpecies, Taxon
from species.tasks.upload_species import (
    string_to_boolean,
    string_to_number,
    upload_species_data,
)


class TestUploadSpeciesApiView(TestCase):
    """Test api view species uploader"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = UserF()
        self.property = PropertyFactory(
            name="Luna’s Reserve"
        )
        self.token = '8f1c1181-982a-4286-b2fe-da1abe8f7174'
        self.api_url = '/api/upload-species/'

    def test_upload_species_without_login(self):
        """Test upload species api"""

        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_session_incorrect(self):
        """Test upload species with incorrect header"""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'incorrect.csv')
        data = open(csv_path, 'rb')
        data = SimpleUploadedFile(
            content=data.read(),
            name=data.name,
            content_type='multipart/form-data'
        )

        request = self.factory.post(
            reverse('upload-species'), {
                'file': data,
                'token': self.token,
                'property': self.property.id
            }
        )
        request.user = self.user
        view = SpeciesUploader.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(UploadSpeciesCSV.objects.filter(token=self.token).count(),
                         1)
        upload_session = UploadSpeciesCSV.objects.get(token=self.token)
        self.assertTrue(upload_session.canceled)
        self.assertEqual(upload_session.process_file.name, '')
        self.assertEqual(upload_session.error_notes,
                         'Header row does not follow the correct format'
                         )

    def test_save_csv_with_no_property(self):
        """Test save csv with not existing property."""

        request = self.factory.post(
            reverse('save-csv-species'),
            data={
                'token': self.token,
                'property': 0
            }, format='json')

        request.user = self.user
        view = SaveCsvSpecies.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_upload_session(self):
        """Test upload species """

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'test.csv')
        data = open(csv_path, 'rb')
        data = SimpleUploadedFile(
            content=data.read(),
            name=data.name,
            content_type='multipart/form-data'
        )

        request = self.factory.post(
            reverse('upload-species'), {
                'file': data,
                'token': self.token,
                'property': self.property.id
            }
        )
        request.user = self.user
        view = SpeciesUploader.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(UploadSpeciesCSV.objects.filter(token=self.token).count(),
                         1)
        file_name = 'species'
        upload_session = UploadSpeciesCSV.objects.get(token=self.token)
        self.assertTrue(file_name in upload_session.process_file.path)
        self.assertEqual(upload_session.error_file.name, '')

        with mock.patch('species.api_views.upload_species.upload_species_data.delay') as mock_task:
            request = self.factory.post(
                reverse('save-csv-species'),
                data={
                    'token': self.token,
                    'property': self.property.id
                }, format='json')

            request.user = self.user
            view = SaveCsvSpecies.as_view()
            response = view(request)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(mock_task.called)

    @mock.patch("species.tasks.upload_species.upload_species_data")
    def test_upload_csv_task(self, mock_app):
        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'test.csv')
        data = open(csv_path, 'rb')
        data = SimpleUploadedFile(
            content=data.read(),
            name=data.name,
            content_type='multipart/form-data'
        )

        request = self.factory.post(
            reverse('upload-species'), {
                'file': data,
                'token': self.token,
                'property': self.property.id
            }
        )
        request.user = self.user
        view = SpeciesUploader.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 204)
        upload_session = UploadSpeciesCSV.objects.get(token=self.token)
        ActivityType.objects.create(
            name="Planned translocation")
        ActivityType.objects.create(
            name="Planned hunt/cull")
        ActivityType.objects.create(
            name="Planned euthanasia")
        ActivityType.objects.create(
            name="Unplanned/illegal hunting")
        Taxon.objects.create(
            scientific_name='Panthera leo',
            common_name_varbatim='Lion'
        )
        upload_species_data(upload_session.id)
        self.assertEqual(Taxon.objects.all().count(), 1)
        self.assertEqual(AnnualPopulationPerActivity.objects.all().count(), 5)
        self.assertEqual(AnnualPopulation.objects.all().count(), 1)
        self.assertTrue(OwnedSpecies.objects.all().count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Planned translocation"
        ).count(), 2)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Planned hunt/cull"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Planned euthanasia"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Unplanned/illegal hunting"
        ).count(), 1)
        self.assertTrue(OpenCloseSystem.objects.all().count() == 1)


    def test_task_string_to_boolean(self):
        """Test string_to_boolean functionality in task"""

        self.assertTrue(string_to_boolean('yes'))
        self.assertFalse(string_to_boolean(''))

    def test_task_string_to_number(self):
        """Test string_to_number functionality in task"""

        self.assertEqual(10, string_to_number('10'))
        self.assertEqual(0.0, string_to_number(''))