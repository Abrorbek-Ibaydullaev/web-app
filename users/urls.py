"""
User URLs
users/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('profile/update/', UserViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='profile-update'),
    path('password/change/', UserViewSet.as_view({'post': 'change_password'}), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]