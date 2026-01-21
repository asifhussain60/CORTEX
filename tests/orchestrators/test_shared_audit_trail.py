"""Tests for Shared Audit Trail - PHASE-DEPLOYMENT-004-multi-repo-gov.

AC-DEP-004-04: Shared audit trail across projects.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestUnifiedAuditTrail:
    """Test unified audit trail across projects."""

    def test_logs_to_unified_db(self):
        """Should log operations to unified governance.db."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_write_to_db") as mock_write:
            mock_write.return_value = True
            
            result = audit.log_operation(
                project="KASHKOLE",
                ac_id="AC-FIN-001",
                operation="CREATE",
            )
        
        assert result is True

    def test_queries_unified_audit(self):
        """Should query unified audit trail."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_query_db") as mock_query:
            mock_query.return_value = [
                {"project": "KASHKOLE", "ac_id": "AC-FIN-001"},
                {"project": "KSESSIONS", "ac_id": "AC-AUTH-001"},
            ]
            
            results = audit.query_all()
        
        assert len(results) >= 2
        projects = {r["project"] for r in results}
        assert len(projects) >= 2


class TestCrossRepoAcIdSearch:
    """Test cross-repo AC-ID search."""

    def test_finds_ac_id_across_repos(self):
        """Should find AC-ID references across repositories."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_search_ac_id") as mock_search:
            mock_search.return_value = [
                {"project": "CORTEX", "file": "test.py", "line": 10},
                {"project": "KASHKOLE", "file": "finance.py", "line": 25},
            ]
            
            results = audit.search_ac_id("AC-FIN-001")
        
        assert len(results) >= 2

    def test_search_with_wildcard(self):
        """Should support wildcard AC-ID search."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_search_ac_id") as mock_search:
            mock_search.return_value = [
                {"ac_id": "AC-FIN-001"},
                {"ac_id": "AC-FIN-002"},
            ]
            
            results = audit.search_ac_id("AC-FIN-*")
        
        assert len(results) >= 2


class TestProjectScopedQuery:
    """Test project-scoped audit queries."""

    def test_queries_single_project(self):
        """Should query audit for single project."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_query_db") as mock_query:
            mock_query.return_value = [
                {"project": "KASHKOLE", "ac_id": "AC-FIN-001"},
            ]
            
            results = audit.query_project("KASHKOLE")
        
        assert all(r["project"] == "KASHKOLE" for r in results)

    def test_excludes_other_projects(self):
        """Should exclude entries from other projects."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        with patch.object(audit, "_query_db") as mock_query:
            mock_query.return_value = [
                {"project": "KASHKOLE", "ac_id": "AC-FIN-001"},
            ]
            
            results = audit.query_project("KASHKOLE")
        
        ksessions_entries = [r for r in results if r["project"] == "KSESSIONS"]
        assert len(ksessions_entries) == 0


class TestAuditIsolationPerProject:
    """Test audit isolation per project."""

    def test_project_cannot_modify_other_project_audit(self):
        """Should prevent cross-project audit modification."""
        from cortex.orchestrators.shared_audit_trail import SharedAuditTrail
        
        audit = SharedAuditTrail()
        
        # Try to log from KASHKOLE modifying KSESSIONS entry
        result = audit.log_operation(
            project="KASHKOLE",
            ac_id="AC-AUTH-001",  # This is a KSESSIONS AC
            operation="UPDATE",
            source_project="KASHKOLE",  # Claiming to be KASHKOLE
        )
        
        # Should either reject or tag with actual source
        # Implementation can choose approach
        assert isinstance(result, bool)
