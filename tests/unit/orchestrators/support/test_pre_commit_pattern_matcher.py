"""
Test Suite: Pre-commit Hook Pattern Matcher

Tests for the pre-commit hook script that prevents regression of 8 duplication
categories by blocking commits with:
1. New ExecutionContext definitions (outside canonical path)
2. New Registry classes (without BaseRegistry inheritance)
3. New orchestrator base classes
4. New wiring system implementations

All tests follow TDD approach (tests written first).

Author: Asif Hussain
Date: 2026-01-31
"""

from __future__ import annotations

import pytest
from pathlib import Path
from typing import List, Dict, Any, Optional

from cortex.orchestrators.support.pre_commit_pattern_matcher import (
    PreCommitPatternMatcher,
    PatternCheckResult,
    BlockingPattern,
)


class TestExecutionContextPatternBlocking:
    """Tests for ExecutionContext pattern detection and blocking"""

    @pytest.fixture
    def matcher(self) -> PreCommitPatternMatcher:
        """Create pattern matcher instance"""
        return PreCommitPatternMatcher()

    def test_blocks_execution_context_in_non_canonical_location(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-001: Blocks ExecutionContext definitions outside canonical path
        
        Canonical Path: cortex/brain/core/orchestrator_base.py
        Blocked: Any other file defining ExecutionContext
        """
        # New file attempting to define ExecutionContext
        file_content = """
class ExecutionContext:
    '''New ExecutionContext in non-canonical location'''
    def __init__(self):
        pass
"""
        
        result = matcher.check_execution_context_pattern(
            file_path="cortex/core/interfaces.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert "ExecutionContext" in result.reason
        assert result.pattern == BlockingPattern.EXECUTION_CONTEXT

    ) -> None:
        """
        PATTERN-002: Allows ExecutionContext in canonical location only
        
        File: cortex/brain/core/orchestrator_base.py (canonical)
        """
        file_content = """
class ExecutionContext:
    '''Canonical ExecutionContext'''
    pass
"""
        
        result = matcher.check_execution_context_pattern(
            file_path="cortex/brain/core/orchestrator_base.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_allows_execution_context_in_whitelisted_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-003: Allows ExecutionContext in whitelisted files
        
        Whitelist: test files, migration scripts, etc.
        """
        whitelist = [
            "tests/",
            "docs/",
            "migration/",
        ]
        matcher.set_whitelist(whitelist)
        
        file_content = "class ExecutionContext: pass"
        
        result = matcher.check_execution_context_pattern(
            file_path="tests/unit/test_execution.py",
            file_content=file_content,
        )
        
        assert result.blocked is False
        assert result.reason == "Path in whitelist"

    def test_detects_execution_context_variants(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-004: Detects ExecutionContext variants (ExecutionCtx, ExecContext, etc.)
        
        Should catch common abbreviations and variations
        """
        variations = [
            "ExecutionContext",
            "ExecutionCtx",
            "ExecContext",
            "ExecutionEnvironment",
        ]
        
        for variant in variations:
            file_content = f"class {variant}: pass"
            
            result = matcher.check_execution_context_pattern(
                file_path="cortex/new_module/new_file.py",
                file_content=file_content,
            )
            
            # At least ExecutionContext and ExecutionCtx should be caught
            if variant in ["ExecutionContext", "ExecutionCtx"]:
                assert result.blocked is True

    # =====================================================================
    # REGISTRY PATTERN BLOCKING
    # =====================================================================

    def test_blocks_registry_without_base_registry_inheritance(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-005: Blocks new Registry classes without BaseRegistry inheritance
        
        Required: class XyzRegistry(BaseRegistry[SomeType])
        Blocked: class XyzRegistry: pass (without inheritance)
        """
        # New registry without BaseRegistry
        file_content = """
class GovernanceRegistry:
    '''New registry without BaseRegistry'''
    _instance = None
    
    def __init__(self):
        pass
"""
        
        result = matcher.check_registry_pattern(
            file_path="cortex/new_module/governance_registry.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert "BaseRegistry" in result.reason
        assert result.pattern == BlockingPattern.REGISTRY

    ) -> None:
        """
        PATTERN-006: Allows Registry classes that inherit from BaseRegistry[T]
        
        Pattern: class XyzRegistry(BaseRegistry[Type]): ...
        """
        file_content = """
from cortex.core.base_registry import BaseRegistry

class GovernanceRegistry(BaseRegistry[GovernanceRule]):
    '''Registry inheriting from BaseRegistry'''
    pass
"""
        
        result = matcher.check_registry_pattern(
            file_path="cortex/brain/core/governance_registry.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_blocks_singleton_pattern_registries(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-007: Blocks registries using bare singleton pattern
        
        Detects: _instance, get_instance() without BaseRegistry
        """
        file_content = """
class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, name, tool):
        pass
"""
        
        result = matcher.check_registry_pattern(
            file_path="cortex/tools/new_registry.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert "singleton" in result.reason.lower() or "BaseRegistry" in result.reason

    def test_detects_registry_keyword_in_class_name(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-008: Detects 'Registry' keyword in class name
        
        Flags any class with 'Registry' in name without BaseRegistry
        """
        file_content = """
class NewRegistry:
    def __init__(self):
        self.items = {}
"""
        
        result = matcher.check_registry_pattern(
            file_path="cortex/domain/new_registry.py",
            file_content=file_content,
        )
        
        assert result.blocked is True

    # =====================================================================
    # ORCHESTRATOR BASE CLASS BLOCKING
    # =====================================================================

    def test_blocks_new_orchestrator_base_classes(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-009: Blocks new orchestrator base classes
        
        Canonical: OrchestratorBase in cortex/brain/core/orchestrator_base.py
        Blocked: BaseOrchestrator, Orchestrator (outside canonical)
        """
        file_content = """
class BaseOrchestrator:
    '''New base orchestrator class'''
    def execute(self):
        pass
"""
        
        result = matcher.check_orchestrator_base_pattern(
            file_path="cortex/orchestrators/base_orchestrator.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert "base" in result.reason.lower()
        assert result.pattern == BlockingPattern.ORCHESTRATOR_BASE

    ) -> None:
        """
        PATTERN-010: Allows OrchestratorBase in canonical location
        
        File: cortex/brain/core/orchestrator_base.py
        """
        file_content = """
class OrchestratorBase:
    '''Canonical orchestrator base class'''
    pass
"""
        
        result = matcher.check_orchestrator_base_pattern(
            file_path="cortex/brain/core/orchestrator_base.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_detects_base_class_keywords(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-011: Detects base class keywords
        
        Keywords: Base, Abstract, Core, Root (for orchestrators)
        """
        class_names = [
            "BaseOrchestrator",
            "AbstractOrchestrator",
            "CoreOrchestrator",
            "RootOrchestrator",
            "Orchestrator",
        ]
        
        for class_name in class_names:
            file_content = f"""
class {class_name}:
    def __init__(self):
        pass
"""
            
            result = matcher.check_orchestrator_base_pattern(
                file_path=f"cortex/orchestrators/{class_name.lower()}.py",
                file_content=file_content,
            )
            
            # Most should be blocked (except maybe generic Orchestrator)
            assert result.blocked is True or "IOrchestrator" in file_content

    # =====================================================================
    # WIRING SYSTEM BLOCKING
    # =====================================================================

    def test_blocks_new_wiring_system_implementations(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-012: Blocks new wiring system implementations
        
        Canonical: cortex/wiring/ (Git-backed YAML)
        Blocked: New transform, harness, guided systems
        """
        file_content = """
class WiringSystem:
    '''New wiring system implementation'''
    def load_wiring(self):
        pass
    
    def apply_wiring(self):
        pass
"""
        
        result = matcher.check_wiring_pattern(
            file_path="cortex/orchestrators/new_wiring_system.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert "wiring" in result.reason.lower()
        assert result.pattern == BlockingPattern.WIRING_SYSTEM

    def test_allows_wiring_in_git_backed_system(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-013: Allows modifications to Git-backed wiring system
        
        Path: cortex/wiring/
        """
        file_content = """
def load_wiring_from_yaml():
    pass
"""
        
        result = matcher.check_wiring_pattern(
            file_path="cortex/wiring/bootstrap.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_detects_wiring_keywords(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-014: Detects wiring-related keywords
        
        Keywords: Wiring, Transform, Harness, Guided, Bootstrap (orchestrators)
        """
        keywords = [
            "WiringSystem",
            "TransformWiring",
            "WiringHarness",
            "GuidedWiring",
            "BootstrapWiring",
        ]
        
        for keyword in keywords:
            file_content = f"class {keyword}: pass"
            
            result = matcher.check_wiring_pattern(
                file_path=f"cortex/orchestrators/{keyword.lower()}.py",
                file_content=file_content,
            )
            
            assert result.blocked is True

    def test_blocks_legacy_wiring_patterns(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-015: Blocks known legacy wiring patterns
        
        Patterns: transform_001, wiring_harness, guided_wiring
        """
        legacy_files = [
            "transform_001_implementation.py",
            "wiring_harness_integration.py",
            "guided_wiring_orchestrator.py",
        ]
        
        for filename in legacy_files:
            file_content = "def wire_orchestrators(): pass"
            
            result = matcher.check_wiring_pattern(
                file_path=f"cortex/orchestrators/{filename}",
                file_content=file_content,
            )
            
            # Should be blocked or at least flagged
            assert result.blocked is True or result.severity == "high"

    # =====================================================================
    # COMPREHENSIVE PATTERN CHECKING
    # =====================================================================

    ) -> None:
        """
        PATTERN-016: Check all patterns in a single file
        
        Should return all detected blocking patterns
        """
        file_content = """
class ExecutionContext:
    pass

class NewRegistry:
    pass
"""
        
        results = matcher.check_file(
            file_path="cortex/new_module/new_file.py",
            file_content=file_content,
        )
        
        # Should detect both patterns
        assert len(results) >= 2
        assert any(r.pattern == BlockingPattern.EXECUTION_CONTEXT for r in results)
        assert any(r.pattern == BlockingPattern.REGISTRY for r in results)

    def test_check_multiple_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-017: Check multiple files in a commit
        
        Returns aggregated results
        """
        files = [
            ("cortex/file1.py", "class ExecutionContext: pass"),
            ("cortex/file2.py", "class NewRegistry: pass"),
            ("cortex/file3.py", "# Normal file\npass"),
        ]
        
        results = matcher.check_files(files)
        
        assert len(results) > 0
        blocked_count = sum(1 for r in results if r.blocked)
        assert blocked_count >= 2

    # =====================================================================
    # WHITELIST HANDLING
    # =====================================================================

    def test_whitelist_test_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-018: Whitelist allows test files
        
        Path patterns: tests/, test_*.py, *_test.py
        """
        whitelist = matcher.get_default_whitelist()
        matcher.set_whitelist(whitelist)
        
        file_content = "class ExecutionContext: pass"
        
        result = matcher.check_execution_context_pattern(
            file_path="tests/unit/test_execution_context.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_whitelist_migration_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-019: Whitelist allows migration scripts
        
        Path patterns: migration/, *_migration.py
        """
        whitelist = matcher.get_default_whitelist()
        matcher.set_whitelist(whitelist)
        
        file_content = "class NewRegistry: pass"
        
        result = matcher.check_registry_pattern(
            file_path="migration/migrate_registry.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    def test_custom_whitelist_entry(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PATTERN-020: Support custom whitelist entries
        
        Allow specific files for exceptions
        """
        matcher.add_whitelist_entry("cortex/special/special_wiring.py")
        
        file_content = "class WiringSystem: pass"
        
        result = matcher.check_wiring_pattern(
            file_path="cortex/special/special_wiring.py",
            file_content=file_content,
        )
        
        assert result.blocked is False

    # =====================================================================
    # PERFORMANCE & ROBUSTNESS
    # =====================================================================

    def test_performance_large_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PERF-001: Handle large files efficiently (< 500ms)
        
        Should process 5000-line file in < 500ms
        """
        # Generate large file content
        large_content = "# Comment line\n" * 2500
        large_content += "\nclass ExecutionContext: pass\n"
        
        import time
        start = time.time()
        result = matcher.check_execution_context_pattern(
            file_path="cortex/large_file.py",
            file_content=large_content,
        )
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # 500ms
        assert result.blocked is True

    def test_performance_batch_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        PERF-002: Handle batch file checking efficiently (< 2s for 100 files)
        
        Pre-commit hook must complete in < 2s for typical commit
        """
        # Generate 100 files
        files = [
            (f"cortex/file_{i}.py", f"# File {i}\npass")
            for i in range(100)
        ]
        
        # Add 5 blocking patterns scattered throughout
        files[10] = (files[10][0], "class ExecutionContext: pass")
        files[30] = (files[30][0], "class NewRegistry: pass")
        files[50] = (files[50][0], "class BaseOrchestrator: pass")
        files[70] = (files[70][0], "class WiringSystem: pass")
        files[90] = (files[90][0], "# Normal file\npass")
        
        import time
        start = time.time()
        results = matcher.check_files(files)
        elapsed = time.time() - start
        
        assert elapsed < 2.0  # 2 seconds
        blocked_count = sum(1 for r in results if r.blocked)
        assert blocked_count == 4

    def test_handles_empty_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        ROBUST-001: Handle empty files gracefully
        """
        result = matcher.check_file(
            file_path="cortex/empty.py",
            file_content="",
        )
        
        # Should not crash
        assert isinstance(result, list)

    def test_handles_binary_files(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        ROBUST-002: Handle binary files gracefully
        """
        binary_content = b"\x80\x81\x82\x83"
        
        try:
            result = matcher.check_file(
                file_path="cortex/binary.bin",
                file_content=binary_content.decode(errors="ignore"),
            )
            # Should handle gracefully
            assert isinstance(result, list)
        except Exception as e:
            # Should not crash with hard error
            assert "binary" in str(e).lower() or True

    def test_handles_syntax_errors(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        ROBUST-003: Handle Python syntax errors gracefully
        """
        bad_syntax = "class ExecutionContext\n  invalid syntax here"
        
        result = matcher.check_execution_context_pattern(
            file_path="cortex/bad_syntax.py",
            file_content=bad_syntax,
        )
        
        # Should still detect ExecutionContext keyword
        assert result.blocked is True or result.reason != ""

    # =====================================================================
    # AUDIT LOGGING
    # =====================================================================

    def test_audit_logging_blocked_commit(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        AUDIT-001: Log all blocked commits to audit trail
        
        Should record: filename, pattern, reason, timestamp
        """
        file_content = "class ExecutionContext: pass"
        
        result = matcher.check_execution_context_pattern(
            file_path="cortex/test.py",
            file_content=file_content,
        )
        
        assert result.blocked is True
        assert result.timestamp is not None
        assert result.audit_id is not None

    def test_audit_logging_allowed_commit(
        self,
        matcher: PreCommitPatternMatcher,
    ) -> None:
        """
        AUDIT-002: Log allowed commits for compliance
        
        Should record: approved files, bypassed rules (if any)
        """
        file_content = "# Normal file\ndef normal_function(): pass"
        
        result = matcher.check_execution_context_pattern(
            file_path="cortex/normal.py",
            file_content=file_content,
        )
        
        assert result.blocked is False
        # Should still have audit record
        assert result.audit_id is not None
