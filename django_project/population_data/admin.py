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
        'property_name',
        'year',
        'scientific_name',
        'common_name'
    ]
    form = AnnualPopulationForm

    def property_name(self, obj: AnnualPopulation):
        return obj.property.name

    def scientific_name(self, obj: AnnualPopulation):
        return obj.taxon.scientific_name

    def common_name(self, obj: AnnualPopulation):
        return obj.taxon.common_name_varbatim


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
        return obj.owned_species.property.name

    def scientific_name(self, obj: AnnualPopulationPerActivity):
        return obj.owned_species.taxon.scientific_name

    def common_name(self, obj: AnnualPopulationPerActivity):
        return obj.owned_species.taxon.common_name_varbatim


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
