from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from activity.models import ActivityType
from activity.serializers import ActivityTypeSerializer


class ActivityTypeAPIView(APIView):
    """Get Activity Type"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = ActivityType.objects.all().order_by('name')
        return Response(
            status=200,
            data=ActivityTypeSerializer(queryset, many=True).data
        )
