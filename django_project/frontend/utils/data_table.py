import urllib.parse
from typing import Dict, List

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest

from activity.models import ActivityType
from frontend.serializers.report import (
    SpeciesReportSerializer,
    SamplingReportSerializer,
    PropertyReportSerializer,
    ActivityReportSerializer,
    NationalLevelSpeciesReport,
    NationalLevelPropertyReport,
    NationalLevelActivityReport,
    NationalLevelProvinceReport
)
from frontend.static_mapping import REGIONAL_DATA_CONSUMER
from frontend.utils.organisation import get_current_organisation_id
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity
)
from property.models import Province, Property
from species.models import OwnedSpecies

ACTIVITY_REPORT = 'Activity_report'
PROPERTY_REPORT = 'Property_report'
SAMPLING_REPORT = 'Sampling_report'
SPECIES_REPORT = 'Species_report'
PROVINCE_REPORT = 'Province_report'


def data_table_reports(queryset: QuerySet, request, user_roles) -> List[Dict]:
    """
    Generate data table reports based on the user's request.
    Params:
        queryset (QuerySet): The initial queryset to generate reports from.
        request: The HTTP request object.
    """
    reports_list = request.GET.get("reports", None)
    reports = []

    if reports_list:
        reports_list = reports_list.split(",")
        report_functions = {
            ACTIVITY_REPORT: activity_report,
            PROPERTY_REPORT: property_report,
            SAMPLING_REPORT: sampling_report,
            SPECIES_REPORT: species_report,
        }

        for report_name in reports_list:
            if report_name in report_functions:
                report_data = report_functions[report_name](queryset, request)
                reports.append(
                    {report_name: report_data}
                ) if report_data else []

    return reports


def get_report_filter(request, report_type):
    default_species_field = 'owned_species__taxon__scientific_name__in'
    filters = {}
    species_fields = {
        SPECIES_REPORT: default_species_field,
        PROPERTY_REPORT: 'taxon__scientific_name__in',
        SAMPLING_REPORT: default_species_field,
        ACTIVITY_REPORT: default_species_field
    }

    default_year_field = 'year__range'
    year_fields = {
        SPECIES_REPORT: default_year_field,
        PROPERTY_REPORT: 'annualpopulation__year__range',
        SAMPLING_REPORT: default_year_field,
        ACTIVITY_REPORT: default_year_field
    }

    species_list = request.GET.get("species")
    if species_list:
        species_list = species_list.split(",")
        filters[species_fields[report_type]] = species_list

    start_year = request.GET.get("start_year")
    if start_year and report_type != PROPERTY_REPORT:
        start_year = int(start_year)
        end_year = int(request.GET.get("end_year"))
        filters[year_fields[report_type]] = (start_year, end_year)

    default_activity_field = (
        'owned_species__annualpopulationperactivity__'
        'activity_type_id__in'
    )
    activity_fields = {
        SPECIES_REPORT: default_activity_field,
        PROPERTY_REPORT: (
            'annualpopulationperactivity__activity_type_id__in'
        ),
        SAMPLING_REPORT: default_activity_field,
        ACTIVITY_REPORT: default_activity_field,
    }

    activity = request.GET.get("activity", "")
    activity = urllib.parse.unquote(activity)
    if activity != 'all':
        filters[activity_fields[report_type]] = [
            int(act) for act in activity.split(',')
        ] if activity else []
    elif report_type == ACTIVITY_REPORT:
        filters[
            activity_fields[report_type]
        ] = ActivityType.objects.values_list('id', flat=True)
    return filters


def species_report(queryset: QuerySet, request) -> List:
    """
    Generate species reports based on the user's request.
    Params:
        queryset (QuerySet): Properties queryset to generate reports from.
        request: The HTTP request object.
    """
    filters = get_report_filter(request, SPECIES_REPORT)
    species_population_data = AnnualPopulation.objects.filter(
        owned_species__property_id__in=queryset.values_list('id', flat=True),
        **filters
    ).distinct()
    species_reports = SpeciesReportSerializer(
        species_population_data,
        many=True
    ).data
    return species_reports


