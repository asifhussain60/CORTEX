"""
IntentRouter VACUUM Operation Detection Tests

Tests for enhanced IntentRouter that routes vacuum/cleanup requests
to the VacuumOrchestrator for efficient CORTEX repository cleanup.
"""
import pytest
from cortex.orchestrators.core.intent_router import IntentRouter
from cortex.models.canonical_enums import IntentType


class TestVacuumKeywordRecognition:
    """Test: VACUUM keyword recognition in IntentRouter"""

    def test_vacuum_keywords_defined(self):
        """Test: VACUUM_KEYWORDS constant is defined"""
        router = IntentRouter()
        
        assert hasattr(router, 'VACUUM_KEYWORDS'), "VACUUM_KEYWORDS must be defined"
        assert len(router.VACUUM_KEYWORDS) > 0, "VACUUM_KEYWORDS must not be empty"

    def test_vacuum_keywords_content(self):
        """Test: VACUUM_KEYWORDS includes core vacuum terms"""
        router = IntentRouter()
        
        # Check for core vacuum keywords
        assert "vacuum" in router.VACUUM_KEYWORDS, "Must include 'vacuum'"
        assert "cleanup" in router.VACUUM_KEYWORDS, "Must include 'cleanup'"
        assert "clean" in router.VACUUM_KEYWORDS, "Must include 'clean'"
        assert "prune" in router.VACUUM_KEYWORDS, "Must include 'prune'"

    def test_vacuum_keywords_include_cleanup_variants(self):
        """Test: VACUUM_KEYWORDS includes cleanup operation variants"""
        router = IntentRouter()
        
        keywords_str = " ".join(router.VACUUM_KEYWORDS).lower()
        
        # Check for cleanup-related keywords
        cleanup_terms = ["remove", "delete", "cache", "logs", "artifacts", "temp"]
        assert any(term in keywords_str for term in cleanup_terms), \
            "Must include cleanup-related operations"


class TestVacuumOperationDetection:
    """Test: VACUUM operation detection in requests"""

    def test_is_vacuum_operation_method_exists(self):
        """Test: _is_vacuum_operation method exists"""
        router = IntentRouter()
        
        assert hasattr(router, '_is_vacuum_operation'), "_is_vacuum_operation method required"
        assert callable(router._is_vacuum_operation), "_is_vacuum_operation must be callable"

    def test_detect_vacuum_cleanup_request(self):
        """Test: Detects 'vacuum cleanup' request"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("use vacuum to cleanup the cortex repo")
        assert result is True, "Should detect vacuum cleanup request"

    def test_detect_efficient_cleanup_request(self):
        """Test: Detects 'efficient cleanup' request"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("perform efficient cleanup in cortex environment")
        assert result is True, "Should detect efficient cleanup request"

    def test_detect_prune_request(self):
        """Test: Detects 'prune' request"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("please prune the repository")
        assert result is True, "Should detect prune request"

    def test_not_vacuum_implement_request(self):
        """Test: Does not detect non-vacuum IMPLEMENT request"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("implement new feature")
        assert result is False, "Should not detect non-vacuum request"

    def test_not_vacuum_fix_request(self):
        """Test: Does not detect non-vacuum FIX request"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("fix the bug in the code")
        assert result is False, "Should not detect non-vacuum request"


class TestVacuumIntentDetection:
    """Test: VACUUM intent detection in detect_intent method"""

    def test_detect_intent_with_vacuum_keyword(self):
        """Test: detect_intent recognizes vacuum keyword"""
        router = IntentRouter()
        
        context = {
            "operation": "cleanup",
            "description": "use vacuum to cleanup the repo efficiently"
        }
        
        # Should detect REFACTOR intent (since VACUUM doesn't exist as IntentType)
        # but mark is_vacuum_operation flag
        intent = router.detect_intent(context)
        
        # VACUUM operations should be mapped to REFACTOR (cleanup is a type of refactor)
        assert intent == IntentType.REFACTOR, "VACUUM should map to REFACTOR intent"
        assert context.get("is_vacuum_operation") is True, "Should set is_vacuum_operation flag"

    def test_detect_intent_cleanup_keyword(self):
        """Test: detect_intent recognizes cleanup keyword"""
        router = IntentRouter()
        
        context = {
            "operation": "cleanup_temp_files",
            "description": "cleanup old temporary files from the environment"
        }
        
        intent = router.detect_intent(context)
        assert context.get("is_vacuum_operation") is True, "Should detect cleanup operation"

    def test_vacuum_higher_priority_than_refactor(self):
        """Test: VACUUM is detected before standard REFACTOR keywords"""
        router = IntentRouter()
        
        # Context with both vacuum AND refactor keywords
        context = {
            "description": "vacuum the repo and simplify the code structure"
        }
        
        intent = router.detect_intent(context)
        # Should detect vacuum first (higher priority)
        assert context.get("is_vacuum_operation") is True, "VACUUM should have priority"


class TestVacuumRoutingTargeting:
    """Test: VACUUM operations route to VacuumOrchestrator"""

    def test_routing_decision_identifies_vacuum(self):
        """Test: Routing decision metadata includes vacuum operation flag"""
        router = IntentRouter()
        
        context = {
            "operation": "cortex_vacuum",
            "description": "vacuum cortex repository"
        }
        
        # Route should create decision with is_vacuum_operation flag
        intent = router.detect_intent(context)
        assert context.get("is_vacuum_operation") is True

    def test_vacuum_operation_context_flag(self):
        """Test: is_vacuum_operation flag is properly set in context"""
        router = IntentRouter()
        
        context = {
            "operation": "repo_cleanup",
            "description": "remove all artifacts using vacuum"
        }
        
        router.detect_intent(context)
        assert "is_vacuum_operation" in context, "Flag should be in context"
        assert context["is_vacuum_operation"] is True, "Flag should be True"

    def test_vacuum_operation_metadata(self):
        """Test: VACUUM operations include metadata about cleanup type"""
        router = IntentRouter()
        
        context = {
            "operation": "vacuum_logs",
            "description": "vacuum repository and remove old logs"
        }
        
        intent = router.detect_intent(context)
        assert context.get("is_vacuum_operation") is True
        
        # Additional metadata could be added to context
        if "cleanup_type" in context:
            assert context["cleanup_type"] in ["logs", "cache", "artifacts", "temp"]


class TestVacuumKeywordVariants:
    """Test: Various VACUUM keyword variants are recognized"""

    def test_vacuum_exact_match(self):
        """Test: 'vacuum' keyword matches exactly"""
        router = IntentRouter()
        assert router._is_vacuum_operation("vacuum the repo") is True

    def test_cortex_vacuum_phrase(self):
        """Test: 'cortex vacuum' phrase matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("cortex vacuum") is True

    def test_vacuum_repo_phrase(self):
        """Test: 'vacuum repo' phrase matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("vacuum repo") is True

    def test_cleanup_phrase(self):
        """Test: 'cleanup' phrase matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("cleanup old files") is True

    def test_clean_up_two_words(self):
        """Test: 'clean up' (two words) matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("clean up temp artifacts") is True

    def test_prune_operation(self):
        """Test: 'prune' keyword matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("prune the repository") is True

    def test_remove_junk_phrase(self):
        """Test: 'remove junk' phrase matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("remove junk files") is True

    def test_archive_operation(self):
        """Test: 'archive' keyword matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("archive old code") is True

    def test_garbage_collection(self):
        """Test: 'garbage collection' phrase matches"""
        router = IntentRouter()
        assert router._is_vacuum_operation("garbage collection cleanup") is True


