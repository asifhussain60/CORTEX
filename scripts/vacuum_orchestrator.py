#!/usr/bin/env python3
"""
CORTEX 6.0 Vacuum Orchestrator - Intelligent File Organization & Cleanup
Enforces CORE-009 (file organization) and naming conventions (kebab-case)

Author: GitHub Copilot + CORTEX Governance System
Version: 4.1.0 (NEW: Post-Vacuum Integrity Verification Phase)
Date: 2026-01-12

CHANGELOG:
- v3.0.0: Safety guards, similarity detection, tier-aware relocation
- v4.0.0: Root pollution prevention, interactive audit, phase 0 detection
- v4.1.0: Post-vacuum integrity verification (Phase 4), self-learning checks
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys
import hashlib
import yaml
from difflib import SequenceMatcher
from datetime import datetime

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


class RootPollutionPrevention:
    """
    NEW (v4.0): Prevents files from accumulating at repository root.
    Analyzes root-level files and suggests intelligent relocation.
    """
    
    # Files ALLOWED at root (essential only)
    ALLOWED_ROOT_FILES = {
        "README.md", "LICENSE", "LICENSE.md", ".gitignore", ".gitattributes",
        ".github", ".git", ".pytest_cache", ".favorites.json", ".cortex",
        "requirements.txt", "package.json", "pyproject.toml", "setup.py",
        ".dockerignore", ".env.example", "Makefile", "CHANGELOG.md"
    }
    
    # File type to relocation target mapping
    RELOCATION_TARGETS = {
        # Python scripts (demo, diagnostic, test utilities)
        r"^(demo|example|test_|diagnose|inspect|analyze).*\.py$": {
            "target_dir": "docs/examples/",
            "category": "example",
            "reason": "Demo and diagnostic utilities"
        },
        # Test outputs
        r"^(test|coverage|results)[-_].*\.(txt|xml|json|html)$": {
            "target_dir": "cortex-brain/documents/testing/",
            "category": "testing",
            "reason": "Test execution outputs"
        },
        # Markdown documentation at root
        r"^[A-Z][A-Z0-9-]*\.md$": {
            "target_dir": "cortex-brain/documents/misc/",
            "category": "documentation",
            "reason": "Root-level markdown moved to documents"
        },
        # Log files
        r"^.*\.(log|trace)$": {
            "target_dir": "cortex-brain/documents/testing/",
            "category": "logs",
            "reason": "System logs and traces"
        },
        # State/metadata files
        r"^\.cortex-.*$": {
            "target_dir": "cortex-brain/state/",
            "category": "metadata",
            "reason": "CORTEX system state files"
        }
    }
    
    @staticmethod
    def scan_root_pollution() -> List[Dict]:
        """
        Scan repository root for files that should be relocated.
        Returns: List of found violations with relocation targets
        """
        violations = []
        
        root_files = list(WORKSPACE_ROOT.glob("*"))
        
        for item in root_files:
            # Skip essential files and directories
            if item.name in RootPollutionPrevention.ALLOWED_ROOT_FILES:
                continue
            
            if item.is_dir():
                continue  # Ignore directories
            
            # Check if file matches relocation pattern
            for pattern, target_info in RootPollutionPrevention.RELOCATION_TARGETS.items():
                if re.match(pattern, item.name, re.IGNORECASE):
                    violations.append({
                        "file": item.name,
                        "full_path": item,
                        "target_dir": target_info["target_dir"],
                        "category": target_info["category"],
                        "reason": target_info["reason"]
                    })
                    break
        
        return violations
    
    @staticmethod
    def auto_relocate_root_pollution(dry_run: bool = False) -> int:
        """
        Automatically relocate files from root to proper directories.
        Returns: Number of files relocated
        """
        violations = RootPollutionPrevention.scan_root_pollution()
        
        if not violations:
            print("  ✓ Root directory clean (no pollution detected)")
            return 0
        
        print(f"  ⚠️  Detected {len(violations)} root-level files to relocate")
        
        count = 0
        for violation in violations:
            source = violation["full_path"]
            target_dir = Path(violation["target_dir"])
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert filename to kebab-case
            new_name = GovernanceRules.to_kebab_case(source.stem) + source.suffix
            dest = target_dir / new_name
            
            if not dry_run:
                try:
                    shutil.move(str(source), str(dest))
                    print(f"    ✓ {source.name:40} → {violation['category']}/")
                    count += 1
                except Exception as e:
                    print(f"    ✗ Failed to move {source.name}: {e}")
            else:
                print(f"    [DRY-RUN] Would move {source.name:30} → {violation['category']}/")
                count += 1
        
        return count


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


class FilePurposeClassifier:
    """
    Classifies file purpose: actionable vs. informational vs. critical
    Enables selective deletion with safety guarantees
    """
    
    # Patterns that indicate ACTIONABLE documents (NEVER DELETE)
    ACTIONABLE_PATTERNS = [
        r".*FUNCTIONAL-ANALYSIS.*",     # Analysis documents (your request)
        r".*IMPLEMENTATION.*",          # Implementation guides
        r".*PROGRESS.*",                # Progress tracking
        r".*EVIDENCE.*",                # Evidence bundles
        r".*RECOVERY.*",                # Recovery strategies
        r".*ROADMAP.*",                 # Project roadmaps
        r".*PLAN.*",                    # Planning documents
        r".*STRATEGY.*",                # Strategic plans
        r".*ARCHITECTURE.*",            # Architecture docs
        r".*CORTEX-BRAIN.*",            # Core analysis
        r"AC-INDEX.*",                  # AC registry
        r".*core-rules.*",              # Core governance
        r".*progress-tracker.*",        # State tracking
        r".*master-plan.*",             # Master plan
    ]
    
    # Patterns that indicate INFORMATIONAL only (SAFE TO DELETE)
    INFORMATIONAL_PATTERNS = [
        r".*TEMP.*",
        r".*DRAFT.*",
        r".*WORKING.*",
        r".*OLD.*",
        r".*BACKUP.*",
        r".*ARCHIVE.*",
        r".*[0-9]{8}.*",                # Timestamped versions (YYYYMMDD)
        r".*\.bak$",                    # Backup files
        r".*\.tmp$",                    # Temp files
        r"test-.*\.md$",                # Test markdown files
        r".*debug.*",
    ]
    
    # Critical system files (NEVER DELETE UNDER ANY CIRCUMSTANCE)
    CRITICAL_PATHS = {
        "cortex-brain/tier0/",
        "cortex-brain/tier1/tracking/",
        "cortex-brain/tier1/acceptance-criteria/",
        ".github/",
        ".git/",
        "src/",
        "tests/",
        "LICENSE",
        "README.md",
    }
    
    @staticmethod
    def is_actionable(file_path: Path) -> bool:
        """Check if file contains actionable content (should be preserved)"""
        filename = file_path.name.upper()
        stem = file_path.stem.upper()
        
        for pattern in FilePurposeClassifier.ACTIONABLE_PATTERNS:
            if re.match(pattern, stem, re.IGNORECASE):
                return True
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def is_informational(file_path: Path) -> bool:
        """Check if file is informational-only (safe to delete)"""
        filename = file_path.name.upper()
        stem = file_path.stem.upper()
        
        for pattern in FilePurposeClassifier.INFORMATIONAL_PATTERNS:
            if re.match(pattern, stem, re.IGNORECASE):
                return True
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def is_critical(file_path: Path) -> bool:
        """Check if file is in critical system area"""
        file_str = str(file_path).replace("\\", "/")
        
        for critical_path in FilePurposeClassifier.CRITICAL_PATHS:
            if critical_path in file_str:
                return True
        
        return False
    
    @staticmethod
    def classify_file(file_path: Path) -> str:
        """
        Classify file purpose.
        Returns: 'critical', 'actionable', 'informational', or 'unknown'
        """
        if FilePurposeClassifier.is_critical(file_path):
            return "critical"
        
        if FilePurposeClassifier.is_actionable(file_path):
            return "actionable"
        
        if FilePurposeClassifier.is_informational(file_path):
            return "informational"
        
        return "unknown"


class SimilarityDetector:
    """
    Detects similar documents for intelligent consolidation.
    Uses fuzzy matching to find related documents.
    """
    
    SIMILARITY_THRESHOLD = 0.85  # 85% content similarity
    
    @staticmethod
    def _similarity_ratio(content1: str, content2: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)"""
        matcher = SequenceMatcher(None, content1, content2)
        return matcher.ratio()
    
    @staticmethod
    def find_similar_files(files: List[Path], threshold: float = 0.85) -> Dict[str, List[Path]]:
        """
        Find groups of similar files.
        Returns: dict mapping representative file to list of similar files
        
        OPTIMIZED: Samples files to avoid O(n²) race condition with large directories
        """
        file_contents = {}
        similar_groups = {}
        
        # FIX: Limit to documents folder only (avoid scanning all of cortex-brain)
        doc_files = [f for f in files if 'documents' in str(f)]
        
        if len(doc_files) < 2:
            return {}
        
        # FIX: Sample if too many files (avoid O(n²) explosion)
        MAX_SAMPLE = 50
        if len(doc_files) > MAX_SAMPLE:
            print(f"    ⚠️  Sampling {MAX_SAMPLE} of {len(doc_files)} files (too many for full comparison)")
            import random
            random.seed(42)  # Deterministic sampling
            doc_files = random.sample(doc_files, MAX_SAMPLE)
        
        # Load file contents with size limit (avoid memory explosion)
        MAX_FILE_SIZE = 1024 * 1024  # 1MB limit per file
        for f in doc_files:
            try:
                size = f.stat().st_size
                if size > MAX_FILE_SIZE:
                    continue  # Skip very large files
                if f.suffix in {'.md', '.yaml', '.yml', '.txt'}:
                    file_contents[f] = f.read_text(encoding='utf-8', errors='ignore')[:100000]  # First 100KB
            except Exception:
                pass
        
        if len(file_contents) < 2:
            return {}
        
        # Compare all pairs (now limited by sampling)
        files_list = list(file_contents.keys())
        processed = set()
        
        for i, file1 in enumerate(files_list):
            if file1 in processed:
                continue
            
            similar_set = [file1]
            
            for file2 in files_list[i+1:]:
                if file2 in processed:
                    continue
                
                similarity = SimilarityDetector._similarity_ratio(
                    file_contents[file1],
                    file_contents[file2]
                )
                
                if similarity >= threshold:
                    similar_set.append(file2)
                    processed.add(file2)
            
            if len(similar_set) > 1:
                # Sort by newest first, use as representative
                representative = sorted(similar_set, 
                                      key=lambda p: p.stat().st_mtime, 
                                      reverse=True)[0]
                similar_groups[representative] = similar_set
                processed.add(file1)
        
        return similar_groups


