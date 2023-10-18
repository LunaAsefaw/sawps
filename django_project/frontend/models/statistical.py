"""Classes for Statistical R Model."""
from django.db import models
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver


# model output types
NATIONAL_TREND = 'national_trend'
POPULATION_PER_PROVINCE = 'population_per_province'
PROVINCE_TREND = 'province_trend'
PROPERTY_TREND = 'property_trend'
POPULATION_PER_PROPERTY = 'population_per_property'
SPECIES_PER_PROPERTY = 'species_per_property'


class StatisticalModel(models.Model):
    """Model that stores R code of statistical model."""

    taxon = models.ForeignKey(
        'species.Taxon',
        on_delete=models.CASCADE,
        unique=True,
        blank=True,
        null=True,
    )

    name = models.CharField(
        blank=False,
        null=False,
        max_length=256
    )

    code = models.TextField(
        null=False,
        blank=False
    )

    def __str__(self) -> str:
        return f'{self.taxon} - {self.name}'


@receiver(post_save, sender=StatisticalModel)
def statistical_model_post_create(sender, instance: StatisticalModel,
                                  created, *args, **kwargs):
    from frontend.tasks.start_plumber import (
        start_plumber_process
    )
    from frontend.utils.statistical_model import (
        clear_statistical_model_output_cache
    )
    if not created:
        clear_statistical_model_output_cache(instance.taxon)
    if instance.code:
        # respawn Plumber API
        start_plumber_process.apply_async(queue='plumber')


@receiver(pre_delete, sender=StatisticalModel)
def statistical_model_pre_delete(sender, instance: StatisticalModel,
                                 *args, **kwargs):
    from frontend.utils.statistical_model import (
        clear_statistical_model_output_cache
    )
    clear_statistical_model_output_cache(instance.taxon)


@receiver(post_delete, sender=StatisticalModel)
def statistical_model_post_delete(sender, instance: StatisticalModel,
                                  *args, **kwargs):
    from frontend.tasks.start_plumber import (
        start_plumber_process
    )
    # respawn Plumber API
    start_plumber_process.apply_async(queue='plumber')


class StatisticalModelOutput(models.Model):
    """Output of statistical model."""

    OUTPUT_TYPE_CHOICES = (
        (NATIONAL_TREND, 'National Trend'),
        (POPULATION_PER_PROVINCE, 'Population Per Province'),
        (PROVINCE_TREND, 'Province Trend'),
        (PROPERTY_TREND, 'Property Trend'),
        (POPULATION_PER_PROPERTY, 'Population Per Property'),
        (SPECIES_PER_PROPERTY, 'Species Per Property')
    )

    model = models.ForeignKey(
        'frontend.StatisticalModel',
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=100,
        choices=OUTPUT_TYPE_CHOICES
    )
