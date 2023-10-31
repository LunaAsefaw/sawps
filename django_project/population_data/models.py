"""Models for population data package.
"""
from django.db import models
from django.contrib.auth.models import User


class AnnualPopulationAbstract(models.Model):
    """ "Annual Population model.
    """
    year = models.PositiveIntegerField()
    # This field is no longer used,
    # but will be deleted after data
    # migration success.
    owned_species = models.ForeignKey(
        "species.OwnedSpecies",
        on_delete=models.CASCADE,
        null=True
    )
    total = models.IntegerField()
    adult_male = models.IntegerField(null=True, blank=True)
    adult_female = models.IntegerField(null=True, blank=True)
    juvenile_male = models.IntegerField(null=True, blank=True)
    juvenile_female = models.IntegerField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class AnnualPopulation(AnnualPopulationAbstract):
    """Annual Population model.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    taxon = models.ForeignKey(
        "species.Taxon",
        on_delete=models.CASCADE,
        null=True
    )
    property = models.ForeignKey(
        "property.Property",
        on_delete=models.CASCADE,
        null=True
    )
    area_available_to_species = models.FloatField(default=0.0)
    sub_adult_total = models.IntegerField(null=True, blank=True)
    sub_adult_male = models.IntegerField(null=True, blank=True)
    sub_adult_female = models.IntegerField(null=True, blank=True)
    juvenile_total = models.IntegerField(null=True, blank=True)
    survey_method = models.ForeignKey(
        "occurrence.SurveyMethod", on_delete=models.CASCADE, null=True
    )
    sampling_size_unit = models.ForeignKey(
        "occurrence.SamplingSizeUnit", on_delete=models.CASCADE, null=True
    )
    certainty = models.ForeignKey(
        "population_data.Certainty", on_delete=models.CASCADE, null=True,
    )
    open_close_system = models.ForeignKey(
        "population_data.OpenCloseSystem", on_delete=models.CASCADE, null=True
    )
    group = models.IntegerField(null=True, blank=True)
    presence = models.BooleanField(null=False, default=False)
    population_status = models.ForeignKey(
        "population_data.PopulationStatus",
        on_delete=models.CASCADE, null=True
    )

    population_estimate_category = models.ForeignKey(
        "population_data.PopulationEstimateCategory",
        on_delete=models.CASCADE, null=True
    )

    sampling_effort_coverage = models.ForeignKey(
        "population_data.SamplingEffortCoverage",
        on_delete=models.CASCADE, null=True
    )
    upper_confidence_level = models.FloatField(
        null=True, blank=True
    )
    lower_confidence_level = models.FloatField(
        null=True, blank=True
    )
    certainty_of_bounds = models.IntegerField(
        null=True, blank=True
    )
    population_estimate_certainty = models.IntegerField(
        null=True, blank=True, choices=[(i, i) for i in range(1, 11)]
    )
    population_estimate_category_other = models.TextField(
        null=True, blank=True
    )
    survey_method_other = models.TextField(
        null=True, blank=True
    )

    def __str__(self):
        return "{} {}".format(
            self.property.name,
            self.year
        )

    class Meta:
        verbose_name = "Annual Population"
        verbose_name_plural = "Annual Populations"
        db_table = "annual_population"
        constraints = [
            models.CheckConstraint(
                name="Adult male and adult female"
                     " must not be greater than total",
                check=models.Q(
                    total__gte=
                    models.F("adult_male") + models.F("adult_female")
                ),
            ),
            models.UniqueConstraint(
                fields=["year",
                        "taxon",
                        "property"
                        ],
                name="unique_population_count",
            )
        ]


class AnnualPopulationPerActivity(AnnualPopulationAbstract):
    """Annual Population per activity model.
    """

    annual_population = models.ForeignKey(
        AnnualPopulation,
        on_delete=models.CASCADE,
        null=True
    )
    activity_type = models.ForeignKey(
        "activity.ActivityType",
        on_delete=models.CASCADE)
    founder_population = models.BooleanField(null=True, blank=True)
    reintroduction_source = models.CharField(max_length=250, null=True,
                                             blank=True)
    intake_permit = models.CharField(null=True, blank=True, max_length=100)
    translocation_destination = models.TextField(null=True, blank=True)
    offtake_permit = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return "{} {} {}".format(
            self.annual_population.property.name,
            self.year,
            self.activity_type.name)

    class Meta:
        verbose_name = "Population count per activity"
        verbose_name_plural = "Population count per activities"
        db_table = "annual_population_per_activity"
        constraints = [
            models.UniqueConstraint(
                fields=["year",
                        "annual_population",
                        "activity_type"
                        ],
                name="unique_population_count_per_activity",
            )
        ]


class Certainty(models.Model):
    """Certainty model.
    """

    name = models.CharField(
        max_length=250, null=False, blank=False, default="", unique=True
    )
    description = models.TextField(null=True, blank=True,
                                   help_text="Description")

    class Meta:
        verbose_name = "Population estimate certainty"
        verbose_name_plural = "Population estimate certainties"
        db_table = "certainty"

    def __str__(self) -> str:
        return self.name


class OpenCloseSystem(models.Model):
    """Open Close System model.
    """

    name = models.CharField(
        max_length=250, null=False, blank=False, default="", unique=True
    )

    class Meta:
        verbose_name = "Open Close System"
        verbose_name_plural = "Open Close System"
        db_table = "open_close_system"

    def __str__(self) -> str:
        return self.name


class PopulationStatus(models.Model):
    """Population status model.
    """

    name = models.TextField(
        null=False,
        blank=False,
        default="",
        unique=True,
        help_text="Name"
    )

    class Meta:
        verbose_name = "Population Status"
        verbose_name_plural = "Population Status"
        db_table = "population_status"

    def __str__(self) -> str:
        return self.name


class PopulationEstimateCategory(models.Model):
    """Population Estimate Category model.
    """

    name = models.TextField(
        null=False,
        blank=False,
        default="",
        unique=True,
        help_text="Name"
    )

    class Meta:
        verbose_name = "Population Estimate Category"
        verbose_name_plural = "Population Estimate Categories"
        db_table = "population_estimate_category"

    def __str__(self) -> str:
        return self.name


class SamplingEffortCoverage(models.Model):
    """Sampling Effort Coverage model.
    """

    name = models.TextField(
        null=False,
        blank=False,
        default="",
        unique=True,
        help_text="Name"
    )

    sort_order = models.IntegerField(
        null=True,
        unique=True,
        help_text="Order sampling effort coverage model."
    )

    class Meta:
        verbose_name = "Sampling Effort Coverage"
        verbose_name_plural = "Sampling Effort Coverages"
        db_table = "sampling_effort_coverage"

    def __str__(self) -> str:
        return self.name
