from django.test import TestCase, override_settings
from property.models import PropertyType, Province, ParcelType, Parcel, Property
from property.factories import PropertyTypeFactory, ProvinceFactory, ParcelTypeFactory, ParcelFactory, PropertyFactory
from django.db.utils import IntegrityError

from stakeholder.factories import organisationFactory


class ProvinceTestCase(TestCase):
    """Province test case"""
    @classmethod
    def setUpTestData(cls):
        cls.province = ProvinceFactory()

    def test_create_province(self):
        'Test create a province.'
        self.assertTrue(isinstance(self.province, Province))
        self.assertEqual(Province.objects.count(), 1)
        self.assertEqual(self.province.name, Province.objects.get(id=self.province.id).name)

    def test_update_province(self):
        'Test update a province.'
        self.province.name = 'Province 2'
        self.province.save()
        self.assertEqual(
            Province.objects.get(id=self.province.id).name, 'Province 2'
        )

    def test_unique_province_name_constraint(self):
        'Test unique province name constraint.'
        with self.assertRaises(Exception) as raised:
            ProvinceFactory(name='Province 2')
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_delete_province(self):
        'Test delete a province.'
        self.province.delete()
        self.assertEqual(Province.objects.count(), 0)


class PropertyTypeTest(TestCase):
    """Propert type test case"""
    @classmethod
    def setUpTestData(cls):
        cls.property_type = PropertyTypeFactory()

    def test_create_property_type(self):
        """Test creating a new property type"""
        self.assertTrue(
            isinstance(self.property_type, PropertyType)
        )
        self.assertEqual(PropertyType.objects.count(), 1)
        self.assertEqual(self.property_type.name, PropertyType.objects.get(id=self.property_type.id).name)

    def test_update_property_type(self):
        """Test updating a property type"""
        self.property_type.name = 'PropertyType 2'
        self.property_type.save()
        self.assertEqual(
            PropertyType.objects.get(id=self.property_type.id).name,
            'PropertyType 2',
        )

    def test_property_type_unique_name_constraint(self):
        """Test property type unique name constraint"""
        with self.assertRaises(Exception) as raised:
            PropertyTypeFactory(name='PropertyType 2')
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_delete_property_type(self):
        """Test deleting a property type"""
        self.property_type.delete()
        self.assertEqual(PropertyType.objects.count(), 0)


@override_settings(
    CELERY_ALWAYS_EAGER=True,
    BROKER_BACKEND='memory',
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True
)
class PropertyTestCase(TestCase):
    """ Property test case."""
    @classmethod
    def setUpTestData(cls):
        cls.province = ProvinceFactory(name='Western Cape')
        cls.organisation = organisationFactory(name='CapeNature')
        cls.property = PropertyFactory(
            name='Lupin',
            province=cls.province,
            organisation=cls.organisation
        )
    
    def test_create_property(self):
        """Test creating property """
        self.assertTrue(isinstance(self.property, Property))
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(self.property.name, Property.objects.get(id=self.property.id).name)

        self.assertEqual(
            self.property.short_code,
            'WCCALU0001'
        )
    
    def test_update_property(self):
        """Test update property."""
        self.property.name = 'Rex Mundi'
        self.property.save()
        self.assertEqual(Property.objects.get(id=self.property.id).name, 'Rex Mundi')

        self.assertEqual(
            self.property.short_code,
            'WCCARM0002'
        )


    def test_delete_property(self):
        """Test delete property."""
        self.property.delete()
        self.assertEqual(Property.objects.count(), 0)


class ParcelTypeTestCase(TestCase):
    """Parcel type test case"""
    @classmethod
    def setUpTestData(cls):
        cls.parcel_type = ParcelTypeFactory()
    
    def test_create_parcel_type(self):
        """Test create parcel types """
        self.assertTrue(isinstance(self.parcel_type, ParcelType))
        self.assertEqual(ParcelType.objects.count(), 1)

    def test_update_parcel_type(self):
        """Test update parcel type."""
        self.parcel_type.name = 'ParcelType_1'
        self.parcel_type.save()
        self.assertEqual(ParcelType.objects.get(id=self.parcel_type.id).name, 'ParcelType_1')

    def test_unique_parcel_type_name_constraint(self):
        """Test unique parcel type name constraint."""
        with self.assertRaises(Exception) as raised:
            ParcelTypeFactory(name='ParcelType_1')
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_delete_parcel_type(self):
        """Test delete parcel type."""
        self.parcel_type.delete()
        self.assertEqual(ParcelType.objects.count(), 0)


class ParcelTestCase(TestCase):
    """Parcel test case."""
    @classmethod
    def setUpTestData(cls):
        cls.parcel = ParcelFactory(sg_number='SG_0')

    def test_create_parcel(self):
        """Test create parcel."""
        self.assertTrue(isinstance(self.parcel, Parcel))
        self.assertEqual(Parcel.objects.count(), 1)
        self.assertEqual(self.parcel.sg_number, 'SG_0')
        self.assertEqual(self.parcel.farm_number, 0)

    def test_update_parcel(self):
        """Test update parcel."""
        self.parcel.sg_number = 'SG_1'
        self.parcel.save()
        self.assertEqual(Parcel.objects.get(id=self.parcel.id).sg_number, 'SG_1')

    def test_unique_parcel_sg_number_constraint(self):
        """Test unique parcel sg number constraint."""
        with self.assertRaises(Exception) as raised:
            ParcelFactory(sg_number='SG_1')
            self.assertEqual(IntegrityError, type(raised.exception))

    def test_delete_parcel(self):
        """Test delete parcel."""
        self.parcel.delete()
        self.assertEqual(Parcel.objects.count(), 0)
