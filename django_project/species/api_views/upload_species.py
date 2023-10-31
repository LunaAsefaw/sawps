import codecs
import csv
import logging
import pandas as pd
from datetime import datetime

from django.utils.datastructures import MultiValueDictKeyError
from frontend.models import UploadSpeciesCSV
from property.models import Property
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from species.scripts.upload_file_scripts import COMPULSORY_FIELDS, SHEET_TITLE
from species.tasks.upload_species import upload_species_data
from core.settings.base import MEDIA_URL

logger = logging.getLogger('sawps')


class SpeciesUploader(APIView):
    """API to upload csv file."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def check_header(self, headers):
        for header in COMPULSORY_FIELDS:
            if header not in headers:
                error_message = "The '{}' field is missing. Please check " \
                                "that all the compulsory fields are in the " \
                                "CSV file headers.".format(header)
                return error_message
        return

    def post(self, request, *args, **kwargs):
        try:
            species_file = request.FILES['file']

        except MultiValueDictKeyError:
            return Response(
                status=400,
                data={
                    'detail': 'File not found'
                }
            )

        upload_session = UploadSpeciesCSV.objects.create(
            uploader=self.request.user,
            uploaded_at=datetime.now(),
            token=request.POST['token'],
            property=Property.objects.get(id=request.POST['property'])
        )

        if species_file.name.endswith('.xlsx'):
            xl = pd.ExcelFile(species_file)
            try:
                dataset = xl.parse(SHEET_TITLE)
                headers = dataset.columns.ravel()
            except ValueError:
                error = "The sheet named {} is not in the Excel " \
                        "file. Please download the template to get " \
                        "the correct file.".format(SHEET_TITLE)
            else:
                error = self.check_header(headers)

        else:
            reader = csv.DictReader(codecs.iterdecode(species_file, 'utf-8'))
            headers = reader.fieldnames
            error = self.check_header(headers)

        if error:
            upload_session.error_notes = error
            upload_session.error_file = species_file
            upload_session.canceled = True
            upload_session.save()
            return Response(
                status=400,
                data={'detail': error}
            )

        upload_session.process_file = species_file
        upload_session.save()
        return Response(status=204)


class SaveCsvSpecies(APIView):
    """API to save csv file into the database."""
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            upload_session = UploadSpeciesCSV.objects.get(
                property=request.data.get('property'),
                uploader=self.request.user,
                token=request.data.get('token')
            )
        except UploadSpeciesCSV.DoesNotExist:
            return Response(
                status=400,
                data={
                    'detail': 'There is something wrong please try again.'
                }
            )

        task = upload_species_data.delay(
            upload_session.id
        )

        if task:
            return Response(
                status=200
            )

        return Response(
            status=404,
            data={
                'detail': 'Somthing wrong with the csv file'
            }
        )


class UploadSpeciesStatus(APIView):
    """Check upload species status."""
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        token = kwargs.get('token')
        try:
            upload_species = UploadSpeciesCSV.objects.get(
                token=token
            )
        except UploadSpeciesCSV.DoesNotExist:
            return Response(status=404)

        success = True
        error_file = None
        message = upload_species.success_notes
        if upload_species.error_file:
            error_file = '{}{}'.format(
                        MEDIA_URL, upload_species.error_file.name)
            success = False

        if not upload_species.success_notes and not upload_species.error_file:
            message = (
                "There is something wrong with the "
                "data please check again." if
                not upload_species.error_notes else upload_species.error_notes
            )
            success = False

        if not upload_species.success_notes and upload_species.error_file:
            message = "There is an error, please check the error file."

        if upload_species.processed:

            return Response(
                status=200,
                data={
                    'status': upload_species.progress if success else 'Error',
                    'error_file': error_file,
                    'message': message
                }
            )

        else:
            return Response(
                status=200,
                data={
                    'status': upload_species.canceled,
                    'error_file': error_file,
                    'message': message
                }
            )
