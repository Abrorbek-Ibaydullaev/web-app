from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'board', 'card', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__email', 'board__name', 'card__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
