"""
Tests for CORTEX Header Template Generator.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime

from src.operations.modules.templates.cortex_header import (
    generate_cortex_header,
    generate_sub_plan_header,
    generate_report_header,
    generate_ado_header,
    extract_document_title,
    has_cortex_header,
    inject_cortex_header,
    CORTEX_ASCII_LOGO
)


class TestCortexHeaderGeneration:
    """Test suite for CORTEX header generation."""
    
    def test_cortex_ascii_logo(self):
        """Test CORTEX ASCII logo constant."""
        assert '██████╗' in CORTEX_ASCII_LOGO
        assert 'CORTEX' in CORTEX_ASCII_LOGO
        assert 'AI-Powered Development Intelligence System' in CORTEX_ASCII_LOGO
        assert 'Asif Hussain' in CORTEX_ASCII_LOGO
        assert 'Copyright © 2025' in CORTEX_ASCII_LOGO
        
    def test_generate_cortex_header_basic(self):
        """Test basic CORTEX header generation."""
        header = generate_cortex_header(
            document_title="Test Document",
            document_type="Test Plan",
            status="✅ Complete",
            version="1.0.0"
        )
        
        assert '██████╗' in header
        assert '# Test Document' in header
        assert '**Type:** Test Plan' in header
        assert '**Status:** ✅ Complete' in header
        assert '**Version:** 1.0.0' in header
        assert '**Created:**' in header
        
    def test_generate_cortex_header_minimal(self):
        """Test CORTEX header with minimal parameters."""
        header = generate_cortex_header(
            document_title="Minimal Doc",
            document_type="Document"
        )
        
        assert '# Minimal Doc' in header
        assert '**Type:** Document' in header
        assert '**Status:** 🟡 In Progress' in header  # Default status
        assert '**Version:**' not in header  # No version specified
        
    def test_generate_cortex_header_with_metadata(self):
        """Test CORTEX header with additional metadata."""
        header = generate_cortex_header(
            document_title="Complex Document",
            document_type="Master Plan",
            status="🟡 In Progress",
            version="3.9.0",
            additional_metadata={
                'Plan Name': 'CORTEX Evolution v3.9',
                'Complexity': 'Tier 4'
            }
        )
        
        assert '**Plan Name:** CORTEX Evolution v3.9' in header
        assert '**Complexity:** Tier 4' in header
        
    def test_generate_sub_plan_header_basic(self):
        """Test sub-plan header generation."""
        header = generate_sub_plan_header(
            phase_id="04",
            phase_name="ADO Orchestrator 3.0",
            master_plan_path="cortex-3.9-master.md",
            status="✅ Complete",
            version="3.0.0"
        )
        
        assert '██████╗' in header
        assert '# ADO Orchestrator 3.0' in header
        assert '**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)' in header
        assert '**Status:** ✅ Complete' in header
        assert '**Phase ID:** 04' in header
        assert '**Version:** 3.0.0' in header
        
    def test_generate_sub_plan_header_minimal(self):
        """Test sub-plan header with minimal parameters."""
        header = generate_sub_plan_header(
            phase_id="01",
            phase_name="Test Phase",
            master_plan_path="master.md"
        )
        
        assert '# Test Phase' in header
        assert '**Phase ID:** 01' in header
        assert '**Status:** ⏳ Pending' in header  # Default status
        assert '**Version:**' not in header
        
    def test_generate_report_header_basic(self):
        """Test report header generation."""
        header = generate_report_header(
            report_title="Code Quality Analysis",
            report_type="Analysis Report",
            project_name="CORTEX"
        )
        
        assert '██████╗' in header
        assert '# Code Quality Analysis' in header
        assert '**Type:** Analysis Report' in header
        assert '**Project:** CORTEX' in header
        assert '**Generated:**' in header
        
    def test_generate_report_header_minimal(self):
        """Test report header without project name."""
        header = generate_report_header(
            report_title="Summary Report",
            report_type="Summary"
        )
        
        assert '# Summary Report' in header
        assert '**Type:** Summary' in header
        assert '**Project:**' not in header
        
    def test_generate_ado_header_basic(self):
        """Test ADO header generation."""
        header = generate_ado_header(
            feature_title="User Authentication Feature",
            feature_type="Feature",
            priority="High",
            area_path="CORTEX\\Security"
        )
        
        assert '██████╗' in header
        assert '# User Authentication Feature' in header
        assert '**Type:** Feature' in header
        assert '**Priority:** High' in header
        assert '**Area Path:** CORTEX\\Security' in header
        
    def test_generate_ado_header_defaults(self):
        """Test ADO header with default values."""
        header = generate_ado_header(
            feature_title="Test Feature"
        )
        
        assert '# Test Feature' in header
        assert '**Type:** Feature' in header  # Default type
        assert '**Priority:** Medium' in header  # Default priority
        assert '**Area Path:**' not in header
        
    def test_extract_document_title(self):
        """Test document title extraction."""
        content = """Some text
