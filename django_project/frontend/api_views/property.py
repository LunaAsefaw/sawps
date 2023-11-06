"""API Views related to property.
"""
from datetime import datetime
from itertools import chain

from area import area
from django.contrib.gis.db.models import Union
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.exceptions import ValidationError
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from frontend.models.parcels import Erf, FarmPortion, Holding, ParentFarm
from frontend.models.places import (
    PlaceNameSmallScale,
    PlaceNameMidScale,
    PlaceNameLargerScale,
    PlaceNameLargestScale
)
from frontend.serializers.places import (
    PlaceLargerScaleSearchSerializer,
    PlaceLargestScaleSearchSerializer,
    PlaceMidScaleSearchSerializer,
    PlaceSmallScaleSearchSerializer
)
from frontend.serializers.property import (
    PropertyDetailSerializer,
    PropertySerializer,
    PropertyTypeSerializer,
    PropertySearchSerializer
)
from frontend.serializers.stakeholder import OrganisationSerializer
from frontend.static_mapping import DATA_CONTRIBUTORS, SUPER_USER
from frontend.utils.organisation import get_current_organisation_id
from frontend.utils.parcel import find_province
from frontend.utils.user_roles import get_user_roles
from population_data.models import OpenCloseSystem
from population_data.serializers import (
    OpenCloseSystemSerializer,
)
from property.models import (
    Parcel,
    ParcelType,
    Property,
    PropertyType,
    Province
)
from stakeholder.models import Organisation, OrganisationUser


class CheckPropertyNameIsAvailable(APIView):
    """Validate if property name is available."""
    permission_classes = [IsAuthenticated]

    def validate_property_name(self, name, property_id=None):
        properties = Property.objects.filter(
            name=name
        )
        if property_id:
            properties = properties.exclude(id=property_id)
        return not properties.exists()

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        property_id = request.data.get('id', None)
        return Response(
            status=200,
            data={
                'name': name,
                'available': self.validate_property_name(name, property_id)
            }
        )