class TierAwareCategorizer:
    """
    Categorizes files to appropriate cortex-brain tier
    Enables intelligent relocation to tier0, tier1, tier2, or tier3
    """
    
    TIER_RULES = {
        "tier0": [
            r".*governance.*",
            r".*core-rules.*",
            r".*SKULL.*",
            r"AC-INDEX.*",
            r".*core-.*",
        ],
        "tier1": [
            r".*progress.*",
            r".*acceptance.*",
            r".*tracking.*",
            r".*state.*",
            r".*active.*",
        ],
        "tier2": [
            r".*standards.*",
            r".*practices.*",
            r".*engineering.*",
            r".*guidelines.*",
        ],
        "tier3": [
            r".*knowledge.*",
            r".*patterns.*",
            r".*insights.*",
            r".*learned.*",
        ]
    }
    
    @staticmethod
    def categorize_to_tier(file_path: Path) -> Optional[str]:
        """
        Determine appropriate tier for a file.
        Returns: 'tier0', 'tier1', 'tier2', 'tier3', or None if no match
        """
        filename = file_path.name.lower()
        stem = file_path.stem.lower()
        
        # Check filename against tier patterns
        for tier in ["tier0", "tier1", "tier2", "tier3"]:
            for pattern in TierAwareCategorizer.TIER_RULES[tier]:
                if re.search(pattern, stem, re.IGNORECASE):
                    return tier
                if re.search(pattern, filename, re.IGNORECASE):
                    return tier
        
        return None
    
    @staticmethod
    def suggest_tier_path(file_path: Path, category: str) -> Path:
        """
        Suggest full path including tier.
        Example: progress-tracker.json → cortex-brain/tier1/tracking/progress-tracker.json
        """
        tier = TierAwareCategorizer.categorize_to_tier(file_path)
        
        if not tier:
            return None
        
        tier_path = CORTEX_BRAIN / tier / category
        return tier_path / file_path.name


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
    
    def audit_root_directory(self) -> Dict:
        """
        NEW (v4.0): Interactive audit of repository root.
        Provides detailed analysis of root-level files and relocation recommendations.
        Returns: Dict with audit results
        """
        print("\n" + "="*70)
        print("📋 CORTEX ROOT DIRECTORY AUDIT (v4.0)")
        print("="*70)
        
        # Scan for pollution
        violations = RootPollutionPrevention.scan_root_pollution()
        
        print(f"\n✓ Repository root contains {len(violations)} files needing relocation\n")
        
        # Categorize violations
        categories = {}
        for v in violations:
            cat = v["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(v)
        
        # Display by category
        for category in sorted(categories.keys()):
            files = categories[category]
            print(f"📁 {category.upper()} ({len(files)} file{'s' if len(files) != 1 else ''})")
            for file_info in files:
                print(f"   • {file_info['file']:40} → {file_info['target_dir']}")
                print(f"     Reason: {file_info['reason']}")
            print()
        
        # Allowed files
        print("✅ ALLOWED AT ROOT (Essential)")
        allowed_list = sorted(list(RootPollutionPrevention.ALLOWED_ROOT_FILES))
        for i, fname in enumerate(allowed_list, 1):
            if (WORKSPACE_ROOT / fname).exists() or fname.startswith("."):
                print(f"   [{i:2}] {fname}")
        
        print("\n" + "="*70)
        
        return {
            "total_violations": len(violations),
            "categories": categories,
            "allowed_count": len(RootPollutionPrevention.ALLOWED_ROOT_FILES)
        }
    
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
        """Remediate a single violation with enhanced safety checks"""
        try:
            if violation.violation_type == ViolationType.DUPLICATE_FILE:
                # ENHANCED: Check file classification before deletion
                classification = FilePurposeClassifier.classify_file(violation.path)
                
                if classification == "critical":
                    self.log_action(f"⛔ BLOCKED (CRITICAL): {violation.path.relative_to(WORKSPACE_ROOT)}")
                    self.log_action(f"   Reason: File is in critical system area")
                    return
                
                if classification == "actionable":
                    self.log_action(f"⚠️  SKIPPED (ACTIONABLE): {violation.path.relative_to(WORKSPACE_ROOT)}")
                    self.log_action(f"   Reason: File contains actionable analysis content")
                    return
                
                # Only remove if informational
                if not self.dry_run:
                    violation.path.unlink()
                
                self.log_action(f"✓ Removed duplicate: {violation.path.relative_to(WORKSPACE_ROOT)} [{classification}]")
            
            elif violation.violation_type == ViolationType.ROOT_LEVEL_DOC:
                # Check classification before moving
                classification = FilePurposeClassifier.classify_file(violation.path)
                
                if classification == "critical":
                    self.log_action(f"⛔ BLOCKED (CRITICAL): {violation.path.relative_to(WORKSPACE_ROOT)}")
                    self.log_action(f"   Cannot move critical files")
                    return
                
                if not self.dry_run:
                    violation.target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(violation.path), str(violation.target_path))
                
                self.log_action(f"✓ Moved: {violation.path.relative_to(WORKSPACE_ROOT)} → {violation.target_path.relative_to(WORKSPACE_ROOT)}")
            
            elif violation.violation_type == ViolationType.UPPERCASE_NAME:
                # Rename to kebab-case
                classification = FilePurposeClassifier.classify_file(violation.path)
                
                if classification == "critical":
                    self.log_action(f"⛔ BLOCKED (CRITICAL): {violation.path.relative_to(WORKSPACE_ROOT)}")
                    self.log_action(f"   Cannot rename critical files")
                    return
                
                new_path = violation.path.parent / violation.new_name
                
                if not self.dry_run:
                    shutil.move(str(violation.path), str(new_path))
                
                self.log_action(f"✓ Renamed: {violation.path.name} → {violation.new_name} [{classification}]")
            
            elif violation.violation_type == ViolationType.LARGE_FILE:
                # Report only (manual review required)
                self.log_action(f"⚠️  REVIEW NEEDED: {violation.path.relative_to(WORKSPACE_ROOT)}")
                self.log_action(f"   {violation.recommendation}")
        
        except Exception as e:
            self.log_error(f"Failed to remediate {violation.path.relative_to(WORKSPACE_ROOT)}: {e}")

    def detect_similar_documents(self):
        """Detect similar documents for consolidation"""
        self.log_action("\n=== Detecting Similar Documents (85%+ similarity) ===\n")
        print("    [Phase 2.1/3] Collecting document files...")
        
        # Collect document files ONLY (fix: avoid scanning entire cortex-brain)
        doc_files = []
        doc_dir = CORTEX_BRAIN / "documents"
        if doc_dir.exists():
            for file_path in doc_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in {'.md', '.yaml', '.yml', '.txt'}:
                    doc_files.append(file_path)
        
        print(f"    [Phase 2.2/3] Found {len(doc_files)} document files")
        
        if len(doc_files) < 2:
            self.log_action("✅ No similar documents found (less than 2 files)")
            return
        
        # Find similar groups
        print("    [Phase 2.3/3] Computing similarities (may take a moment)...")
        similar_groups = SimilarityDetector.find_similar_files(doc_files, threshold=0.85)
        
        if not similar_groups:
            self.log_action("✅ No similar documents found (>85% similarity)")
            return
        
        self.log_action(f"Found {len(similar_groups)} consolidation opportunities:\n")
        
        for i, (representative, similar_files) in enumerate(similar_groups.items(), 1):
            self.log_action(f"Consolidation Group {i}:")
            self.log_action(f"  ✓ KEEP (newest): {representative.relative_to(WORKSPACE_ROOT)}")
            
            for similar in similar_files:
                if similar != representative:
                    # Archive with timestamp suffix
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    archive_dir = CORTEX_BRAIN / "documents" / "archive" / "consolidated"
                    archive_path = archive_dir / f"{similar.stem}-{timestamp}{similar.suffix}"
                    
                    self.log_action(f"  ↳ ARCHIVE: {similar.relative_to(WORKSPACE_ROOT)}")
                    self.log_action(f"     → {archive_path.relative_to(WORKSPACE_ROOT)}")
                    
                    if not self.dry_run:
                        try:
                            archive_dir.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(str(similar), str(archive_path))
                        except Exception as e:
                            self.log_error(f"Failed to archive {similar}: {e}")
            
            self.log_action("")
    
    def suggest_tier_relocations(self):
        """Suggest tier-aware relocations for documents"""
        self.log_action("\n=== Suggesting Tier-Aware Relocations ===\n")
        print("    [Phase 2.4/4] Analyzing tier placement...")
        
        relocations = []
        
        # FIX: Only scan documents folder (not entire cortex-brain)
        doc_dir = CORTEX_BRAIN / "documents"
        if not doc_dir.exists():
            self.log_action("✅ No documents folder found")
            return
        
        scanned = 0
        for file_path in doc_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            scanned += 1
            if scanned % 10 == 0:
                print(f"    Scanned {scanned} files...")
            
            if file_path.suffix not in {'.md', '.yaml', '.yml', '.txt'}:
                continue
            
            # Skip files already in tier structure
            if any(tier in str(file_path) for tier in ["tier0", "tier1", "tier2", "tier3"]):
                continue
            
            # Check tier suggestion
            tier = TierAwareCategorizer.categorize_to_tier(file_path)
            
            if tier:
                category = GovernanceRules.categorize_document(file_path)
                suggested_path = TierAwareCategorizer.suggest_tier_path(file_path, category)
                
                if suggested_path and suggested_path != file_path:
                    relocations.append((file_path, suggested_path, tier, category))
        
        print(f"    Analyzed {scanned} files, found {len(relocations)} tier suggestions")
        
        if relocations:
            self.log_action(f"Found {len(relocations)} suggested tier relocations:\n")
            
            for file_path, suggested_path, tier, category in relocations[:20]:  # Limit to 20 suggestions
                self.log_action(f"✓ {file_path.relative_to(WORKSPACE_ROOT)}")
                self.log_action(f"  → Tier: {tier}, Category: {category}")
                self.log_action(f"  → {suggested_path.relative_to(WORKSPACE_ROOT)}\n")
            
            if len(relocations) > 20:
                self.log_action(f"... and {len(relocations) - 20} more suggestions")
        else:
            self.log_action("✅ All documents are properly tier-organized")
    
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
    
    def verify_post_vacuum_integrity(self):
        """
        NEW (v4.0): Post-vacuum integrity verification phase.
        Ensures vacuum operations didn't break CORTEX architecture.
        
        Checks:
        1. All critical files still exist
        2. Core module imports work
        3. Governance files are valid
        4. Database integrity
        """
        print("  [1/4] Checking critical files...")
        critical_files = [
            "cortex-brain/tier0/governance/core-rules.yaml",
            "cortex-brain/tier1/tracking/progress-tracker.json",
            "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
            "cortex-brain/cx6-plan/master-plan.yaml",
            "src/infrastructure/enhanced_audit_logger.py",
            "src/orchestrators/core/governance_merger.py",
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = WORKSPACE_ROOT / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                self.log_error(f"Critical file missing: {file_path}")
        
        if missing_files:
            print(f"    ✗ {len(missing_files)} critical file(s) missing")
        else:
            print(f"    ✓ All {len(critical_files)} critical files present")
        
        print("  [2/4] Verifying core imports...")
        import_errors = []
        critical_imports = [
            ("src.infrastructure.enhanced_audit_logger", "EnhancedAuditLogger"),
            ("src.orchestrators.core.governance_merger", "GovernanceMerger"),
            ("src.orchestrators.core.master_orchestrator", "MasterOrchestrator"),
        ]
        
        import sys
        original_path = sys.path.copy()
        sys.path.insert(0, str(WORKSPACE_ROOT))
        
        for module_name, class_name in critical_imports:
            try:
                module = __import__(module_name, fromlist=[class_name])
                if hasattr(module, class_name):
                    print(f"    ✓ {module_name}.{class_name}")
                else:
                    import_errors.append(f"{module_name}.{class_name} not exported")
                    self.log_error(f"Import error: {module_name}.{class_name} not exported")
            except Exception as e:
                import_errors.append(str(e))
                self.log_error(f"Import failed: {module_name}: {e}")
        
        sys.path = original_path
        
        if import_errors:
            print(f"    ✗ {len(import_errors)} import error(s)")
        else:
            print(f"    ✓ All core imports verified")
        
        print("  [3/4] Validating governance files...")
        governance_files = [
            "cortex-brain/tier0/governance/core-rules.yaml",
            "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
        ]
        
        governance_errors = []
        for gov_file in governance_files:
            file_path = WORKSPACE_ROOT / gov_file
            if file_path.exists():
                try:
                    data = yaml.safe_load(open(file_path, 'r'))
                    if data is None:
                        governance_errors.append(f"{gov_file} is empty")
                    else:
                        print(f"    ✓ {gov_file} (valid)")
                except Exception as e:
                    governance_errors.append(f"{gov_file}: {e}")
                    self.log_error(f"Governance file error: {gov_file}: {e}")
            else:
                governance_errors.append(f"{gov_file} not found")
        
        if governance_errors:
            print(f"    ✗ {len(governance_errors)} governance error(s)")
        else:
            print(f"    ✓ All governance files valid")
        
        print("  [4/4] Database integrity check...")
        db_path = WORKSPACE_ROOT / "cortex-brain" / "database" / "governance.db"
        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                conn.close()
                print(f"    ✓ Database has {table_count} table(s)")
            except Exception as e:
                self.log_error(f"Database error: {e}")
                print(f"    ✗ Database error: {e}")
        else:
            print(f"    ⚠ Database not found (may not be initialized)")
        
        # Summary
        total_issues = len(missing_files) + len(import_errors) + len(governance_errors)
        
        print()
        if total_issues == 0:
            print("  ✅ INTEGRITY VERIFICATION PASSED - No issues detected")
            self.log_action("✅ Post-vacuum verification: All checks passed")
        else:
            print(f"  ⚠️  INTEGRITY VERIFICATION COMPLETE - {total_issues} issue(s) detected")
            self.log_action(f"⚠️  Post-vacuum verification: {total_issues} issue(s) found")
            if missing_files:
                self.log_action(f"   - Missing files: {', '.join(missing_files)}")
            if import_errors:
                self.log_action(f"   - Import errors: {len(import_errors)}")
            if governance_errors:
                self.log_action(f"   - Governance errors: {len(governance_errors)}")
    
    def execute(self):
        """Execute the full vacuum operation with all enhancements (SEQUENTIAL)"""
        try:
            print("\n" + "="*70)
            print("🔍 PHASE 0: Root Pollution Prevention")
            print("="*70)
            print("  [1/1] Checking for root-level files that should be relocated...")
            root_pollution_count = RootPollutionPrevention.auto_relocate_root_pollution(
                dry_run=self.dry_run
            )
            if root_pollution_count > 0:
                self.actions_log.append(f"Relocated {root_pollution_count} root-level files")
            
            print("\n" + "="*70)
            print("🔍 PHASE 1: Governance Violation Detection & Remediation")
            print("="*70)
            print("  [1/3] Scanning for governance violations...")
            self.scan_for_violations()
            
            print("  [2/3] Detecting duplicate files...")
            self.detect_duplicates()
            
            print("  [3/3] Executing remediation with safety checks...")
            self.execute_remediation()
            
            print("\n" + "="*70)
            print("📚 PHASE 2: Smart Document Analysis")
            print("="*70)
            self.detect_similar_documents()
            self.suggest_tier_relocations()
            
            print("\n" + "="*70)
            print("📊 PHASE 3: Summary Report")
            print("="*70)
            self.generate_report()
            
            print("\n" + "="*70)
            print("🔍 PHASE 4: Post-Vacuum Integrity Verification (NEW - Self-Learning)")
            print("="*70)
            self.verify_post_vacuum_integrity()
            print("="*70)
            
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
    parser.add_argument(
        "--audit-root",
        action="store_true",
        help="NEW (v4.0): Audit repository root for pollution (no cleanup)"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("CORTEX 6.0 VACUUM ORCHESTRATOR")
    print("="*70)
    
    # If audit-root flag is set, run audit only
    if args.audit_root:
        print("Mode: ROOT AUDIT ONLY")
        print("="*70)
        print()
        orchestrator = VacuumOrchestrator(dry_run=True)
        orchestrator.audit_root_directory()
        sys.exit(0)
    
    # Execute is opposite of dry-run
    dry_run = not args.execute
    
    print(f"Mode: {'DRY-RUN (preview only)' if dry_run else 'EXECUTE (apply changes)'}")
    print("="*70)
    print()
    
    orchestrator = VacuumOrchestrator(dry_run=dry_run)
    success = orchestrator.execute()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
