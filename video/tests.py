from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from teacher.models import Teacher
from video.models import Video
import json

class VideoModelTests(TestCase):
    def setUp(self):
        # Create user, teacher, and video directly
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
        self.video = Video.objects.create(
            teacher=self.teacher,
            title='Test Video',
            video_id='VID001',
            description='Test description'
        )
    
    def test_video_creation(self):
        """Test video model creation"""
        self.assertEqual(Video.objects.count(), 1)
        # Match your actual __str__ format
        self.assertEqual(str(self.video), 'VID001 - Test Video')
    
    def test_video_like_count(self):
        """Test like count functionality"""
        initial_count = self.video.like_count
        self.video.like_count = initial_count + 1
        self.video.save()
        self.assertEqual(self.video.like_count, initial_count + 1)
    
    def test_video_duration(self):
        """Test video duration field"""
        self.video.duration = '15:45'
        self.video.save()
        self.assertEqual(self.video.duration, '15:45')

class VideoViewTests(TestCase):
    def setUp(self):
        # Create user, teacher, and video directly
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
        self.video = Video.objects.create(
            teacher=self.teacher,
            title='Test Video',
            video_id='VID001',
            description='Test description'
        )
    
    def test_video_player_page(self):
        """Test video player page loads"""
        self.client.login(username=self.user.username, password='password123')
        response = self.client.get(reverse('watch_video') + f'?v={self.video.video_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'video_player.html')
        self.assertContains(response, self.video.title)
    
    def test_search_view(self):
        """Test search functionality"""
        response = self.client.get(reverse('search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_results.html')
    
    def test_hashtag_search(self):
        """Test hashtag search works"""
        video2 = Video.objects.create(
            teacher=self.teacher,
            title='Python Tutorial',
            video_id='VID002',
            description="Learn #python programming"
        )
        response = self.client.get(reverse('search'), {'q': '#python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search results')
    
    def test_subject_by_teacher_search(self):
        """Test 'subject by teacher' search pattern"""
        # Create a second user for the second teacher
        user2 = User.objects.create_user(
            username='teacher2user',
            email='teacher2@example.com',
            password='password123'
        )
        teacher2 = Teacher.objects.create(
            teacher_id='TCH002',
            user=user2,  # Use the new user instead of self.user
            name='John Doe',
            username='johndoe'
        )
        video2 = Video.objects.create(
            teacher=teacher2,
            title='Math Tutorial',
            video_id='VID003',
            description='Mathematics basics',
            subject='Mathematics'
        )
        response = self.client.get(reverse('search'), {'q': 'Math by John'})
        self.assertEqual(response.status_code, 200)
    
    def test_empty_search(self):
        """Test empty search query doesn't crash"""
        response = self.client.get(reverse('search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
    
    def test_video_json_response(self):
        """Test API-like video response"""
        response = self.client.get(reverse('watch_video') + f'?v={self.video.video_id}')
        self.assertEqual(response.status_code, 200)
        # Should contain video data in context
        self.assertIn('video', response.context)

class VideoSecurityTests(TestCase):
    def test_xss_protection_in_search(self):
        """Test that search input is sanitized"""
        response = self.client.get(reverse('search'), {'q': '<script>alert(1)</script>'})
        self.assertEqual(response.status_code, 200)
        # Check that script tags are escaped
        content = response.content.decode('utf-8')
        self.assertNotIn('<script>alert(1)</script>', content)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', content)
    
    def test_sql_injection_protection(self):
        """Test SQL injection attempts are handled safely"""
        response = self.client.get(reverse('search'), {'q': "' OR '1'='1"})
        self.assertEqual(response.status_code, 200)