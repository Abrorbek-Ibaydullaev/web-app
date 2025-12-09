from django.contrib import admin
from .models import List


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'position', 'is_archived', 'created_at']
    list_filter = ['is_archived', 'created_at']
    search_fields = ['name', 'board__name']
    readonly_fields = ['created_at', 'updated_at', 'archived_at']
    ordering = ['board', 'position']