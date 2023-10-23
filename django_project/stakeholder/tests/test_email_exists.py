from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from stakeholder.views import check_email_exists
from django.contrib.auth import get_user_model

class CheckEmailExistsViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.factory = RequestFactory()

    def test_email_exists(self):
        url = reverse('check_email_exists')
        data = {
            'email': 'test@gmail.com',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }

        request = self.factory.get(url, data)
        request.user = self.user

        results = check_email_exists(request)
        self.assertEqual(results.status_code, 200)

        expected_data = {'exists': False}
        self.assertJSONEqual(results.content, expected_data)

    def test_same_email_as_current_user(self):
        url = reverse('check_email_exists')
        data = {
            'email': self.user.email,
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }

        request = self.factory.get(url, data)
        request.user = self.user

        results = check_email_exists(request)
        self.assertEqual(results.status_code, 200)

        expected_data = {'exists': False}
        self.assertJSONEqual(results.content, expected_data)
