"""
Compliance Marker - Audit Log Compliance Annotations

Production-grade compliance marker system with:
- Compliance framework support (SOC2, ISO27001, HIPAA, GDPR, PCI-DSS)
- Automatic compliance classification
- Evidence capture and correlation
- Audit trail integration
- Report generation

Satisfies: NFR-003-03 - Compliance Markers in Audit Logs

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from cortex.brain.core.result import Err, Ok, Result


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    PCI_DSS = "PCI-DSS"
    ALL = "ALL"


class ComplianceCategory(str, Enum):
    """Compliance categories for operations."""
    
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    DATA_PROTECTION = "DATA_PROTECTION"
    ENCRYPTION = "ENCRYPTION"
    AUDIT_LOGGING = "AUDIT_LOGGING"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    DATA_RETENTION = "DATA_RETENTION"
    USER_PRIVACY = "USER_PRIVACY"
    SYSTEM_AVAILABILITY = "SYSTEM_AVAILABILITY"
    CHANGE_MANAGEMENT = "CHANGE_MANAGEMENT"
    VENDOR_MANAGEMENT = "VENDOR_MANAGEMENT"


@dataclass
class ComplianceRequirement:
    """Single compliance requirement."""
    
    framework: ComplianceFramework
    requirement_id: str  # e.g., "SOC2-CC6.1", "ISO27001-A.9.1"
    description: str
    category: ComplianceCategory
    
    def __hash__(self):
        return hash((self.framework, self.requirement_id))


@dataclass
class ComplianceMarker:
    """Marker for compliance-relevant operation."""
    
    id: str
    timestamp: str
    operation: str  # e.g., "LOGIN", "SECRET_ACCESS", "DATA_EXPORT"
    frameworks: Set[ComplianceFramework] = field(default_factory=set)
    categories: Set[ComplianceCategory] = field(default_factory=set)
    requirements: Set[str] = field(default_factory=set)  # Requirement IDs like "SOC2-CC6.1"
    evidence_refs: List[str] = field(default_factory=list)  # References to evidence bundles
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None  # "SUCCESS" or "FAILURE"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'operation': self.operation,
            'frameworks': list(f.value for f in self.frameworks),
            'categories': list(c.value for c in self.categories),
            'requirements': list(self.requirements),
            'evidence_refs': self.evidence_refs,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'action': self.action,
            'result': self.result,
            'metadata': self.metadata,
        }


class ComplianceMarkerRegistry:
    """Registry of compliance requirements by framework and category."""
    
    def __init__(self):
        """Initialize compliance registry."""
        self._requirements: Dict[str, ComplianceRequirement] = {}
        self._init_requirements()
    
    def _init_requirements(self):
        """Initialize standard compliance requirements."""
        
        # SOC2 Requirements
        soc2_requirements = [
            ComplianceRequirement(
                ComplianceFramework.SOC2,
                "SOC2-CC6.1",
                "User access logging",
                ComplianceCategory.AUDIT_LOGGING,
            ),
            ComplianceRequirement(
                ComplianceFramework.SOC2,
                "SOC2-CC6.2",
                "System access logging",
                ComplianceCategory.ACCESS_CONTROL,
            ),
            ComplianceRequirement(
                ComplianceFramework.SOC2,
                "SOC2-CC9.2",
                "Authentication controls",
                ComplianceCategory.AUTHENTICATION,
            ),
            ComplianceRequirement(
                ComplianceFramework.SOC2,
                "SOC2-CC7.2",
                "Change management",
                ComplianceCategory.CHANGE_MANAGEMENT,
            ),
        ]
        
        # ISO 27001 Requirements
        iso_requirements = [
            ComplianceRequirement(
                ComplianceFramework.ISO27001,
                "ISO27001-A.9.1",
                "Access control policy",
                ComplianceCategory.ACCESS_CONTROL,
            ),
            ComplianceRequirement(
                ComplianceFramework.ISO27001,
                "ISO27001-A.12.4.1",
                "Audit logging and monitoring",
                ComplianceCategory.AUDIT_LOGGING,
            ),
            ComplianceRequirement(
                ComplianceFramework.ISO27001,
                "ISO27001-A.14.2.1",
                "Change management",
                ComplianceCategory.CHANGE_MANAGEMENT,
            ),
        ]
        
        # GDPR Requirements
        gdpr_requirements = [
            ComplianceRequirement(
                ComplianceFramework.GDPR,
                "GDPR-5.1",
                "Data processing principles",
                ComplianceCategory.USER_PRIVACY,
            ),
            ComplianceRequirement(
                ComplianceFramework.GDPR,
                "GDPR-32",
                "Security of processing",
                ComplianceCategory.DATA_PROTECTION,
            ),
        ]
        
        # HIPAA Requirements
        hipaa_requirements = [
            ComplianceRequirement(
                ComplianceFramework.HIPAA,
                "HIPAA-164.312(b)",
                "Audit controls",
                ComplianceCategory.AUDIT_LOGGING,
            ),
            ComplianceRequirement(
                ComplianceFramework.HIPAA,
                "HIPAA-164.312(a)(2)(i)",
                "Encryption and decryption",
                ComplianceCategory.ENCRYPTION,
            ),
        ]
        
        # PCI-DSS Requirements
        pci_requirements = [
            ComplianceRequirement(
                ComplianceFramework.PCI_DSS,
                "PCI-DSS-10.1",
                "Implement user identification",
                ComplianceCategory.AUTHENTICATION,
            ),
            ComplianceRequirement(
                ComplianceFramework.PCI_DSS,
                "PCI-DSS-10.2",
                "Implement automated audit trails",
                ComplianceCategory.AUDIT_LOGGING,
            ),
            ComplianceRequirement(
                ComplianceFramework.PCI_DSS,
                "PCI-DSS-6.5.1",
                "Change management",
                ComplianceCategory.CHANGE_MANAGEMENT,
            ),
        ]
        
        for req in soc2_requirements + iso_requirements + gdpr_requirements + hipaa_requirements + pci_requirements:
            self._requirements[req.requirement_id] = req
    
    def get_requirement(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """Get requirement by ID."""
        return self._requirements.get(requirement_id)
    
    def get_requirements_for_framework(self, framework: ComplianceFramework) -> List[ComplianceRequirement]:
        """Get all requirements for a framework."""
        return [
            req for req in self._requirements.values()
            if req.framework == framework
        ]
    
    def get_requirements_for_category(self, category: ComplianceCategory) -> List[ComplianceRequirement]:
        """Get all requirements for a category."""
        return [
            req for req in self._requirements.values()
            if req.category == category
        ]
    
    def get_requirements_for_operation(self, operation: str) -> List[ComplianceRequirement]:
        """Get applicable requirements for an operation."""
        operation_upper = operation.upper()
        
        # Map operations to categories
        operation_categories = {
            "LOGIN": [ComplianceCategory.AUTHENTICATION, ComplianceCategory.AUDIT_LOGGING],
            "LOGOUT": [ComplianceCategory.AUDIT_LOGGING],
            "SECRET_ACCESS": [ComplianceCategory.AUDIT_LOGGING, ComplianceCategory.DATA_PROTECTION],
            "DATA_EXPORT": [ComplianceCategory.DATA_RETENTION, ComplianceCategory.USER_PRIVACY],
            "PERMISSION_CHANGE": [ComplianceCategory.CHANGE_MANAGEMENT, ComplianceCategory.AUDIT_LOGGING],
            "ENCRYPTION": [ComplianceCategory.ENCRYPTION, ComplianceCategory.DATA_PROTECTION],
            "CONFIG_CHANGE": [ComplianceCategory.CHANGE_MANAGEMENT, ComplianceCategory.AUDIT_LOGGING],
        }
        
        categories = operation_categories.get(operation_upper, [])
        requirements = []
        for category in categories:
            requirements.extend(self.get_requirements_for_category(category))
        
        return requirements


class ComplianceMarkerService:
    """Service for creating and managing compliance markers."""
    
    def __init__(self):
        """Initialize compliance marker service."""
        self.registry = ComplianceMarkerRegistry()
    
    def create_marker(
        self,
        marker_id: str,
        operation: str,
        frameworks: Optional[List[ComplianceFramework]] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        evidence_refs: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ComplianceMarker:
        """
        Create a compliance marker.
        
        Args:
            marker_id: Unique identifier for marker
            operation: Type of operation (e.g., "LOGIN")
            frameworks: List of applicable compliance frameworks
            user_id: User performing operation
            resource_id: Resource affected by operation
            action: Detailed action performed
            result: Result of operation ("SUCCESS" or "FAILURE")
            evidence_refs: References to evidence bundles
            metadata: Additional metadata
            
        Returns:
            ComplianceMarker instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Default to all frameworks if not specified
        marker_frameworks = set(frameworks) if frameworks else set(ComplianceFramework)
        
        # Auto-detect requirements based on operation
        requirements = set()
        auto_requirements = self.registry.get_requirements_for_operation(operation)
        for req in auto_requirements:
            if req.framework in marker_frameworks:
                requirements.add(req.requirement_id)
        
        # Extract categories from requirements
        categories = set()
        for req_id in requirements:
            req = self.registry.get_requirement(req_id)
            if req:
                categories.add(req.category)
        
        return ComplianceMarker(
            id=marker_id,
            timestamp=timestamp,
            operation=operation,
            frameworks=marker_frameworks,
            categories=categories,
            requirements=requirements,
            evidence_refs=evidence_refs or [],
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            result=result,
            metadata=metadata or {},
        )
    
    def create_marker_for_frameworks(
        self,
        marker_id: str,
        operation: str,
        frameworks: List[ComplianceFramework],
        **kwargs
    ) -> ComplianceMarker:
        """
        Create marker for specific frameworks.
        
        Args:
            marker_id: Unique identifier
            operation: Operation type
            frameworks: List of frameworks to apply
            **kwargs: Additional arguments for create_marker
            
        Returns:
            ComplianceMarker instance
        """
        return self.create_marker(marker_id, operation, frameworks, **kwargs)
    
    def create_audit_marker(
        self,
        marker_id: str,
        operation: str,
        user_id: Optional[str] = None,
        result: Optional[str] = None,
    ) -> ComplianceMarker:
        """
        Create marker for audit logging requirement.
        
        Args:
            marker_id: Unique identifier
            operation: Operation type
            user_id: User performing operation
            result: Result of operation
            
        Returns:
            ComplianceMarker instance
        """
        marker = self.create_marker(
            marker_id=marker_id,
            operation=operation,
            user_id=user_id,
            result=result,
        )
        # Ensure audit logging category is present
        marker.categories.add(ComplianceCategory.AUDIT_LOGGING)
        return marker
    
    def get_markers_by_framework(
        self,
        markers: List[ComplianceMarker],
        framework: ComplianceFramework,
    ) -> List[ComplianceMarker]:
        """
        Filter markers by compliance framework.
        
        Args:
            markers: List of markers
            framework: Framework to filter by
            
        Returns:
            Filtered list of markers
        """
        return [m for m in markers if framework in m.frameworks]
    
    def get_markers_by_category(
        self,
        markers: List[ComplianceMarker],
        category: ComplianceCategory,
    ) -> List[ComplianceMarker]:
        """
        Filter markers by compliance category.
        
        Args:
            markers: List of markers
            category: Category to filter by
            
        Returns:
            Filtered list of markers
        """
        return [m for m in markers if category in m.categories]
    
    def get_markers_by_user(
        self,
        markers: List[ComplianceMarker],
        user_id: str,
    ) -> List[ComplianceMarker]:
        """
        Filter markers by user ID.
        
        Args:
            markers: List of markers
            user_id: User to filter by
            
        Returns:
            Filtered list of markers
        """
        return [m for m in markers if m.user_id == user_id]
    
    def generate_compliance_report(
        self,
        markers: List[ComplianceMarker],
        framework: ComplianceFramework,
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a framework.
        
        Args:
            markers: List of markers
            framework: Framework to report on
            
        Returns:
            Report dictionary
        """
        framework_markers = self.get_markers_by_framework(markers, framework)
        
        # Collect requirements and their coverage
        requirements = self.registry.get_requirements_for_framework(framework)
        requirement_coverage = {}
        
        for req in requirements:
            matching_markers = [
                m for m in framework_markers
                if req.requirement_id in m.requirements
            ]
            requirement_coverage[req.requirement_id] = {
                'requirement': req.description,
                'category': req.category.value,
                'marker_count': len(matching_markers),
                'last_occurrence': matching_markers[-1].timestamp if matching_markers else None,
            }
        
        return {
            'framework': framework.value,
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'total_markers': len(framework_markers),
            'total_requirements': len(requirements),
            'coverage': requirement_coverage,
        }
    
    def generate_audit_trail_summary(
        self,
        markers: List[ComplianceMarker],
    ) -> Dict[str, Any]:
        """
        Generate audit trail summary.
        
        Args:
            markers: List of markers
            
        Returns:
            Summary dictionary
        """
        return {
            'total_events': len(markers),
            'frameworks_covered': list(set(
                f.value for m in markers for f in m.frameworks
            )),
            'categories_covered': list(set(
                c.value for m in markers for c in m.categories
            )),
            'operations': list(set(m.operation for m in markers)),
            'successful_operations': len([m for m in markers if m.result == "SUCCESS"]),
            'failed_operations': len([m for m in markers if m.result == "FAILURE"]),
            'first_event': min((m.timestamp for m in markers), default=None),
            'last_event': max((m.timestamp for m in markers), default=None),
        }
