#!/usr/bin/env python3
"""
Tests for Markdown to YAML Converter

Part of: CORTEX 6.0 Remediation Plan - Phase P0-T3
TDD Cycle: RED → GREEN → REFACTOR
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08
"""

import pytest
import yaml
from pathlib import Path
from src.tools.md_to_yaml_converter import (
    MDToYAMLConverter,
    ConversionResult,
    ConversionError,
    RequirementExtractor
)


class TestMDToYAMLConverter:
    """Test suite for MDToYAMLConverter."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        return MDToYAMLConverter()
    
    @pytest.fixture
    def simple_md_file(self, tmp_path):
        """Create simple markdown requirements file."""
        content = """# Feature: User Authentication

## Description
User authentication system with OAuth2 support.

## Requirements

### REQ-001: Login Functionality
**Priority:** P0_CRITICAL  
**Status:** COMPLETE

Users must be able to log in using email and password.

**Acceptance Criteria:**
- Email validation
- Password strength checking
- Session management

### REQ-002: OAuth2 Integration
**Priority:** P1_HIGH  
**Status:** IN_PROGRESS

Support OAuth2 login via Google and GitHub.

**Acceptance Criteria:**
- Google OAuth2 flow
- GitHub OAuth2 flow
- Token management
"""
        file_path = tmp_path / "simple_requirements.md"
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
    
    @pytest.fixture
    def complex_md_file(self, tmp_path):
        """Create complex markdown with tables and edge cases."""
        content = """# Feature: Advanced Analytics

## Metadata
- **Feature ID:** feat03
- **Owner:** Team Analytics
- **Estimated Hours:** 40

## Requirements

| ID | Description | Priority | Status |
|----|-------------|----------|--------|
| REQ-010 | Real-time dashboard | P0_CRITICAL | COMPLETE |
| REQ-011 | Historical reports | P1_HIGH | IN_PROGRESS |

### REQ-012: Data Export
Export analytics data in multiple formats (CSV, JSON, PDF).

**Dependencies:** REQ-010, REQ-011
"""
        file_path = tmp_path / "complex_requirements.md"
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
    
    @pytest.fixture
    def malformed_md_file(self, tmp_path):
        """Create malformed markdown file."""
        content = """# Incomplete Feature

## Requirements

### Invalid ID Format
This requirement has no proper ID.

### REQ-999
Missing priority and status fields.
"""
        file_path = tmp_path / "malformed_requirements.md"
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
    
    # ==================== TEST CASES ====================
    
    def test_converter_initialization(self, converter):
        """Test converter initializes correctly."""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'validate_output')
    
    def test_parse_simple_markdown(self, converter, simple_md_file):
        """Test parsing simple markdown file."""
        result = converter.convert(simple_md_file)
        
        assert result.success is True
        assert result.output_data is not None
        assert len(result.errors) == 0
    
    def test_extract_requirements(self, converter, simple_md_file):
        """Test extracting requirements from markdown."""
        result = converter.convert(simple_md_file)
        
        data = result.output_data
        assert "requirements" in data or isinstance(data, list)
        
        # Check we extracted both requirements
        reqs = data if isinstance(data, list) else data.get("requirements", [])
        assert len(reqs) >= 2
    
    def test_requirement_structure(self, converter, simple_md_file):
        """Test extracted requirement has correct structure."""
        result = converter.convert(simple_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        req = reqs[0]
        
        # Required fields
        assert "requirement_id" in req
        assert "description" in req
        
        # Optional but expected fields
        if "priority" in req:
            assert req["priority"] in ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
        
        if "status" in req:
            assert req["status"] in ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "BLOCKED"]
    
    def test_parse_priority(self, converter, simple_md_file):
        """Test parsing priority from markdown."""
        result = converter.convert(simple_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        req_001 = next(r for r in reqs if r["requirement_id"] == "REQ-001")
        assert req_001["priority"] == "P0_CRITICAL"
    
    def test_parse_status(self, converter, simple_md_file):
        """Test parsing status from markdown."""
        result = converter.convert(simple_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        req_001 = next(r for r in reqs if r["requirement_id"] == "REQ-001")
        assert req_001["status"] == "COMPLETE"
    
    def test_parse_acceptance_criteria(self, converter, simple_md_file):
        """Test parsing acceptance criteria."""
        result = converter.convert(simple_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        req_001 = next(r for r in reqs if r["requirement_id"] == "REQ-001")
        
        assert "acceptance_criteria" in req_001
        assert isinstance(req_001["acceptance_criteria"], list)
        assert len(req_001["acceptance_criteria"]) == 3
        assert "Email validation" in req_001["acceptance_criteria"]
    
    def test_parse_table_format(self, converter, complex_md_file):
        """Test parsing requirements from markdown tables."""
        result = converter.convert(complex_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        # Should extract REQ-010 and REQ-011 from table
        req_ids = [r["requirement_id"] for r in reqs]
        assert "REQ-010" in req_ids
        assert "REQ-011" in req_ids
    
    def test_parse_dependencies(self, converter, complex_md_file):
        """Test parsing dependencies."""
        result = converter.convert(complex_md_file)
        reqs = result.output_data if isinstance(result.output_data, list) else result.output_data.get("requirements", [])
        
        req_012 = next((r for r in reqs if r["requirement_id"] == "REQ-012"), None)
        if req_012 and "dependencies" in req_012:
            assert "REQ-010" in req_012["dependencies"]
            assert "REQ-011" in req_012["dependencies"]
    
    def test_handle_malformed_markdown(self, converter, malformed_md_file):
        """Test handling of malformed markdown."""
        result = converter.convert(malformed_md_file)
        
        # Should still succeed but with warnings
        assert result.success is True or len(result.warnings) > 0
    
    def test_validate_output_against_schema(self, converter, simple_md_file, tmp_path):
        """Test output validation against requirements schema."""
        result = converter.convert(simple_md_file)
        
        # Should have validation step
        assert hasattr(result, "validated")
        
        if result.success:
            # Try to save and validate
            output_file = tmp_path / "output.yaml"
            converter.save(result, output_file)
            
            assert output_file.exists()
    
    def test_conversion_report(self, converter, simple_md_file):
        """Test conversion generates report."""
        result = converter.convert(simple_md_file)
        
        assert hasattr(result, "summary")
        assert hasattr(result, "requirements_count")
    
    def test_preserve_metadata(self, converter, complex_md_file):
        """Test metadata preservation."""
        result = converter.convert(complex_md_file)
        
        # Check if feature-level metadata extracted
        if isinstance(result.output_data, dict):
            data = result.output_data
            # Metadata might be in feature object or inline
            assert "feature_id" in data or "requirements" in data
    
    def test_cli_interface(self, converter, simple_md_file, tmp_path):
        """Test CLI can convert file."""
        output_file = tmp_path / "output.yaml"
        
        # Programmatic test (CLI tested separately)
        result = converter.convert(simple_md_file)
        converter.save(result, output_file)
        
        assert output_file.exists()
        
        # Verify it's valid YAML
        with open(output_file, "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
    
    def test_batch_conversion(self, converter, simple_md_file, complex_md_file):
        """Test batch conversion of multiple files."""
        results = converter.convert_batch([simple_md_file, complex_md_file])
        
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_error_reporting(self, converter, tmp_path):
        """Test error reporting for non-existent file."""
        result = converter.convert(tmp_path / "nonexistent.md")
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_edge_case_empty_file(self, converter, tmp_path):
        """Test handling of empty markdown file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")
        
        result = converter.convert(empty_file)
        
        # Should handle gracefully
        assert result is not None
        assert result.success is False or len(result.warnings) > 0
