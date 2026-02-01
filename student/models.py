from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from cloudinary_storage.validators import validate_image

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
    
    bio = models.TextField(max_length=500, blank=True)

    no_of_quiz_given = models.PositiveIntegerField(default=0)
    no_of_points_earned = models.PositiveIntegerField(default=0)
    rank_in_leaderboard = models.PositiveIntegerField(null=True, blank=True)

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