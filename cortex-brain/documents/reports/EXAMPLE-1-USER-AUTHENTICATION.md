# TDD Mastery - Real-World Example: User Authentication

**Example Type:** Complete TDD workflow for authentication system  
**Phase:** All phases (Phase 1 + Phase 2 + Phase 3 integration)  
**Language:** Python  
**Framework:** FastAPI + pytest

---

## Scenario

Building a secure user authentication system with:
- User registration
- Login with JWT tokens
- Password hashing (bcrypt)
- Session management
- Role-based access control

---

## Step 1: Initialize TDD Session

```python
from src.workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)

# Configure orchestrator
config = TDDWorkflowConfig(
    project_root="/path/to/project",
    test_output_dir="tests",
    enable_refactoring=True,
    enable_session_tracking=True
)

orchestrator = TDDWorkflowOrchestrator(config)

# Start TDD session
session_id = orchestrator.start_session("user_authentication")
print(f"Started session: {session_id}")
```

---

## Step 2: RED Phase - Generate Tests

### Source Code (Initial Skeleton)

**File:** `src/auth/user_service.py`

```python
from typing import Optional
from datetime import datetime, timedelta
import bcrypt
import jwt


class UserService:
    """User authentication service."""
    
    def __init__(self, secret_key: str, database):
        self.secret_key = secret_key
        self.database = database
    
    def register_user(self, username: str, email: str, password: str) -> dict:
        """
        Register new user.
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            
        Returns:
            User object with id, username, email, created_at
            
        Raises:
            ValueError: If username/email already exists
            ValueError: If password too weak
        """
        pass
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and return JWT token.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            JWT token if authentication successful, None otherwise
        """
        pass
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify JWT token and return user data.
        
        Args:
            token: JWT token
            
        Returns:
            User data if token valid, None otherwise
        """
        pass
```

### Generate Comprehensive Tests

```python
# Generate tests using TDD orchestrator
result = orchestrator.generate_tests(
    source_file="src/auth/user_service.py",
    scenarios=[
        "edge_cases",           # Empty strings, None values
        "domain_knowledge",     # Authentication patterns
        "error_conditions",     # ValueError, TypeError
        "parametrized",         # Multiple test cases
        "property_based"        # Hypothesis testing
    ]
)

print(f"Generated {result['test_count']} tests")
print(f"Test file: {result['test_file']}")
```

### Generated Test File

**File:** `tests/auth/test_user_service.py` (Auto-generated)

