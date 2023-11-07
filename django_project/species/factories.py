import factory
from django.contrib.auth.models import User

from species.models import Taxon, TaxonRank, TaxonSurveyMethod


class TaxonRankFactory(factory.django.DjangoModelFactory):
    """taxon rank factory"""
    class Meta:
        model = TaxonRank

    name = factory.Sequence(lambda n: 'taxon_rank_%d' % n)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class TaxonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Taxon

    scientific_name = factory.Sequence(lambda n: f"Scientific Name {n}")
    common_name_varbatim = factory.Sequence(lambda n: f"Common Name {n}")
    colour_variant = factory.Faker('boolean')
    infraspecific_epithet = factory.Sequence(
        lambda n: f"Infraspecific Epithet {n}"
    )
    taxon_rank = factory.SubFactory('species.factories.TaxonRankFactory')
    parent = None
    show_on_front_page = factory.Faker('boolean')
    is_selected = factory.Faker('boolean')
    # icon = factory.django.ImageField(filename='icon.jpg', color='blue')


class TaxonSurveyMethodF(factory.django.DjangoModelFactory):
    """Taxon Survey Method factory."""
    class Meta:
        model = TaxonSurveyMethod


class TaxonF(factory.django.DjangoModelFactory):
    """Taxon model factory."""
    class Meta:
        model = Taxon

    scientific_name = factory.Sequence(lambda n: 'scientific_%d' % n)
    common_name_varbatim = factory.Sequence(lambda n: 'common_%d' % n)
    colour_variant = False
    taxon_rank = factory.SubFactory(
        'species.factories.TaxonRankFactory'
    )
