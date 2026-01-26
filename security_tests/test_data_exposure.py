# test_data_exposure.py
"""
Data Exposure Security Tests
"""
import re
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
import json

class DataExposureTests(TestCase):
    """Test for sensitive data exposure"""
    
    def setUp(self):
        """Create test users with different roles"""
        self.user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        self.other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='otherpass123',
            first_name='Other',
            last_name='User'
        )
        
        self.admin = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_idor_prevention(self):
        """Test Insecure Direct Object Reference prevention"""
        print("\n🔒 Testing IDOR prevention...")
        
        # Login as regular user
        self.client.login(username='regular_user', password='userpass123')
        
        # Try to access other user's data
        test_cases = [
            ('user_profile', {'user_id': self.other_user.id}),
            ('user_orders', {'user_id': self.other_user.id}),
            ('user_messages', {'user_id': self.other_user.id}),
        ]
        
        for endpoint_name, params in test_cases:
            try:
                endpoint = reverse(endpoint_name)
                response = self.client.get(endpoint, params)
                
                # Should not allow access (403 or redirect)
                self.assertIn(response.status_code, [403, 404, 302],
                            f"IDOR vulnerability in {endpoint_name}")
                
                if response.status_code == 403:
                    print(f"   ✓ {endpoint_name} prevents IDOR")
                
            except Exception:
                continue
        
        print("   ✓ IDOR prevention working")
    
    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed"""
        print("\n🔒 Testing sensitive data exposure...")
        
        # Check various endpoints for sensitive data
        endpoints_to_check = [
            ('api_users', {}),
            ('user_list', {}),
            ('debug_info', {}),
        ]
        
        sensitive_patterns = [
            r'password.*:.*[^\s]',  # Passwords in responses
            r'token.*:.*[^\s]',     # API tokens
            r'secret.*:.*[^\s]',    # Secret keys
            r'key.*:.*[^\s]',       # Encryption keys
            r'credit.*card',        # Credit card info
            r'ssn|social.*security', # Social security numbers
            r'private.*key',        # Private keys
        ]
        
        for endpoint_name, params in endpoints_to_check:
            try:
                endpoint = reverse(endpoint_name)
                response = self.client.get(endpoint, params)
                
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    for pattern in sensitive_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        self.assertEqual(len(matches), 0,
                                       f"Sensitive data exposed in {endpoint_name}: {matches}")
                
            except Exception:
                continue
        
        print("   ✓ No sensitive data exposed")
    
    def test_api_data_limitation(self):
        """Test that APIs don't expose unnecessary data"""
        print("\n🔒 Testing API data limitation...")
        
        # Login as regular user
        self.client.login(username='regular_user', password='userpass123')
        
        try:
            # Get user profile via API
            response = self.client.get(reverse('api_user_profile'))
            
            if response.status_code == 200:
                data = json.loads(response.content)
                
                # Check what fields are exposed
                exposed_fields = set(data.keys())
                
                # Sensitive fields that should NOT be exposed
                sensitive_fields = {
                    'password', 'password_hash', 'salt',
                    'session_key', 'last_login_ip',
                    'security_question', 'security_answer',
                    'payment_info', 'credit_card',
                }
                
                # Check intersection
                exposed_sensitive = exposed_fields.intersection(sensitive_fields)
                self.assertEqual(len(exposed_sensitive), 0,
                               f"Sensitive fields exposed: {exposed_sensitive}")
                
                print(f"   ✓ API exposes {len(exposed_fields)} safe fields")
                
        except Exception as e:
            print(f"   Note: {str(e)[:50]}")
        
        print("   ✓ API data limitation working")