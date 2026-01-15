"""
CORTEX Vacuum Analyzer

Phase 1: Non-destructive analysis of repository structure and file organization.
Generates migration plans without modifying any files.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import hashlib


@dataclass
class FileReference:
    """Represents a reference to a file in another file."""
    source_file: str
    target_file: str
    line_number: int
    line_content: str
    ref_type: str  # 'import', 'link', 'comment', 'yaml'
    old_reference: str
    new_reference: str = ""


@dataclass
class FileIssue:
    """Represents an issue with a file."""
    file_path: str
    issue_type: str  # 'name_violation', 'duplicate', 'backup', 'temp', 'unclear_location'
    severity: str  # 'error', 'warning', 'info'
    description: str
    suggested_action: str


@dataclass
class ClassificationResult:
    """Result of classifying a file."""
    file_path: str
    current_location: str
    suggested_location: str
    suggested_name: str
    reasoning: str
    confidence: float  # 0.0 to 1.0


@dataclass
class MigrationPlan:
    """Complete migration plan for a file."""
    source_path: str
    destination_path: str
    is_delete: bool = False
    is_rename: bool = False
    is_move: bool = False
    is_consolidate: bool = False
    consolidated_with: List[str] = field(default_factory=list)
    references_to_update: List[FileReference] = field(default_factory=list)
    reason: str = ""


class CortexVacuumAnalyzer:
    """
    Analyzes CORTEX repository structure and generates migration plans.
    
    This tool:
    - Scans all files and folders
    - Identifies naming violations
    - Detects redundant/backup files
    - Finds all cross-file references
    - Proposes file classifications
    - Generates a complete migration plan
    - Is 100% non-destructive
    """

    def __init__(self, repo_root: str):
        """Initialize the analyzer with repository root."""
        self.repo_root = Path(repo_root)
        self.all_files: Dict[str, Path] = {}
        self.all_folders: Dict[str, Path] = {}
        self.references: List[FileReference] = []
        self.issues: List[FileIssue] = []
        self.classifications: List[ClassificationResult] = []
        self.migration_plans: List[MigrationPlan] = []

    def analyze(self) -> Dict:
        """Execute full analysis pipeline."""
        print(f"🔍 Starting CORTEX Vacuum Analysis...")
        print(f"   Root: {self.repo_root}")

        # Phase 1: Inventory
        self._scan_repository()
        print(f"   ✓ Scanned {len(self.all_files)} files, {len(self.all_folders)} folders")

        # Phase 2: Identify issues
        self._identify_file_issues()
        print(f"   ✓ Found {len(self.issues)} issues")

        # Phase 3: Find references
        self._find_all_references()
        print(f"   ✓ Found {len(self.references)} cross-file references")

        # Phase 4: Classify files
        self._classify_files()
        print(f"   ✓ Classified {len(self.classifications)} files")

        # Phase 5: Generate migration plans
        self._generate_migration_plans()
        print(f"   ✓ Generated {len(self.migration_plans)} migration plans")

        return self._compile_report()

    def _scan_repository(self) -> None:
        """Recursively scan all files and folders."""
        ignore_patterns = {
            '__pycache__', '.pytest_cache', '.git', '.venv', 'venv',
            '.DS_Store', '*.pyc', '*.egg-info', 'node_modules'
        }

        for root, dirs, files in os.walk(self.repo_root):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]

            # Process files
            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.repo_root)
                self.all_files[str(rel_path)] = file_path

            # Process folders (excluding root)
            if root != str(self.repo_root):
                folder_path = Path(root)
                rel_path = folder_path.relative_to(self.repo_root)
                self.all_folders[str(rel_path)] = folder_path

    def _identify_file_issues(self) -> None:
        """Identify naming violations, backups, duplicates, etc."""
        # Check for backup/temp files
        backup_patterns = [
            r'.*\.(bak|backup|tmp|temp)$',
            r'.*-(old|new|fixed|enhanced|backup|temp|v\d+).*',
            r'.*\.pyc$',
        ]

        for file_path in self.all_files.keys():
            # Check naming violations
            filename = Path(file_path).name
            self._check_filename_compliance(file_path, filename)

            # Check for backup files
            for pattern in backup_patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    self.issues.append(FileIssue(
                        file_path=file_path,
                        issue_type='backup',
                        severity='error',
                        description=f"Backup/temp file: {filename}",
                        suggested_action='DELETE'
                    ))
                    break

    def _check_filename_compliance(self, file_path: str, filename: str) -> None:
        """Check if filename follows kebab-case convention and length limits."""
        # Skip certain files
        if filename in {'pytest.ini', 'requirements.txt', 'README.md', '.gitignore'}:
            return

        # Check for uppercase/mixed case
        if filename != filename.lower():
            self.issues.append(FileIssue(
                file_path=file_path,
                issue_type='name_violation',
                severity='warning',
                description=f"Not lowercase: {filename}",
                suggested_action=f'Rename to: {filename.lower()}'
            ))

        # Check for spaces
        if ' ' in filename:
            self.issues.append(FileIssue(
                file_path=file_path,
                issue_type='name_violation',
                severity='warning',
                description=f"Contains spaces: {filename}",
                suggested_action=f'Rename to: {filename.replace(" ", "-")}'
            ))

        # Check for excessive length
        name_no_ext = Path(filename).stem
        if len(name_no_ext) > 20:
            self.issues.append(FileIssue(
                file_path=file_path,
                issue_type='name_violation',
                severity='warning',
                description=f"Filename too long ({len(name_no_ext)} chars): {filename}",
                suggested_action=f'Abbreviate to ≤20 chars'
            ))

    def _find_all_references(self) -> None:
        """Find all cross-file references."""
        for file_path in self.all_files.keys():
            full_path = self.all_files[file_path]

            # Skip binary files
            if not self._is_text_file(full_path):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    self._extract_references_from_line(file_path, line_num, line)
            except Exception as e:
                print(f"   ⚠ Error reading {file_path}: {e}")

    def _extract_references_from_line(self, source_file: str, line_num: int, line: str) -> None:
        """Extract references from a single line."""
        line_stripped = line.strip()

        # Markdown links: [text](path/to/file)
        markdown_links = re.finditer(r'\]\(([\w\-./]+\.(?:md|yaml|yml|json|py))\)', line)
        for match in markdown_links:
            target = match.group(1)
            self.references.append(FileReference(
                source_file=source_file,
                target_file=target,
                line_number=line_num,
                line_content=line_stripped,
                ref_type='link',
                old_reference=target
            ))

        # Python imports: from X import Y, import X
        import_match = re.match(r'\s*(?:from|import)\s+([\w\-.]+)', line_stripped)
        if import_match:
            module = import_match.group(1)
            self.references.append(FileReference(
                source_file=source_file,
                target_file=module,
                line_number=line_num,
                line_content=line_stripped,
                ref_type='import',
                old_reference=module
            ))

        # YAML file references: - file: path/to/file or path: path/to/file
        yaml_match = re.search(r'(?:file|path):\s*(["\']?)(.+?)\1(?:\s|$)', line_stripped)
        if yaml_match:
            target = yaml_match.group(2)
            if '.' in target:  # Likely a file reference
                self.references.append(FileReference(
                    source_file=source_file,
                    target_file=target,
                    line_number=line_num,
                    line_content=line_stripped,
                    ref_type='yaml',
                    old_reference=target
                ))

        # Code comments referencing files: # See: path/to/file
        comment_match = re.search(r'#\s*(?:See|see|Ref|ref):\s*([\w\-./]+)', line_stripped)
        if comment_match:
            target = comment_match.group(1)
            self.references.append(FileReference(
                source_file=source_file,
                target_file=target,
                line_number=line_num,
                line_content=line_stripped,
                ref_type='comment',
                old_reference=target
            ))

    def _classify_files(self) -> None:
        """Classify files into their appropriate locations."""
        for file_path in sorted(self.all_files.keys()):
            if self._is_marked_for_deletion(file_path):
                continue

            classification = self._classify_single_file(file_path)
            if classification:
                self.classifications.append(classification)

    def _classify_single_file(self, file_path: str) -> Optional[ClassificationResult]:
        """Classify a single file to its suggested location."""
        current_dir = str(Path(file_path).parent)
        filename = Path(file_path).name
        name_stem = Path(filename).stem
        ext = Path(filename).suffix

        # Skip files already in correct locations
        if self._is_in_correct_location(file_path):
            return None

        dest_location, reasoning = self._determine_destination(file_path)
        suggested_name = self._suggest_filename(name_stem, ext)

        return ClassificationResult(
            file_path=file_path,
            current_location=current_dir,
            suggested_location=dest_location,
            suggested_name=suggested_name,
            reasoning=reasoning,
            confidence=0.85
        )

    def _determine_destination(self, file_path: str) -> Tuple[str, str]:
        """Determine the destination folder for a file."""
        filename = Path(file_path).name
        ext = Path(filename).suffix.lower()

        # Executive docs
        if filename.startswith('EXECUTIVE'):
            return 'docs/executive', 'Executive documentation'

        # Phase docs
        if filename.startswith('PHASE'):
            return 'docs/phases', 'Phase documentation'

        # Review docs
        if filename.startswith('REVIEW') or 'review' in filename.lower():
            return 'docs/reviews', 'Review documentation'

        # Status docs
        if 'status' in filename.lower() and filename.endswith('.md'):
            return 'docs', 'Status documentation'

        # Reports
        if filename.endswith('REPORT.md') or filename.endswith('ANALYSIS.md'):
            return 'reports', 'Report or analysis document'

        # Completion reports
        if 'completion' in filename.lower() and filename.endswith('.md'):
            return 'reports', 'Completion report'

        # Handoff docs
        if 'handoff' in filename.lower():
            return 'reports', 'Handoff documentation'

        # Python scripts in root
        if ext == '.py' and str(Path(file_path).parent) == '.':
            return 'scripts', 'Utility script'

        # Config files
        if filename in {'pytest.ini', 'requirements.txt'}:
            return '.', 'Project configuration'

        # JSON/YAML in root
        if ext in {'.json', '.yaml', '.yml'} and str(Path(file_path).parent) == '.':
            # Check content
            if 'rollback' in filename.lower():
                return 'cortex-brain/audit-logs', 'Rollback history'
            return 'config', 'Configuration file'

        # Default: keep in current location
        return str(Path(file_path).parent), 'No relocation needed'

    def _suggest_filename(self, name_stem: str, ext: str) -> str:
        """Suggest a kebab-case filename."""
        # Remove common adjectives
        remove_words = {'old', 'new', 'fixed', 'enhanced', 'current', 'latest', 'final', 'draft'}

        # Split and clean
        words = re.split(r'[-_\s]+', name_stem.lower())
        words = [w for w in words if w and w not in remove_words]

        # Abbreviate long words
        abbrev = {
            'completion': 'completion',
            'completion': 'completion',
            'verification': 'verify',
            'implementation': 'impl',
            'executive': 'exec',
            'analysis': 'analysis',
            'report': 'report',
        }

        words = [abbrev.get(w, w) for w in words]

        # Join
        suggested = '-'.join(words)

        # Truncate if too long
        if len(suggested) > 20:
            suggested = suggested[:17] + '...'  # Will be adjusted manually

        return suggested + ext

    def _is_marked_for_deletion(self, file_path: str) -> bool:
        """Check if file should be deleted."""
        for issue in self.issues:
            if issue.file_path == file_path and issue.issue_type in {'backup', 'duplicate'}:
                return True
        return False

    def _is_in_correct_location(self, file_path: str) -> bool:
        """Check if file is already in correct location."""
        # Implementation simplified - in production would be more sophisticated
        return False

    def _is_text_file(self, path: Path) -> bool:
        """Determine if file is text-readable."""
        text_extensions = {
            '.py', '.md', '.txt', '.yaml', '.yml', '.json', '.ini',
            '.toml', '.cfg', '.conf', '.sh', '.bash', '.zsh', '.fish',
            '.sql', '.js', '.ts', '.jsx', '.tsx', '.html', '.css'
        }
        return path.suffix.lower() in text_extensions

    def _generate_migration_plans(self) -> None:
        """Generate migration plans for all identified changes."""
        # Plans for files marked for deletion
        for issue in self.issues:
            if issue.issue_type == 'backup':
                plan = MigrationPlan(
                    source_path=issue.file_path,
                    destination_path='',
                    is_delete=True,
                    reason=f"Backup/temp file: {issue.description}"
                )
                self.migration_plans.append(plan)

        # Plans for files needing reclassification
        for classification in self.classifications:
            if classification.suggested_location != classification.current_location:
                new_path = str(Path(classification.suggested_location) / classification.suggested_name)
                plan = MigrationPlan(
                    source_path=classification.file_path,
                    destination_path=new_path,
                    is_move=True,
                    is_rename=classification.suggested_name != Path(classification.file_path).name,
                    references_to_update=self._get_references_for_file(classification.file_path),
                    reason=classification.reasoning
                )
                self.migration_plans.append(plan)

    def _get_references_for_file(self, file_path: str) -> List[FileReference]:
        """Get all references to a specific file."""
        return [ref for ref in self.references if ref.target_file in file_path or file_path in ref.target_file]

    def _compile_report(self) -> Dict:
        """Compile comprehensive analysis report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'repo_root': str(self.repo_root),
            'summary': {
                'total_files': len(self.all_files),
                'total_folders': len(self.all_folders),
                'issues_found': len(self.issues),
                'references_found': len(self.references),
                'files_to_move': sum(1 for p in self.migration_plans if p.is_move),
                'files_to_delete': sum(1 for p in self.migration_plans if p.is_delete),
                'files_to_rename': sum(1 for p in self.migration_plans if p.is_rename),
            },
            'issues': [asdict(issue) for issue in self.issues],
            'references': [asdict(ref) for ref in self.references],
            'classifications': [asdict(c) for c in self.classifications],
            'migration_plans': [asdict(plan) for plan in self.migration_plans],
            'statistics': self._calculate_statistics(),
        }

    def _calculate_statistics(self) -> Dict:
        """Calculate statistics about the analysis."""
        return {
            'naming_violations': sum(1 for i in self.issues if i.issue_type == 'name_violation'),
            'backup_files': sum(1 for i in self.issues if i.issue_type == 'backup'),
            'average_references_per_file': len(self.references) / max(len(self.all_files), 1),
            'classification_confidence_avg': sum(c.confidence for c in self.classifications) / max(len(self.classifications), 1),
        }


def run_analysis(repo_root: str, output_dir: Optional[str] = None) -> Dict:
    """
    Run complete analysis and save results.
    
    Args:
        repo_root: Root directory of CORTEX repository
        output_dir: Directory to save analysis results
        
    Returns:
        Analysis report dictionary
    """
    analyzer = CortexVacuumAnalyzer(repo_root)
    report = analyzer.analyze()

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save report JSON
        with open(output_path / 'analysis-report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Save migration plan JSON
        with open(output_path / 'migration-plan.json', 'w') as f:
            json.dump({
                'timestamp': report['timestamp'],
                'plans': report['migration_plans']
            }, f, indent=2, default=str)

        # Save reference map
        with open(output_path / 'reference-map.json', 'w') as f:
            json.dump({
                'timestamp': report['timestamp'],
                'references': report['references']
            }, f, indent=2, default=str)

        print(f"\n✓ Analysis saved to {output_path}")
        print(f"  - analysis-report.json")
        print(f"  - migration-plan.json")
        print(f"  - reference-map.json")

    return report
