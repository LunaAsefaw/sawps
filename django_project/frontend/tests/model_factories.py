"""Model factories for frontend."""
import factory
from django.contrib.auth import get_user_model
from frontend.models.boundary_search import BoundaryFile
from frontend.models.context_layer import ContextLayer, Layer, ContextLayerLegend
from frontend.models.parcels import Erf, FarmPortion, Holding, ParentFarm
from frontend.models.statistical import (
    NATIONAL_TREND,
    StatisticalModel,
    StatisticalModelOutput,
)
from frontend.models.upload import UploadSpeciesCSV
from frontend.models.spatial import (
    SpatialDataModel,
    SpatialDataValueModel
)


class UserF(factory.django.DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        """Meta class for UserF."""
        model = get_user_model()

    username = factory.Sequence(
        lambda n: f'username {n}'
    )


class ContextLayerF(factory.django.DjangoModelFactory):
    """Factory for ContextLayer Model."""

    class Meta:
        """Meta class Factory for ContextLayer Model."""
        model = ContextLayer

    name = factory.Sequence(
        lambda n: f'layer-{n}'
    )


class ContextLayerLegendF(factory.django.DjangoModelFactory):
    """Factory for ContextLayerLegend Model."""

    class Meta:
        """Meta class Factory for ContextLayerLegend Model."""
        model = ContextLayerLegend

    name = factory.Sequence(
        lambda n: f'layer-{n}'
    )
    colour = factory.Sequence(
        lambda n: f'colour-{n}'
    )
    layer = factory.SubFactory(
        'frontend.tests.model_factories.ContextLayerF'
    )


class LayerF(factory.django.DjangoModelFactory):
    """Factory for Layer Model"""

    class Meta:
        model = Layer

    name = factory.Sequence(
        lambda n: f'layer-{n}'
    )
    spatial_filter_field = factory.Sequence(
        lambda n: f'spatial-filter-{n}'
    )
    context_layer = factory.SubFactory(
        'frontend.tests.model_factories.ContextLayerF'
    )


class ErfF(factory.django.DjangoModelFactory):
    """Factory for Erf Model."""

    class Meta:
        """Meta class Factory for Erf Model."""
        model = Erf

    cname = factory.Sequence(
        lambda n: f'erf-{n}'
    )


class FarmPortionF(factory.django.DjangoModelFactory):
    """Factory for FarmPortion Model."""

    class Meta:
        """Meta class Factory for FarmPortion Model."""
        model = FarmPortion

    cname = factory.Sequence(
        lambda n: f'farm-portion-{n}'
    )


class HoldingF(factory.django.DjangoModelFactory):
    """Factory for Holding Model."""

    class Meta:
        """Meta class Factory for Holding Model."""
        model = Holding

    cname = factory.Sequence(
        lambda n: f'holding-{n}'
    )


class ParentFarmF(factory.django.DjangoModelFactory):
    """Factory for ParentFarm Model."""

    class Meta:
        """Meta class Factory for ParentFarm Model."""
        model = ParentFarm

    cname = factory.Sequence(
        lambda n: f'parent-farm-{n}'
    )


class BoundaryFileF(factory.django.DjangoModelFactory):
    """Factory for BoundaryFile."""

    class Meta:
        """Meta class Factory for BoundaryFile Model."""
        model = BoundaryFile

    meta_id = factory.Sequence(
        lambda n: 'meta_id_%s' % n
    )

    name = factory.Sequence(
        lambda n: 'name %s' % n
    )

    session = factory.Sequence(
        lambda n: 'session_%s' % n
    )

    file = factory.django.FileField(filename='admin.geojson')


class StatisticalModelOutputF(factory.django.DjangoModelFactory):
    """Factory for StatisticalModelOutput Model."""

    class Meta:
        """Meta class Factory for StatisticalModelOutput Model."""
        model = StatisticalModelOutput

    model = factory.SubFactory(
        'frontend.tests.model_factories.StatisticalModelF'
    )

    type = NATIONAL_TREND


class StatisticalModelF(factory.django.DjangoModelFactory):
    """Factory for StatisticalModel Model."""

    class Meta:
        """Meta class Factory for StatisticalModel Model."""
        model = StatisticalModel

    taxon = factory.SubFactory(
        'species.factories.TaxonF'
    )

    name = factory.Sequence(
        lambda n: f'statistical-model-{n}'
    )

    code = 'cleaned_data <- all_data'


class UploadSpeciesCSVF(factory.django.DjangoModelFactory):
    """Factory for UploadSpeciesCSV Model."""

    class Meta:
        """Meta class Factory for UploadSpeciesCSV Model."""
        model = UploadSpeciesCSV


class SpatialDataModelF(factory.django.DjangoModelFactory):
    """Factor for SpatialData model"""

    property = factory.SubFactory(
        'property.factories.PropertyFactory'
    )

    context_layer = factory.SubFactory(
        'frontend.tests.model_factories.ContextLayerF'
    )

    class Meta:
        model = SpatialDataModel


class SpatialDataModelValueF(factory.django.DjangoModelFactory):
    """Factor for SpatialDataModelValue model"""
    spatial_data = factory.SubFactory(
        'frontend.tests.model_factories.SpatialDataModelF'
    )

    context_layer_value = factory.Sequence(
        lambda n: f'context layer value {n}'
    )

    layer = factory.SubFactory(
        'frontend.tests.model_factories.LayerF'
    )

    class Meta:
        model = SpatialDataValueModel
