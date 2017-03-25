from django.conf.urls import url, include
from core import views as core_views
from answers import views as answers_views
from django.contrib import admin

urlpatterns = [
    url(r'^hip-help/', include([
        url(r'^$', core_views.home, name='home'),
        url(r'^admin/', admin.site.urls),
        url(r'capabilities.json', core_views.capabilities, name='capabilities'),
        url(r'installed', core_views.installed, name='installed'),
        url(r'uninstalled', core_views.uninstalled, name='uninstalled'),
        url(r'listener', core_views.listener, name='listener'),
        url(r'help', core_views.help, name='help'),
        url(r'summary/(?P<room_name>[a-zA-Z0-9_-]+)', answers_views.summary, name='summary'),
        url(r'fetch-data-for-all-rooms/', answers_views.fetch_data_for_all_rooms, name='fetch-data')
    ])),
]
