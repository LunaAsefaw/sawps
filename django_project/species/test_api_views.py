import csv
from unittest import mock
import pandas as pd
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
    OpenCloseSystem,
)
from property.factories import PropertyFactory
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from species.api_views.upload_species import (
    SaveCsvSpecies,
    SpeciesUploader,
    UploadSpeciesStatus,
)
from species.models import OwnedSpecies, Taxon
from species.tasks.upload_species import upload_species_data
from species.scripts.data_upload import (
    SpeciesCSVUpload,
    string_to_boolean,
    string_to_number
)
from species.scripts.upload_file_scripts import SHEET_TITLE


class TestUploadSpeciesApiView(TestCase):
    """Test api view species uploader"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = UserF()
        self.property = PropertyFactory(
            name="Luna"
        )
        self.token = '8f1c1181-982a-4286-b2fe-da1abe8f7174'
        self.api_url = '/api/upload-species/'
        ActivityType.objects.create(
            name="Unplanned/Illegal Hunting")
        ActivityType.objects.create(
            name="Planned Euthanasia/DCA")
        ActivityType.objects.create(
            name="Planned Hunt/Cull")
        ActivityType.objects.create(
            name="Translocation (Intake)")
        ActivityType.objects.create(
            name="Translocation (Offtake)")
        Taxon.objects.create(
            scientific_name='Panthera leo',
            common_name_varbatim='Lion'
        )

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
                         "The 'Property_name' field is missing. "
                         "Please check that all the compulsory fields "
                         "are in the CSV file headers."
                         )

    def test_upload_session_no_sheet(self):
        """Test upload species with no sheet in excel file."""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'excel_no_sheet.xlsx')
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
                         "The sheet named Dataset pilot is not in the Excel "
                         "file. Please download the template to get "
                         "the correct file."
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
        """Test upload csv task."""
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

        upload_species_data(upload_session.id)
        self.assertEqual(Taxon.objects.all().count(), 1)
        self.assertEqual(AnnualPopulationPerActivity.objects.all().count(), 5)
        self.assertEqual(AnnualPopulation.objects.all().count(), 1)
        self.assertTrue(OwnedSpecies.objects.all().count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Translocation (Offtake)"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Planned Hunt/Cull"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Translocation (Intake)"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Planned Euthanasia/DCA"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            activity_type__name="Unplanned/Illegal Hunting"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            translocation_destination="KNP", offtake_permit="ABC100X10"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            offtake_permit="DEF100X10"
        ).count(), 1)

        self.assertTrue(OpenCloseSystem.objects.all().count() == 1)

    def test_upload_species_status(self):
        """Test upload species status."""
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

        upload_session.progress = 'Processing'
        upload_session.save()
        file_upload = SpeciesCSVUpload()
        file_upload.upload_session = upload_session
        file_upload.start('utf-8-sig')

        kwargs = {
            'token': self.token
        }
        request = self.factory.get(
            reverse('upload-species-status', kwargs=kwargs)
        )
        request.user = self.user
        view = UploadSpeciesStatus.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'Finished')
        self.assertFalse(response.data['error_file'])

    def test_upload_species_status_404(self):
        """Test upload species status with 404 error."""
        kwargs = {
            'token': '8f1c1181-982a-4286-b2fe-da1abe8f7172'
        }
        request = self.factory.get(
            reverse('upload-species-status', kwargs=kwargs)
        )
        request.user = self.user
        view = UploadSpeciesStatus.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 404)

    def test_upload_species_status_not_processed(self):
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
        kwargs = {
            'token': self.token
        }
        request = self.factory.get(
            reverse('upload-species-status', kwargs=kwargs)
        )
        request.user = self.user
        view = UploadSpeciesStatus.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], False)


    def test_task_string_to_boolean(self):
        """Test string_to_boolean functionality in task"""

        self.assertTrue(string_to_boolean('yes'))
        self.assertFalse(string_to_boolean(''))

    def test_task_string_to_number(self):
        """Test string_to_number functionality in task"""

        self.assertEqual(10, string_to_number('10'))
        self.assertEqual(0.0, string_to_number(''))

    def test_upload_species_with_property_taxon_not_exit(self):
        """Test upload species task with a property and taxon not existing."""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'test_property_taxon.csv')
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
        upload_session.progress = 'Processing'
        upload_session.save()
        file_upload = SpeciesCSVUpload()
        file_upload.upload_session = upload_session
        file_upload.start('utf-8-sig')

        kwargs = {
            'token': self.token
        }
        request = self.factory.get(
            reverse('upload-species-status', kwargs=kwargs)
        )
        request.user = self.user
        view = UploadSpeciesStatus.as_view()
        response = view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('media' in response.data['error_file'])

        self.assertTrue('error' in upload_session.error_file.path)
        with open(upload_session.error_file.path, encoding='utf-8-sig') as csv_file:
            error_file = csv.DictReader(csv_file)
            headers = error_file.fieldnames
            self.assertTrue('error_message' in headers)
            errors = []
            for row in error_file:
                errors.append(row['error_message'])
            self.assertTrue("Property name Luna's Reserve doesn't match "
                            "the selected property. Please replace "
                            "it with Luna." in errors)
            self.assertTrue("Lemurs doesn't exist in the database. "
                            "Please select species available in the "
                            "dropdown only." in errors)
            self.assertTrue("The value of field "
                            "If_other_(population_estimate_category)_please "
                            "explain is empty." in errors)
            self.assertTrue("The value of field "
                            "If_other_(survey_method)_please "
                            "explain is empty." in errors)
            self.assertTrue("The value of the compulsory field "
                            "Population_estimate_category is empty." in errors)
            self.assertTrue("The value of the compulsory field "
                            "presence/absence is empty. The value "
                            "of the compulsory field "
                            "Population_estimate_category is empty." in errors)
            self.assertTrue("The total of Count_adult_males and "
                            "Count_adult_females must not exceed "
                            "COUNT_TOTAL." in errors)
            self.assertTrue("The total of "
                            "Planned hunt/culling_Offtake_adult_males and "
                            "Planned hunt/culling_Offtake_adult_females must "
                            "not exceed Planned hunt/culling_TOTAL." in errors)

        self.assertTrue(AnnualPopulation.objects.filter(
            survey_method_other="Test survey"
        ).count(), 1)
        self.assertTrue(AnnualPopulation.objects.filter(
            survey_method__name="Other - please explain",
            survey_method_other="Test survey"
        ).count(), 1)
        self.assertTrue(AnnualPopulation.objects.filter(
            population_estimate_category__name="Other (please describe how the "
                                               "population size estimate was "
                                               "determined)",
            population_estimate_category_other="Decennial census"
        ).count(), 1)
        self.assertTrue(AnnualPopulation.objects.filter(
            population_estimate_category__name="Ad hoc or "
                                               "opportunistic monitoring"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            intake_permit="12345"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            reintroduction_source="KNP"
        ).count(), 1)
        self.assertTrue(AnnualPopulationPerActivity.objects.filter(
            founder_population=True
        ).count(), 1)

    def test_upload_excel_missing_compulsory_field(self):
        """Test upload species with an excel file which misses
         a compulsory field."""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'excel_wrong_header.xlsx')
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
                         "The 'Property_name' field is missing. Please check "
                         "that all the compulsory fields are in the "
                         "CSV file headers."
                         )

    def test_upload_species_with_excel_property_not_exit(self):
        """Test upload Excel file with a property not existing."""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'excel_error_property.xlsx')
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
        upload_session.progress = 'Processing'
        upload_session.save()
        file_upload = SpeciesCSVUpload()
        file_upload.upload_session = upload_session
        file_upload.start('utf-8-sig')
        self.assertTrue('error' in upload_session.error_file.path)

        xl = pd.ExcelFile(upload_session.error_file.path)
        dataset = xl.parse(SHEET_TITLE)
        self.assertEqual(
            dataset.iloc[0]['error_message'],
            "Property name Venetia Limpopo doesn't match the selected "
            "property. Please replace it with {}. Loxodonta africana "
            "doesn't exist in the database. Please select species "
            "available in the dropdown only.".format(
                upload_session.property.name
            )
        )

    @mock.patch("species.tasks.upload_species.upload_species_data")
    def test_upload_task_with_upload_session_not_existing(self, mock_app):
        """Test upload task with upload session not existing."""

        self.assertEqual(upload_species_data(1), None)

    def test_uploader_view_without_file(self):
        """Test uploader file view with no file"""

        request = self.factory.post(
            reverse('upload-species'), {
                'token': self.token,
                'property': self.property.id
            }
        )
        request.user = self.user
        view = SpeciesUploader.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'File not found')

    def test_uploader_view_with_empty_compulsory_fields(self):
        """Test uploader file view with an empty value in
        compulsory field."""

        csv_path = absolute_path(
            'frontend', 'tests',
            'csv', 'test_empty_value_of_compulsory_fields.csv')
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
        upload_session.progress = 'Processing'
        upload_session.save()
        file_upload = SpeciesCSVUpload()
        file_upload.upload_session = upload_session
        file_upload.start('utf-8-sig')
        self.assertTrue('error' in upload_session.error_file.path)