```python
import pytest
from hypothesis import given, strategies as st
from src.auth.user_service import UserService


class TestUserServiceRegistration:
    """Test user registration functionality."""
    
    def test_register_user_basic(self, mock_database):
        """Should register user with valid credentials."""
        service = UserService("secret_key", mock_database)
        
        user = service.register_user(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123!"
        )
        
        assert user["username"] == "john_doe"
        assert user["email"] == "john@example.com"
        assert "id" in user
        assert "created_at" in user
        assert "password" not in user  # Password should not be in response
    
    # Edge Cases (Phase 1 - M1.1)
    def test_register_user_empty_username(self, mock_database):
        """Should raise ValueError for empty username."""
        service = UserService("secret_key", mock_database)
        
        with pytest.raises(ValueError, match="Username cannot be empty"):
            service.register_user("", "email@test.com", "password")
    
    def test_register_user_empty_email(self, mock_database):
        """Should raise ValueError for empty email."""
        service = UserService("secret_key", mock_database)
        
        with pytest.raises(ValueError, match="Email cannot be empty"):
            service.register_user("username", "", "password")
    
    def test_register_user_duplicate_username(self, mock_database):
        """Should raise ValueError for duplicate username."""
        service = UserService("secret_key", mock_database)
        service.register_user("john", "john@example.com", "password")
        
        with pytest.raises(ValueError, match="Username already exists"):
            service.register_user("john", "other@example.com", "password")
    
    # Domain Knowledge (Phase 1 - M1.2)
    def test_register_user_password_hashed(self, mock_database):
        """Should store hashed password, not plain text."""
        service = UserService("secret_key", mock_database)
        
        service.register_user("user", "user@test.com", "MyPassword123")
        
        stored_password = mock_database.get_user("user")["password"]
        assert stored_password != "MyPassword123"
        assert stored_password.startswith("$2b$")  # bcrypt hash prefix
    
    def test_register_user_weak_password(self, mock_database):
        """Should reject weak passwords."""
        service = UserService("secret_key", mock_database)
        
        with pytest.raises(ValueError, match="Password too weak"):
            service.register_user("user", "user@test.com", "123")
    
    # Parametrized Tests (Phase 1 - M1.4)
    @pytest.mark.parametrize("username,email,password,expected_error", [
        ("", "valid@email.com", "Pass123!", "Username cannot be empty"),
        ("valid_user", "", "Pass123!", "Email cannot be empty"),
        ("valid_user", "valid@email.com", "", "Password cannot be empty"),
        ("valid_user", "invalid_email", "Pass123!", "Invalid email format"),
        ("a", "valid@email.com", "Pass123!", "Username too short"),
        ("valid_user", "valid@email.com", "123", "Password too weak"),
    ])
    def test_register_user_validation(
        self, mock_database, username, email, password, expected_error
    ):
        """Should validate registration inputs."""
        service = UserService("secret_key", mock_database)
        
        with pytest.raises(ValueError, match=expected_error):
            service.register_user(username, email, password)
    
    # Property-Based Tests (Phase 1 - M1.4)
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(categories=["L", "N"])),
        password=st.text(min_size=8, max_size=100)
    )
    def test_register_user_password_never_stored_plaintext(self, mock_database, username, password):
        """Property: Password should never be stored in plain text."""
        service = UserService("secret_key", mock_database)
        email = f"{username}@example.com"
        
        try:
            service.register_user(username, email, password)
            stored_user = mock_database.get_user(username)
            
            # Property: Stored password must be different from input
            assert stored_user["password"] != password
            
        except ValueError:
            # Validation errors are acceptable
            pass


class TestUserServiceAuthentication:
    """Test user authentication functionality."""
    
    def test_authenticate_user_valid_credentials(self, mock_database):
        """Should return JWT token for valid credentials."""
        service = UserService("secret_key", mock_database)
        
        # Register user first
        service.register_user("alice", "alice@example.com", "SecurePass123!")
        
        # Authenticate
        token = service.authenticate_user("alice", "SecurePass123!")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long
    
    def test_authenticate_user_invalid_password(self, mock_database):
        """Should return None for invalid password."""
        service = UserService("secret_key", mock_database)
        service.register_user("bob", "bob@example.com", "CorrectPassword")
        
        token = service.authenticate_user("bob", "WrongPassword")
        
        assert token is None
    
    def test_authenticate_user_nonexistent_user(self, mock_database):
        """Should return None for nonexistent user."""
        service = UserService("secret_key", mock_database)
        
        token = service.authenticate_user("nonexistent", "password")
        
        assert token is None
    
    # Domain Knowledge (Phase 1 - M1.2)
    def test_authenticate_user_token_contains_user_id(self, mock_database):
        """Should include user ID in JWT token."""
        service = UserService("secret_key", mock_database)
        service.register_user("charlie", "charlie@example.com", "Pass123!")
        
        token = service.authenticate_user("charlie", "Pass123!")
        user_data = service.verify_token(token)
        
        assert "user_id" in user_data
        assert user_data["username"] == "charlie"
    
    def test_authenticate_user_token_has_expiration(self, mock_database):
        """Should include expiration time in JWT token."""
        service = UserService("secret_key", mock_database)
        service.register_user("dave", "dave@example.com", "Pass123!")
        
        token = service.authenticate_user("dave", "Pass123!")
        user_data = service.verify_token(token)
        
        assert "exp" in user_data
        assert user_data["exp"] > datetime.now().timestamp()


class TestUserServiceTokenVerification:
    """Test JWT token verification."""
    
    def test_verify_token_valid(self, mock_database):
        """Should verify valid token."""
        service = UserService("secret_key", mock_database)
        service.register_user("eve", "eve@example.com", "Pass123!")
        token = service.authenticate_user("eve", "Pass123!")
        
        user_data = service.verify_token(token)
        
        assert user_data is not None
        assert user_data["username"] == "eve"
    
    def test_verify_token_invalid_signature(self, mock_database):
        """Should reject token with invalid signature."""
        service = UserService("secret_key", mock_database)
        
        # Create token with different secret
        other_service = UserService("different_secret", mock_database)
        other_service.database = service.database
        other_service.register_user("frank", "frank@example.com", "Pass123!")
        bad_token = other_service.authenticate_user("frank", "Pass123!")
        
        # Try to verify with original service
        user_data = service.verify_token(bad_token)
        
        assert user_data is None
    
    def test_verify_token_expired(self, mock_database, freezer):
        """Should reject expired token."""
        service = UserService("secret_key", mock_database)
        service.register_user("grace", "grace@example.com", "Pass123!")
        token = service.authenticate_user("grace", "Pass123!")
        
        # Fast-forward time by 2 hours
        freezer.move_to(datetime.now() + timedelta(hours=2))
        
        user_data = service.verify_token(token)
        
        assert user_data is None
    
    # Error Conditions (Phase 1 - M1.3)
    def test_verify_token_malformed(self, mock_database):
        """Should handle malformed tokens gracefully."""
        service = UserService("secret_key", mock_database)
        
        user_data = service.verify_token("not.a.valid.jwt.token")
        
        assert user_data is None
    
    def test_verify_token_empty_string(self, mock_database):
        """Should handle empty token string."""
        service = UserService("secret_key", mock_database)
        
        user_data = service.verify_token("")
        
        assert user_data is None


# Pytest fixtures
@pytest.fixture
def mock_database():
    """Mock database for testing."""
    class MockDatabase:
        def __init__(self):
            self.users = {}
        
        def get_user(self, username):
            return self.users.get(username)
        
        def create_user(self, user_data):
            self.users[user_data["username"]] = user_data
            return user_data
        
        def user_exists(self, username):
            return username in self.users
    
    return MockDatabase()


@pytest.fixture
def freezer(monkeypatch):
    """Fixture to freeze time for testing token expiration."""
    import datetime as dt
    
    class FreezeTime:
        def __init__(self):
            self.frozen_time = None
        
        def move_to(self, target_time):
            self.frozen_time = target_time
            monkeypatch.setattr(dt, "datetime", lambda: target_time)
    
    return FreezeTime()
```

