"""
CORTEX LENS Golden Test Suite - Extended Core Capabilities
Tests for comment extraction, vendor detection, and polyglot analysis.

Authority: AC-GOLDEN-LENS-012, AC-GOLDEN-LENS-013, AC-GOLDEN-LENS-014
Created: 2026-02-17
"""

import pytest
from pathlib import Path


@pytest.mark.e2e
@pytest.mark.lens
@pytest.mark.xfail(reason="RED phase - LENS orchestrator wiring pending")
class TestLENSExtendedCore:
    """Golden tests for extended LENS core capabilities."""
    
    def test_golden_12_comment_extraction(self, lens_harness, temp_repo_builder):
        """
        AC-GOLDEN-LENS-012: Comment Extraction
        
        Validates LENS ability to extract and categorize comments across Python and TypeScript:
        - Python docstrings (module, class, method)
        - JSDoc blocks with tags
        - TODO/FIXME/HACK markers
        - Inline comments
        - Deprecated annotations
        """
        scenario_path = Path(__file__).parent / "scenarios/lens/core/golden_12_comment_extraction.yaml"
        
        result = lens_harness.execute_lens_scenario(
            scenario_path=scenario_path,
            temp_repo_builder=temp_repo_builder
        )
        
        assert result.success, f"Comment extraction failed: {result.error}"
        assert result.comments_extracted >= 15, "Should extract all docstrings and comments"
        assert "TODO" in result.technical_debt_markers
        assert "FIXME" in result.technical_debt_markers
        assert "HACK" in result.technical_debt_markers
    
    def test_golden_13_vendor_detection(self, lens_harness, temp_repo_builder):
        """
        AC-GOLDEN-LENS-013: Vendor/Third-Party Detection
        
        Validates LENS ability to identify third-party libraries and frameworks:
        - Package manifest parsing (requirements.txt, package.json)
        - Import statement analysis
        - Framework detection (Django, React, Redux)
        - Cloud provider SDKs (AWS boto3)
        - Monitoring tools (Sentry, Datadog)
        """
        scenario_path = Path(__file__).parent / "scenarios/lens/core/golden_13_vendor_detection.yaml"
        
        result = lens_harness.execute_lens_scenario(
            scenario_path=scenario_path,
            temp_repo_builder=temp_repo_builder
        )
        
        assert result.success, f"Vendor detection failed: {result.error}"
        assert result.vendors_detected >= 20, "Should detect all third-party packages"
        assert "Django" in result.frameworks
        assert "React" in result.frameworks
        assert "AWS" in result.cloud_providers
    
    def test_golden_14_polyglot_analysis(self, lens_harness, temp_repo_builder):
        """
        AC-GOLDEN-LENS-014: Polyglot Codebase Analysis
        
        Validates LENS ability to analyze multi-language codebases:
        - Python + TypeScript + C# + SQL integration
        - Cross-language API boundaries
        - Shared data model alignment (User entity)
        - REST API contract detection
        - Docker composition analysis
        """
        scenario_path = Path(__file__).parent / "scenarios/lens/core/golden_14_polyglot_analysis.yaml"
        
        result = lens_harness.execute_lens_scenario(
            scenario_path=scenario_path,
            temp_repo_builder=temp_repo_builder
        )
        
        assert result.success, f"Polyglot analysis failed: {result.error}"
        assert len(result.languages) >= 4, "Should detect Python, TypeScript, C#, SQL"
        assert result.cross_language_calls >= 4, "Should detect API boundaries"
        assert "User" in result.shared_data_models
        assert result.api_boundaries_detected
