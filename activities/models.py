"""
Activity Models
activities/models.py
"""

import uuid
from django.db import models
from django.utils import timezone
from users.models import User
from boards.models import Board
from cards.models import Card


class Activity(models.Model):
    """Activity log for tracking all actions"""
    
    ACTION_TYPES = [
        # Board actions
        ('board_created', 'Board Created'),
        ('board_updated', 'Board Updated'),
        ('board_archived', 'Board Archived'),
        ('board_restored', 'Board Restored'),
        ('board_member_added', 'Board Member Added'),
        ('board_member_removed', 'Board Member Removed'),
        
        # List actions
        ('list_created', 'List Created'),
        ('list_updated', 'List Updated'),
        ('list_moved', 'List Moved'),
        ('list_archived', 'List Archived'),
        ('list_restored', 'List Restored'),
        
        # Card actions
        ('card_created', 'Card Created'),
        ('card_updated', 'Card Updated'),
        ('card_moved', 'Card Moved'),
        ('card_archived', 'Card Archived'),
        ('card_restored', 'Card Restored'),
        ('card_completed', 'Card Completed'),
        ('card_member_added', 'Card Member Added'),
        ('card_member_removed', 'Card Member Removed'),
        ('card_label_added', 'Card Label Added'),
        ('card_label_removed', 'Card Label Removed'),
        ('card_due_date_set', 'Card Due Date Set'),
        ('card_due_date_changed', 'Card Due Date Changed'),
        ('card_due_date_removed', 'Card Due Date Removed'),
        
        # Checklist actions
        ('checklist_created', 'Checklist Created'),
        ('checklist_updated', 'Checklist Updated'),
        ('checklist_deleted', 'Checklist Deleted'),
        ('checklist_item_completed', 'Checklist Item Completed'),
        ('checklist_item_uncompleted', 'Checklist Item Uncompleted'),
        
        # Attachment actions
        ('attachment_added', 'Attachment Added'),
        ('attachment_deleted', 'Attachment Deleted'),
        
        # Comment actions
        ('comment_added', 'Comment Added'),
        ('comment_updated', 'Comment Updated'),
        ('comment_deleted', 'Comment Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action_type = models.CharField(max_length=100, choices=ACTION_TYPES)
    action_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data about the action"
    )
    
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'activities'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['board']),
            models.Index(fields=['card']),
            models.Index(fields=['user']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()}"
    
    @staticmethod
    def log_activity(user, action_type, board=None, card=None, action_data=None):
        """Helper method to log activities"""
        return Activity.objects.create(
            user=user,
            action_type=action_type,
            board=board,
            card=card,
            action_data=action_data or {}
        )