class CreateNewProperty(CheckPropertyNameIsAvailable):
    """Create new property API."""
    permission_classes = [IsAuthenticated]

    def get_geom_size_in_ha(self, geom: GEOSGeometry):
        meters_sq = area(geom.geojson)
        acres = meters_sq * 0.000247105381  # meters^2 to acres
        return acres / 2.471

    def get_geometry(self, parcels):
        geom: GEOSGeometry = None
        erf_parcel_ids = [p['id'] for p in parcels if p['layer'] == 'erf']
        if erf_parcel_ids:
            queryset = Erf.objects.filter(
                id__in=erf_parcel_ids
            )
            queryset = queryset.aggregate(Union('geom'))
            geom = (
                queryset['geom__union'] if geom is None else
                geom.union(queryset['geom__union'])
            )

        holding_parcel_ids = [p['id'] for p in parcels if
                              p['layer'] == 'holding']
        if holding_parcel_ids:
            queryset = Holding.objects.filter(
                id__in=holding_parcel_ids
            )
            queryset = queryset.aggregate(Union('geom'))
            geom = (
                queryset['geom__union'] if geom is None else
                geom.union(queryset['geom__union'])
            )

        farm_portion_parcel_ids = [p['id'] for p in parcels if
                                   p['layer'] == 'farm_portion']
        if farm_portion_parcel_ids:
            queryset = FarmPortion.objects.filter(
                id__in=farm_portion_parcel_ids
            )
            queryset = queryset.aggregate(Union('geom'))
            geom = (
                queryset['geom__union'] if geom is None else
                geom.union(queryset['geom__union'])
            )

        parent_farm_parcel_ids = [p['id'] for p in parcels if
                                  p['layer'] == 'parent_farm']
        if parent_farm_parcel_ids:
            queryset = ParentFarm.objects.filter(
                id__in=parent_farm_parcel_ids
            )
            queryset = queryset.aggregate(Union('geom'))
            geom = (
                queryset['geom__union'] if geom is None else
                geom.union(queryset['geom__union'])
            )
        if isinstance(geom, Polygon):
            # parcels geom is in 3857
            geom = MultiPolygon([geom], srid=3857)
        province = find_province(geom, Province.objects.first())
        if geom:
            # transform srid to 4326
            geom.transform(4326)
        return geom, province

    def add_parcels(self, property, parcels):
        for parcel in parcels:
            type = parcel['type']
            parcel_type = ParcelType.objects.filter(
                name__iexact=type
            ).first()
            if not parcel_type:
                raise ValidationError(f'Invalid parcel_type: {type}')
            data = {
                'sg_number': parcel['cname'],
                'year': datetime.today().date(),
                'property': property,
                'parcel_type_id': parcel_type.id
            }
            Parcel.objects.create(**data)

    def post(self, request, *args, **kwargs):
        # union of parcels
        parcels = request.data.get('parcels')
        geom, province = self.get_geometry(parcels)
        if not province:
            return Response(
                status=400, data=(
                    'Invalid Province! Please contact administrator '
                    'to populate province table!'
                ))
        current_organisation_id = get_current_organisation_id(
            request.user
        ) or 0
        organisation_id = current_organisation_id
        if not organisation_id:
            return Response(status=400, data='Invalid Organisation!')
        # validate if user belongs to the organisation
        if not self.request.user.is_superuser:
            organisation_user = OrganisationUser.objects.filter(
                organisation_id=organisation_id,
                user=self.request.user
            )
            if not organisation_user.exists():
                return Response(
                    status=403,
                    data='User does not belong to this organisation!'
                )
        property_name = request.data.get('name')
        if not self.validate_property_name(property_name):
            return Response(
                status=400, data=(
                    f'There is existing property with name {property_name}! '
                    'Please use other name for the property!'
                ))
        data = {
            'name': property_name,
            'owner_email': request.data.get('owner_email'),
            'property_type_id': request.data.get('property_type_id'),
            'province_id': province.id,
            'open_id': request.data.get('open_id'),
            'organisation_id': request.data.get('organisation_id'),
            'geometry': geom,
            'property_size_ha': self.get_geom_size_in_ha(geom) if geom else 0,
            'created_by_id': self.request.user.id,
            'created_at': datetime.now(),
            'centroid': geom.point_on_surface
        }
        property = Property.objects.create(**data)
        self.add_parcels(property, parcels)
        return Response(status=201, data=PropertySerializer(property).data)


class PropertyMetadataList(APIView):
    """Get metadata for property: type, organisation, province."""
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        types = PropertyType.objects.all().order_by('name')
        current_organisation_id = get_current_organisation_id(
            self.request.user
        ) or 0
        organisations = Organisation.objects.filter(
            id=current_organisation_id
        ).order_by('name')
        open_close_systems = OpenCloseSystem.objects.all().order_by("name")
        return Response(status=200, data={
            'types': (
                PropertyTypeSerializer(types, many=True).data
            ),
            'organisations': (
                OrganisationSerializer(organisations, many=True).data
            ),
            "opens": (
                OpenCloseSystemSerializer(
                    open_close_systems, many=True).data
            ),
            'user_email': self.request.user.email,
            'user_name': (
                f'{self.request.user.first_name} '
                f'{self.request.user.last_name}' if
                self.request.user.first_name else self.request.user.username
            )
        })


