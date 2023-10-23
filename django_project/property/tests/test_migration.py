from django.db.models.signals import pre_save, post_save
from django.test import TestCase

from property.models import Province, Property
from property.models import (
    property_pre_save,
    property_post_save
)
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
from property.utils import forward_func_0007
from property.factories import PropertyFactory


class TestPropertyMigration(TestCase):

    def test_migration_function(self):
        # Disable signal to create organisation and property without short code
        with disconnected_signal(pre_save, organisation_pre_save, Organisation):
            with disconnected_signal(post_save, organisation_post_save, Organisation):
                with disconnected_signal(pre_save, property_pre_save, Property):
                    with disconnected_signal(post_save, property_post_save, Property):
                        province, _ = Province.objects.get_or_create(
                            name="Limpopo"
                        )
                        province_2, _ = Province.objects.get_or_create(
                            name="Western Cape"
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
                        property_1 = PropertyFactory.create(
                            name='Lupin',
                            organisation=organization_1,
                            province=province
                        )
                        property_2 = PropertyFactory.create(
                            name='Kartoza',
                            organisation=organization_1,
                            province=province_2
                        )
                        # Check organization short code is empty
                        self.assertEqual(organization_1.short_code, '')
                        self.assertEqual(organization_2.short_code, '')
                        self.assertEqual(organization_3.short_code, '')
                        self.assertEqual(property_1.short_code, '')
                        self.assertEqual(property_2.short_code, '')

        forward_func_0007(Province, Property)
        organization_1.refresh_from_db()
        organization_2.refresh_from_db()
        organization_3.refresh_from_db()
        property_1.refresh_from_db()
        property_2.refresh_from_db()

        # Check Organization short code is not updated
        self.assertEqual(organization_1.short_code, '')
        self.assertEqual(organization_2.short_code, '')
        self.assertEqual(organization_3.short_code, '')

        # Check Property short code is updated.
        self.assertEqual(property_1.short_code, 'LICALU0001')
        self.assertEqual(property_2.short_code, 'WCCAKA0001')
