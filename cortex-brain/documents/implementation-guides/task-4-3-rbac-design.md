# Task 4.3 Design: RBAC Manager Implementation

**Plan:** A01 - Enterprise Python Audit Logger with Self-Healing  
**Phase:** 4 - Security Layer  
**Task:** 4.3 - Role-Based Access Control (RBAC)  
**Status:** 🎨 **DESIGN PHASE**  
**Date:** January 5, 2026  
**Author:** Asif Hussain

---

## 🎯 Objectives

Implement enterprise-grade role-based access control for audit logs with:
1. **Role Hierarchy:** admin → developer → auditor → read-only
2. **Permission Matrix:** Granular control over log operations
3. **Audit Trail:** All access attempts logged (success + failure)
4. **Integration:** Seamless with PII Sanitizer + Encryptor
5. **Compliance:** SOC 2, ISO 27001, NIST requirements

---

## 🏗️ Architecture

### Component Hierarchy
```
RBACManager (Main Class)
├── Role Definitions
│   ├── Admin (full access)
│   ├── Developer (write logs, read own logs)
│   ├── Auditor (read all logs, no write)
│   └── Read-Only (read sanitized logs only)
├── Permission Checker
│   ├── Operation validation
│   ├── Resource ownership
│   └── Time-based access
├── Audit Logger
│   ├── Access attempts (success/failure)
│   ├── Permission changes
│   └── Role assignments
└── Integration Layer
    ├── Encryptor integration (role-based keys)
    ├── PII Sanitizer integration (role-based redaction)
    └── Context manager (with RBAC())
```

### Design Patterns
- **Strategy Pattern:** Pluggable permission policies
- **Chain of Responsibility:** Permission checks cascade through hierarchy
- **Decorator Pattern:** @require_permission decorators
- **Context Manager:** Automatic audit logging with `with` statement
- **Observer Pattern:** Role change notifications

---

## 📊 Role Definitions

### Role Hierarchy (Inheritance)

```
Admin (Level 4)
  ↓ inherits all permissions
Developer (Level 3)
  ↓ inherits read permissions
Auditor (Level 2)
  ↓ inherits basic read
Read-Only (Level 1)
```

### Permission Matrix

| Operation | Admin | Developer | Auditor | Read-Only |
|-----------|-------|-----------|---------|-----------|
| **CREATE_LOG** | ✅ | ✅ | ❌ | ❌ |
| **READ_OWN_LOG** | ✅ | ✅ | ❌ | ❌ |
| **READ_ALL_LOGS** | ✅ | ❌ | ✅ | ✅ (sanitized) |
| **UPDATE_LOG** | ✅ | ✅ (own) | ❌ | ❌ |
| **DELETE_LOG** | ✅ | ❌ | ❌ | ❌ |
| **ENCRYPT_LOG** | ✅ | ✅ | ❌ | ❌ |
| **DECRYPT_LOG** | ✅ | ✅ (own) | ✅ | ❌ |
| **ROTATE_KEYS** | ✅ | ❌ | ❌ | ❌ |
| **ASSIGN_ROLE** | ✅ | ❌ | ❌ | ❌ |
| **VIEW_AUDIT_TRAIL** | ✅ | ❌ | ✅ | ❌ |
| **EXPORT_LOGS** | ✅ | ❌ | ✅ | ❌ |
| **SANITIZE_PII** | ✅ | ✅ | ❌ | ❌ |

### Role Details

#### Admin (Level 4)
- **Purpose:** System administrators, security officers
- **Permissions:** Full access to all operations
- **Key Features:**
  - Create, read, update, delete any log
  - Rotate encryption keys
  - Assign roles to users
  - View complete audit trail
  - Export logs in any format
- **Restrictions:** None (highest privilege)

#### Developer (Level 3)
- **Purpose:** Application developers, system integrators
- **Permissions:** Create logs, manage own logs
- **Key Features:**
  - Create new audit logs
  - Read logs they created (ownership)
  - Update/sanitize their own logs
  - Encrypt logs they create
  - Decrypt logs they own
- **Restrictions:**
  - Cannot read others' logs
  - Cannot delete any logs
  - Cannot rotate keys
  - Cannot assign roles

#### Auditor (Level 2)
- **Purpose:** Security auditors, compliance officers
- **Permissions:** Read-only access to all logs
- **Key Features:**
  - Read all audit logs (complete access)
  - Decrypt logs for audit purposes
  - View audit trail
  - Export logs for compliance
