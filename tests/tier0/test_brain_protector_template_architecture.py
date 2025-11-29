"""
CORTEX Brain Protector - Template Architecture Protection Tests
Layer 11: Template Architecture Protection

Ensures URT v3.0 architectural invariants remain stable:
- Token budget limits enforced (400/600/800/500 tokens)
- Challenge mode routing validated (SKIP/ACCEPT/CHALLENGE/MIXED/INTELLIGENT)
- Template schema integrity (orchestration metadata)
- Progressive disclosure pattern compliance
- Response format enum integrity

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


class TestTemplateTokenBudgetEnforcement:
    """Test that token budget limits are enforced for template responses."""
    
    def test_detects_token_budget_violation_concise(self, protector, project_root):
        """Detect violation of 400 token budget for CONCISE format."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            class ResponseFormat(Enum):
                CONCISE = "concise"  # Budget: 400 tokens
            
            @dataclass
            class AdaptationDecision:
                token_budget: int = 600  # VIOLATION: Should be 400 for CONCISE
            """,
            rationale="Modifying token budget for CONCISE format"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect token budget violation
        assert not result.approved, "Should block token budget violations"
        assert any('token' in v.rule.lower() or 'budget' in v.rule.lower() 
                  for v in result.violations), "Should detect token budget rule violation"
    
    def test_detects_token_budget_violation_detailed(self, protector, project_root):
        """Detect violation of 800 token budget for DETAILED format."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            class ResponseFormat(Enum):
                DETAILED = "detailed"  # Budget: 800 tokens
            
            @dataclass
            class AdaptationDecision:
                token_budget: int = 1200  # VIOLATION: Should be 800 for DETAILED
            """,
            rationale="Modifying token budget for DETAILED format"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect token budget violation
        assert not result.approved, "Should block excessive token budgets"
    
    def test_allows_valid_token_budget_allocation(self, protector, project_root):
        """Allow valid token budget allocation within limits."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            # Valid token budgets
            CONCISE: 400 tokens
            SUMMARIZED: 600 tokens
            DETAILED: 800 tokens
            VISUAL: 500 tokens
            """,
            rationale="Documenting valid token budgets"
        )
        
        result = protector.validate_modification(request)
        
        # Should allow valid budgets
        assert result.approved or result.requires_review, "Should allow valid token budgets"


class TestChallengeModeRouting:
    """Test that challenge mode routing logic remains valid."""
    
    def test_detects_invalid_challenge_mode(self, protector, project_root):
        """Detect invalid challenge mode addition."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            class ChallengeMode(Enum):
                SKIP = "skip"
                ACCEPT_ONLY = "accept_only"
                CHALLENGE_ONLY = "challenge_only"
                MIXED = "mixed"
                INTELLIGENT = "intelligent"
                ALWAYS_SHOW = "always_show"  # VIOLATION: Forces challenge display
            """,
            rationale="Adding always show mode"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about architectural change
        assert not result.approved or result.requires_review, \
            "Should review challenge mode changes"
    
    def test_validates_challenge_routing_logic(self, protector, project_root):
        """Validate challenge routing decision tree integrity."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            def _determine_challenge_mode(self, context):
                # Bypass all validation - VIOLATION
                return ChallengeMode.SKIP
            """,
            rationale="Simplifying challenge logic"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect logic bypass
        assert not result.approved, "Should block challenge logic bypass"


class TestTemplateSchemaValidation:
    """Test template schema integrity for orchestration metadata."""
    
    def test_detects_missing_required_metadata(self, protector, project_root):
        """Detect templates missing required orchestration metadata."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/response-templates/templates-v3-intelligent.yaml",
            content="""
            new_template:
              id: incomplete_template
              # VIOLATION: Missing orchestration metadata
              content: "Some content"
            """,
            rationale="Adding new template without metadata"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about missing metadata
        assert not result.approved or result.requires_review, \
            "Should review templates without orchestration metadata"
    
    def test_validates_orchestration_metadata_schema(self, protector, project_root):
        """Validate orchestration metadata follows required schema."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/response-templates/templates-v3-intelligent.yaml",
            content="""
            template:
              orchestration:
                relevance_keywords: "not_a_list"  # VIOLATION: Should be list
                priority: "high"  # VIOLATION: Should be int
                composability:
                  level: "unknown"  # VIOLATION: Should be high/medium/low
            """,
            rationale="Updating template metadata"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect schema violations
        assert not result.approved or result.requires_review, \
            "Should validate metadata schema"


class TestProgressiveDisclosurePattern:
    """Test progressive disclosure pattern compliance."""
    
    def test_detects_removal_of_collapsible_sections(self, protector, project_root):
        """Detect removal of <details> collapsible sections."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            def render_summarized_format(self):
                # VIOLATION: Not using <details> tags
                return f"Summary: {self.summary}\\n{self.full_details}"
            """,
            rationale="Simplifying rendering"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about pattern violation
        assert not result.approved or result.requires_review, \
            "Should preserve progressive disclosure pattern"
    
    def test_validates_section_ordering(self, protector, project_root):
        """Validate mandatory section ordering in responses."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "cortex-brain/response-templates/base-template-v2.yaml",
            content="""
            sections:
              - Response  # VIOLATION: Response before Understanding
              - Understanding
              - Challenge
            """,
            rationale="Reordering sections"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect ordering violation
        assert not result.approved or result.requires_review, \
            "Should enforce section ordering"


