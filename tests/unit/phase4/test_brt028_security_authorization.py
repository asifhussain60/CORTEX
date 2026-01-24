"""
BRT-028: Security & Authorization

Implements security patterns and authorization controls for the
resilience framework.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set, List
from threading import Lock
import hashlib
import hmac
import time
from enum import Enum


class Permission(Enum):
    """System permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"


class Role(Enum):
    """System roles."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class User:
    """User entity."""
    user_id: str
    username: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    enabled: bool = True
    created_at_ms: float = field(default_factory=lambda: time.time() * 1000)


@dataclass
class Secret:
    """Secret storage."""
    secret_id: str
    name: str
    value: str
    created_at_ms: float = field(default_factory=lambda: time.time() * 1000)
    rotated_at_ms: float = field(default_factory=lambda: time.time() * 1000)
    owner_id: str = ""


class AuthenticationProvider(ABC):
    """Base class for authentication providers."""
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return token."""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[str]:
        """Verify token and return user_id."""
        pass


class BasicAuthProvider(AuthenticationProvider):
    """Basic authentication provider."""
    
    def __init__(self):
        self._users: Dict[str, tuple] = {}  # username -> (password_hash, user_id)
        self._tokens: Dict[str, str] = {}  # token -> user_id
        self._lock = Lock()
    
    def register_user(self, username: str, password: str, user_id: str) -> bool:
        """Register a user."""
        with self._lock:
            if username in self._users:
                return False
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self._users[username] = (password_hash, user_id)
            return True
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user."""
        with self._lock:
            if username not in self._users:
                return None
            
            password_hash, user_id = self._users[username]
            provided_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash != provided_hash:
                return None
            
            # Generate token
            token = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()
            self._tokens[token] = user_id
            return token
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify token."""
        with self._lock:
            return self._tokens.get(token)


