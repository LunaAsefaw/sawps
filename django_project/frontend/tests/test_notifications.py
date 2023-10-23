from django.test import (
    TestCase,
    RequestFactory
)
from frontend.utils.organisation import CURRENT_ORGANISATION_ID_KEY
from frontend.views.base_view import get_user_notifications
from stakeholder.factories import (
    organisationFactory,
)
from stakeholder.models import (
    Reminders,
    UserProfile
)
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from datetime import datetime
from django.contrib.messages.storage.fallback import FallbackStorage


class GetUserNotificationsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        # Create a test user profile
        self.user_profile = self.user.user_profile
        self.user_profile.received_notif = False
        self.user.save()

        # create organisation
        self.organisation = organisationFactory.create()
        # Create a test reminder
        self.reminder = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            status=Reminders.PASSED,
            email_sent=True,
            date=datetime.now()
        )

    def test_get_user_notifications(self):
        # Simulate a request to the view
        request = RequestFactory().get('get_user_notifications')
        request.user = self.user
        request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation.pk}

        # Add a message storage to the request
        setattr(request, '_messages', FallbackStorage(request))

        # Call the view function
        response = get_user_notifications(request)

        # Check that the view returns a JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Check that the UserProfile received_notif is set to True
        self.assertTrue(UserProfile.objects.get(user=self.user).received_notif)

        messages = list(get_messages(response))
        self.assertTrue(len(messages) == 0)

