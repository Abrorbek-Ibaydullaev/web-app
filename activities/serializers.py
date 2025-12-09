from rest_framework import serializers
from .models import Activity
from users.serializers import UserSerializer

class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'board', 'card', 'user', 'user_details',
            'action_type', 'action_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']