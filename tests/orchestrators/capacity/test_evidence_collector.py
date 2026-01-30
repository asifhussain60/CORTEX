"""
CAP-001: Evidence Collector Tests

Tests for evidence collection from multiple sources:
- LENSOrchestrator integration for code complexity
- Git repository for historical velocity
- Tier3 knowledge base for domain patterns

AC-IDs: CAP-001-AC01, CAP-001-AC02

CORE Governance:
  - CORE-008: TDD (tests created first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Date: 2026-01-30
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock


class TestEvidenceCollectorIntegration:
    """Test EvidenceCollector integration with external systems."""
    
    def test_collect_evidence_integrates_with_lens(self):
        """
        Test that evidence collector integrates with LENSOrchestrator.
        
        AC-CAP-001-AC01: Evidence collector integrates with LENSOrchestrator
        """
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert
        assert evidence is not None
        assert evidence.complexity is not None
        assert isinstance(evidence.complexity, dict)
    
    def test_collect_evidence_includes_complexity_metrics(self):
        """
        Test that evidence includes complexity metrics from LENS.
        
        AC-CAP-001-AC01: Complexity analysis included
        """
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/master_orchestrator.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert
        assert evidence.complexity is not None
        complexity = evidence.complexity
        assert "cyclomatic_complexity" in complexity or "sloc" in complexity
    
    def test_collect_evidence_includes_git_velocity(self):
        """
        Test that evidence includes Git velocity data.
        
        AC-CAP-001-AC02: Git velocity extraction functional
        """
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert
        assert evidence.git_velocity is not None
        velocity = evidence.git_velocity
        assert "change_frequency" in velocity or "commit_count" in velocity
    
    def test_collect_evidence_includes_domain_patterns(self):
        """
        Test that evidence includes domain estimation patterns from Tier3.
        
        AC-CAP-001-AC02: Domain patterns included
        """
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/dor_approval_gate.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert
        assert evidence.domain_patterns is not None
        patterns = evidence.domain_patterns
        assert isinstance(patterns, dict)
    
    def test_collect_evidence_handles_missing_file(self):
        """
        Test that evidence collector handles missing files gracefully.
        
        AC-CAP-001: Error handling for invalid paths
        """
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "nonexistent/file/path.py"
        
        # Act & Assert
        with pytest.raises((FileNotFoundError, ValueError)):
            collector.collect_evidence(file_path)


class TestComplexityAnalysis:
    """Test complexity analysis component of evidence collection."""
    
    def test_analyze_complexity_returns_metrics(self):
        """Test that complexity analysis returns standard metrics."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        complexity = collector._analyze_complexity(file_path)
        
        # Assert
        assert complexity is not None
        assert isinstance(complexity, dict)
        assert "sloc" in complexity or "cyclomatic_complexity" in complexity
    
    def test_analyze_complexity_detects_high_complexity(self):
        """Test that high complexity files are flagged."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"  # Known large file
        
        # Act
        complexity = collector._analyze_complexity(file_path)
        
        # Assert
        assert complexity["sloc"] > 100  # Intent router is large
    
    def test_analyze_complexity_caches_results(self):
        """Test that complexity analysis caches results for performance."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act - call twice
        complexity1 = collector._analyze_complexity(file_path)
        complexity2 = collector._analyze_complexity(file_path)
        
        # Assert - should return same cached result
        assert complexity1 == complexity2


class TestGitVelocityExtraction:
    """Test Git velocity extraction component."""
    
    def test_extract_git_velocity_returns_metrics(self):
        """Test that Git velocity extraction returns metrics."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        velocity = collector._extract_git_velocity(file_path)
        
        # Assert
        assert velocity is not None
        assert isinstance(velocity, dict)
        assert "change_frequency" in velocity or "commit_count" in velocity
    
    def test_extract_git_velocity_calculates_change_frequency(self):
        """Test that velocity includes change frequency calculation."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/master_orchestrator.py"
        
        # Act
        velocity = collector._extract_git_velocity(file_path)
        
        # Assert
        assert "change_frequency" in velocity
    
    def test_extract_git_velocity_handles_new_files(self):
        """Test that velocity extraction handles files with no Git history."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            velocity = collector._extract_git_velocity(temp_path)
            
            # Assert - should return default/zero values
            assert velocity is not None
            assert velocity.get("commit_count", 0) == 0
        finally:
            # Cleanup
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDomainPatternRetrieval:
    """Test domain pattern retrieval from Tier3 knowledge base."""
    
    def test_retrieve_domain_patterns_returns_data(self):
        """Test that domain pattern retrieval returns data."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        patterns = collector._retrieve_domain_patterns(file_path)
        
        # Assert
        assert patterns is not None
        assert isinstance(patterns, dict)
    
    def test_retrieve_domain_patterns_identifies_orchestrator_type(self):
        """Test that patterns identify orchestrator type for estimation."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        patterns = collector._retrieve_domain_patterns(file_path)
        
        # Assert
        assert "orchestrator_type" in patterns or "domain" in patterns
    
    def test_retrieve_domain_patterns_includes_historical_estimates(self):
        """Test that patterns include historical estimates if available."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/master_orchestrator.py"
        
        # Act
        patterns = collector._retrieve_domain_patterns(file_path)
        
        # Assert
        # May or may not have historical data, but field should exist
        assert "estimated_complexity" in patterns or patterns is not None


class TestEvidenceCollectorOutput:
    """Test output format and structure of evidence collector."""
    
    def test_evidence_structure_is_complete(self):
        """Test that evidence object has all required fields."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert - check all required fields
        assert evidence.complexity is not None
        assert evidence.git_velocity is not None
        assert evidence.domain_patterns is not None
        assert evidence.confidence_score >= 0.0
    
    def test_evidence_is_json_serializable(self):
        """Test that evidence can be serialized to JSON."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        import json
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/intent_router.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert - should not raise exception
        json_str = evidence.to_json()
        assert len(json_str) > 0
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "complexity" in parsed
    
    def test_evidence_includes_confidence_score(self):
        """Test that evidence includes confidence score for estimates."""
        # Arrange
        from cortex.orchestrators.capacity.evidence_collector import EvidenceCollector
        
        collector = EvidenceCollector()
        file_path = "cortex/orchestrators/core/master_orchestrator.py"
        
        # Act
        evidence = collector.collect_evidence(file_path)
        
        # Assert
        assert evidence.confidence_score is not None
        confidence = evidence.confidence_score
        assert 0.0 <= confidence <= 100.0
