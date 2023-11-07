# -*- coding: utf-8 -*-


"""Species forms.
"""
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from species.models import Taxon


class TaxonForm(ModelForm):
    """Taxon form.

    """
    class Meta:
        model = Taxon
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }
        help_texts = {
            'graph_icon': mark_safe(
                "SVG file with black (#000000) "
                "fill and transparent background. "
                "It will be used as species icon in graph/charts. "
                "<a href='%s' target='_blank'>Click here for sample!</a>" % (
                    '/static/images/Loxodonta_africana-graph.svg')
            ),
            'topper_icon': mark_safe(
                "SVG file with fill = #75B37A "
                "and transparent background. "
                "Will be generated automatically from graph_icon "
                "to be used in Report and Charts topper. "
                "Please re-upload graph_icon to regenerate topper_icon! "
                "<a href='%s' target='_blank'>Click here for sample!</a>" % (
                    '/static/images/Loxodonta_africana-topper.svg')
            ),
            'icon': mark_safe(
                "SVG file with fill = #FFFFFF and transparent background. "
                "Will be generated automatically from graph_icon to be "
                "used in population overview graph at landing page. "
                "Please re-upload graph_icon to regenerate icon! "
                "<a href='%s' target='_blank'>Click here for sample!</a>" % (
                    '/static/images/Loxodonta_africana-icon.svg')
            )
        }
