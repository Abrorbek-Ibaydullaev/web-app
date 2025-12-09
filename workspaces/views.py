"""
Workspace Views
workspaces/views.py
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Workspace, WorkspaceMember
from users.models import User
from .serializers import (
    WorkspaceSerializer,
    WorkspaceDetailSerializer,
    WorkspaceMemberSerializer,
    AddWorkspaceMemberSerializer
)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for Workspace operations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return workspaces where user is a member"""
        return Workspace.objects.filter(
            members=self.request.user
        ).distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'retrieve':
            return WorkspaceDetailSerializer
        return WorkspaceSerializer
    
    def perform_create(self, serializer):
        """Create workspace with current user as owner"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get workspace members"""
        workspace = self.get_object()
        members = workspace.workspace_members.all()
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to workspace"""
        workspace = self.get_object()
        
        # Check if user is admin
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user
        ).first()
        
        if not member or member.role != 'admin':
            return Response(
                {'error': 'Only admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AddWorkspaceMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data['role']
        
        # Check if user is already a member
        if WorkspaceMember.objects.filter(
            workspace=workspace,
            user_id=user_id
        ).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add member
        user = get_object_or_404(User, id=user_id)
        workspace_member = WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=role
        )
        
        return Response(
            WorkspaceMemberSerializer(workspace_member).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['delete'], url_path='remove_member/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        """Remove member from workspace"""
        workspace = self.get_object()
        
        # Check if user is admin
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user
        ).first()
        
        if not member or member.role != 'admin':
            return Response(
                {'error': 'Only admins can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot remove owner
        user_to_remove = get_object_or_404(User, id=user_id)
        if user_to_remove == workspace.owner:
            return Response(
                {'error': 'Cannot remove workspace owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove member
        WorkspaceMember.objects.filter(
            workspace=workspace,
            user_id=user_id
        ).delete()
        
        return Response(
            {'message': 'Member removed successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['patch'], url_path='update_member_role/(?P<user_id>[^/.]+)')
    def update_member_role(self, request, pk=None, user_id=None):
        """Update member role"""
        workspace = self.get_object()
        
        # Check if user is admin
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user
        ).first()
        
        if not member or member.role != 'admin':
            return Response(
                {'error': 'Only admins can update member roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_role = request.data.get('role')
        if new_role not in ['admin', 'member', 'observer']:
            return Response(
                {'error': 'Invalid role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update member role
        workspace_member = get_object_or_404(
            WorkspaceMember,
            workspace=workspace,
            user_id=user_id
        )
        workspace_member.role = new_role
        workspace_member.save()
        
        return Response(
            WorkspaceMemberSerializer(workspace_member).data
        )