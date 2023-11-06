"""Helper function for map."""
import os
import json
import time
import ast
import math
from enum import Enum
from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from core.settings.utils import absolute_path
from species.models import Taxon
from frontend.models.map_session import MapSession
from frontend.utils.color import linear_gradient
from stakeholder.models import OrganisationUser
from activity.models import ActivityType


User = get_user_model()
# number of breaks to generate stops for color gradient of population count
CHOROPLETH_NUMBER_OF_BREAKS = 5
DEFAULT_BASE_COLOR = '#FF5252'


class MapQueryEnum(Enum):
    # show properties layer using active organisation
    MAP_DEFAULT = 'MAP_DEFAULT'
    # show properties/province layers using filters
    MAP_USING_SESSION = 'MAP_SESSION'


def get_map_template_style(request, session = None, theme_choice: int = 0,
                           token: str = None):
    """
    Fetch map template style from file.

    :param theme_choice: 0 light, 1 dark
    :return: json map style
    """
    load_normal_map = True
    if hasattr(request.user, 'user_profile'):
        user_role = str(
            request.user.user_profile.user_role_type_id
        )
        if "Decision Maker" in user_role:
            style_file_path = absolute_path(
                'frontend', 'utils', 'country_level_light_v2.json'
            )
            if theme_choice == 1:
                style_file_path = absolute_path(
                    'frontend', 'utils', 'country_level_dark_v2.json'
                )
            load_normal_map = False
    if load_normal_map:
        style_file_path = absolute_path(
            'frontend', 'utils', 'sanbi_styling_light.json'
        )
        if theme_choice == 1:
            style_file_path = absolute_path(
                'frontend', 'utils', 'sanbi_styling_dark.json'
            )
    styles = {}
    with open(style_file_path) as config_file:
        styles = json.load(config_file)
    # update sanbi source URL
    schema = 'https://'
    domain = Site.objects.get_current().domain
    if settings.DEBUG:
        schema = 'http://'
        tegola_dev_port = os.environ.get('TEGOLA_DEV_PORT', '9191')
        domain = f'localhost:{tegola_dev_port}'
    elif 'localhost' in domain:
        schema = 'http://'
    if 'sources' in styles and 'sanbi' in styles['sources']:
        tile_url = f'{schema}{domain}/maps/sanbi/{{z}}/{{x}}/{{y}}'
        if settings.DEBUG:
            tile_url = tile_url + '.pbf'
        if not settings.DEBUG and token:
            tile_url = tile_url + f'?token={token}'
        styles['sources']['sanbi']['tiles'] = [tile_url]
    if 'sources' in styles and 'NGI Aerial Imagery' in styles['sources']:
        url = (
            reverse('aerial-map-layer', kwargs={
                'z': 0,
                'x': 0,
                'y': 0
            })
        )
        url = request.build_absolute_uri(url)
        url = url.replace('/0/0/0', '/{z}/{x}/{y}')
        if not settings.DEBUG:
            # if not dev env, then replace with https
            url = url.replace('http://', schema)
        styles['sources']['NGI Aerial Imagery']['tiles'] = [url]
    # add properties layer
    if 'sources' in styles:
        if session:
            url = (
                reverse('session-properties-map-layer', kwargs={
                    'z': 0,
                    'x': 0,
                    'y': 0
                })
            )
        else:
            url = (
                reverse('default-properties-map-layer', kwargs={
                    'z': 0,
                    'x': 0,
                    'y': 0
                })
            )
        url = request.build_absolute_uri(url)
        url = url.replace('/0/0/0', '/{z}/{x}/{y}')
        if not settings.DEBUG:
            # if not dev env, then replace with https
            url = url.replace('http://', schema)
        # add epoch datetime
        url = url + f'?t={int(time.time())}'
        if session:
            url = url + f'&session={session}'
        styles['sources']['sanbi-dynamic'] = {
            "type": "vector",
            "tiles": [url],
            "minzoom": 5,
            "maxzoom": 24
        }
        styles['layers'].append(get_highlighted_layer('erf'))
        styles['layers'].append(get_highlighted_layer('holding'))
        styles['layers'].append(get_highlighted_layer('farm_portion'))
        styles['layers'].append(get_highlighted_layer('parent_farm'))
    # update maptiler api key
    styles = replace_maptiler_api_key(styles)
    return styles


