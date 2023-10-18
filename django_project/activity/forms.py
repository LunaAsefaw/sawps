from django.forms import ModelForm
from django.forms.widgets import TextInput
from activity.models import ActivityType


class ActivityTypeForm(ModelForm):
    """
    Activity Type form.
    """
    class Meta:
        model = ActivityType
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }
