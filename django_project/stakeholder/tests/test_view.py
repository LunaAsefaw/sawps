from django.http import JsonResponse
from django.test import (
    TestCase,
    Client,
    RequestFactory
)
from django.utils import timezone
from stakeholder.views import (
    adjust_date_to_server_time,
    convert_date_to_local_time,
    convert_reminder_dates,
    paginate,
    search_reminders_or_notifications,
    delete_reminder_and_notification,
    get_reminder_or_notification,
    get_organisation_reminders
)
from stakeholder.models import (
    Organisation,
    OrganisationUser
)
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from stakeholder.views import RemindersView,NotificationsView
from regulatory_permit.models import DataUsePermission
import json
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from unittest.mock import patch
from stakeholder.models import Reminders


class TestDateTimeConversion(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_adjust_date_to_server_time(self):

        # Create a request factory
        factory = RequestFactory()

        # Define the input date string and timezone value
        date_str = '2023-07-21T16:17'
        timezone_value = 'Africa/Johannesburg'

        # Create a fake POST request with the required data
        url = reverse('reminders', kwargs={'slug': self.user.username})
        request = factory.post(url, data={
            'date': date_str,
            'timezone': timezone_value,
        })

        # Call the function and get the result
        server_datetime = adjust_date_to_server_time(request)

        # Check if the result is a datetime object
        self.assertIsInstance(server_datetime, datetime)

    def test_convert_date_to_local_time(self):
        # Create a sample datetime object in the server's timezone (UTC)
        server_datetime = timezone.now()

        # Call the function and get the result
        local_datetime_str = convert_date_to_local_time(
            server_datetime, 'Africa/Johannesburg')

        # Check if the result is a string
        self.assertIsInstance(local_datetime_str, str)

        # Convert the string back to a datetime object
        datetime_format = "%Y-%m-%d %I:%M %p"
        local_datetime = datetime.strptime(local_datetime_str, datetime_format)
        self.assertTrue(isinstance(local_datetime, datetime))


class TestConvertReminderDates(TestCase):
    def test_convert_reminder_dates(self):
        # Create a sample reminder list with dates in the server's timezone (UTC)
        server_timezone = timezone.get_current_timezone()
        reminders = [
            Reminders(
                title='Reminder 1',
                date=datetime(2023, 7, 21, 12, 30, tzinfo=server_timezone),
                timezone='Africa/Johannesburg'
            ),
            Reminders(
                title='Reminder 2',
                date=datetime(2023, 8, 15, 16, 45, tzinfo=server_timezone),
                timezone='Africa/Johannesburg'
            ),
            Reminders(
                title='Reminder 3',
                date=datetime(2023, 9, 5, 9, 0, tzinfo=server_timezone),
                timezone='Africa/Johannesburg'
            ),
        ]

        # Call the function to convert the dates to the local timezone
        converted_reminders = convert_reminder_dates(reminders)

        # Check if the converted_reminders list contains the correct number of reminders
        self.assertEqual(len(converted_reminders), len(reminders))


class DeleteReminderAndNotificationTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123454$',
            email='email@gamil.com'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission=self.data_use_permission
        )
        self.user.user_profile.current_organisation = self.organisation
        self.user.save()

        self.client = Client()
        self.reminder_1 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 1',
            reminder='First reminder',
            status=Reminders.PASSED,
            email_sent=True,
        )
        self.reminder_2 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 2',
            reminder='Second reminder',
            status=Reminders.ACTIVE,
            email_sent=False,
        )
        self.factory = RequestFactory()

    def test_delete_single_reminder(self):
        reminders_before_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation)
        self.assertEqual(reminders_before_delete.count(), 2)

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_reminder',
            'ids': json.dumps([self.reminder_1.pk]),
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = delete_reminder_and_notification(request)

        reminders_after_delete = Reminders.objects.filter(
            user=self.user,
            organisation=self.organisation)
        self.assertEqual(reminders_after_delete.count(), 2)

        self.assertEqual(len(results), 2)
        # Return the remaining Reminder
        self.assertEqual(results[0].title, 'Reminder 1')

    def test_delete_multiple_reminders(self):
        reminders_before_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation)
        self.assertEqual(reminders_before_delete.count(), 2)

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_reminder',
            'ids': json.dumps([self.reminder_1.id, self.reminder_2.id]),
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }

        request = self.factory.post(
            url,
            data=data
        )
        request.user = self.user
        view = RemindersView.as_view()
        results = view(request)

        reminders_after_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation)
        self.assertEqual(reminders_after_delete.count(), 2)

        self.assertIsNotNone(results)

    def test_delete_invalid_reminder(self):
        reminders_before_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation)
        self.assertEqual(reminders_before_delete.count(), 2)

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_reminder',
            'ids': json.dumps([999]),
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = delete_reminder_and_notification(request)

        reminders_after_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation)
        self.assertEqual(reminders_after_delete.count(), 2)

        self.assertEqual(len(results), 2)

    def test_delete_notification(self):
        reminders_before_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation
        )
        self.assertEqual(reminders_before_delete.count(), 2)

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_notification',
            'notifications_page': True,
            'ids': json.dumps([self.reminder_1.pk]),
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = delete_reminder_and_notification(request)

        reminders_after_delete = Reminders.objects.filter(
            user=self.user, organisation=self.organisation
        )
        self.assertEqual(reminders_after_delete.count(), 2)

        # Convert the queryset to a list
        if isinstance(results, QuerySet):
            results = list(results)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Reminder 1')

    def test_delete_reminder_and_notification_invalid_ids(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_notification',
            'notifications_page': True,
            'ids': json.dumps(['999']),
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        result = delete_reminder_and_notification(request)

        self.assertEqual(result, 'Reminders matching query does not exist.')



class TestPaginateFunction(TestCase):
    def setUp(self):
        # Create sample data for pagination
        self.rows = [f"Item {i}" for i in range(1, 101)]

    def test_paginate_first_page(self):
        # Test pagination for the first page (page=1) with 10 rows per page
        rows_per_page = 10
        page = 1

        paginated_rows = paginate(self.rows, rows_per_page, page)

        # Check the paginated_rows object
        self.assertTrue(paginated_rows.has_next())
        self.assertFalse(paginated_rows.has_previous())
        self.assertEqual(paginated_rows.number, page)
        self.assertEqual(len(paginated_rows), rows_per_page)
        self.assertEqual(paginated_rows[0], "Item 1")
        self.assertEqual(paginated_rows[-1], "Item 10")

    def test_paginate_last_page(self):
        # Test pagination for the last page (page=10) with 10 rows per page
        rows_per_page = 10
        page = 10

        paginated_rows = paginate(self.rows, rows_per_page, page)

        # Check the paginated_rows object
        self.assertFalse(paginated_rows.has_next())
        self.assertTrue(paginated_rows.has_previous())
        self.assertEqual(paginated_rows.number, page)
        self.assertEqual(len(paginated_rows), rows_per_page)
        self.assertEqual(paginated_rows[0], "Item 91")
        self.assertEqual(paginated_rows[-1], "Item 100")

    def test_paginate_invalid_page(self):
        # Test pagination with an invalid page value (page='invalid')
        rows_per_page = 10
        page = 'invalid'

        paginated_rows = paginate(self.rows, rows_per_page, page)

        # Check the paginated_rows object
        self.assertTrue(paginated_rows.has_next())
        self.assertFalse(paginated_rows.has_previous())
        # The page defaults to 1 for invalid input
        self.assertEqual(paginated_rows.number, 1)
        self.assertEqual(len(paginated_rows), rows_per_page)
        self.assertEqual(paginated_rows[0], "Item 1")
        self.assertEqual(paginated_rows[-1], "Item 10")

    def test_paginate_empty_page(self):
        # Test pagination for an empty page (page=11) with 10 rows per page
        rows_per_page = 60
        page = 2

        paginated_rows = paginate(self.rows, rows_per_page, page)

        # Check the paginated_rows object
        self.assertFalse(paginated_rows.has_next())
        self.assertTrue(paginated_rows.has_previous())




class TestAddReminderAndScheduleTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
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
        self.user.user_profile.current_organisation = (
            self.organisation
        )
        self.user.save()
        self.reminder = Reminders.objects.create(
            title='Test Reminder',
            user=self.user,
            organisation=self.organisation,
            reminder='Test Reminder Note'
        )

    def test_add_reminder_and_schedule_task_success(self):
        # Test the success case for adding a reminder and scheduling a task
        url = reverse('reminders', kwargs={'slug': self.user.username})
        date_str = (timezone.now() + timedelta(days=1)
                    ).strftime('%Y-%m-%dT%H:%M')

        data = {
            'action': 'add_reminder',
            'title': 'Test Reminder',
            'reminder': 'Test Reminder Note',
            'date': date_str,
            'timezone': 'Africa/Johannesburg',
            'reminder_type': 'personal',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }

        self.factory = RequestFactory()
        request = self.factory.post(url, data)
        request.user = self.user

        view = RemindersView()

        response = view.add_reminder_and_schedule_task(request)

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)

        # Check that the reminder was added to the database and task was scheduled
        reminders = Reminders.objects.filter(user=self.user)
        self.assertEqual(reminders.count(), 2)
        reminder = reminders.first()
        self.assertEqual(reminder.title, 'Test Reminder')
        self.assertEqual(reminder.reminder, 'Test Reminder Note')

        data = {
            'action': 'add_reminder',
            'title': 'Test Reminder2',
            'reminder': 'Test Reminder Note2',
            'date': date_str,
            'timezone': 'Africa/Johannesburg',
            'reminder_type': 'everyone',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }

        self.factory = RequestFactory()
        request = self.factory.post(url, data)
        request.user = self.user

        view = RemindersView()

        response = view.add_reminder_and_schedule_task(request)

        # Check the response status code
        self.assertEqual(response.status_code, 200)
        # Check that the reminder was added to the database
        reminders = Reminders.objects.filter(user=self.user)
        self.assertEqual(reminders.count(), 3)
        reminder = Reminders.objects.filter(
            user=self.user,
            title='Test Reminder2'
        ).first()
        self.assertEqual(reminder.title, 'Test Reminder2')
        self.assertEqual(reminder.reminder, 'Test Reminder Note2')