def replace_maptiler_api_key(styles):
    """Replace maptiler_key."""
    map_tiler_key = settings.MAPTILER_API_KEY
    if 'glyphs' in styles and styles['glyphs']:
        styles['glyphs'] = styles['glyphs'].replace(
            '{{MAPTILER_API_KEY}}',
            map_tiler_key
        )
    return styles


def get_highlighted_layer(layer_name):
    # green
    return {
        "id": f"{layer_name}-highlighted",
        "type": "line",
        "source": "sanbi",
        "source-layer": f"{layer_name}",
        "minzoom": 12,
        "layout": {"visibility": "visible", "line-join": "bevel"},
        "paint": {
            "line-color": "#ffffff",
            "line-width": [
                "case",
                [
                    "boolean",
                    ["feature-state", "parcel-selected-highlighted"],
                    False
                ],
                4,
                0
            ],
            "line-opacity": 1
        }
    }


def get_query_condition_for_properties_query(
        filter_organisation: str,
        filter_spatial: str,
        filter_property: str,
        property_alias_name: str = 'p'):
    """
    Generate query condition from properties filters.

    Filters that are used for properties layer:
    - organisation
    - property
    - spatial

    :param filter_organisation: filter by organisation id list
    :param filter_spatial: property spatial filter list
    :param filter_property: filter by property id list
    :param property_alias_name: alias for property table in the query
    :return: list of SQL conditions and list of query values
    """
    sql_conditions = []
    query_values = []
    if filter_organisation:
        if filter_organisation != 'all':
            sql_conditions.append(
                f'{property_alias_name}.organisation_id IN %s')
            query_values.append(
                ast.literal_eval('(' + filter_organisation + ',)'))
    else:
        sql_conditions.append(
            f'{property_alias_name}.organisation_id = any(ARRAY[]::bigint[])')
    if filter_property:
        if filter_property != 'all':
            sql_conditions.append(f'{property_alias_name}.id IN %s')
            query_values.append(
                ast.literal_eval('(' + filter_property + ',)'))
    else:
        sql_conditions.append(
            f'{property_alias_name}.id = any(ARRAY[]::bigint[])')
    if filter_spatial:
        spatial_filter_values = tuple(
            filter(None, filter_spatial.split(','))
        )
        if spatial_filter_values:
            spatial_sql = (
                """
                select 1 from frontend_spatialdatavaluemodel fs2
                inner join frontend_spatialdatamodel fs3 on
                fs3.id = fs2.spatial_data_id
                where fs3.property_id={property_alias_name}.id and
                fs2.context_layer_value in %s
                """
            ).format(property_alias_name=property_alias_name)
            sql_conditions.append(
                'exists({spatial_sql})'.format(spatial_sql=spatial_sql)
            )
            query_values.append(spatial_filter_values)
    return sql_conditions, query_values


def get_query_condition_for_population_query(
        filter_start_year: int,
        filter_end_year: int,
        filter_species_name: str,
        filter_activity: str):
    """
    Generate query condition from species filters.

    Filters that are used for choropleth:
    - species (mandatory)
    - start + end years
    - activity

    :param filter_start_year: filter by start year
    :param filter_end_year: filter by end year
    :param filter_species_name: filter by species name
    :param filter_activity: filter by activity list
    :return: list of SQL conditions and list of query values
    """
    sql_conditions = []
    query_values = []
    sql_conditions.append('t.scientific_name=%s')
    query_values.append(filter_species_name)
    if filter_activity and filter_activity != 'all':
        activities = ast.literal_eval('(' + filter_activity + ',)')
        if ActivityType.objects.count() != len(activities):
            filter_years = ''
            if filter_start_year and filter_end_year:
                filter_years = (
                    """AND appa.year between %s and %s"""
                )
            activity_sql = (
                """
                SELECT 1 FROM annual_population_per_activity appa
                WHERE appa.annual_population_id=ap.id
                AND appa.activity_type_id IN %s
                {filter_years}
                """
            ).format(filter_years=filter_years)
            sql_conditions.append(
                'exists({activity_sql})'.format(activity_sql=activity_sql)
            )
            query_values.append(activities)
            if filter_years:
                query_values.append(filter_start_year)
                query_values.append(filter_end_year)
    if filter_start_year and filter_end_year:
        sql_conditions.append('ap.year between %s and %s')
        query_values.append(filter_start_year)
        query_values.append(filter_end_year)
    return sql_conditions, query_values


