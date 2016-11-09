"""
URL patterns for 'api' app
"""
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^explore/', views.explore)
]
