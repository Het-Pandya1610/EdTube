import cloudinary.api as api
import yt_dlp
import urllib.parse as urlparse
from django.db import models
from django.contrib.auth.models import User
from teacher.models import Teacher
from cloudinary_storage.storage import VideoMediaCloudinaryStorage, RawMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video, validate_image
from django.core.exceptions import ValidationError


class Video(models.Model):
    # Identification
    video_id = models.CharField(
        max_length=50,
        primary_key=True,
        unique=True
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Cloudinary storage for thumbnail
    thumbnail = models.ImageField(
        upload_to="video_thumbnails/",
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
        validators=[validate_image]
    )

    # Sources
    video_link = models.URLField(blank=True, null=True)
    
    # Cloudinary storage for video files
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True,
        storage=VideoMediaCloudinaryStorage(),
        validators=[validate_video]
    )
    
    # Metadata
    duration = models.CharField(max_length=10, default="0:00", blank=True)
    language = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    
    # Engagement
    likes = models.ManyToManyField(User, related_name="video_likes", blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    
    # Resources - Cloudinary storage
    notes = models.FileField(
        upload_to="video_notes/", 
        blank=True, 
        null=True,
        storage=RawMediaCloudinaryStorage()
    )
    
    quiz = models.FileField(
        upload_to="video_quizzes/", 
        blank=True, 
        null=True,
        storage=RawMediaCloudinaryStorage()
    )
    
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Generate Custom Video ID
        if not self.video_id:
            teacher_name = self.teacher.name.strip().split()
            initials = "".join([n[0].upper() for n in teacher_name[:2]])
            subject_code = self.subject.strip()[:2].upper()

            last_video = Video.objects.order_by("created_at").last()
            if last_video and last_video.video_id:
                try:
                    last_num = int(last_video.video_id.split("-")[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.video_id = f"VID-{initials}-{subject_code}-{new_num:04d}"

        # 2. File size validation
        if self.video_file and hasattr(self.video_file, "size"):
            if self.video_file.size > 100 * 1024 * 1024:
                raise ValidationError("Video file must be under 100MB")

        if self.thumbnail and hasattr(self.thumbnail, "size"):
            if self.thumbnail.size > 10 * 1024 * 1024:
                raise ValidationError("Thumbnail must be under 10MB")

        for field, name in [(self.notes, "Notes"), (self.quiz, "Quiz")]:
            if field and hasattr(field, "size"):
                if field.size > 10 * 1024 * 1024:
                    raise ValidationError(f"{name} must be under 10MB")

        # 3. FIRST save → upload files to Cloudinary
        super().save(*args, **kwargs)

        # 4. Duration extraction (ONLY if not set)
        if not self.duration or self.duration == "0:00":
            try:
                # Option A: YouTube link
                if self.video_link:
                    ydl_opts = {"quiet": True, "noplaylist": True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.video_link, download=False)
                        seconds = info.get("duration")
                        if seconds:
                            self.duration = self.format_seconds(seconds)
                            super().save(update_fields=["duration"])

                # Option B: Cloudinary video file
                elif self.video_file:
                    resource = api.resource(
                        self.video_file.name,
                        resource_type="video",
                        type="upload",
                        media_metadata=True
                    )

                    seconds = resource.get("duration")
                    if seconds:
                        self.duration = self.format_seconds(seconds)
                        super().save(update_fields=["duration"])

            except Exception as e:
                print("Duration extraction error:", e)
                self.duration = "N/A"
                super().save(update_fields=["duration"])

    def format_seconds(self, seconds):
        """Helper to turn 125 seconds into '2:05'"""
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @property
    def youtube_id(self):
        if not self.video_link:
            return None
        url = self.video_link
        if 'youtu.be/' in url:
            return url.split('/')[-1].split('?')[0]
        elif 'youtube.com/watch' in url:
            parsed_url = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed_url.query).get('v', [None])[0]
        return None

    def __str__(self):
        return f"{self.video_id} - {self.title}"
    
class Comment(models.Model):
    video = models.ForeignKey(
        'video.video',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField(max_length=2000)

    is_reply = models.BooleanField(default=False)

    likes_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.video}"
    
class CommentReply(models.Model):
    parent_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_replies'
    )

    content = models.TextField(max_length=2000)

    likes_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.author}"
    
class Quiz(models.Model):
    video = models.ForeignKey(
        'video.video',
        on_delete=models.CASCADE,
        related_name='quiz_questions'
    )
    question_id = models.CharField(max_length=50)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Quiz for {self.video.title}"