def get_province_population_query(
        filter_start_year: int,
        filter_end_year: int,
        filter_species_name: str,
        filter_organisation: str,
        filter_activity: str,
        filter_spatial: str,
        filter_property: str):
    """
    Generate query for population count in province level.

    :param filter_start_year: filter by start year
    :param filter_end_year: filter by end year
    :param filter_species_name: filter by species name
    :param filter_organisation: filter by organisation id list
    :param filter_activity: filter by activity list
    :param filter_spatial: property spatial filter list
    :param filter_property: filter by property id list
    :return: SQL for materialized view and query values
    """
    sql_view = ''
    query_values = []
    sql_conds_pop, query_values_pop = get_query_condition_for_population_query(
        filter_start_year, filter_end_year,
        filter_species_name, filter_activity
    )
    sql_conds_properties, query_values_properties = (
        get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
    )
    sql_conds = []
    if sql_conds_pop:
        sql_conds.extend(sql_conds_pop)
        query_values.extend(query_values_pop)
    if sql_conds_properties:
        sql_conds.extend(sql_conds_properties)
        query_values.extend(query_values_properties)
    where_sql = ' AND '.join(sql_conds)
    sql = (
        """
        select p.province_id as id, sum(ap.total) as count
        from annual_population ap
        inner join taxon t on ap.taxon_id=t.id
        inner join property p on ap.property_id=p.id
        {where_sql} group by p.province_id
        """
    ).format(
        where_sql=f'where {where_sql}' if where_sql else ''
    )
    sql_view = (
        """
        select p2.id, p2.name, COALESCE(population_summary.count, 0) as count
        from province p2 left join ({sub_sql}) as population_summary
        on p2.id=population_summary.id
        """
    ).format(
        sub_sql=sql
    )
    return sql_view, query_values


def get_properties_population_query(
        filter_start_year: int,
        filter_end_year: int,
        filter_species_name: str,
        filter_organisation: str,
        filter_activity: str,
        filter_spatial: str,
        filter_property: str):
    """
    Generate query for population count in properties level.

    :param filter_start_year: filter by start year
    :param filter_end_year: filter by end year
    :param filter_species_name: filter by species name
    :param filter_organisation: filter by organisation id list
    :param filter_activity: filter by activity list
    :param filter_spatial: property spatial filter list
    :param filter_property: filter by property id list
    :return: SQL for materialized view and query values
    """
    sql_view = ''
    query_values = []
    sql_conds_pop, query_values_pop = get_query_condition_for_population_query(
        filter_start_year, filter_end_year,
        filter_species_name, filter_activity
    )
    sql_conds_properties, query_values_properties = (
        get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property,
            property_alias_name='p2'
        )
    )
    where_sql = ''
    if sql_conds_pop:
        where_sql = ' AND '.join(sql_conds_pop)
        query_values.extend(query_values_pop)
    sql = (
        """
        select ap.property_id as id, sum(ap.total) as count
        from annual_population ap
        inner join taxon t on ap.taxon_id=t.id
        inner join property p on ap.property_id=p.id
        {where_sql} group by ap.property_id
        """
    ).format(
        where_sql=f'where {where_sql}' if where_sql else ''
    )
    where_sql_properties = ''
    if sql_conds_properties:
        where_sql_properties = ' AND '.join(sql_conds_properties)
        query_values.extend(query_values_properties)
    sql_view = (
        """
        select p2.id, p2.name, COALESCE(population_summary.count, 0) as count
        from property p2 left join ({sub_sql}) as population_summary
        on p2.id=population_summary.id
        {where_sql}
        """
    ).format(
        sub_sql=sql,
        where_sql=(
            f'where {where_sql_properties}' if where_sql_properties else ''
        )
    )
    return sql_view, query_values


