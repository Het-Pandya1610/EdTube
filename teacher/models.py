from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    pfp = models.ImageField(
        upload_to="teacher_profiles/",
        null=True,
        blank=True
    )
    banner_img = models.ImageField(
        upload_to="teacher_banner/",
        null=True,
        blank=True
    )
    bio = models.TextField(blank=True)
    nos = models.IntegerField(default=0)
    nov = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.teacher_id
    
class Follower(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="followers_set")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'follower')

    def __str__(self):
        return f"{self.follower.username} follows {self.teacher.teacher_id}"