# -*- coding: utf-8 -*-


"""Admin for property package.
"""
from django.contrib import admin
from property.models import (
    PropertyType, Province, ParcelType,
    Property,
    Parcel
)


class PropertyAdmin(admin.ModelAdmin):
    """Admin page for Property model.

    """
    list_display = (
        'name',
        'short_code',
        'organisation',
        'property_size_ha',
        'province'
    )
    search_fields = ['name', 'organisation__name', 'province__name']

    @admin.action(
        description="Generate spatial filters for selected properties"
    )
    def generate_spatial_filters_for_properties(self, request, queryset):
        """Admin action to generate spatial filter data for
            selected properties."""
        from property.tasks.generate_spatial_filter import (
            generate_spatial_filter_task
        )
        for property_obj in queryset:
            property_obj.spatialdatamodel_set.all().delete()
            generate_spatial_filter_task.delay(
                property_obj.id
            )

    actions = [generate_spatial_filters_for_properties]


class ParcelAdmin(admin.ModelAdmin):
    """Admin page for Parcel model.

    """
    list_display = ('sg_number', 'property', 'parcel_type')
    search_fields = ['sg_number', 'property__name', 'parcel_type__name']


admin.site.register(PropertyType)
admin.site.register(Province)
admin.site.register(ParcelType)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Parcel, ParcelAdmin)