class TestRemindersView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123454$',
            email='email@gamil.com'
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
        self.user.user_profile.current_organisation = (
            self.organisation
        )
        self.user.save()
        self.reminder = Reminders.objects.create(
            title='Test Reminder',
            user=self.user,
            organisation=self.organisation,
            reminder='Test Reminder Note'
        )
        self.client = Client()
        self.factory = RequestFactory()

    def test_get_reminders(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminders',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        self.factory = RequestFactory()
        request = self.factory.post(url, data)
        request.user = self.user

        view = RemindersView()

        response = view.get_reminders(request)

        rows_per_page = 1
        page = 1
        rows = [f"Item {i}" for i in range(1, 2)]

        paginated_rows = paginate(rows, rows_per_page, page)

        #response should contain a page
        self.assertEqual(str(response), str(paginated_rows))

    def test_dispatch_get_reminders(self):
        # Test the 'get_reminders' action of dispatch
        self.client.login(username='testuser', password='testpassword123454$')
        url = reverse('reminders', kwargs={'slug': 'testuser'})
        data = {
            'action': 'get_reminders',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
        }

        request = self.factory.post(
            url,
            data=data
        )

        request.user = self.user
        view = RemindersView.as_view()
        response = view(request)
        self.assertEqual(len(response), 1)

    def test_dispatch_add_reminder(self):
        self.client.login(username='testuser', password='testpassword123454$')
        url = reverse('reminders', kwargs={'slug': self.user.username})
        date_str = (timezone.now() + timedelta(days=1)
                    ).strftime('%Y-%m-%dT%H:%M')

        request = self.factory.post(
            url,
            {
                'action': 'add_reminder',
                'title': 'Test Reminder',
                'reminder': 'Test Reminder Note',
                'date': date_str,
                'timezone': 'Africa/Johannesburg',
                'reminder_type': 'personal',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
            }
        )

        request.user = self.user
        view = RemindersView.as_view()
        response = view(request)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['status'], 'success')

        updated_reminders = response_data['updated_reminders']
        self.assertIsInstance(updated_reminders, list)
        self.assertEqual(len(updated_reminders), 2)

    def test_get_context_data(self):
        # Test the 'get_context_data' method
        logged_in = self.client.login(
            username=self.user.username,
            password='testpassword123454$'
        )
        self.assertTrue(logged_in)
        url = reverse('reminders', kwargs={'slug': self.user.username})

        response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)

        view = RemindersView()
        view.setup(request=response.wsgi_request)

        reminders = []
        view.get_reminders = lambda request: reminders

        context = view.get_context_data()

        # Check the context variables
        self.assertIn('reminders', context)
        self.assertEqual(context['reminders'], reminders)


    def test_edit_reminder(self):
        # Create a test reminder
        reminder = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Test Reminder',
            date='2023-07-25 12:00',
            type=Reminders.PERSONAL,
            status=Reminders.ACTIVE,
            reminder='Test Reminder Note',
            email_sent=False
        )

        # Simulate a POST request to edit the reminder
        date_str = '2023-07-26T13:00'
        self.client.login(username='testuser', password='testpassword123454$')
        url = reverse('reminders', kwargs={'slug': self.user.username})
        ids_json = json.dumps([str(reminder.id)])
        request = self.factory.post(
            url,
            {
                'action': 'edit_reminder',
                'ids': ids_json,
                'title': 'Updated Reminder',
                'status': 'draft',
                'date': date_str,
                'timezone': 'Africa/Johannesburg',
                'reminder_type': 'personal',
                'reminder': 'Updated Reminder Note',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
            }
        )

        request.user = self.user
        view = RemindersView.as_view()
        response = view(request)
        response_data = json.loads(response.content.decode('utf-8'))
        updated_reminders = response_data['data']
        self.assertIsInstance(updated_reminders, list)
        self.assertEqual(len(updated_reminders), 2)
        if updated_reminders[1].get('status') == reminder.id:
            self.assertEqual(updated_reminders[1].get('status'),Reminders.DRAFT)

        # test with status passed and everyone
        request = self.factory.post(
            url,
            {
                'action': 'edit_reminder',
                'ids': ids_json,
                'title': 'Updated Reminder',
                'status': 'passed',
                'date': date_str,
                'timezone': 'Africa/Johannesburg',
                'reminder_type': 'everyone',
                'reminder': 'Updated Reminder Note',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
            }
        )
        request.user = self.user
        view = RemindersView.as_view()
        response = view(request)
        response_data = json.loads(response.content.decode('utf-8'))
        updated_reminders = response_data['data']
        self.assertIsInstance(updated_reminders, list)
        self.assertEqual(len(updated_reminders), 2)
        if updated_reminders[1].get('status') == reminder.id:
            self.assertEqual(updated_reminders[1].get('status'),Reminders.PASSED)

        # test with status active status and fail test
        request = self.factory.post(
            url,
            {
                'action': 'edit_reminder',
                'ids': [reminder.id],
                'title': 'Updated Reminder',
                'status': 'active',
                'date': date_str,
                'timezone': 'Africa/Johannesburg',
                'reminder_type': 'everyone',
                'reminder': 'Updated Reminder Note',
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
            }
        )
        response = view(request)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['status'],'errors')


class SearchRemindersOrNotificationsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123454$',
            email='email@gamil.com'
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission = self.data_use_permission
        )
        self.user.user_profile.current_organisation = (
            self.organisation
        )
        self.user.save()
        self.client = Client()
        self.reminder_1 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 1',
            reminder='First reminder',
            status=Reminders.PASSED,
            email_sent=True,
        )
        self.reminder_2 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 2',
            reminder='Second reminder',
            status=Reminders.ACTIVE,
            email_sent=False,
        )
        self.factory = RequestFactory()

    def test_search_by_title(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_reminders',
            'query': 'Reminder 1',
            'filter': 'title',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = search_reminders_or_notifications(request)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Reminder 1')

    def test_search_by_reminder(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_reminders',
            'query': 'Re',
            'filter': 'reminder',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = search_reminders_or_notifications(request)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, 'Reminder 1')

    def test_search_without_filter(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_reminders',
            'query': 'Remi',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = search_reminders_or_notifications(request)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, 'Reminder 1')
        self.assertEqual(results[1].title, 'Reminder 2')

    def test_notifications_page(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_reminders',
            'query': 'Reminder 1',
            'filter': 'reminder',
            'notifications_page': True,
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        results = search_reminders_or_notifications(request)

        # notifications is empty
        self.assertEqual(len(results), 0)



class GetReminderOrNotificationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission = self.data_use_permission
        )
        self.client = Client()
        self.reminder_1 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 1',
            reminder='First reminder',
            status=Reminders.PASSED,
            email_sent=True,
        )

    def test_get_reminder_or_notification_valid_ids(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminder',
            'ids': [str(self.reminder_1.id)],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        result = get_reminder_or_notification(request)

        self.assertTrue(len(result) > 0)

    def test_get_reminder_or_notification_invalid_ids(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminder',
            'ids': ['999'],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user

        result = get_reminder_or_notification(request)

        self.assertEqual(result, "'int' object is not iterable")


class GetOrganisationRemindersTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission = self.data_use_permission
        )
        self.user.user_profile.current_organisation = (
            self.organisation
        )
        self.user.save()
        self.client = Client()
        self.reminder_1 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 1',
            reminder='First reminder',
            status=Reminders.PASSED,
            email_sent=True,
        )
        self.reminder_2 = Reminders.objects.create(
            user=self.user,
            organisation=self.organisation,
            title='Reminder 2',
            reminder='First reminders',
            status=Reminders.PASSED,
            email_sent=True,
        )

    def test_get_organisation_reminders(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminders',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user

        result = get_organisation_reminders(request)

        # Check that the result contains both reminders for the given organization
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, 'Reminder 1')
        self.assertEqual(result[1].title, 'Reminder 2')
        # Add more assertions as needed for other fields

    def test_get_organisation_reminders_empty(self):
        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminders',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user
        # request.session = {
        #     CURRENT_ORGANISATION_ID_KEY: self.organisation.id + 1}

        result = get_organisation_reminders(request)

        # Check that the result is contains only reminders created
        self.assertEqual(len(result), 2)



class RemindersViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
        )
        self.data_use_permission = DataUsePermission.objects.create(
            name="test"
        )
        self.organisation = Organisation.objects.create(
            name="test_organisation",
            data_use_permission = self.data_use_permission
        )
        self.reminder1 = Reminders.objects.create(
            user=self.user,
            organisation_id=self.organisation.id,
            title='Reminder 1',
        )
        self.reminder2 = Reminders.objects.create(
            user=self.user,
            organisation_id=self.organisation.id,
            title='Reminder 2',
        )

    @patch('stakeholder.views.search_reminders_or_notifications')
    @patch('stakeholder.views.convert_reminder_dates')
    @patch('frontend.serializers.stakeholder.ReminderSerializer')
    def test_search_reminders(
        self,
        mock_serializer,
        mock_convert_dates,
        mock_search_reminders):
        # Configure the mock search_reminders_or_notifications
        mock_search_reminders.return_value = [self.reminder1, self.reminder2]

        # Configure the mock ReminderSerializer
        expected_serialized_data = [
            {'id': self.reminder1.id, 'title': self.reminder1.title},
            {'id': self.reminder2.id, 'title': self.reminder2.title},
        ]
        mock_serializer.return_value.data = expected_serialized_data

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_reminders',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user

        # Instantiate the RemindersView and call the search_reminders method
        view = RemindersView()
        response = view.search_reminders(request)

        # Check that the function returns a JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Check that the mock functions were called with the correct arguments
        mock_convert_dates.assert_called_once_with(
            [self.reminder1, self.reminder2])

    @patch('stakeholder.views.search_reminders_or_notifications')
    def test_search_reminders_error(self, mock_search_reminders):
        # return error
        error_message = 'Invalid search query'
        mock_search_reminders.return_value = error_message

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_reminders',
            'query': 5,
            'filter': 'filter',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user

        # Instantiate the RemindersView
        view = RemindersView()
        response = view.search_reminders(request)

        self.assertIsInstance(response, JsonResponse)

    @patch('stakeholder.views.delete_reminder_and_notification')
    @patch('stakeholder.views.convert_reminder_dates')
    @patch('frontend.serializers.stakeholder.ReminderSerializer')
    def test_delete_reminder(self, mock_serializer, mock_convert_dates, mock_delete_reminder):
        mock_delete_reminder.return_value = [self.reminder1, self.reminder2]

        expected_serialized_data = [
            {'id': self.reminder1.id, 'title': self.reminder1.title},
            {'id': self.reminder2.id, 'title': self.reminder2.title},
        ]
        mock_serializer.return_value.data = expected_serialized_data

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_reminder',
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user

        view = RemindersView()
        response = view.delete_reminder(request)

        self.assertIsInstance(response, JsonResponse)

        mock_convert_dates.assert_called_once_with(
            [self.reminder1, self.reminder2])

    @patch('stakeholder.views.get_reminder_or_notification')
    @patch('stakeholder.views.convert_reminder_dates')
    def test_get_reminder_success(self, mock_serializer, mock_convert_dates):

        expected_serialized_data = [
            {'id': self.reminder1.id, 'title': self.reminder1.title},
        ]
        mock_serializer.return_value.data = expected_serialized_data

        url = reverse('reminders', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_reminder',
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user

        view = RemindersView()
        response = view.get_reminder(request)

        self.assertIsInstance(response, JsonResponse)


class NotificationsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123454$',
            email='email@gamil.com'
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
        self.user.user_profile.current_organisation = (
            self.organisation
        )
        self.user.save()
        self.reminder1 = Reminders.objects.create(
            title='Test Reminder 1',
            user=self.user,
            organisation=self.organisation,
            reminder='Test Reminder Note',
            email_sent=True,
            status=Reminders.PASSED
        )
        self.reminder2 = Reminders.objects.create(
            title='Test Reminder 2',
            user=self.user,
            organisation=self.organisation,
            reminder='Test Reminder Note'
        )
        self.client = Client()


    def test_get_notifications(self):

        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.get(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        # Instantiate the RemindersView and call the get notifications
        view = NotificationsView()
        response = view.get_notifications(request)

        self.assertIsNotNone(response)


    @patch('stakeholder.views.get_reminder_or_notification')
    @patch('stakeholder.views.convert_reminder_dates')
    @patch('frontend.serializers.stakeholder.ReminderSerializer')
    def test_get_notification(
        self,
        mock_reminder,
        mock_convert_dates,
        mock_reminders_serializer):
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_notification',
            'ids': [json.dumps(self.reminder1.pk)],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', '')
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        view = NotificationsView()
        response = view.get_notification(request)

        self.assertIsNotNone(response)

    @patch('stakeholder.views.search_reminders_or_notifications')
    @patch('stakeholder.views.convert_reminder_dates')
    @patch('frontend.serializers.stakeholder.ReminderSerializer')
    def test_search_notifications(
        self,
        mock_reminder,
        mock_convert_dates,
        mock_reminders_serializer):
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_notifications',
            'query': 'Remin',
            'notifications_page': True,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        view = NotificationsView()
        response = view.search_notifications(request)

        self.assertIsNotNone(response)

    @patch('stakeholder.views.delete_reminder_and_notification')
    @patch('stakeholder.views.convert_reminder_dates')
    @patch('frontend.serializers.stakeholder.ReminderSerializer')
    def test_delete_notification(
        self,
        mock_reminder,
        mock_convert_dates,
        mock_reminders_serializer):
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_notification',
            'notifications_page': True,
            'ids': [json.dumps(self.reminder1.pk)],
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        view = NotificationsView()
        response = view.delete_notification(request)

        self.assertIsNotNone(response)

    def test_dispatch_get_notification(self):
        # Simulate a POST request with action 'get_notification'
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'get_notification',
            'notifications_page': True,
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}
        view = NotificationsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_dispatch_search_notifications(self):
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'search_notifications',
            'query': 'i',
            'notifications_page': True,
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        view = NotificationsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_dispatch_delete_notification(self):
        # Simulate a POST request with action 'delete_notification'
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'delete_notification',
            'notifications_page': True,
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
        }
        request = self.factory.post(url, data)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        # Create an instance of the NotificationsView and call the dispatch method
        view = NotificationsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_dispatch_default_action(self):
        # Simulate a POST request with an invalid action
        url = reverse('notifications', kwargs={'slug': self.user.username})
        data = {
            'action': 'invalid_action',
            'ids': [self.reminder1.id],
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken', ''),
        }
        request = self.factory.post(url, data)
        request.user = self.user

        view = NotificationsView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 405)

    def test_get_context_data(self):
        # Simulate a GET request to the notifications view
        url = reverse('notifications', kwargs={'slug': self.user.username})
        request = self.factory.get(url)
        request.user = self.user
        # request.session = {CURRENT_ORGANISATION_ID_KEY: self.organisation}

        view = NotificationsView.as_view()
        response = view(request)

        self.assertIn('notifications', response.context_data)

