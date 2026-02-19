from datetime import timedelta
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True, default="")

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class EmailVerification(models.Model):
    
    PURPOSE_CHOICES = (
        ("registration", "Registration"),
        ("login", "Login"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    otp_purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="registration")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))
    
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['user', '-searched_at']),
            models.Index(fields=['query']),  # For popular searches
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.query} - {self.searched_at}"
