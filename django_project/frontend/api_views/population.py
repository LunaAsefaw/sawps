"""API Views related to uploading population data.
"""
from datetime import datetime

from activity.models import ActivityType
from activity.serializers import ActivityTypeSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404
from frontend.models.upload import DraftSpeciesUpload
from frontend.utils.statistical_model import (
    clear_statistical_model_output_cache
)
from occurrence.models import SurveyMethod
from occurrence.serializers import (
    SurveyMethodSerializer,
)
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    SamplingEffortCoverage,
    PopulationStatus,
    PopulationEstimateCategory,
)
from population_data.serializers import (
    SamplingEffortCoverageSerializer,
    PopulationStatusSerializer,
    PopulationEstimateCategorySerializer,
)
from property.models import Property
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from species.models import Taxon
from species.serializers import TaxonSerializer
from stakeholder.models import OrganisationUser


class PopulationMetadataList(APIView):
    """Get metadata for uploading population."""

    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        # filter only taxon with rank species
        taxons = Taxon.objects.filter(
            taxon_rank__name__iexact="species"
        ).order_by('scientific_name')
        survey_methods = SurveyMethod.objects.all().order_by("name")
        intake_events = ActivityType.objects.filter(
            recruitment=True).order_by("name")
        offtake_events = ActivityType.objects.filter(
            Q(recruitment=False) | Q(recruitment__isnull=True)
        ).order_by("name")
        sampling_effort_coverages = (
            SamplingEffortCoverage.objects.all().order_by("name")
        )
        population_statuses = PopulationStatus.objects.all().order_by("name")
        population_estimate_categories = (
            PopulationEstimateCategory.objects.all().order_by("name")
        )
        return Response(
            status=200,
            data={
                "taxons": TaxonSerializer(taxons, many=True).data,
                "survey_methods": (
                    SurveyMethodSerializer(survey_methods, many=True).data
                ),
                "intake_events": (
                    ActivityTypeSerializer(intake_events, many=True).data
                ),
                "offtake_events": (
                    ActivityTypeSerializer(offtake_events, many=True).data
                ),
                "sampling_effort_coverages": (
                    SamplingEffortCoverageSerializer(
                        sampling_effort_coverages, many=True
                    ).data
                ),
                "population_statuses": (
                    PopulationStatusSerializer(
                        population_statuses, many=True
                    ).data
                ),
                "population_estimate_categories": (
                    PopulationEstimateCategorySerializer(
                        population_estimate_categories, many=True
                    ).data
                )
            },
        )


