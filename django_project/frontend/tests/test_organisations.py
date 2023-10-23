from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from regulatory_permit.models import DataUsePermission
from django_otp.plugins.otp_totp.models import TOTPDevice
from stakeholder.models import OrganisationUser, Organisation
from stakeholder.factories import (
    organisationFactory,
    userRoleTypeFactory,
)
from stakeholder.views import OrganisationAPIView
from property.factories import (
    ProvinceFactory
)
from frontend.tests.model_factories import UserF
from frontend.tests.request_factories import OrganisationAPIRequestFactory
from rest_framework import status


class OrganisationsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )
        device = TOTPDevice(
            user=self.user,
            name='device_name'
        )
        device.save()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('organisations', args=[self.user.username])

    def test_organisations_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'organisations.html')
        self.assertIn('organisations', response.context)


    def test_switch_organisation_with_none_organisation_user(self):
        # Login as the regular user
        self.client.login(username='testuser', password='testpassword')

        # Switch to the organisation
        response = self.client.get(
            reverse(
                'switch-organisation',
                args=[self.organisation.id]
                )
            )

        # Assert that the response is a redirect to the homepage
        self.assertEqual(response.status_code, 403)

    def test_switch_organisation_with_organisation_user(self):
        OrganisationUser.objects.create(
            organisation=self.organisation,
            user=self.user
        )
        # Login as the regular user
        self.client.login(username='testuser', password='testpassword')

        # Attempt to switch to the organisation
        response = self.client.get(
            reverse(
                'switch-organisation',
                args=[self.organisation.id]
                )
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def tearDown(self):
        self.client.logout()


class TestOrganisationAPIView(TestCase):
    def setUp(self) -> None:
        self.province = ProvinceFactory.create()

        #creat organisation
        self.organisation_1 = organisationFactory.create(
            national=False,
            province=self.province
        )
        self.organisation_2 = organisationFactory.create(national=True)

        # create user
        self.user_1 = UserF.create(username='test_1')
        self.user_2 = UserF.create(username='test_2')

    def test_organisation_list(self):
        """Test organisation for regional user"""

        factory = OrganisationAPIRequestFactory(self.organisation_1)
        user_role = userRoleTypeFactory.create(
            name='Regional data scientist'
        )
        self.user_1.user_profile.current_organisation = self.organisation_1
        self.user_1.user_profile.user_role_type_id = user_role
        self.user_1.save()

        request = factory.get(
            reverse('organisation')
        )
        request.user = self.user_1
        view = OrganisationAPIView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        _organisation = response.data[0]
        self.assertEqual(_organisation['id'], self.organisation_1.id)
        self.assertEqual(_organisation['name'], self.organisation_1.name)

    def test_organisation_list_for_national(self):
        """Test organisation for regional user"""

        factory = OrganisationAPIRequestFactory(self.organisation_2)
        user_role = userRoleTypeFactory.create(
            name='National data scientist'
        )
        self.user_1.user_profile.current_organisation = self.organisation_2
        self.user_1.user_profile.user_role_type_id = user_role
        self.user_1.save()

        request = factory.get(
            reverse('organisation')
        )
        request.user = self.user_1
        view = OrganisationAPIView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class OrganisationTests(TestCase):

    def setUp(self):
        self.organisation = organisationFactory.create(
            name="Test Organisation"
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        device = TOTPDevice(
            user=self.user,
            name='device_name'
        )
        device.save()
        self.client.login(username='testuser', password='testpassword')

    def test_save_permissions_valid_request(self):
        data = {
            'only_sanbi': 'true',
            'hosting_data_sanbi': 'false',
            'hosting_data_sanbi_other': 'true',
        }
        url = reverse('save_permissions', args=[self.organisation.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organisation.refresh_from_db()
        self.assertTrue(self.organisation.use_of_data_by_sanbi_only)
        self.assertFalse(self.organisation.hosting_through_sanbi_platforms)
        self.assertTrue(self.organisation.allowing_sanbi_to_expose_data)

    def test_save_permissions_invalid_request(self):
        data = {}  # Invalid request with missing data
        url = reverse('save_permissions', args=[self.organisation.id])
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_permissions_organisation_not_found(self):
        data = {
            'only_sanbi': 'true',
            'hosting_data_sanbi': 'false',
            'hosting_data_sanbi_other': 'true',
        }
        invalid_org_id = self.organisation.id + 1  # Non-existent ID
        url = reverse('save_permissions', args=[invalid_org_id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_organization_detail_valid(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('organization_detail_by_id', args=[self.organisation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Test Organisation')

    def test_organization_detail_invalid(self):
        self.client.login(username='testuser', password='testpassword')
        invalid_org_id = self.organisation.id + 1  # Non-existent ID
        url = reverse('organization_detail_by_id', args=[invalid_org_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

