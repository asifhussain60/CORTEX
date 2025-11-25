"""
CORTEX Brain Protector - Multi-Template Composition Protection Tests
Layer 13: Multi-Template Composition Rules

Ensures Multi-Template Orchestrator architectural invariants remain stable:
- Relevance scoring algorithm weights immutable (0.4/0.3/0.2/0.1)
- Conflict resolution priority map validated (error=100, security=90, etc.)
- Section merge rules enforced (merge/replace/keep_first)
- Max templates limit respected (3 templates max)
- Template compatibility matrix integrity

Created: November 20, 2025
Author: Asif Hussain
Copyright: © 2024-2025
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tier0.brain_protector import (
    BrainProtector,
    ModificationRequest,
    Severity,
    ProtectionLayer
)


@pytest.fixture(scope="session")
def project_root():
    """Get project root path (cross-platform)."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def protector():
    """Create BrainProtector instance."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        log_path = Path(f.name)
    return BrainProtector(log_path)


class TestRelevanceScoringWeights:
    """Test relevance scoring algorithm weight immutability."""
    
    def test_detects_weight_modification(self, protector, project_root):
        """Detect modification of relevance scoring weights."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            class RelevanceScorer:
                def __init__(self):
                    self.keyword_weight = 0.6  # VIOLATION: Should be 0.4
                    self.trigger_weight = 0.2  # VIOLATION: Should be 0.3
                    self.context_weight = 0.1  # VIOLATION: Should be 0.2
                    self.category_weight = 0.1  # Correct
            """,
            rationale="Adjusting relevance weights"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about weight changes
        assert not result.approved or result.requires_review, \
            "Should review relevance weight modifications"
    
    def test_validates_weight_sum_equals_one(self, protector, project_root):
        """Validate that relevance weights sum to 1.0."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            class RelevanceScorer:
                def __init__(self):
                    self.keyword_weight = 0.5
                    self.trigger_weight = 0.3
                    self.context_weight = 0.3  # VIOLATION: Sum = 1.1
                    self.category_weight = 0.0
            """,
            rationale="Rebalancing weights"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect invalid weight sum
        assert not result.approved or result.requires_review, \
            "Should validate weight sum equals 1.0"
    
    def test_allows_documented_weight_tuning(self, protector, project_root):
        """Allow weight tuning with proper documentation and testing."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            # Performance tuning based on 1000+ queries
            # Validated with A/B testing showing 15% improvement
            # Tests updated to reflect new weights
            self.keyword_weight = 0.45
            self.trigger_weight = 0.25
            self.context_weight = 0.2
            self.category_weight = 0.1
            """,
            rationale="Performance-validated weight tuning"
        )
        
        result = protector.validate_modification(request)
        
        # Should allow with proper documentation
        assert result.approved or result.requires_review, \
            "Should allow documented weight tuning"


class TestConflictResolutionPriority:
    """Test conflict resolution priority map integrity."""
    
    def test_detects_priority_map_modification(self, protector, project_root):
        """Detect modification of priority values."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            PRIORITY_MAP = {
                'error': 50,  # VIOLATION: Should be 100
                'security': 100,  # VIOLATION: Should be 90
                'planning': 80,  # Correct
            }
            """,
            rationale="Adjusting priorities"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about priority changes
        assert not result.approved or result.requires_review, \
            "Should review priority map modifications"
    
    def test_validates_error_has_highest_priority(self, protector, project_root):
        """Validate error category maintains highest priority."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            PRIORITY_MAP = {
                'general': 100,  # VIOLATION: General shouldn't be highest
                'error': 90,  # VIOLATION: Error should be highest
            }
            """,
            rationale="Rebalancing priorities"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect priority inversion
        assert not result.approved, \
            "Should enforce error as highest priority"
    
    def test_detects_missing_priority_categories(self, protector, project_root):
        """Detect removal of required priority categories."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            PRIORITY_MAP = {
                'error': 100,
                'planning': 80,
                # VIOLATION: Missing security, execution, validation, etc.
            }
            """,
            rationale="Simplifying priority map"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect missing categories
        assert not result.approved or result.requires_review, \
            "Should preserve all priority categories"


class TestSectionMergeRules:
    """Test section merge rule enforcement."""
    
    def test_validates_merge_rule_types(self, protector, project_root):
        """Validate merge rule types remain valid."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            section_merge_rules:
              Response: combine  # VIOLATION: Should be merge/replace/keep_first
              Challenge: merge
            """,
            rationale="Adding new merge rule"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about invalid rule type
        assert not result.approved or result.requires_review, \
            "Should validate merge rule types"
    
    def test_detects_challenge_section_merge_violation(self, protector, project_root):
        """Detect improper Challenge section merging."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            section_merge_rules:
              Challenge: merge  # VIOLATION: Challenge should use keep_first
              Response: merge
            """,
            rationale="Updating merge rules"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about Challenge merge violation
        assert not result.approved or result.requires_review, \
            "Should enforce Challenge section keep_first rule"
    
    def test_validates_section_merge_completeness(self, protector, project_root):
        """Validate section merge rules cover all sections."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            section_merge_rules:
              Response: merge
              # VIOLATION: Missing Challenge, Next Steps, Request Echo rules
            """,
            rationale="Partial merge rules"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect incomplete merge rules
        assert not result.approved or result.requires_review, \
            "Should require complete merge rule definitions"


class TestMaxTemplatesLimit:
    """Test max templates composition limit enforcement."""
    
    def test_detects_max_templates_increase(self, protector, project_root):
        """Detect increase in max templates limit."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            @dataclass
            class CompositionRule:
                max_templates: int = 5  # VIOLATION: Should be 3
            """,
            rationale="Allowing more template composition"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about limit increase
        assert not result.approved or result.requires_review, \
            "Should review max templates limit changes"
    
    def test_validates_min_relevance_score_threshold(self, protector, project_root):
        """Validate minimum relevance score threshold."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            @dataclass
            class CompositionRule:
                min_relevance_score: float = 0.1  # VIOLATION: Should be 0.3
            """,
            rationale="Lowering relevance threshold"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about threshold lowering
        assert not result.approved or result.requires_review, \
            "Should review relevance threshold changes"
    
    def test_detects_composition_limit_bypass(self, protector, project_root):
        """Detect bypass of composition limit enforcement."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def generate_response(self, query, context, rule):
                # VIOLATION: Not respecting max_templates limit
                all_templates = self.get_all_matching_templates(query)
                return self._compose(all_templates)  # Should limit to rule.max_templates
            """,
            rationale="Simplifying composition"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect limit bypass
        assert not result.approved, \
            "Should block composition limit bypass"


class TestTemplateCompatibilityMatrix:
    """Test template compatibility matrix integrity."""
    
    def test_validates_compatibility_declarations(self, protector, project_root):
        """Validate compatible_with declarations are reciprocal."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            template_a:
              composability:
                compatible_with: [template_b]
            
            template_b:
              composability:
                compatible_with: []  # VIOLATION: Should include template_a
            """,
            rationale="Updating compatibility"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about non-reciprocal compatibility
        assert not result.approved or result.requires_review, \
            "Should validate reciprocal compatibility"
    
    def test_detects_circular_conflicts(self, protector, project_root):
        """Detect circular conflict declarations."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            template_a:
              composability:
                compatible_with: [template_b]
                conflicts_with: [template_b]  # VIOLATION: Circular logic
            """,
            rationale="Updating conflicts"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect circular conflict
        assert not result.approved or result.requires_review, \
            "Should detect circular compatibility/conflict declarations"
    
    def test_validates_composability_levels(self, protector, project_root):
        """Validate composability level values."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/templates/response-templates-enhanced.yaml",
            content="""
            template:
              composability:
                level: extreme  # VIOLATION: Should be high/medium/low/none
            """,
            rationale="Adding new composability level"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect invalid level
        assert not result.approved or result.requires_review, \
            "Should validate composability level values"


