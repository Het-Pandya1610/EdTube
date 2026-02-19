from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from cloudinary_storage.validators import validate_image
from video.models import Quiz, Video
from django.db.models import Max
from datetime import date, timedelta

class Student(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="student"
    )

    student_id = models.CharField(max_length=20, primary_key=True, unique=True)

    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    
    # Cloudinary storage for profile picture
    pfp = models.ImageField(
        upload_to="student_profiles/", 
        null=True, 
        blank=True,
        storage=RawMediaCloudinaryStorage(),
        validators=[validate_image],
        help_text="Profile picture (max 10MB - Cloudinary Free limit)"
    )

    no_of_quiz_given = models.PositiveIntegerField(default=0)
    no_of_points_earned = models.PositiveIntegerField(default=0)
    rank_in_leaderboard = models.PositiveIntegerField(null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_id
    
    def save(self, *args, **kwargs):
        # Validate image size before saving to Cloudinary
        if self.pfp and hasattr(self.pfp, 'size'):
            max_image_size = 10 * 1024 * 1024  # 10MB Cloudinary free limit
            if self.pfp.size > max_image_size:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Profile picture must be under 10MB. Current: {self.pfp.size/1024:.1f}KB"
                )
        
        super().save(*args, **kwargs)
    
    @property
    def pfp_url(self):
        """Get Cloudinary URL for profile picture with optimizations"""
        if self.pfp:
            return self.pfp.url
        return None
    
    @property
    def total_quizzes(self):
        return self.quiz_attempts.count()
    
    @property
    def best_percentage(self):
        return self.quiz_attempts.aggregate(Max("percentage"))["percentage__max"] or 0
    
    @property
    def best_score(self):
        return self.quiz_attempts.aggregate(Max("score"))["score__max"] or 0

    @property
    def current_streak(self):
        days = (
            self.quiz_attempts
            .dates("created_at", "day", order="DESC")
        )

        streak = 0
        today = date.today()

        for i, day in enumerate(days):
            if day == today - timedelta(days=i):
                streak += 1
            else:
                break

        return streak
    
class QuizAttempt(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    quiz_id = models.CharField(max_length=50, default=None)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "quiz_id")

    def __str__(self):
        return f"{self.student.student_id} - {self.quiz.id}"

class CoinTransaction(models.Model):
    TRANSACTION_TYPES = (
        ("credit", "Credit"),
        ("debit", "Debit"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="coin_transactions"
    )

    amount = models.IntegerField()
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.amount}"

class DailyQuizCoinsRedemption(models.Model):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name="daily_quiz_coins_redemptions"
    )
    redeemed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-redeemed_at']
        
    def is_expired(self):
        """Check if 24 hours have passed since redemption"""
        return timezone.now() > self.redeemed_at + timedelta(hours=24)