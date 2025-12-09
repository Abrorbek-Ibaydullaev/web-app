"""
Notification Models
notifications/models.py
"""

import uuid
from django.db import models
from django.utils import timezone
from users.models import User
from boards.models import Board
from cards.models import Card


class Notification(models.Model):
    """Notification model for user notifications"""
    
    TYPE_CHOICES = [
        ('mention', 'Mention'),
        ('assignment', 'Assignment'),
        ('due_date', 'Due Date'),
        ('comment', 'Comment'),
        ('card_moved', 'Card Moved'),
        ('board_invite', 'Board Invite'),
        ('workspace_invite', 'Workspace Invite'),
        ('card_completed', 'Card Completed'),
        ('checklist_completed', 'Checklist Completed'),
        ('attachment_added', 'Attachment Added'),
        ('member_added', 'Member Added'),
        ('member_removed', 'Member Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link_url = models.URLField(max_length=500, blank=True)
    
    is_read = models.BooleanField(default=False)
    
    related_board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='triggered_notifications'
    )
    
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save()
    
    @staticmethod
    def create_notification(user, type, title, message='', link_url='', 
                          related_board=None, related_card=None, related_user=None):
        """Helper method to create notifications"""
        return Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            link_url=link_url,
            related_board=related_board,
            related_card=related_card,
            related_user=related_user
        )