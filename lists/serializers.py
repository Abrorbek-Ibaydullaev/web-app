"""
List Serializers
lists/serializers.py
"""

from rest_framework import serializers
from .models import List


class ListSerializer(serializers.ModelSerializer):
    """Serializer for List model"""
    
    cards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = List
        fields = [
            'id', 'board', 'name', 'position', 'is_archived',
            'cards_count', 'created_at', 'updated_at', 'archived_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archived_at']
    
    def get_cards_count(self, obj):
        return obj.cards.filter(is_archived=False).count()


class ListDetailSerializer(ListSerializer):
    """Detailed serializer for List with cards"""
    
    from cards.serializers import CardSerializer
    cards = CardSerializer(many=True, read_only=True)
    
    class Meta(ListSerializer.Meta):
        fields = ListSerializer.Meta.fields + ['cards']


class MoveListSerializer(serializers.Serializer):
    """Serializer for moving lists"""
    
    position = serializers.IntegerField(min_value=0, required=True)