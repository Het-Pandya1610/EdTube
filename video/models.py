import os
import cv2
import yt_dlp
import urllib.parse as urlparse
from django.db import models
from django.contrib.auth.models import User
from teacher.models import Teacher

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
    thumbnail = models.ImageField(
        upload_to="video_thumbnails/",
        null=True,
        blank=True
    )

    # Sources
    video_link = models.URLField(blank=True, null=True)
    video_file = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True
    )
    
    # Metadata
    duration = models.CharField(max_length=10, default="0:00", blank=True)
    language = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    
    # Engagement
    likes = models.ManyToManyField(User, related_name="video_likes", blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    # Resources
    notes = models.FileField(upload_to="video_notes/", blank=True, null=True)
    quiz = models.FileField(upload_to="video_quizzes/", blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 1. Generate Custom Video ID (VID-INITIALS-SUBJECT-0001)
        if not self.video_id:
            teacher_name = self.teacher.name.strip().split()
            initials = "".join([n[0].upper() for n in teacher_name[:2]])
            subject_code = self.subject.strip()[:2].upper()

            last_video = Video.objects.order_by("created_at").last()
            if last_video and "-" in last_video.video_id:
                try:
                    last_num = int(last_video.video_id.split("-")[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.video_id = f"VID-{initials}-{subject_code}-{new_num:04d}"

        # 2. Extract Duration before saving
        # We only calculate if duration is default to avoid re-calculating on every edit
        if self.duration == "0:00":
            try:
                # Option A: YouTube Link
                if self.video_link:
                    ydl_opts = {'quiet': True, 'noplaylist': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.video_link, download=False)
                        self.duration = self.format_seconds(info.get('duration', 0))

                # Option B: Local Media File
                elif self.video_file:
                    # Save the file first so we have a physical path to read
                    super().save(*args, **kwargs)
                    cap = cv2.VideoCapture(self.video_file.path)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if fps > 0:
                        duration_seconds = frame_count / fps
                        self.duration = self.format_seconds(duration_seconds)
                    cap.release()
            except Exception as e:
                print(f"Error extracting duration: {e}")

        super().save(*args, **kwargs)

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
