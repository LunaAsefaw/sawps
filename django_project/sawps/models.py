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

    class Meta:
        permissions = [
            ("can_view_population_trend", "Can view population trend"),
            ("can_view_population_category", "Can view population category"),
            ("can_view_property_type", "Can view property type"),
            ("can_view_density_bar", "Can view density bar"),
            ("can_view_property_available", "Can view property available"),
            ("can_view_age_group", "Can view age group"),
            ("can_view_area_available", "Can view area available"),
            (
                "can_view_province_species_count",
                "Can view province species count"
            ),
            (
                "can_view_province_species_count_as_percentage",
                "Can view province species count as percentage",
            ),
            ("can_view_total_count", "Can view total count"),
            ("can_view_count_as_percentage", "Can view count as percentage"),
            ("can_view_population_estimate", "Can view population estimate"),
            (
                "can_view_population_estimate_as_percentage",
                "Can view population estimate as percentage",
            ),
            (
                "can_view_sampling_report",
                "Can view sampling report",
            ),
            (
                "can_view_province_report",
                "Can view province report",
            )
        ]


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
