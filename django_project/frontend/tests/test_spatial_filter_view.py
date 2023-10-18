from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status

from frontend.api_views.spatial_filter import SpatialLayerSerializer
from frontend.tests.model_factories import LayerF


class SpatialLayerSerializerTestCase(TestCase):

    def setUp(self):
        self.layer1 = LayerF.create(
            layer_title='Layer 1',
            name='test'
        )

    def test_serializer(self):
        serialized_layer = SpatialLayerSerializer(self.layer1).data
        self.assertEqual(serialized_layer['layer_title'], "Layer 1")


class SpatialFilterListViewTestCase(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(
            self.username, password=self.password)
        device = TOTPDevice(
            user=self.user,
            name='device_name'
        )
        device.save()
        self.client.login(username=self.username, password=self.password)

        self.layer1 = LayerF.create(layer_title="Layer 1", is_filter_layer=True)
        self.layer2 = LayerF.create(layer_title="Layer 2", is_filter_layer=False)

    def test_get_spatial_filter_list(self):
        url = reverse('spatial-filter-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['layer_title'], "Layer 1")
