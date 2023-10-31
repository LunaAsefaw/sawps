"""Filters in Data table.

"""
import django_filters
from django.db.models.query import QuerySet
from property.models import Property


class DataContributorsFilter(django_filters.FilterSet):
    property = django_filters.CharFilter(method='filter_property')

    class Meta:
        model = Property
        fields = ['property']

    def filter_property(self, queryset: QuerySet, name: str, value: str) \
        -> QuerySet:
        """
        Filter queryset by given property
        Params:
            queryset (QuerySet): The queryset to be filtered.
            name (str): The name of the property to filter by.
            value (str): A comma-separated list of property IDs.
        """
        property_list = value.split(',')
        return queryset.filter(id__in=property_list)
