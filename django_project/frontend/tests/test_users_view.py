import json

from django.contrib.auth.models import User, Permission
from django.core.serializers.json import DjangoJSONEncoder
from django.test import RequestFactory, TestCase, Client
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.contenttypes.models import ContentType

from frontend.static_mapping import REGIONAL_DATA_CONSUMER
from frontend.views.users import OrganisationUsersView
from regulatory_permit.models import DataUsePermission
from sawps.models import ExtendedGroup
from sawps.tests.models.account_factory import GroupF
from stakeholder.factories import userRoleTypeFactory
from stakeholder.models import (
    Organisation,
    OrganisationInvites,
    OrganisationUser
)


class OrganisationUsersViewTest(TestCase):
    """This covers the testcases on the view functions """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@gmail.com'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test")
        self.organisation = Organisation.objects.create(
            name="test_organisation", data_use_permission=self.data_use_permission)
        self.organisation_user = OrganisationUser.objects.create(
            organisation=self.organisation, user=self.user)
        self.org_invitation = OrganisationInvites.objects.create(
            email=self.user.email,
            organisation=self.organisation
        )
        self.role = userRoleTypeFactory.create(
            id=1,
            name='Admin',
        )
        self.user.user_profile.user_role_type_id = self.role
        self.user.user_profile.current_organisation = self.organisation
        self.user.save()

    def test_delete_post_method(self):
        # url = reverse('Users')
        response = self.client.post(
                '/users/',
                {
                    'action': 'delete',
                    'object_id': self.user.pk,
                    'current_organisation': self.organisation.name
                }
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

        # Verify that the OrganisationUser has been deleted
        self.assertFalse(OrganisationUser.objects.filter(
            user=self.organisation_user.user).exists())

        # test organisation does not exist
        response = self.client.post(
                '/users/',
                {
                    'action': 'delete',
                    'object_id': self.user.pk,
                    'current_organisation': 'fake_org'
                }
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'failed'})

        # test user does not exist
        response = self.client.post(
                '/users/',
                {
                    'action': 'delete',
                    'object_id': 55,
                    'current_organisation': self.organisation.name
                }
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'failed'})


    def test_invite_post(self):
        # Create a request object with the required POST data
        response = self.client.post(
            '/users/',
            {
                'action': 'invite',
                'email': 'test@example.com',
                'inviteAs': 'manager',
                'memberRole': 'write'
            }
        )

        OrganisationInvites.objects.filter(organisation=self.organisation)

        # expected_json = {'status': "'current_organisation_id'"}

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), expected_json)

        # test with read permissions
        response = self.client.post(
            '/users/',
            {
                'action': 'invite',
                'email': 'test@example.com',
                'inviteAs': 'manager',
                'memberRole': 'read'
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_get_organisation_users(self):

        factory = RequestFactory()
        request = factory.post('/users/')
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation.id}

        view = OrganisationUsersView()

        response = view.get_organisation_users(request)

        self.assertIsNotNone(response)

        # test user without an invite
        user = User.objects.create_user(
            username='testuser33',
            password='testpassword',
            email='test33@gmail.com'
        )
        user.user_profile.user_role_type_id = self.role
        user.user_profile.current_organisation = self.organisation
        user.save()

        OrganisationUser.objects.create(
            organisation=self.organisation, user=user
        )

        factory = RequestFactory()
        request = factory.post('/users/')
        request.user = user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation.id}

        view = OrganisationUsersView()

        response = view.get_organisation_users(request)

        self.assertIsNotNone(response)

    def test_get_organisation_invites(self):
        factory = RequestFactory()
        request = factory.post('/users/')
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation.id}

        view = OrganisationUsersView()

        response = view.get_organisation_users(request)

        self.assertIsNotNone(response)


    def test_search_user_table(self):
        # Create a request object with the required POST data
        response = self.client.post(
            '/users/',
            {
                'action': 'search_user_table',
                'query': 'test',
                'current_organisation': self.organisation.name
            }
        )

        # Assert the expected outcome
        expected_data = [
            {
                'organisation': str(self.organisation),
                'user': str(self.user),
                'id': self.user.pk,
                'role': 'Organisation '+self.org_invitation.assigned_as,
                'joined': self.org_invitation.joined
            }
        ]
        expected_json = {'data': json.dumps(expected_data, cls=DjangoJSONEncoder)}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

        # test with = in string
        response = self.client.post(
            '/users/',
            {
                'action': 'search_user_table',
                'query': 'q=test',
                'current_organisation': self.organisation.name
            }
        )

        # Assert the expected outcome
        expected_data = [
            {
                'organisation': str(self.organisation),
                'user': str(self.user),
                'id': self.user.pk,
                'role': 'Organisation '+self.org_invitation.assigned_as,
                'joined': self.org_invitation.joined
            }
        ]
        expected_json = {'data': json.dumps(expected_data, cls=DjangoJSONEncoder)}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

        # search with fake org
        response = self.client.post(
            '/users/',
            {
                'action': 'search_user_table',
                'query': 'q=test',
                'current_organisation': 'fake_org'
            }
        )

        # Assert the expected outcome
        expected_data = []
        expected_json = {'data': json.dumps(expected_data, cls=DjangoJSONEncoder)}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json)

    def test_get_user_by_email(self):

        view = OrganisationUsersView()

        response = view.get_user_email(self.user)

        self.assertEqual(response, self.user.email)

        # test user does not exist
        view = OrganisationUsersView()

        response = view.get_user_email('none')

        self.assertEqual(response, None)

    def test_get_role(self):
        view = OrganisationUsersView()

        response = view.get_role(self.user, self.organisation)

        self.assertEqual(response, None)

        # get role from user profile
        user = User.objects.create_user(
            username='testuser23',
            password='testpassword',
            email='test2@gmail.com'
        )
        user.user_profile.user_role_type_id = self.role
        user.save()

        OrganisationUser.objects.create(
            organisation=self.organisation, user=user
        )

        response = view.get_role(user, self.organisation)

        self.assertEqual(str(response), 'Admin')

    def test_is_new_invitation(self):
        view = OrganisationUsersView()

        response = view.is_new_invitation(self.user.email, self.organisation)

        self.assertEqual(response,True)

        # test with fake email
        response = view.is_new_invitation('me@fake.com',self.organisation)

        self.assertEqual(response, False)

    def test_is_user_registered(self):
        view = OrganisationUsersView()

        response = view.is_user_registerd(self.user.email)

        self.assertEqual(response, True)

        # test none registered user
        response = view.is_user_registerd('new@new.com')

        self.assertEqual(response, False)

    def test_calculate_rows_per_page(self):
        view = OrganisationUsersView()

        response = view.calculate_rows_per_page([])

        self.assertEqual(response,0)

    def test_context_data(self):

        client = Client()
        superuser = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@example.com',
            password='testpassword'
        )

        login = client.login(
            username='testadmin',
            password='testpassword'
        )
        self.assertTrue(login, True)
        device = TOTPDevice(
            user=superuser,
            name='device_name'
        )
        device.save()
        response = client.post('/users/')

        # Check if the response status code is OK (200)
        self.assertEqual(response.status_code, 200)

        # Access the context data from the response
        context_data = response.context

        # no organisation users found
        self.assertEqual(context_data, None)


