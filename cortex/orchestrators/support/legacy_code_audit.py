"""
Phase 61: Legacy Code Audit Implementation

Detects and categorizes legacy code:
- DEPRECATED: Code marked with @deprecated or deprecated() calls
- DUPLICATE: Code violating CORE-035 (duplicate detection)
- ORPHANED: Code with no imports (orphaned modules)
- SUPERSEDED: Code superseded by newer implementations

AC_START: AC-PHASE61-002
Description: Legacy Code Audit implementation
"""

import ast
from pathlib import Path
from typing import Set, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict
import yaml


class LegacyCodeCategory(Enum):
    """Legacy code categorization"""
    DEPRECATED = "deprecated"
    DUPLICATE = "duplicate"
    ORPHANED = "orphaned"
    SUPERSEDED = "superseded"


@dataclass
class LegacyCodeIssue:
    """Represents detected legacy code issue"""
    file_path: Path
    category: LegacyCodeCategory
    severity: str  # "LOW", "MEDIUM", "HIGH"
    reason: str
    recommendation: str
    confidence_score: float
    
    def __hash__(self):
        return hash(self.file_path)
    
    def __eq__(self, other):
        if not isinstance(other, LegacyCodeIssue):
            return False
        return self.file_path == other.file_path


class LegacyCodeAudit:
    """Comprehensive legacy code audit engine"""
    
    # Patterns for deprecated detection
    DEPRECATED_PATTERNS = [
        r'@deprecated',
        r'@Deprecated',
        r'deprecated\(',
        r'warn.*deprecated',
        r'DEPRECATED\s*=\s*True',
    ]
    
    DEPRECATED_COMMENTS = [
        'TODO: remove',
        'FIXME: delete',
        'deprecated since',
        'no longer used',
        'obsolete',
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize audit engine"""
        self.repo_root = Path(repo_root)
        self.issues: List[LegacyCodeIssue] = []
        self.python_files: Set[Path] = set()
        self.file_imports: Dict[Path, Set[str]] = defaultdict(set)
        self.module_definitions: Dict[str, Path] = {}
        self.content_hashes: Dict[Path, str] = {}
    
    def scan_repository(self) -> List[LegacyCodeIssue]:
        """Scan repository for legacy code"""
        self.issues = []
        
        # Collect all Python files
        self._collect_python_files()
        
        # Analyze imports and definitions
        self._analyze_imports_and_definitions()
        
        # Detect each category
        self.issues.extend(self.detect_deprecated_code())
        self.issues.extend(self.detect_duplicates())
        self.issues.extend(self.detect_orphaned_code())
        self.issues.extend(self.detect_superseded_code())
        
        return self.issues
    
    def _collect_python_files(self) -> None:
        """Collect all .py files in repository"""
        for py_file in self.repo_root.rglob("*.py"):
            # Skip test files and hidden directories
            if "test" not in str(py_file) and not any(p.startswith(".") for p in py_file.parts):
                self.python_files.add(py_file)
    
    def _analyze_imports_and_definitions(self) -> None:
        """Analyze imports and module definitions"""
        for file_path in self.python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    # Extract module name
                    module_name = self._path_to_module(file_path)
                    self.module_definitions[module_name] = file_path
                    
                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self.file_imports[file_path].add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self.file_imports[file_path].add(node.module)
                    
                    # Store content hash for duplicate detection
                    self.content_hashes[file_path] = self._hash_content(content)
            except Exception:
                pass  # Skip files with parse errors
    
    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        relative = file_path.relative_to(self.repo_root)
        module_parts = list(relative.parts[:-1])  # Exclude filename
        module_parts.append(relative.stem)  # Add filename without .py
        return ".".join(module_parts)
    
    def _hash_content(self, content: str) -> str:
        """Create hash of code content (simplified)"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def categorize_issue(self, file_path: Path) -> LegacyCodeCategory:
        """Determine category of legacy code"""
        if self._is_deprecated(file_path):
            return LegacyCodeCategory.DEPRECATED
        elif self._is_duplicate(file_path):
            return LegacyCodeCategory.DUPLICATE
        elif self._is_orphaned(file_path):
            return LegacyCodeCategory.ORPHANED
        else:
            return LegacyCodeCategory.SUPERSEDED
    
    def _is_deprecated(self, file_path: Path) -> bool:
        """Check if file is deprecated"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for deprecation markers
                for pattern in self.DEPRECATED_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
                
                # Check for comments
                for comment_text in self.DEPRECATED_COMMENTS:
                    if comment_text in content.lower():
                        return True
        except Exception:
            pass
        
        return False
    
    def _is_duplicate(self, file_path: Path) -> bool:
        """Check if file is duplicate code"""
        if file_path not in self.content_hashes:
            return False
        
        file_hash = self.content_hashes[file_path]
        
        # Count how many files have same hash
        duplicate_count = sum(
            1 for h in self.content_hashes.values()
            if h == file_hash
        )
        
        return duplicate_count > 1
    
    def _is_orphaned(self, file_path: Path) -> bool:
        """Check if file has no imports (orphaned)"""
        # Count how many other files import this module
        module_name = self._path_to_module(file_path)
        import_count = 0
        
        for other_file, imports in self.file_imports.items():
            if other_file != file_path:
                if any(module_name in imp for imp in imports):
                    import_count += 1
        
        # Orphaned if no imports and not in active directories
        return import_count == 0 and not self._is_active_module(file_path)
    
    def _is_active_module(self, file_path: Path) -> bool:
        """Check if module is in active directories"""
        active_dirs = [
            'orchestrators',
            'core',
            'api',
            'lens',
            'governance',
        ]
        
        path_str = str(file_path)
        return any(active_dir in path_str for active_dir in active_dirs)
    
    def detect_deprecated_code(self) -> List[LegacyCodeIssue]:
        """Detect code marked as @deprecated"""
        issues = []
        
        for file_path in self.python_files:
            if self._is_deprecated(file_path):
                issues.append(LegacyCodeIssue(
                    file_path=file_path,
                    category=LegacyCodeCategory.DEPRECATED,
                    severity="MEDIUM",
                    reason="Code marked with @deprecated or similar marker",
                    recommendation="Schedule for removal with deprecation notice",
                    confidence_score=0.95
                ))
        
        return issues
    
    def detect_duplicates(self) -> List[LegacyCodeIssue]:
        """Detect duplicate code (CORE-035)"""
        issues = []
        seen_hashes: Dict[str, Path] = {}
        
        for file_path, content_hash in self.content_hashes.items():
            if content_hash in seen_hashes:
                issues.append(LegacyCodeIssue(
                    file_path=file_path,
                    category=LegacyCodeCategory.DUPLICATE,
                    severity="HIGH",
                    reason=f"Identical code to {seen_hashes[content_hash]}",
                    recommendation="Consolidate or remove duplicate",
                    confidence_score=0.99
                ))
            else:
                seen_hashes[content_hash] = file_path
        
        return issues
    
    def detect_orphaned_code(self) -> List[LegacyCodeIssue]:
        """Detect orphaned code with no imports"""
        issues = []
        
        for file_path in self.python_files:
            if self._is_orphaned(file_path):
                issues.append(LegacyCodeIssue(
                    file_path=file_path,
                    category=LegacyCodeCategory.ORPHANED,
                    severity="MEDIUM",
                    reason="No other files import this module",
                    recommendation="Investigate usage or mark for removal",
                    confidence_score=0.85
                ))
        
        return issues
    
    def detect_superseded_code(self) -> List[LegacyCodeIssue]:
        """Detect code superseded by newer implementations"""
        issues = []
        
        # Look for v1/v2 patterns or old/new naming
        version_patterns = [
            (r'_v1\.py$', r'_v2\.py$'),
            (r'_old\.py$', r'_new\.py$'),
            (r'legacy_', r'new_'),
        ]
        
        for file_path in self.python_files:
            for old_pattern, new_pattern in version_patterns:
                if re.search(old_pattern, str(file_path)):
                    # Check if newer version exists
                    new_path = Path(str(file_path).replace(
                        old_pattern, new_pattern
                    ))
                    if new_path.exists():
                        issues.append(LegacyCodeIssue(
                            file_path=file_path,
                            category=LegacyCodeCategory.SUPERSEDED,
                            severity="HIGH",
                            reason="Newer version available",
                            recommendation="Migrate code to new version and remove",
                            confidence_score=0.90
                        ))
        
        return issues
    
    def generate_removal_candidates(self) -> List[LegacyCodeIssue]:
        """Filter and return safe-to-remove items"""
        candidates = []
        
        for issue in self.issues:
            # High confidence + not critical
            if issue.confidence_score > 0.80:
                if issue.category in [
                    LegacyCodeCategory.DEPRECATED,
                    LegacyCodeCategory.SUPERSEDED,
                ]:
                    candidates.append(issue)
        
        return candidates


class RemovalApprovalWorkflow:
    """User approval workflow for code removal"""
    
    def __init__(self):
        """Initialize workflow"""
        self.pending_removals: List[LegacyCodeIssue] = []
        self.approved_removals: List[LegacyCodeIssue] = []
        self.rejected_removals: List[LegacyCodeIssue] = []
    
    def submit_for_approval(self, issue: LegacyCodeIssue) -> None:
        """Submit item for user approval"""
        if issue not in self.pending_removals:
            self.pending_removals.append(issue)
    
    def approve_removal(self, issue: LegacyCodeIssue) -> None:
        """Mark as approved for removal"""
        if issue in self.pending_removals:
            self.pending_removals.remove(issue)
            self.approved_removals.append(issue)
    
    def reject_removal(self, issue: LegacyCodeIssue, reason: str) -> None:
        """Reject removal with reason"""
        if issue in self.pending_removals:
            self.pending_removals.remove(issue)
            self.rejected_removals.append(issue)
    
    def get_pending_approvals(self) -> List[LegacyCodeIssue]:
        """Get items awaiting approval"""
        return list(self.pending_removals)


class AuditReport:
    """Comprehensive audit report"""
    
    def __init__(self):
        """Initialize report"""
        self.deprecated_count = 0
        self.duplicate_count = 0
        self.orphaned_count = 0
        self.superseded_count = 0
        self.total_issues = 0
        self.removal_candidates = 0
        self.issues: List[LegacyCodeIssue] = []
    
    def from_audit(self, audit: LegacyCodeAudit) -> None:
        """Build report from audit results"""
        self.issues = audit.issues
        self.total_issues = len(audit.issues)
        
        for issue in audit.issues:
            if issue.category == LegacyCodeCategory.DEPRECATED:
                self.deprecated_count += 1
            elif issue.category == LegacyCodeCategory.DUPLICATE:
                self.duplicate_count += 1
            elif issue.category == LegacyCodeCategory.ORPHANED:
                self.orphaned_count += 1
            elif issue.category == LegacyCodeCategory.SUPERSEDED:
                self.superseded_count += 1
        
        self.removal_candidates = sum(
            1 for issue in audit.issues
            if issue.confidence_score > 0.80
        )
    
    def generate_report(self) -> Dict[str, object]:
        """Generate audit summary report"""
        return {
            "total_issues": self.total_issues,
            "deprecated": self.deprecated_count,
            "duplicate": self.duplicate_count,
            "orphaned": self.orphaned_count,
            "superseded": self.superseded_count,
            "removal_candidates": self.removal_candidates,
            "high_priority": sum(
                1 for issue in self.issues
                if issue.severity == "HIGH"
            ),
            "medium_priority": sum(
                1 for issue in self.issues
                if issue.severity == "MEDIUM"
            ),
            "low_priority": sum(
                1 for issue in self.issues
                if issue.severity == "LOW"
            ),
        }
    
    def export_to_yaml(self, output_path: Path) -> None:
        """Export audit results to YAML"""
        import yaml
        
        report_dict = self.generate_report()
        
        issues_list = []
        for issue in self.issues:
            issues_list.append({
                'file': str(issue.file_path),
                'category': issue.category.value,
                'severity': issue.severity,
                'confidence': issue.confidence_score,
                'reason': issue.reason,
                'recommendation': issue.recommendation,
            })
        
        output_data = {
            'summary': report_dict,
            'issues': issues_list,
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(output_data, f, default_flow_style=False)


# AC_COMPLETE: AC-PHASE61-002 ✅
