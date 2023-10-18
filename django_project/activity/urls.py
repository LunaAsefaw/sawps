from django.urls import path

from activity.views import ActivityTypeAPIView

# views urls
urlpatterns = [  # '',
    path(
        'api/activity-type/',
        ActivityTypeAPIView.as_view(),
        name='activity-type'
    )
]