---

## Step 3: Run Tests (Should Fail - RED Phase)

```bash
$ pytest tests/auth/test_user_service.py -v

# Expected Output:
# ======================== test session starts =========================
# tests/auth/test_user_service.py::TestUserServiceRegistration::test_register_user_basic FAILED
# tests/auth/test_user_service.py::TestUserServiceRegistration::test_register_user_empty_username FAILED
# ...
# ======================== 24 failed in 0.45s ==========================
```

All tests fail because we haven't implemented the functionality yet. This is **expected** in the RED phase.

---

## Step 4: GREEN Phase - Minimal Implementation

Now implement just enough code to make tests pass:

```python
# Update src/auth/user_service.py

import bcrypt
import jwt
import re
from datetime import datetime, timedelta
from typing import Optional


class UserService:
    """User authentication service."""
    
    def __init__(self, secret_key: str, database):
        self.secret_key = secret_key
        self.database = database
    
    def register_user(self, username: str, email: str, password: str) -> dict:
        """Register new user."""
        # Validation
        if not username:
            raise ValueError("Username cannot be empty")
        if len(username) < 3:
            raise ValueError("Username too short")
        if not email:
            raise ValueError("Email cannot be empty")
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
        if not password:
            raise ValueError("Password cannot be empty")
        if len(password) < 8:
            raise ValueError("Password too weak")
        
        # Check duplicates
        if self.database.user_exists(username):
            raise ValueError("Username already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        user_data = {
            "id": self._generate_id(),
            "username": username,
            "email": email,
            "password": hashed_password.decode(),
            "created_at": datetime.now().isoformat()
        }
        
        self.database.create_user(user_data)
        
        # Return user without password
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "created_at": user_data["created_at"]
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token."""
        user = self.database.get_user(username)
        
        if not user:
            return None
        
        # Verify password
        if not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return None
        
        # Generate JWT token
        payload = {
            "user_id": user["id"],
            "username": user["username"],
            "exp": datetime.now() + timedelta(hours=1)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token."""
        if not token:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _generate_id(self) -> str:
        """Generate unique user ID."""
        import uuid
        return str(uuid.uuid4())
```

---

## Step 5: Run Tests Again (Should Pass - GREEN Phase)

```bash
$ pytest tests/auth/test_user_service.py -v

# Expected Output:
# ======================== test session starts =========================
# tests/auth/test_user_service.py::TestUserServiceRegistration::test_register_user_basic PASSED
# tests/auth/test_user_service.py::TestUserServiceRegistration::test_register_user_empty_username PASSED
# ...
# ======================== 24 passed in 1.23s ==========================
```

Verify all tests pass:

