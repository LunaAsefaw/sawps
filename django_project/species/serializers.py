from django.db.models import Sum
from population_data.models import AnnualPopulation
from rest_framework import serializers
from species.models import Taxon


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
        populations = AnnualPopulation.objects.filter(
            taxon=obj
        )
        latest = populations.order_by('-year').first()
        if not latest:
            return 0
        data = AnnualPopulation.objects.filter(
            taxon=obj,
            year=latest.year
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


class TrendPageTaxonSerializer(FrontPageTaxonSerializer):
    """Display species data on TrendPage."""
    species_name = serializers.CharField(source='scientific_name')

    class Meta:
        model = Taxon
        fields = [
            'id',
            'species_name',
            'graph_icon',
            'total_population',
            'total_area',
            'colour'
        ]
