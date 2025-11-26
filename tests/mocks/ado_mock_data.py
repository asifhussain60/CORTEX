"""
ADO Mock Data for End-to-End Testing

Purpose:
- Provides realistic mock Azure DevOps API responses
- Enables CI/CD testing without real ADO connection
- Supports multiple test scenarios (clean PRs, problematic PRs)

Author: Asif Hussain
Created: 2025-01-XX (Phase 4+5)
"""

from datetime import datetime
from typing import Dict, List, Any


# Mock PR metadata for a security-problematic PR
MOCK_PR_METADATA_SECURITY_ISSUES = {
    "pullRequestId": 12345,
    "title": "Add user authentication system",
    "description": "Implements JWT-based authentication with password hashing",
    "sourceRefName": "refs/heads/feature/auth",
    "targetRefName": "refs/heads/main",
    "status": "active",
    "createdBy": {
        "displayName": "John Developer",
        "uniqueName": "john@example.com"
    },
    "creationDate": "2025-01-15T10:30:00Z",
    "repository": {
        "id": "repo-id-123",
        "name": "MyApp",
        "project": {
            "name": "MyProject"
        }
    }
}

# Mock PR diffs - files with security issues
MOCK_PR_DIFFS_SECURITY_ISSUES = [
    {
        "item": {
            "path": "/src/auth.py"
        },
        "changeType": "add"
    },
    {
        "item": {
            "path": "/src/models/user.py"
        },
        "changeType": "edit"
    },
    {
        "item": {
            "path": "/tests/test_auth.py"
        },
        "changeType": "add"
    }
]

# Mock file content - auth.py with security issues
MOCK_FILE_CONTENT_AUTH_PY = '''"""
User authentication module
"""
import hashlib
import sqlite3

# Hardcoded secret - SECURITY ISSUE
SECRET_KEY = "my-secret-key-12345"
DB_PASSWORD = "admin123"

def authenticate_user(username, password):
    """Authenticate user with username and password."""
    # SQL Injection vulnerability - SECURITY ISSUE
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    conn = sqlite3.connect("users.db", password=DB_PASSWORD)
    cursor = conn.cursor()
    cursor.execute(query)
    
    user = cursor.fetchone()
    
    # Bare except - BEST PRACTICES ISSUE
    try:
        if user:
            return generate_token(user)
    except:
        pass
    
    return None

def generate_token(user):
    """Generate JWT token for user."""
    # Magic number - BEST PRACTICES ISSUE
    token_data = str(user) + SECRET_KEY
    token = hashlib.md5(token_data.encode()).hexdigest()  # Insecure MD5 - SECURITY ISSUE
    return token

# Long function - CODE SMELL (this would be 100+ lines)
def process_user_registration(username, email, password, first_name, last_name, age, address, city, country, phone):
    """Process user registration with validation."""
    # Nested loops - PERFORMANCE ISSUE
    for i in range(len(username)):
        for j in range(len(email)):
            for k in range(len(password)):
                if username[i] == email[j] == password[k]:
                    return False
    
    # N+1 query pattern - PERFORMANCE ISSUE
    users = get_all_users()
    for user in users:
        profile = get_user_profile(user.id)  # Separate query per user
        if profile.email == email:
            return False
    
    # TODO: Add proper validation
    # ... imagine 80+ more lines here
    return True
'''

# Mock file content - user.py with code smells
MOCK_FILE_CONTENT_USER_PY = '''"""
User model
"""

class User:
    """User model class."""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def SomeMethodWithCamelCase(self):  # Naming convention issue
        """Method with incorrect naming."""
        pass
    
    def check_permissions(self, user, resource, action, context, metadata):
        """Check user permissions - complex condition."""
        # Complex condition - CODE SMELL
        if user.is_active and not user.is_banned and user.age >= 18 and user.has_verified_email and (user.role == "admin" or user.role == "moderator") and resource.is_public or (resource.owner_id == user.id and action in ["read", "write", "delete"]):
            return True
        return False
'''

# Mock file content - test_auth.py (clean test file)
MOCK_FILE_CONTENT_TEST_AUTH_PY = '''"""
Authentication tests
"""
import pytest
from src.auth import authenticate_user, generate_token

def test_authenticate_user_valid():
    """Test authentication with valid credentials."""
    result = authenticate_user("testuser", "testpass")
    assert result is not None

def test_authenticate_user_invalid():
    """Test authentication with invalid credentials."""
    result = authenticate_user("testuser", "wrongpass")
    assert result is None

def test_generate_token():
    """Test token generation."""
    user = {"id": 1, "username": "testuser"}
    token = generate_token(user)
    assert token is not None
    assert len(token) > 0
'''

