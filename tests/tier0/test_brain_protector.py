"""
CORTEX Brain Protector Tests
Phase 3 Task 3.4: Testing

Updated: November 8, 2025
Tests now validate YAML-based configuration instead of hardcoded rules.
Configuration: cortex-brain/brain-protection-rules.yaml
"""

import pytest
import tempfile
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tier0.brain_protector import (
    BrainProtector,
    ModificationRequest,
    Severity,
    ProtectionLayer,
    Violation
)


class TestYAMLConfiguration:
    """Test that YAML configuration loads correctly."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_loads_yaml_configuration(self, protector):
        """Verify YAML rules are loaded successfully."""
        assert protector.rules_config is not None
        assert 'protection_layers' in protector.rules_config
        assert len(protector.rules_config['protection_layers']) == 6
    
    def test_has_all_protection_layers(self, protector):
        """Verify all 6 protection layers are configured."""
        layer_ids = [layer['layer_id'] for layer in protector.protection_layers]
        expected_layers = [
            'instinct_immutability',
            'tier_boundary',
            'solid_compliance',
            'hemisphere_specialization',
            'knowledge_quality',
            'commit_integrity'
        ]
        for expected in expected_layers:
            assert expected in layer_ids
    
    def test_critical_paths_loaded(self, protector):
        """Verify critical paths loaded from YAML."""
        assert len(protector.CRITICAL_PATHS) > 0
        assert any('tier0' in path.lower() for path in protector.CRITICAL_PATHS)
    
    def test_application_paths_loaded(self, protector):
        """Verify application paths loaded from YAML."""
        assert len(protector.APPLICATION_PATHS) > 0
    
    def test_brain_state_files_loaded(self, protector):
        """Verify brain state files loaded from YAML."""
        assert len(protector.BRAIN_STATE_FILES) > 0
        assert any('conversation-history' in f for f in protector.BRAIN_STATE_FILES)


class TestInstinctImmutability:
    """Test Layer 1: Instinct Immutability protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_tdd_bypass_attempt(self, protector):
        """Verify BLOCKS code implementation without tests."""
        request = ModificationRequest(
            intent="skip tests for quick fix",
            description="Need to bypass TDD for urgent production bug",
            files=["CORTEX/src/tier2/knowledge_graph.py"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.BLOCKED
        assert result.decision == "BLOCK"
        assert any(v.rule == "TDD_ENFORCEMENT" for v in result.violations)
    
    def test_detects_dod_bypass_attempt(self, protector):
        """Verify BLOCKS attempts to skip Definition of Done."""
        request = ModificationRequest(
            intent="allow warnings in build",
            description="Disable error checking to ship faster",
            files=["CORTEX/src/tier1/conversation_manager.py"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.BLOCKED
        assert any(v.rule == "DEFINITION_OF_DONE" for v in result.violations)
    
    def test_allows_compliant_changes(self, protector):
        """Verify allows TDD-compliant modifications."""
        request = ModificationRequest(
            intent="add new pattern type with tests",
            description="Implementing RED-GREEN-REFACTOR workflow",
            files=["CORTEX/src/tier2/knowledge_graph.py"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.SAFE
        assert result.decision == "ALLOW"


class TestTierBoundaryProtection:
    """Test Layer 2: Tier Boundary protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_application_data_in_tier0(self, protector):
        """Verify BLOCKS application paths in Tier 0."""
        request = ModificationRequest(
            intent="add KSESSIONS pattern to governance",
            description="Store SPA/KSESSIONS workflow in tier0",
            files=["cortex-brain/tier0/ksessions-patterns.yaml"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.BLOCKED
        assert any(v.rule == "TIER0_APPLICATION_DATA" for v in result.violations)
    
    def test_warns_conversation_data_in_tier2(self, protector):
        """Verify WARNS on conversation data in Tier 2."""
        request = ModificationRequest(
            intent="store conversation in knowledge graph",
            description="Add conversation-history to tier2",
            files=["cortex-brain/tier2/conversation-storage.db"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "TIER2_CONVERSATION_DATA" for v in result.violations)


class TestSOLIDCompliance:
    """Test Layer 3: SOLID Compliance protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_god_object_pattern(self, protector):
        """Verify WARNS on God Object patterns."""
        request = ModificationRequest(
            intent="add mode switch to handle all cases",
            description="Add switch statement to do everything in one class",
            files=["prompts/internal/code-executor.md"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "SINGLE_RESPONSIBILITY" for v in result.violations)
    
    def test_detects_hardcoded_dependencies(self, protector):
        """Verify WARNS on hardcoded paths."""
        request = ModificationRequest(
            intent="configure system",
            description="Hardcode path to D:/PROJECTS/CORTEX in code",
            files=["CORTEX/src/tier1/conversation_manager.py"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "DEPENDENCY_INVERSION" for v in result.violations)


class TestHemisphereSpecialization:
    """Test Layer 4: Hemisphere Specialization protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_strategic_logic_in_left_brain(self, protector):
        """Verify WARNS on planning logic in tactical agents."""
        request = ModificationRequest(
            intent="add create plan function to executor",
            description="Code executor should estimate time and assess risk",
            files=["prompts/internal/code-executor.md"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "LEFT_BRAIN_TACTICAL" for v in result.violations)
    
    def test_detects_tactical_logic_in_right_brain(self, protector):
        """Verify WARNS on execution logic in strategic agents."""
        request = ModificationRequest(
            intent="planner should write code directly",
            description="Work planner will implement and run tests",
            files=["prompts/internal/work-planner.md"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "RIGHT_BRAIN_STRATEGIC" for v in result.violations)


class TestKnowledgeQuality:
    """Test Layer 5: Knowledge Quality protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_high_confidence_single_event(self, protector):
        """Verify WARNS on high confidence with single occurrence."""
        request = ModificationRequest(
            intent="add pattern",
            description="Add pattern with confidence: 1.0 and occurrences: 1",
            files=["cortex-brain/tier2/knowledge_graph.db"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "MIN_OCCURRENCES" for v in result.violations)


class TestCommitIntegrity:
    """Test Layer 6: Commit Integrity protection."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_detects_brain_state_commit_attempt(self, protector):
        """Verify WARNS on committing brain state files."""
        request = ModificationRequest(
            intent="commit conversation history",
            description="Add conversation-history.jsonl to git",
            files=["cortex-brain/conversation-history.jsonl"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.WARNING
        assert any(v.rule == "BRAIN_STATE_GITIGNORE" for v in result.violations)


class TestChallengeGeneration:
    """Test challenge generation and formatting."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_generates_challenge_with_alternatives(self, protector):
        """Verify challenge includes safe alternatives."""
        violations = [
            Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="TDD_ENFORCEMENT",
                severity=Severity.BLOCKED,
                description="Attempt to bypass TDD",
                evidence="Intent: skip tests"
            )
        ]
        
        challenge = protector.generate_challenge(violations)
        
        assert "BRAIN PROTECTION CHALLENGE" in challenge.challenge_text
        assert len(challenge.options) == 3
        assert "Accept alternative" in challenge.options
        assert challenge.result.alternatives  # Has alternatives
    
    def test_challenge_includes_severity(self, protector):
        """Verify challenge displays severity correctly."""
        violations = [
            Violation(
                layer=ProtectionLayer.SOLID_COMPLIANCE,
                rule="SINGLE_RESPONSIBILITY",
                severity=Severity.WARNING,
                description="God Object detected",
                evidence="Adding multiple modes"
            )
        ]
        
        challenge = protector.generate_challenge(violations)
        
        assert "WARNING" in challenge.challenge_text
        assert challenge.result.severity == Severity.WARNING


class TestEventLogging:
    """Test protection event logging to corpus callosum."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector with temp log file."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path), log_path
    
    def test_logs_protection_event(self, protector):
        """Verify events are logged correctly."""
        bp, log_path = protector
        
        violations = [
            Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="TDD_ENFORCEMENT",
                severity=Severity.BLOCKED,
                description="TDD bypass attempt",
                evidence="skip tests"
            )
        ]
        
        challenge = bp.generate_challenge(violations)
        bp.log_event(challenge, "override", "Production emergency")
        
        # Read log
        with open(log_path, 'r') as f:
            event = json.loads(f.readline())
        
        assert event["event"] == "brain_protector_challenge"
        assert event["user_decision"] == "override"
        assert event["override_justification"] == "Production emergency"
        assert len(event["violations"]) == 1
        assert event["violations"][0]["rule"] == "TDD_ENFORCEMENT"
    
    def test_log_contains_alternatives(self, protector):
        """Verify logged events include suggested alternatives."""
        bp, log_path = protector
        
        violations = [
            Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="TDD_ENFORCEMENT",
                severity=Severity.BLOCKED,
                description="TDD bypass",
                evidence="skip tests"
            )
        ]
        
        challenge = bp.generate_challenge(violations)
        bp.log_event(challenge, "accept")
        
        # Read log
        with open(log_path, 'r') as f:
            event = json.loads(f.readline())
        
        assert "alternatives_suggested" in event
        assert len(event["alternatives_suggested"]) > 0


class TestMultipleViolations:
    """Test handling of multiple simultaneous violations."""
    
    @pytest.fixture
    def protector(self):
        """Create BrainProtector instance."""
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
            log_path = Path(f.name)
        return BrainProtector(log_path)
    
    def test_combines_multiple_violations(self, protector):
        """Verify multiple violations are detected together."""
        request = ModificationRequest(
            intent="skip tests and add mode switch",
            description="Bypass TDD and add switch to handle all cases with hardcode path",
            files=["prompts/internal/code-executor.md"]
        )
        
        result = protector.analyze_request(request)
        
        # Should detect TDD bypass + SOLID violation + DIP violation
        assert len(result.violations) >= 2
        assert result.severity == Severity.BLOCKED  # Highest severity wins
    
    def test_blocked_severity_overrides_warning(self, protector):
        """Verify BLOCKED takes precedence over WARNING."""
        request = ModificationRequest(
            intent="skip tests and hardcode path",
            description="No tests needed, just inline the config",
            files=["CORTEX/src/tier2/knowledge_graph.py"]
        )
        
        result = protector.analyze_request(request)
        
        assert result.severity == Severity.BLOCKED  # Not WARNING
        assert result.decision == "BLOCK"
        assert result.override_required is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
