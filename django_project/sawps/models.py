from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ExtendedGroup(models.Model):
    """
    Stores additional attributes for Django's built-in Group model.
    Related to :model:`auth.Group`.
    """

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='extended')

    description = models.TextField()

    def __str__(self):
        return self.description


@receiver(post_save, sender=Group)
def save_extended_group(sender, instance, created, **kwargs):
    """
    Handle ExtendedGroup creation and saving for the Group
    """
    extended_group, created = (
        ExtendedGroup.objects.get_or_create(group=instance)
    )

    if not created:
        instance.extended.save()
