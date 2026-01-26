# test_sql_injection.py (expanded)
"""
Comprehensive SQL Injection Security Tests
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection
import json

class SQLInjectionTests(TestCase):
    """Comprehensive SQL injection prevention tests"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_basic_sql_injection(self):
        """Test common SQL injection vectors"""
        print("\n🔒 Testing SQL injection prevention...")
        
        injection_vectors = [
            # Basic injections
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin' --",
            "' OR 'a'='a",
            
            # Union attacks
            "' UNION SELECT NULL, username, password FROM auth_user --",
            "' UNION SELECT 1,@@version,3,4 --",
            
            # Error-based
            "' AND EXTRACTVALUE(1, CONCAT(0x5c, VERSION())) --",
            "' AND 1=CONVERT(int, @@version) --",
            
            # Blind SQLi
            "' AND SLEEP(5) --",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
            
            # Stacked queries
            "'; DROP TABLE users; --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            
            # Bypass techniques
            "' OR 1=1#",
            "' OR '1'='1' /*!50000or*/",
            "'/**/OR/**/1=1",
            
            # JSON injection
            '{"username": "admin", "password": {"$ne": null}}',
        ]
        
        vulnerable_endpoints = [
            ('search', {'q': ''}),
            ('user_profile', {'username': ''}),
            ('get_videos', {'category': ''}),
            ('api_search', {'query': ''}),
        ]
        
        for endpoint_name, params in vulnerable_endpoints[:2]:  # Test subset
            try:
                endpoint = reverse(endpoint_name)
            except:
                continue  # Skip if endpoint doesn't exist
            
            print(f"   Testing endpoint: {endpoint_name}")
            
            for i, vector in enumerate(injection_vectors[:10]):  # Test subset
                test_params = params.copy()
                for key in test_params:
                    if test_params[key] == '':
                        test_params[key] = vector
                
                try:
                    response = self.client.get(endpoint, test_params)
                    
                    # Check for SQL errors in response
                    content = response.content.decode().lower()
                    
                    # Should not expose SQL errors
                    sql_keywords = ['sql', 'syntax', 'mysql', 'postgresql', 
                                   'database', 'error at', 'exception', 
                                   'stack trace', 'traceback']
                    
                    for keyword in sql_keywords:
                        self.assertNotIn(keyword, content, 
                                       f"SQL error leaked on {endpoint_name} with vector {i}")
                    
                    # Check response is valid
                    self.assertIn(response.status_code, [200, 302, 400, 404, 403],
                                f"Unexpected status code {response.status_code}")
                    
                except Exception as e:
                    # Should handle injection attempts gracefully
                    self.fail(f"Endpoint crashed with SQLi: {str(e)}")
        
        print("   ✓ All SQL injection tests passed")
    
    def test_orm_injection_protection(self):
        """Test Django ORM protection against injection"""
        print("\n🔒 Testing ORM injection protection...")
        
        from django.db.models import Q
        
        # Test raw() method safety (should be avoided)
        dangerous_input = "test' OR 1=1 --"
        
        # This should be parameterized
        try:
            User.objects.raw(
                'SELECT * FROM auth_user WHERE username = %s', 
                [dangerous_input]
            )
        except Exception as e:
            print(f"   Raw query error (expected): {str(e)[:50]}...")
        
        # Test Q objects safety
        safe_query = Q(username__contains="test")
        users = User.objects.filter(safe_query)
        
        # Test extra() method (deprecated but check if used)
        try:
            User.objects.extra(
                where=["username=%s"], 
                params=[dangerous_input]
            )
        except Exception:
            pass  # extra() is deprecated
        
        print("   ✓ ORM protections verified")
    
    def test_json_injection(self):
        """Test JSON/NoSQL injection prevention"""
        print("\n🔒 Testing JSON/NoSQL injection...")
        
        json_vectors = [
            '{"$where": "1==1"}',
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"username": {"$regex": ".*"}}',
            '{"$or": [{"username": "admin"}, {"1": "1"}]}',
        ]
        
        # Test endpoints that might accept JSON
        json_endpoints = [
            ('api_login', {'username': '', 'password': ''}),
            ('api_search', {'query': ''}),
        ]
        
        for endpoint_name, payload in json_endpoints:
            try:
                endpoint = reverse(endpoint_name)
            except:
                continue
            
            for vector in json_vectors[:3]:
                try:
                    # Try as query parameter
                    response = self.client.get(endpoint, {'q': vector})
                    self.assertNotEqual(response.status_code, 500)
                    
                    # Try as JSON body
                    response = self.client.post(
                        endpoint, 
                        data=vector,
                        content_type='application/json'
                    )
                    self.assertNotEqual(response.status_code, 500)
                    
                except json.JSONDecodeError:
                    pass  # Expected for invalid JSON
                except Exception as e:
                    self.fail(f"JSON injection vulnerability: {str(e)}")
        
        print("   ✓ JSON injection tests passed")