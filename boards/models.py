"""
Board Models
boards/models.py
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from users.models import User
from workspaces.models import Workspace


class Board(models.Model):
    """Board model"""
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('workspace', 'Workspace'),
        ('public', 'Public'),
    ]
    
    BACKGROUND_TYPE_CHOICES = [
        ('color', 'Color'),
        ('gradient', 'Gradient'),
        ('image', 'Image'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='boards',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    background_type = models.CharField(
        max_length=50,
        choices=BACKGROUND_TYPE_CHOICES,
        default='color'
    )
    background_value = models.TextField(blank=True, help_text="Hex color, gradient CSS, or image URL")
    
    visibility = models.CharField(
        max_length=50,
        choices=VISIBILITY_CHOICES,
        default='private'
    )
    
    is_template = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_boards'
    )
    members = models.ManyToManyField(
        User,
        through='BoardMember',
        related_name='boards'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'boards'
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_archived']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def archive(self):
        """Archive the board"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore the board from archive"""
        self.is_archived = False
        self.archived_at = None
        self.save()


class BoardMember(models.Model):
    """Board membership with roles"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('observer', 'Observer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='board_members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='board_memberships'
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'board_members'
        verbose_name = 'Board Member'
        verbose_name_plural = 'Board Members'
        unique_together = [['board', 'user']]
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['board']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.board.name} ({self.role})"


class BoardStar(models.Model):
    """Board stars for quick access"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='stars'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='starred_boards'
    )
    starred_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'board_stars'
        verbose_name = 'Board Star'
        verbose_name_plural = 'Board Stars'
        unique_together = [['board', 'user']]
        ordering = ['-starred_at']
    
    def __str__(self):
        return f"{self.user.username} starred {self.board.name}"


class Label(models.Model):
    """Labels for cards"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='labels'
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50, help_text="Hex color code")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'labels'
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'
        ordering = ['name']
        indexes = [
            models.Index(fields=['board']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.board.name})"