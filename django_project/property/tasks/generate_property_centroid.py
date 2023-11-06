from celery import shared_task


@shared_task(name='generate_property_centroid')
def generate_property_centroid():
    from property.models import Property
    properties = Property.objects.filter(
        centroid__isnull=True
    )
    total_count = properties.count()
    for property in properties:
        property.centroid = property.geometry.point_on_surface
        property.save(update_fields=['centroid'])
    print(f'Finished patching centroid: {total_count} properties')
