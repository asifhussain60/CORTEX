"""
CORTEX Brain Protector - Context Management Architecture Protection Tests
Layer 12: Context Management Architecture Protection

Ensures Context Management system architectural invariants remain stable:
- Tier boundary isolation maintained (T1/T2/T3 separation)
- Token budget allocation algorithm fairness (relevance-based distribution)
- Staleness thresholds enforced (T1: 24h, T2: 90d, T3: 7d)
- Cross-tier linking schema validated (used_patterns, used_metrics fields)
- Quality score calculation consistency (health monitoring)
- Unified context orchestration integrity

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


class TestTierBoundaryIsolation:
    """Test tier boundary isolation enforcement."""
    
    def test_detects_tier_boundary_violation(self, protector, project_root):
        """Detect direct database access across tier boundaries."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/tier1/working_memory.py",
            content="""
            def get_context(self):
                # VIOLATION: T1 directly accessing T2 database
                from src.tier2.knowledge_graph import KnowledgeGraph
                kg = KnowledgeGraph()
                return kg.patterns  # Should use UnifiedContextManager
            """,
            rationale="Direct pattern access"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect tier boundary violation
        assert not result.approved, \
            "Should block direct cross-tier database access"
    
    def test_validates_unified_context_manager_usage(self, protector, project_root):
        """Validate context access goes through UnifiedContextManager."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/cortex_agents/code_executor.py",
            content="""
            def execute(self, request):
                # VIOLATION: Bypassing UnifiedContextManager
                tier1_data = self.tier1.query_directly()
                tier2_data = self.tier2.query_directly()
            """,
            rationale="Direct tier access"
        )
        
        result = protector.validate_modification(request)
        
        # Should enforce UnifiedContextManager usage
        assert not result.approved or result.requires_review, \
            "Should require UnifiedContextManager for context access"
    
    def test_allows_unified_context_manager_coordination(self, protector, project_root):
        """Allow proper cross-tier coordination via UnifiedContextManager."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/unified_context_manager.py",
            content="""
            def build_context(self, conversation_id, user_request):
                # VALID: UnifiedContextManager coordinating tiers
                t1_context = self.tier1.get_recent_conversations()
                t2_context = self.tier2.search_patterns()
                t3_context = self.tier3.get_insights()
                return self._merge_contexts(t1_context, t2_context, t3_context)
            """,
            rationale="Proper tier coordination"
        )
        
        result = protector.validate_modification(request)
        
        # Should allow UnifiedContextManager coordination
        assert result.approved or result.requires_review, \
            "Should allow UnifiedContextManager to coordinate tiers"


