# realtime_dashboard_auth

Real-Time Dashboard Authentication Layer

Provides authentication and authorization for WebSocket connections.

Features:
    - Admin token generation and validation
    - WebSocket middleware authentication
    - Session management with 30-minute timeout
    - Audit logging for admin operations
    - Token revocation support
    - Role-based access control (RBAC)

Security:
    - Tokens are UUID-based (cryptographically random)
    - Automatic token expiration (30 minutes)
    - Audit trail for all authentication events
    - Admin-only access enforcement
    - Session cleanup for expired tokens

Usage:
    auth = RealtimeDashboardAuth()
    
    # Generate admin token
    token = auth.generate_token('admin_user', is_admin=True)
    
    user_info = auth.validate_token(token)
    if user_info and user_info['is_admin']:
        # Grant access
        pass
    
    # Revoke token
    auth.revoke_token(token)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [TokenStatus](#tokenstatus)
- [AuthToken](#authtoken)
- [AuditLogEntry](#auditlogentry)
- [RealtimeDashboardAuth](#realtimedashboardauth)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, logging, pathlib, sqlite3, typing, uuid


## Classes

### TokenStatus

```python
class TokenStatus(Enum)
```

Token status enumeration.



---

### AuthToken

```python
class AuthToken
```

**Decorators:** `dataclass`

Authentication token data structure.


**Attributes:**

- `token`: str
- `user_id`: str
- `is_admin`: bool
- `created_at`: datetime
- `expires_at`: datetime
- `status`: TokenStatus
- `metadata`: Dict[str, Any]



---

### AuditLogEntry

```python
class AuditLogEntry
```

**Decorators:** `dataclass`

Audit log entry data structure.


**Attributes:**

- `timestamp`: datetime
- `user_id`: str
- `action`: str
- `resource`: str
- `success`: bool
- `ip_address`: Optional[str]
- `details`: Dict[str, Any]



---

### RealtimeDashboardAuth

```python
class RealtimeDashboardAuth
```

Authentication layer for real-time dashboard WebSocket connections.

Features:
    - Token-based authentication (UUID)
    - Session management with expiration
    - Audit logging
    - Token revocation
    - Admin-only access enforcement

Attributes:
    tokens (Dict[str, AuthToken]): Active tokens
    audit_log (List[AuditLogEntry]): Audit log entries
    token_duration (timedelta): Token expiration duration


**Methods:**

  #### `generate_token`

  ```python
  generate_token(self, user_id: str, is_admin: bool, metadata: Optional[Dict[str, Any]]) -> str
  ```

  Generate authentication token.

Args:
    user_id: User identifier
    is_admin: Admin privileges flag
    metadata: Additional token metadata
    
Returns:
    Authentication token (UUID)

  **Parameters:**

  - `self`
  - `user_id` (str): User identifier
  - `is_admin` (bool) = `False`: Admin privileges flag
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional token metadata


  **Returns:** str
    Authentication token (UUID)


  #### `validate_token`

  ```python
  validate_token(self, token: str) -> Optional[Dict[str, Any]]
  ```

  Validate authentication token.

Args:
    token: Authentication token
    
Returns:
    User information if valid, None otherwise

  **Parameters:**

  - `self`
  - `token` (str): Authentication token


  **Returns:** Optional[Dict[str, Any]]
    User information if valid, None otherwise


  #### `revoke_token`

  ```python
  revoke_token(self, token: str) -> bool
  ```

  Revoke authentication token.

Args:
    token: Authentication token
    
Returns:
    True if revoked, False if not found

  **Parameters:**

  - `self`
  - `token` (str): Authentication token


  **Returns:** bool
    True if revoked, False if not found


  #### `cleanup_expired_tokens`

  ```python
  cleanup_expired_tokens(self) -> int
  ```

  Clean up expired tokens.

Returns:
    Number of tokens cleaned up

  **Parameters:**

  - `self`


  **Returns:** int
    Number of tokens cleaned up


  #### `get_active_sessions`

  ```python
  get_active_sessions(self) -> List[Dict[str, Any]]
  ```

  Get list of active sessions.

Returns:
    List of active session information

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of active session information


  #### `get_audit_log`

  ```python
  get_audit_log(self, user_id: Optional[str], limit: int) -> List[Dict[str, Any]]
  ```

  Get audit log entries.

Args:
    user_id: Filter by user ID (optional)
    limit: Maximum number of entries
    
Returns:
    List of audit log entries

  **Parameters:**

  - `self`
  - `user_id` (Optional[str]) = `None`: Filter by user ID (optional)
  - `limit` (int) = `100`: Maximum number of entries


  **Returns:** List[Dict[str, Any]]
    List of audit log entries



---
