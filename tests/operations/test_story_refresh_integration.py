"""
Integration Tests for Story Refresh Operation

These tests implement SKULL-005 (Transformation Verification) by validating
that operations claiming transformation actually produce measurable changes.

Author: CORTEX Protection System
Version: 1.0
Created: 2025-11-10
"""

import pytest
import hashlib
import subprocess
from pathlib import Path
from src.operations import execute_operation
from src.config import config


class TestStoryRefreshIntegration:
    """
    Integration tests for refresh_cortex_story operation.
    
    SKULL-005 Enforcement:
    - Operations claiming transformation MUST produce file changes
    - Hash comparisons MUST show differences
    - Git diff MUST show modifications
    - No pass-through implementations allowed
    """
    
    def setup_method(self):
        """Setup test environment."""
        self.project_root = Path(config.get('project_root', Path.cwd()))
        self.story_source = self.project_root / "prompts" / "shared" / "story.md"
        self.story_output = self.project_root / "docs" / "awakening-of-cortex.md"
        
        # Ensure output file exists for testing
        if not self.story_output.exists():
            self.story_output.parent.mkdir(parents=True, exist_ok=True)
            self.story_output.write_text("# Placeholder\n\nTest content\n")
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of file contents."""
        if not file_path.exists():
            return "FILE_NOT_FOUND"
        return hashlib.md5(file_path.read_bytes()).hexdigest()
    
    def _git_diff_has_changes(self, file_path: Path) -> bool:
        """Check if git diff shows changes for file."""
        try:
            result = subprocess.run(
                ['git', 'diff', str(file_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            return len(result.stdout.strip()) > 0
        except Exception as e:
            pytest.skip(f"Git not available or error: {e}")
    
    def _check_for_mock_patterns(self, module_path: Path) -> list[str]:
        """Scan module for mock/stub patterns."""
        if not module_path.exists():
            return ["MODULE_NOT_FOUND"]
        
        content = module_path.read_text()
        mock_patterns = []
        
        # Check if module is explicitly marked as validation-only
        is_validation_only = (
            "VALIDATION-ONLY" in content or
            "validation-only" in content or
            "operation_type': 'validation'" in content or
            '"operation_type": "validation"' in content
        )
        
        # If explicitly marked as validation, pass-through is acceptable
        if is_validation_only:
            # Validation-only operations can copy input to output
            # This is honest behavior, not deceptive mocking
            return []
        
        # For operations claiming transformation, check for deceptive patterns
        
        # Check for pass-through pattern WITHOUT validation marking
        if "context['transformed_story'] = story_content" in content:
            if "transformation_applied'] = False" not in content:
                mock_patterns.append("PASS_THROUGH: Direct assignment without transformation (not marked as validation-only)")
        
        if "context['transformed_story'] = context['story_content']" in content:
            if "transformation_applied'] = False" not in content:
                mock_patterns.append("PASS_THROUGH: Direct context copy (not marked as validation-only)")
        
        # Check for TODO markers indicating incomplete transformation
        if "# TODO" in content and "transformation" in content.lower():
            if not is_validation_only:
                mock_patterns.append("TODO: Incomplete transformation logic")
        
        # Check for placeholder markers
        if "# PLACEHOLDER" in content or "# STUB" in content:
            mock_patterns.append("PLACEHOLDER: Stub implementation")
        
        # Check for deceptive claims (says transformation but is validation)
        if "transformation complete" in content.lower():
            if "VALIDATION-ONLY" not in content and "validation-only" not in content:
                mock_patterns.append("DECEPTIVE: Claims transformation but is validation-only")
        
        return mock_patterns
    
    # SKULL-005: File Hash Verification
    def test_story_refresh_changes_output_file(self):
        """
        SKULL-005 Requirement: File hash MUST change after transformation.
        
        This test ensures operations claiming transformation actually
        produce measurable changes to output files.
        """
        # Get hash before operation
        hash_before = self._compute_file_hash(self.story_output)
        
        # Execute story refresh operation
        report = execute_operation('refresh story')
        
        # Get hash after operation
        hash_after = self._compute_file_hash(self.story_output)
        
        # SKULL-005 ENFORCEMENT: Hashes MUST differ
        assert hash_before != hash_after, (
            f"SKULL-005 VIOLATION: Story refresh claims success but file unchanged!\n"
            f"Before: {hash_before}\n"
            f"After:  {hash_after}\n"
            f"Operation: {report.operation_id}\n"
            f"Status: {report.success}\n"
            f"This indicates a pass-through or no-op implementation."
        )
    
    # SKULL-005: Git Diff Verification
    def test_story_refresh_produces_git_diff(self):
        """
        SKULL-005 Requirement: git diff MUST show changes.
        
        Ensures operations actually modify tracked files, not just
        claim success without doing work.
        """
        # Execute story refresh operation
        report = execute_operation('refresh story')
        
        # Check if git diff shows changes
        has_changes = self._git_diff_has_changes(self.story_output)
        
        # SKULL-005 ENFORCEMENT: Must have git diff output
        assert has_changes, (
            f"SKULL-005 VIOLATION: Story refresh claims success but git diff empty!\n"
            f"Operation: {report.operation_id}\n"
            f"Output file: {self.story_output}\n"
            f"Status: {report.success}\n"
            f"Run 'git diff {self.story_output}' to verify.\n"
            f"This indicates the operation did nothing despite claiming success."
        )
    
    # SKULL-005: Mock Detection
    def test_apply_narrator_voice_not_passthrough(self):
        """
        SKULL-005 Requirement: No pass-through implementations.
        
        Scans the transformation module for pass-through patterns
        that copy input to output without actual transformation.
        """
        module_path = self.project_root / "src" / "operations" / "modules" / "apply_narrator_voice_module.py"
        
        mock_patterns = self._check_for_mock_patterns(module_path)
        
        # SKULL-005 ENFORCEMENT: No mock patterns allowed
        assert len(mock_patterns) == 0, (
            f"SKULL-005 VIOLATION: Mock/stub patterns detected in transformation module!\n"
            f"Module: {module_path.name}\n"
            f"Patterns found:\n" +
            "\n".join(f"  - {pattern}" for pattern in mock_patterns) +
            f"\n\nThis module claims to transform content but contains pass-through logic.\n"
            f"Either implement real transformation or mark as validation-only operation."
        )
    
    # SKULL-005: Operation Success Validation
    def test_operation_success_matches_actual_changes(self):
        """
        SKULL-005 Requirement: Success claims must match actual changes.
        
        Ensures operation reports success only when real work was done.
        """
        # Get hash before operation
        hash_before = self._compute_file_hash(self.story_output)
        
        # Execute operation
        report = execute_operation('refresh story')
        
        # Get hash after operation
        hash_after = self._compute_file_hash(self.story_output)
        
        # If operation claims success, changes MUST exist
        if report.success:
            actual_changes = (hash_before != hash_after)
            
            assert actual_changes, (
                f"SKULL-005 VIOLATION: Operation reports success=True but no changes!\n"
                f"Operation: {report.operation_id}\n"
                f"Modules executed: {len(report.modules_executed)}\n"
                f"Modules succeeded: {len(report.modules_succeeded)}\n"
                f"File hash unchanged: {hash_before}\n"
                f"\nThis is a FALSE SUCCESS - operation did nothing.\n"
                f"Fix by implementing real transformation or returning success=False."
            )
    
    # Content Validation
    def test_story_output_has_expected_sections(self):
        """
        Validate story output contains expected narrative sections.
        
        This ensures transformation produces valid content, not just
        any changes to pass hash tests.
        """
        # Execute operation
        report = execute_operation('refresh story')
        
        # Read output
        if not self.story_output.exists():
            pytest.fail("Story output file not created")
        
        content = self.story_output.read_text()
        
        # Validate key sections exist
        expected_sections = [
            "# CORTEX Story",
            "The Intern with Amnesia",
            "Dual-Hemisphere Brain Architecture",
            "LEFT HEMISPHERE",
            "RIGHT HEMISPHERE",
            "Four-Tier Memory System",
            "TIER 1",
            "TIER 2",
            "TIER 3"
        ]
        
        missing_sections = [
            section for section in expected_sections
            if section not in content
        ]
        
        assert len(missing_sections) == 0, (
            f"Story output missing expected sections:\n" +
            "\n".join(f"  - {section}" for section in missing_sections) +
            f"\n\nOutput file: {self.story_output}\n"
            f"This indicates incomplete or corrupted transformation."
        )
    
    # Module Execution Validation
    def test_all_story_modules_executed(self):
        """
        Validate all story refresh modules actually executed.
        
        Ensures orchestration works and all modules ran.
        """
        report = execute_operation('refresh story')
        
        expected_modules = [
            'load_story_template',
            'apply_narrator_voice',
            'validate_story_structure',
            'save_story_markdown'
        ]
        
        missing_modules = [
            mod for mod in expected_modules
            if mod not in report.modules_executed
        ]
        
        assert len(missing_modules) == 0, (
            f"Story refresh missing module executions:\n" +
            "\n".join(f"  - {mod}" for mod in missing_modules) +
            f"\n\nExecuted: {report.modules_executed}\n"
            f"This indicates orchestration failure."
        )
    
    # Error Handling
    def test_operation_handles_missing_source(self, tmp_path):
        """
        Test operation behavior when source file missing.
        
        Should fail gracefully, not claim success.
        """
        # Create isolated test with missing source
        fake_config = {
            'project_root': tmp_path
        }
        
        # Execute should fail or handle gracefully
        with pytest.raises(Exception) as exc_info:
            execute_operation('refresh story', **fake_config)
        
        # Validate it doesn't claim success with missing source
        assert "not found" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()


class TestMockDetectionForAllOperations:
    """
    Scan all production operations for mock/stub implementations.
    
    SKULL-005 Extension: Ensure no production operations use mock data.
    """
    
    def test_no_mocks_in_environment_setup(self):
        """Environment setup must use real implementations."""
        modules_dir = Path(__file__).parent.parent.parent / "src" / "operations" / "modules"
        
        setup_modules = [
            "platform_detection_module.py",
            "virtual_environment_module.py",
            "python_dependencies_module.py",
            "brain_initialization_module.py"
        ]
        
        for module_name in setup_modules:
            module_path = modules_dir / module_name
            if not module_path.exists():
                continue
            
            content = module_path.read_text()
            
            # Check for mock patterns
            mock_indicators = [
                "mock_",
                "Mock(",
                "PLACEHOLDER",
                "# TODO: Implement actual",
                "stub implementation",
                "pass-through"
            ]
            
            found_mocks = [
                indicator for indicator in mock_indicators
                if indicator in content
            ]
            
            assert len(found_mocks) == 0, (
                f"SKULL-005 VIOLATION: Production module contains mock patterns!\n"
                f"Module: {module_name}\n"
                f"Patterns: {found_mocks}\n"
                f"Environment setup is marked READY but uses mock data."
            )
    
    def test_no_mocks_in_demo_modules(self):
        """Demo modules should demonstrate real functionality."""
        modules_dir = Path(__file__).parent.parent.parent / "src" / "operations" / "modules"
        
        demo_modules = [
            "demo_introduction_module.py",
            "demo_help_system_module.py",
            "demo_story_refresh_module.py"
        ]
        
        for module_name in demo_modules:
            module_path = modules_dir / module_name
            if not module_path.exists():
                continue
            
            content = module_path.read_text()
            
            # Acceptable: Demo can SHOW mock data for illustration
            # Not acceptable: Demo USES mock data pretending to be real
            
            # Check for deceptive mocks (claiming real operation but using mock)
            if "execute_operation" in content and "mock" not in content.lower():
                # Demo calls real operation - good
                continue
            
            if "# Demonstration only" in content or "# Example output" in content:
                # Demo explicitly marked as illustration - acceptable
                continue
            
            # Check for deceptive patterns
            deceptive_patterns = [
                ("return True", "# Mock success"),  # Claims success with mock
                ("success=True", "mock")  # Success flag with mock data
            ]
            
            for pattern, context in deceptive_patterns:
                if pattern in content and context in content.lower():
                    pytest.fail(
                        f"SKULL-005 WARNING: Demo module may use deceptive mocks!\n"
                        f"Module: {module_name}\n"
                        f"Pattern: {pattern} with {context}\n"
                        f"Demo should either call real operations or clearly mark as illustration."
                    )


# Performance Tests (optional, for future enhancement)
class TestStoryRefreshPerformance:
    """
    Performance tests for story refresh operation.
    
    Ensures transformation completes within acceptable time.
    """
    
    @pytest.mark.slow
    def test_story_refresh_completes_within_5_seconds(self):
        """Story refresh should complete quickly."""
        import time
        
        start = time.time()
        report = execute_operation('refresh story')
        duration = time.time() - start
        
        assert duration < 5.0, (
            f"Story refresh too slow: {duration:.2f}s\n"
            f"Expected: <5.0s\n"
            f"Modules: {len(report.modules_executed)}\n"
            f"Investigate performance bottlenecks."
        )


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
