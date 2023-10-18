from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.models import Layer


class SpatialLayerSerializer(serializers.ModelSerializer):

    values = serializers.SerializerMethodField()

    def get_values(self, obj: Layer) -> List[str]:
        """
        Retrieve distinct spatial values for the given layer.

        :param obj: Instance of Layer model
        :type obj: Layer
        """
        return list(
            obj.spatialdatavaluemodel_set.distinct(
                'context_layer_value'
            ).values_list(
                'context_layer_value',
                flat=True
            )
        )

    class Meta:
        model = Layer
        fields = [
            'layer_title', 'values'
        ]


class SpatialFilterList(LoginRequiredMixin, APIView):
    """
    A view that returns a list of layers marked as spatial filters.
    """

    def get(self, request, **kwargs) -> Response:
        """
        Handles the GET request and returns the list of spatial filter layers
        """
        spatial_filter_layers = Layer.objects.filter(
            is_filter_layer=True
        )
        return Response(
            SpatialLayerSerializer(
                spatial_filter_layers, many=True).data
        )
