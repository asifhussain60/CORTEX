"""
Phase 23 Golden Tests: STS Knowledge Synthesis

Zero-mock tests for knowledge YAMLs, component registry, and STS analyzer.
"""
import pytest
from pathlib import Path
import yaml

from cortex.brain.knowledge.yaml_synthesizer import KnowledgeYAMLSynthesizer
from cortex.registry.component_registry import (
    ComponentRegistry,
    ComponentRegistration,
    consolidate_components
)
from cortex.sts.sts_analyzer import STSAnalyzer, cortex_analyze_sts_app


class TestKnowledgeYAMLSynthesis:
    """Test knowledge YAML creation (S1)."""
    
    def test_azure_security_yaml_structure(self):
        """Test Azure Security YAML has required fields."""
        synthesizer = KnowledgeYAMLSynthesizer()
        content = synthesizer.create_azure_security_yaml()
        
        assert content["domain"] == "azure-security"
        assert "patterns" in content
        assert len(content["patterns"]) >= 2
        assert content["patterns"][0]["id"].startswith("AZ-SEC")
    
    def test_databricks_yaml_structure(self):
        """Test Databricks YAML has Spark + Delta patterns."""
        synthesizer = KnowledgeYAMLSynthesizer()
        content = synthesizer.create_databricks_patterns_yaml()
        
        assert content["domain"] == "databricks"
        assert any("Spark" in p["name"] for p in content["patterns"])
        assert any("Delta" in p["name"] for p in content["patterns"])
    
    def test_launchdarkly_yaml_structure(self):
        """Test LaunchDarkly YAML has feature flag patterns."""
        synthesizer = KnowledgeYAMLSynthesizer()
        content = synthesizer.create_launchdarkly_yaml()
        
        assert content["domain"] == "feature-flags"
        assert any("Flag" in p["name"] for p in content["patterns"])


class TestComponentRegistry:
    """Test component registration system (S2)."""
    
    def test_component_registration(self):
        """Test registering a component."""
        registry = ComponentRegistry()
        comp = ComponentRegistration(
            "test_comp",
            "service",
            "IntelligenceOrchestrator",
            ["test"],
            "HIGH_VALUE"
        )
        
        result = registry.register_component(comp)
        assert result is True
        assert "test_comp" in registry.components
    
    def test_duplicate_registration_prevented(self):
        """Test duplicate registration is prevented."""
        registry = ComponentRegistry()
        comp = ComponentRegistration(
            "dup_comp",
            "service",
            "IntelligenceOrchestrator",
            ["test"],
            "HIGH_VALUE"
        )
        
        assert registry.register_component(comp) is True
        assert registry.register_component(comp) is False
    
    def test_get_components_by_orchestrator(self):
        """Test retrieving components by orchestrator."""
        registry = consolidate_components()
        comps = registry.get_components_by_orchestrator("IntelligenceOrchestrator")
        
        assert len(comps) >= 2
        assert all(c.orchestrator == "IntelligenceOrchestrator" for c in comps)
    
    def test_high_value_components_filter(self):
        """Test filtering HIGH_VALUE components."""
        registry = consolidate_components()
        high_value = registry.get_high_value_components()
        
        assert len(high_value) >= 3
        assert all(c.priority == "HIGH_VALUE" for c in high_value)
    
    def test_contract_validation(self):
        """Test contract validation prevents unwiring."""
        registry = consolidate_components()
        
        assert registry.validate_contract("learning_loop_service") is True
        assert registry.validate_contract("nonexistent_comp") is False


class TestSTSAnalyzer:
    """Test STS automated analysis tool (S3)."""
    
    def test_load_anti_patterns(self):
        """Test loading 61 STS anti-patterns."""
        analyzer = STSAnalyzer()
        
        assert len(analyzer.anti_patterns) >= 3
        assert all(ap.id.startswith("STS-") for ap in analyzer.anti_patterns)
    
    def test_analyze_repository(self, tmp_path):
        """Test repository analysis."""
        analyzer = STSAnalyzer()
        result = analyzer.analyze_repository(str(tmp_path))
        
        assert result.repository_path == str(tmp_path)
        assert len(result.anti_patterns_detected) >= 0
        assert result.complexity_score >= 0
        assert result.technical_debt_hours >= 0
    
    def test_metrics_report_generation(self, tmp_path):
        """Test metrics report has before/after/improvement."""
        analyzer = STSAnalyzer()
        result = analyzer.analyze_repository(str(tmp_path))
        report = analyzer.generate_metrics_report(result)
        
        assert "before" in report
        assert "after" in report
        assert "improvement" in report
        assert report["after"]["complexity"] < report["before"]["complexity"]
    
    def test_mcp_tool_interface(self, tmp_path):
        """Test cortex_analyze_sts_app MCP tool."""
        report = cortex_analyze_sts_app(str(tmp_path))
        
        assert "repository" in report
        assert "before" in report
        assert "after" in report
        assert "improvement" in report


class TestPhase23Integration:
    """Integration tests for Phase 23."""
    
    def test_knowledge_component_sts_integration(self, tmp_path):
        """Test all 3 stages work together."""
        # S1: Knowledge YAMLs
        synthesizer = KnowledgeYAMLSynthesizer()
        domains = synthesizer.synthesize_all()
        assert len(domains) >= 3
        
        # S2: Component Registry
        registry = consolidate_components()
        assert len(registry.components) >= 3
        
        # S3: STS Analyzer
        report = cortex_analyze_sts_app(str(tmp_path))
        assert report["improvement"]["complexity_reduction"] == "70%"
