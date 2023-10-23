# your_app/tests/test_tasks.py
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from property.factories import PropertyFactory
from property.models import Province
from regulatory_permit.models import DataUsePermission
from stakeholder.factories import (
    organisationFactory,
)
from stakeholder.models import (
    Organisation,
    OrganisationUser,
    Reminders
)
from stakeholder.tasks import (
    send_reminder_emails,
    send_reminder_email,
    update_user_profile
)
from stakeholder.tasks import update_property_short_code


class SendReminderEmailsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@gmail.com'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission = self.data_use_permission
        )
        self.organisation_user = OrganisationUser.objects.create(
            organisation=self.organisation,
            user=self.user
        )
        self.user_profile = self.user.user_profile

        # Create a test reminder
        self.reminder = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            status=Reminders.ACTIVE,
            email_sent=False,
            title='Test Reminder',
            reminder='Test reminder content',
            date=timezone.now()
        )

    def test_send_reminder_emails(self):
        # Call the task to send reminder emails
        send_reminder_emails()

        # Check if the reminder was updated
        self.assertEqual(self.reminder.status, Reminders.ACTIVE)
        self.assertEqual(self.reminder.email_sent, False)

    def test_send_reminder_email(self):
        # Call the task to send a single reminder email
        send_reminder_email.apply(args=[self.reminder.id])

        # Check if the reminder email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, f"Reminder: {self.reminder.title}")
        self.assertEqual(email.to, [self.user.email])


    def test_update_user_profile(self):
        # Call the task to send a single reminder email
        update_user_profile(self.user)

        # when email is sent this is updated to false
        self.assertEqual(False, self.user_profile.received_notif)


class TestUpdatePropertyShortCode(TestCase):
    """Update Property Short Code test case."""

    def setUp(self):
        self.province, created = Province.objects.get_or_create(
                    name="Limpopo"
        )
        self.organization = organisationFactory(
            name='CapeNature',
            province=self.province
        )

    def test_update_short_code_from_organisation(self):
        """Test updating property short code when organization is updated."""
        self.assertEqual(
            self.organization.short_code,
            'LICA0001'
        )
        property_1 = PropertyFactory.create(
            organisation=self.organization,
            province=self.province
        )
        property_2 = PropertyFactory.create(
            organisation=self.organization,
            province=self.province
        )
        self.organization.name = 'test'
        self.organization.national = True
        self.organization.province = self.province
        self.organization.save()

        # call task function
        update_property_short_code(self.organization.id)

        property_1.refresh_from_db()
        property_2.refresh_from_db()

        self.assertEqual(
            self.organization.short_code,
            'LITE0002'
        )
        self.assertEqual(
            property_1.short_code,
            'LITEPR0001'
        )
        self.assertEqual(
            property_2.short_code,
            'LITEPR0002'
        )

    def test_update_short_code_from_province(self):
        """
        Test updating property and organisaition short code when provincr is updated.
        """
        province, created = Province.objects.get_or_create(
            name="Western Cape"
        )
        property_1 = PropertyFactory.create(
            organisation=self.organization,
            province=self.province
        )
        property_2 = PropertyFactory.create(
            organisation=self.organization,
            province=self.province
        )
        self.organization.name = 'test'
        self.organization.national = True
        self.organization.province = province
        self.organization.save()

        # call task function
        update_property_short_code(self.organization.id)

        property_1.refresh_from_db()
        property_2.refresh_from_db()

        self.assertEqual(
            self.organization.short_code,
            'WCTE0001'
        )
        self.assertEqual(
            property_1.short_code,
            'LITEPR0001'
        )
        self.assertEqual(
            property_2.short_code,
            'LITEPR0002'
        )