# Mock PR metadata for a clean PR
MOCK_PR_METADATA_CLEAN = {
    "pullRequestId": 67890,
    "title": "Add user model documentation",
    "description": "Improves code documentation and adds docstrings",
    "sourceRefName": "refs/heads/docs/user-model",
    "targetRefName": "refs/heads/main",
    "status": "active",
    "createdBy": {
        "displayName": "Jane Developer",
        "uniqueName": "jane@example.com"
    },
    "creationDate": "2025-01-16T14:00:00Z",
    "repository": {
        "id": "repo-id-123",
        "name": "MyApp",
        "project": {
            "name": "MyProject"
        }
    }
}

# Mock PR diffs - clean documentation changes
MOCK_PR_DIFFS_CLEAN = [
    {
        "item": {
            "path": "/docs/user-model.md"
        },
        "changeType": "add"
    },
    {
        "item": {
            "path": "/src/models/user.py"
        },
        "changeType": "edit"
    }
]

# Mock file content - user.py with good practices
MOCK_FILE_CONTENT_USER_PY_CLEAN = '''"""
User model with comprehensive documentation.

This module provides the User model class for managing user data
and authentication within the application.
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class User:
    """
    User model representing an application user.
    
    Attributes:
        user_id (int): Unique user identifier
        username (str): User's username
        email (str): User's email address
        is_active (bool): Whether user account is active
    """
    
    def __init__(self, user_id: int, username: str, email: str):
        """
        Initialize User instance.
        
        Args:
            user_id: Unique identifier
            username: User's username
            email: User's email address
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        logger.info(f"User {self.username} deactivated")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Returns:
            Dictionary with user data
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active
        }
'''

# Mock ADO work items
MOCK_WORK_ITEMS = [
    {
        "id": 1234,
        "fields": {
            "System.Title": "Implement user authentication",
            "System.WorkItemType": "User Story",
            "System.State": "Active",
            "System.Tags": "security; authentication"
        }
    }
]


def get_mock_pr_response(scenario: str = "security_issues") -> Dict[str, Any]:
    """
    Get mock PR API response for testing.
    
    Args:
        scenario: Test scenario ("security_issues", "clean", "performance_issues")
    
    Returns:
        Mock PR metadata dictionary
    """
    if scenario == "clean":
        return MOCK_PR_METADATA_CLEAN
    else:
        return MOCK_PR_METADATA_SECURITY_ISSUES


def get_mock_pr_diffs(scenario: str = "security_issues") -> List[Dict[str, Any]]:
    """
    Get mock PR diffs for testing.
    
    Args:
        scenario: Test scenario
    
    Returns:
        List of mock file changes
    """
    if scenario == "clean":
        return MOCK_PR_DIFFS_CLEAN
    else:
        return MOCK_PR_DIFFS_SECURITY_ISSUES


def get_mock_file_content(file_path: str, scenario: str = "security_issues") -> str:
    """
    Get mock file content for testing.
    
    Args:
        file_path: Path to file
        scenario: Test scenario
    
    Returns:
        Mock file content as string
    """
    file_mapping = {
        "security_issues": {
            "/src/auth.py": MOCK_FILE_CONTENT_AUTH_PY,
            "/src/models/user.py": MOCK_FILE_CONTENT_USER_PY,
            "/tests/test_auth.py": MOCK_FILE_CONTENT_TEST_AUTH_PY
        },
        "clean": {
            "/src/models/user.py": MOCK_FILE_CONTENT_USER_PY_CLEAN,
            "/docs/user-model.md": "# User Model Documentation\n\nComprehensive guide..."
        }
    }
    
    return file_mapping.get(scenario, {}).get(file_path, "")


def get_mock_work_items() -> List[Dict[str, Any]]:
    """
    Get mock ADO work items.
    
    Returns:
        List of mock work item dictionaries
    """
    return MOCK_WORK_ITEMS


# Mock ADO URL patterns
MOCK_ADO_URL_SECURITY_ISSUES = "https://dev.azure.com/myorg/MyProject/_git/MyApp/pullrequest/12345"
MOCK_ADO_URL_CLEAN = "https://dev.azure.com/myorg/MyProject/_git/MyApp/pullrequest/67890"
