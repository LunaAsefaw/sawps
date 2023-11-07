import logging
import os
import urllib.parse
from typing import Dict
from typing import List
from zipfile import ZipFile

import pandas as pd
from django.conf import settings
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest

from activity.models import ActivityType
from frontend.filters.data_table import DataContributorsFilter
from frontend.filters.metrics import BaseMetricsFilter
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
from frontend.static_mapping import DATA_CONTRIBUTORS, DATA_SCIENTISTS
from frontend.static_mapping import REGIONAL_DATA_CONSUMER
from frontend.utils.organisation import get_current_organisation_id
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity
)
from property.models import Property
from property.models import Province
from species.models import Taxon

logger = logging.getLogger('sawps')

ACTIVITY_REPORT = 'Activity_report'
PROPERTY_REPORT = 'Property_report'
SAMPLING_REPORT = 'Sampling_report'
SPECIES_REPORT = 'Species_report'
PROVINCE_REPORT = 'Province_report'



def get_queryset(user_roles: List[str], request):
    organisation_id = get_current_organisation_id(request.user)
    if set(user_roles) & set(DATA_CONTRIBUTORS + DATA_SCIENTISTS):
        query_filter = DataContributorsFilter
        organisation = request.GET.get("organisation")
        if organisation and (set(user_roles) & set(DATA_SCIENTISTS)):
            ids = organisation.split(",")
            queryset = Property.objects.filter(
                organisation_id__in=ids,
                annualpopulation__taxon__taxon_rank__name="Species"
            ).distinct().order_by("name")
        else:
            queryset = Property.objects.filter(
                organisation_id=organisation_id,
                annualpopulation__taxon__taxon_rank__name="Species"
            ).distinct().order_by("name")

        spatial_filter_values = request.GET.get(
            'spatial_filter_values',
            ''
        ).split(',')

        spatial_filter_values = list(
            filter(None, spatial_filter_values)
        )

        if spatial_filter_values:
            queryset = queryset.filter(
                **({
                    'spatialdatamodel__spatialdatavaluemodel__'
                    'context_layer_value__in':
                        spatial_filter_values
                })
            )
    else:
        query_filter = BaseMetricsFilter
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name="Species"
        ).distinct().order_by("scientific_name")

    filtered_queryset = query_filter(
        request.GET, queryset=queryset
    ).qs

    return filtered_queryset


