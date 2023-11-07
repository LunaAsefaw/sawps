import datetime
from typing import Dict, List, Any, Tuple
from population_data.models import AnnualPopulation

from frontend.static_mapping import ACTIVITY_COLORS_DICT
from django.db.models import QuerySet, Sum, Min, Max
from property.models import Property

CATEGORY_LABELS = 'category_labels'
YEAR_LABELS = 'years'
CATEGORY_DATA = 'data'


def calculate_species_count_per_province(
        taxon,
        filters
) -> Dict[str, int]:

    annual_populations = AnnualPopulation.objects.select_related(
        'property__province'
    ).filter(
        **filters, taxon=taxon
    ).order_by('-year').distinct('year', 'property__province')

    result_data = dict()

    for pop_data in annual_populations:
        print(pop_data.property.province, pop_data.total)
        data = {
            "year": pop_data.year,
            "count": pop_data.total,
            "province": pop_data.property.province.name,
            "species": pop_data.taxon.scientific_name,
        }
        key = f'{pop_data.year}-{pop_data.property.province.name}'
        if key in result_data:
            result_data[key]['count'] += pop_data.total
        else:
            result_data[key] = data

    return result_data.values()


def calculate_population_categories(
        queryset,
        species_name: str,
        year_range: Tuple[int] = None
) -> Dict[str, int]:
    """
    Calculate population categories for a given queryset of properties.

    Args:
        queryset (QuerySet): A queryset of properties.
        species_name (str): The name of the species.
        year_range (Tuple[int]): Start year and end year.

    Returns:
        Dict[str, Any]: A dictionary containing:
        - CATEGORY_LABELS: List of population category labels.
        - YEAR_LABELS: List of years for which the data is available.
        - CATEGORY_DATA: List of dictionaries with year, property count,
            and population category details.

    This function takes a queryset of properties and the name of a species.
    It calculates population categories based on annual population
    data for the specified species across
    the provided properties.
    It retrieves the annual population data, calculates
    the minimum and maximum populations,
    creates 6 population categories, and counts
    the number of properties in each category for each year.
    """

    if not year_range:
        year_range = (1960, datetime.datetime.now().year)

    # Extract property IDs from the queryset
    property_ids = list(set(
        queryset.values_list('id', flat=True)
    ))

    # Fetch the annual population data for the specified property IDs
    annual_population_data = AnnualPopulation.objects.filter(
        property__in=property_ids,
        taxon__scientific_name=species_name,
        year__range=year_range
    ).distinct()

    if not annual_population_data.exists():
        return {}

    min_population, max_population = annual_population_data.aggregate(
        Min('total'), Max('total')
    ).values()

    # Calculate the category width (create 6 groups minimum)
    category_width = (max_population - min_population) / 6

    # Create the population categories
    category_count = 1 if category_width == 0 else 6
    categories = [
        int(min_population + category_width * i)
        for i in range(category_count)
    ]
    category_labels = []

    results = []

    for index, category in enumerate(categories):
        if len(categories) == 1:
            max_category = categories[index]
            category_key = f'{category}-{max_category}'
        elif len(categories) - 1 > index:
            max_category = categories[index + 1]
            category_key = f'{category}-{max_category}'
        else:
            max_category = max_population
            category_key = f'>{category}'

        category_labels.append(category_key)

        for year in annual_population_data.values_list(
                'year', flat=True).distinct():
            annual_population_data_by_category = annual_population_data.filter(
                total__gte=category,
                total__lte=max_category,
                year=year
            )
            property_count = (
                annual_population_data_by_category.values(
                    'property').distinct().count()
            )

            results.append({
                'year': year,
                'category': category_key,
                'property_count': property_count
            })

    return {
        CATEGORY_LABELS: category_labels,
        YEAR_LABELS: sorted(set(
            int(year) for year in annual_population_data.values_list(
                'year', flat=True)
        )),
        CATEGORY_DATA: results
    }


def calculate_total_area_per_property_type(
    queryset: QuerySet,
    species_name: str) -> List[dict]:
    """
    Calculate the total area per property type
    for a given queryset of properties.
    Params:
        queryset (QuerySet): The queryset of Property objects.
        species_name: filter results by species
    Returns:
        list[dict]: A list of dictionaries, each containing property_type
                    and total_area keys representing the property type name
                    and the aggregated total area respectively.
    """
    # Filter the properties based on the owned species
    property_ids = AnnualPopulation.objects.filter(
        taxon__scientific_name=species_name
    ).values_list('property_id', flat=True)

    # Calculate the total area for each property type
    properties_type_area = Property.objects.filter(
        id__in=property_ids
    ).values('property_type__name').annotate(
        total_area=Sum('property_size_ha')
    ).values('property_type__name', 'created_at', 'name', 'total_area')

    return properties_type_area


def calculate_base_population_of_species(data: List[Dict[str, Any]]) \
    -> Dict[str, Any]:
    """
    Calculate base population of species and modify the input data.
    Params:
        data (List[Dict[str, Any]]): List of dictionaries
        representing species data.
    Returns:
        Dict[str, Any]: A dictionary containing modified species
        data with base percentages and activity colors.
    """
    calculated_data = []
    for species in data:
        activities_total = sum(
            activity["activity_total"] for activity in species["activities"]
        )
        if species["total"]:
            base = species["total"] - activities_total
            base_percentage = (
                base / species["total"]
            ) * 100 if base else None
            species["activities"].append({"Base population": base_percentage})
            calculated_data.append(species)
    species_data = {
        "data": calculated_data,
        "activity_colours": ACTIVITY_COLORS_DICT
    }
    return species_data
