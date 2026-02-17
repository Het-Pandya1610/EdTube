# video/analytics.py
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import VideoHistory, SearchHistory

def get_user_analytics(user):
    """Get detailed analytics for a user"""
    
    # Last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Video watching stats
    video_stats = VideoHistory.objects.filter(
        user=user,
        watched_at__gte=thirty_days_ago
    ).aggregate(
        total_videos=Count('id'),
        unique_videos=Count('video', distinct=True)
    )
    
    # Most active hours
    active_hours = VideoHistory.objects.filter(
        user=user
    ).extra({'hour': "EXTRACT(hour FROM watched_at)"}).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    # Search trends
    search_trends = SearchHistory.objects.filter(
        user=user,
        searched_at__gte=thirty_days_ago
    ).values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    return {
        'video_stats': video_stats,
        'active_hours': list(active_hours),
        'search_trends': list(search_trends),
    }