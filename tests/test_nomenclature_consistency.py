"""
Test suite for nomenclature consistency across CORTEX registry, prompts, and agents.

Authority: CORE-042 (Hierarchical Terminology)
Purpose: Ensure EPIC→FEATURE→PHASE→STAGE→TASK hierarchy is consistent
Status: RED (expected to fail until cleanup complete)
"""

import pytest
import re
from pathlib import Path
from typing import List, Dict, Tuple


# AC_START: AC-NOMENCLATURE-001
# Description: Validate hierarchical terminology consistency


class TestNomenclatureConsistency:
    """Test nomenclature consistency across CORTEX system."""
    
    @pytest.fixture
    def registry_root(self) -> Path:
        """Return path to cortex-registry/_cortex-master."""
        return Path(__file__).parent.parent / "cortex-registry" / "_cortex-master"
    
    @pytest.fixture
    def prompts_root(self) -> Path:
        """Return path to .github/prompts."""
        return Path(__file__).parent.parent / ".github" / "prompts"
    
    @pytest.fixture
    def agents_root(self) -> Path:
        """Return path to .github/agents."""
        return Path(__file__).parent.parent / ".github" / "agents"
    
    def scan_for_pattern(
        self, 
        root: Path, 
        pattern: str, 
        extensions: List[str] = None,
        exclude_dirs: List[str] = None
    ) -> List[Tuple[Path, int, str]]:
        """
        Scan directory for regex pattern.
        
        Args:
            root: Root directory to scan
            pattern: Regex pattern to search for
            extensions: File extensions to include (e.g., ['.md', '.yaml'])
            exclude_dirs: Directory names to exclude (e.g., ['archive', '.archive'])
        
        Returns:
            List of (file_path, line_number, line_content) tuples
        """
        if not root.exists():
            return []
        
        extensions = extensions or ['.md', '.yaml', '.yml', '.txt']
        exclude_dirs = exclude_dirs or ['archive', '.archive', '_archive']
        
        matches = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for file_path in root.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Only scan specified file types
            if file_path.suffix not in extensions:
                continue
            
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, start=1):
                            if regex.search(line):
                                matches.append((file_path, line_num, line.strip()))
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return matches
    
    def test_no_wave_references_in_active_registry(self, registry_root: Path):
        """
        Test: Active registry files should not reference 'wave' terminology.
        
        CORE-042: PHASE→STAGE→TASK hierarchy
        Exceptions: Historical markers (LEGACY-WAVE-*, legacy_wave:), documentation about migration
        """
        # Pattern matches: wave, Wave, WAVE, wave-1, WAVE-1, etc.
        # Excludes: waveform, wavelength (compound words)
        pattern = r'\b[Ww]ave(?:[-\s]\d+|[-\s][A-Z]+)?\b'
        
        matches = self.scan_for_pattern(
            registry_root, 
            pattern,
            exclude_dirs=['archive', '.archive', '_archive', 'obsolete']
        )
        
        # Filter out acceptable historical references
        unacceptable = []
        for file_path, line_num, line_content in matches:
            # Allow historical markers
            if 'LEGACY-WAVE' in line_content or 'legacy_wave:' in line_content:
                continue
            # Allow documentation about migration
            if 'historical wave' in line_content.lower() or 'deprecated wave' in line_content.lower():
                continue
            # Allow references in migration/realignment docs
            if 'realign' in str(file_path).lower() or 'migration' in str(file_path).lower():
                continue
            unacceptable.append((file_path, line_num, line_content))
        
        if unacceptable:
            error_msg = "\n❌ Found unacceptable 'wave' references in active registry:\n"
            for file_path, line_num, line_content in unacceptable[:10]:
                rel_path = file_path.relative_to(registry_root)
                error_msg += f"  {rel_path}:{line_num} → {line_content[:80]}\n"
            
            if len(unacceptable) > 10:
                error_msg += f"  ... and {len(unacceptable) - 10} more matches\n"
            
            pytest.fail(error_msg)
    
    def test_no_wave_references_in_prompts(self, prompts_root: Path):
        """
        Test: Active prompt files should not reference 'wave' terminology.
        
        Exception: Historical archive files (WAVE-7-COMPLETION-SUMMARY.txt), migration documentation
        """
        pattern = r'\b[Ww]ave(?:[-\s]\d+|[-\s][A-Z]+)?\b'
        
        matches = self.scan_for_pattern(
            prompts_root, 
            pattern,
            exclude_dirs=['archive', '.archive']
        )
        
        # Filter out explicitly allowed files and content
        allowed_files = ['WAVE-7-COMPLETION-SUMMARY.txt', 'REGISTRY-REALIGNMENT-PLAN.md']
        unacceptable = []
        
        for file_path, line_num, line_content in matches:
            # Allow specific historical files
            if file_path.name in allowed_files:
                continue
            # Allow historical markers
            if 'LEGACY-WAVE' in line_content or 'legacy-wave' in line_content:
                continue
            # Allow documentation about migration
            if 'historical wave' in line_content.lower() or 'deprecated wave' in line_content.lower():
                continue
            unacceptable.append((file_path, line_num, line_content))
        
        if unacceptable:
            error_msg = "\n❌ Found unacceptable 'wave' references in active prompts:\n"
            for file_path, line_num, line_content in unacceptable[:10]:
                rel_path = file_path.relative_to(prompts_root)
                error_msg += f"  {rel_path}:{line_num} → {line_content[:80]}\n"
            
            if len(unacceptable) > 10:
                error_msg += f"  ... and {len(unacceptable) - 10} more matches\n"
            
            pytest.fail(error_msg)
    
    def test_no_wave_references_in_agents(self, agents_root: Path):
        """
        Test: Agent files should not reference 'wave' terminology.
        
        Exception: phase_group, __phase_obj variables (refactored equivalents)
        """
        pattern = r'\b[Ww]ave(?:[-\s]\d+|[-\s][A-Z]+)?\b'
        
        matches = self.scan_for_pattern(
            agents_root, 
            pattern,
            exclude_dirs=['archive', '.archive', 'archived']
        )
        
        # Filter out acceptable refactored references
        unacceptable = []
        for file_path, line_num, line_content in matches:
            # Allow phase_group (refactored wave concept)
            if 'phase_group' in line_content:
                continue
            # Allow __phase_obj (refactored wave variable)
            if '__phase_obj' in line_content:
                continue
            # Allow documentation about historical structure
            if 'historical' in line_content.lower() or 'legacy' in line_content.lower():
                continue
            # Allow guide files documenting migration
            if 'guide' in str(file_path).lower() and 'cleanup' in str(file_path).lower():
                continue
            unacceptable.append((file_path, line_num, line_content))
        
        if unacceptable:
            error_msg = "\n❌ Found unacceptable 'wave' references in agent files:\n"
            for file_path, line_num, line_content in unacceptable[:10]:
                rel_path = file_path.relative_to(agents_root)
                error_msg += f"  {rel_path}:{line_num} → {line_content[:80]}\n"
            
            if len(unacceptable) > 10:
                error_msg += f"  ... and {len(unacceptable) - 10} more matches\n"
            
            pytest.fail(error_msg)
    
    def test_initiative_replaced_with_epic(self, registry_root: Path, prompts_root: Path):
        """
        Test: 'INITIATIVE' terminology should be replaced with 'EPIC'.
        
        Exception: Historical references in context (e.g., "Initiative: Post-Production...")
        Expected: FAIL (RED) - initiative references currently exist
        """
        pattern = r'\bINITIATIVE→'
        
        # Check registry
        registry_matches = self.scan_for_pattern(
            registry_root, 
            pattern,
            exclude_dirs=['archive', '.archive', '_archive']
        )
        
        # Check prompts
        prompt_matches = self.scan_for_pattern(
            prompts_root, 
            pattern,
            exclude_dirs=['archive', '.archive']
        )
        
        all_matches = registry_matches + prompt_matches
        
        if all_matches:
            error_msg = "\n❌ Found 'INITIATIVE→' (should be 'EPIC→'):\n"
            for file_path, line_num, line_content in all_matches[:10]:
                error_msg += f"  {file_path}:{line_num} → {line_content[:80]}\n"
            
            pytest.fail(error_msg)
    
    def test_hierarchy_consistency_in_core_files(self, prompts_root: Path):
        """
        Test: CORE-042 should specify PHASE→STAGE→TASK (simplified hierarchy).
        
        Authority: CORE-042 explicitly states "Simple, universal. No wave/epic/feature concepts."
        Expected: PASS (GREEN) - should show PHASE→STAGE→TASK
        """
        copilot_instructions = prompts_root.parent / "copilot-instructions.md"
        
        if not copilot_instructions.exists():
            pytest.skip("copilot-instructions.md not found")
        
        with open(copilot_instructions, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have PHASE→STAGE→TASK (simplified)
        expected_pattern = r'PHASE→STAGE→TASK'
        
        # Should explicitly say "No wave/epic/feature concepts"
        no_concepts_pattern = r'No wave/epic/feature concepts'
        
        # Should NOT have INITIATIVE→PHASE
        incorrect_pattern = r'INITIATIVE.*?→.*?PHASE'
        
        has_correct = re.search(expected_pattern, content)
        has_no_concepts = re.search(no_concepts_pattern, content)
        has_incorrect = re.search(incorrect_pattern, content)
        
        if has_incorrect or not has_correct:
            pytest.fail(
                "❌ CORE-042 should specify PHASE→STAGE→TASK hierarchy (simplified), "
                f"but found incorrect hierarchy. Has correct: {has_correct is not None}, "
                f"Has 'no concepts': {has_no_concepts is not None}, "
                f"Has incorrect: {has_incorrect is not None}"
            )
    
    def test_prefix_consistency(self, registry_root: Path):
        """
        Test: Phase files should use P- prefix consistently.
        
        Exception: Historical archive files
        Expected: PASS (GREEN) - this should already be consistent
        """
        phase_files = list((registry_root / "phases").glob("*.yaml"))
        
        incorrect_prefixes = []
        for phase_file in phase_files:
            if not phase_file.stem[0].isdigit() and not phase_file.stem.startswith('P-'):
                incorrect_prefixes.append(phase_file.name)
        
        if incorrect_prefixes:
            pytest.fail(
                f"❌ Phase files should use P- prefix or numeric: {incorrect_prefixes}"
            )


# AC_COMPLETE: AC-NOMENCLATURE-001 ✅ Test suite complete
