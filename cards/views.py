"""
Card Views
cards/views.py
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Card, CardMember, Checklist, ChecklistItem, Attachment, Comment
from lists.models import List
from users.models import User
from .serializers import (
    CardSerializer, CardDetailSerializer, CardMemberSerializer, MoveCardSerializer,
    ChecklistSerializer, ChecklistItemSerializer, AttachmentSerializer, CommentSerializer
)


class CardViewSet(viewsets.ModelViewSet):
    """ViewSet for Card operations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return cards for boards where user is a member"""
        queryset = Card.objects.filter(
            list__board__members=self.request.user
        ).distinct()
        
        # Filter by list
        list_id = self.request.query_params.get('list')
        if list_id:
            queryset = queryset.filter(list_id=list_id)
        
        # Filter archived
        is_archived = self.request.query_params.get('archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
        else:
            queryset = queryset.filter(is_archived=False)
        
        return queryset.order_by('position')
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'retrieve':
            return CardDetailSerializer
        return CardSerializer
    
    def perform_create(self, serializer):
        """Create card with current user as creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive card"""
        card = self.get_object()
        card.archive()
        return Response({'message': 'Card archived successfully'})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore card from archive"""
        card = self.get_object()
        card.restore()
        return Response({'message': 'Card restored successfully'})
    
    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        """Move card to different list/position"""
        card = self.get_object()
        serializer = MoveCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_list_id = serializer.validated_data['list_id']
        new_position = serializer.validated_data['position']
        
        new_list = get_object_or_404(List, id=new_list_id)
        old_list = card.list
        
        card.list = new_list
        card.position = new_position
        card.save()
        
        return Response(CardSerializer(card).data)
    
    # Member operations
    @action(detail=True, methods=['post'])
    def assign_member(self, request, pk=None):
        """Assign member to card"""
        card = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, id=user_id)
        
        if CardMember.objects.filter(card=card, user=user).exists():
            return Response({'error': 'User is already assigned'}, status=status.HTTP_400_BAD_REQUEST)
        
        card_member = CardMember.objects.create(
            card=card,
            user=user,
            assigned_by=request.user
        )
        
        return Response(CardMemberSerializer(card_member).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='remove_member/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        """Remove member from card"""
        card = self.get_object()
        CardMember.objects.filter(card=card, user_id=user_id).delete()
        return Response({'message': 'Member removed successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    # Checklist operations
    @action(detail=True, methods=['post'])
    def add_checklist(self, request, pk=None):
        """Add checklist to card"""
        card = self.get_object()
        serializer = ChecklistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checklist = serializer.save(card=card)
        return Response(ChecklistSerializer(checklist).data, status=status.HTTP_201_CREATED)
    
    # Comment operations
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get card comments"""
        card = self.get_object()
        comments = card.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to card"""
        card = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(card=card, user=request.user)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    
    # Attachment operations
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add attachment to card"""
        card = self.get_object()
        serializer = AttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(card=card, uploaded_by=request.user)
        return Response(AttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)


class ChecklistViewSet(viewsets.ModelViewSet):
    """ViewSet for Checklist operations"""
    
    serializer_class = ChecklistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Checklist.objects.filter(card__list__board__members=self.request.user).distinct()


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """ViewSet for ChecklistItem operations"""
    
    serializer_class = ChecklistItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChecklistItem.objects.filter(
            checklist__card__list__board__members=self.request.user
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle checklist item completion"""
        item = self.get_object()
        item.is_completed = not item.is_completed
        if item.is_completed:
            item.completed_by = request.user
        else:
            item.completed_by = None
        item.save()
        return Response(ChecklistItemSerializer(item).data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment operations"""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(
            card__list__board__members=self.request.user
        ).distinct()
    
    def perform_update(self, serializer):
        """Mark comment as edited when updated"""
        serializer.save(is_edited=True)


class AttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Attachment operations"""
    
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Attachment.objects.filter(
            card__list__board__members=self.request.user
        ).distinct()