def get_properties_query(
        filter_organisation: str,
        filter_spatial: str,
        filter_property: str):
    """
    Generate query for properties layer.

    :param filter_organisation: filter by organisation id list
    :param filter_spatial: property spatial filter list
    :param filter_property: filter by property id list
    :return: SQL for materialized view and query values
    """
    sql_view = ''
    query_values = []
    sql_conds_properties, query_values_properties = (
        get_query_condition_for_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
    )
    where_sql_properties = ''
    if sql_conds_properties:
        where_sql_properties = ' AND '.join(sql_conds_properties)
        query_values.extend(query_values_properties)
    sql_view = (
        """
        select p.id, p.name, 0 as count
        from property p
        {where_sql}
        """
    ).format(
        where_sql=(
            f'where {where_sql_properties}' if where_sql_properties else ''
        )
    )
    return sql_view, query_values


def get_count_summary_of_population(
        is_province_layer: bool,
        session: MapSession):
    """
    Return (Min, Max) for population query count.
    Materialized view for current session must be created.

    :param is_province_layer: True if the summary is for province layer
    :param session: map filter session
    :return: Tuple[int, int]: A tuple of (Min, Max) population count
    """
    where_sql = ''
    if not is_province_layer:
        where_sql = 'WHERE count > 0'
    sql = (
        """
        select min(count), max(count) from "{view_name}"
        {where_sql}
        """
    ).format(
        view_name=(
            session.province_view_name if is_province_layer else
            session.properties_view_name
        ),
        where_sql=where_sql
    )
    max = 0
    min = 0
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            min = row[0] if row[0] else 0
            max = row[1] if row[1] else 0
    return (min, max)


def generate_population_count_categories_base(
        min: int,
        max: int,
        base_color: str):
    """
    Generate population count categories for choropleth map.
    Using equal interval classification.
    http://wiki.gis.com/wiki/index.php/Equal_Interval_classification

    :param min: minimum population count
    :param max: maximum population count
    :param base_color: base color in hex to calculate color gradient
    :return: list of dict of minLabel, maxLabel, value and color.
    """
    result = []
    colors = linear_gradient(base_color, n=CHOROPLETH_NUMBER_OF_BREAKS)['hex']
    colors = colors[::-1]
    if max == 0 and min == 0:
        max = 100
    break_val = math.ceil((max - min) / CHOROPLETH_NUMBER_OF_BREAKS)
    if break_val == 0:
        # case min = max
        break_val = 20
    val = min
    for t in range(0, CHOROPLETH_NUMBER_OF_BREAKS):
        result.append({
            'minLabel': val,
            'maxLabel': val + break_val,
            'value': val,
            'color': ''
        })
        val += break_val
    t = CHOROPLETH_NUMBER_OF_BREAKS - 1
    for element in reversed(result):
        element['color'] = colors[t]
        t -= 1
        if t <= -1:
            break
    return result


def generate_population_count_categories(
        is_province_layer: bool,
        session: MapSession,
        filter_species_name: str):
    """
    Generate population count categories from species.
    This function will read from materialized view from MapSession.

    :param is_province_layer: True if this is for province layer
    :param session: map filter session
    :param filter_species_name: map filter by species name
    :return: list of dict of minLabel, maxLabel, value and color
    """
    min, max = get_count_summary_of_population(is_province_layer, session)
    base_color = DEFAULT_BASE_COLOR
    taxon = Taxon.objects.filter(scientific_name=filter_species_name).first()
    if taxon and taxon.colour:
        base_color = taxon.colour
    return generate_population_count_categories_base(min, max, base_color)


