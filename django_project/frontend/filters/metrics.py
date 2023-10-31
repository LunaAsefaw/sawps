"""Filters in metrics.

"""
import django_filters
from django.db.models.query import QuerySet
from property.models import Property
from species.models import Taxon


class BaseMetricsFilter(django_filters.FilterSet):
    """
    Filter class for metrics based on species, start year, and property.
    """
    species = django_filters.CharFilter(method='filter_species')
    start_year = django_filters.CharFilter(method='filter_start_year')
    property = django_filters.CharFilter(method='filter_property')

    class Meta:
        model = Taxon
        fields = ['species', 'start_year', 'property']

    def filter_species(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Filter species based on common_name_varbatim.

        Params:
            queryset (QuerySet): The base queryset of Taxon model.
            value (str): Comma-separated species names.
            name (str): The name of the field to be filtered (property).
        """
        species_list = value.split(',')
        return queryset.filter(scientific_name__in=species_list)

    def filter_start_year(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Filter annual populations based on range from start_year to end_year.

        Params:
            queryset (QuerySet): The base queryset of Taxon model.
            value (str): The start year of the annual population.
            name (str): The name of the field to be filtered (property).
        """
        start_year = int(value)
        end_year = int(self.data.get('end_year'))
        return queryset.filter(
            annualpopulation__year__range=(
                start_year,
                end_year
            )
        )

    def filter_property(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Filter properties based on owned species.

        Params:
            queryset (QuerySet): The base queryset of Taxon model.
            value (str): Comma-separated property IDs.
            name (str): The name of the field to be filtered (property).
        """
        properties_list = value.split(',')
        return queryset.filter(
            annualpopulation__property__id__in=properties_list
        )


class ActivityBaseMetricsFilter(BaseMetricsFilter):
    """
    Filter the queryset based on the start year and end year of activity data.
    Params:
            queryset (QuerySet): The base queryset of Taxon model.
            value (str): The start year of the annual population.
            name (str): The name of the field to be filtered (property).
    """

    def filter_start_year(self, queryset, name, value):
        start_year = int(value)
        end_year = int(self.data.get('end_year'))
        return queryset.filter(
            annualpopulation__annualpopulationperactivity__year__range=(
                start_year,
                end_year
            )
        )


class PropertyFilter(django_filters.FilterSet):
    """
    A custom filter for filtering Property objects based on
    a comma-separated list of property IDs.
    """
    property = django_filters.CharFilter(method='filter_property')
    start_year = django_filters.CharFilter(method='filter_start_year')

    class Meta:
        model = Property
        fields = ['property', 'start_year']

    def filter_property(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Custom filter method to filter properties by their IDs.
        params:
            queryset (QuerySet): The initial queryset of Property objects.
            name (str): The name of the field to be filtered (property).
            value (str): A comma-separated list of property IDs.
        """
        properties_list = value.split(',')
        return queryset.filter(id__in=properties_list)

    def filter_start_year(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Filter property based on range from start_year to end_year.

        Params:
            queryset (QuerySet): The base queryset of Taxon model.
            value (str): The start year of the annual population.
            name (str): The name of the field to be filtered (property).
        """
        start_year = int(value)
        end_year = int(self.data.get('end_year'))
        return queryset.filter(
            annualpopulation__year__range=(
                start_year,
                end_year
            )
        )
