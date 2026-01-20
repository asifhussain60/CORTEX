"""
Tests for Compliance Marker

AC-NFR-003-03: Compliance markers in audit logs

Test scenarios:
- Marker creation
- Framework support
- Category assignment
- Requirement mapping
- Marker filtering
- Report generation
- Audit trail summary
"""

import pytest
from src.infrastructure.compliance_marker import (
    ComplianceFramework,
    ComplianceCategory,
    ComplianceMarker,
    ComplianceMarkerRegistry,
    ComplianceMarkerService,
)


class TestComplianceMarkerRegistry:
    """Test suite for ComplianceMarkerRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create registry."""
        return ComplianceMarkerRegistry()
    
    def test_get_requirement(self, registry):
        """Test getting requirement by ID."""
        req = registry.get_requirement("SOC2-CC6.1")
        assert req is not None
        assert req.requirement_id == "SOC2-CC6.1"
        assert req.framework == ComplianceFramework.SOC2
    
    def test_get_nonexistent_requirement(self, registry):
        """Test getting nonexistent requirement."""
        req = registry.get_requirement("NONEXISTENT")
        assert req is None
    
    def test_get_requirements_for_framework(self, registry):
        """Test getting all requirements for framework."""
        soc2_reqs = registry.get_requirements_for_framework(ComplianceFramework.SOC2)
        assert len(soc2_reqs) > 0
        assert all(r.framework == ComplianceFramework.SOC2 for r in soc2_reqs)
    
    def test_get_requirements_for_category(self, registry):
        """Test getting requirements for category."""
        audit_reqs = registry.get_requirements_for_category(ComplianceCategory.AUDIT_LOGGING)
        assert len(audit_reqs) > 0
        assert all(r.category == ComplianceCategory.AUDIT_LOGGING for r in audit_reqs)
    
    def test_get_requirements_for_operation_login(self, registry):
        """Test getting requirements for LOGIN operation."""
        reqs = registry.get_requirements_for_operation("LOGIN")
        assert len(reqs) > 0
        categories = set(r.category for r in reqs)
        assert ComplianceCategory.AUTHENTICATION in categories
        assert ComplianceCategory.AUDIT_LOGGING in categories
    
    def test_get_requirements_for_operation_secret_access(self, registry):
        """Test getting requirements for SECRET_ACCESS operation."""
        reqs = registry.get_requirements_for_operation("SECRET_ACCESS")
        assert len(reqs) > 0
        categories = set(r.category for r in reqs)
        assert ComplianceCategory.AUDIT_LOGGING in categories
        assert ComplianceCategory.DATA_PROTECTION in categories


