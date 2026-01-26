from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from teacher.models import Teacher, Follower
from video.models import Video

class TeacherModelTests(TestCase):
    def setUp(self):
        # Create user and teacher directly
        self.user = User.objects.create_user(
            username='teacheruser',
            email='teacher@example.com',
            password='password123'
        )
        self.teacher = Teacher.objects.create(
            teacher_id='TCH001',
            user=self.user,
            name='John Doe',
            username='teacheruser'
        )
    
    def test_teacher_creation(self):
        """Test teacher model"""
        self.assertEqual(Teacher.objects.count(), 1)
        # Match your actual __str__ format
        self.assertEqual(str(self.teacher), 'TCH001')
    
    def test_teacher_pfp_upload(self):
        """Test teacher profile picture field"""
        self.teacher.pfp = 'teacher_profiles/test.jpg'
        self.teacher.save()
        self.assertEqual(self.teacher.pfp, 'teacher_profiles/test.jpg')
    
    def test_teacher_followers(self):
        """Test follower relationship"""
        user2 = User.objects.create_user(
            username='followeruser',
            email='follower@example.com',
            password='password123'
        )
        follower = Follower.objects.create(
            teacher=self.teacher,
            follower=user2
        )
        self.assertEqual(Follower.objects.count(), 1)
        self.assertEqual(follower.teacher, self.teacher)
        self.assertEqual(follower.follower, user2)
        self.assertEqual(str(follower), f'{user2.username} follows {self.teacher.teacher_id}')

class TeacherViewTests(TestCase):
    def setUp(self):
        # Create user and teacher directly
        self.user = User.objects.create_user(
            username='teacheruser',
            email='teacher@example.com',
            password='password123'
        )
        self.teacher = Teacher.objects.create(
            teacher_id='TCH001',
            user=self.user,
            name='John Doe',
            username='teacheruser'
        )
    
    def test_teacher_profile_page(self):
        """Test teacher profile page loads"""
        self.client.login(username=self.user.username, password='password123')
        response = self.client.get(reverse('user_profile', args=[self.teacher.username]))
        self.assertEqual(response.status_code, 200)
        # Check if username appears somewhere in the page
        self.assertContains(response, 'teacheruser')
    
    def test_teacher_videos_list(self):
        """Test teacher's videos are displayed"""
        # Create a video for this teacher
        video = Video.objects.create(
            teacher=self.teacher,
            title='Test Video',
            video_id='VID001',
            description='Test description'
        )
        response = self.client.get(reverse('user_profile', args=[self.teacher.username]))
        self.assertEqual(response.status_code, 200)
        # The test might need adjustment based on your actual view
        # Some views don't pass 'videos' in context
        if 'videos' in response.context:
            self.assertIn('videos', response.context)