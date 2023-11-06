from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.gis.geos import GEOSGeometry


logger = get_task_logger(__name__)


@shared_task(name="patch_province_in_properties")
def patch_province_in_properties():
    """Patch province field in properties."""
    from frontend.utils.parcel import find_province
    from property.models import Property
    properties = Property.objects.all().order_by('id')
    total = properties.count()
    total_updated = 0
    for property in properties:
        geometry: GEOSGeometry = property.geometry
        geom = geometry.transform(3857, clone=True)
        province = find_province(geom, property.province)
        if province and province.id != property.province.id:
            property.province = province
            property.save(update_fields=['province'])
            total_updated += 1
    logger.info(f'System has patched {total_updated}/{total} properties')
