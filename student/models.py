from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="student"
    )

    student_id = models.CharField(max_length=20, primary_key=True, unique=True)

    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    pfp = models.ImageField(upload_to="student_profiles/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    no_of_quiz_given = models.PositiveIntegerField(default=0)
    no_of_points_earned = models.PositiveIntegerField(default=0)
    rank_in_leaderboard = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_id