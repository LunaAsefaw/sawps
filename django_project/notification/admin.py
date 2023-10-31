from django.contrib import admin
from notification.models import Reminder

# Register your models here.


class ReminderAdmin(admin.ModelAdmin):
    """Admin page for Reminder model

    """
    list_display = ('title', 'date', 'text', 'status')
    list_filter = ('title', 'status', 'date')
    ordering = ('status', 'date')
    search_fields = [
        'title',
        'date',
        'text',
        'status'
    ]


admin.site.register(Reminder, ReminderAdmin)
