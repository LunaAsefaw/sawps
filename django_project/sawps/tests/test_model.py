from django.db.models.signals import post_save
from django.test import TestCase
from django.contrib.admin import site
from sawps.tests.model_factories import (
    GroupF,
    Group,
)
from sawps.models import (
    save_extended_group, ExtendedGroup
)
from sawps.admin import GroupAdmin


class TestExtendedGroup(TestCase):

    def test_extended_group_created(self):
        group = GroupF.create()
        self.assertIsNotNone(group.extended)
        self.assertTrue('Group name' in str(
            group.extended.group.name
        ))

    def test_save_group(self):

        post_save.disconnect(save_extended_group, sender=Group)

        group = GroupF.create()
        group.extended = None
        group.save()

        self.assertFalse(
            ExtendedGroup.objects.filter(
                group_id=group.id
            ).exists()
        )

        post_save.connect(save_extended_group, sender=Group)

        group.save()
        self.assertTrue(
            ExtendedGroup.objects.filter(
                group_id=group.id
            ).exists()
        )

        group.extended.description = 'test'
        group.save()

        self.assertEqual(
            ExtendedGroup.objects.get(
                group_id=group.id
            ).description,
            'test'
        )


class GroupAdminTestCase(TestCase):

    def setUp(self):
        self.group = GroupF.create(name="Test Group")
        self.group.extended.description = "Test Description"
        self.group.save()

    def test_get_no_description(self):

        post_save.disconnect(save_extended_group, sender=Group)

        group = GroupF.create()

        post_save.connect(save_extended_group, sender=Group)

        admin_instance = GroupAdmin(Group, site)
        description = admin_instance.get_description(
            group
        )
        self.assertEqual(description, "No description")

    def test_get_description_method(self):
        admin_instance = GroupAdmin(Group, site)
        description = admin_instance.get_description(self.group)
        self.assertEqual(description, "Test Description")

    def test_list_display(self):
        admin_instance = GroupAdmin(Group, site)
        self.assertIn('get_description', admin_instance.list_display)