def property_report(queryset: QuerySet, request) -> List:
    """
    Generate property reports based on the user's request.
    Params:
        queryset (QuerySet): Properties queryset to generate reports from.
        request: The HTTP request object.
    """
    filters = get_report_filter(request, PROPERTY_REPORT)
    area_available_values = OwnedSpecies.objects.filter(
        property__in=queryset,
        **filters
    )

    property_reports = PropertyReportSerializer(
        area_available_values, many=True
    ).data

    return property_reports


def sampling_report(queryset: QuerySet, request) -> List:
    """
    Generate sampling reports based on the user's request.
    Params:
        queryset (QuerySet): Properties queryset to generate reports from.
        request: The HTTP request object.
    """
    filters = get_report_filter(request, SAMPLING_REPORT)

    sampling_reports_data = AnnualPopulation.objects.filter(
        owned_species__property__id__in=queryset.values_list('id', flat=True),
        **filters
    )
    sampling_reports = SamplingReportSerializer(
        sampling_reports_data,
        many=True
    ).data

    return sampling_reports


def activity_report(queryset: QuerySet, request) -> Dict[str, List[Dict]]:
    """
    Generate property reports based on the user's request.
    Params:
        queryset (QuerySet): Properties queryset to generate reports from.
        request: The HTTP request object.
    """
    filters = get_report_filter(request, ACTIVITY_REPORT)
    activity_field = (
        'owned_species__annualpopulationperactivity__'
        'activity_type_id__in'
    )
    activity_type_ids = filters[activity_field]
    del filters[activity_field]

    activity_reports = {}
    valid_activities = ActivityType.objects.filter(id__in=activity_type_ids)
    for activity in valid_activities:
        activity_data = AnnualPopulationPerActivity.objects.filter(
            owned_species__property__in=queryset,
            activity_type=activity,
            **filters
        )
        serializer = ActivityReportSerializer(
            activity_data,
            many=True,
            activity=activity
        )
        activity_reports[activity.name] = serializer.data

    activity_reports = {k: v for k, v in activity_reports.items() if v}

    return activity_reports


def national_level_user_table(
        queryset: QuerySet, request: HttpRequest, user_roles: List[str]
) -> List[Dict]:
    """
    Generate national-level reports for a user based on their role.

    Params:
        queryset : The initial queryset for data retrieval.
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.
    """
    reports_list = request.GET.get("reports")
    reports = []
    if reports_list:
        reports_list = reports_list.split(",")
        report_functions = {
            PROPERTY_REPORT: national_level_property_report,
            ACTIVITY_REPORT: national_level_activity_report,
            SPECIES_REPORT: national_level_species_report,
        }

        if REGIONAL_DATA_CONSUMER not in user_roles:
            report_functions[
                PROVINCE_REPORT
            ] = national_level_province_report

        for report_name in reports_list:
            if report_name in report_functions:
                report_data = report_functions[
                    report_name
                ](queryset, request, user_roles)
                if report_data:
                    reports.append({report_name: report_data})

    else:
        data = national_level_property_report(queryset, request, user_roles)
        if data:
            reports.append({PROPERTY_REPORT: data})

    return reports


def common_filters(request: HttpRequest, user_roles: List[str]) -> Dict:
    """
    Generate common filters for data retrieval based on
    the user's role and request parameters.

    Params:
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.
    """
    filters = {}
    properties = Property.objects.all()

    start_year = request.GET.get("start_year")
    if start_year:
        end_year = request.GET.get("end_year")
        filters["annualpopulation__year__range"] = (
            start_year, end_year
        )

    property_param = request.GET.get("property")
    if property_param:
        properties = properties.filter(
            id__in=property_param.split(',')
        )

    spatial_filter_values = request.GET.get(
        'spatial_filter_values',
        ''
    ).split(',')

    spatial_filter_values = list(
        filter(None, spatial_filter_values)
    )

    if spatial_filter_values:
        properties = properties.filter(
            **({
                'spatialdatamodel__spatialdatavaluemodel__'
                'context_layer_value__in':
                    spatial_filter_values
            })
        )

    activity = request.GET.get("activity", "")
    activity = urllib.parse.unquote(activity)
    if activity == 'all':
        filters[
            "annualpopulationperactivity__activity_type_id__in"
        ] = ActivityType.objects.values_list('id', flat=True)
    else:
        filters['annualpopulationperactivity__activity_type_id__in'] = [
            int(act) for act in activity.split(',')
        ] if activity else []

    if REGIONAL_DATA_CONSUMER in user_roles:
        organisation_id = get_current_organisation_id(request.user)
        province_ids = Province.objects.filter(
            property__organisation_id=organisation_id
        ).values_list("id", flat=True)
        properties = properties.filter(
            province__id__in=province_ids
        )

    filters['property__id__in'] = list(
        properties.values_list('id', flat=True)
    )

    return filters