```python
test_results = {
    "passed": 24,
    "failed": 0,
    "code_lines": 85
}

orchestrator.verify_tests_pass(test_results)
print("✅ GREEN phase complete - all tests passing!")
```

---

## Step 6: REFACTOR Phase - Get Suggestions

```python
# Get refactoring suggestions from Phase 2 intelligence
suggestions = orchestrator.suggest_refactorings("src/auth/user_service.py")

for suggestion in suggestions:
    print(f"\n{suggestion['type']}: {suggestion['description']}")
    print(f"Confidence: {suggestion['confidence']}")
    print(f"Effort: {suggestion['effort']}")
    print(f"\nBefore:\n{suggestion['code_before']}")
    print(f"\nAfter:\n{suggestion['code_after']}")
```

**Example Output:**

```
extract_method: Extract validation logic into separate method
Confidence: 0.85
Effort: medium

Before:
if not username:
    raise ValueError("Username cannot be empty")
if len(username) < 3:
    raise ValueError("Username too short")
...

After:
def _validate_username(self, username: str) -> None:
    if not username:
        raise ValueError("Username cannot be empty")
    if len(username) < 3:
        raise ValueError("Username too short")

# In register_user():
self._validate_username(username)
```

---

## Step 7: Apply Refactorings & Complete Cycle

```python
# Apply suggested refactorings (manual or automated)
# ... refactor code ...

# Complete refactor phase
orchestrator.complete_refactor_phase(
    lines_refactored=25,
    iterations=1
)

# Complete TDD cycle
metrics = orchestrator.complete_cycle()

print(f"\n✅ Cycle {metrics['cycle_number']} complete!")
print(f"Tests written: {metrics['tests_written']}")
print(f"Tests passing: {metrics['tests_passing']}")
print(f"Duration: {metrics['duration_seconds']:.1f}s")
```

---

## Step 8: Save Progress & Generate Summary

```python
from src.workflows.page_tracking import PageLocation

# Save current location
location = PageLocation(
    filepath="src/auth/user_service.py",
    line_number=45,
    column_offset=4,
    function_name="register_user",
    class_name="UserService"
)

orchestrator.save_progress(
    location=location,
    notes="Completed user registration with validation. Next: Add role-based access control."
)

# Get session summary
summary = orchestrator.get_session_summary()

print("\n📊 Session Summary:")
print(f"Feature: {summary['feature_name']}")
print(f"Total cycles: {summary['total_cycles']}")
print(f"Tests written: {summary['total_tests_written']}")
print(f"Tests passing: {summary['total_tests_passing']}")
print(f"Test pass rate: {summary['test_pass_rate']:.1f}%")
print(f"Code lines added: {summary['total_code_lines_added']}")
print(f"Code lines refactored: {summary['total_code_lines_refactored']}")
print(f"Total duration: {summary['total_duration_seconds']:.1f}s")
```

---

## Step 9: Resume Later (Optional)

```python
# Resume session later
resumed = orchestrator.resume_session(session_id)

print(f"\n🔄 Resumed session: {resumed['feature_name']}")
print(f"Last location: {resumed['last_location']['file']}:{resumed['last_location']['line']}")
print(f"Function: {resumed['last_location']['function']}")
print(f"Notes: {resumed['notes']}")

# Jump back to exact location and continue TDD workflow
```

---

## Benefits Demonstrated

### Phase 1 (Test Generation)
- ✅ **Edge Cases:** Empty strings, None values, boundary conditions
- ✅ **Domain Knowledge:** Password hashing, JWT token structure, email validation
- ✅ **Error Conditions:** ValueError for validation failures
- ✅ **Parametrized Tests:** Multiple input combinations
- ✅ **Property-Based Tests:** Password never stored plaintext (Hypothesis)

### Phase 2 (Workflow Management)
- ✅ **State Machine:** RED→GREEN→REFACTOR transitions enforced
- ✅ **Refactoring Intelligence:** Extract method, simplify validation
- ✅ **Session Tracking:** Save/resume exact location
- ✅ **Cycle Metrics:** Tests written/passing, duration, code lines

### Phase 3 (Integration)
- ✅ **Unified API:** Single orchestrator for complete workflow
- ✅ **End-to-End:** From test generation to refactoring suggestions
- ✅ **Production Ready:** Real-world authentication system with security best practices

---

## Next Example

See `EXAMPLE-2-PAYMENT-PROCESSING.md` for payment gateway integration with TDD.
