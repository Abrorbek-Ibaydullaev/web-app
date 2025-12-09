"""
List Models
lists/models.py
"""

import uuid
from django.db import models
from django.utils import timezone
from boards.models import Board


class List(models.Model):
    """List model (columns in a board)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='lists'
    )
    name = models.CharField(max_length=255)
    position = models.IntegerField(default=0, help_text="Order position in the board")
    
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'lists'
        verbose_name = 'List'
        verbose_name_plural = 'Lists'
        ordering = ['position']
        indexes = [
            models.Index(fields=['board']),
            models.Index(fields=['board', 'position']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.board.name}"
    
    def archive(self):
        """Archive the list"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore the list from archive"""
        self.is_archived = False
        self.archived_at = None
        self.save()
    
    def save(self, *args, **kwargs):
        """Auto-assign position if not provided"""
        if self.position == 0 and not self.pk:
            # Get the highest position in this board
            max_position = List.objects.filter(
                board=self.board
            ).aggregate(models.Max('position'))['position__max']
            self.position = (max_position or 0) + 1
        super().save(*args, **kwargs)