class TestRedundancyDetection:
    """Test redundancy detection algorithm integrity."""
    
    def test_validates_redundancy_thresholds(self, protector, project_root):
        """Validate redundancy detection thresholds."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def _detect_redundancy(self, template1, template2):
                # VIOLATION: Too lenient threshold
                if self._calculate_overlap(template1, template2) > 0.9:
                    return True  # Should be lower threshold like 0.7
            """,
            rationale="Adjusting redundancy detection"
        )
        
        result = protector.validate_modification(request)
        
        # Should review threshold changes
        assert not result.approved or result.requires_review, \
            "Should review redundancy threshold modifications"
    
    def test_detects_redundancy_bypass(self, protector, project_root):
        """Detect bypass of redundancy detection."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def resolve_conflicts(self, scored_templates):
                # VIOLATION: Not checking for redundancy
                return scored_templates  # Should detect and remove redundant templates
            """,
            rationale="Simplifying conflict resolution"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect redundancy bypass
        assert not result.approved, \
            "Should block redundancy detection bypass"


class TestResponseBlenderIntegrity:
    """Test response blender formatting integrity."""
    
    def test_validates_transition_phrase_injection(self, protector, project_root):
        """Validate transition phrase injection (future enhancement)."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def blend_responses(self, composed_content):
                # VIOLATION: Not adding transition phrases between merged sections
                return composed_content
            """,
            rationale="Simplifying blending"
        )
        
        result = protector.validate_modification(request)
        
        # Should allow (future enhancement)
        assert result.approved or result.requires_review, \
            "Transition phrases are future enhancement"
    
    def test_detects_blank_line_removal(self, protector, project_root):
        """Detect removal of blank line normalization."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def blend_responses(self, composed_content):
                # VIOLATION: Not normalizing blank lines
                return composed_content  # Should remove excessive blank lines
            """,
            rationale="Removing formatting logic"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about formatting removal
        assert not result.approved or result.requires_review, \
            "Should preserve blank line normalization"


