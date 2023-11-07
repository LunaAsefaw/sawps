"""Species models.
"""
import re
from django.contrib.auth.models import User
from django.db import models
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator


class TaxonRank(models.Model):
    """Taxon rank model."""

    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taxon Rank"
        verbose_name_plural = "Taxon Ranks"
        db_table = "taxon_rank"


class Taxon(models.Model):
    """Taxon model."""

    scientific_name = models.CharField(max_length=250, unique=True)
    common_name_varbatim = models.CharField(
        max_length=250,
        null=True, blank=True)
    colour_variant = models.BooleanField(null=True, blank=True)
    infraspecific_epithet = models.CharField(
        max_length=250, unique=True, null=True, blank=True
    )
    taxon_rank = models.ForeignKey(
        "species.TaxonRank",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    show_on_front_page = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    front_page_order = models.PositiveIntegerField(
        verbose_name="Front page order", null=False, blank=True, default=0
    )
    colour = models.CharField(max_length=20, null=True, blank=True)
    icon = models.FileField(
        upload_to="taxon_icons",
        null=True, blank=True,
        help_text=(
            'Will be generated automatically from graph_icon to be used in '
            'population overview. Please re-upload graph_icon to '
            'regenerate icon.'
        )
    )
    graph_icon = models.FileField(
        upload_to="taxon_graph_icons",
        null=True, blank=True,
        validators=[FileExtensionValidator(['svg'])],
        help_text=(
            'Use SVG file with black (#000000) '
            'fill and transparent background. '
            'It will be used as species icon in graph/charts.'
        )
    )
    topper_icon = models.FileField(
        upload_to="taxon_topper_icons",
        null=True, blank=True,
        validators=[FileExtensionValidator(['svg'])],
        help_text=(
            'Will be generated automatically from graph_icon to be used in '
            'Report and Charts topper. Please re-upload graph_icon to '
            'regenerate topper_icon.'
        )
    )

    def __str__(self):
        return self.scientific_name

    class Meta:
        verbose_name = "Taxon"
        verbose_name_plural = "Taxa"
        db_table = "taxon"

    def replace_fill_color(self, data, new_color):
        fill_pattern = re.compile(br'fill="[^"]*"', re.IGNORECASE)
        return fill_pattern.sub(br'fill="' + new_color.encode() + br'"', data)

    def save(self, *args, **kwargs):
        if self.graph_icon:
            graph_icon_original = self.graph_icon.read()

            # Edit graph icon fill to be black
            graph_icon = self.replace_fill_color(
                graph_icon_original, '#000000'
            )
            graph_icon = ContentFile(
                graph_icon, name=f"{self.scientific_name}-graph.svg"
            )
            self.graph_icon = graph_icon

            topper_icon = self.replace_fill_color(
                graph_icon_original, '#75B37A'
            )
            topper_icon = ContentFile(
                topper_icon, name=f"{self.scientific_name}-topper.svg"
            )
            self.topper_icon = topper_icon

            icon = self.replace_fill_color(graph_icon_original, '#FFFFFF')
            icon = ContentFile(
                icon, name=f"{self.scientific_name}-icon.svg"
            )
            self.icon = icon

        return super().save(*args, **kwargs)


class OwnedSpecies(models.Model):
    """Owned species mdoel."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    taxon = models.ForeignKey("species.Taxon", on_delete=models.CASCADE)
    property = models.ForeignKey("property.Property", on_delete=models.CASCADE)
    area_available_to_species = models.FloatField(default=0.0)

    def __str__(self):
        return self.property.name

    class Meta:
        verbose_name = "Owned Species"
        verbose_name_plural = "Owned Species"
        db_table = "owned_species"


class TaxonSurveyMethod(models.Model):
    """taxon survey methods"""

    taxon = models.ForeignKey("species.Taxon", on_delete=models.CASCADE)
    survey_method = models.ForeignKey(
        "occurrence.SurveyMethod", on_delete=models.CASCADE
    )
