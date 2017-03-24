from django.conf.urls import url, include
from core import views as core_views
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hip-help/', include([
        url(r'capabilities.json', core_views.capabilities, name='capabilities'),
        url(r'installed', core_views.installed, name='installed'),
        url(r'help', core_views.help, name='help'),
    ])),
]
