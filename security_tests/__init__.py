# __init__.py (for security_tests package)
"""
Security Tests Package
"""
from .test_authentication import AuthenticationSecurityTests
from .test_sql_injection import SQLInjectionTests
from .test_xss import XSSTests
from .test_csrf import CSRFTests
from .test_file_upload import FileUploadSecurityTests
from .test_configuration import SecurityConfigurationTests
from .test_api_security import APISecurityTests
from .test_data_exposure import DataExposureTests

__all__ = [
    'AuthenticationSecurityTests',
    'SQLInjectionTests',
    'XSSTests',
    'CSRFTests',
    'FileUploadSecurityTests',
    'SecurityConfigurationTests',
    'APISecurityTests',
    'DataExposureTests',
]