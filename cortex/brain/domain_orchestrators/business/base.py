"""
AC-PHX-008-04/05: Business Domain Orchestrator Base Class

Base class for all business domain-specific orchestrators.
Provides common functionality for domain context management,
compliance checking, and reporting.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import uuid


class ComplianceFramework(Enum):
    """Industry compliance frameworks."""
    SOX = "SOX"           # Sarbanes-Oxley (Financial)
    PCI_DSS = "PCI-DSS"   # Payment Card Industry
    HIPAA = "HIPAA"       # Healthcare
    GDPR = "GDPR"         # Data protection
    SOC2 = "SOC2"         # Service Organization Control


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceCheckResult:
    """Result of a compliance check."""
    passed: bool
    framework: str
    details: str = ""
    violations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    level: str
    score: float = 0.0
    factors: List[str] = field(default_factory=list)
    requires_review: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DomainContext:
    """Context for domain operations."""
    domain: str
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BusinessDomainOrchestrator(ABC):
    """
    Abstract base class for business domain-specific orchestrators.
    
    Provides:
    - Domain context management
    - Compliance framework integration
    - Risk assessment capabilities
    - Audit trail integration
    - Reporting capabilities
    """
    
    def __init__(self) -> None:
        """Initialize business domain orchestrator."""
        self._audit_entries: List[Dict[str, Any]] = []
        self._context: Optional[DomainContext] = None
    
    # =========================================================================
    # Abstract Properties (must be implemented by subclasses)
    # =========================================================================
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Return the business domain name."""
        pass
    
    @property
    @abstractmethod
    def orchestrator_id(self) -> str:
        """Return unique orchestrator identifier."""
        pass
    
    @property
    @abstractmethod
    def compliance_requirements(self) -> List[str]:
        """Return list of compliance frameworks required."""
        pass
    
    @property
    @abstractmethod
    def supported_operations(self) -> List[str]:
        """Return list of supported operations."""
        pass
    
    @property
    def required_tier(self) -> int:
        """Return required governance tier. Default is 2 for business domains."""
        return 2
    
    # =========================================================================
    # Abstract Methods (must be implemented by subclasses)
    # =========================================================================
    
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate context for operation.
        
        Args:
            context: Operation context dictionary
            
        Returns:
            True if context is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute domain-specific operation.
        
        Args:
            context: Operation context dictionary
            
        Returns:
            Result dictionary with operation outcome
        """
        pass
    
    @abstractmethod
    def assess_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk for the given context.
        
        Args:
            context: Operation context dictionary
            
        Returns:
            Risk assessment result
        """
        pass
    
    @abstractmethod
    def generate_report(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate domain-specific report.
        
        Args:
            **kwargs: Report parameters
            
        Returns:
            Report data dictionary
        """
        pass
    
    # =========================================================================
    # Common Methods (inherited by all business domain orchestrators)
    # =========================================================================
    
    def check_compliance(
        self,
        context: Dict[str, Any],
        framework: Optional[str] = None
    ) -> ComplianceCheckResult:
        """
        Check compliance against specified framework.
        
        Args:
            context: Operation context
            framework: Specific framework to check (or all if None)
            
        Returns:
            ComplianceCheckResult with pass/fail status
        """
        frameworks_to_check = (
            [framework] if framework else self.compliance_requirements
        )
        
        violations = []
        
        # Check for suspicious flags (AML/KYC violations)
        suspicious_flags = context.get("suspicious_flags", [])
        if suspicious_flags:
            for flag in suspicious_flags:
                violations.append(f"AML: Suspicious activity detected - {flag}")
        
        for fw in frameworks_to_check:
            # Framework-specific checks
            if fw == "PCI-DSS":
                if "card_number" in context:
                    violations.append(f"{fw}: Raw card data not allowed")
            elif fw == "HIPAA":
                if not context.get("authorized_user"):
                    violations.append(f"{fw}: Missing authorization")
            elif fw == "SOX":
                if not context.get("audit_trail_enabled", True):
                    violations.append(f"{fw}: Audit trail required")
        
        return ComplianceCheckResult(
            passed=len(violations) == 0,
            framework=",".join(frameworks_to_check),
            violations=violations,
        )
    
    def log_audit_entry(
        self,
        operation: str,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> str:
        """
        Log an audit trail entry.
        
        Args:
            operation: Operation performed
            context: Operation context
            result: Operation result
            
        Returns:
            Audit entry ID
        """
        audit_id = str(uuid.uuid4())
        entry = {
            "audit_id": audit_id,
            "domain": self.domain,
            "orchestrator_id": self.orchestrator_id,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "context_hash": hash(str(sorted(context.items()))),
            "result_status": result.get("status", "unknown"),
        }
        self._audit_entries.append(entry)
        return audit_id
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Return all audit entries for this orchestrator instance."""
        return self._audit_entries.copy()
    
    def _create_base_result(
        self,
        status: str,
        context: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create base result dictionary with common fields.
        
        Args:
            status: Operation status
            context: Operation context
            **kwargs: Additional result fields
            
        Returns:
            Result dictionary
        """
        result = {
            "status": status,
            "domain": self.domain,
            "orchestrator_id": self.orchestrator_id,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }
        
        # Add audit entry
        audit_id = self.log_audit_entry(
            operation=context.get("operation", "unknown"),
            context=context,
            result=result,
        )
        result["audit_id"] = audit_id
        
        return result
