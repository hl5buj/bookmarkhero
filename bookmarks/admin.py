from django.contrib import admin
from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """북마크 관리자 페이지"""

    list_display = ['title', 'url', 'owner', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at', 'owner']
    search_fields = ['title', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('owner', 'title', 'url')
        }),
        ('상세 정보', {
            'fields': ('description', 'is_public')
        }),
        ('날짜 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
