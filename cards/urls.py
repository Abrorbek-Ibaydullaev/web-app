"""
Card URLs
cards/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CardViewSet, ChecklistViewSet, ChecklistItemViewSet,
    CommentViewSet, AttachmentViewSet
)

router = DefaultRouter()
router.register(r'', CardViewSet, basename='card')
router.register(r'checklists', ChecklistViewSet, basename='checklist')
router.register(r'checklist-items', ChecklistItemViewSet, basename='checklist-item')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]