class TestVacuumOperationIntegration:
    """Integration Tests: VACUUM operations end-to-end"""

    def test_vacuum_request_full_flow(self):
        """Test: Full flow of vacuum request detection and routing"""
        router = IntentRouter()
        
        # User request: "use vacuum to cleanup CORTEX repo efficiently"
        context = {
            "operation": "vacuum_cortex",
            "description": "use vacuum to cleanup cortex repo in my environment for efficient storage",
            "keywords": ["vacuum", "cleanup", "efficient", "cortex", "repo"]
        }
        
        # Detect intent
        intent = router.detect_intent(context)
        
        # Should be marked as vacuum operation
        assert context.get("is_vacuum_operation") is True, "Should detect vacuum operation"

    def test_cleanup_different_contexts(self):
        """Test: VACUUM detection works in different contexts"""
        router = IntentRouter()
        
        test_cases = [
            "vacuum cleanup of cortex environment",
            "clean up the repository artifacts",
            "prune old code and dependencies",
            "run vacuum on the cortex repo",
            "efficient cleanup process",
        ]
        
        for test_case in test_cases:
            context = {"description": test_case}
            intent = router.detect_intent(context)
            assert context.get("is_vacuum_operation") is True, \
                f"Should detect vacuum in: {test_case}"


class TestVacuumNonMatchCases:
    """Test: VACUUM does not match non-vacuum requests"""

    def test_no_match_implement_request(self):
        """Test: IMPLEMENT request not detected as VACUUM"""
        router = IntentRouter()
        
        context = {"description": "create new feature for storage"}
        result = router._is_vacuum_operation("create new feature for storage")
        assert result is False, "IMPLEMENT request should not match vacuum"

    def test_no_match_refactor_request(self):
        """Test: REFACTOR request without vacuum keywords not detected"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("refactor the code structure")
        assert result is False, "Generic refactor should not match vacuum"

    def test_no_match_fix_request(self):
        """Test: FIX request not detected as VACUUM"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("fix the storage method")
        assert result is False, "FIX request should not match vacuum"

    def test_no_match_empty_string(self):
        """Test: Empty string does not match"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("")
        assert result is False, "Empty string should not match"

    def test_no_match_unrelated_keywords(self):
        """Test: Unrelated keywords do not trigger vacuum"""
        router = IntentRouter()
        
        result = router._is_vacuum_operation("implement authentication mechanism")
        assert result is False, "Unrelated keywords should not match"


class TestVacuumOrchestrationRouting:
    """Test: VACUUM operations route correctly"""

    def test_vacuum_sets_context_flag(self):
        """Test: VACUUM detection sets context flag for routing"""
        router = IntentRouter()
        
        context = {
            "operation": "cortex_vacuum",
            "description": "vacuum cortex repo"
        }
        
        router.detect_intent(context)
        
        # Flag should be set for downstream routing logic
        assert "is_vacuum_operation" in context
        assert context["is_vacuum_operation"] is True

    def test_vacuum_operation_preserved_in_context(self):
        """Test: VACUUM operation flag is preserved through routing"""
        router = IntentRouter()
        
        context = {
            "operation": "repo_cleanup",
            "description": "run vacuum to cleanup cortex efficiently"
        }
        
        original_context = context.copy()
        router.detect_intent(context)
        
        # Original operation preserved
        assert context.get("operation") == original_context["operation"]
        # But vacuum flag added
        assert context.get("is_vacuum_operation") is True
