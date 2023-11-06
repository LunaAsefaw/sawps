import datetime
from django.test import TestCase
from frontend.models.map_session import MapSession
from frontend.tasks.map_session import clear_expired_map_session
from frontend.tests.model_factories import UserF


class TestMapSession(TestCase):

    def test_clear_expired(self):
        user_1 = UserF.create(username='test_1')
        MapSession.objects.create(
            user=user_1,
            created_date=datetime.datetime(2000, 8, 14, 8, 8, 8),
            expired_date=datetime.datetime(2000, 8, 14, 8, 8, 8)
        )
        clear_expired_map_session()
        self.assertFalse(MapSession.objects.exists())
