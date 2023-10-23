from django.urls import path, re_path
from species.api_views.upload_species import (
    SaveCsvSpecies,
    SpeciesUploader,
    UploadSpeciesStatus,
)

from .views import (
    TaxonFrontPageListAPIView,
    TaxonListAPIView,
    TaxonTrendPageAPIView
)

urlpatterns = [
    path('api/species/front-page/list/', TaxonFrontPageListAPIView.as_view(),
         name='species-front-page'),
    re_path(r'^api/species/trend-page/?$',
            TaxonTrendPageAPIView.as_view(),
            name='taxon-trend-page'),
    path('species/', TaxonListAPIView.as_view(),
         name='species'),
    path('api/upload-species/', SpeciesUploader.as_view(),
         name='upload-species'),
    path('api/save-csv-species/', SaveCsvSpecies.as_view(),
         name='save-csv-species'),
    re_path(r'api/upload-species-status/(?P<token>[\da-f-]+)/?$',
            UploadSpeciesStatus.as_view(),
            name='upload-species-status'
            ),

]
