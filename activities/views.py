from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Activity
from .serializers import ActivitySerializer

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Activity (read-only)"""
    
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return activities for boards where user is a member"""
        queryset = Activity.objects.filter(
            board__members=self.request.user
        ).distinct()
        
        # Filter by board
        board_id = self.request.query_params.get('board')
        if board_id:
            queryset = queryset.filter(board_id=board_id)
        
        # Filter by card
        card_id = self.request.query_params.get('card')
        if card_id:
            queryset = queryset.filter(card_id=card_id)
        
        return queryset.order_by('-created_at')[:50]  # Limit to 50 recent activities

