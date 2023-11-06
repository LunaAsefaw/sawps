"""Admin for population data package.
"""
from django.contrib import admin
from population_data.forms import AnnualPopulationForm
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    OpenCloseSystem,
    PopulationEstimateCategory,
    PopulationStatus,
    SamplingEffortCoverage,
)


class AnnualPopulationAdmin(admin.ModelAdmin):
    list_display = [
        'property_name',
        'year',
        'scientific_name',
        'common_name'
    ]
    search_fields = [
        'property__name',
        'year',
        'taxon__scientific_name',
        'taxon__common_name_varbatim'
    ]
    form = AnnualPopulationForm

    def property_name(self, obj: AnnualPopulation):
        if obj.property:
            return obj.property.name
        return None

    def scientific_name(self, obj: AnnualPopulation):
        if obj.taxon:
            return obj.taxon.scientific_name
        return None

    def common_name(self, obj: AnnualPopulationPerActivity):
        if obj.taxon:
            return obj.taxon.common_name_varbatim
        return None


class OpenCloseSystemAdmin(admin.ModelAdmin):
    """Admin page for OpenCloseSystem model

    """
    list_display = ('id', 'name',)
    search_fields = ['name']


admin.site.register(OpenCloseSystem, OpenCloseSystemAdmin)
admin.site.register(AnnualPopulation, AnnualPopulationAdmin)


@admin.register(AnnualPopulationPerActivity)
class AnnualPopulationPerActivityAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'property_name',
        'scientific_name',
        'common_name',
        'year',
        'activity_type',
        'total'
    ]
    search_fields = [
        'owned_species__property__name',
        'owned_species__taxon__scientific_name',
        'owned_species__taxon__common_name_varbatim'
    ]

    def property_name(self, obj: AnnualPopulationPerActivity):
        if obj.annual_population and obj.annual_population.property:
            return obj.annual_population.property.name
        return None

    def scientific_name(self, obj: AnnualPopulationPerActivity):
        if obj.annual_population and obj.annual_population.taxon:
            return obj.annual_population.taxon.scientific_name
        return None

    def common_name(self, obj: AnnualPopulationPerActivity):
        if obj.annual_population and obj.annual_population.taxon:
            return obj.annual_population.taxon.common_name_varbatim
        return None


class SamplingEffortCoverageAdmin(admin.ModelAdmin):
    """Admin page for SamplingEffortCoverage model

    """
    list_display = ('id', 'name', 'sort_order')
    search_fields = ['name', 'sort_order']


class PopulationStatusAdmin(admin.ModelAdmin):
    """Admin page for PopulationStatus model

    """
    list_display = ('id', 'name')
    search_fields = ['name']


class PopulationEstimateCategoryAdmin(admin.ModelAdmin):
    """Admin page for PopulationEstimateCategory model

    """
    list_display = ('id', 'name')
    search_fields = ['name']


admin.site.register(SamplingEffortCoverage, SamplingEffortCoverageAdmin)
admin.site.register(PopulationStatus, PopulationStatusAdmin)
admin.site.register(
    PopulationEstimateCategory,
    PopulationEstimateCategoryAdmin
)
