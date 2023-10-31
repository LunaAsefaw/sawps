from django.forms import ModelForm
from population_data.models import AnnualPopulation


class AnnualPopulationForm(ModelForm):

    class Meta:

        model = AnnualPopulation
        fields = (
            "year",
            "owned_species",
            "user",
            "taxon",
            "property",
            "area_available_to_species",
            "total",
            "adult_male",
            "adult_female",
            "sub_adult_total",
            "sub_adult_male",
            "sub_adult_female",
            "juvenile_total",
            "group",
            "juvenile_male",
            "juvenile_female",
            "survey_method",
            "open_close_system",
            "presence",
            "population_status",
            "population_estimate_category",
            "sampling_effort_coverage",
            "upper_confidence_level",
            "lower_confidence_level",
            "certainty_of_bounds",
            "population_estimate_certainty",
            "note",
        )
