from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.test import TestCase

from frontend.static_mapping import REGIONAL_DATA_CONSUMER, SUPER_USER, ORGANISATION_MEMBER, ORGANISATION_MANAGER
from frontend.utils.user_roles import get_user_roles
from regulatory_permit.models import DataUsePermission
from stakeholder.models import (
    Organisation,
    OrganisationUser,
    OrganisationInvites, MANAGER, create_user_profile, save_user_profile
)
from sawps.tests.models.account_factory import GroupF


class TestUserRoles(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuserd',
            password='testpasswordd',
            email='test@email.com',
            is_superuser=True
        )
        self.group = GroupF.create(name=REGIONAL_DATA_CONSUMER)
        self.user.groups.add(self.group)

        self.data_use_permission = DataUsePermission.objects.create(
            name="test")
        self.organisation = Organisation.objects.create(
            name="test_organisation", data_use_permission=self.data_use_permission)

    def test_get_user_roles(self):
        user_roles = get_user_roles(self.user)
        self.assertTrue(SUPER_USER in user_roles)
        self.assertTrue(REGIONAL_DATA_CONSUMER in user_roles)

    def test_get_user_roles_as_organisation_member(self):
        OrganisationUser.objects.create(
            user=self.user,
            organisation=self.organisation
        )
        self.user.user_profile.current_organisation = self.organisation
        self.user.save()
        user_roles = get_user_roles(self.user)
        self.assertTrue(ORGANISATION_MEMBER in user_roles)

    def test_get_user_roles_as_organisation_manager(self):
        OrganisationInvites.objects.create(
            email=self.user.email,
            organisation=self.organisation,
            assigned_as=MANAGER
        )
        self.user.user_profile.current_organisation = self.organisation
        self.user.save()
        user_roles = get_user_roles(self.user)
        self.assertTrue(ORGANISATION_MANAGER in user_roles)

    def test_get_user_roles_without_user_profile(self):
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)
        user = User.objects.create(username='test999')
        user_roles = get_user_roles(user)
        self.assertTrue(ORGANISATION_MEMBER not in user_roles)
        post_save.connect(create_user_profile, sender=User)
        post_save.connect(save_user_profile, sender=User)
