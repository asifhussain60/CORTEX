"""MCP Tool Governance - Authorization and compliance model for MCP tools.

Implements tool access control, compliance validation, and audit tracking
for all MCP tool invocations. Each tool is categorized and governed by
specific authorization rules.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ToolCategory(str, Enum):
    """MCP tool categories."""
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"
    SECURITY = "security"  # Phase 8.2: Security analysis tools (ENH-050)


class AuthLevel(str, Enum):
    """Authorization levels for tool access."""
    PUBLIC = "public"           # Any caller
    AUTHENTICATED = "authenticated"  # Logged-in user
    PRIVILEGED = "privileged"   # Admin/system operations
    SYSTEM = "system"           # Internal CORTEX operations only


class ComplianceMode(str, Enum):
    """Tool compliance and audit modes."""
    STRICT = "strict"           # Full audit logging, slow
    NORMAL = "normal"           # Standard audit logging
    LIGHTWEIGHT = "lightweight" # Minimal logging, fast
    DISABLED = "disabled"       # No audit (internal only)


@dataclass
class ToolGovernancePolicy:
    """Governance policy for an MCP tool.

    Attributes:
        tool_id: Unique tool identifier
        tool_name: Human-readable tool name
        category: Tool category (governance/orchestration/knowledge/utility)
        auth_level: Required authorization level
        compliance_mode: Audit/logging mode
        allowed_roles: Roles authorized to call this tool (empty = based on auth_level)
        rate_limit: Max calls per minute (None = unlimited)
        timeout_seconds: Tool execution timeout
        requires_context: Whether tool requires execution context
        requires_audit_log: Whether to force audit logging
        description: Tool purpose and behavior
    """
    tool_id: str
    tool_name: str
    category: ToolCategory
    auth_level: AuthLevel = AuthLevel.PUBLIC
    compliance_mode: ComplianceMode = ComplianceMode.NORMAL
    allowed_roles: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    requires_context: bool = False
    requires_audit_log: bool = False
    description: str = ""


class ToolGovernanceManager:
    """Manages governance policies and compliance for all MCP tools.

    Provides:
    - Tool authorization checking
    - Rate limiting per tool
    - Audit trail management
    - Compliance validation
    - Category-based access control
    """

    def __init__(self):
        """Initialize governance manager."""
        self._policies: Dict[str, ToolGovernancePolicy] = {}
        self._call_counts: Dict[str, int] = {}  # Per-minute tracking
        self._last_reset: Dict[str, datetime] = {}

    def register_policy(self, policy: ToolGovernancePolicy) -> None:
        """Register governance policy for a tool.

        Args:
            policy: ToolGovernancePolicy for the tool

        Raises:
            ValueError: If policy already registered
        """
        if policy.tool_id in self._policies:
            raise ValueError(f"Policy for {policy.tool_id} already registered")
        self._policies[policy.tool_id] = policy
        self._call_counts[policy.tool_id] = 0
        self._last_reset[policy.tool_id] = datetime.now()

    def get_policy(self, tool_id: str) -> Optional[ToolGovernancePolicy]:
        """Get governance policy for a tool.

        Args:
            tool_id: Tool identifier

        Returns:
            ToolGovernancePolicy if registered, None otherwise
        """
        return self._policies.get(tool_id)

    def can_access(
        self,
        tool_id: str,
        user_role: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[bool, Optional[str]]:
        """Check if tool access is authorized.

        Args:
            tool_id: Tool identifier
            user_role: User's role (None = unauthenticated)
            context: Execution context

        Returns:
            Tuple of (authorized: bool, reason: str if denied)
        """
        policy = self.get_policy(tool_id)
        if not policy:
            return False, f"Tool {tool_id} has no governance policy"

        # Check authorization level
        if policy.auth_level == AuthLevel.SYSTEM and user_role != "system":
            return False, f"Tool {tool_id} requires SYSTEM authorization"

        if policy.auth_level == AuthLevel.PRIVILEGED and user_role not in ["admin", "system"]:
            return False, f"Tool {tool_id} requires PRIVILEGED authorization"

        if policy.auth_level == AuthLevel.AUTHENTICATED and not user_role:
            return False, f"Tool {tool_id} requires AUTHENTICATED user"

        # Check role-based access
        if policy.allowed_roles and user_role not in policy.allowed_roles:
            return False, f"User role {user_role} not in allowed_roles"

        # Check context requirement
        if policy.requires_context and not context:
            return False, f"Tool {tool_id} requires execution context"

        return True, None

    def check_rate_limit(self, tool_id: str) -> tuple[bool, Optional[str]]:
        """Check rate limit for tool.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (allowed: bool, reason: str if denied)
        """
        policy = self.get_policy(tool_id)
        if not policy or not policy.rate_limit:
            return True, None

        now = datetime.now()
        if (now - self._last_reset[tool_id]).total_seconds() > 60:
            self._call_counts[tool_id] = 0
            self._last_reset[tool_id] = now

        if self._call_counts[tool_id] >= policy.rate_limit:
            return False, f"Rate limit exceeded for {tool_id}"

        self._call_counts[tool_id] += 1
        return True, None

    def list_tools_by_category(self, category: ToolCategory) -> List[ToolGovernancePolicy]:
        """List all tools in a category.

        Args:
            category: Tool category to filter by

        Returns:
            List of policies matching category
        """
        return [p for p in self._policies.values() if p.category == category]

    def get_tools_for_role(self, user_role: str) -> List[ToolGovernancePolicy]:
        """Get tools accessible by a specific role.

        Args:
            user_role: User role to check

        Returns:
            List of accessible tools
        """
        accessible = []
        for policy in self._policies.values():
            if policy.auth_level == AuthLevel.PUBLIC:
                accessible.append(policy)
            elif policy.auth_level == AuthLevel.AUTHENTICATED and user_role:
                accessible.append(policy)
            elif policy.allowed_roles and user_role in policy.allowed_roles:
                accessible.append(policy)
            elif policy.auth_level == AuthLevel.PRIVILEGED and user_role in ["admin", "system"]:
                accessible.append(policy)
        return accessible


# Global governance manager instance
_governance_manager: Optional[ToolGovernanceManager] = None


def get_governance_manager() -> ToolGovernanceManager:
    """Get or create global governance manager.

    Returns:
        ToolGovernanceManager instance
    """
    global _governance_manager
    if _governance_manager is None:
        _governance_manager = ToolGovernanceManager()
    return _governance_manager
