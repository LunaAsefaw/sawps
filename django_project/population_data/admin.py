"""Admin for population data package.
"""
from django.contrib import admin
from population_data.forms import AnnualPopulationForm
from population_data.models import (
    AnnualPopulation,
    AnnualPopulationPerActivity,
    OpenCloseSystem,
    SamplingEffortCoverage,
    PopulationStatus,
    PopulationEstimateCategory
)


class AnnualPopulationAdmin(admin.ModelAdmin):
    form = AnnualPopulationForm


admin.site.register(OpenCloseSystem)
admin.site.register(AnnualPopulation, AnnualPopulationAdmin)


@admin.register(AnnualPopulationPerActivity)
class AnnualPopulationPerActivityAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'property_name',
        'year',
        'activity_type',
        'total'
    ]
    # list_filter = [
    #     'owned_species__property',
    #     'year',
    #     'activity_type'
    # ]
    search_fields = [
        'owned_species__property__name',
        'owned_species__taxon__scientific_name',
        'owned_species__taxon__common_name_varbatim'
    ]

    def property_name(self, obj: AnnualPopulationPerActivity):
        return obj.owned_species.property.name


admin.site.register(SamplingEffortCoverage)
admin.site.register(PopulationStatus)
admin.site.register(PopulationEstimateCategory)
