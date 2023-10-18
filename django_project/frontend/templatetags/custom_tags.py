from django import template
from django.conf import settings
from django.contrib.auth.models import User
from frontend.utils.user_roles import (
    is_organisation_manager as is_organisation_manager_util
)
from stakeholder.models import Organisation

register = template.Library()


@register.simple_tag
def sentry_dsn():
    return getattr(settings, "SENTRY_DSN", "")


@register.simple_tag
def is_organisation_manager(user_id: int, organisation_id: int) -> bool:
    """
    Determines if a user is a manager of a specified organisation.

    :param user_id: The ID of the user to check.
    :param organisation_id: The ID of the organisation to verify against.
    :return: True if the user is a manager of the organisation
    """
    try:
        user = User.objects.get(
            id=user_id
        )
    except User.DoesNotExist:
        return False

    if user.is_superuser:
        return True

    try:
        organisation = Organisation.objects.get(
            id=organisation_id
        )
    except Organisation.DoesNotExist:
        return False

    return is_organisation_manager_util(
        user,
        organisation
    )
