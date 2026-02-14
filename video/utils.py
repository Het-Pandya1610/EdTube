import json
import os
import threading
from datetime import datetime
from django.conf import settings
import csv
from django.core.exceptions import ValidationError

# Global lock to prevent file corruption during simultaneous writes
file_lock = threading.Lock()

# This stores the file in your main project folder
HISTORY_FILE = os.path.join(settings.BASE_DIR, 'user_history.json')

REQUIRED_COLUMNS = [
    "question_id",
    "question_number",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_option"
]

def save_to_history(history_type, email, data_value):
    """
    Saves user activity to a JSON file.
    history_type: "search" or "video"
    email: request.user.email
    data_value: The search query string OR the video_id
    """
    
    with file_lock:
        # 1. Initialize file structure if it doesn't exist
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w') as f:
                json.dump({"search_history": [], "video_history": []}, f, indent=4)

        # 2. Read existing data
        try:
            with open(HISTORY_FILE, 'r') as f:
                content = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            content = {"search_history": [], "video_history": []}

        # 3. Create the entry object
        entry = {
            "email": email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if history_type == "search":
            entry["query"] = data_value
            content["search_history"].append(entry)
            
            # Optional: Keep only last 100 searches to keep file small
            if len(content["search_history"]) > 1000:
                content["search_history"] = content["search_history"][-1000:]

        elif history_type == "video":
            entry["video_id"] = data_value
            # Remove old entry of the same video for this user to avoid duplicates
            content["video_history"] = [
                item for item in content["video_history"] 
                if not (item['email'] == email and item['video_id'] == data_value)
            ]
            content["video_history"].append(entry)

        # 4. Write back to the file safely
        with open(HISTORY_FILE, 'w') as f:
            json.dump(content, f, indent=4)

def get_user_video_history(email, limit=10):
    """
    Retrieves the most recent videos watched by a specific user.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, 'r') as f:
        try:
            content = json.load(f)
            # Filter by email and reverse to get newest first
            user_videos = [item for item in content.get("video_history", []) if item['email'] == email]
            return user_videos[::-1][:limit]
        except:
            return []
        
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

        # Validate headers
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValidationError(
                f"CSV headers must be exactly: {', '.join(REQUIRED_COLUMNS)}"
            )

        question_ids = set()

        for row_number, row in enumerate(reader, start=2):

            # Empty value check
            for column in REQUIRED_COLUMNS:
                if not row.get(column):
                    raise ValidationError(
                        f"Missing value in column '{column}' at row {row_number}"
                    )

            # Correct option validation
            if row["correct_option"].upper() not in ["A", "B", "C", "D"]:
                raise ValidationError(
                    f"Invalid correct_option at row {row_number}. Must be A, B, C or D."
                )

            # Duplicate question_id
            if row["question_id"] in question_ids:
                raise ValidationError(
                    f"Duplicate question_id '{row['question_id']}' at row {row_number}"
                )

            question_ids.add(row["question_id"])

    except UnicodeDecodeError:
        raise ValidationError("Invalid file encoding. Use UTF-8.")

    except csv.Error:
        raise ValidationError("Invalid CSV format.")

    finally:
        file.seek(0)  # reset pointer for future use

    return True