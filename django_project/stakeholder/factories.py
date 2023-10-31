from stakeholder.models import (
    UserRoleType,
    UserTitle,
    LoginStatus,
    UserProfile,
    Organisation,
    OrganisationUser,
    OrganisationRepresentative,
    OrganisationInvites,
    UserLogin
)
import factory
from django.contrib.auth.models import User


class userRoleTypeFactory(factory.django.DjangoModelFactory):
    """Factory class for user role type models."""

    class Meta:
        model = UserRoleType

    name = factory.Faker(
        'random_element', elements=('base user', 'admin', 'super user')
    )
    description = factory.Faker('text', max_nb_chars=200)


class loginStatusFactory(factory.django.DjangoModelFactory):
    """Factory class for login status models."""

    class Meta:
        model = LoginStatus

    name = factory.Faker(
        'random_element', elements=('logged in', 'logged out')
    )


class userTitleFactory(factory.django.DjangoModelFactory):
    """Factory class for user title models."""

    class Meta:
        model = UserTitle

    name = factory.Faker(
        'random_element', elements=('mr', 'mrs', 'miss', 'dr')
    )


class userFactory(factory.django.DjangoModelFactory):
    """Factory class for user models."""

    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = factory.Faker('email')


class userProfileFactory(factory.django.DjangoModelFactory):
    """Factory class for user profile model."""

    class Meta:
        model = UserProfile

    user = factory.SubFactory('stakeholder.factories.userFactory')
    title_id = factory.SubFactory('stakeholder.factories.userTitleFactory')
    cell_number = factory.Faker('random_int', min=10000, max=99999)
    user_role_type_id = factory.SubFactory(
        'stakeholder.factories.userRoleTypeFactory'
    )


class userLoginFactory(factory.django.DjangoModelFactory):
    """User login facfory class."""

    class Meta:
        model = UserLogin

    user = factory.SubFactory('stakeholder.factories.userFactory')
    login_status = factory.SubFactory(
        'stakeholder.factories.loginStatusFactory')
    date_time = factory.Faker('date_time')
    ip_address = factory.Faker('ipv4')


class organisationFactory(factory.django.DjangoModelFactory):
    """Factory class for organisation model."""

    class Meta:
        model = Organisation

    name = factory.Faker('company')
    data_use_permission = factory.SubFactory(
        'regulatory_permit.factories.DataUsePermissionFactory')


class organisationUserFactory(factory.django.DjangoModelFactory):
    """Factory class for organisation user model."""

    class Meta:
        model = OrganisationUser

    organisation = factory.SubFactory(
        'stakeholder.factories.organisationFactory')
    user = factory.SubFactory('stakeholder.factories.userFactory')


class organisationRepresentativeFactory(factory.django.DjangoModelFactory):
    """Factory class for organisation representative model."""

    class Meta:
        model = OrganisationRepresentative

    organisation = factory.SubFactory(
        'stakeholder.factories.organisationFactory')
    user = factory.SubFactory('stakeholder.factories.userFactory')


class OrganisationInvitesFactory(factory.django.DjangoModelFactory):
    """Factory class for Organisation Invites model."""

    class Meta:
        model = OrganisationInvites

    organisation = factory.SubFactory(
        'stakeholder.factories.organisationFactory')
