from django.conf import settings
from django.template import Context, Template
from django.test import TestCase
from django.contrib.auth.models import User

from stakeholder.factories import (
    organisationFactory
)
from stakeholder.models import OrganisationInvites, MANAGER
from frontend.templatetags.custom_tags import is_organisation_manager


class SentryDsnTagTestCase(TestCase):

    def render_template(self, string, context=None):
        """Helper method to render templates"""
        context = context or {}
        t = Template(string)
        return t.render(Context(context))

    def test_sentry_dsn_template_tag(self):
        with self.settings(SENTRY_DSN="https://example.com/dsn"):
            rendered = self.render_template("{% load custom_tags %}{% sentry_dsn %}")
            self.assertEqual(rendered, "https://example.com/dsn")

        delattr(settings, "SENTRY_DSN")
        rendered = self.render_template("{% load custom_tags %}{% sentry_dsn %}")
        self.assertEqual(rendered, "")


class IsOrganisationManagerTest(TestCase):

    def setUp(self):
        # Creating test user
        self.user = User.objects.create_user(
            username='test',
            email='testuser@example.com',
            password='testpass123'
        )

        # Creating test organisation
        self.organisation = organisationFactory.create(
            name='Test Organisation'
        )

    def test_non_existent_user(self):
        self.assertFalse(is_organisation_manager(999, self.organisation.id))

    def test_non_existent_organisation(self):
        self.assertFalse(is_organisation_manager(self.user.id, 999))

    def test_superuser_is_manager(self):
        # Making user superuser
        self.user.is_superuser = True
        self.user.save()

        self.assertTrue(is_organisation_manager(self.user.id, self.organisation.id))

    def test_normal_user_is_not_manager(self):
        self.assertFalse(is_organisation_manager(self.user.id, self.organisation.id))

    def test_user_invited_as_manager(self):
        # Adding user to organisation invites
        OrganisationInvites.objects.create(
            email=self.user.email,
            organisation=self.organisation,
            assigned_as=MANAGER
        )

        self.assertTrue(
            is_organisation_manager(
                self.user.id, self.organisation.id))