def get_taxon_queryset(request):
    organisation_id = get_current_organisation_id(request.user)
    query_filter = BaseMetricsFilter
    queryset = Taxon.objects.filter(
        annualpopulation__property__organisation_id=organisation_id,
        taxon_rank__name="Species"
    ).distinct().order_by("scientific_name")

    filtered_queryset = query_filter(
        request.GET, queryset=queryset
    ).qs
    return filtered_queryset


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
    default_species_field = 'taxon__scientific_name__in'
    filters = {}
    species_fields = {
        SPECIES_REPORT: default_species_field,
        PROPERTY_REPORT: default_species_field,
        SAMPLING_REPORT: default_species_field,
        ACTIVITY_REPORT: 'annual_population__taxon__scientific_name__in'
    }

    default_year_field = 'year__range'
    year_fields = {
        SPECIES_REPORT: default_year_field,
        PROPERTY_REPORT: default_year_field,
        SAMPLING_REPORT: default_year_field,
        ACTIVITY_REPORT: default_year_field
    }

    species_list = request.GET.get("species")
    if species_list:
        species_list = species_list.split(",")
        filters[species_fields[report_type]] = species_list

    start_year = request.GET.get("start_year")
    if start_year:
        start_year = int(start_year)
        end_year = int(request.GET.get("end_year"))
        filters[year_fields[report_type]] = (start_year, end_year)

    default_activity_field = (
        'annualpopulationperactivity__'
        'activity_type_id__in'
    )

    activity = request.GET.get("activity", "")
    activity = urllib.parse.unquote(activity)
    if activity != 'all':
        filters[default_activity_field] = [
            int(act) for act in activity.split(',')
        ] if activity else []
    elif report_type == ACTIVITY_REPORT:
        filters[
            default_activity_field
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
        property_id__in=queryset.values_list('id', flat=True),
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
    area_available_values = AnnualPopulation.objects.filter(
        property__in=queryset,
        **filters
    ).distinct('property', 'year')

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
        property__in=queryset,
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
        'annualpopulationperactivity__'
        'activity_type_id__in'
    )
    activity_type_ids = filters[activity_field]
    del filters[activity_field]

    activity_reports = {}
    valid_activities = ActivityType.objects.filter(id__in=activity_type_ids)
    for activity in valid_activities:
        activity_data = AnnualPopulationPerActivity.objects.filter(
            annual_population__property__in=queryset,
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
        filters["year__range"] = (
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
    if activity not in ['all', '']:
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

    report_data = AnnualPopulation.objects. \
        filter(**filters, taxon__in=queryset). \
        values(
            'taxon__common_name_varbatim',
            'taxon__scientific_name',
            'year'
        ). \
        annotate(
            property_area=Sum("property__property_size_ha"),
            total_area_available=Sum("area_available_to_species"),
            adult_male_total_population=Sum(
                "adult_male"
            ),
            adult_female_total_population=Sum(
                "adult_female"
            ),
            sub_adult_male_total_population=Sum(
                "sub_adult_male"
            ),
            sub_adult_female_total_population=Sum(
                "sub_adult_female"
            ),
            juvenile_male_total_population=Sum(
                "juvenile_male"
            ),
            juvenile_female_total_population=Sum(
                "juvenile_female"
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

    return serializer.data[0] if serializer.data else []


def write_report_to_rows(queryset, request):
    """
    Write report rows.
    """
    reports_list = request.GET.get("reports", None)
    path = os.path.join(settings.MEDIA_ROOT, "download_data")
    if not os.path.exists(path):
        os.mkdir(path)

    if reports_list:
        reports_list = reports_list.split(",")

        report_functions = {
            ACTIVITY_REPORT: activity_report_rows,
            PROPERTY_REPORT: property_report,
            SAMPLING_REPORT: sampling_report,
            SPECIES_REPORT: species_report,
            # PROVINCE_REPORT: province_reports
        }

        if request.GET.get('file') == 'xlsx':
            filename = 'data_report' + '.' + request.GET.get('file')
            path_file = os.path.join(path, filename)
            if os.path.exists(path_file):
                os.remove(path_file)

            with pd.ExcelWriter(path_file, engine='openpyxl', mode='w') \
                    as writer:
                for report_name in reports_list:
                    logger.log(
                        level=logging.ERROR,
                        msg=str(report_name)
                    )
                    if report_name in report_functions:
                        rows = report_functions[report_name](queryset, request)
                        dataframe = pd.DataFrame(rows)
                        dataframe.to_excel(
                            writer,
                            sheet_name=report_name,
                            index=False
                        )
                return settings.MEDIA_URL + 'download_data/' \
                    + os.path.basename(path_file)

        csv_reports = []
        for report_name in reports_list:
            if report_name in report_functions:
                rows = report_functions[report_name](queryset, request)
                dataframe = pd.DataFrame(rows)
                filename = "data_report_" + report_name
                filename = filename + '.' + request.GET.get('file')
                path_file = os.path.join(path, filename)

                if os.path.exists(path_file):
                    os.remove(path_file)
                dataframe.to_csv(path_file)
                csv_reports.append(path_file)
        if len(csv_reports) < 1:
            return
        elif len(csv_reports) == 1:
            return settings.MEDIA_URL + 'download_data/' \
                   + os.path.basename(csv_reports[0])
        path_zip = os.path.join(path, 'data_report.zip')
        if os.path.exists(path_zip):
            os.remove(path_zip)
        with ZipFile(path_zip, 'w') as zip:
            for file in csv_reports:
                zip.write(file, os.path.basename(file))
        return settings.MEDIA_URL + 'download_data/' \
            + os.path.basename(path_zip)


def activity_report_rows(queryset: QuerySet, request) -> Dict[str, List[Dict]]:
    """
    Generate property reports for csv and Excel file
    based on the user's request.
    Params:
        queryset (QuerySet): Properties queryset to generate reports from.
        request: The HTTP request object.
    """
    filters = get_report_filter(request, ACTIVITY_REPORT)
    activity_field = (
        'annualpopulationperactivity__'
        'activity_type_id__in'
    )
    activity_type_ids = filters[activity_field]
    del filters[activity_field]
    valid_activities = ActivityType.objects.filter(id__in=activity_type_ids)
    activity_data = AnnualPopulationPerActivity.objects.filter(
        annual_population__property__in=queryset,
        **filters
    )
    years = activity_data.order_by().values_list('year', flat=True).distinct()
    properties = activity_data.order_by(
    ).values_list('annual_population__property__name', flat=True).distinct()
    rows = []

    for year in list(years):
        activity_report_one_row = {}
        for property in list(properties):
            for activity in valid_activities:
                activity_data = AnnualPopulationPerActivity.objects.filter(
                    annual_population__property__name=property,
                    activity_type=activity,
                    year=year,
                    **filters
                )
                serializer = ActivityReportSerializer(
                    activity_data,
                    many=True,
                    activity=activity
                )
                total_field = activity.name + "_total"
                adult_male_field = activity.name + "_adult_male"
                adult_female_field = activity.name + "_adult_female"
                juvenile_male_field = activity.name + "_juvenile_male"
                juvenile_female_field = activity.name + "_juvenile_female"
                for activity_data in serializer.data:
                    activity_report_one_row['property_name'] = \
                        activity_data['property_name']
                    activity_report_one_row['scientific_name'] = \
                        activity_data['scientific_name']
                    activity_report_one_row['common_name'] = \
                        activity_data['common_name']
                    activity_report_one_row['year'] = year
                    activity_report_one_row[total_field] = \
                        activity_data['total']
                    activity_report_one_row[adult_male_field] = \
                        activity_data['adult_male']
                    activity_report_one_row[juvenile_male_field] = \
                        activity_data['adult_female']
                    activity_report_one_row[adult_female_field] = \
                        activity_data['juvenile_male']
                    activity_report_one_row[juvenile_female_field] = \
                        activity_data['juvenile_female']
        rows.append(activity_report_one_row)

    return rows