class TokenAuthProvider(AuthenticationProvider):
    """Token-based authentication provider."""
    
    def __init__(self, secret: str):
        self.secret = secret
        self._tokens: Dict[str, str] = {}
        self._lock = Lock()
    
    def create_token(self, user_id: str) -> str:
        """Create a token."""
        with self._lock:
            payload = f"{user_id}:{time.time()}"
            signature = hmac.new(
                self.secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            token = f"{payload}:{signature}"
            self._tokens[token] = user_id
            return token
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Not used for token auth."""
        return None
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify token signature."""
        with self._lock:
            if token not in self._tokens:
                return None
            
            try:
                parts = token.split(":")
                if len(parts) != 3:
                    return None
                
                user_id, timestamp, signature = parts[0], parts[1], parts[2]
                payload = f"{user_id}:{timestamp}"
                
                expected_sig = hmac.new(
                    self.secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if signature == expected_sig:
                    return user_id
            except Exception:
                pass
            
            return None


class AuthorizationManager:
    """Manages authorization and permissions."""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._roles: Dict[Role, Set[Permission]] = self._init_roles()
        self._lock = Lock()
    
    def _init_roles(self) -> Dict[Role, Set[Permission]]:
        """Initialize role permissions."""
        return {
            Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN, Permission.EXECUTE},
            Role.OPERATOR: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
            Role.VIEWER: {Permission.READ},
            Role.GUEST: set()
        }
    
    def register_user(self, user: User) -> bool:
        """Register a user."""
        with self._lock:
            if user.user_id in self._users:
                return False
            
            self._users[user.user_id] = user
            return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        with self._lock:
            return self._users.get(user_id)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission."""
        with self._lock:
            user = self._users.get(user_id)
            if not user or not user.enabled:
                return False
            
            role_permissions = self._roles.get(user.role, set())
            return permission in role_permissions or permission in user.permissions
    
    def add_permission(self, user_id: str, permission: Permission) -> bool:
        """Add explicit permission to user."""
        with self._lock:
            user = self._users.get(user_id)
            if not user:
                return False
            
            user.permissions.add(permission)
            return True
    
    def disable_user(self, user_id: str) -> bool:
        """Disable a user."""
        with self._lock:
            user = self._users.get(user_id)
            if not user:
                return False
            
            user.enabled = False
            return True


class SecretManager:
    """Manages secrets securely."""
    
    def __init__(self):
        self._secrets: Dict[str, Secret] = {}
        self._access_log: List[tuple] = []
        self._lock = Lock()
    
    def store_secret(self, secret: Secret) -> bool:
        """Store a secret."""
        with self._lock:
            if secret.secret_id in self._secrets:
                return False
            
            self._secrets[secret.secret_id] = secret
            return True
    
    def retrieve_secret(self, secret_id: str, user_id: str) -> Optional[str]:
        """Retrieve a secret (with access logging)."""
        with self._lock:
            secret = self._secrets.get(secret_id)
            if not secret:
                return None
            
            # Log access
            self._access_log.append((user_id, secret_id, time.time() * 1000))
            
            return secret.value
    
    def rotate_secret(self, secret_id: str, new_value: str) -> bool:
        """Rotate a secret."""
        with self._lock:
            secret = self._secrets.get(secret_id)
            if not secret:
                return False
            
            secret.value = new_value
            secret.rotated_at_ms = time.time() * 1000
            return True
    
    def get_access_log(self, secret_id: str) -> List[tuple]:
        """Get access log for a secret."""
        with self._lock:
            return [(u, s, t) for u, s, t in self._access_log if s == secret_id]


class AuditLogger:
    """Logs security events."""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self._logs: List[Dict[str, Any]] = []
        self._lock = Lock()
    
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> bool:
        """Log a security event."""
        with self._lock:
            if len(self._logs) >= self.max_entries:
                # Remove oldest
                self._logs.pop(0)
            
            event = {
                "timestamp_ms": time.time() * 1000,
                "event_type": event_type,
                "user_id": user_id,
                "details": details
            }
            self._logs.append(event)
            return True
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logged events."""
        with self._lock:
            if event_type:
                return [e for e in self._logs if e["event_type"] == event_type]
            return self._logs.copy()
    
    def get_user_events(self, user_id: str) -> List[Dict[str, Any]]:
        """Get events for a specific user."""
        with self._lock:
            return [e for e in self._logs if e["user_id"] == user_id]


class RateLimitingPolicyManager:
    """Manages rate limiting policies."""
    
    def __init__(self):
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def create_policy(
        self,
        policy_id: str,
        requests_per_second: int,
        burst_size: int
    ) -> bool:
        """Create a rate limiting policy."""
        with self._lock:
            if policy_id in self._policies:
                return False
            
            self._policies[policy_id] = {
                "requests_per_second": requests_per_second,
                "burst_size": burst_size
            }
            return True
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a policy."""
        with self._lock:
            return self._policies.get(policy_id)


class EncryptionManager:
    """Manages encryption/decryption."""
    
    def encrypt(self, data: str, key: str) -> str:
        """Encrypt data (simple XOR for testing)."""
        # Note: This is simplified for testing. Use proper crypto in production.
        result = ""
        for i, char in enumerate(data):
            result += chr(ord(char) ^ ord(key[i % len(key)]))
        return result
    
    def decrypt(self, encrypted: str, key: str) -> str:
        """Decrypt data."""
        # XOR is symmetric, so same operation decrypts
        return self.encrypt(encrypted, key)


# ============================================================================
# TEST SUITE
# ============================================================================

class TestBasicAuthProvider:
    """Test BasicAuthProvider functionality."""
    
    def test_register_user(self):
        """Test user registration."""
        provider = BasicAuthProvider()
        assert provider.register_user("alice", "password123", "user_1")
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        provider = BasicAuthProvider()
        provider.register_user("alice", "password123", "user_1")
        
        token = provider.authenticate("alice", "password123")
        assert token is not None
    
    def test_authenticate_wrong_password(self):
        """Test authentication with wrong password."""
        provider = BasicAuthProvider()
        provider.register_user("alice", "password123", "user_1")
        
        token = provider.authenticate("alice", "wrongpassword")
        assert token is None
    
    def test_verify_token(self):
        """Test token verification."""
        provider = BasicAuthProvider()
        provider.register_user("alice", "password123", "user_1")
        
        token = provider.authenticate("alice", "password123")
        user_id = provider.verify_token(token)
        
        assert user_id == "user_1"


class TestTokenAuthProvider:
    """Test TokenAuthProvider functionality."""
    
    def test_create_token(self):
        """Test token creation."""
        provider = TokenAuthProvider("secret_key")
        token = provider.create_token("user_1")
        
        assert token is not None
    
    def test_verify_valid_token(self):
        """Test verifying valid token."""
        provider = TokenAuthProvider("secret_key")
        token = provider.create_token("user_1")
        
        user_id = provider.verify_token(token)
        assert user_id == "user_1"
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token."""
        provider = TokenAuthProvider("secret_key")
        
        user_id = provider.verify_token("invalid_token")
        assert user_id is None
    
    def test_verify_tampered_token(self):
        """Test verifying tampered token."""
        provider = TokenAuthProvider("secret_key")
        token = provider.create_token("user_1")
        
        # Tamper with token
        tampered = token[:-5] + "xxxxx"
        user_id = provider.verify_token(tampered)
        assert user_id is None


class TestAuthorizationManager:
    """Test AuthorizationManager functionality."""
    
    def test_register_user(self):
        """Test user registration."""
        manager = AuthorizationManager()
        user = User("user_1", "alice", Role.VIEWER)
        
        assert manager.register_user(user)
    
    def test_admin_has_all_permissions(self):
        """Test admin has all permissions."""
        manager = AuthorizationManager()
        user = User("user_1", "alice", Role.ADMIN)
        manager.register_user(user)
        
        assert manager.has_permission("user_1", Permission.READ)
        assert manager.has_permission("user_1", Permission.WRITE)
        assert manager.has_permission("user_1", Permission.DELETE)
        assert manager.has_permission("user_1", Permission.ADMIN)
    
    def test_viewer_has_read_only(self):
        """Test viewer has read-only permission."""
        manager = AuthorizationManager()
        user = User("user_1", "alice", Role.VIEWER)
        manager.register_user(user)
        
        assert manager.has_permission("user_1", Permission.READ)
        assert not manager.has_permission("user_1", Permission.WRITE)
    
    def test_disabled_user_no_permissions(self):
        """Test disabled user has no permissions."""
        manager = AuthorizationManager()
        user = User("user_1", "alice", Role.ADMIN)
        manager.register_user(user)
        
        manager.disable_user("user_1")
        assert not manager.has_permission("user_1", Permission.READ)
    
    def test_add_explicit_permission(self):
        """Test adding explicit permission to user."""
        manager = AuthorizationManager()
        user = User("user_1", "alice", Role.GUEST)
        manager.register_user(user)
        
        manager.add_permission("user_1", Permission.READ)
        assert manager.has_permission("user_1", Permission.READ)


class TestSecretManager:
    """Test SecretManager functionality."""
    
    def test_store_secret(self):
        """Test storing a secret."""
        manager = SecretManager()
        secret = Secret("s1", "api_key", "secret_value", owner_id="user_1")
        
        assert manager.store_secret(secret)
    
    def test_retrieve_secret(self):
        """Test retrieving a secret."""
        manager = SecretManager()
        secret = Secret("s1", "api_key", "secret_value", owner_id="user_1")
        manager.store_secret(secret)
        
        value = manager.retrieve_secret("s1", "user_1")
        assert value == "secret_value"
    
    def test_retrieve_nonexistent_secret(self):
        """Test retrieving nonexistent secret."""
        manager = SecretManager()
        value = manager.retrieve_secret("nonexistent", "user_1")
        assert value is None
    
    def test_rotate_secret(self):
        """Test rotating a secret."""
        manager = SecretManager()
        secret = Secret("s1", "api_key", "old_value", owner_id="user_1")
        manager.store_secret(secret)
        
        assert manager.rotate_secret("s1", "new_value")
        value = manager.retrieve_secret("s1", "user_1")
        assert value == "new_value"
    
    def test_access_log(self):
        """Test access logging."""
        manager = SecretManager()
        secret = Secret("s1", "api_key", "secret_value", owner_id="user_1")
        manager.store_secret(secret)
        
        manager.retrieve_secret("s1", "user_1")
        manager.retrieve_secret("s1", "user_2")
        
        log = manager.get_access_log("s1")
        assert len(log) == 2


class TestAuditLogger:
    """Test AuditLogger functionality."""
    
    def test_log_event(self):
        """Test logging an event."""
        logger = AuditLogger()
        
        assert logger.log_event(
            "LOGIN",
            "user_1",
            {"ip_address": "192.168.1.1"}
        )
    
    def test_get_events(self):
        """Test retrieving events."""
        logger = AuditLogger()
        
        logger.log_event("LOGIN", "user_1", {})
        logger.log_event("LOGOUT", "user_1", {})
        logger.log_event("LOGIN", "user_2", {})
        
        events = logger.get_events("LOGIN")
        assert len(events) == 2
    
    def test_get_user_events(self):
        """Test retrieving user events."""
        logger = AuditLogger()
        
        logger.log_event("LOGIN", "user_1", {})
        logger.log_event("LOGOUT", "user_1", {})
        logger.log_event("LOGIN", "user_2", {})
        
        events = logger.get_user_events("user_1")
        assert len(events) == 2


class TestRateLimitingPolicyManager:
    """Test RateLimitingPolicyManager functionality."""
    
    def test_create_policy(self):
        """Test creating a policy."""
        manager = RateLimitingPolicyManager()
        
        assert manager.create_policy("default", 100, 10)
    
    def test_get_policy(self):
        """Test getting a policy."""
        manager = RateLimitingPolicyManager()
        manager.create_policy("default", 100, 10)
        
        policy = manager.get_policy("default")
        assert policy["requests_per_second"] == 100
        assert policy["burst_size"] == 10


class TestEncryptionManager:
    """Test EncryptionManager functionality."""
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        manager = EncryptionManager()
        data = "sensitive_data"
        key = "encryption_key"
        
        encrypted = manager.encrypt(data, key)
        decrypted = manager.decrypt(encrypted, key)
        
        assert decrypted == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
