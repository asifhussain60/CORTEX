# Toolkit Security Model

**Purpose:** Security considerations for CORTEX tools  
**Audience:** Security Teams, Architects  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Input Validation](#input-validation)
- [Output Sanitization](#output-sanitization)
- [Rate Limiting](#rate-limiting)
- [Audit Logging](#audit-logging)
- [Related Documents](#related-documents)

---

## Overview

CORTEX tools implement defense-in-depth security with multiple layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 1: Authentication                                 │   │
│  │  • API Key validation                                    │   │
│  │  • Token verification                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 2: Authorization                                  │   │
│  │  • Permission checking                                   │   │
│  │  • Scope validation                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 3: Input Validation                               │   │
│  │  • Schema validation                                     │   │
│  │  • Path traversal prevention                             │   │
│  │  • Injection prevention                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 4: Rate Limiting                                  │   │
│  │  • Request throttling                                    │   │
│  │  • Burst protection                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Layer 5: Audit Logging                                  │   │
│  │  • Request logging                                       │   │
│  │  • Action tracking                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication

### API Key Authentication

```python
class APIKeyAuthenticator:
    """Validate API keys for tool access."""
    
    def __init__(self, key_store: KeyStore):
        self.key_store = key_store
    
    async def authenticate(
        self,
        request: Request
    ) -> AuthResult:
        """Authenticate request using API key."""
        # Extract key from header
        api_key = request.headers.get("X-CORTEX-API-KEY")
        
        if not api_key:
            return AuthResult(
                authenticated=False,
                error="Missing API key"
            )
        
        # Validate key format
        if not self._is_valid_format(api_key):
            return AuthResult(
                authenticated=False,
                error="Invalid API key format"
            )
        
        # Look up key
        key_info = await self.key_store.get(api_key)
        
        if not key_info:
            return AuthResult(
                authenticated=False,
                error="Unknown API key"
            )
        
        # Check expiration
        if key_info.expired:
            return AuthResult(
                authenticated=False,
                error="API key expired"
            )
        
        return AuthResult(
            authenticated=True,
            client_id=key_info.client_id,
            permissions=key_info.permissions
        )
```

### Key Rotation

```python
class KeyRotationManager:
    """Manage API key rotation."""
    
    KEY_LIFETIME_DAYS = 90
    WARNING_DAYS = 14
    
    async def rotate_key(
        self,
        client_id: str
    ) -> RotationResult:
        """Rotate API key for client."""
        # Generate new key
        new_key = self._generate_key()
        
        # Store with overlap period
        await self.key_store.add(
            key=new_key,
            client_id=client_id,
            expires=datetime.utcnow() + timedelta(days=self.KEY_LIFETIME_DAYS)
        )
        
        # Mark old key for deprecation
        old_keys = await self.key_store.get_for_client(client_id)
        for key in old_keys[:-1]:  # Keep new key
            await self.key_store.set_deprecated(
                key,
                grace_period=timedelta(days=7)
            )
        
        return RotationResult(new_key=new_key)
```

---

## Authorization

### Permission Model

```python
class Permission(Enum):
    """Tool access permissions."""
    
    # Read operations
    READ_CODE = "read:code"
    READ_CONFIG = "read:config"
    READ_HISTORY = "read:history"
    
    # Write operations
    WRITE_CODE = "write:code"
    WRITE_CONFIG = "write:config"
    
    # Analysis operations
    ANALYZE_CODE = "analyze:code"
    ANALYZE_SECURITY = "analyze:security"
    
    # Admin operations
    ADMIN_AUDIT = "admin:audit"
    ADMIN_TOOLS = "admin:tools"
```

### Permission Checking

```python
class PermissionChecker:
    """Check permissions for tool access."""
    
    # Tool permission requirements
    TOOL_PERMISSIONS = {
        "cortex_lens_analyze": [Permission.ANALYZE_CODE],
        "cortex_process_request": [
            Permission.READ_CODE,
            Permission.WRITE_CODE
        ],
        "cortex_audit": [Permission.ADMIN_AUDIT],
        "cortex_git_history": [Permission.READ_HISTORY],
    }
    
    def check(
        self,
        tool_name: str,
        client_permissions: List[Permission]
    ) -> PermissionResult:
        """Check if client has required permissions."""
        required = self.TOOL_PERMISSIONS.get(tool_name, [])
        
        missing = [
            p for p in required
            if p not in client_permissions
        ]
        
        if missing:
            return PermissionResult(
                allowed=False,
                missing=missing,
                message=f"Missing permissions: {missing}"
            )
        
        return PermissionResult(allowed=True)
```

---

## Input Validation

### Schema Validation

```python
class InputValidator:
    """Validate tool inputs."""
    
    def validate(
        self,
        tool: Tool,
        arguments: Dict[str, Any]
    ) -> ValidationResult:
        """Validate arguments against tool schema."""
        errors = []
        
        for param in tool.get_parameters():
            value = arguments.get(param.name)
            
            # Check required
            if param.required and value is None:
                errors.append(f"Missing required parameter: {param.name}")
                continue
            
            if value is None:
                continue
            
            # Check type
            if not self._check_type(value, param.type):
                errors.append(
                    f"Invalid type for {param.name}: "
                    f"expected {param.type}, got {type(value).__name__}"
                )
            
            # Check enum
            if param.enum and value not in param.enum:
                errors.append(
                    f"Invalid value for {param.name}: "
                    f"must be one of {param.enum}"
                )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
```

### Path Traversal Prevention

```python
class PathValidator:
    """Prevent path traversal attacks."""
    
    def validate_path(
        self,
        path: str,
        workspace: str
    ) -> PathValidationResult:
        """Validate path is within workspace."""
        # Normalize paths
        abs_path = os.path.abspath(path)
        abs_workspace = os.path.abspath(workspace)
        
        # Check containment
        if not abs_path.startswith(abs_workspace):
            return PathValidationResult(
                valid=False,
                error="Path traversal detected"
            )
        
        # Check for symlink escape
        real_path = os.path.realpath(abs_path)
        if not real_path.startswith(abs_workspace):
            return PathValidationResult(
                valid=False,
                error="Symlink escape detected"
            )
        
        return PathValidationResult(valid=True)
```

### Injection Prevention

```python
class InjectionPrevention:
    """Prevent code injection attacks."""
    
    DANGEROUS_PATTERNS = [
        r";\s*rm\s+",           # Shell injection
        r";\s*curl\s+",         # Network injection
        r"__import__\s*\(",     # Python import
        r"eval\s*\(",           # Eval injection
        r"exec\s*\(",           # Exec injection
    ]
    
    def check(self, value: str) -> InjectionCheckResult:
        """Check for injection patterns."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return InjectionCheckResult(
                    safe=False,
                    pattern=pattern
                )
        
        return InjectionCheckResult(safe=True)
```

---

## Output Sanitization

### Sensitive Data Redaction

```python
class OutputSanitizer:
    """Sanitize tool outputs."""
    
    REDACTION_PATTERNS = [
        (r"password\s*=\s*['\"].*['\"]", "password=***REDACTED***"),
        (r"api_key\s*=\s*['\"].*['\"]", "api_key=***REDACTED***"),
        (r"secret\s*=\s*['\"].*['\"]", "secret=***REDACTED***"),
        (r"-----BEGIN.*PRIVATE KEY-----.*-----END.*PRIVATE KEY-----",
         "***PRIVATE_KEY_REDACTED***"),
    ]
    
    def sanitize(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize output data."""
        return self._sanitize_value(output)
    
    def _sanitize_value(self, value: Any) -> Any:
        """Recursively sanitize value."""
        if isinstance(value, str):
            return self._redact_sensitive(value)
        elif isinstance(value, dict):
            return {
                k: self._sanitize_value(v)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            return [self._sanitize_value(v) for v in value]
        else:
            return value
    
    def _redact_sensitive(self, text: str) -> str:
        """Redact sensitive patterns."""
        for pattern, replacement in self.REDACTION_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.DOTALL)
        return text
```

---

## Rate Limiting

### Token Bucket Algorithm

```python
class RateLimiter:
    """Rate limiting using token bucket."""
    
    def __init__(
        self,
        rate: int = 60,      # Requests per minute
        burst: int = 10      # Burst capacity
    ):
        self.rate = rate
        self.burst = burst
        self._buckets: Dict[str, TokenBucket] = {}
    
    async def check(self, client_id: str) -> RateLimitResult:
        """Check if request is allowed."""
        bucket = self._get_bucket(client_id)
        
        if bucket.consume():
            return RateLimitResult(
                allowed=True,
                remaining=bucket.tokens,
                reset_at=bucket.next_refill
            )
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=bucket.next_refill,
            retry_after=bucket.seconds_until_refill
        )
    
    def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create bucket for client."""
        if client_id not in self._buckets:
            self._buckets[client_id] = TokenBucket(
                capacity=self.burst,
                refill_rate=self.rate / 60  # Per second
            )
        return self._buckets[client_id]
```

---

## Audit Logging

### Audit Trail

```python
class ToolAuditLogger:
    """Log tool invocations for audit."""
    
    async def log(
        self,
        tool_name: str,
        client_id: str,
        arguments: Dict[str, Any],
        result: ToolResult,
        context: Dict[str, Any]
    ) -> str:
        """Log tool invocation."""
        audit_id = self._generate_audit_id()
        
        entry = AuditEntry(
            id=audit_id,
            timestamp=datetime.utcnow(),
            tool=tool_name,
            client_id=client_id,
            arguments=self._sanitize_for_log(arguments),
            success=result.success,
            error=result.error,
            duration_ms=context.get("duration_ms"),
            source_ip=context.get("source_ip")
        )
        
        await self._store.save(entry)
        
        return audit_id
```

---

## Related Documents

- [Toolkit Overview](overview.md) — Introduction
- [Developer Guide](developer-guide.md) — Creating tools
- [Governance](../capabilities/governance-compliance.md) — Compliance

---

*Part of CORTEX Architecture Documentation*
