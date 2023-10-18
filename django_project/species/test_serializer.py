from django.test import TestCase
from species.factories import (
    TaxonFactory
)
from species.serializers import TaxonSerializer

class TestTaxonSerializer(TestCase):
    """
    Test Taxon Serializer
    """
    def setUp(self) -> None:
        self.taxon_1 = TaxonFactory.create()

    def test_serialize_taxon(self):
        serialized_taxon = TaxonSerializer(self.taxon_1).data
        self.assertEqual(
            serialized_taxon,
            {
                'id': self.taxon_1.id,
                'scientific_name': self.taxon_1.scientific_name,
                'common_name_varbatim': self.taxon_1.common_name_varbatim
            }
        )