- **Restrictions:**
  - Cannot create, update, or delete logs
  - Cannot rotate keys
  - Cannot assign roles
  - Cannot sanitize PII

#### Read-Only (Level 1)
- **Purpose:** Viewers, report consumers, external auditors
- **Permissions:** Limited read access to sanitized logs
- **Key Features:**
  - Read all logs (PII automatically sanitized)
  - View redacted audit trail
- **Restrictions:**
  - Cannot decrypt logs
  - Cannot create, update, or delete logs
  - Cannot view full audit trail
  - Cannot export logs
  - Cannot access unsanitized data

---

## 🔐 Permission Model

### Permission Structure

```python
class Permission(Enum):
    """Enumeration of all available permissions"""
    CREATE_LOG = 'create_log'
    READ_OWN_LOG = 'read_own_log'
    READ_ALL_LOGS = 'read_all_logs'
    UPDATE_LOG = 'update_log'
    DELETE_LOG = 'delete_log'
    ENCRYPT_LOG = 'encrypt_log'
    DECRYPT_LOG = 'decrypt_log'
    ROTATE_KEYS = 'rotate_keys'
    ASSIGN_ROLE = 'assign_role'
    VIEW_AUDIT_TRAIL = 'view_audit_trail'
    EXPORT_LOGS = 'export_logs'
    SANITIZE_PII = 'sanitize_pii'
```

### Role Configuration

```python
ROLE_PERMISSIONS = {
    'admin': {
        'level': 4,
        'permissions': [  # All permissions
            Permission.CREATE_LOG,
            Permission.READ_OWN_LOG,
            Permission.READ_ALL_LOGS,
            Permission.UPDATE_LOG,
            Permission.DELETE_LOG,
            Permission.ENCRYPT_LOG,
            Permission.DECRYPT_LOG,
            Permission.ROTATE_KEYS,
            Permission.ASSIGN_ROLE,
            Permission.VIEW_AUDIT_TRAIL,
            Permission.EXPORT_LOGS,
            Permission.SANITIZE_PII
        ]
    },
    'developer': {
        'level': 3,
        'permissions': [
            Permission.CREATE_LOG,
            Permission.READ_OWN_LOG,
            Permission.UPDATE_LOG,  # Own logs only
            Permission.ENCRYPT_LOG,
            Permission.DECRYPT_LOG,  # Own logs only
            Permission.SANITIZE_PII
        ]
    },
    'auditor': {
        'level': 2,
        'permissions': [
            Permission.READ_ALL_LOGS,
            Permission.DECRYPT_LOG,
            Permission.VIEW_AUDIT_TRAIL,
            Permission.EXPORT_LOGS
        ]
    },
    'read_only': {
        'level': 1,
        'permissions': [
            Permission.READ_ALL_LOGS  # Sanitized only
        ]
    }
}
```

---

## 📝 API Design

### RBACManager Class

```python
class RBACManager:
    """Role-based access control manager"""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize RBAC manager with optional audit logger"""
        pass
    
    def create_user(self, user_id: str, role: str) -> User:
        """Create user with role"""
        pass
    
    def assign_role(self, user_id: str, role: str, by_user_id: str) -> bool:
        """Assign role to user (requires admin)"""
        pass
    
    def check_permission(self, user: User, permission: Permission, 
                        resource: Optional[Any] = None) -> bool:
        """Check if user has permission for operation"""
        pass
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Quick permission check by user ID"""
        pass
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for user"""
        pass
    
    def audit_access(self, user: User, operation: str, 
                    resource: Optional[str], success: bool) -> None:
        """Log access attempt to audit trail"""
        pass

    @contextmanager
    def as_user(self, user: User):
        """Context manager for user operations with audit logging"""
        pass
```

### User Class

```python
@dataclass
class User:
    """User with role and permissions"""
    user_id: str
    role: str
    created_at: datetime
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def permissions(self) -> List[Permission]:
        """Get permissions from role"""
        pass
    
    @property
    def level(self) -> int:
        """Get role level (1-4)"""
        pass
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        pass
    
    def can_access_resource(self, resource: Resource) -> bool:
        """Check resource ownership for developer role"""
        pass
```

### Decorator Pattern

```python
def require_permission(permission: Permission):
    """Decorator to enforce permission checks"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, user: User, *args, **kwargs):
            if not rbac_manager.check_permission(user, permission):
                raise PermissionDeniedError(
                    f"User {user.user_id} lacks permission: {permission}"
                )
            return func(self, user, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
@require_permission(Permission.CREATE_LOG)
def create_audit_log(self, user: User, log_data: Dict) -> str:
    """Create audit log (requires CREATE_LOG permission)"""
    pass
```

