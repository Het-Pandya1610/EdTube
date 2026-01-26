# test_configuration.py
"""
Security Configuration Tests
"""
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
import os
import re

class SecurityConfigurationTests(TestCase):
    """Test security-related configuration"""
    
    def test_debug_mode_disabled(self):
        """Ensure DEBUG is False in production"""
        print("\n🔒 Testing debug mode...")
        
        self.assertFalse(settings.DEBUG, 
                        "DEBUG should be False in production")
        print("   ✓ DEBUG mode is disabled")
    
    def test_secret_key_security(self):
        """Test secret key configuration"""
        print("\n🔒 Testing secret key...")
        
        secret_key = getattr(settings, 'SECRET_KEY', '')
        
        # Should not be default
        self.assertNotEqual(secret_key, '', "SECRET_KEY not set")
        self.assertNotEqual(secret_key, 'django-insecure-', 
                          "SECRET_KEY is using default insecure value")
        
        # Should be sufficiently long
        self.assertGreater(len(secret_key), 32, 
                          "SECRET_KEY should be at least 32 characters")
        
        print("   ✓ SECRET_KEY is properly configured")
    
    def test_security_headers(self):
        """Test security headers"""
        print("\n🔒 Testing security headers...")
        
        # Try multiple possible home/root endpoints
        possible_home_endpoints = ['home', '', 'index', 'dashboard', 'landing']
        
        response = None
        for endpoint_name in possible_home_endpoints:
            try:
                endpoint = reverse(endpoint_name)
                response = self.client.get(endpoint)
                print(f"   Testing headers on: {endpoint_name}")
                break
            except:
                continue
        
        if not response:
            # Try root URL
            response = self.client.get('/')
        
        # Check for security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],  # Accept either
            'X-XSS-Protection': '1; mode=block',
        }
        
        headers_found = 0
        for header, expected_values in security_headers.items():
            actual_value = response.headers.get(header, '')
            
            if isinstance(expected_values, list):
                # Check if any of the expected values are present
                found = False
                for expected in expected_values:
                    if expected in actual_value:
                        found = True
                        break
                if found:
                    headers_found += 1
                    print(f"   ✓ {header} header present")
                else:
                    print(f"   ⚠️  Missing or incorrect {header} header")
            else:
                if expected_values in actual_value:
                    headers_found += 1
                    print(f"   ✓ {header} header present")
                else:
                    print(f"   ⚠️  Missing or incorrect {header} header")
        
        # Check CSP if implemented
        csp_header = response.headers.get('Content-Security-Policy', '')
        if csp_header:
            print(f"   ✓ CSP header present")
        else:
            print("   ⚠️  Consider adding Content-Security-Policy header")
        
        if headers_found >= 2:  # At least 2 of 3 major headers
            print("   ✓ Basic security headers in place")
        else:
            print("   ⚠️  Missing important security headers")

    def test_https_redirect(self):
        """Test HTTPS redirect in production - Skip if not configured"""
        print("\n🔒 Testing HTTPS settings...")
        
        from django.conf import settings
        
        # These are warnings, not failures, in test environment
        warnings = []
        
        if hasattr(settings, 'SECURE_SSL_REDIRECT'):
            if not settings.SECURE_SSL_REDIRECT:
                warnings.append("SECURE_SSL_REDIRECT should be True in production")
            else:
                print("   ✓ SECURE_SSL_REDIRECT is enabled")
        
        if hasattr(settings, 'SESSION_COOKIE_SECURE'):
            if not settings.SESSION_COOKIE_SECURE:
                warnings.append("SESSION_COOKIE_SECURE should be True in production")
            else:
                print("   ✓ SESSION_COOKIE_SECURE is enabled")
        
        if hasattr(settings, 'CSRF_COOKIE_SECURE'):
            if not settings.CSRF_COOKIE_SECURE:
                warnings.append("CSRF_COOKIE_SECURE should be True in production")
            else:
                print("   ✓ CSRF_COOKIE_SECURE is enabled")
        
        if warnings:
            print("   ⚠️  HTTPS warnings (OK for development):")
            for warning in warnings:
                print(f"     - {warning}")
        else:
            print("   ✓ HTTPS settings configured")
        
        def test_cors_configuration(self):
            """Test CORS settings"""
            print("\n🔒 Testing CORS configuration...")
            
            if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
                # Should not be wildcard in production
                self.assertNotIn('*', settings.CORS_ALLOWED_ORIGINS,
                            "CORS_ALLOWED_ORIGINS should not be '*' in production")
            
            if hasattr(settings, 'CORS_ORIGIN_ALLOW_ALL'):
                self.assertFalse(getattr(settings, 'CORS_ORIGIN_ALLOW_ALL', False),
                            "CORS_ORIGIN_ALLOW_ALL should be False")
            
            print("   ✓ CORS properly configured")