def national_level_species_report(
        queryset: QuerySet, request: HttpRequest, user_roles: List[str]
) -> List[Dict]:
    """
    Generate a national-level species report based on
    the provided queryset and request parameters.

    Args:
        queryset : The initial queryset containing species data.
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.

    """
    filters = common_filters(request, user_roles)

    report_data = OwnedSpecies.objects.\
        filter(**filters, taxon__in=queryset).\
        values(
            'taxon__common_name_varbatim',
            'taxon__scientific_name'
        ).\
        annotate(
            property_area=Sum("property__property_size_ha"),
            total_area_available=Sum("area_available_to_species"),
            adult_male_total_population=Sum(
                "annualpopulation__adult_male"
            ),
            adult_female_total_population=Sum(
                "annualpopulation__adult_female"
            ),
            sub_adult_male_total_population=Sum(
                "annualpopulation__sub_adult_male"
            ),
            sub_adult_female_total_population=Sum(
                "annualpopulation__sub_adult_female"
            ),
            juvenile_male_total_population=Sum(
                "annualpopulation__juvenile_male"
            ),
            juvenile_female_total_population=Sum(
                "annualpopulation__juvenile_female"
            ),
        )
    return NationalLevelSpeciesReport(report_data, many=True).data


def national_level_property_report(
        queryset: QuerySet, request: HttpRequest, user_roles: List[str]
) -> List[Dict]:
    """
    Generate a national-level property report based on
    the provided queryset and request parameters.

    Args:
        queryset : The initial queryset containing species data.
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.

    """
    filters = common_filters(request, user_roles)
    serializer = NationalLevelPropertyReport(
        queryset,
        many=True,
        context={
            'filters': filters
        }
    )

    return serializer.data


def national_level_activity_report(
        queryset: QuerySet, request: HttpRequest, user_roles: List[str]
) -> List[Dict]:
    """
    Generate a national-level activity report based on
    the provided queryset and request parameters.

    Args:
        queryset : The initial queryset containing species data.
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.

    """
    filters = {}

    start_year = request.GET.get("start_year")
    if start_year:
        end_year = request.GET.get("end_year")
        filters[
            "annualpopulationperactivity__year__range"
        ] = (start_year, end_year)

    property_param = request.GET.get("property")
    if property_param:
        property_list = property_param.split(",")
        filters["property__id__in"] = property_list

    if REGIONAL_DATA_CONSUMER in user_roles:
        organisation_id = get_current_organisation_id(request.user)
        province_ids = Province.objects.filter(
            property__organisation_id=organisation_id
        ).values_list("id", flat=True)
        filters["property__province__id__in"] = province_ids

    serializer = NationalLevelActivityReport(
        queryset,
        many=True,
        context={
            'filters': filters
        }
    )
    return serializer.data


def national_level_province_report(
        queryset: QuerySet, request: HttpRequest, user_roles: List[str]
) -> List[Dict]:
    """
    Generate a national-level species report based on
    the provided queryset and request parameters.

    Args:
        queryset : The initial queryset containing species data.
        request : The HTTP request object containing query parameters.
        user_roles : The roles of the user.

    """
    filters = common_filters(request, user_roles)

    serializer = NationalLevelProvinceReport(
        queryset,
        many=True,
        context={
            'filters': filters
        }
    )

    return serializer.data