---

## 🔍 Audit Trail

### Access Logging

Every permission check is logged with:
- **User ID:** Who attempted access
- **Operation:** What they tried to do
- **Resource:** What they tried to access
- **Result:** Success or permission denied
- **Timestamp:** When the attempt occurred
- **Metadata:** Additional context (IP, session, etc.)

### Audit Log Format

```python
{
    "audit_id": "audit-20260105-123456-abc",
    "user_id": "user-123",
    "role": "developer",
    "operation": "READ_LOG",
    "resource": "log-789",
    "result": "success" | "denied",
    "timestamp": 1704470400,
    "metadata": {
        "ip_address": "192.168.1.100",
        "session_id": "sess-456",
        "reason": "Permission denied: READ_ALL_LOGS"
    }
}
```

### Audit Trail Operations

```python
# Log successful access
rbac_manager.audit_access(
    user=user,
    operation="READ_LOG",
    resource="log-123",
    success=True
)

# Log denied access
rbac_manager.audit_access(
    user=user,
    operation="DELETE_LOG",
    resource="log-456",
    success=False,
    reason="Permission denied: DELETE_LOG"
)
```

---

## 🔗 Integration with Security Components

### With Encryptor

```python
# Role-based encryption keys
class RoleBasedEncryptor:
    def __init__(self, rbac_manager: RBACManager, encryptor: Encryptor):
        self.rbac = rbac_manager
        self.encryptor = encryptor
    
    def encrypt_log(self, user: User, log_data: str) -> Dict:
        """Encrypt log with role-based access control"""
        if not self.rbac.check_permission(user, Permission.ENCRYPT_LOG):
            raise PermissionDeniedError()
        
        # Add role metadata to encrypted log
        encrypted = self.encryptor.encrypt(log_data, metadata={
            'created_by': user.user_id,
            'role': user.role,
            'access_level': user.level
        })
        
        self.rbac.audit_access(user, 'ENCRYPT_LOG', None, True)
        return encrypted
```

### With PII Sanitizer

```python
# Role-based sanitization
class RoleBasedSanitizer:
    def __init__(self, rbac_manager: RBACManager, sanitizer: PIISanitizer):
        self.rbac = rbac_manager
        self.sanitizer = sanitizer
    
    def get_log(self, user: User, log_id: str) -> str:
        """Get log with role-appropriate sanitization"""
        log_data = fetch_log(log_id)
        
        # Read-only users always get sanitized data
        if user.role == 'read_only':
            log_data = self.sanitizer.sanitize(log_data)
        
        # Auditors get full access for compliance
        elif user.role == 'auditor':
            pass  # No sanitization
        
        # Developers only see own logs unsanitized
        elif user.role == 'developer':
            if log_data['created_by'] != user.user_id:
                log_data = self.sanitizer.sanitize(log_data)
        
        self.rbac.audit_access(user, 'READ_LOG', log_id, True)
        return log_data
```

---

## 🧪 Test Cases

### Unit Tests (TDD RED Phase)

