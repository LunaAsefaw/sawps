# -*- coding: utf-8 -*-


"""Admin page for Occurrence models.
"""
from django.contrib import admin
from occurrence.models import SurveyMethod


class SurveyMethodAdmin(admin.ModelAdmin):
    """Admin page for SurveyMethod model

    """
    list_display = ('name', 'sort_id')
    search_fields = [
        'name',
        'sort_id'
    ]


admin.site.register(SurveyMethod, SurveyMethodAdmin)
