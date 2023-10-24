from django.conf import settings
from .base_view import RegisteredOrganisationBaseView
from django.http import HttpResponseRedirect
from django.urls import reverse


def redirect_to_reports(request):
    tab_number = 1
    redirect_url = f"{reverse('map')}?tab={tab_number}"
    return HttpResponseRedirect(redirect_url)


def redirect_to_charts(request):
    tab_number = 2
    redirect_url = f"{reverse('map')}?tab={tab_number}"
    return HttpResponseRedirect(redirect_url)


def redirect_to_trends(request):
    tab_number = 3
    redirect_url = f"{reverse('map')}?tab={tab_number}"
    return HttpResponseRedirect(redirect_url)


def redirect_to_upload(request):
    tab_number = 4
    redirect_url = f"{reverse('map')}?tab={tab_number}"
    return HttpResponseRedirect(redirect_url)


def redirect_to_explore(request):
    tab_number = 0
    redirect_url = f"{reverse('map')}?tab={tab_number}"
    return HttpResponseRedirect(redirect_url)


class MapView(RegisteredOrganisationBaseView):
    """
    MapView displays the map page by rendering the 'map.html' template.
    """

    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['maptiler_api_key'] = settings.MAPTILER_API_KEY
        return ctx
