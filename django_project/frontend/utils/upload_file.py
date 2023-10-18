"""Utility functions for shapefile."""
import os
from datetime import datetime
import json
import fiona
from fiona.io import (
    MemoryFile
)
import zipfile
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)
from frontend.models.base_task import (
    DONE
)
from frontend.models.parcels import (
    Erf,
    Holding,
    FarmPortion
)
from frontend.serializers.parcel import (
    ErfParcelSerializer,
    HoldingParcelSerializer,
    FarmPortionParcelSerializer
)
from frontend.models.boundary_search import (
    BoundarySearchRequest,
    BoundaryFile,
    SHAPEFILE
)
from frontend.utils.parcel import find_parcel_base


# when searching for parcels,
# we can ignore ParentFarm because it is broken down to FarmPortion
PARCEL_SERIALIZER_MAP = {
    Erf: ErfParcelSerializer,
    Holding: HoldingParcelSerializer,
    FarmPortion: FarmPortionParcelSerializer
}

fiona.drvsupport.supported_drivers['KML'] = 'ro'


def _store_zip_memory_to_temp_file(file_obj: InMemoryUploadedFile):
    tmp_path = os.path.join(settings.MEDIA_ROOT, 'tmp')
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    path = 'tmp/' + file_obj.name
    with default_storage.open(path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    return tmp_file


def validate_shapefile_zip(layer_file_path: any):
    """
    Validate if shapefile zip has correct necessary files.

    Note: fiona will throw exception only if dbf or shx is missing
    if there are 2 layers inside the zip, and 1 of them is invalid,
    then fiona will only return 1 layer
    """
    layers = []
    try:
        tmp_file = None
        if isinstance(layer_file_path, InMemoryUploadedFile):
            tmp_file = _store_zip_memory_to_temp_file(layer_file_path)
            layers = fiona.listlayers(f'zip://{tmp_file}')
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        elif isinstance(layer_file_path, TemporaryUploadedFile):
            layers = fiona.listlayers(
                f'zip://{layer_file_path.temporary_file_path()}'
            )
        else:
            layers = fiona.listlayers(f'zip://{layer_file_path}')
    except Exception:
        pass
    is_valid = len(layers) > 0
    error = []
    names = []
    with zipfile.ZipFile(layer_file_path, 'r') as zipFile:
        names = zipFile.namelist()
    shp_files = [n for n in names if n.endswith('.shp') and '/' not in n]
    shx_files = [n for n in names if n.endswith('.shx') and '/' not in n]
    dbf_files = [n for n in names if n.endswith('.dbf') and '/' not in n]

    if is_valid:
        for filename in layers:
            if f'{filename}.shp' not in shp_files:
                error.append(f'{filename}.shp')
            if f'{filename}.shx' not in shx_files:
                error.append(f'{filename}.shx')
            if f'{filename}.dbf' not in dbf_files:
                error.append(f'{filename}.dbf')
    else:
        distinct_files = (
            [
                os.path.splitext(shp)[0] for shp in shp_files
            ] +
            [
                os.path.splitext(shx)[0] for shx in shx_files
            ] +
            [
                os.path.splitext(dbf)[0] for dbf in dbf_files
            ]
        )
        distinct_files = list(set(distinct_files))
        if len(distinct_files) == 0:
            error.append('No required .shp file')
        else:
            for filename in distinct_files:
                if f'{filename}.shp' not in shp_files:
                    error.append(f'{filename}.shp')
                if f'{filename}.shx' not in shx_files:
                    error.append(f'{filename}.shx')
                if f'{filename}.dbf' not in dbf_files:
                    error.append(f'{filename}.dbf')
    is_valid = is_valid and len(error) == 0
    return is_valid, error


def _get_crs_epsg(crs):
    return crs['init'] if 'init' in crs else None


def get_uploaded_file_crs(file_obj, type):
    """Get CRS from uploaded file."""
    crs = None
    # if less than <2MB, it will be InMemoryUploadedFile
    if isinstance(file_obj, InMemoryUploadedFile):
        if type == 'SHAPEFILE':
            # fiona having issues with reading ZipMemoryFile
            # need to store to temp file
            tmp_file = _store_zip_memory_to_temp_file(file_obj)
            file_path = f'zip://{tmp_file}'
            with fiona.open(file_path) as collection:
                crs = _get_crs_epsg(collection.crs)
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        else:
            # geojson/geopackage can be read using MemoryFile
            with MemoryFile(file_obj.file) as file:
                with file.open() as collection:
                    crs = _get_crs_epsg(collection.crs)
    else:
        # TemporaryUploadedFile or just string to file path
        file_path = file_obj
        if type == 'SHAPEFILE':
            if isinstance(file_obj, TemporaryUploadedFile):
                file_path = f'zip://{file_obj.temporary_file_path()}'
            else:
                file_path = f'zip://{file_obj}'
        with fiona.open(file_path) as collection:
            crs = _get_crs_epsg(collection.crs)
    return crs


def search_parcels_by_boundary_files(request: BoundarySearchRequest):
    """Search parcels by uploaded boundary files."""
    request.task_on_started()
    request.geometry = None
    request.parcels = []
    request.save()
    # get files from session
    files = BoundaryFile.objects.filter(session=request.session)
    total_progress = files.count()
    current_progress = 0
    results = []
    parcel_keys = []
    unavailable_parcels = []
    union_geom: GEOSGeometry = None
    for boundary_file in files:
        file_path = boundary_file.file.path
        if boundary_file.file_type == SHAPEFILE:
            file_path = f'zip://{boundary_file.file.path}'
        with fiona.open(file_path, encoding='utf-8') as layer:
            for feature in layer:
                geom = None
                try:
                    geom_str = json.dumps(feature['geometry'])
                    geom = GEOSGeometry(geom_str, srid=4326)
                except Exception as ex:
                    print(ex)
                if geom is None:
                    continue
                if isinstance(geom, Polygon):
                    geom = MultiPolygon([geom], srid=4326)
                search_geom = geom.transform(3857, clone=True)
                # iterate from map
                for parcel_class, parcel_serializer in\
                    PARCEL_SERIALIZER_MAP.items():
                    parcels, keys, used_parcels = find_parcel_base(
                        parcel_class,
                        parcel_serializer,
                        search_geom,
                        parcel_keys
                    )
                    if keys:
                        parcel_keys.extend(keys)
                    if parcels:
                        results.extend(parcels)
                    if used_parcels:
                        unavailable_parcels.extend(used_parcels)
                # add to union geom
                if union_geom:
                    union_geom = union_geom.union(geom)
                else:
                    union_geom = geom
        current_progress += 1
        request.progress = current_progress * 100 / total_progress
        request.save(update_fields=['progress'])
    request.finished_at = datetime.now()
    request.progress = 100
    request.parcels = results
    request.geometry = union_geom
    request.used_parcels = unavailable_parcels
    request.status = DONE
    request.save()
