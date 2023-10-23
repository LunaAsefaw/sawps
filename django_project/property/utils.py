from typing import Union, List

from django.db.models import QuerySet

from property.models import Property
from stakeholder.utils import update_organisation_property_short_code


def batch_short_code_update(
    province_id: int,
    organisation_id: int,
    PropertyModel=None
):
    PropertyModel = PropertyModel if PropertyModel else Property

    properties: Union[QuerySet, List[Property]] = PropertyModel.objects.filter(
        province_id=province_id,
        organisation_id=organisation_id
    ).order_by('id')
    for idx, property_obj in enumerate(properties):
        short_code_prefix = get_property_short_code(
            province_name=(
                property_obj.province.name if property_obj.province else ''
            ),
            organisation_name=property_obj.organisation.name,
            property_name=property_obj.name,
            with_digit=False
        )
        digit = "{:04d}".format(idx + 1)
        property_obj.short_code = f"{short_code_prefix}{digit}"
        property_obj.skip_post_save = True
        property_obj.save()


def get_property_short_code(
    province_name: str,
    organisation_name: str,
    property_name: str,
    with_digit: bool = True
):
    from frontend.utils.organisation import get_abbreviation
    province = get_abbreviation(
        province_name
    ) if province_name else ''
    organisation = get_abbreviation(
        organisation_name
    ) if organisation_name else ''
    property_abr = get_abbreviation(
        property_name
    ) if property_name else ''

    if with_digit:
        # instead of using DB count, take next digit based on
        # the latest digit

        obj_latest_code = Property.objects.filter(
            province__name=province_name,
            organisation__name=organisation_name
        ).order_by('short_code').last()

        digit = 1
        if obj_latest_code:
            digit = int(obj_latest_code.short_code[-4:]) + 1
        digit = "{:04d}".format(digit)
        return f"{province}{organisation}{property_abr}{digit}"
    else:
        return f"{province}{organisation}{property_abr}"


def forward_func_0007(Province, Property):
    for province in Province.objects.all():
        update_organisation_property_short_code(
            province_id=province.id,
            update_organisation=False,
            update_property=True,
            ProvinceModel=Province,
            PropertyModel=Property
        )
