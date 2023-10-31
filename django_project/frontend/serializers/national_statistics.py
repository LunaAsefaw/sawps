from typing import List
from django.db.models import Q, Sum
from population_data.models import AnnualPopulation
from rest_framework import serializers
from species.models import Taxon
from datetime import datetime


class SpeciesListSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing species.
    """
    species_name = serializers.SerializerMethodField()
    species_colour = serializers.SerializerMethodField()
    icon = serializers.ImageField(use_url=True)
    annualpopulation_count = serializers.SerializerMethodField()
    total_population = serializers.SerializerMethodField()
    total_area = serializers.SerializerMethodField()

    class Meta:
        model = Taxon
        fields = [
            "id",
            "species_name",
            "species_colour",
            "icon",
            "annualpopulation_count",
            "total_population",
            "total_area"
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

    def get_species_icon(self, obj: Taxon) -> str:
        """Get the icon of the species.
        Params:
            obj (Taxon): The Taxon instance representing the species.
        """
        return obj.icon.url

    def get_annualpopulation_count(self, obj: Taxon) -> List[dict]:
        """Get the population count per year for the species.
        Params:
            obj (Taxon): The Taxon instance representing the species.
        """

        current_year = datetime.now().year
        start_year = current_year - 10  # should start from 10 years before
        end_year = current_year
        annual_populations = (
            AnnualPopulation.objects.filter(
                Q(
                    year__range=(start_year, end_year)
                ) if start_year and end_year else Q(),
                taxon=obj
            )
            .values("year")
            .annotate(year_total=Sum("total"))
            .values(
                "year",
                "year_total",
                "sub_adult_male",
                "sub_adult_female",
                "adult_male",
                "adult_female",
                "juvenile_male",
                "juvenile_female"
            )
            .order_by("-year")[:10]
        )
        return list(annual_populations)

    def get_total_population(self, obj: Taxon):
        # get latest year from current species
        latest_data_per_year = AnnualPopulation.objects.filter(
            taxon=obj
        ).order_by(
            'property', '-year'
        ).distinct(
            'property'
        )
        data = AnnualPopulation.objects.filter(
            id__in=latest_data_per_year,
            taxon=obj
        ).aggregate(Sum('total'))
        return data['total__sum'] if data['total__sum'] else 0

    def get_total_area(self, obj: Taxon):
        data = AnnualPopulation.objects.filter(
            taxon=obj
        ).aggregate(Sum('area_available_to_species'))
        return (
            data['area_available_to_species__sum'] if
            data['area_available_to_species__sum'] else 0
        )


class NationalStatisticsSerializer(serializers.Serializer):
    total_property_count = serializers.IntegerField()
    total_property_area = serializers.FloatField()
    total_area_available_to_species = serializers.FloatField()
