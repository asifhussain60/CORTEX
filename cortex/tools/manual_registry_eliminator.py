"""
Manual Registry Eliminator - Automatic detection and removal of manual orchestrator registries

AC-PERMANENT-FIX-012: Complete elimination of manual registry usage
This module automatically detects and removes all manual orchestrator registry patterns,
ensuring 100% DatabaseBackedRegistry usage with no fallbacks possible.

CRITICAL ENFORCEMENT:
- Scans ALL Python files for manual registry patterns
- Automatically replaces with DatabaseBackedRegistry equivalents
- Removes manual wiring files and imports
- Blocks system if manual registries detected
- Enforces single execution path

Author: Asif Hussain
Date: 2026-01-25
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class ManualRegistryPattern:
    """Manual registry usage pattern."""
    
    pattern_type: str
    file_path: str
    line_number: int
    content: str
    replacement: str
    severity: str = "CRITICAL"  # CRITICAL, HIGH, MEDIUM


@dataclass
class EliminationReport:
    """Report of manual registry elimination."""
    
    manual_registries_found: int = 0
    files_scanned: int = 0
    files_modified: int = 0
    fallbacks_removed: int = 0
    patterns_eliminated: List[ManualRegistryPattern] = field(default_factory=list)
    single_path_active: bool = False
    errors: List[str] = field(default_factory=list)


class ManualRegistryEliminator:
    """
    Automatic detection and elimination of manual orchestrator registries.
    
    Ensures 100% DatabaseBackedRegistry usage by:
    1. Scanning all Python files for manual registry patterns
    2. Detecting legacy imports and usage
    3. Automatically replacing with DatabaseBackedRegistry equivalents
    4. Removing manual wiring files
    5. Enforcing single execution path
    
    Usage:
        >>> eliminator = ManualRegistryEliminator()
        >>> report = eliminator.eliminate_all_manual_registries()
        >>> print(f"Eliminated {report.manual_registries_found} manual registries")
    """
    
    # Patterns that indicate manual registry usage
    MANUAL_REGISTRY_PATTERNS = {
        "legacy_orchestrator_registry": [
            r"from cortex\.orchestrators\.registry\.orchestrator_registry import OrchestratorRegistry",
            r"OrchestratorRegistry\.instance\(\)",
            r"OrchestratorRegistry\(\)",
# REMOVED: Manual registry pattern - r"registry = OrchestratorRegistry"
        ],
        "manual_wire_imports": [
            r"from cortex\.orchestrators\.core\.wire_00[123].*import",
            r"execute_wire_00[123]",
            r"wire_00[123]_.*_wiring"
        ],
        "manual_wire_calls": [
            r"execute_wire_00[123]\(\)",
            r"if execute_wire_00[123] is not None:",
            r"wire_00[123]_result = execute_wire_00[123]\(\)"
        ],
        "fallback_logic": [
# REMOVED: Manual registry pattern - r"# Fallback to manual.*wire",
# REMOVED: Manual registry pattern - r"wire.*fallback",
# REMOVED: Manual registry pattern - r"manual.*wiring.*fallback"
        ]
    }
    
    # Manual wiring files to be deleted
    MANUAL_WIRING_FILES = [
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - "cortex/orchestrators/core/wire_001_core_wiring.py",
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - "cortex/orchestrators/core/wire_002_domain_wiring.py",
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - "cortex/orchestrators/core/wire_003_support_wiring.py",
        "cortex/orchestrators/core/orchestrator_wiring.py",
        "cortex/orchestrators/registry/orchestrator_registry.py"  # Legacy registry
    ]
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize manual registry eliminator."""
        self.project_root = project_root or Path(".")
        self.logger = EnhancedAuditLogger.instance()
        self.report = EliminationReport()
        
    def eliminate_all_manual_registries(self) -> EliminationReport:
        """
        Eliminate all manual registry usage patterns.
        
        Returns:
            EliminationReport with detailed results
        """
        self.logger.log_operation_start(
            ac_id="AC-PERMANENT-FIX-012",
            operation="ELIMINATE_MANUAL_REGISTRIES",
            details={"project_root": str(self.project_root)}
        )
        
        try:
            # Step 1: Scan all Python files
            self._scan_all_files()
            
            # Step 2: Replace patterns with DatabaseBackedRegistry equivalents
            self._replace_manual_patterns()
            
            # Step 3: Remove manual wiring files
            self._remove_manual_wiring_files()
            
            # Step 4: Verify single path enforcement
            self._verify_single_path()
            
            self.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-012",
                operation="ELIMINATE_MANUAL_REGISTRIES",
                success=True,
                details={
                    "patterns_eliminated": len(self.report.patterns_eliminated),
                    "files_modified": self.report.files_modified,
                    "single_path_active": self.report.single_path_active
                }
            )
            
            return self.report
            
        except Exception as e:
            self.report.errors.append(str(e))
            self.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-012",
                operation="ELIMINATE_MANUAL_REGISTRIES",
                success=False,
                details={"error": str(e)}
            )
            return self.report
    
    def _scan_all_files(self) -> None:
        """Scan all Python files for manual registry patterns."""
        python_files = list(self.project_root.rglob("*.py"))
        self.report.files_scanned = len(python_files)
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._scan_file_for_patterns(file_path, content)
                
            except Exception as e:
                self.report.errors.append(f"Error scanning {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scan."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".git",
            "tests/",  # Skip tests for now, handle separately
            self.__class__.__module__.replace(".", "/") + ".py"  # Skip self
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _scan_file_for_patterns(self, file_path: Path, content: str) -> None:
        """Scan individual file for manual registry patterns."""
        lines = content.split('\n')
        
        for pattern_type, patterns in self.MANUAL_REGISTRY_PATTERNS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        manual_pattern = ManualRegistryPattern(
                            pattern_type=pattern_type,
                            file_path=str(file_path),
                            line_number=line_num,
                            content=line.strip(),
                            replacement=self._generate_replacement(pattern_type, line.strip())
                        )
                        self.report.patterns_eliminated.append(manual_pattern)
                        self.report.manual_registries_found += 1
    
    def _generate_replacement(self, pattern_type: str, original_line: str) -> str:
        """Generate DatabaseBackedRegistry replacement for manual pattern."""
        replacements = {
            "legacy_orchestrator_registry": {
"from cortex.orchestrators import get_database_registry":
                    "from cortex.orchestrators import get_database_registry",
"get_database_registry()":
                    "get_database_registry()",
"registry = get_database_registry()":
                    "registry = get_database_registry()"
            },
            "manual_wire_imports": {
"from cortex.orchestrators import initialize_database_wiring":
                    "from cortex.orchestrators import initialize_database_wiring",
"# REMOVED: Manual wiring replaced with DatabaseBackedRegistry":
                    "# REMOVED: Manual wiring replaced with DatabaseBackedRegistry",
"# REMOVED: Manual wiring replaced with DatabaseBackedRegistry":
                    "# REMOVED: Manual wiring replaced with DatabaseBackedRegistry"
            },
            "manual_wire_calls": {
"initialize_database_wiring()": "initialize_database_wiring()",
"# REMOVED: All orchestrators wired via DatabaseBackedRegistry": "# REMOVED: All orchestrators wired via DatabaseBackedRegistry",
"# REMOVED: All orchestrators wired via DatabaseBackedRegistry": "# REMOVED: All orchestrators wired via DatabaseBackedRegistry"
            }
        }
        
        # Find matching replacement
        for pattern, replacement in replacements.get(pattern_type, {}).items():
            if pattern in original_line:
                return original_line.replace(pattern, replacement)
        
        return f"# REMOVED: Manual registry pattern - {original_line}"
    
    def _replace_manual_patterns(self) -> None:
        """Replace all detected manual patterns with DatabaseBackedRegistry equivalents."""
        files_to_modify = {}
        
        # Group patterns by file for efficient replacement
        for pattern in self.report.patterns_eliminated:
            if pattern.file_path not in files_to_modify:
                files_to_modify[pattern.file_path] = []
            files_to_modify[pattern.file_path].append(pattern)
        
        for file_path, patterns in files_to_modify.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply replacements
                modified_content = self._apply_replacements(content, patterns)
                
                # Write back modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.report.files_modified += 1
                
            except Exception as e:
                self.report.errors.append(f"Error modifying {file_path}: {e}")
    
    def _apply_replacements(self, content: str, patterns: List[ManualRegistryPattern]) -> str:
        """Apply all replacements to file content."""
        lines = content.split('\n')
        
        # Sort patterns by line number (descending) to avoid line number shifts
        patterns.sort(key=lambda p: p.line_number, reverse=True)
        
        for pattern in patterns:
            line_idx = pattern.line_number - 1
            if 0 <= line_idx < len(lines):
                lines[line_idx] = pattern.replacement
                if pattern.pattern_type == "fallback_logic":
                    self.report.fallbacks_removed += 1
        
        return '\n'.join(lines)
    
    def _remove_manual_wiring_files(self) -> None:
        """Remove manual wiring files that are no longer needed."""
        for file_path in self.MANUAL_WIRING_FILES:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.logger.log_operation_complete(
                        ac_id="AC-PERMANENT-FIX-012",
                        operation="DELETE_MANUAL_WIRING_FILE",
                        success=True,
                        details={"file": str(full_path)}
                    )
                except Exception as e:
                    self.report.errors.append(f"Error deleting {full_path}: {e}")
    
    def _verify_single_path(self) -> None:
        """Verify that only DatabaseBackedRegistry path exists."""
        # Scan for any remaining manual registry patterns
        remaining_patterns = []
        
        for file_path in self.project_root.rglob("*.py"):
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for any remaining manual patterns
                for pattern_type, patterns in self.MANUAL_REGISTRY_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            remaining_patterns.append(f"{file_path}:{pattern}")
                            
            except Exception:
                continue
        
        self.report.single_path_active = len(remaining_patterns) == 0
        
        if remaining_patterns:
            self.report.errors.extend([
                "Manual registry patterns still detected:",
                *remaining_patterns
            ])


def eliminate_manual_registries() -> EliminationReport:
    """
    Convenience function to eliminate all manual registries.
    
    Returns:
        EliminationReport with results
    """
    eliminator = ManualRegistryEliminator()
    return eliminator.eliminate_all_manual_registries()


def enforce_database_registry_only() -> bool:
    """
    Enforce that only DatabaseBackedRegistry is used.
    
    Returns:
        True if enforcement successful, False if manual registries detected
        
    Raises:
        RuntimeError if manual registries found and system should be blocked
    """
    eliminator = ManualRegistryEliminator()
    
    # Quick scan for manual patterns (no modifications)
    eliminator._scan_all_files()
    
    if eliminator.report.manual_registries_found > 0:
        error_msg = (
            f"CRITICAL: {eliminator.report.manual_registries_found} manual registry "
            f"patterns detected. System blocked until elimination complete."
        )
        
        # Log patterns found
        for pattern in eliminator.report.patterns_eliminated[:5]:  # Show first 5
            error_msg += f"\n  - {pattern.file_path}:{pattern.line_number} - {pattern.content}"
        
        if len(eliminator.report.patterns_eliminated) > 5:
            error_msg += f"\n  ... and {len(eliminator.report.patterns_eliminated) - 5} more"
        
        raise RuntimeError(error_msg)
    
    return True