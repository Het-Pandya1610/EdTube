# video/admin.py
from django.contrib import admin
from .models import VideoHistory
from accounts.models import SearchHistory

@admin.register(VideoHistory)
class VideoHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'watched_at']
    list_filter = ['watched_at']
    search_fields = ['user__email', 'video__title']
    date_hierarchy = 'watched_at'

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'searched_at']
    list_filter = ['searched_at']
    search_fields = ['user__email', 'query']
    date_hierarchy = 'searched_at'