from typing import Dict, List, Any
from population_data.models import AnnualPopulation

from frontend.static_mapping import ACTIVITY_COLORS_DICT
from django.db.models import QuerySet, Sum, Q
from property.models import Property
from species.models import OwnedSpecies


def calculate_species_count_per_province(
        queryset,
        species_name: str
) -> Dict[str, int]:
    property_ids = [query.id for query in queryset]

    # Filter properties by the provided property ids
    if property_ids:
        queryset = queryset.filter(id__in=property_ids)

        # Retrieve species data per property and province
        species_data = (
            OwnedSpecies.objects.filter(
                property__in=queryset,
                taxon__scientific_name=species_name
            )
            .values(
                "property__province__name",
                "taxon__scientific_name",
                "annualpopulation__year"
            )
            .annotate(total=Sum("annualpopulation__total"))
        )

        # Group the data by province, species, and year
        grouped_data = {}
        for item in species_data:
            province_name = item["property__province__name"]
            species_name = item["taxon__scientific_name"]
            year = item["annualpopulation__year"]
            total = item["total"]

            key = (province_name, species_name, year)
            if key in grouped_data:
                grouped_data[key] += total
            else:
                grouped_data[key] = total

        # Format the result data
        result_data = []
        for (
            province_name,
            species_name, year
        ), total in grouped_data.items():
            result_data.append({
                "province": province_name,
                "species": species_name,
                "year": year,
                "count": total,
            })

    return result_data


def calculate_population_categories(
    queryset,
    species_name: str,
    categories: list = None
) -> Dict[str, int]:
    """
    Calculate population categories for a given queryset of properties.

    Args:
        queryset (QuerySet): A queryset of properties.
        species_name (str): The name of the species.

    Returns:
        Dict[str, int]: A dictionary containing population categories
        as keys and their corresponding counts as values.

    This function takes a queryset of properties and calculates
    population categories based on annual population data.
    It retrieves the annual population data for the
    specified properties and species provided, calculates
    the minimum and maximum populations,
    creates 6 population categories, and counts
    the properties in each category.

    The result is a dictionary
    with population categories as keys and
    their counts as values.
    """

    # Extract property IDs from the queryset
    property_ids = [query.id for query in queryset]

    # Fetch the annual population data for the specified property IDs
    annual_population_data = AnnualPopulation.objects.filter(
        owned_species__property__id__in=property_ids,
        owned_species__taxon__scientific_name=species_name
    ).values(
        'year'
    ).annotate(
        # Calculate the sum of total populations for each year
        population_total=Sum('total')
    ).order_by(
        'year'
    )

    # Handle the case where annual_population_data is empty
    try:
        # Calculate the minimum and maximum for category boundaries
        min_population = min(
            item['population_total'] for item in annual_population_data
        )
        max_population = max(
            item['population_total'] for item in annual_population_data
        )
    except ValueError:
        return {}

    # Calculate the category width (create 6 groups minimum)
    category_width = (max_population - min_population) / 6

    # Create the population categories
    categories = [int(min_population + category_width * i) for i in range(6)]

    results = {}

    # Iterate through the annual_population_data
    # and count properties in each category
    for item in annual_population_data:
        population = item['population_total']
        year = item['year']

        # Assign the category based on the population
        category = None
        for i in range(len(categories) - 1):
            if categories[i] <= population < categories[i + 1]:
                category = f'{categories[i]}-{categories[i+1]}'
                break
        else:
            category = f'>{categories[-1]}'

        # Create a unique key for each year and category
        key = f'{year}_{category}'

        # Increment the count for the key
        if key in results:
            results[key]['property_count'] += 1
        else:
            results[key] = {'year': year, 'property_count': 1}

    # Convert the results dictionary to the final format
    result = {key: value for key, value in results.items()}

    return result



def calculate_total_area_available_to_species(
    queryset: QuerySet[Property],
    species_name: str) -> List[Dict[str, int]]:
    """
    Calculate the total area available to species for
    each property in the queryset.

    Params:
        queryset (QuerySet[Property]): The queryset of properties for
        which to calculate total area available to species.

    Returns:
        List[Dict[str, int]]: A list of dictionaries,
        each containing the property name and
        the total area available to species for that property.
    """

    properties = []
    for property in queryset:
        year_to_area_mapping = {}

        # Check if species_name is provided
        if species_name:
            owned_species_query = OwnedSpecies.objects.filter(
                Q(property=property),
                Q(taxon__common_name_varbatim=species_name) |
                Q(taxon__scientific_name=species_name)
            )
        else:
            owned_species_query = OwnedSpecies.objects.filter(
                property=property
            )

        for owned_species in owned_species_query:
            annual_population_data = AnnualPopulation.objects.filter(
                owned_species__property=property)
            for annual_population in annual_population_data:
                year = annual_population.year
                area_available = owned_species.area_available_to_species
                if year in year_to_area_mapping:
                    year_to_area_mapping[year] += area_available
                else:
                    year_to_area_mapping[year] = area_available

        for year, area_total in year_to_area_mapping.items():
            # Check if an entry for the same year already exists
            existing_entry = next(
                (entry for entry in properties if entry["year"] == year), None
            )
            if existing_entry:
                existing_entry["area"] += area_total
            else:
                data = {
                    "species": species_name if species_name else None,
                    "property_name": property.name.capitalize(),
                    "year": year,
                    "organisation_name": property.organisation.name,
                    "province_name": property.province.name,
                    "area": area_total
                }
                properties.append(data)

    return properties


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
    property_ids = OwnedSpecies.objects.filter(
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