```python
def test_create_user_with_role():
    """Test user creation with role assignment"""
    rbac = RBACManager()
    user = rbac.create_user('user-123', 'developer')
    assert user.role == 'developer'
    assert user.level == 3

def test_admin_has_all_permissions():
    """Test admin role has all permissions"""
    rbac = RBACManager()
    admin = rbac.create_user('admin-1', 'admin')
    
    for permission in Permission:
        assert admin.has_permission(permission)

def test_developer_cannot_delete():
    """Test developer lacks delete permission"""
    rbac = RBACManager()
    dev = rbac.create_user('dev-1', 'developer')
    
    assert not dev.has_permission(Permission.DELETE_LOG)

def test_auditor_can_read_all():
    """Test auditor can read all logs"""
    rbac = RBACManager()
    auditor = rbac.create_user('auditor-1', 'auditor')
    
    assert auditor.has_permission(Permission.READ_ALL_LOGS)
    assert auditor.has_permission(Permission.VIEW_AUDIT_TRAIL)

def test_read_only_limited_access():
    """Test read-only user has minimal permissions"""
    rbac = RBACManager()
    viewer = rbac.create_user('viewer-1', 'read_only')
    
    assert viewer.has_permission(Permission.READ_ALL_LOGS)
    assert not viewer.has_permission(Permission.DECRYPT_LOG)
    assert not viewer.has_permission(Permission.CREATE_LOG)

def test_permission_denied_raises_error():
    """Test permission check raises error"""
    rbac = RBACManager()
    dev = rbac.create_user('dev-1', 'developer')
    
    with pytest.raises(PermissionDeniedError):
        rbac.check_permission(dev, Permission.DELETE_LOG, enforce=True)

def test_resource_ownership_check():
    """Test developer can only access own resources"""
    rbac = RBACManager()
    dev = rbac.create_user('dev-1', 'developer')
    
    resource_own = Resource(id='log-1', created_by='dev-1')
    resource_other = Resource(id='log-2', created_by='dev-2')
    
    assert dev.can_access_resource(resource_own)
    assert not dev.can_access_resource(resource_other)

def test_audit_trail_logging():
    """Test all access attempts are logged"""
    rbac = RBACManager()
    dev = rbac.create_user('dev-1', 'developer')
    
    # Successful access
    rbac.check_permission(dev, Permission.CREATE_LOG)
    
    # Failed access
    try:
        rbac.check_permission(dev, Permission.DELETE_LOG, enforce=True)
    except PermissionDeniedError:
        pass
    
    audit_trail = rbac.get_audit_trail(user_id='dev-1')
    assert len(audit_trail) == 2
    assert audit_trail[0]['result'] == 'success'
    assert audit_trail[1]['result'] == 'denied'

def test_role_assignment_requires_admin():
    """Test only admin can assign roles"""
    rbac = RBACManager()
    admin = rbac.create_user('admin-1', 'admin')
    dev = rbac.create_user('dev-1', 'developer')
    
    # Admin can assign
    assert rbac.assign_role('user-123', 'auditor', by_user_id='admin-1')
    
    # Developer cannot assign
    with pytest.raises(PermissionDeniedError):
        rbac.assign_role('user-456', 'admin', by_user_id='dev-1')

def test_context_manager_audit():
    """Test context manager logs operations"""
    rbac = RBACManager()
    dev = rbac.create_user('dev-1', 'developer')
    
    with rbac.as_user(dev):
        # Operations auto-logged
        create_log("Test log")
    
    audit_trail = rbac.get_audit_trail(user_id='dev-1')
    assert len(audit_trail) > 0
```

---

## 📊 Performance Targets

| Operation | Target | Method |
|-----------|--------|--------|
| **Permission Check** | <0.1ms | In-memory role lookup |
| **Audit Log Write** | <1ms | Async write (non-blocking) |
| **Role Assignment** | <10ms | Database update |
| **Get Permissions** | <0.1ms | Cached role permissions |

---

## 🔒 Security Considerations

### Best Practices
- ✅ Principle of least privilege (minimal permissions by default)
- ✅ Separation of duties (developers can't audit themselves)
- ✅ Defense in depth (multiple permission checks)
- ✅ Audit all access attempts (success and failure)
- ✅ Immutable audit trail (append-only)
- ✅ Time-based access (optional expiration)

### Threat Model
- **Attacker Goals:** Privilege escalation, unauthorized access
- **Attack Vectors:** Role spoofing, permission bypass, audit log tampering
- **Mitigations:** Cryptographic signatures, immutable logs, admin-only role assignment

---

## 📚 Dependencies

```python
# requirements.txt additions
# (None - uses standard library + existing audit_logger components)
```

---

## ✅ Completion Criteria

- [ ] RBACManager class implemented
- [ ] 4 roles with permission matrix
- [ ] Audit trail logging (all access attempts)
- [ ] Integration with Encryptor
- [ ] Integration with PII Sanitizer
- [ ] 20+ unit tests (100% coverage)
- [ ] Integration tests for full security stack
- [ ] Performance benchmarks (<0.1ms permission checks)
- [ ] Documentation (API docs, permission matrix)

---

## 🎯 Next Steps

1. ✅ **Design Complete** (this document)
2. ➡️ **Write Tests (RED):** Create test_rbac.py with failing tests
3. ➡️ **Implement (GREEN):** Create rbac.py to pass all tests
4. ➡️ **Refactor (REFACTOR):** Apply SKULL rules, optimize performance
5. ➡️ **Integration:** Test with PII Sanitizer + Encryptor
6. ➡️ **Documentation:** Update completion report

---

**Generated:** 2026-01-05T12:15:00Z  
**Author:** Asif Hussain  
**Review:** GitHub Copilot (CORTEX)
