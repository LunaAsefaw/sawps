from property.tasks import update_organisation_property_short_code


def get_organisation_short_code(
    province_name: str = None,
    organisation_name: str = None,
    with_digit: bool = True,
    OrganisationModel=None
):
    from frontend.utils.organisation import get_abbreviation
    from stakeholder.models import Organisation

    OrganisationModel = (
        OrganisationModel if OrganisationModel else Organisation
    )
    province_name = province_name if province_name else ''
    organisation_name = organisation_name if organisation_name else ''

    province = get_abbreviation(
        province_name
    ) if province_name else ''
    organisation = get_abbreviation(
        organisation_name
    ) if organisation_name else ''

    if with_digit:
        # instead of using DB count, take next digit based on
        # the latest digit
        obj_latest_code = OrganisationModel.objects.filter(
            province__name=province_name
        ).order_by('short_code').last()

        digit = 1
        if obj_latest_code:
            digit = int(obj_latest_code.short_code[-4:]) + 1
        digit = "{:04d}".format(digit)
        return f"{province}{organisation}{digit}"
    else:
        return f"{province}{organisation}"


def forward_func_0015(Province, Organisation):
    for province in Province.objects.all():
        update_organisation_property_short_code(
            province_id=province.id,
            update_organisation=True,
            update_property=False,
            ProvinceModel=Province,
            OrganisationModel=Organisation
        )

    for org in Organisation.objects.filter(province__isnull=True):
        short_code = get_organisation_short_code(
            province_name='',
            organisation_name=org.name,
            with_digit=True,
            OrganisationModel=Organisation
        )
        org.short_code = short_code
        org.save()
