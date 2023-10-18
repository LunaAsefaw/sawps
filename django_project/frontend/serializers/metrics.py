from typing import List
from frontend.static_mapping import YEAR_DATA_LIMIT
from django.db.models import (
    F,
    Q,
    Sum
)
from population_data.models import AnnualPopulation
from property.models import Property
from rest_framework import serializers
from species.models import OwnedSpecies, Taxon


class SpeciesPopuationCountPerYearSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing population count per year for a species.
    """
    species_name = serializers.SerializerMethodField()
    species_colour = serializers.SerializerMethodField()
    annualpopulation_count = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = [
            "species_name",
            "species_colour",
            "annualpopulation_count",
        ]

    def get_species_name(self, obj: Taxon) -> str:
        """Get the common name of the species.
        Params:
            obj (Taxon): The Taxon instance representing the species.
        """
        return obj.common_name_varbatim

    def get_species_colour(self, obj: Taxon) -> str:
        """Get the color of the species.
        Params:
            obj (Taxon): The Taxon instance representing the species.
        """
        return obj.colour

    def get_annualpopulation_count(self, obj: Taxon) -> List[dict]:
        """Get the population count per year for the species.
        Params:
            obj (Taxon): The Taxon instance representing the species.
        """
        start_year = self.context["request"].GET.get("start_year")
        end_year = self.context["request"].GET.get("end_year")
        property = self.context['request'].GET.get('property')
        annual_populations = (
            AnnualPopulation.objects.filter(
                Q(
                    year__range=(start_year, end_year)
                ) if start_year and end_year else Q(),
                Q(
                    owned_species__property__id__in=property.split(",")
                ) if property else Q(),
                owned_species__taxon=obj
            )
            .values("year")
            .annotate(year_total=Sum("total"))
            .values("year", "year_total")
            .order_by("-year")[:10]
        )
        return list(annual_populations)


class ActivityMatrixSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing activity percentage data for species.
    """
    total = serializers.SerializerMethodField()
    species_name = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = [
            "total",
            "species_name",
            "graph_icon",
            "activities",
        ]

    def get_total(self, obj) -> int:
        """Get the total count of species.
        Params: obj (Taxon): The Taxon instance.
        """
        property = self.context['request'].GET.get('property')
        property_list = property.split(',') if property else []
        owned_species = OwnedSpecies.objects.values(
            "taxon__common_name_varbatim").filter(taxon=obj)
        if property_list:
            owned_species = owned_species.filter(
                property__id__in=property_list,
            )
        owned_species = owned_species.annotate(
            total=Sum("annualpopulation__total")
        )
        if owned_species.exists():
            return owned_species[0].get("total")
        else:
            return None

    def get_species_name(self, obj) -> str:
        """Get the species name.
        Params: obj (Taxon): The Taxon instance.
        """
        return obj.common_name_varbatim

    def get_activities(self, obj) -> List[dict]:
        """Calculate activity percentage data for species.
        Params: obj (Taxon): The Taxon instance.
        """
        property = self.context['request'].GET.get('property')
        property_list = property.split(',') if property else []
        owned_species = OwnedSpecies.objects.values(
            "taxon__common_name_varbatim"
        ).filter(taxon=obj)

        if property_list:
            owned_species = owned_species.filter(
                property__id__in=property_list
            )

        owned_species = owned_species.annotate(
            total=Sum("annualpopulationperactivity__total")
        ).values("annualpopulationperactivity__activity_type__name", "total")

        total_count = self.get_total(obj)
        activities_list = []

        for item in owned_species:
            activity_type = item[
                "annualpopulationperactivity__activity_type__name"
            ]
            total = item["total"]

            if activity_type and total:
                percentage = (
                    total / total_count
                ) * 100 if total_count else None
                activity_data = {
                    activity_type: percentage,
                    "activity_total": total
                }
                activities_list.append(activity_data)

        return activities_list


