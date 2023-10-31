from frontend.utils.organisation import get_current_organisation_id
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Taxon
from .serializers import (
    FrontPageTaxonSerializer,
    TaxonSerializer,
    TrendPageTaxonSerializer
)

# Create your views here.


class TaxonListAPIView(APIView):
    """Get taxon within the organisations"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organisation_id = get_current_organisation_id(self.request.user)
        organisation = self.request.GET.get("organisation")
        if organisation:
            _organisation = organisation.split(",")
            taxon = Taxon.objects.filter(
                annualpopulation__property__organisation_id__in=(
                    [int(id) for id in _organisation]
                ),
                annualpopulation__taxon__taxon_rank__name__iexact="Species"
            ).order_by("scientific_name").distinct()
        else:
            taxon = Taxon.objects.filter(
                annualpopulation__property__organisation_id=organisation_id,
                taxon_rank__name="Species"
            ).order_by("scientific_name").distinct()

        return Response(
            status=200,
            data=TaxonSerializer(taxon, many=True).data
        )


class TaxonFrontPageListAPIView(APIView):
    """Fetch taxon list to display on FrontPage."""
    permission_classes = [AllowAny]

    def get(self, request):
        taxon = Taxon.objects.filter(
            show_on_front_page=True).order_by('front_page_order')
        return Response(
            status=200,
            data=FrontPageTaxonSerializer(taxon, many=True).data
        )


class TaxonTrendPageAPIView(APIView):
    """Fetch taxon detail to display on TrendPage."""
    permission_classes = [AllowAny]

    def get(self, request):
        species_name = request.GET.get('species', '')
        try:
            taxon = Taxon.objects.get(scientific_name=species_name)
        except Taxon.DoesNotExist:
            return Response(
                status=200,
                data={}
            )
        return Response(
            status=200,
            data=TrendPageTaxonSerializer(taxon).data
        )