class PropertyList(APIView):
    """Get properties that the current user owns."""
    permission_classes = [IsAuthenticated]

    def get(self, request, organisation_id=None, *args, **kwargs):
        current_organisation_id = get_current_organisation_id(
            request.user
        ) or 0

        if organisation_id:
            # Fetch properties based on
            # the organisation ID provided in the URL
            properties = Property.objects.filter(
                organisation_id=organisation_id
            ).order_by('name')
        else:
            # Fetch properties based on
            # the current organisation set on the user profile
            organisation_id = current_organisation_id

            organisation = request.GET.get("organisation")
            if organisation:
                _organisation = organisation.split(",")
                properties = Property.objects.filter(
                    organisation_id__in=(
                        [int(oid) for oid in _organisation]
                    ),
                ).order_by("name")
            else:
                properties = Property.objects.filter(
                    organisation_id=organisation_id
                ).order_by('name')

        user_roles = get_user_roles(self.request.user)

        # If role is DATA_CONTRIBUTORS and not a super user, limit properties
        if set(user_roles) & set(DATA_CONTRIBUTORS) and \
            SUPER_USER not in user_roles:
            properties = properties.filter(
                organisation_id=current_organisation_id
            ).order_by('name')

        return Response(
            status=200,
            data=PropertySerializer(properties, many=True).data
        )

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class UpdatePropertyInformation(CheckPropertyNameIsAvailable):
    """Update property information."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        property = get_object_or_404(
            Property,
            id=request.data.get('id')
        )
        property_name = request.data.get('name')
        if not self.validate_property_name(property_name, property.id):
            return Response(
                status=400, data=(
                    f'There is existing property with name {property_name}! '
                    'Please use other name for the property!'
                ))
        property.name = property_name
        property.property_type = (
            PropertyType.objects.get(id=request.data.get('property_type_id'))
        )
        property.organisation = (
            Organisation.objects.get(id=request.data.get('organisation_id'))
        )
        property.open = (
            OpenCloseSystem.objects.get(id=request.data.get('open_id'))
        )
        property.save()
        return Response(status=204)


class UpdatePropertyBoundaries(CreateNewProperty):
    """Update property parcels."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        property = get_object_or_404(
            Property,
            id=request.data.get('id')
        )
        parcels = request.data.get('parcels')
        geom, province = self.get_geometry(parcels)
        property.geometry = geom
        property.property_size_ha = (
            self.get_geom_size_in_ha(geom) if geom else 0
        )
        property.centroid = geom.point_on_surface
        property.province = province
        property.save()
        # delete existing parcel
        Parcel.objects.filter(property=property).delete()
        self.add_parcels(property, parcels)
        return Response(status=201, data=PropertySerializer(property).data)


class PropertyDetail(APIView):
    """Fetch property detail."""
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        property = get_object_or_404(
            Property,
            id=kwargs.get('id')
        )
        return Response(
            status=200,
            data=PropertyDetailSerializer(property).data
        )


class PropertySearch(APIView):
    """Search property and roads."""
    permission_classes = [IsAuthenticated]
    place_serializers = {
        PlaceNameSmallScale: PlaceSmallScaleSearchSerializer,
        PlaceNameMidScale: PlaceMidScaleSearchSerializer,
        PlaceNameLargerScale: PlaceLargerScaleSearchSerializer,
        PlaceNameLargestScale: PlaceLargestScaleSearchSerializer
    }

    def search_place(self, cls, serializer_cls, search_text, name_list):
        places = cls.objects.annotate(
            name_type=Concat(F('name'), Value('-'), F('fclass'),
                             output_field=CharField())
        ).filter(
            name__istartswith=search_text
        ).exclude(
            name_type__in=name_list
        ).order_by('name')[:5]
        results = serializer_cls(places, many=True).data
        return results, [f'{p["name"]}-{p["fclass"]}' for p in results]

    def get(self, *args, **kwargs):
        search_text = self.request.GET.get('search_text', '')
        # filter property from current organisation
        current_organisation_id = get_current_organisation_id(
            self.request.user
        ) or 0
        properties = Property.objects.filter(
            name__istartswith=search_text,
            organisation_id=current_organisation_id
        ).order_by('name')[:10]
        properties_search_results = PropertySearchSerializer(
            properties,
            many=True
        ).data
        place_results = []
        name_list = []
        for place_class, place_serializer in self.place_serializers.items():
            result, names = self.search_place(
                place_class,
                place_serializer,
                search_text,
                name_list
            )
            if names:
                name_list.extend(names)
            place_results.extend(result)
        results = list(chain(properties_search_results, place_results))
        results.sort(key=lambda x: x['name'])
        return Response(
            status=200,
            data=results
        )
