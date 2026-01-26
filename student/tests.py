from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from student.models import Student

class StudentModelTests(TestCase):
    def setUp(self):
        # Create user and student directly
        self.user = User.objects.create_user(
            username='studentuser',
            email='student@example.com',
            password='password123'
        )
        self.student = Student.objects.create(
            student_id='STU001',
            user=self.user,
            name='Jane Smith',
            username='studentuser'
        )
    
    def test_student_creation(self):
        """Test student model"""
        self.assertEqual(Student.objects.count(), 1)
        # Match your actual __str__ format
        self.assertEqual(str(self.student), 'STU001')
    
    def test_student_pfp_upload(self):
        """Test student profile picture field"""
        self.student.pfp = 'student_profiles/test.jpg'
        self.student.save()
        self.assertEqual(self.student.pfp, 'student_profiles/test.jpg')

class StudentViewTests(TestCase):
    def setUp(self):
        # Create user and student directly
        self.user = User.objects.create_user(
            username='studentuser',
            email='student@example.com',
            password='password123'
        )
        self.student = Student.objects.create(
            student_id='STU001',
            user=self.user,
            name='Jane Smith',
            username='studentuser'
        )
    
    def test_student_dashboard(self):
        """Test student dashboard access"""
        self.client.login(username=self.user.username, password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')