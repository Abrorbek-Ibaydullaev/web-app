"""
Card Models
cards/models.py
"""

import uuid
from django.db import models
from django.utils import timezone
from lists.models import List
from users.models import User
from boards.models import Label


class Card(models.Model):
    """Card model (tasks in a list)"""
    
    COVER_TYPE_CHOICES = [
        ('color', 'Color'),
        ('image', 'Image'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    position = models.IntegerField(default=0, help_text="Order position in the list")
    
    cover_type = models.CharField(
        max_length=50,
        choices=COVER_TYPE_CHOICES,
        blank=True,
        null=True
    )
    cover_value = models.TextField(blank=True, help_text="Hex color or image URL")
    
    due_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_cards'
    )
    members = models.ManyToManyField(
    User,
    through='CardMember',
    through_fields=('card', 'user'),  # Add this line
    related_name='assigned_cards'
    )
    labels = models.ManyToManyField(
        Label,
        through='CardLabel',
        related_name='cards'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'cards'
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        ordering = ['position']
        indexes = [
            models.Index(fields=['list']),
            models.Index(fields=['list', 'position']),
            models.Index(fields=['created_by']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def archive(self):
        """Archive the card"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore the card from archive"""
        self.is_archived = False
        self.archived_at = None
        self.save()
    
    def save(self, *args, **kwargs):
        """Auto-assign position if not provided"""
        if self.position == 0 and not self.pk:
            # Get the highest position in this list
            max_position = Card.objects.filter(
                list=self.list
            ).aggregate(models.Max('position'))['position__max']
            self.position = (max_position or 0) + 1
        super().save(*args, **kwargs)


class CardMember(models.Model):
    """Card member assignments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='card_members'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='card_assignments'
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_cards_by'
    )
    
    class Meta:
        db_table = 'card_members'
        verbose_name = 'Card Member'
        verbose_name_plural = 'Card Members'
        unique_together = [['card', 'user']]
        ordering = ['assigned_at']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} assigned to {self.card.title}"


class CardLabel(models.Model):
    """Card label associations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='card_labels'
    )
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        related_name='card_labels'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'card_labels'
        verbose_name = 'Card Label'
        verbose_name_plural = 'Card Labels'
        unique_together = [['card', 'label']]
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['label']),
        ]
    
    def __str__(self):
        return f"{self.label.name} on {self.card.title}"


class Checklist(models.Model):
    """Checklist model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='checklists'
    )
    title = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'checklists'
        verbose_name = 'Checklist'
        verbose_name_plural = 'Checklists'
        ordering = ['position']
        indexes = [
            models.Index(fields=['card']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.card.title}"
    
    def save(self, *args, **kwargs):
        """Auto-assign position if not provided"""
        if self.position == 0 and not self.pk:
            max_position = Checklist.objects.filter(
                card=self.card
            ).aggregate(models.Max('position'))['position__max']
            self.position = (max_position or 0) + 1
        super().save(*args, **kwargs)


class ChecklistItem(models.Model):
    """Checklist item model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checklist = models.ForeignKey(
        Checklist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    title = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    position = models.IntegerField(default=0)
    
    due_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_checklist_items'
    )
    
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_checklist_items'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'checklist_items'
        verbose_name = 'Checklist Item'
        verbose_name_plural = 'Checklist Items'
        ordering = ['position']
        indexes = [
            models.Index(fields=['checklist']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-assign position and handle completion"""
        if self.position == 0 and not self.pk:
            max_position = ChecklistItem.objects.filter(
                checklist=self.checklist
            ).aggregate(models.Max('position'))['position__max']
            self.position = (max_position or 0) + 1
        
        # Set completed_at when marking as completed
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
            self.completed_by = None
        
        super().save(*args, **kwargs)


class Attachment(models.Model):
    """File attachments for cards"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file_name = models.CharField(max_length=255)
    file_url = models.URLField(max_length=1000)
    file_type = models.CharField(max_length=100, blank=True, help_text="MIME type")
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    thumbnail_url = models.URLField(max_length=1000, blank=True)
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'attachments'
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['card']),
        ]
    
    def __str__(self):
        return f"{self.file_name} - {self.card.title}"


class Comment(models.Model):
    """Comments on cards"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} on {self.card.title}"


class CommentMention(models.Model):
    """User mentions in comments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='mentions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_mentions'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'comment_mentions'
        verbose_name = 'Comment Mention'
        verbose_name_plural = 'Comment Mentions'
        unique_together = [['comment', 'user']]
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"@{self.user.username} in comment"