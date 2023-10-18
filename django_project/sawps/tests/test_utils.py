from django.test import TestCase
from django.db.models.signals import post_save
import logging
from sawps.utils import (
    disconnected_signal
)
from stakeholder.models import Reminders

logger = logging.getLogger('test')


def dummy_signal_handler(sender, **kwargs):
    logger.info("Signal received.")


class TestUtils(TestCase):
    """Test utilities."""

    def setUp(self):
        post_save.connect(dummy_signal_handler, sender=Reminders)

    def test_signal(self):
        with self.assertLogs(logger) as log:
            Reminders.objects.create(title="Test")

        self.assertIn("Signal received.",
                         [record.msg for record in log.records])

    def test_temporary_disconnect_signal(self):
        with disconnected_signal(post_save, dummy_signal_handler, Reminders):
            Reminders.objects.create(title="Test")

        self.assertNoLogs(logger)

