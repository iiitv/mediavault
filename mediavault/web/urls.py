"""
URL patterns for 'web' app
"""
from django.conf.urls import url
from django.conf.urls.static import static

from mediavault import settings
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/?', views.login, name='explore'),
    url(r'^shared-items/?$', views.shared_items, name='shared-items'),
    url(r'^shared-items/(?P<id>[0-9]+)/?$', views.single_shared_item,
        name='single-shared-item'),
    url(r'^media/(?P<id>[0-9]+)/?$', views.media_page, name='media-page'),
    url(r'^media-get/(?P<id>[0-9]+)/?$', views.media_get, name='media-get'),
    url(r'^explore/?$', views.explore_root, name='explore-root'),
    url(r'^explore/(?P<id>[0-9]+)/?$', views.explore, name='explore')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
