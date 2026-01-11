#!/usr/bin/env python3
"""
CORTEX 6.0 Vacuum Orchestrator - Intelligent File Organization & Cleanup
Enforces CORE-009 (file organization) and naming conventions (kebab-case)

Author: GitHub Copilot + CORTEX Governance System
Version: 2.0.0
Date: 2026-01-11
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import sys
import hashlib
import yaml

# Define workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent
CORTEX_BRAIN = WORKSPACE_ROOT / "cortex-brain"


class ViolationType(Enum):
    """Types of governance violations"""
    UPPERCASE_NAME = "uppercase_filename"
    ROOT_LEVEL_DOC = "root_level_document"
    MISPLACED_FILE = "misplaced_file"
    DUPLICATE_FILE = "duplicate_file"
    ORPHANED_FILE = "orphaned_file"
    LARGE_FILE = "large_file"  # >1000 LOC


@dataclass
class FileViolation:
    """Represents a file that violates governance rules"""
    path: Path
    violation_type: ViolationType
    severity: str  # "high", "medium", "low"
    recommendation: str
    target_path: Path = None
    new_name: str = None


class GovernanceRules:
    """CORTEX governance rules for file organization"""
    
    # Files that are ALLOWED to have uppercase (exceptions)
    ALLOWED_UPPERCASE = {
        "README.md", "LICENSE", "LICENSE.md", "CHANGELOG.md", 
        "CONTRIBUTING.md", "AUTHORS", "NOTICE", "PATENTS",
        "AC-INDEX.yaml"  # AC-IDs use uppercase by design
    }
    
    # Patterns that are ALLOWED to have uppercase
    ALLOWED_PATTERNS = [
        r"^AC-[A-Z]+-\d{3}",  # AC-IDs like AC-AUDIT-001
        r"^README",            # README files
        r"^LICENSE",           # LICENSE files
        r"^CHANGELOG",         # CHANGELOG files
        r"^CONTRIBUTING",      # CONTRIBUTING files
    ]
    
    # Folders that should NOT have files at root level
    FORBIDDEN_ROOT_LEVEL = {
        CORTEX_BRAIN / "documents",
    }
    
    # Proper organization structure
    DOCUMENT_CATEGORIES = {
        "session-handoff": "handoffs",
        "handoff": "handoffs",
        "conflict": "analysis",
        "architecture": "architecture",
        "requirement": "requirements",
        "standard": "standards",
        "validation": "validation",
        "implementation": "implementation",
        "report": "reports",
        "upgrade": "upgrades",
        "fix": "fixes",
        "correction": "corrections",
        "milestone": "milestones",
        "orchestrator": "orchestrators",
        "planning": "planning",
        "governance": "governance",
        "diagram": "diagrams",
    }
    
    @staticmethod
    def is_allowed_uppercase(filename: str) -> bool:
        """Check if a filename is allowed to have uppercase"""
        # Check exact matches
        if filename in GovernanceRules.ALLOWED_UPPERCASE:
            return True
        
        # Check patterns
        for pattern in GovernanceRules.ALLOWED_PATTERNS:
            if re.match(pattern, filename):
                return True
        
        return False
    
    @staticmethod
    def to_kebab_case(name: str) -> str:
        """Convert filename to kebab-case"""
        # Special handling for AC-IDs (keep uppercase)
        if name.startswith("AC-") and name.count("-") >= 2:
            return name
        
        # First, replace underscores and spaces with hyphens
        name = re.sub(r'[_\s]+', '-', name)
        
        # Insert hyphens before uppercase letters that follow lowercase letters
        # This handles: "TruthSources" → "Truth-Sources"
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        return name
    
    @staticmethod
    def categorize_document(file_path: Path) -> str:
        """Determine the correct category for a document"""
        name_lower = file_path.stem.lower()
        
        # Check against known patterns
        for pattern, category in GovernanceRules.DOCUMENT_CATEGORIES.items():
            if pattern in name_lower:
                return category
        
        # Default to generic 'misc' category
        return "misc"


class VacuumOrchestrator:
    """Main orchestrator for file cleanup and organization"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.violations: List[FileViolation] = []
        self.actions_log: List[str] = []
        self.errors_log: List[str] = []
        self.file_hashes: Dict[str, List[Path]] = {}
        
    def log_action(self, action: str):
        """Log an action"""
        prefix = "[DRY-RUN] " if self.dry_run else "[EXECUTE] "
        message = f"{prefix}{action}"
        self.actions_log.append(message)
        print(message)
        
    def log_error(self, error: str):
        """Log an error"""
        message = f"[ERROR] {error}"
        self.errors_log.append(message)
        print(message, file=sys.stderr)
    
    def calculate_file_hash(self, path: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            hasher = hashlib.md5()
            with open(path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except Exception as e:
            self.log_error(f"Failed to hash {path}: {e}")
            return None
    
    def scan_for_violations(self):
        """Scan cortex-brain for governance violations"""
        self.log_action("=== Scanning for Governance Violations ===\n")
        
        # Scan all files in cortex-brain
        for file_path in CORTEX_BRAIN.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip non-document files
            if file_path.suffix not in {".md", ".yaml", ".yml", ".txt"}:
                continue
            
            # Skip certain directories
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", "node_modules", "venv"]):
                continue
            
            # Check for violations
            self._check_file_violations(file_path)
        
        self.log_action(f"\n✅ Scan complete: {len(self.violations)} violations found")
        
    def _check_file_violations(self, file_path: Path):
        """Check a single file for violations"""
        
        # 1. Check for uppercase violations (excluding allowed files)
        if (not GovernanceRules.is_allowed_uppercase(file_path.name) and 
            any(c.isupper() for c in file_path.stem)):
            
            new_name = GovernanceRules.to_kebab_case(file_path.stem) + file_path.suffix
            
            # Only flag if the new name is actually different
            if new_name != file_path.name:
                self.violations.append(FileViolation(
                    path=file_path,
                    violation_type=ViolationType.UPPERCASE_NAME,
                    severity="medium",
                    recommendation=f"Rename to kebab-case: {new_name}",
                    new_name=new_name
                ))
        
        # 2. Check for root-level documents in forbidden directories
        for forbidden_root in GovernanceRules.FORBIDDEN_ROOT_LEVEL:
            if file_path.parent == forbidden_root:
                category = GovernanceRules.categorize_document(file_path)
                target_dir = forbidden_root / category
                
                # Apply kebab-case to the filename when moving
                kebab_name = GovernanceRules.to_kebab_case(file_path.stem) + file_path.suffix
                
                self.violations.append(FileViolation(
                    path=file_path,
                    violation_type=ViolationType.ROOT_LEVEL_DOC,
                    severity="high",
                    recommendation=f"Move to {category}/ subfolder with kebab-case name",
                    target_path=target_dir / kebab_name
                ))
        
        # 3. Check for duplicate files (same content, different locations)
        file_hash = self.calculate_file_hash(file_path)
        if file_hash:
            if file_hash in self.file_hashes:
                self.file_hashes[file_hash].append(file_path)
            else:
                self.file_hashes[file_hash] = [file_path]
        
        # 4. Check for large files (>1000 lines - violates CORE-001)
        if file_path.suffix == ".md":
            try:
                line_count = len(file_path.read_text().splitlines())
                if line_count > 1000:
                    self.violations.append(FileViolation(
                        path=file_path,
                        violation_type=ViolationType.LARGE_FILE,
                        severity="low",
                        recommendation=f"File has {line_count} lines (>1000 limit). Consider splitting."
                    ))
            except Exception:
                pass
    
    def detect_duplicates(self):
        """Detect duplicate files based on content hash"""
        self.log_action("\n=== Detecting Duplicate Files ===\n")
        
        duplicates_found = 0
        for file_hash, paths in self.file_hashes.items():
            if len(paths) > 1:
                duplicates_found += 1
                self.log_action(f"Duplicate set {duplicates_found} (hash: {file_hash[:8]}):")
                
                # Keep the one in the best location, mark others for removal
                paths_sorted = sorted(paths, key=lambda p: (
                    # Prefer files in proper subdirectories
                    len(p.parts),
                    # Prefer files with kebab-case names
                    not any(c.isupper() for c in p.stem),
                    # Prefer shorter paths
                    len(str(p))
                ))
                
                keeper = paths_sorted[0]
                self.log_action(f"  ✓ KEEP: {keeper.relative_to(WORKSPACE_ROOT)}")
                
                for duplicate in paths_sorted[1:]:
                    self.log_action(f"  ✗ REMOVE: {duplicate.relative_to(WORKSPACE_ROOT)}")
                    self.violations.append(FileViolation(
                        path=duplicate,
                        violation_type=ViolationType.DUPLICATE_FILE,
                        severity="medium",
                        recommendation=f"Duplicate of {keeper.relative_to(WORKSPACE_ROOT)}"
                    ))
        
        if duplicates_found == 0:
            self.log_action("✅ No duplicate files found")
    
    def generate_remediation_plan(self) -> Dict[ViolationType, List[FileViolation]]:
        """Generate remediation plan grouped by violation type"""
        plan = {}
        for violation in self.violations:
            if violation.violation_type not in plan:
                plan[violation.violation_type] = []
            plan[violation.violation_type].append(violation)
        return plan
    
    def execute_remediation(self):
        """Execute the remediation plan"""
        self.log_action("\n=== Executing Remediation ===\n")
        
        plan = self.generate_remediation_plan()
        
        # Process violations by priority
        priority_order = [
            ViolationType.DUPLICATE_FILE,      # Remove duplicates first
            ViolationType.ROOT_LEVEL_DOC,      # Move misplaced files
            ViolationType.UPPERCASE_NAME,      # Rename to kebab-case
            ViolationType.LARGE_FILE,          # Report only (manual review)
        ]
        
        for violation_type in priority_order:
            if violation_type not in plan:
                continue
            
            violations = plan[violation_type]
            self.log_action(f"\n--- Processing {violation_type.value} ({len(violations)} files) ---")
            
            for violation in violations:
                self._remediate_violation(violation)
    
    def _remediate_violation(self, violation: FileViolation):
        """Remediate a single violation"""
        try:
            if violation.violation_type == ViolationType.DUPLICATE_FILE:
                # Remove duplicate
                if not self.dry_run:
                    violation.path.unlink()
                self.log_action(f"Removed duplicate: {violation.path.relative_to(WORKSPACE_ROOT)}")
            
            elif violation.violation_type == ViolationType.ROOT_LEVEL_DOC:
                # Move to proper subfolder
                if not self.dry_run:
                    violation.target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(violation.path), str(violation.target_path))
                self.log_action(f"Moved: {violation.path.relative_to(WORKSPACE_ROOT)} → {violation.target_path.relative_to(WORKSPACE_ROOT)}")
            
            elif violation.violation_type == ViolationType.UPPERCASE_NAME:
                # Rename to kebab-case
                new_path = violation.path.parent / violation.new_name
                if not self.dry_run:
                    shutil.move(str(violation.path), str(new_path))
                self.log_action(f"Renamed: {violation.path.name} → {violation.new_name}")
            
            elif violation.violation_type == ViolationType.LARGE_FILE:
                # Report only (manual review required)
                self.log_action(f"⚠️  REVIEW NEEDED: {violation.path.relative_to(WORKSPACE_ROOT)} - {violation.recommendation}")
        
        except Exception as e:
            self.log_error(f"Failed to remediate {violation.path.relative_to(WORKSPACE_ROOT)}: {e}")
    
    def generate_report(self):
        """Generate summary report"""
        self.log_action("\n" + "="*70)
        self.log_action("=== VACUUM ORCHESTRATOR SUMMARY ===")
        self.log_action("="*70)
        
        self.log_action(f"\nMode: {'DRY-RUN (no changes made)' if self.dry_run else 'EXECUTE (changes applied)'}")
        self.log_action(f"Total Violations: {len(self.violations)}")
        self.log_action(f"Total Actions: {len(self.actions_log)}")
        self.log_action(f"Total Errors: {len(self.errors_log)}")
        
        # Breakdown by violation type
        plan = self.generate_remediation_plan()
        self.log_action("\nViolations by Type:")
        for violation_type, violations in plan.items():
            self.log_action(f"  - {violation_type.value}: {len(violations)}")
        
        # Severity breakdown
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for violation in self.violations:
            severity_counts[violation.severity] += 1
        
        self.log_action("\nViolations by Severity:")
        for severity, count in severity_counts.items():
            self.log_action(f"  - {severity.upper()}: {count}")
        
        if self.errors_log:
            self.log_action("\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.errors_log:
                print(error)
        
        if not self.dry_run:
            self.log_action("\n✅ Vacuum complete!")
            self.log_action("\nNext steps:")
            self.log_action("1. Review changes")
            self.log_action("2. Update any broken references")
            self.log_action("3. Run tests to verify integrity")
            self.log_action("4. Commit changes")
        else:
            self.log_action("\n✅ Dry-run complete. Review the actions above.")
            self.log_action("\nTo execute, run:")
            self.log_action("  python3 scripts/vacuum_orchestrator.py --execute")
    
    def execute(self):
        """Execute the full vacuum operation"""
        try:
            self.scan_for_violations()
            self.detect_duplicates()
            self.execute_remediation()
            self.generate_report()
            
            return len(self.errors_log) == 0
        
        except Exception as e:
            self.log_error(f"Fatal error during vacuum: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX 6.0 Vacuum Orchestrator - Intelligent File Organization & Cleanup"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the cleanup (default is dry-run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without executing (default)"
    )
    
    args = parser.parse_args()
    
    # Execute is opposite of dry-run
    dry_run = not args.execute
    
    print("="*70)
    print("CORTEX 6.0 VACUUM ORCHESTRATOR")
    print("="*70)
    print(f"Mode: {'DRY-RUN (preview only)' if dry_run else 'EXECUTE (apply changes)'}")
    print("="*70)
    print()
    
    orchestrator = VacuumOrchestrator(dry_run=dry_run)
    success = orchestrator.execute()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
