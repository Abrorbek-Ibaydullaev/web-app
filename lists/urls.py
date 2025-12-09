"""
List URLs
lists/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListViewSet

router = DefaultRouter()
router.register(r'', ListViewSet, basename='list')

urlpatterns = [
    path('', include(router.urls)),
]