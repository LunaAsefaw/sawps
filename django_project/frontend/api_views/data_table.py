"""API Views related to data table.
"""
from typing import List

from django.db.models.query import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.filters.metrics import BaseMetricsFilter
from frontend.static_mapping import DATA_CONTRIBUTORS, DATA_SCIENTISTS
from frontend.utils.data_table import (
    data_table_reports,
    national_level_user_table,
    national_level_province_report,
    PROVINCE_REPORT,
    write_report_to_rows,
    get_queryset
)
from frontend.utils.organisation import get_current_organisation_id
from frontend.utils.user_roles import get_user_roles
from species.models import Taxon


class DataTableAPIView(APIView):
    """
    API view for retrieving data table reports.
    """
    permission_classes = [IsAuthenticated]

    def get_taxon_queryset(self):
        """
        Get the filtered Taxon queryset based on user filters.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        query_filter = BaseMetricsFilter
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name="Species"
        ).distinct().order_by("scientific_name")

        filtered_queryset = query_filter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get_queryset(self, user_roles: List[str]) -> QuerySet:
        """
        Get the filtered queryset based on user filters.
        """
        return get_queryset(user_roles, self.request)

    def get(self, request) -> Response:
        """
        Handle GET request to retrieve data table reports.
        Params: request (Request) The HTTP request object.
        """
        user_roles = get_user_roles(self.request.user)
        queryset = self.get_queryset(user_roles)
        if set(user_roles) & set(DATA_CONTRIBUTORS + DATA_SCIENTISTS):
            reports = data_table_reports(queryset, request, user_roles)

            report_list = request.GET.get("reports", None)
            if report_list:
                report_list = report_list.split(",")
                if PROVINCE_REPORT in report_list:
                    taxon_queryset = self.get_taxon_queryset()
                    province_reports = national_level_province_report(
                        taxon_queryset,
                        request,
                        user_roles
                    )
                    if province_reports:
                        reports.append({
                            PROVINCE_REPORT: province_reports
                        })
            if request.GET.get("file"):
                return Response({
                    "file": write_report_to_rows(queryset, request)
                })

            return Response(reports)
        else:
            return Response(
                national_level_user_table(
                    queryset, request, user_roles)
            )