# My Document Title
More content"""
        
        title = extract_document_title(content)
        assert title == "My Document Title"
        
    def test_extract_document_title_none(self):
        """Test title extraction with no H1."""
        content = "## H2 heading\n### H3 heading"
        
        title = extract_document_title(content)
        assert title is None
        
    def test_has_cortex_header_true(self):
        """Test CORTEX header detection - present."""
        content = CORTEX_ASCII_LOGO + "\n# Document\nContent"
        
        assert has_cortex_header(content) is True
        
    def test_has_cortex_header_false(self):
        """Test CORTEX header detection - absent."""
        content = "# Document\nRegular content without CORTEX header"
        
        assert has_cortex_header(content) is False
        
    def test_inject_cortex_header_document(self):
        """Test header injection for document type."""
        original = "# My Document\n\nThis is content."
        
        result = inject_cortex_header(
            original,
            header_type="document",
            document_title="My Document",
            document_type="Test Document",
            status="✅ Complete"
        )
        
        assert '██████╗' in result
        assert '# My Document' in result
        assert '**Type:** Test Document' in result
        assert '**Status:** ✅ Complete' in result
        assert 'This is content.' in result
        
    def test_inject_cortex_header_sub_plan(self):
        """Test header injection for sub-plan type."""
        original = "# Phase 01\n\nPhase content."
        
        result = inject_cortex_header(
            original,
            header_type="sub_plan",
            phase_id="01",
            phase_name="Phase 01",
            master_plan_path="master.md",
            status="🟡 In Progress"
        )
        
        assert '██████╗' in result
        assert '**🔗 Breadcrumb:**' in result
        assert '**Phase ID:** 01' in result
        assert 'Phase content.' in result
        
    def test_inject_cortex_header_report(self):
        """Test header injection for report type."""
        original = "# Analysis Report\n\nReport data."
        
        result = inject_cortex_header(
            original,
            header_type="report",
            report_title="Analysis Report",
            report_type="Analysis",
            project_name="CORTEX"
        )
        
        assert '██████╗' in result
        assert '**Type:** Analysis' in result
        assert '**Project:** CORTEX' in result
        assert 'Report data.' in result
        
    def test_inject_cortex_header_ado(self):
        """Test header injection for ADO type."""
        original = "# Feature Title\n\nFeature description."
        
        result = inject_cortex_header(
            original,
            header_type="ado",
            feature_title="Feature Title",
            feature_type="Feature",
            priority="High"
        )
        
        assert '██████╗' in result
        assert '**Type:** Feature' in result
        assert '**Priority:** High' in result
        assert 'Feature description.' in result
        
    def test_inject_cortex_header_already_present(self):
        """Test header injection skips if already present."""
        original = CORTEX_ASCII_LOGO + "\n# Document\n\nContent"
        
        result = inject_cortex_header(
            original,
            header_type="document",
            document_title="Document",
            document_type="Test"
        )
        
        # Should return unchanged
        assert result == original
        
    def test_inject_cortex_header_invalid_type(self):
        """Test header injection with invalid type."""
        original = "# Document\n\nContent"
        
        with pytest.raises(ValueError, match="Unknown header type"):
            inject_cortex_header(
                original,
                header_type="invalid_type",
                document_title="Document"
            )
            
    def test_inject_cortex_header_no_title(self):
        """Test header injection with no existing title."""
        original = "Content without title."
        
        result = inject_cortex_header(
            original,
            header_type="document",
            document_title="Generated Title",
            document_type="Document"
        )
        
        assert '# Generated Title' in result
        assert 'Content without title.' in result
        
    def test_header_consistency_all_types(self):
        """Test all header types include consistent CORTEX branding."""
        headers = [
            generate_cortex_header("Doc", "Plan"),
            generate_sub_plan_header("01", "Phase", "master.md"),
            generate_report_header("Report", "Analysis"),
            generate_ado_header("Feature", "Feature")
        ]
        
        for header in headers:
            assert '██████╗' in header
            assert 'CORTEX' in header
            assert 'AI-Powered Development Intelligence System' in header
            assert 'Asif Hussain' in header
            assert 'Copyright © 2025' in header
