# -*- coding: utf-8 -*-


"""Admin for activity package.
"""
from django.contrib import admin
from django.utils.html import format_html
from activity.models import ActivityType
from activity.forms import ActivityTypeForm


class ActivityTypeAdmin(admin.ModelAdmin):
    """Admin page for Activity Type model

    """
    list_display = [
        'name',
        'recruitment',
        'width',
        'display_color',
        'display_export_fields'
    ]
    search_fields = [
        'name',
        'width',
        'export_fields'
    ]
    form = ActivityTypeForm

    def display_export_fields(self, obj):
        return ', '.join(obj.export_fields)

    def display_color(self, obj):
        return format_html(
            '<span style="width:10px;height:10px;'
            'display:inline-block;background-color:%s"></span>' % obj.colour
        )
    display_color.short_description = 'Colour'
    display_color.allow_tags = True


admin.site.register(ActivityType, ActivityTypeAdmin)
