"""
Card Serializers
cards/serializers.py
"""

from rest_framework import serializers
from .models import (
    Card, CardMember, CardLabel, Checklist, ChecklistItem,
    Attachment, Comment, CommentMention
)
from users.serializers import UserSerializer
from boards.serializers import LabelSerializer


class ChecklistItemSerializer(serializers.ModelSerializer):
    """Serializer for ChecklistItem"""
    
    assigned_to_user = UserSerializer(source='assigned_to', read_only=True)
    completed_by_user = UserSerializer(source='completed_by', read_only=True)
    
    class Meta:
        model = ChecklistItem
        fields = [
            'id', 'checklist', 'title', 'is_completed', 'position',
            'due_date', 'assigned_to', 'assigned_to_user',
            'completed_at', 'completed_by', 'completed_by_user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'completed_at', 'completed_by', 'created_at', 'updated_at']


class ChecklistSerializer(serializers.ModelSerializer):
    """Serializer for Checklist"""
    
    items = ChecklistItemSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Checklist
        fields = [
            'id', 'card', 'title', 'position', 'items', 'progress',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_progress(self, obj):
        """Calculate checklist progress"""
        total = obj.items.count()
        if total == 0:
            return 0
        completed = obj.items.filter(is_completed=True).count()
        return round((completed / total) * 100, 2)


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment"""
    
    uploaded_by_user = UserSerializer(source='uploaded_by', read_only=True)
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'card', 'file_name', 'file_url', 'file_type',
            'file_size', 'thumbnail_url', 'uploaded_by', 'uploaded_by_user',
            'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment"""
    
    user_details = UserSerializer(source='user', read_only=True)
    mentioned_users = UserSerializer(many=True, read_only=True, source='mentions')
    
    class Meta:
        model = Comment
        fields = [
            'id', 'card', 'user', 'user_details', 'content', 'is_edited',
            'mentioned_users', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_edited', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create comment and handle mentions"""
        request = self.context.get('request')
        comment = Comment.objects.create(
            user=request.user,
            **validated_data
        )
        return comment


class CardMemberSerializer(serializers.ModelSerializer):
    """Serializer for card members"""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    assigned_by_user = UserSerializer(source='assigned_by', read_only=True)
    
    class Meta:
        model = CardMember
        fields = ['id', 'user', 'user_id', 'assigned_by', 'assigned_by_user', 'assigned_at']
        read_only_fields = ['id', 'assigned_by', 'assigned_at']


class CardLabelSerializer(serializers.ModelSerializer):
    """Serializer for card labels"""
    
    label_details = LabelSerializer(source='label', read_only=True)
    
    class Meta:
        model = CardLabel
        fields = ['id', 'label', 'label_details', 'created_at']
        read_only_fields = ['id', 'created_at']


class CardSerializer(serializers.ModelSerializer):
    """Serializer for Card model"""
    
    created_by_user = UserSerializer(source='created_by', read_only=True)
    members_count = serializers.SerializerMethodField()
    checklists_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Card
        fields = [
            'id', 'list', 'title', 'description', 'position',
            'cover_type', 'cover_value', 'due_date', 'is_completed', 'is_archived',
            'created_by', 'created_by_user', 'members_count', 'checklists_count',
            'attachments_count', 'comments_count',
            'created_at', 'updated_at', 'archived_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'archived_at']
    
    def get_members_count(self, obj):
        return obj.card_members.count()
    
    def get_checklists_count(self, obj):
        return obj.checklists.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class CardDetailSerializer(CardSerializer):
    """Detailed serializer for Card with all relationships"""
    
    card_members = CardMemberSerializer(many=True, read_only=True)
    card_labels = CardLabelSerializer(many=True, read_only=True)
    checklists = ChecklistSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta(CardSerializer.Meta):
        fields = CardSerializer.Meta.fields + [
            'card_members', 'card_labels', 'checklists', 'attachments', 'comments'
        ]


class MoveCardSerializer(serializers.Serializer):
    """Serializer for moving cards"""
    
    list_id = serializers.UUIDField(required=True)
    position = serializers.IntegerField(min_value=0, required=True)