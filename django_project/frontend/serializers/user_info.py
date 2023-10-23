"""Serializer for user info classes."""
from django.contrib.auth.models import User
from rest_framework import serializers
from frontend.utils.user_roles import (
    get_user_roles as get_user_roles_func,
    get_user_permissions as get_user_permissions_func
)


class UserInfoSerializer(serializers.Serializer):
    user_roles = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    current_organisation_id = serializers.SerializerMethodField()
    current_organisation = serializers.SerializerMethodField()

    def get_current_organisation(self, obj: User):
        if obj.user_profile and obj.user_profile.current_organisation:
            return obj.user_profile.current_organisation.name
        return ''

    def get_current_organisation_id(self, obj: User):
        if obj.user_profile and obj.user_profile.current_organisation:
            return obj.user_profile.current_organisation_id
        return ''

    def get_user_roles(self, obj: User):
        return get_user_roles_func(obj)

    def get_user_permissions(self, obj: User):
        return get_user_permissions_func(obj)

    class Meta:
        fields = [
            'user_roles',
            'permissions'
            'current_organisation_id',
            'current_organisation',
        ]
        model = User