class TotalCountPerPopulationEstimateSerializer(serializers.Serializer):
    def get_total_counts_per_population_estimate(self):
        """
        Retrieves and calculates the total counts per
        population estimate category.

        This function filters AnnualPopulation records
        based on the provided parameters
        (species_name, property_ids).
        It then iterates through the filtered records and calculates
        the total counts per population estimate category,
        along with the most recent year and total sums associated
        with each category.

        Returns:
        - result (dict): A dictionary containing total counts per
        population estimate category.
            Each category includes count, years, total, and percentage.
        """

        # Extract filter parameters from the request context
        species_name = self.context["request"].GET.get("species")
        property_list = self.context['request'].GET.get('property')
        property_ids = property_list.split(',') if property_list else []

        # Initialize a dictionary to store the results
        result = {}

        start_year = self.context["request"].GET.get('start_year')
        end_year = self.context["request"].GET.get('end_year')
        try:
            start_year = int(start_year)
            end_year = int(end_year)
            max_year = max(start_year, end_year)
        except (ValueError, TypeError):
            max_year = None  # if the input is not valid integers

        # Query AnnualPopulation model to filter records
        # for the most recent year
        annual_populations = (
            AnnualPopulation.objects.filter(
                Q(
                    owned_species__property__id__in=property_ids
                ) if property_ids else Q(),
                Q(
                    Q(
                        owned_species__taxon__common_name_varbatim=(
                            species_name
                        )
                    ) |
                    Q(owned_species__taxon__scientific_name=species_name)
                ) if species_name else Q(),
                year=max_year,
            )
        )

        # Iterate through filtered records
        for record in annual_populations:
            population_estimate_category = (
                record.population_estimate_category.name
            )
            year = record.year
            total = record.total

            # Calculate percentage against the total
            percentage = (total / total) * 100 if total > 0 else 0

            # Create or update the result dictionary
            if population_estimate_category not in result:
                result[population_estimate_category] = {
                    "count": 1,
                    "years": [year],
                    "total": total,
                    "percentage": percentage
                }
            elif year in result[population_estimate_category]["years"]:
                result[population_estimate_category]["count"] += 1
                result[population_estimate_category]["total"] += total
            else:
                result[population_estimate_category]["years"].append(year)
                result[population_estimate_category]["count"] += 1
                result[population_estimate_category]["total"] += total

        # Initialize a dictionary to store the final results
        final_result = {}

        # Iterate over the result again to calculate the percentages
        for category, data in result.items():
            count = data["count"]
            total = data["total"]

            # Calculate percentage as count divided by total * 100
            percentage = (count / total) * 100 if total > 0 else 0

            # Create the final result entry
            final_result[category] = {
                "count": count,
                "years": data["years"],
                "total": total,
                "percentage": percentage,
            }

        return final_result


class TotalCountPerActivitySerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing the total count per activity data.
    """
    total = serializers.SerializerMethodField()
    species_name = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = [
            "total",
            "species_name",
            "graph_icon",
            "activities",
            "colour"
        ]

    def get_total(self, obj) -> int:
        """Get the total count of species.
        Params: obj (Taxon): The Taxon instance.
        """
        property = self.context['request'].GET.get('property')
        property_list = property.split(',') if property else []
        owned_species = OwnedSpecies.objects.values(
            "taxon__common_name_varbatim").filter(taxon=obj)
        if property_list:
            owned_species = owned_species.filter(
                property__id__in=property_list,
            )
        owned_species = owned_species.annotate(
            total=Sum("annualpopulationperactivity__total")
        )
        if owned_species.exists():
            return owned_species[0].get("total")
        else:
            return None

    def get_species_name(self, obj) -> str:
        """Get the species name.
        Params: obj (Taxon): The Taxon instance.
        """
        return obj.common_name_varbatim


    def get_activities(self, obj) -> List[dict]:
        """Calculate total count per activity for species.
        Params: obj (Taxon): The Taxon instance.
        """
        property_param = self.context['request'].GET.get('property')
        property_list = property_param.split(',') if property_param else []

        q_filters = Q(taxon=obj)
        if property_list:
            q_filters &= Q(property__id__in=property_list)

        owned_species = OwnedSpecies.objects.values(
            activity_type=F(
                "annualpopulationperactivity__activity_type__name"),
            year=F("annualpopulationperactivity__year"),
            total=Sum("annualpopulationperactivity__total"),
        ).filter(q_filters)

        activities_list = [
            {
                "activity_type": item["activity_type"],
                "year": item["year"],
                "total": item["total"],
            }
            for item in owned_species
            if item["activity_type"] and item["total"]
        ]
        return activities_list


class SpeciesPopulationDensityPerPropertySerializer(
    serializers.ModelSerializer
):
    """
    Serializer class for serializing species population total and density.
    """
    density = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    organisation_name = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "density",
            "province_name",
            "organisation_name"
        ]

    def get_province_name(self, obj):
        return obj.province.name if obj.province else None

    def get_organisation_name(self, obj):
        return obj.organisation.name if obj.organisation else None

    def get_density(self, obj) -> dict:
        species_name = self.context.get("species_name")
        if not species_name:
            return None

        owned_species_data = (
            OwnedSpecies.objects.filter(
                property=obj,
                taxon__scientific_name=species_name
            )
            .values("property__name")
            .annotate(
                total=Sum("annualpopulation__total"),
                property_in_ha=Sum("property__property_size_ha"),
                year=F("annualpopulation__year"),
            )
        )

        # Calculate density and format data
        result_data = []
        for data in owned_species_data:
            total = data.get("total")
            property_in_ha = data.get("property_in_ha")
            year = data.get("year")

            if total and property_in_ha:
                density = total / property_in_ha
            else:
                density = None

            property_name = data.get("property__name").capitalize()

            result_data.append({
                "property_name": property_name,
                "density": density,
                "species_name": species_name,
                "year": year,
            })

        return result_data


class PopulationPerAgeGroupSerialiser(serializers.ModelSerializer):
    """
    Serializer class for serializing population per age group.
    """
    age_group = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = ["age_group", "graph_icon", "common_name_varbatim", "colour"]

    def get_age_group(self, obj) -> dict:
        """ Calculate population per age group.
        Params: obj (Taxon): The Taxon instance.
        """
        sum_fields = [
            "adult_male",
            "adult_female",
            "sub_adult_male",
            "sub_adult_female",
            "juvenile_male",
            "juvenile_female",
            "year"
        ]

        filters = {
            "owned_species__taxon": obj
        }

        property_list = self.context['request'].GET.get("property")
        if property_list:
            property_ids = property_list.split(",")
            filters["owned_species__property__id__in"] = property_ids

        start_year = self.context['request'].GET.get("start_year")
        if start_year:
            end_year = self.context['request'].GET.get("end_year")
            filters["year__range"] = (start_year, end_year)

        age_groups_totals = (
            AnnualPopulation.objects
            .values("owned_species__taxon__common_name_varbatim")
            .filter(**filters)
            .annotate(
                **{
                    f"total_{field}": (
                        Sum(field) if field != 'year' else F('year')
                    )
                    for field in sum_fields
                }
            )
        )

        return age_groups_totals


class AnnualPopulationSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing AnnualPopulation.
    """
    class Meta:
        model = AnnualPopulation
        fields = (
            'year',
            'survey_method'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owned_species'] = instance.owned_species
        data['owned_species__taxon'] = instance.owned_species.taxon
        data['owned_species__property'] = instance.owned_species.property
        data['owned_species__property__province'] = (
            instance.owned_species.property.province
        )
        data['owned_species__property__property_type'] = (
            instance.owned_species.property.property_type
        )
        return data


class TotalAreaVSAvailableAreaSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing total area and available area.
    """
    area = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = ["area", "common_name_varbatim"]

    def get_area(self, obj) -> list:
        """ Calculate and get total area and available area.
        Params: obj (Taxon): The Taxon instance.
        """

        filters = {}
        property_list = self.context['request'].GET.get("property")
        if property_list:
            property_ids = property_list.split(",")
            filters["property__id__in"] = property_ids

        start_year = self.context['request'].GET.get("start_year")
        if start_year:
            end_year = self.context['request'].GET.get("end_year")
            filters["annualpopulation__year__range"] = (start_year, end_year)

        owned_species = OwnedSpecies.objects.values(
            "annualpopulation__year",
        ).filter(**filters, taxon=obj).annotate(
            area_total=Sum("property__property_size_ha"),
            area_available=Sum("area_available_to_species")
        )
        data = {
            "owned_species": owned_species
        }
        if len(owned_species) > YEAR_DATA_LIMIT:
            data = {
                "owned_species": owned_species[:YEAR_DATA_LIMIT],
                "message": "Only last 10 years data are displayed \
                for search with >10 years data returned"
            }

        return data