class TestComplianceMarkerService:
    """Test suite for ComplianceMarkerService."""
    
    @pytest.fixture
    def service(self):
        """Create service."""
        return ComplianceMarkerService()
    
    def test_create_marker_basic(self, service):
        """Test basic marker creation."""
        marker = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            user_id="user123",
        )
        
        assert marker.id == "marker-001"
        assert marker.operation == "LOGIN"
        assert marker.user_id == "user123"
        assert len(marker.frameworks) > 0
        assert len(marker.categories) > 0
    
    def test_create_marker_specific_frameworks(self, service):
        """Test marker creation with specific frameworks."""
        frameworks = [ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
        marker = service.create_marker(
            marker_id="marker-002",
            operation="LOGIN",
            frameworks=frameworks,
        )
        
        assert ComplianceFramework.SOC2 in marker.frameworks
        assert ComplianceFramework.ISO27001 in marker.frameworks
    
    def test_create_marker_with_result(self, service):
        """Test marker creation with success result."""
        marker = service.create_marker(
            marker_id="marker-003",
            operation="LOGIN",
            result="SUCCESS",
        )
        
        assert marker.result == "SUCCESS"
    
    def test_create_marker_with_evidence(self, service):
        """Test marker creation with evidence references."""
        evidence = ["evidence-001", "evidence-002"]
        marker = service.create_marker(
            marker_id="marker-004",
            operation="LOGIN",
            evidence_refs=evidence,
        )
        
        assert marker.evidence_refs == evidence
    
    def test_create_audit_marker(self, service):
        """Test creating audit-specific marker."""
        marker = service.create_audit_marker(
            marker_id="audit-001",
            operation="LOGIN",
            user_id="user123",
            result="SUCCESS",
        )
        
        assert ComplianceCategory.AUDIT_LOGGING in marker.categories
        assert marker.user_id == "user123"
        assert marker.result == "SUCCESS"
    
    def test_marker_to_dict(self, service):
        """Test marker serialization."""
        marker = service.create_marker(
            marker_id="marker-005",
            operation="LOGIN",
            user_id="user123",
        )
        
        marker_dict = marker.to_dict()
        assert marker_dict['id'] == "marker-005"
        assert marker_dict['operation'] == "LOGIN"
        assert marker_dict['user_id'] == "user123"
        assert 'frameworks' in marker_dict
        assert 'categories' in marker_dict
    
    def test_get_markers_by_framework(self, service):
        """Test filtering markers by framework."""
        marker1 = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            frameworks=[ComplianceFramework.SOC2],
        )
        marker2 = service.create_marker(
            marker_id="marker-002",
            operation="LOGIN",
            frameworks=[ComplianceFramework.ISO27001],
        )
        
        markers = [marker1, marker2]
        soc2_markers = service.get_markers_by_framework(markers, ComplianceFramework.SOC2)
        
        assert len(soc2_markers) == 1
        assert soc2_markers[0].id == "marker-001"
    
    def test_get_markers_by_category(self, service):
        """Test filtering markers by category."""
        marker1 = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
        )
        marker2 = service.create_marker(
            marker_id="marker-002",
            operation="DATA_EXPORT",
        )
        
        markers = [marker1, marker2]
        auth_markers = service.get_markers_by_category(markers, ComplianceCategory.AUTHENTICATION)
        
        # LOGIN includes AUTHENTICATION
        assert len(auth_markers) >= 1
    
    def test_get_markers_by_user(self, service):
        """Test filtering markers by user."""
        marker1 = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            user_id="user123",
        )
        marker2 = service.create_marker(
            marker_id="marker-002",
            operation="LOGIN",
            user_id="user456",
        )
        
        markers = [marker1, marker2]
        user_markers = service.get_markers_by_user(markers, "user123")
        
        assert len(user_markers) == 1
        assert user_markers[0].user_id == "user123"
    
    def test_generate_compliance_report(self, service):
        """Test compliance report generation."""
        marker1 = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            frameworks=[ComplianceFramework.SOC2],
        )
        marker2 = service.create_marker(
            marker_id="marker-002",
            operation="LOGIN",
            frameworks=[ComplianceFramework.SOC2],
        )
        
        markers = [marker1, marker2]
        report = service.generate_compliance_report(markers, ComplianceFramework.SOC2)
        
        assert report['framework'] == "SOC2"
        assert report['total_markers'] >= 2
        assert 'coverage' in report
    
    def test_generate_audit_trail_summary(self, service):
        """Test audit trail summary generation."""
        marker1 = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            result="SUCCESS",
        )
        marker2 = service.create_marker(
            marker_id="marker-002",
            operation="LOGIN",
            result="FAILURE",
        )
        
        markers = [marker1, marker2]
        summary = service.generate_audit_trail_summary(markers)
        
        assert summary['total_events'] == 2
        assert summary['successful_operations'] == 1
        assert summary['failed_operations'] == 1
        assert 'LOGIN' in summary['operations']
    
    def test_marker_categories_auto_assigned(self, service):
        """Test that categories are auto-assigned based on operation."""
        marker = service.create_marker(
            marker_id="marker-001",
            operation="PERMISSION_CHANGE",
        )
        
        assert len(marker.categories) > 0
        assert ComplianceCategory.CHANGE_MANAGEMENT in marker.categories
    
    def test_marker_requirements_auto_assigned(self, service):
        """Test that requirements are auto-assigned."""
        marker = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            frameworks=[ComplianceFramework.SOC2],
        )
        
        assert len(marker.requirements) > 0
    
    def test_multiple_frameworks_coverage(self, service):
        """Test marker covering multiple frameworks."""
        frameworks = [
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
            ComplianceFramework.GDPR,
        ]
        marker = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            frameworks=frameworks,
        )
        
        assert all(f in marker.frameworks for f in frameworks)
    
    def test_marker_metadata(self, service):
        """Test marker with custom metadata."""
        metadata = {
            'ip_address': '192.168.1.1',
            'session_id': 'session-123',
            'client': 'web-app',
        }
        marker = service.create_marker(
            marker_id="marker-001",
            operation="LOGIN",
            metadata=metadata,
        )
        
        assert marker.metadata == metadata
    
    def test_create_marker_all_fields(self, service):
        """Test marker creation with all fields."""
        marker = service.create_marker(
            marker_id="marker-001",
            operation="SECRET_ACCESS",
            frameworks=[ComplianceFramework.SOC2, ComplianceFramework.HIPAA],
            user_id="user123",
            resource_id="resource-456",
            action="accessed_api_key",
            result="SUCCESS",
            evidence_refs=["evidence-001"],
            metadata={'ip': '192.168.1.1'},
        )
        
        assert marker.id == "marker-001"
        assert marker.user_id == "user123"
        assert marker.resource_id == "resource-456"
        assert marker.action == "accessed_api_key"
        assert marker.result == "SUCCESS"
        assert len(marker.evidence_refs) == 1
        assert marker.metadata['ip'] == '192.168.1.1'