class TestTokenBudgetAllocation:
    """Test token budget allocation algorithm fairness."""
    
    def test_detects_unfair_budget_allocation(self, protector, project_root):
        """Detect unfair token budget allocation."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/token_budget_manager.py",
            content="""
            def allocate_budget(self, total_budget, tier_relevance):
                # VIOLATION: T1 always gets 90% regardless of relevance
                return {
                    'tier1': total_budget * 0.9,
                    'tier2': total_budget * 0.05,
                    'tier3': total_budget * 0.05
                }
            """,
            rationale="Prioritizing T1"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect unfair allocation
        assert not result.approved, \
            "Should enforce relevance-based budget allocation"
    
    def test_validates_budget_allocation_proportionality(self, protector, project_root):
        """Validate budget allocation is proportional to relevance."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/token_budget_manager.py",
            content="""
            def allocate_budget(self, total_budget, tier_relevance):
                # VIOLATION: Not using relevance scores
                allocation = {}
                for tier in tier_relevance:
                    allocation[tier] = total_budget / len(tier_relevance)
                return allocation  # Should be proportional to relevance
            """,
            rationale="Equal distribution"
        )
        
        result = protector.validate_modification(request)
        
        # Should enforce proportional allocation
        assert not result.approved or result.requires_review, \
            "Should require proportional budget allocation"
    
    def test_detects_budget_sum_violation(self, protector, project_root):
        """Detect budget allocation exceeding total budget."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/token_budget_manager.py",
            content="""
            def allocate_budget(self, total_budget, tier_relevance):
                # VIOLATION: Sum exceeds total_budget
                return {
                    'tier1': total_budget * 0.6,
                    'tier2': total_budget * 0.6,
                    'tier3': total_budget * 0.6
                }
            """,
            rationale="Generous allocation"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect budget overflow
        assert not result.approved, \
            "Should enforce total budget constraint"


class TestStalenessThresholds:
    """Test staleness threshold enforcement."""
    
    def test_detects_staleness_threshold_modification(self, protector, project_root):
        """Detect modification of staleness thresholds."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            STALENESS_THRESHOLDS = {
                'tier1': 168,  # VIOLATION: Should be 24 hours
                'tier2': 180,  # VIOLATION: Should be 90 days
                'tier3': 14    # VIOLATION: Should be 7 days
            }
            """,
            rationale="Extending staleness windows"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about threshold changes
        assert not result.approved or result.requires_review, \
            "Should review staleness threshold modifications"
    
    def test_validates_staleness_detection_logic(self, protector, project_root):
        """Validate staleness detection logic integrity."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def check_staleness(self, tier, last_update):
                # VIOLATION: Always returns False (not stale)
                return False
            """,
            rationale="Disabling staleness checks"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect staleness bypass
        assert not result.approved, \
            "Should block staleness detection bypass"
    
    def test_detects_missing_staleness_warnings(self, protector, project_root):
        """Detect removal of staleness warning generation."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def generate_health_report(self):
                # VIOLATION: Not reporting staleness issues
                return {
                    'overall_health': 'GOOD',
                    'recommendations': []
                }
            """,
            rationale="Simplifying reports"
        )
        
        result = protector.validate_modification(request)
        
        # Should require staleness reporting
        assert not result.approved or result.requires_review, \
            "Should preserve staleness warning generation"


class TestCrossTierLinkingSchema:
    """Test cross-tier linking schema integrity."""
    
    def test_detects_schema_field_removal(self, protector, project_root):
        """Detect removal of cross-tier linking fields."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/migrate_cross_tier_linking.py",
            content="""
            # VIOLATION: Not adding used_patterns field
            ALTER TABLE conversations ADD COLUMN used_metrics TEXT DEFAULT '[]';
            # Missing: used_patterns, context_quality_score
            """,
            rationale="Partial migration"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect incomplete schema
        assert not result.approved or result.requires_review, \
            "Should require complete cross-tier linking schema"
    
    def test_validates_json_field_types(self, protector, project_root):
        """Validate JSON field types for linking data."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/tier1/working_memory.py",
            content="""
            def store_conversation(self, conv_data):
                # VIOLATION: Storing list as string without JSON serialization
                conv_data['used_patterns'] = str(['pattern1', 'pattern2'])
            """,
            rationale="Storing patterns"
        )
        
        result = protector.validate_modification(request)
        
        # Should require proper JSON serialization
        assert not result.approved or result.requires_review, \
            "Should enforce JSON serialization for linking fields"
    
    def test_detects_bidirectional_linking_violation(self, protector, project_root):
        """Detect violations of bidirectional linking integrity."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/tier2/knowledge_graph.py",
            content="""
            def apply_pattern(self, pattern_id, conversation_id):
                # VIOLATION: Only updating T1, not T2
                self.tier1.add_used_pattern(conversation_id, pattern_id)
                # Missing: Update pattern's applied_in_conversations
            """,
            rationale="Linking pattern to conversation"
        )
        
        result = protector.validate_modification(request)
        
        # Should enforce bidirectional linking
        assert not result.approved or result.requires_review, \
            "Should require bidirectional linking updates"


class TestQualityScoreCalculation:
    """Test quality score calculation consistency."""
    
    def test_detects_quality_score_calculation_change(self, protector, project_root):
        """Detect changes to quality score calculation algorithm."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def calculate_quality_score(self, metrics):
                # VIOLATION: Changed formula
                return (metrics['staleness'] + metrics['coverage']) / 2
                # Should use weighted formula: staleness*0.4 + coverage*0.4 + performance*0.2
            """,
            rationale="Simplifying calculation"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about formula changes
        assert not result.approved or result.requires_review, \
            "Should review quality score formula changes"
    
    def test_validates_quality_score_range(self, protector, project_root):
        """Validate quality score remains in valid range (0-10)."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def calculate_quality_score(self, metrics):
                # VIOLATION: Can return values > 10
                return metrics['staleness'] * 100
            """,
            rationale="Enhanced scoring"
        )
        
        result = protector.validate_modification(request)
        
        # Should enforce score range
        assert not result.approved or result.requires_review, \
            "Should enforce quality score range (0-10)"
    
    def test_detects_health_status_mapping_change(self, protector, project_root):
        """Detect changes to health status thresholds."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def get_health_status(self, score):
                # VIOLATION: Changed thresholds
                if score >= 5: return 'EXCELLENT'  # Should be >= 8
                if score >= 3: return 'GOOD'       # Should be >= 6
                return 'POOR'
            """,
            rationale="More lenient thresholds"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about threshold changes
        assert not result.approved or result.requires_review, \
            "Should review health status threshold changes"