class UserApiTest(TestCase):

    def test_get_user_info(self):
        """
        Test getting non superuser user info.
        """
        client = Client()
        user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@gmail.com'
        )
        group = GroupF.create(name=REGIONAL_DATA_CONSUMER)
        content_type = ContentType.objects.get_for_model(ExtendedGroup)
        all_permissions = Permission.objects.filter(content_type=content_type)
        group.permissions.add(all_permissions[0])

        user.groups.add(group)
        login = client.login(
            username='testuser',
            password='testpassword'
        )
        self.assertTrue(login, True)
        device = TOTPDevice(
            user=user,
            name='device_name'
        )
        device.save()

        # Test with no organisation
        response = client.get('/api/user-info/')
        self.assertEqual(response.status_code, 200)

        self.assertTrue(REGIONAL_DATA_CONSUMER in response.data['user_roles'])
        data_use_permission = DataUsePermission.objects.create(
            name="test"
        )

        # Test with organisation
        organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=data_use_permission,
            national=True
        )
        user.user_profile.current_organisation = organisation
        user.save()

        response = client.get('/api/user-info/')
        self.assertEqual(response.data['current_organisation_id'], organisation.id)
        self.assertEqual(response.data['current_organisation'], organisation.name)

        # Permission 2 should not be in the user permisions because:
        # - It is not assigned to user's group
        # - It is not allowed for organisation member or manager
        self.assertEqual(
            sorted(response.data['user_permissions']),
            sorted([all_permissions[0].name, 'Can view province report'])
        )

    def test_get_user_info_superuser(self):
        """
        Test getting superuser user info. All permissions should be assigned.
        """
        client = Client()
        user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@gmail.com',
            is_superuser=True
        )
        content_type = ContentType.objects.get_for_model(ExtendedGroup)
        all_permissions = Permission.objects.filter(content_type=content_type)

        login = client.login(
            username='testuser',
            password='testpassword'
        )
        self.assertTrue(login, True)
        device = TOTPDevice(
            user=user,
            name='device_name'
        )
        device.save()

        # Test with no organisation
        response = client.get('/api/user-info/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['user_permissions'],
            sorted(list(all_permissions.values_list('name', flat=True)))
        )
