# -*- coding: utf-8 -*-

"""Context Layers with mapping table to tegola layers.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContextLayer(models.Model):
    """A model for the context layer."""

    name = models.CharField(
        max_length=512
    )

    is_static = models.BooleanField(
        default=True,
    )

    layer_names = models.JSONField(
        default=[],
        blank=True,
        help_text='A list of names for different layers. '
                  'E.g ["layer_1", "layer_2"].'
    )

    def __str__(self) -> str:
        return self.name


class ContextLayerLegend(models.Model):
    """Legend for context layer."""

    layer = models.ForeignKey(ContextLayer, on_delete=models.CASCADE)

    name = models.CharField(
        max_length=512
    )

    colour = models.CharField(
        max_length=20, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class ContextLayerTilingTask(models.Model):
    """Vector tile status for context layer."""

    class TileStatus(models.TextChoices):
        PENDING = 'PE', _('Pending')
        PROCESSING = 'PR', _('Processing')
        DONE = 'DO', _('Done')
        ERROR = 'ER', _('Error')
        CANCELLED = 'CD', _('Cancelled')

    status = models.CharField(
        max_length=2,
        choices=TileStatus.choices,
        default=TileStatus.PENDING
    )

    task_id = models.CharField(
        null=True,
        blank=True,
        default='',
        max_length=256
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    total_size = models.TextField(
        null=True,
        blank=True,
        default=''
    )

    task_return_code = models.IntegerField(
        null=True,
        blank=True
    )

    log = models.TextField(
        default='',
        null=True,
        blank=True
    )

    error_log = models.TextField(
        default='',
        null=True,
        blank=True
    )

    config_path = models.TextField(
        default='',
        null=True,
        blank=True
    )


class Layer(models.Model):
    """A model representing an individual layer within a context."""

    layer_title = models.CharField(
        max_length=512,
        default='',
        blank=True,
        help_text='Title of the layer.'
    )

    display_order = models.IntegerField(
        default=0,
        help_text='Order in which the layer should be displayed.'
    )

    is_filter_layer = models.BooleanField(
        default=False,
        help_text='Indicates if this layer is used as a spatial filter.'
    )

    name = models.CharField(
        max_length=512,
        help_text='The unique name that identifies this layer. E.g., '
                  '"Roads", "Buildings", etc.'
    )

    spatial_filter_field = models.TextField(
        blank=True,
        null=True,
        help_text=(
            'The specific field within this layer used for spatial filtering. '
            'For instance, if filtering by region, this could be '
            'a field like "region_name".'
        )
    )

    context_layer = models.ForeignKey(
        ContextLayer,
        on_delete=models.CASCADE,
        help_text='The context layer to which this individual layer belongs.'
    )

    class Meta:
        ordering = ['display_order']

    def __str__(self) -> str:
        return self.name
