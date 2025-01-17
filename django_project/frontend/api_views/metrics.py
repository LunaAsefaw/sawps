﻿"""API Views related to metrics.
"""
import datetime
from typing import List

from django.db.models.query import QuerySet
from django.http import HttpRequest
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.filters.metrics import (
    ActivityBaseMetricsFilter,
    BaseMetricsFilter,
    PropertyFilter,
)
from frontend.serializers.metrics import (
    ActivityMatrixSerializer,
    SpeciesPopuationCountPerYearSerializer,
    SpeciesPopulationDensityPerPropertySerializer,
    TotalCountPerActivitySerializer,
    PopulationPerAgeGroupSerialiser,
    TotalAreaVSAvailableAreaSerializer,
    TotalCountPerPopulationEstimateSerializer
)
from frontend.serializers.metrics import AreaAvailablePerSpeciesSerializer
from frontend.utils.data_table import (
    get_queryset, get_report_filter, SPECIES_REPORT
)
from frontend.utils.data_table import get_taxon_queryset, common_filters
from frontend.utils.metrics import (
    calculate_population_categories,
    calculate_total_area_per_property_type,
    calculate_base_population_of_species,
    calculate_species_count_per_province
)
from frontend.utils.organisation import (
    get_current_organisation_id
)
from frontend.utils.user_roles import get_user_roles
from population_data.models import AnnualPopulation
from property.models import Property
from species.models import Taxon


class SpeciesPopuationCountPerYearAPIView(APIView):
    """
    An API view to retrieve species population count per year.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SpeciesPopuationCountPerYearSerializer

    def get_queryset(self) -> List[Taxon]:
        """
        Returns a filtered queryset of Taxon objects representing
        species within the specified organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name='Species'
        ).distinct()
        filtered_queryset = BaseMetricsFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Handles HTTP GET requests and returns a serialized JSON response.
        Params: The HTTP request object containing the user's request data.
        """
        queryset = self.get_queryset()
        serializer = SpeciesPopuationCountPerYearSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class ActivityPercentageAPIView(APIView):
    """
    API view to retrieve activity percentage data for species.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityMatrixSerializer

    def get_queryset(self) -> List[Taxon]:
        """
        Returns a filtered queryset of Taxon objects representing
        species within the specified organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name='Species'
        ).distinct()
        filtered_queryset = ActivityBaseMetricsFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle the GET request to retrieve activity percentage data.
        Params: request (Request): The HTTP request object.
        """
        queryset = self.get_queryset()
        serializer = ActivityMatrixSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(calculate_base_population_of_species(serializer.data))


class TotalCountPerPopulationEstimateAPIView(APIView):
    """
    API view to retrieve total counts per population
    estimate category for species.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        serializer = TotalCountPerPopulationEstimateSerializer(
            context={"request": request}
        )
        result = serializer.get_total_counts_per_population_estimate()
        return Response(result)


class TotalCountPerActivityAPIView(APIView):
    """
    API view to retrieve total counts per activity for species.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityMatrixSerializer

    def get_queryset(self) -> List[Taxon]:
        """
        Returns a filtered queryset of Taxon objects representing
        species within the specified organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name='Species'
        ).distinct()
        filtered_queryset = ActivityBaseMetricsFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle the GET request to retrieve total counts per activity data.
        Params:request (Request): The HTTP request object.
        """
        queryset = self.get_queryset()
        serializer = TotalCountPerActivitySerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class SpeciesPopulationCountPerProvinceAPIView(APIView):
    """
    API view to retrieve species pcount per province.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Property]:
        """
        Returns a filtered queryset of property objects
        within the specified organization.
        """

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET request to retrieve species count per province.
        """
        user_roles = get_user_roles(request.user)
        queryset = get_taxon_queryset(request)
        filters = common_filters(request, user_roles)

        return Response(
            calculate_species_count_per_province(
                queryset.first(),
                filters
            )
        )


