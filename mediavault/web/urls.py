"""
URL patterns for 'web' app
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/?', views.login, name='explore'),
    url(r'^shared-items/?$', views.shared_items, name='shared-items'),
    url(r'^shared-items/(?P<id>[0-9]+)/?$', views.single_shared_item,
        name='single-shared-item')
]
