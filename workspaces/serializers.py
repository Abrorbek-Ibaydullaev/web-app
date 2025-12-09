"""
Workspace Serializers
workspaces/serializers.py
"""

from rest_framework import serializers
from .models import Workspace, WorkspaceMember
from users.serializers import UserSerializer


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Serializer for workspace members"""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Workspace model"""
    
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    boards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'description', 'logo_url',
            'owner', 'is_active', 'members_count', 'boards_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.workspace_members.count()
    
    def get_boards_count(self, obj):
        return obj.boards.count()
    
    def create(self, validated_data):
        """Create workspace and add owner as admin"""
        request = self.context.get('request')
        workspace = Workspace.objects.create(
            owner=request.user,
            **validated_data
        )
        # Add owner as admin member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=request.user,
            role='admin'
        )
        return workspace


class WorkspaceDetailSerializer(WorkspaceSerializer):
    """Detailed serializer for Workspace with members"""
    
    workspace_members = WorkspaceMemberSerializer(many=True, read_only=True)
    
    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + ['workspace_members']


class AddWorkspaceMemberSerializer(serializers.Serializer):
    """Serializer for adding members to workspace"""
    
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