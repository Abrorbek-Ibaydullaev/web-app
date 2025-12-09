from django.contrib import admin
from .models import Board, BoardMember, BoardStar, Label


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace', 'visibility', 'is_template', 'is_starred', 'is_archived', 'created_at']
    list_filter = ['visibility', 'is_template', 'is_starred', 'is_archived', 'created_at']
    search_fields = ['name', 'slug', 'workspace__name', 'created_by__email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'archived_at']


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'board', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__email', 'board__name']
    readonly_fields = ['joined_at']


@admin.register(BoardStar)
class BoardStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'board', 'starred_at']
    list_filter = ['starred_at']
    search_fields = ['user__email', 'board__name']
    readonly_fields = ['starred_at']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'board', 'created_at']
    list_filter = ['board', 'created_at']
    search_fields = ['name', 'board__name']
    readonly_fields = ['created_at', 'updated_at']

