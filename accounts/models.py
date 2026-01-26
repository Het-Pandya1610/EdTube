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
    is_email_verified = models.BooleanField(default=False)  # ADD THIS LINE

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # Changed from 4 to 6
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f'OTP for {self.user.email}'
    
    def is_expired(self):
        # OTP valid for 15 minutes
        return timezone.now() > self.created_at + timedelta(minutes=15)
    
    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))