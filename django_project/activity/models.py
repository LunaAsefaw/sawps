# -*- coding: utf-8 -*-


"""Models for activity package.
"""
from django.db import models


class ActivityType(models.Model):
    """activity type model"""

    name = models.CharField(max_length=150, unique=True)
    recruitment = models.BooleanField(null=True, blank=True)
    colour = models.CharField(
        max_length=20,
        default='#000000'
    )
    width = models.FloatField(
        default=130.2,
        help_text=(
            'Column width in the Activity Report. The default is 130.2.'
        )
    )
    export_fields = models.JSONField(
        default=list,
        help_text=(
            'Fields that will be taken from Annual Population '
            'Per Activity table when exporting Activity Report. '
            'Input as Array e.g. '
            '["intake_permit", "translocation_destination"]'
        ),
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
