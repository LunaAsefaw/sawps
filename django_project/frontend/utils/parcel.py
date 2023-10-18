"""Common functions for parcel."""
from django.db import connection
from django.contrib.gis.geos import GEOSGeometry
from frontend.models.parcels import (
    Erf,
    Holding,
    FarmPortion,
    ParentFarm
)
from property.models import (
    Parcel, Province
)


def find_layer_by_cname(cname: str):
    """Find layer name+id by cname."""
    obj = Erf.objects.filter(cname=cname).first()
    if obj:
        return 'erf', obj.id
    obj = Holding.objects.filter(cname=cname).first()
    if obj:
        return 'holding', obj.id
    obj = FarmPortion.objects.filter(cname=cname).first()
    if obj:
        return 'farm_portion', obj.id
    obj = ParentFarm.objects.filter(cname=cname).first()
    if obj:
        return 'parent_farm', obj.id
    return None, None


def find_parcel_base(cls, serialize_cls,
                     other: GEOSGeometry, parcel_keys=[]):
    """Base function to find parcel."""
    used_parcels = []
    parcels = cls.objects.filter(geom__intersects=other)
    if parcel_keys:
        parcels = parcels.exclude(
            cname__in=parcel_keys
        )
    parcels = parcels.order_by('cname').distinct('cname')
    if parcels:
        cname_list = [a.cname for a in parcels]
        used_parcels = Parcel.objects.filter(
            sg_number__in=cname_list
        ).values_list('sg_number', flat=True)
        filtered_parcels = [a for a in parcels if
                            a.cname not in used_parcels]
        if filtered_parcels:
            results = serialize_cls(
                filtered_parcels,
                many=True
            ).data
            return results, cname_list, used_parcels
    return [], [], used_parcels


def find_province(geom: GEOSGeometry, default: Province):
    """
    Find province for given geometry (SRID 3857).

    :param geom: Geometry
    :param default: Default Province if no result
    :return: Province that has biggest overlap with geom
    """
    query = (
        """
        with input_geom as (select ST_GeomFromText(%s, 3857) as geom)
        select zpss.adm1_en as name,
        ST_AREA(ST_Intersection(ig.geom, zpss.geom)) / ST_AREA(zpss.geom)
        as overlap
        from layer.zaf_provinces_small_scale zpss
        inner join input_geom ig on ST_Intersects(ig.geom, zpss.geom)
        order by overlap desc limit 1
        """
    )
    query_values = [geom.ewkt]
    province_name = None
    with connection.cursor() as cursor:
        cursor.execute(query, query_values)
        row = cursor.fetchone()
        if row:
            province_name = row[0]
    if province_name is None:
        return default
    province = Province.objects.filter(
        name=province_name
    ).first()
    return province if province else default
