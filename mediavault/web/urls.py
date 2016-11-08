"""
URL patterns for 'web' app
"""
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^home/', views.home, name='home'),
    url(r'^explore/', views.explore, name='explore')
]
