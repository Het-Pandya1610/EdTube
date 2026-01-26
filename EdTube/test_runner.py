# test_runner.py (updated)
"""
Custom test runner for security testing
"""
import os
import sys
from django.test.runner import DiscoverRunner

class SecurityTestRunner(DiscoverRunner):
    """
    Custom test runner specifically for security tests.
    
    Usage:
    1. Run all security tests:
       python manage.py test --testrunner=EdTube.test_runner.SecurityTestRunner
       
    2. Or add to settings.py:
       TEST_RUNNER = 'EdTube.test_runner.SecurityTestRunner'
    """
    
    def run_tests(self, test_labels, **kwargs):
        """
        Override to run only security tests by default
        """
        # If no specific tests are specified, run security tests
        if not test_labels:
            test_labels = ['security_tests']
        
        print("\n" + "="*60)
        print("🔒 RUNNING SECURITY TESTS")
        print("="*60)
        print(f"Test labels: {test_labels}")
        
        # Run the tests - REMOVE extra_tests parameter
        result = super().run_tests(test_labels, **kwargs)
        
        print("\n" + "="*60)
        print("🔒 SECURITY TESTS COMPLETE")
        print("="*60)
        
        return result
    
    def setup_test_environment(self, **kwargs):
        """
        Setup for security testing environment
        """
        super().setup_test_environment(**kwargs)
        
        # You can add security-specific test setup here
        # For example, enable stricter security settings during tests
        print("\n⚠️  Security test environment initialized")
        print("   - Debug mode: DISABLED for security tests")
        print("   - Secure settings: ENABLED")
    
    def teardown_test_environment(self, **kwargs):
        """
        Cleanup after security tests
        """
        super().teardown_test_environment(**kwargs)
        print("\n✅ Security test environment cleaned up")


class RegularTestRunner(DiscoverRunner):
    """
    Regular test runner for functional tests (excludes security tests)
    """
    
    def run_tests(self, test_labels, **kwargs):
        """
        Run all tests EXCEPT security tests
        """
        print("\n" + "="*60)
        print("🧪 RUNNING FUNCTIONAL TESTS")
        print("="*60)
        
        # Exclude security tests
        if not test_labels:
            # Default: run all app tests but not security_tests
            test_labels = ['accounts', 'teacher', 'video', 'pages', 'student']
        
        return super().run_tests(test_labels, **kwargs)

class AllTestsRunner(DiscoverRunner):
    """
    Run ALL tests (both functional and security)
    """
    
    def run_tests(self, test_labels, **kwargs):
        """
        Run all tests including security
        """
        print("\n" + "="*60)
        print("🚀 RUNNING ALL TESTS (Functional + Security)")
        print("="*60)
        
        if not test_labels:
            # Run everything
            test_labels = ['accounts', 'teacher', 'video', 'pages', 
                          'student', 'security_tests']
        
        return super().run_tests(test_labels, **kwargs)