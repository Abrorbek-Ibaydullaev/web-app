from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    related_user_details = UserSerializer(source='related_user', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'link_url', 'is_read',
            'related_board', 'related_card', 'related_user', 'related_user_details',
            'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

