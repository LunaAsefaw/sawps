"""frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from frontend.api_views.data_table import DataTableAPIView
from frontend.api_views.map import (
    AerialTile,
    ContextLayerList,
    FindParcelByCoord,
    FindPropertyByCoord,
    MapAuthenticate,
    MapStyles,
    PropertiesLayerMVTTiles,
)
from frontend.api_views.metrics import (
    ActivityPercentageAPIView,
    PropertiesPerPopulationCategoryAPIView,
    SpeciesPopuationCountPerYearAPIView,
    TotalAreaPerPropertyTypeAPIView,
    SpeciesPopulationDensityPerPropertyAPIView,
    SpeciesPopulationCountPerProvinceAPIView,
    TotalCountPerActivityAPIView,
    TotalAreaAvailableToSpeciesAPIView,
    PopulationPerAgeGroupAPIView,
    TotalAreaVSAvailableAreaAPIView,
    TotalCountPerPopulationEstimateAPIView
)
from frontend.api_views.population import (
    DraftPopulationUpload,
    FetchDraftPopulationUpload,
    PopulationMetadataList,
    UploadPopulationAPIVIew,
)
from frontend.api_views.property import (
    CreateNewProperty,
    PropertyDetail,
    PropertyList,
    PropertyMetadataList,
    UpdatePropertyBoundaries,
    UpdatePropertyInformation,
    PropertySearch
)
from frontend.api_views.spatial_filter import (
    SpatialFilterList
)
from frontend.api_views.statistical import (
    SpeciesNationalTrend,
    SpeciesTrend
)
from frontend.api_views.upload import (
    BoundaryFileList,
    BoundaryFileRemove,
    BoundaryFileSearch,
    BoundaryFileSearchStatus,
    BoundaryFileUpload,
)
from frontend.views.base_view import get_user_notifications
from .api_views.user import UserInfoAPIView

from .views.about import AboutView
from .views.contact import ContactUsView
from .views.help import HelpView
from .views.home import HomeView
from .views.map import (
    MapView,
    redirect_to_reports,
    redirect_to_charts,
    redirect_to_trends,
    redirect_to_upload,
    redirect_to_explore
)
from .views.online_form import OnlineFormView
from .views.switch_organisation import switch_organisation
from .views.totp_device import (
    add_totp_device,
    delete_totp_device,
    view_totp_devices
)
from .views.users import OrganisationUsersView
from frontend.api_views.national_statistic import (
    NationalStatisticsView,
    NationalSpeciesView,
    NationalPropertiesView,
    NationalActivityCountView,
    NationalActivityCountPerProvinceView,
    NationalActivityCountPerPropertyView
)
from .views.organisations import (
    OrganisationsView,
    organization_detail,
    save_permissions
)

urlpatterns = [
    re_path(
        r'^api/map/search/parcel/?$',
        FindParcelByCoord.as_view(),
        name='find-parcel'
    ),
    re_path(
        r'^api/map/search/property/?$',
        FindPropertyByCoord.as_view(),
        name='find-property'
    ),
    re_path(
        r'^api/map/search/context_layer/list/?$',
        ContextLayerList.as_view(),
        name='context-layer-list'
    ),
    re_path(
        r'^api/map/styles/?$',
        MapStyles.as_view(),
        name='map-style'
    ),
    re_path(
        r'^api/map/authenticate/?$',
        MapAuthenticate.as_view(),
        name='map-authenticate'
    ),
    re_path(
        r'^api/map/layer/aerial/'
        r'(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/?$',
        AerialTile.as_view(),
        name='aerial-map-layer'
    ),
    re_path(
        r'^api/map/layer/properties/'
        r'(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/?$',
        PropertiesLayerMVTTiles.as_view(),
        name='properties-map-layer'
    ),
    re_path(
        r'^api/property/create/?$',
        CreateNewProperty.as_view(),
        name='property-create'
    ),
    re_path(
        r'^api/property/list/(?P<organisation_id>\d+)?/?$',
        PropertyList.as_view(),
        name='property-list'
    ),
    re_path(
        r'^api/property/detail/(?P<id>\d+)/?$',
        PropertyDetail.as_view(),
        name='property-detail'
    ),
    re_path(
        r'^api/property/detail/update/?$',
        UpdatePropertyInformation.as_view(),
        name='property-update-detail'
    ),
    re_path(
        r'^api/property/search/?$',
        PropertySearch.as_view(),
        name='property-search'
    ),
    re_path(
        r'^api/property/boundaries/update/?$',
        UpdatePropertyBoundaries.as_view(),
        name='property-update-boundaries'
    ),
    re_path(
        r'^api/property/metadata/list/?$',
        PropertyMetadataList.as_view(),
        name='property-metadata'
    ),
    re_path(
        r'^api/upload/boundary-file/remove/?$',
        BoundaryFileRemove.as_view(),
        name='boundary-file-remove'
    ),
    re_path(
        r'^api/upload/boundary-file/(?P<session>[\da-f-]+)/list/?$',
        BoundaryFileList.as_view(),
        name='boundary-file-list'
    ),
    re_path(
        r'^api/upload/boundary-file/(?P<session>[\da-f-]+)/search/?$',
        BoundaryFileSearch.as_view(),
        name='boundary-file-search'
    ),
    re_path(
        r'^api/upload/boundary-file/(?P<session>[\da-f-]+)/status/?$',
        BoundaryFileSearchStatus.as_view(),
        name='boundary-file-status'
    ),
    re_path(
        r'^api/upload/boundary-file/?$',
        BoundaryFileUpload.as_view(),
        name='boundary-file-upload'
    ),
    re_path(
        r'^api/population/metadata/list/?$',
        PopulationMetadataList.as_view(),
        name='population-metadata'
    ),
    re_path(
        r'^api/upload/population/(?P<property_id>\d+)/?$',
        UploadPopulationAPIVIew.as_view(),
        name='population-upload'
    ),
    re_path(
        r'^api/species/(?P<species_id>\d+)/trend/national/?$',
        SpeciesNationalTrend.as_view(),
        name='species-national-trend'
    ),
    path(
        'api/species/population_trend/',
        SpeciesTrend.as_view(),
        name='species-population-trend'
    ),
    path(
        'api/upload/population/draft/<uuid:draft_uuid>/',
        FetchDraftPopulationUpload.as_view(),
        name='fetch-draft-upload-species'
    ),
    path(
        'api/upload/population/draft/<int:property_id>/',
        DraftPopulationUpload.as_view(),
        name='draft-upload-species'
    ),
    path(
        'switch-organisation/<int:organisation_id>/',
        switch_organisation,
        name='switch-organisation'
    ),
    path('map/', MapView.as_view(), name='map'),
    path(
        'reports/',
        redirect_to_reports,
        name='reports'
    ),
    path(
        'charts/',
        redirect_to_charts,
        name='charts'
    ),
    path(
        'trends/',
        redirect_to_trends,
        name='trends'
    ),
    path(
        'upload/',
        redirect_to_upload,
        name='upload'
    ),
    path(
        'explore/',
        redirect_to_explore,
        name='explore'
    ),
    path(
        'upload-data/<int:property_id>/',
        OnlineFormView.as_view(),
        name='online-form'
    ),
    path('help/', HelpView.as_view(), name='help'),
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('users/', OrganisationUsersView.as_view(), name='Users'),
    path(
        'organisations/<str:slug>/',
        OrganisationsView.as_view(),
        name='organisations'
    ),
    path('contact/', ContactUsView.as_view(), name='contact'),
    path('api/data-table/', DataTableAPIView.as_view(), name='data-table'),
    path(
        'api/species-population-count/',
        SpeciesPopuationCountPerYearAPIView.as_view(),
        name='species_population_count'
    ),
    path(
        'api/activity-percentage/',
        ActivityPercentageAPIView.as_view(),
        name='activity_percentage'
    ),
    path(
        'api/total-count-per-activity/',
        TotalCountPerActivityAPIView.as_view(),
        name='total_count_per_activity'
    ),
    path(
        'api/species-population-total-density/',
        SpeciesPopulationDensityPerPropertyAPIView.as_view(),
        name='species_population_total_density'
    ),
    path(
        'api/total-count-per-population-estimate/',
        TotalCountPerPopulationEstimateAPIView.as_view(),
        name='total-count-per-population-estimate'
    ),
    path(
        'api/species-count-per-province/',
        SpeciesPopulationCountPerProvinceAPIView.as_view(),
        name='species_count_per_province'
    ),
    path(
        'api/properties-per-population-category/',
        PropertiesPerPopulationCategoryAPIView.as_view(),
        name='properties_per_population_category'
    ),
    path(
        'api/total-area-available-to-species/',
        TotalAreaAvailableToSpeciesAPIView.as_view(),
        name='total_area_available_to_species'
    ),
    path(
        'api/total-area-per-property-type/',
        TotalAreaPerPropertyTypeAPIView.as_view(),
        name='total_area_per_property_type'
    ),
    path(
        'api/population-per-age-group/',
        PopulationPerAgeGroupAPIView.as_view(),
        name='population_per_age_group'
    ),
    path(
        'api/total-area-vs-available-area/',
        TotalAreaVSAvailableAreaAPIView.as_view(),
        name='total_area_vs_available_area'
    ),
    path(
        'add_totp_devices/',
        add_totp_device,
        name='add_totp_devices'
    ),
    path(
        'view_totp_devices/',
        view_totp_devices,
        name='view_totp_devices'
    ),
    path(
        'delete_totp_device/<int:device_id>/',
        delete_totp_device,
        name='delete_totp_device'
    ),
    path(
        'get_user_notifications/',
        get_user_notifications,
        name='get_user_notifications'
    ),
    path(
        'api/species-list/',
        NationalSpeciesView.as_view(),
        name='species_list_national'
    ),
    path(
        'api/statistics/',
        NationalStatisticsView.as_view(),
        name='statistics_national'
    ),
    path(
        'api/properties_population_category/',
        NationalPropertiesView.as_view(),
        name='properties_population_category'
    ),
    path(
        'api/activity_count_percentage/',
        NationalActivityCountView.as_view(),
        name='activity_count'
    ),
    path(
        'api/activity_count_per_province/',
        NationalActivityCountPerProvinceView.as_view(),
        name='activity_count_per_province'
    ),
    path(
        'api/activity_count_per_property/',
        NationalActivityCountPerPropertyView.as_view(),
        name='activity_count_per_property'
    ),
    path(
        'api/organization/<int:identifier>/',
        organization_detail,
        name='organization_detail_by_id'
    ),
    path(
        'save_permissions/<int:organisation_id>/',
        save_permissions,
        name='save_permissions'
    ),
    path(
        'api/spatial-filter-list/',
        SpatialFilterList.as_view(),
        name='spatial-filter-list'
    ),
    path(
        'api/user-info/',
        UserInfoAPIView.as_view(),
        name='user-info-api'
    )
]
