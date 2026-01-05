"""
Access Control - Role-Based Access Control (RBAC) Implementation.

Provides:
- 4-tier role hierarchy (Admin, Developer, Auditor, Read-Only)
- Permission validation
- Audit trail for all access attempts
- Session-based access control
- IP whitelisting
- Time-based access restrictions
"""

import json
import uuid
import threading
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field


class AccessDeniedError(Exception):
    """Raised when access is denied."""
    pass


class Role(Enum):
    """User roles with hierarchy levels."""
    ADMIN = ("admin", 100)
    DEVELOPER = ("developer", 70)
    AUDITOR = ("auditor", 50)
    READ_ONLY = ("read_only", 10)
    
    def __init__(self, role_name: str, level: int):
        self.role_name = role_name
        self.level = level


class Permission(Enum):
    """Available permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CONFIGURE = "configure"
    AUDIT = "audit"


@dataclass
class AccessPolicy:
    """Access policy for a role."""
    role: Role
    allowed_permissions: List[Permission]
    inherits_from: Optional[Role] = None


@dataclass
class AuditEntry:
    """Audit trail entry for access attempts."""
    timestamp: datetime
    user_id: str
    role: str
    permission: str
    resource_id: Optional[str]
    result: str  # "granted" or "denied"
    reason: Optional[str] = None
    ip_address: Optional[str] = None


@dataclass
class Session:
    """User session with TTL."""
    session_id: str
    user: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    is_active: bool = True


class AccessControl:
    """
    Role-based access control for audit logs.
    
    Features:
    - 4-tier role hierarchy
    - Fine-grained permissions
    - Audit trail logging
    - Session management
    - IP whitelisting
    - Time-based restrictions
    """
    
    # Default policies for each role
    DEFAULT_POLICIES = [
        AccessPolicy(
            role=Role.ADMIN,
            allowed_permissions=[
                Permission.READ,
                Permission.WRITE,
                Permission.DELETE,
                Permission.CONFIGURE,
                Permission.AUDIT,
            ]
        ),
        AccessPolicy(
            role=Role.DEVELOPER,
            allowed_permissions=[Permission.READ, Permission.WRITE]
        ),
        AccessPolicy(
            role=Role.AUDITOR,
            allowed_permissions=[Permission.READ, Permission.AUDIT]
        ),
        AccessPolicy(
            role=Role.READ_ONLY,
            allowed_permissions=[Permission.READ]
        ),
    ]
    
    def __init__(self, policies: Optional[List[AccessPolicy]] = None):
        """
        Initialize access control.
        
        Args:
            policies: Custom access policies (uses defaults if None)
        """
        self.policies = policies or self.DEFAULT_POLICIES
        self._audit_trail: List[AuditEntry] = []
        self._sessions: Dict[str, Session] = {}
        self._revoked_users: set = set()
        self._lock = threading.Lock()
        
        # Build permission map
        self._permission_map: Dict[Role, List[Permission]] = {}
        for policy in self.policies:
            self._permission_map[policy.role] = policy.allowed_permissions.copy()
            
            # Add inherited permissions
            if policy.inherits_from:
                parent_perms = self._get_role_permissions(policy.inherits_from)
                self._permission_map[policy.role].extend(parent_perms)
    
    def _get_role_permissions(self, role: Role) -> List[Permission]:
        """Get permissions for a role."""
        return self._permission_map.get(role, [])
    
    def has_permission(self, user: Dict[str, Any], permission: Permission) -> bool:
        """
        Check if user has permission.
        
        Args:
            user: User dictionary with 'role' key
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        user_role = user.get("role")
        if not isinstance(user_role, Role):
            return False
        
        allowed_perms = self._get_role_permissions(user_role)
        return permission in allowed_perms
    
    def check_permission(
        self,
        user: Dict[str, Any],
        permission: Permission,
        resource_id: Optional[str] = None
    ):
        """
        Check permission and raise error if denied.
        
        Args:
            user: User dictionary
            permission: Permission to check
            resource_id: Optional resource ID
            
        Raises:
            AccessDeniedError: If access is denied
        """
        user_id = user.get("user_id", "unknown")
        user_role = user.get("role")
        
        # Check if user is revoked
        if user_id in self._revoked_users:
            self._log_access(user, permission, resource_id, "denied", "User revoked")
            raise AccessDeniedError(f"Access revoked for user: {user_id}")
        
        # Check permission
        has_perm = self.has_permission(user, permission)
        
        if has_perm:
            self._log_access(user, permission, resource_id, "granted")
        else:
            role_name = user_role.role_name if user_role else "unknown"
            reason = f"Role {role_name} lacks permission {permission.value}"
            self._log_access(user, permission, resource_id, "denied", reason)
            raise AccessDeniedError(reason)
    
    def can_access_resource(
        self,
        user: Dict[str, Any],
        resource_id: str,
        operation: Permission
    ) -> bool:
        """
        Check if user can access specific resource.
        
        Args:
            user: User dictionary
            resource_id: Resource identifier
            operation: Operation to perform
            
        Returns:
            True if access allowed
        """
        try:
            self.check_permission(user, operation, resource_id)
            return True
        except AccessDeniedError:
            return False
    
    def _log_access(
        self,
        user: Dict[str, Any],
        permission: Permission,
        resource_id: Optional[str],
        result: str,
        reason: Optional[str] = None
    ):
        """Log access attempt to audit trail."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            user_id=user.get("user_id", "unknown"),
            role=user.get("role").role_name if user.get("role") else "unknown",
            permission=permission.value,
            resource_id=resource_id,
            result=result,
            reason=reason
        )
        
        with self._lock:
            self._audit_trail.append(entry)
    
    def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail entries.
        
        Args:
            user_id: Filter by user ID
            limit: Maximum entries to return
            
        Returns:
            List of audit entries
        """
        entries = self._audit_trail
        
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        
        # Sort by timestamp descending
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            entries = entries[:limit]
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "user_id": e.user_id,
                "role": e.role,
                "permission": e.permission,
                "resource_id": e.resource_id,
                "result": e.result,
                "reason": e.reason,
            }
            for e in entries
        ]
    
    def is_access_time_valid(self, user: Dict[str, Any]) -> bool:
        """
        Check if current time is within user's allowed access hours.
        
        Args:
            user: User dictionary with optional 'access_hours'
            
        Returns:
            True if access time is valid
        """
        access_hours = user.get("access_hours")
        if not access_hours:
            return True  # No restrictions
        
        current_hour = datetime.now().hour
        start = access_hours.get("start", 0)
        end = access_hours.get("end", 24)
        
        return start <= current_hour < end
    
    def is_ip_allowed(self, user: Dict[str, Any], ip_address: str) -> bool:
        """
        Check if IP address is whitelisted for user.
        
        Args:
            user: User dictionary with optional 'ip_whitelist'
            ip_address: IP address to check
            
        Returns:
            True if IP is allowed
        """
        ip_whitelist = user.get("ip_whitelist")
        if not ip_whitelist:
            return True  # No restrictions
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            for allowed in ip_whitelist:
                if "/" in allowed:
                    # CIDR notation
                    network = ipaddress.ip_network(allowed, strict=False)
                    if ip in network:
                        return True
                else:
                    # Single IP
                    if ip == ipaddress.ip_address(allowed):
                        return True
            
            return False
        except ValueError:
            return False
    
    def create_session(
        self,
        user: Dict[str, Any],
        ttl_minutes: int = 60
    ) -> str:
        """
        Create user session.
        
        Args:
            user: User dictionary
            ttl_minutes: Session time-to-live in minutes
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = Session(
            session_id=session_id,
            user=user,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            is_active=True
        )
        
        with self._lock:
            self._sessions[session_id] = session
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate session is active and not expired.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session is valid
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if not session.is_active:
            return False
        
        if datetime.utcnow() > session.expires_at:
            session.is_active = False
            return False
        
        return True
    
    def get_session_user(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user from session."""
        session = self._sessions.get(session_id)
        return session.user if session else None
    
    def revoke_access(self, user_id: str):
        """
        Revoke access for user.
        
        Args:
            user_id: User ID to revoke
        """
        with self._lock:
            self._revoked_users.add(user_id)
            
            # Invalidate all sessions for user
            for session in self._sessions.values():
                if session.user.get("user_id") == user_id:
                    session.is_active = False
    
    def grant_permission(
        self,
        requester: Dict[str, Any],
        target_user_id: str,
        permission: Permission
    ):
        """
        Grant permission to target user (requires CONFIGURE permission).
        
        Args:
            requester: User requesting the grant
            target_user_id: Target user ID
            permission: Permission to grant
            
        Raises:
            AccessDeniedError: If requester lacks CONFIGURE permission
        """
        self.check_permission(requester, Permission.CONFIGURE)
        
        # Implementation would update user permissions in database
        # For now, just validate requester has permission
    
    def cleanup_audit_trail(self, days: int = 30) -> int:
        """
        Remove audit entries older than specified days.
        
        Args:
            days: Keep entries from last N days
            
        Returns:
            Number of deleted entries
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with self._lock:
            before = len(self._audit_trail)
            self._audit_trail = [
                e for e in self._audit_trail
                if e.timestamp > cutoff
            ]
            after = len(self._audit_trail)
        
        return before - after
    
    def export_audit_trail(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export audit trail for compliance.
        
        Args:
            start_time: Start of export window
            end_time: End of export window (defaults to now)
            format: Export format ("json")
            
        Returns:
            Export data dictionary
        """
        if end_time is None:
            end_time = datetime.utcnow()
        
        entries = [
            e for e in self._audit_trail
            if start_time <= e.timestamp <= end_time
        ]
        
        return {
            "export_time": datetime.utcnow().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "entry_count": len(entries),
            "audit_entries": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "user_id": e.user_id,
                    "role": e.role,
                    "permission": e.permission,
                    "resource_id": e.resource_id,
                    "result": e.result,
                    "reason": e.reason,
                }
                for e in entries
            ]
        }
