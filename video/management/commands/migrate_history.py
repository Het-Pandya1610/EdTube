from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from video.models import VideoHistory, Video
from accounts.models import SearchHistory
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import json
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Migrate JSON history to database'

    def handle(self, *args, **options):
        HISTORY_FILE = Path('C:/Users/HET/Desktop/EdTube/user_history.json')
        
        if not HISTORY_FILE.exists():
            self.stdout.write(self.style.ERROR('❌ No history file found'))
            return
        
        self.stdout.write(f'📁 Found history file: {HISTORY_FILE}')
        
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
        
        self.stdout.write(f'📊 Video history entries: {len(data.get("video_history", []))}')
        self.stdout.write(f'📊 Search history entries: {len(data.get("search_history", []))}')
        
        # ===== FIX 1: Parse timestamps properly =====
        from datetime import datetime
        
        # Migrate video history
        video_count = 0
        video_errors = 0
        
        for entry in data.get('video_history', []):
            try:
                user = User.objects.get(email=entry['email'])
                video = Video.objects.get(video_id=entry['video_id'])
                
                # Parse timestamp string to datetime object
                timestamp_str = entry['timestamp']
                
                # Try different timestamp formats
                try:
                    # Format: "2024-01-15 10:30:00"
                    watched_at = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        # Format: "2024-01-15T10:30:00"
                        watched_at = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                    except ValueError:
                        # Default to now if parsing fails
                        watched_at = timezone.now()
                        self.stdout.write(self.style.WARNING(f'  ⚠ Could not parse timestamp: {timestamp_str}, using now'))
                
                # Make timezone aware
                if timezone.is_naive(watched_at):
                    watched_at = timezone.make_aware(watched_at)
                
                # Create or get video history
                obj, created = VideoHistory.objects.get_or_create(
                    user=user,
                    video=video,
                    watched_at=watched_at,
                    defaults={
                        'watch_duration': entry.get('watch_duration', 0),
                        'completed': entry.get('completed', False)
                    }
                )
                
                if created:
                    video_count += 1
                    self.stdout.write(f'  ✅ Video: {user.email} - {video.title[:30]}...')
                else:
                    self.stdout.write(f'  ℹ️ Already exists: {user.email} - {video.title[:30]}...')
                
            except User.DoesNotExist:
                video_errors += 1
                self.stdout.write(self.style.WARNING(f'  ⚠ User not found: {entry["email"]}'))
            except Video.DoesNotExist:
                video_errors += 1
                self.stdout.write(self.style.WARNING(f'  ⚠ Video not found: {entry["video_id"]}'))
            except Exception as e:
                video_errors += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}'))
        
        # Migrate search history
        search_count = 0
        search_errors = 0
        
        for entry in data.get('search_history', []):
            try:
                user = User.objects.filter(email=entry['email']).first()
                
                if not user:
                    search_errors += 1
                    self.stdout.write(self.style.WARNING(f'  ⚠ User not found: {entry["email"]}'))
                    continue
                
                # Parse timestamp
                timestamp_str = entry['timestamp']
                
                try:
                    searched_at = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        searched_at = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                    except ValueError:
                        searched_at = timezone.now()
                
                if timezone.is_naive(searched_at):
                    searched_at = timezone.make_aware(searched_at)
                
                # Create search history
                SearchHistory.objects.create(
                    user=user,
                    query=entry['query'][:255],  # Limit length
                    searched_at=searched_at
                )
                
                search_count += 1
                self.stdout.write(f'  ✅ Search: {user.email} - "{entry["query"][:20]}..."')
                
            except Exception as e:
                search_errors += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(
            f'✅ SUCCESS: Migrated {video_count} video records and {search_count} search records'
        ))
        
        if video_errors > 0 or search_errors > 0:
            self.stdout.write(self.style.WARNING(
                f'⚠️ ERRORS: {video_errors} video errors, {search_errors} search errors'
            ))