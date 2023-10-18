"""API Views related to user.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.serializers.user_info import UserInfoSerializer


class UserInfoAPIView(LoginRequiredMixin, APIView):
    """
    API View to retrieve information of the currently logged-in user.

    This view is protected and requires the user to be logged in.
    Once accessed, it returns the serialized information of the logged-in user.
    """

    def get(self, request, *args, **kwargs):
        user = self.request.user
        return Response(
            UserInfoSerializer(user).data
        )
