"""
Board Views
boards/views.py
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Board, BoardMember, BoardStar, Label
from users.models import User
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardMemberSerializer,
    AddBoardMemberSerializer,
    LabelSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """ViewSet for Board operations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return boards where user is a member"""
        queryset = Board.objects.filter(
            members=self.request.user
        ).distinct()
        
        # Filter by workspace if provided
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        # Filter archived
        is_archived = self.request.query_params.get('archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
        else:
            queryset = queryset.filter(is_archived=False)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardSerializer
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive board"""
        board = self.get_object()
        board.archive()
        return Response({
            'message': 'Board archived successfully'
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore board from archive"""
        board = self.get_object()
        board.restore()
        return Response({
            'message': 'Board restored successfully'
        })
    
    @action(detail=True, methods=['post'])
    def star(self, request, pk=None):
        """Star/favorite a board"""
        board = self.get_object()
        star, created = BoardStar.objects.get_or_create(
            board=board,
            user=request.user
        )
        
        if created:
            return Response({
                'message': 'Board starred successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Board already starred'
            })
    
    @action(detail=True, methods=['post'])
    def unstar(self, request, pk=None):
        """Unstar/unfavorite a board"""
        board = self.get_object()
        deleted = BoardStar.objects.filter(
            board=board,
            user=request.user
        ).delete()
        
        if deleted[0] > 0:
            return Response({
                'message': 'Board unstarred successfully'
            })
        else:
            return Response({
                'message': 'Board was not starred'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get board members"""
        board = self.get_object()
        members = board.board_members.all()
        serializer = BoardMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to board"""
        board = self.get_object()
        
        # Check if user is admin
        member = BoardMember.objects.filter(
            board=board,
            user=request.user
        ).first()
        
        if not member or member.role != 'admin':
            return Response(
                {'error': 'Only admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AddBoardMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data['role']
        
        # Check if user is already a member
        if BoardMember.objects.filter(
            board=board,
            user_id=user_id
        ).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add member
        user = get_object_or_404(User, id=user_id)
        board_member = BoardMember.objects.create(
            board=board,
            user=user,
            role=role
        )
        
        return Response(
            BoardMemberSerializer(board_member).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['delete'], url_path='remove_member/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        """Remove member from board"""
        board = self.get_object()
        
        # Check if user is admin
        member = BoardMember.objects.filter(
            board=board,
            user=request.user
        ).first()
        
        if not member or member.role != 'admin':
            return Response(
                {'error': 'Only admins can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cannot remove creator
        user_to_remove = get_object_or_404(User, id=user_id)
        if user_to_remove == board.created_by:
            return Response(
                {'error': 'Cannot remove board creator'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove member
        BoardMember.objects.filter(
            board=board,
            user_id=user_id
        ).delete()
        
        return Response(
            {'message': 'Member removed successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['get'])
    def labels(self, request, pk=None):
        """Get board labels"""
        board = self.get_object()
        labels = board.labels.all()
        serializer = LabelSerializer(labels, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_label(self, request, pk=None):
        """Create a new label"""
        board = self.get_object()
        
        serializer = LabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        label = serializer.save(board=board)
        
        return Response(
            LabelSerializer(label).data,
            status=status.HTTP_201_CREATED
        )


class LabelViewSet(viewsets.ModelViewSet):
    """ViewSet for Label operations"""
    
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return labels for boards where user is a member"""
        return Label.objects.filter(
            board__members=self.request.user
        ).distinct()