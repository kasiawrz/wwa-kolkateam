from django.conf.urls import url, include


urlpatterns = [
    url(r'^hip-help/', include([
        url(r'capabilities.json', )
    ])),
]