def create_map_materialized_view(view_name: str, sql: str, query_values):
    """
    Execute sql to create materialized view.

    :param view_name: name of the materialized view
    :param sql: the SQL for the materialized view
    :param query_values: list of query values
    """
    view_sql = (
        """
        CREATE MATERIALIZED VIEW "{view_name}"
        AS {sql}
        """
    ).format(
        view_name=view_name,
        sql=sql
    )
    index_sql = (
        """
        CREATE UNIQUE INDEX "{view_name}_idx" ON "{view_name}" (id)
        """
    ).format(view_name=view_name)
    with connection.cursor() as cursor:
        cursor.execute(view_sql, query_values)
        cursor.execute(index_sql)
        if '_province' in view_name:
            # need to add index by name
            index_sql = (
                """
                CREATE UNIQUE INDEX "{view_name}_name_idx"
                ON "{view_name}" (name)
                """
            ).format(view_name=view_name)
            cursor.execute(index_sql)


def drop_map_materialized_view(view_name: str):
    """
    Execute sql to drop materialized view.

    :param view_name: name of the materialized view
    """
    view_sql = (
        """
        DROP MATERIALIZED VIEW IF EXISTS "{view_name}"
        """
    ).format(view_name=view_name)
    with connection.cursor() as cursor:
        cursor.execute(view_sql)


def delete_expired_map_materialized_view():
    """Remove expired materialized view."""
    sessions = MapSession.objects.filter(
        expired_date__lt=timezone.now()
    )
    total_count = sessions.count()
    for session in sessions:
        session.delete()
    return total_count


def generate_map_view(
        session: MapSession,
        is_province_view: bool,
        filter_start_year: int = None,
        filter_end_year: int = None,
        filter_species_name: str = None,
        filter_organisation: str = None,
        filter_activity: str = None,
        filter_spatial: str = None,
        filter_property: str = None):
    """
    Generate materialized view from map filter session.

    :param session: map filter session
    :param is_province_view: True only if there is filter_species_name
    and user can view province layer
    :param filter_start_year: filter by start year
    :param filter_end_year: filter by end year
    :param filter_species_name: filter by species name
    :param filter_organisation: filter by organisation id list
    :param filter_activity: filter by activity list
    :param filter_spatial: property spatial filter list
    :param filter_property: filter by property id list
    """
    if is_province_view:
        drop_map_materialized_view(session.province_view_name)
    else:
        drop_map_materialized_view(session.properties_view_name)
    if filter_organisation == 'all' and not session.user.is_superuser:
        # get user organisation ids
        org_ids = OrganisationUser.objects.filter(
            user=session.user
        ).values_list('organisation_id', flat=True).distinct()
        filter_organisation = ','.join(map(str, org_ids))
    is_choropleth_layer = True if filter_species_name else False
    if is_choropleth_layer:
        if is_province_view:
            sql_view, query_values = get_province_population_query(
                filter_start_year, filter_end_year, filter_species_name,
                filter_organisation, filter_activity, filter_spatial,
                filter_property
            )
        else:
            sql_view, query_values = get_properties_population_query(
                filter_start_year, filter_end_year, filter_species_name,
                filter_organisation, filter_activity, filter_spatial,
                filter_property
            )
    else:
        sql_view, query_values = get_properties_query(
            filter_organisation, filter_spatial, filter_property
        )
    create_map_materialized_view(
        session.province_view_name if is_province_view else
        session.properties_view_name, sql_view, query_values
    )
    # store queryparams
    query_params = (
        """
        start_year={start_year}&end_year={end_year}&species={species}&
        organisation={organisation}&activity={activity}&
        spatial_filter_values={spatial_filter_values}&property={property}
        """
    ).format(
        start_year=filter_start_year,
        end_year=filter_end_year,
        species=filter_species_name,
        organisation=filter_organisation,
        activity=filter_activity,
        spatial_filter_values=filter_spatial,
        property=filter_property
    )
    session.query_params = query_params
    session.save(update_fields=['query_params'])
