"""
Tests for StandardsResolver - Company domain integration.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from cortex.common.standards_resolver import (
    StandardsResolver,
    StandardsSource,
    StandardsResult,
)


class TestStandardsResolverBasic:
    """Test basic StandardsResolver initialization and schema."""
    
    def test_resolver_initializes(self):
        """StandardsResolver initializes with default paths."""
        resolver = StandardsResolver()
        
        assert resolver is not None
        assert resolver.cache_size == 100
        assert resolver.cache_ttl == 3600
    
    def test_standards_source_enum(self):
        """StandardsSource enum defines priority levels."""
        assert StandardsSource.COMPANY.value == "company"
        assert StandardsSource.CORTEX.value == "cortex"
        assert StandardsSource.DEFAULTS.value == "defaults"
    
    def test_standards_result_dataclass(self):
        """StandardsResult captures content, source, and gaps."""
        result = StandardsResult(
            content={"key": "value"},
            source=StandardsSource.COMPANY,
            gaps=[],
        )
        
        assert result.content == {"key": "value"}
        assert result.source == StandardsSource.COMPANY
        assert result.gaps == []


class TestStandardsPriorityLoading:
    """Test priority-based standards loading (company → cortex → defaults)."""
    
    def test_loads_company_standards_first(self, tmp_path):
        """Should load from company/domains/ with highest priority."""
        # Setup directory structure
        company_dir = tmp_path / "company" / "domains" / "security"
        company_dir.mkdir(parents=True)
        (company_dir / "authentication.yaml").write_text("auth_pattern: oauth2")
        
        resolver = StandardsResolver(
            company_root=str(tmp_path / "company" / "domains"),
            cortex_root=str(tmp_path / "cortex"),
            defaults_root=str(tmp_path / "defaults"),
        )
        
        result = resolver.load_standards("security", "authentication")
        
        assert result.source == StandardsSource.COMPANY
        assert "auth_pattern" in result.content
        assert result.gaps == []
    
    def test_fallback_to_cortex_when_company_missing(self, tmp_path):
        """Should fallback to cortex/knowledge/ when company missing."""
        # Company missing, cortex exists
        cortex_dir = tmp_path / "cortex" / "knowledge" / "security"
        cortex_dir.mkdir(parents=True)
        (cortex_dir / "authentication.yaml").write_text("auth_pattern: jwt")
        
        resolver = StandardsResolver(
            company_root=str(tmp_path / "company"),
            cortex_root=str(tmp_path / "cortex" / "knowledge"),
            defaults_root=str(tmp_path / "defaults"),
        )
        
        result = resolver.load_standards("security", "authentication")
        
        assert result.source == StandardsSource.CORTEX
        assert "auth_pattern" in result.content
        assert len(result.gaps) == 1  # Gap logged
        assert "security/authentication" in result.gaps[0]
    
    def test_fallback_to_defaults_when_all_missing(self, tmp_path):
        """Should fallback to defaults when company and cortex missing."""
        # Only defaults exist
        defaults_dir = tmp_path / "defaults" / "security"
        defaults_dir.mkdir(parents=True)
        (defaults_dir / "authentication.yaml").write_text("auth_pattern: basic")
        
        resolver = StandardsResolver(
            company_root=str(tmp_path / "company"),
            cortex_root=str(tmp_path / "cortex"),
            defaults_root=str(tmp_path / "defaults"),
        )
        
        result = resolver.load_standards("security", "authentication")
        
        assert result.source == StandardsSource.DEFAULTS
        assert "auth_pattern" in result.content
        assert len(result.gaps) == 2  # Company + cortex gaps logged


class TestCaching:
    """Test LRU caching for performance."""
    
    def test_caching_reduces_file_reads(self, tmp_path):
        """Second request should use cache, not re-read file."""
        company_dir = tmp_path / "company" / "domains" / "security"
        company_dir.mkdir(parents=True)
        standards_file = company_dir / "authentication.yaml"
        standards_file.write_text("auth_pattern: oauth2")
        
        resolver = StandardsResolver(
            company_root=str(tmp_path / "company" / "domains"),
        )
        
        # First load
        result1 = resolver.load_standards("security", "authentication")
        
        # Modify file (should not affect cached result)
        standards_file.write_text("auth_pattern: saml")
        
        # Second load (from cache)
        result2 = resolver.load_standards("security", "authentication")
        
        assert result1.content == result2.content
        assert result1.content["auth_pattern"] == "oauth2"  # Original


class TestPhase28ProfileIntegration:
    """Test integration with Phase 28 repository profiles."""
    
    def test_uses_profile_for_company_path(self, tmp_path):
        """Should use profile.structure.company_domains_path."""
        # Mock profile
        mock_profile = Mock()
        mock_profile.structure.has_company_domains = True
        mock_profile.structure.company_domains_path = str(tmp_path / "custom_company")
        
        # Create standards in custom path
        company_dir = tmp_path / "custom_company" / "security"
        company_dir.mkdir(parents=True)
        (company_dir / "auth.yaml").write_text("pattern: custom")
        
        resolver = StandardsResolver()
        resolver.load_profile(mock_profile)
        
        result = resolver.load_standards("security", "auth")
        
        assert result.source == StandardsSource.COMPANY
        assert result.content["pattern"] == "custom"
    
    def test_graceful_degradation_no_profile(self):
        """Should work without profile (use defaults)."""
        resolver = StandardsResolver()
        
        # No profile loaded, should use default paths
        result = resolver.load_standards("security", "authentication")
        
        # Should not crash, may return defaults or gaps
        assert result is not None
