from django.contrib import admin
from .models import (
    Card, CardMember, CardLabel, Checklist, 
    ChecklistItem, Attachment, Comment, CommentMention
)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'list', 'position', 'due_date', 'is_completed', 'is_archived', 'created_at']
    list_filter = ['is_completed', 'is_archived', 'created_at']
    search_fields = ['title', 'description', 'list__name']
    readonly_fields = ['created_at', 'updated_at', 'archived_at']
    ordering = ['list', 'position']


@admin.register(CardMember)
class CardMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'assigned_by', 'assigned_at']
    list_filter = ['assigned_at']
    search_fields = ['user__email', 'card__title']
    readonly_fields = ['assigned_at']


@admin.register(CardLabel)
class CardLabelAdmin(admin.ModelAdmin):
    list_display = ['card', 'label', 'created_at']
    list_filter = ['created_at']
    search_fields = ['card__title', 'label__name']
    readonly_fields = ['created_at']


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ['title', 'card', 'position', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'card__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'checklist', 'is_completed', 'position', 'assigned_to', 'due_date']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['title', 'checklist__title']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'card', 'file_type', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'card__title']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['content', 'user__email', 'card__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CommentMention)
class CommentMentionAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'comment__content']
    readonly_fields = ['created_at']