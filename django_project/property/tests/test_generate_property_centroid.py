from unittest.mock import patch

from django.test import TestCase
from property.factories import PropertyFactory
from property.tasks.generate_property_centroid import (
    generate_property_centroid
)


class TestGeneratePropertyCentroid(TestCase):

    @patch('property.tasks.generate_spatial_filter.generate_spatial_filter_task')
    def test_generate_centroid(self, mock_task):
        property = PropertyFactory.create()
        self.assertFalse(property.centroid)
        generate_property_centroid()
        property.refresh_from_db()
        self.assertTrue(property.centroid)