class SpeciesPopulationDensityPerPropertyAPIView(APIView):
    """
    API view to retrieve species population density per property.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SpeciesPopulationDensityPerPropertySerializer

    def get_queryset(self) -> QuerySet[Property]:
        """
        Returns a filtered queryset of property objects
        within the specified organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Property.objects.filter(organisation_id=organisation_id)
        filtered_queryset = PropertyFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset.distinct('name')

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle the GET request to retrieve species
        population density per property.
        Params:request (Request): The HTTP request object.
        """
        queryset = self.get_queryset()

        # Extract the species_name query parameter from the URL
        species_name = self.request.query_params.get("species", None)

        serializer = SpeciesPopulationDensityPerPropertySerializer(
            queryset,
            many=True,
            context={
                "request": request,
                "species_name": species_name
            }
        )
        return Response(serializer.data)


class PropertiesPerPopulationCategoryAPIView(APIView):
    """
    API endpoint to retrieve population categories
    for properties within an organization.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Property]:
        """
        Get the filtered queryset of properties owned by the organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Property.objects.filter(organisation_id=organisation_id)
        filtered_queryset = PropertyFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET request to retrieve population categories for properties.
        """
        species_name = request.GET.get("species")
        start_year = request.GET.get("start_year", 0)
        end_year = request.GET.get("end_year", datetime.datetime.now().year)
        year_range = (int(start_year), int(end_year))
        queryset = self.get_queryset()
        return Response(
            calculate_population_categories(queryset, species_name, year_range)
        )


class TotalAreaAvailableToSpeciesAPIView(APIView):
    """
    An API view to retrieve total area available to species.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Property]:
        """
        Get the filtered queryset of properties for the current organization.
            """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Property.objects.filter(organisation_id=organisation_id)
        filtered_queryset = PropertyFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset.distinct('name')

    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Retrieve the calculated total area available to species and
        return it as a Response.
        """
        user_roles = get_user_roles(request.user)
        queryset = get_queryset(user_roles, request)
        filters = get_report_filter(request, SPECIES_REPORT)
        if 'annualpopulationperactivity__activity_type_id__in' in filters:
            del filters['annualpopulationperactivity__activity_type_id__in']
        species_population_data = AnnualPopulation.objects.filter(
            property__in=queryset,
            **filters
        )
        return Response(
            AreaAvailablePerSpeciesSerializer(
                species_population_data, many=True
            ).data
        )


class TotalAreaPerPropertyTypeAPIView(APIView):
    """
    API endpoint to retrieve total area per property type
    for properties within an organization.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Property]:
        """
        Get the filtered queryset of properties owned by the organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Property.objects.filter(organisation_id=organisation_id)
        filtered_queryset = PropertyFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET request to retrieve total area per property type.
        """
        species_name = request.GET.get("species")
        queryset = self.get_queryset()
        return Response(
            calculate_total_area_per_property_type(
                queryset, species_name)
        )


class PopulationPerAgeGroupAPIView(APIView):
    """
    API endpoint to retrieve population of age group.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Taxon]:
        """
        Get the filtered queryset taxon owned by the organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name='Species'
        ).distinct()
        filtered_queryset = BaseMetricsFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle the GET request to retrieve population of age groups.
        Params:request (Request): The HTTP request object.
        """
        queryset = self.get_queryset()
        serializer = PopulationPerAgeGroupSerialiser(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class TotalAreaVSAvailableAreaAPIView(APIView):
    """
    API endpoint to retrieve total area and area available.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> List[Taxon]:
        """
        Returns a filtered queryset of Taxon objects representing
        species within the specified organization.
        """
        organisation_id = get_current_organisation_id(self.request.user)
        queryset = Taxon.objects.filter(
            annualpopulation__property__organisation_id=organisation_id,
            taxon_rank__name='Species'
        ).distinct()
        filtered_queryset = BaseMetricsFilter(
            self.request.GET, queryset=queryset
        ).qs
        return filtered_queryset

    def get(self, request, *args, **kwargs) -> Response:
        """
        Handle GET request to retrieve total area and available area.
        """
        queryset = self.get_queryset()
        serializer = TotalAreaVSAvailableAreaSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
