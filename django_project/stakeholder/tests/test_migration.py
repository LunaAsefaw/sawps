from django.db.models.signals import pre_save, post_save
from django.test import TestCase

from property.models import Province
from sawps.utils import disconnected_signal
from stakeholder.models import (
    Organisation
)
from stakeholder.models import (
    organisation_pre_save,
    organisation_post_save
)
from stakeholder.factories import (
    organisationFactory,
)
from stakeholder.utils import forward_func_0015


class TestOrganisationMigration(TestCase):

    def test_migration_function(self):
        # Disable signal to create organisation without short code
        with disconnected_signal(pre_save, organisation_pre_save, Organisation):
            with disconnected_signal(post_save, organisation_post_save, Organisation):
                province, created = Province.objects.get_or_create(
                    name="Limpopo"
                )
                organization_1 = organisationFactory(
                    name='CapeNature',
                    province=province
                )
                organization_2 = organisationFactory(
                    name='CapeVerde',
                    province=province
                )
                organization_3 = organisationFactory(
                    name='SANS Parks',
                    province=None
                )
                # Check organization short code is empty
                self.assertEqual(organization_1.short_code, '')
                self.assertEqual(organization_2.short_code, '')
                self.assertEqual(organization_3.short_code, '')

        forward_func_0015(Province, Organisation)
        organization_1.refresh_from_db()
        organization_2.refresh_from_db()
        organization_3.refresh_from_db()

        # Check organization short code is now filled.
        self.assertEqual(organization_1.short_code, 'LICA0001')
        self.assertEqual(organization_2.short_code, 'LICA0002')
        self.assertEqual(organization_3.short_code, 'SP0001')
