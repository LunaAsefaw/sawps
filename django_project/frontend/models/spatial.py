from django.db import models


class SpatialDataModel(models.Model):
    property = models.ForeignKey(
        'property.Property',
        on_delete=models.CASCADE,
    )
    context_layer = models.ForeignKey(
        'frontend.ContextLayer',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.property.name

    class Meta:
        verbose_name = "Spatial data"
        verbose_name_plural = 'Spatial data'


class SpatialDataValueModel(models.Model):
    context_layer_value = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    spatial_data = models.ForeignKey(
        SpatialDataModel,
        on_delete=models.CASCADE,
        null=True,
        blank=False
    )
    layer = models.ForeignKey(
        'frontend.Layer',
        on_delete=models.CASCADE,
        null=True,
        blank=False
    )

    def __str__(self):
        return self.context_layer_value

    class Meta:
        verbose_name = "Spatial data value"
        verbose_name_plural = 'Spatial data values'
        indexes = [
            models.Index(fields=['spatial_data_id', 'context_layer_value']),
        ]
