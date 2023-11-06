"""Classes for map filter session."""
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class MapSession(models.Model):
    """Store session for map."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    query_params = models.TextField(
        null=True,
        blank=True,
        default=''
    )

    uuid = models.UUIDField(
        default=uuid4,
        unique=True
    )

    species = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=''
    )

    created_date = models.DateTimeField()
    expired_date = models.DateTimeField()

    @property
    def properties_view_name(self):
        return f'{str(self.uuid)}_properties'

    @property
    def province_view_name(self):
        return f'{str(self.uuid)}_province'


@receiver(pre_delete, sender=MapSession)
def map_session_pre_delete(sender, instance, using, **kwargs):
    from frontend.utils.map import drop_map_materialized_view
    drop_map_materialized_view(instance.properties_view_name)
    drop_map_materialized_view(instance.province_view_name)