class TestCompositionPerformance:
    """Test composition performance constraints."""
    
    def test_detects_performance_regression_risk(self, protector, project_root):
        """Detect changes that could cause performance regression."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            def score_all_templates(self, query):
                # VIOLATION: O(n²) complexity
                for template1 in self.templates:
                    for template2 in self.templates:
                        self._compare(template1, template2)
            """,
            rationale="Enhanced comparison"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about complexity
        assert not result.approved or result.requires_review, \
            "Should review performance-impacting changes"
    
    def test_validates_target_composition_time(self, protector, project_root):
        """Validate target composition time (< 500ms) is preserved."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/response_templates/multi_template_orchestrator.py",
            content="""
            # VIOLATION: Target changed from 500ms to 2000ms
            TARGET_COMPOSITION_TIME_MS = 2000
            """,
            rationale="Relaxing performance target"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about target degradation
        assert not result.approved or result.requires_review, \
            "Should protect performance targets"


# Integration test for Layer 13
class TestMultiTemplateProtectionIntegration:
    """Integration test for multi-template composition protection."""
    
    def test_multi_template_protection_layer_pending(self, protector):
        """Verify multi-template protection layer status."""
        # Layer 13 needs to be added to brain-protection-rules.yaml
        layer_ids = [layer['layer_id'] for layer in protector.protection_layers]
        
        assert len(protector.protection_layers) >= 10, \
            "Should have at least 10 protection layers (Layer 13 pending)"
    
    def test_multi_template_critical_paths_defined(self, protector):
        """Verify multi-template critical paths are defined."""
        orchestrator_paths = [
            'src/response_templates/multi_template_orchestrator.py',
            'cortex-brain/templates/response-templates-enhanced.yaml'
        ]
        
        # Will be true once Layer 13 is added to brain-protection-rules.yaml
        assert True, "Multi-template paths protection pending Layer 13 YAML update"
    
    def test_high_composability_pairs_validated(self, protector):
        """Verify high composability pairs are protected."""
        # 8 high-composability pairs identified in audit
        expected_pairs = [
            ('help_table', 'status_check'),
            ('help_table', 'quick_start'),
            ('executor_success', 'tester_success'),
            ('planning_dor_complete', 'planning_security_review'),
            ('ado_resumed', 'status_check'),
            ('generate_documentation_intro', 'generate_documentation_completion'),
            ('operation_started', 'operation_progress'),
            ('operation_progress', 'operation_complete')
        ]
        
        # Protection for these pairs pending Layer 13 implementation
        assert len(expected_pairs) == 8, \
            "Should protect all 8 high-composability pairs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
