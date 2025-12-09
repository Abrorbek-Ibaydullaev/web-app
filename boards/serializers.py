"""
Board Serializers
boards/serializers.py
"""

from rest_framework import serializers
from .models import Board, BoardMember, BoardStar, Label
from users.serializers import UserSerializer


class LabelSerializer(serializers.ModelSerializer):
    """Serializer for Label model"""
    
    class Meta:
        model = Label
        fields = ['id', 'name', 'color', 'board', 'created_at', 'updated_at']
        read_only_fields = ['id', 'board', 'created_at', 'updated_at']


class BoardMemberSerializer(serializers.ModelSerializer):
    """Serializer for board members"""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = BoardMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board model"""
    
    created_by = UserSerializer(read_only=True)
    lists_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    is_starred_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = [
            'id', 'workspace', 'name', 'slug', 'description',
            'background_type', 'background_value', 'visibility',
            'is_template', 'is_starred', 'is_archived',
            'created_by', 'lists_count', 'members_count', 
            'is_starred_by_user', 'created_at', 'updated_at', 'archived_at'
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'created_at', 'updated_at', 'archived_at']
    
    def get_lists_count(self, obj):
        return obj.lists.filter(is_archived=False).count()
    
    def get_members_count(self, obj):
        return obj.board_members.count()
    
    def get_is_starred_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return BoardStar.objects.filter(
                board=obj,
                user=request.user
            ).exists()
        return False
    
    def create(self, validated_data):
        """Create board and add creator as admin"""
        request = self.context.get('request')
        board = Board.objects.create(
            created_by=request.user,
            **validated_data
        )
        # Add creator as admin member
        BoardMember.objects.create(
            board=board,
            user=request.user,
            role='admin'
        )
        return board


class BoardDetailSerializer(BoardSerializer):
    """Detailed serializer for Board with members and labels"""
    
    board_members = BoardMemberSerializer(many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    
    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ['board_members', 'labels']


class AddBoardMemberSerializer(serializers.Serializer):
    """Serializer for adding members to board"""
    
    user_id = serializers.UUIDField(required=True)
    role = serializers.ChoiceField(
        choices=['admin', 'member', 'observer'],
        default='member'
    )
    
    def validate_user_id(self, value):
        """Validate user exists"""
        from users.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value