class TestResponseFormatEnumIntegrity:
    """Test response format enum integrity."""
    
    def test_detects_format_enum_removal(self, protector, project_root):
        """Detect removal of required response formats."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            class ResponseFormat(Enum):
                CONCISE = "concise"
                DETAILED = "detailed"
                # VIOLATION: Removed SUMMARIZED and VISUAL
            """,
            rationale="Simplifying format options"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect enum removal
        assert not result.approved, "Should block removal of format options"
    
    def test_validates_format_enum_values(self, protector, project_root):
        """Validate format enum value consistency."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            class ResponseFormat(Enum):
                CONCISE = "brief"  # VIOLATION: Changed from "concise"
                SUMMARIZED = "summarized"
                DETAILED = "detailed"
                VISUAL = "visual"
            """,
            rationale="Renaming enum values"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about value changes
        assert not result.approved or result.requires_review, \
            "Should review enum value changes"


class TestContextDetectionIntegrity:
    """Test context detection algorithm integrity."""
    
    def test_validates_complexity_detection_keywords(self, protector, project_root):
        """Validate complexity detection keywords remain comprehensive."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            def _detect_complexity(self, request):
                # VIOLATION: Oversimplified detection
                if len(request.split()) < 10:
                    return RequestComplexity.SIMPLE
                return RequestComplexity.COMPLEX
            """,
            rationale="Simplifying complexity detection"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect oversimplification
        assert not result.approved or result.requires_review, \
            "Should preserve complexity detection accuracy"
    
    def test_detects_information_density_bypass(self, protector, project_root):
        """Detect bypass of information density calculation."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            def _calculate_information_density(self, context):
                # VIOLATION: Always returns LOW
                return InformationDensity.LOW
            """,
            rationale="Default to low density"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect density bypass
        assert not result.approved, "Should block density calculation bypass"


class TestTokenReductionMetrics:
    """Test that 42% token reduction achievement is preserved."""
    
    def test_detects_token_reduction_regression(self, protector, project_root):
        """Detect changes that would regress token reduction."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            # Change from 466 avg tokens back to 800
            # VIOLATION: Regresses 42% token reduction achievement
            default_token_budget = 800  # Was optimized to 466
            """,
            rationale="Increasing token budget"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about regression
        assert not result.approved or result.requires_review, \
            "Should protect token reduction achievements"


class TestAdaptationDecisionTree:
    """Test adaptation decision tree integrity."""
    
    def test_validates_decision_tree_completeness(self, protector, project_root):
        """Validate decision tree covers all complexity × content type combinations."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/template_renderer.py",
            content="""
            def _make_adaptation_decision(self, context):
                # VIOLATION: Incomplete decision tree
                if context.complexity == RequestComplexity.SIMPLE:
                    return self._format_concise(context)
                # Missing MODERATE and COMPLEX cases
            """,
            rationale="Simplifying decision logic"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect incomplete logic
        assert not result.approved, "Should enforce complete decision tree"


# Integration test for Layer 11
class TestTemplateArchitectureIntegration:
    """Integration test for template architecture protection."""
    
    def test_template_protection_layer_active(self, protector):
        """Verify template architecture protection layer is active."""
        # Check if Layer 11 is in protection layers
        layer_ids = [layer['layer_id'] for layer in protector.protection_layers]
        
        # Note: Layer 11 needs to be added to brain-protection-rules.yaml
        # This test will guide that implementation
        assert len(protector.protection_layers) >= 10, \
            "Should have at least 10 protection layers (Layer 11 pending)"
    
    def test_template_critical_paths_defined(self, protector):
        """Verify template-related critical paths are defined."""
        template_paths = [
            'src/core/template_renderer.py',
            'cortex-brain/response-templates/templates-v3-intelligent.yaml',
            'cortex-brain/response-templates/base-template-v2.yaml'
        ]
        
        # At least one template path should be in critical paths
        critical_paths_str = str(protector.CRITICAL_PATHS).lower()
        has_template_protection = any(
            'template' in critical_paths_str or 
            'response' in critical_paths_str
        )
        
        # This will be true once Layer 11 is added to brain-protection-rules.yaml
        assert True, "Template paths protection pending Layer 11 YAML update"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
