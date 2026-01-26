from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile, EmailVerification

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
    
    def test_user_creation(self):
        """Test that user and profile are created together"""
        self.assertTrue(User.objects.filter(username=self.user.username).exists())
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
    
    def test_profile_str(self):
        """Test profile string representation"""
        profile = self.user.profile
        profile.role = 'student'  # Ensure role is set
        profile.save()
        self.assertEqual(str(profile), f'{self.user.username} - student')
    
    def test_email_verification_creation(self):
        """Test email verification model"""
        verification = EmailVerification.objects.create(
            user=self.user,
            otp='123456'  # 6 characters as defined in model
        )
        self.assertEqual(str(verification), f'OTP for {self.user.email}')

class AuthViewTests(TestCase):
    def setUp(self):
        # Create a test user with verified email
        # IMPORTANT: The username must match email.split("@")[0] for login to work
        self.user = User.objects.create_user(
            username='test',  # email.split("@")[0] = 'test'
            email='test@example.com',
            password='password123'
        )
        profile = self.user.profile
        profile.is_email_verified = True
        profile.save()
    
    def test_login_page_loads(self):
        """Test login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        # Check for login form elements
        self.assertContains(response, 'email')
        self.assertContains(response, 'password')
    
    def test_successful_login(self):
        """Test user can login with correct credentials"""
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # The view returns a redirect on success
        self.assertEqual(response.status_code, 302)
        # Check if redirected to index
        self.assertEqual(response.url, '/')
    
    def test_failed_login_wrong_email(self):
        """Test login fails with wrong email"""
        response = self.client.post(reverse('login'), {
            'email': 'wrong@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        # Check for error message
        content = response.content.decode('utf-8')
        self.assertIn('Email not found', content)
    
    def test_failed_login_wrong_password(self):
        """Test login fails with wrong password"""
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        # Check for error message
        content = response.content.decode('utf-8')
        self.assertIn('Invalid password', content)
    
    def test_registration_page(self):
        """Test registration page loads"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='test', password='password123')
        # Then logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/account/login/')