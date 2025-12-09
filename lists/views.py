"""
List Views
lists/views.py
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import List
from .serializers import ListSerializer, ListDetailSerializer, MoveListSerializer


class ListViewSet(viewsets.ModelViewSet):
    """ViewSet for List operations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return lists for boards where user is a member"""
        queryset = List.objects.filter(
            board__members=self.request.user
        ).distinct()
        
        # Filter by board
        board_id = self.request.query_params.get('board')
        if board_id:
            queryset = queryset.filter(board_id=board_id)
        
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
            return ListDetailSerializer
        return ListSerializer
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive list"""
        list_obj = self.get_object()
        list_obj.archive()
        return Response({
            'message': 'List archived successfully'
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore list from archive"""
        list_obj = self.get_object()
        list_obj.restore()
        return Response({
            'message': 'List restored successfully'
        })
    
    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        """Move list to new position"""
        list_obj = self.get_object()
        serializer = MoveListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_position = serializer.validated_data['position']
        old_position = list_obj.position
        
        if new_position == old_position:
            return Response(ListSerializer(list_obj).data)
        
        # Update positions
        lists_in_board = List.objects.filter(
            board=list_obj.board,
            is_archived=False
        ).exclude(id=list_obj.id).order_by('position')
        
        # Reorder
        if new_position > old_position:
            # Moving right
            for lst in lists_in_board:
                if old_position < lst.position <= new_position:
                    lst.position -= 1
                    lst.save()
        else:
            # Moving left
            for lst in lists_in_board:
                if new_position <= lst.position < old_position:
                    lst.position += 1
                    lst.save()
        
        list_obj.position = new_position
        list_obj.save()
        
        return Response(ListSerializer(list_obj).data)