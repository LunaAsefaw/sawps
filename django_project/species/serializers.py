from django.db.models import Sum
from population_data.models import AnnualPopulation
from rest_framework import serializers
from species.models import OwnedSpecies, Taxon


class TaxonSerializer(serializers.ModelSerializer):
    """Species serializer"""

    class Meta:
        model = Taxon
        fields = [
            "id",
            "scientific_name",
            # common name is used to autofill common
            # name in online form
            "common_name_varbatim"
        ]


class FrontPageTaxonSerializer(serializers.ModelSerializer):
    """Display species data on FrontPage."""
    species_name = serializers.CharField(source='scientific_name')
    total_population = serializers.SerializerMethodField()
    total_area = serializers.SerializerMethodField()

    def get_total_population(self, obj: Taxon):
        # get latest year from current species
        latest_data_per_year = AnnualPopulation.objects.filter(
            owned_species__taxon=obj
        ).order_by(
            'owned_species__property', '-year'
        ).distinct(
            'owned_species__property'
        )
        data = AnnualPopulation.objects.filter(
            id__in=latest_data_per_year,
            owned_species__taxon=obj
        ).aggregate(Sum('total'))
        return data['total__sum'] if data['total__sum'] else 0

    def get_total_area(self, obj: Taxon):
        data = OwnedSpecies.objects.filter(
            taxon=obj
        ).aggregate(Sum('area_available_to_species'))
        return (
            data['area_available_to_species__sum'] if
            data['area_available_to_species__sum'] else 0
        )


    class Meta:
        model = Taxon
        fields = [
            'id',
            'species_name',
            'icon',
            'total_population',
            'total_area',
            'colour'
        ]
