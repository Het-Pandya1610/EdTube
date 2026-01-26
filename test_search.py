from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from teacher.models import Teacher
from video.models import Video

class SearchFunctionalityTests(TestCase):
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
            name='John Smith',
            username='johnsmith'
        )
        self.video = Video.objects.create(
            teacher=self.teacher,
            title='Test Video',
            video_id='VID001',
            description='Test description',
            subject='Mathematics'
        )
    
    def test_basic_search(self):
        """Test basic text search"""
        # Use the correct URL name 'search' which points to 'search-results/'
        response = self.client.get(reverse('search'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
    
    def test_teacher_name_search(self):
        """Test search by teacher name"""
        response = self.client.get(reverse('search'), {'q': 'John'})
        self.assertEqual(response.status_code, 200)
    
    def test_hashtag_search_exact(self):
        """Test exact hashtag search"""
        video2 = Video.objects.create(
            teacher=self.teacher,
            title='Python Video',
            video_id='VID002',
            description='Learn #python programming'
        )
        response = self.client.get(reverse('search'), {'q': '#python'})
        self.assertEqual(response.status_code, 200)
    
    def test_subject_search(self):
        """Test subject search"""
        response = self.client.get(reverse('search'), {'q': 'Mathematics'})
        self.assertEqual(response.status_code, 200)
    
    def test_special_characters_search(self):
        """Test search with special characters"""
        response = self.client.get(reverse('search'), {'q': 'test-video@special'})
        self.assertEqual(response.status_code, 200)
    
    def test_no_results_search(self):
        """Test search with no results"""
        response = self.client.get(reverse('search'), {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)