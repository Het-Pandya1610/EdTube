import json
import os
import threading
from datetime import datetime
from django.conf import settings
import csv
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.cache import cache
from .models import VideoHistory
from accounts.models import SearchHistory

# Global lock to prevent file corruption during simultaneous writes
file_lock = threading.Lock()

# This stores the file in your main project folder
HISTORY_FILE = os.path.join(settings.BASE_DIR, 'user_history.json')

REQUIRED_COLUMNS = [
    "question_text",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_option"
]

@transaction.atomic
def save_to_history(history_type, user, data_value):
    """
    Saves user activity to database.
    history_type: "search" or "video"
    user: request.user object
    data_value: The search query string OR the video object/id
    """
    
    if history_type == "search":
        SearchHistory.objects.create(
            user=user,
            query=data_value
        )
        
        old_searches = SearchHistory.objects.filter(user=user)[100:]
        if old_searches:
            old_searches.delete()

        cache.delete(f"search_suggestions_{user.id}")
        
    elif history_type == "video":
        if isinstance(data_value, str):
            from .models import Video
            video = Video.objects.get(video_id=data_value)
        else:
            video = data_value
            
        VideoHistory.objects.create(
            user=user,
            video=video
        )
        
        # Clean up old history (keep last 200 videos per user)
        old_videos = VideoHistory.objects.filter(user=user)[200:]
        if old_videos:
            old_videos.delete()
        
        # Clear video history cache
        cache.delete(f"video_history_{user.id}")

def get_user_video_history(user, limit=10):
    """
    Retrieves the most recent videos watched by a specific user.
    """
    cache_key = f"video_history_{user.id}"
    cached = cache.get(cache_key)
    
    if cached:
        return cached[:limit]
    history = VideoHistory.objects.filter(
        user=user
    ).select_related('video').order_by('-watched_at')[:limit]
    
    videos = [entry.video for entry in history]
    cache.set(cache_key, videos, 3600)
    
    return videos

def validate_quiz_csv(file):
    """
    Validates quiz CSV file format and content.
    Raises ValidationError if invalid.
    """

    # Check file extension
    if not file.name.endswith(".csv"):
        raise ValidationError("Only CSV files are allowed.")

    # Check file size (max 5MB for example)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("CSV file must be under 5MB.")

    try:
        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        # Validate headers - should match what's expected (no question_id)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValidationError(
                f"CSV headers must be exactly: {', '.join(REQUIRED_COLUMNS)}"
            )

        question_texts = set()  # To check for duplicate questions (optional)

        for row_number, row in enumerate(reader, start=2):

            # Empty value check
            for column in REQUIRED_COLUMNS:
                if not row.get(column):
                    raise ValidationError(
                        f"Missing value in column '{column}' at row {row_number}"
                    )

            # Correct option validation
            if row["correct_option"].strip().upper() not in ["A", "B", "C", "D"]:
                raise ValidationError(
                    f"Invalid correct_option at row {row_number}. Must be A, B, C or D."
                )

            # Optional: Check for duplicate question text
            if row["question_text"] in question_texts:
                raise ValidationError(
                    f"Duplicate question_text at row {row_number}"
                )

            question_texts.add(row["question_text"])

    except UnicodeDecodeError:
        raise ValidationError("Invalid file encoding. Use UTF-8.")

    except csv.Error:
        raise ValidationError("Invalid CSV format.")

    finally:
        file.seek(0)  # reset pointer for future use

    return True