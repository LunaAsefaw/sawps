from typing import Union, List

from celery import shared_task
from django.db.models import QuerySet

from property.models import Province, Property


@shared_task
def update_organisation_property_short_code(
    province_id: int,
    update_organisation: bool = True,
    update_property: bool = True,
    ProvinceModel=None,
    OrganisationModel=None,
    PropertyModel=None,
) -> None:
    from stakeholder.models import Organisation
    from stakeholder.utils import get_organisation_short_code
    from property.utils import batch_short_code_update

    ProvinceModel = ProvinceModel if ProvinceModel else Province
    OrganisationModel = (
        OrganisationModel if OrganisationModel else Organisation
    )
    PropertyModel = PropertyModel if PropertyModel else Property

    try:
        instance = ProvinceModel.objects.get(id=province_id)
    except ProvinceModel.DoesNotExist:
        return

    if update_organisation:
        organisations: Union[
            QuerySet,
            List[OrganisationModel]
        ] = instance.organisation_set.all().order_by('id')
        for idx, organisation in enumerate(organisations):
            short_code_prefix = get_organisation_short_code(
                province_name=(
                    organisation.province.name if organisation.province else ''
                ),
                organisation_name=organisation.name,
                with_digit=False
            )
            digit = "{:04d}".format(idx + 1)
            organisation.short_code = f"{short_code_prefix}{digit}"
            organisation.skip_post_save = True
            organisation.save()

    if update_property:
        prov_orgs: Union[QuerySet, List[dict]] = PropertyModel.objects.filter(
            province=instance).values('province', 'organisation').distinct()
        for prov_org in prov_orgs:
            batch_short_code_update(
                province_id=prov_org['province'],
                organisation_id=prov_org['organisation'],
                PropertyModel=PropertyModel
            )
