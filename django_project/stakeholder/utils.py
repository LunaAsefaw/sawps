from frontend.static_mapping import (
    ORGANISATION_MANAGER,
    ORGANISATION_MEMBER
)
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


def add_user_to_organisation_group(
    instance,
    OrgInvModel=None,
    GroupModel=None,
):
    """
    Add user to Organisation Member/Manager group.
    """
    from stakeholder.models import OrganisationInvites, MANAGER
    from django.contrib.auth.models import Group

    OrgInvModel = OrgInvModel if OrgInvModel else OrganisationInvites
    GroupModel = GroupModel if GroupModel else Group

    # check Organisation Invites.
    # If it exists as Manager, assign to Organisation Manager group.
    # Otherwise assign to Organisation Member
    invitation: OrgInvModel = OrgInvModel.objects.filter(
        email=instance.user.email,
        organisation=instance.organisation,
        joined=True
    ).first()
    if invitation:
        if invitation.assigned_as == MANAGER:
            group, _ = GroupModel.objects.get_or_create(
                name=ORGANISATION_MANAGER
            )
            instance.user.groups.add(group)
            return
    group, _ = GroupModel.objects.get_or_create(name=ORGANISATION_MEMBER)
    instance.user.groups.add(group)


def remove_organisation_user_from_group(instance):
    """
    Remove user to Organisation Member/Manager group.
    """

    from stakeholder.models import (
        OrganisationInvites, OrganisationUser, MANAGER
    )
    from django.contrib.auth.models import Group

    organisation_users = OrganisationUser.objects.filter(user=instance.user)

    # Remove from Data Contributor groups if user is
    # no longer assigned to any organisation
    group = Group.objects.filter(name='Data contributor').first()
    if group:
        instance.user.groups.remove(group)

    if organisation_users.exists():
        organisations = organisation_users.values_list('organisation')
        # check invitation as manager for the user, for
        # current organisations assigned to them.
        invitations = OrganisationInvites.objects.filter(
            organisation__in=organisations,
            email=instance.user.email,
            assigned_as=MANAGER
        )
        # if invitation as manager does not exist, remove from
        # Organisation Manager group
        if not invitations.exists():
            group, _ = Group.objects.get_or_create(name=ORGANISATION_MANAGER)
            instance.user.groups.remove(group)
    else:
        group = Group.objects.filter(name=ORGANISATION_MEMBER).first()
        if group:
            instance.user.groups.remove(group)

        group = Group.objects.filter(name=ORGANISATION_MANAGER).first()
        if group:
            instance.user.groups.remove(group)