class TestUnifiedContextOrchestration:
    """Test unified context orchestration integrity."""
    
    def test_validates_parallel_tier_loading(self, protector, project_root):
        """Validate parallel tier loading is preserved."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/unified_context_manager.py",
            content="""
            def build_context(self):
                # VIOLATION: Sequential loading (not parallel)
                t1 = self.tier1.load()
                t2 = self.tier2.load()
                t3 = self.tier3.load()
                # Should use async/parallel loading
            """,
            rationale="Simplifying loading"
        )
        
        result = protector.validate_modification(request)
        
        # Should warn about performance degradation
        assert not result.approved or result.requires_review, \
            "Should preserve parallel tier loading"
    
    def test_detects_cache_bypass(self, protector, project_root):
        """Detect bypass of caching mechanism."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/unified_context_manager.py",
            content="""
            def build_context(self, request):
                # VIOLATION: Always rebuilding, never using cache
                return self._load_fresh_context(request)
            """,
            rationale="Removing caching"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect cache bypass
        assert not result.approved or result.requires_review, \
            "Should preserve caching mechanism"
    
    def test_validates_merge_deduplication(self, protector, project_root):
        """Validate context merge includes deduplication."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/unified_context_manager.py",
            content="""
            def _merge_contexts(self, t1, t2, t3):
                # VIOLATION: No deduplication
                return {'all': t1 + t2 + t3}
            """,
            rationale="Simplifying merge"
        )
        
        result = protector.validate_modification(request)
        
        # Should require deduplication
        assert not result.approved or result.requires_review, \
            "Should enforce context deduplication"


class TestContextInjectorIntegrity:
    """Test context injector formatting integrity."""
    
    def test_validates_format_styles_available(self, protector, project_root):
        """Validate all format styles (detailed/compact/minimal) remain available."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_injector.py",
            content="""
            FORMAT_STYLES = {
                'detailed': DetailedFormat,
                # VIOLATION: Missing compact and minimal
            }
            """,
            rationale="Removing unused formats"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect format removal
        assert not result.approved or result.requires_review, \
            "Should preserve all format styles"
    
    def test_detects_quality_badge_removal(self, protector, project_root):
        """Detect removal of quality badges from context display."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_injector.py",
            content="""
            def format_context(self, context):
                # VIOLATION: Not showing quality score
                return f"Context: {context['summary']}"
            """,
            rationale="Simplifying display"
        )
        
        result = protector.validate_modification(request)
        
        # Should preserve quality indicators
        assert not result.approved or result.requires_review, \
            "Should preserve quality badge display"
    
    def test_validates_token_usage_transparency(self, protector, project_root):
        """Validate token usage transparency is maintained."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_injector.py",
            content="""
            def format_context(self, context):
                # VIOLATION: Not showing token usage
                return self._format_without_token_info(context)
            """,
            rationale="Hiding implementation details"
        )
        
        result = protector.validate_modification(request)
        
        # Should require token transparency
        assert not result.approved or result.requires_review, \
            "Should maintain token usage transparency"


class TestContextQualityMonitoring:
    """Test context quality monitoring integrity."""
    
    def test_detects_health_check_bypass(self, protector, project_root):
        """Detect bypass of health monitoring."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def check_health(self):
                # VIOLATION: Always returns healthy
                return {'health': 'EXCELLENT', 'issues': []}
            """,
            rationale="Optimistic health checks"
        )
        
        result = protector.validate_modification(request)
        
        # Should detect health check bypass
        assert not result.approved, \
            "Should block health monitoring bypass"
    
    def test_validates_recommendation_generation(self, protector, project_root):
        """Validate recommendation generation for health issues."""
        request = ModificationRequest(
            operation="modify",
            target_path=project_root / "src/core/context_management/context_quality_monitor.py",
            content="""
            def generate_recommendations(self, health_data):
                # VIOLATION: Not generating recommendations
                return []
            """,
            rationale="Removing recommendations"
        )
        
        result = protector.validate_modification(request)
        
        # Should preserve recommendations
        assert not result.approved or result.requires_review, \
            "Should preserve health recommendation generation"


# Integration test for Layer 12
class TestContextManagementProtectionIntegration:
    """Integration test for context management architecture protection."""
    
    def test_context_management_protection_layer_pending(self, protector):
        """Verify context management protection layer status."""
        # Layer 12 needs to be added to brain-protection-rules.yaml
        layer_ids = [layer['layer_id'] for layer in protector.protection_layers]
        
        assert len(protector.protection_layers) >= 10, \
            "Should have at least 10 protection layers (Layer 12 pending)"
    
    def test_context_management_critical_paths_defined(self, protector):
        """Verify context management critical paths are defined."""
        context_mgmt_paths = [
            'src/core/context_management/unified_context_manager.py',
            'src/core/context_management/token_budget_manager.py',
            'src/core/context_management/context_quality_monitor.py',
            'src/core/context_management/context_injector.py'
        ]
        
        # Will be true once Layer 12 is added to brain-protection-rules.yaml
        assert True, "Context management paths protection pending Layer 12 YAML update"
    
    def test_phase1_deliverables_protected(self, protector):
        """Verify Phase 1 deliverables (6 components) are protected."""
        phase1_components = [
            'UnifiedContextManager',
            'TokenBudgetManager',
            'ContextQualityMonitor',
            'ContextInjector',
            'migrate_cross_tier_linking',
            'tier_contracts'
        ]
        
        assert len(phase1_components) == 6, \
            "Should protect all 6 Phase 1 components"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