class UploadPopulationAPIVIew(APIView):
    """Save new upload of population data."""

    permission_classes = [IsAuthenticated]

    def can_add_data(self, property: Property):
        # check if user belongs to organisation of property
        if self.request.user.is_superuser:
            return True
        return OrganisationUser.objects.filter(
            organisation=property.organisation, user=self.request.user
        ).exists()

    def check_existing_data(self, property: Property, taxon: Taxon, year):
        # check if no data exist for taxon+property+year
        return AnnualPopulation.objects.filter(
            year=year, property=property,
            taxon=taxon
        ).exists()

    def post(self, request, *args, **kwargs):
        taxon_id = request.data.get("taxon_id")
        property_id = kwargs.get("property_id")
        year = request.data.get("year")
        property = get_object_or_404(Property, id=property_id)
        taxon = get_object_or_404(Taxon, id=taxon_id)
        # validate can add data
        if not self.can_add_data(property):
            return Response(
                status=403,
                data={
                    "detail": (
                        "You cannot add data to property that "
                        "does not belong to your organisations!"
                    )
                },
            )
        if self.check_existing_data(property, taxon, year):
            return Response(
                status=400,
                data={
                    "detail": (
                        "There is already existing data "
                        f"for {taxon.scientific_name} in year {year}!"
                    )
                },
            )
        annual_population = request.data.get("annual_population")
        intake_populations = request.data.get("intake_populations")
        offtake_populations = request.data.get("offtake_populations")
        # get survey_method
        survey_method = get_object_or_404(
            SurveyMethod, id=annual_population.get("survey_method_id", 0)
        )
        # area_available_to_species
        area_available_to_species = annual_population.get(
            "area_available_to_species", 0
        )
        sampling_effort_coverage = None
        sampling_effort_coverage_id = annual_population.get(
            "sampling_effort_coverage_id", None)
        if sampling_effort_coverage_id:
            sampling_effort_coverage = get_object_or_404(
                SamplingEffortCoverage, id=sampling_effort_coverage_id
            )
        population_status = None
        population_status_id = annual_population.get(
            "population_status_id", None)
        if population_status_id:
            population_status = get_object_or_404(
                PopulationStatus, id=population_status_id
            )
        population_estimate_category = None
        population_estimate_category_id = annual_population.get(
            "population_estimate_category_id", None)
        if population_estimate_category_id:
            population_estimate_category = get_object_or_404(
                PopulationEstimateCategory, id=population_estimate_category_id
            )
        annual_population_obj = AnnualPopulation.objects.create(
            year=year,
            taxon=taxon,
            property=property,
            user=self.request.user,
            area_available_to_species=area_available_to_species,
            total=annual_population.get("total"),
            adult_male=annual_population.get("adult_male", 0),
            adult_female=annual_population.get("adult_female", 0),
            juvenile_male=annual_population.get("juvenile_male", 0),
            juvenile_female=annual_population.get("juvenile_female", 0),
            group=annual_population.get("group", 0),
            note=annual_population.get("note", None),
            survey_method=survey_method,
            sub_adult_male=annual_population.get("sub_adult_male", 0),
            sub_adult_female=annual_population.get("sub_adult_female", 0),
            sub_adult_total=(annual_population.get("sub_adult_male", 0) +
                             annual_population.get("sub_adult_female", 0)
                             ),
            juvenile_total=(annual_population.get("juvenile_male", 0) +
                            annual_population.get("juvenile_female", 0)
                            ),
            population_estimate_certainty=annual_population.get(
                "population_estimate_certainty", None),
            upper_confidence_level=annual_population.get(
                "upper_confidence_level", None),
            lower_confidence_level=annual_population.get(
                "lower_confidence_level", None),
            certainty_of_bounds=annual_population.get(
                "certainty_of_bounds", None),
            population_estimate_category_other=annual_population.get(
                "population_estimate_category_other", None),
            survey_method_other=annual_population.get(
                "survey_method_other", None),
            population_status=population_status,
            population_estimate_category=population_estimate_category,
            sampling_effort_coverage=sampling_effort_coverage
        )
        # add annual population per activity - intake
        for intake_population in intake_populations:
            # get intake activity
            intake_activity = ActivityType.objects.filter(
                id=intake_population.get("activity_type_id", 0)
            ).first()
            if intake_activity is None:
                continue
            AnnualPopulationPerActivity.objects.create(
                year=year,
                annual_population=annual_population_obj,
                activity_type=intake_activity,
                total=intake_population.get("total"),
                adult_male=intake_population.get("adult_male", 0),
                adult_female=intake_population.get("adult_female", 0),
                juvenile_male=intake_population.get("juvenile_male", 0),
                juvenile_female=intake_population.get("juvenile_female", 0),
                founder_population=intake_population.get(
                    "founder_population", None),
                reintroduction_source=intake_population.get(
                    "reintroduction_source", None),
                intake_permit=intake_population.get("permit", None),
                note=intake_population.get("note", None),
            )
        # add annual population per activity - offtake
        for offtake_population in offtake_populations:
            # get offtake activity
            offtake_activity = ActivityType.objects.filter(
                id=offtake_population.get("activity_type_id", 0)
            ).first()
            if offtake_activity is None:
                continue
            AnnualPopulationPerActivity.objects.create(
                year=year,
                annual_population=annual_population_obj,
                activity_type=offtake_activity,
                total=offtake_population.get("total"),
                adult_male=offtake_population.get("adult_male", 0),
                adult_female=offtake_population.get("adult_female", 0),
                juvenile_male=offtake_population.get("juvenile_male", 0),
                juvenile_female=offtake_population.get("juvenile_female", 0),
                reintroduction_source=offtake_population.get(
                    "reintroduction_source", None),
                translocation_destination=offtake_population.get(
                    "translocation_destination", None),
                offtake_permit=offtake_population.get("permit", None),
                note=offtake_population.get("note", None),
            )
        # if draft exists, then delete it
        draft_uuid = request.GET.get("uuid", None)
        if draft_uuid:
            DraftSpeciesUpload.objects.filter(uuid=draft_uuid).delete()
        # clear caches of the species
        clear_statistical_model_output_cache(taxon)
        return Response(status=204)


class FetchDraftPopulationUpload(APIView):
    """API to fetch draft upload."""

    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        draft_uuid = kwargs.get("draft_uuid")
        draft_upload = get_object_or_404(DraftSpeciesUpload, uuid=draft_uuid)
        return Response(
            status=200,
            data={
                "last_step": draft_upload.last_step,
                "form_data": draft_upload.form_data,
            },
        )

    def delete(self, request, *args, **kwargs):
        draft_uuid = kwargs.get("draft_uuid")
        draft_upload = get_object_or_404(DraftSpeciesUpload, uuid=draft_uuid)
        draft_upload.delete()
        return Response(status=204)


class DraftPopulationUpload(APIView):
    """API to fetch draft list and save as draft."""

    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        property_id = kwargs.get("property_id")
        property = get_object_or_404(Property, id=property_id)
        drafts = (
            DraftSpeciesUpload.objects.filter(property=property)
            .order_by("-upload_date")
            .values_list("uuid", flat=True)
        )
        return Response(status=200, data=drafts)

    def post(self, request, *args, **kwargs):
        property_id = kwargs.get("property_id")
        property = get_object_or_404(Property, id=property_id)
        draft_uuid = request.GET.get("uuid", None)
        draft_time = datetime.now()
        draft_name = request.data.get("name", None)
        if draft_name is None:
            draft_name = f'{property.name}_{draft_time.strftime("%d_%m_%y")}'
        draft: DraftSpeciesUpload
        if draft_uuid:
            draft = get_object_or_404(DraftSpeciesUpload, uuid=draft_uuid)
        else:
            draft = DraftSpeciesUpload.objects.create(
                property=property,
                name=draft_name,
                upload_by=request.user,
                upload_date=draft_time,
            )
        draft.last_step = request.data.get("last_step")
        draft.form_data = request.data.get("form_data")
        taxon_id = draft.form_data.get("taxon_id", None)
        if taxon_id:
            draft.taxon = get_object_or_404(Taxon, id=taxon_id)
        draft.year = draft.form_data.get("year", None)
        draft.upload_date = draft_time
        draft.save()
        return Response(status=201, data={"uuid": str(draft.uuid)})
