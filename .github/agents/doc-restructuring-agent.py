#!/usr/bin/env python3
"""
CORTEX Documentation Restructuring Agent
Autonomous agent for discovering, categorizing, and consolidating documentation
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.github/agents/doc-restructuring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """Classification for discovered files"""
    ROOT_DOCS = "root-level-documentation"
    SUBDIRECTORY_DOCS = "scattered-subdirectory-documentation"
    PHASE_DOCS = "phase-workspace-documentation"
    ANALYSIS_REPORTS = "analysis-reports"
    CONFIG_EXAMPLES = "configuration-examples"
    PROTECTED = "protected-files"
    OTHER = "other"


@dataclass
class DiscoveredFile:
    """Represents a discovered documentation file"""
    path: str
    category: FileCategory
    action: str  # move, archive, protect, review
    reason: str
    source_dir: str
    target_dir: str = None
    priority: int = 0  # 0=low, 1=medium, 2=high


class ProtectionFilter:
    """Manages protected files and folders that should not be moved"""
    
    PROTECTED_PATTERNS = {
        # Root critical files
        'requirements.txt',
        'pytest.ini',
        'setup.py',
        'pyproject.toml',
        'cortex-config.yaml',
        'governance.db',
        '.gitignore',
        'conftest.py',
        
        # Directories to protect
        '.git',
        '.venv',
        '__pycache__',
        '.pytest_cache',
        '.tox',
        'node_modules',
        '.vscode',
        '.idea',
        'dist',
        'build',
    }
    
    PROTECTED_PATHS = {
        '.github/workflows',
        '.github/prompts',
        '.github/agents',
        'cortex',
        'cortex_brain',
        'cortex_toolkit',
        'src',
        '.git',
        'venv',
    }
    
    @staticmethod
    def is_protected(file_path: str) -> bool:
        """Check if file should be protected from moving"""
        path = Path(file_path)
        
        # Check filename
        if path.name in ProtectionFilter.PROTECTED_PATTERNS:
            return True
        
        # Check if in protected directory
        parts = path.parts
        for protected in ProtectionFilter.PROTECTED_PATHS:
            if protected in parts:
                return True
        
        # Check extension for source files
        if path.suffix in {'.py', '.js', '.ts'}:
            # But allow docs in source dirs
            if path.parent.name not in {'docs', 'documentation'}:
                return True
        
        return False


class DocumentationScanner:
    """Scans repository for documentation files"""
    
    DOC_EXTENSIONS = {'.md', '.txt', '.rst', '.adoc'}
    CONFIG_EXTENSIONS = {'.yaml', '.yml', '.json'}
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.discovered_files: List[DiscoveredFile] = []
        self.protection_filter = ProtectionFilter()
        
    def scan(self) -> List[DiscoveredFile]:
        """Execute full repository scan"""
        logger.info(f"Starting documentation scan in {self.root_path}")
        
        # Phase 1: Root directory scan
        self._scan_root()
        
        # Phase 2: Recursive subdirectory scan
        self._scan_subdirectories()
        
        # Phase 3: Filter protected files
        self._filter_protected()
        
        logger.info(f"Scan complete. Found {len(self.discovered_files)} files")
        return self.discovered_files
    
    def _scan_root(self):
        """Scan root directory for documentation files"""
        logger.info("Phase 1: Scanning root directory")
        
        for item in self.root_path.iterdir():
            if item.is_file() and item.suffix in self.DOC_EXTENSIONS:
                if self.protection_filter.is_protected(str(item)):
                    continue
                
                category = self._categorize_file(item)
                self.discovered_files.append(DiscoveredFile(
                    path=str(item),
                    category=category,
                    action=self._get_action(category),
                    reason=f"Root-level {category.value}",
                    source_dir=str(self.root_path),
                    target_dir=self._get_target_dir(category)
                ))
    
    def _scan_subdirectories(self):
        """Recursively scan subdirectories"""
        logger.info("Phase 2: Scanning subdirectories")
        
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache', 'node_modules'}
        
        for root, dirs, files in os.walk(self.root_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip protected files
                if self.protection_filter.is_protected(str(file_path)):
                    continue
                
                # Look for documentation files
                if file_path.suffix in self.DOC_EXTENSIONS or file_path.suffix in self.CONFIG_EXTENSIONS:
                    category = self._categorize_file(file_path)
                    
                    self.discovered_files.append(DiscoveredFile(
                        path=str(file_path),
                        category=category,
                        action=self._get_action(category),
                        reason=self._get_reason(file_path, category),
                        source_dir=str(file_path.parent),
                        target_dir=self._get_target_dir(category)
                    ))
    
    def _filter_protected(self):
        """Remove protected files from discovered list"""
        original_count = len(self.discovered_files)
        self.discovered_files = [
            f for f in self.discovered_files 
            if not self.protection_filter.is_protected(f.path)
        ]
        filtered = original_count - len(self.discovered_files)
        if filtered > 0:
            logger.info(f"Filtered {filtered} protected files")
    
    def _categorize_file(self, file_path: Path) -> FileCategory:
        """Determine file category based on location and name"""
        
        # Check for special names
        if file_path.name in {'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}:
            return FileCategory.ROOT_DOCS
        
        # Check for phase/workspace
        if '_workspaces' in file_path.parts or 'phases' in file_path.parts:
            if 'report' in file_path.name.lower() or 'analysis' in file_path.name.lower():
                return FileCategory.ANALYSIS_REPORTS
            return FileCategory.PHASE_DOCS
        
        # Check for analysis/reports
        if any(keyword in file_path.name.lower() for keyword in ['analysis', 'report', 'findings', 'summary']):
            return FileCategory.ANALYSIS_REPORTS
        
        # Check for config examples
        if file_path.suffix in self.CONFIG_EXTENSIONS and 'example' in file_path.name.lower():
            return FileCategory.CONFIG_EXAMPLES
        
        # Subdirectory READMEs
        if file_path.name == 'README.md':
            return FileCategory.SUBDIRECTORY_DOCS
        
        return FileCategory.OTHER
    
    def _get_action(self, category: FileCategory) -> str:
        """Determine action based on category"""
        actions = {
            FileCategory.ROOT_DOCS: "review",
            FileCategory.SUBDIRECTORY_DOCS: "move",
            FileCategory.PHASE_DOCS: "archive",
            FileCategory.ANALYSIS_REPORTS: "archive",
            FileCategory.CONFIG_EXAMPLES: "move",
            FileCategory.PROTECTED: "protect",
            FileCategory.OTHER: "review"
        }
        return actions.get(category, "review")
    
    def _get_reason(self, file_path: Path, category: FileCategory) -> str:
        """Generate reason for categorization"""
        reasons = {
            FileCategory.ROOT_DOCS: "Root-level documentation candidate",
            FileCategory.SUBDIRECTORY_DOCS: "Scattered documentation in subdirectories",
            FileCategory.PHASE_DOCS: "Phase/workspace documentation for archival",
            FileCategory.ANALYSIS_REPORTS: "Analysis or report for archival",
            FileCategory.CONFIG_EXAMPLES: "Configuration example for documentation",
            FileCategory.PROTECTED: "Protected system file",
            FileCategory.OTHER: "Requires manual review"
        }
        return reasons.get(category, "Unknown")
    
    def _get_target_dir(self, category: FileCategory) -> str:
        """Get target directory for file based on category"""
        targets = {
            FileCategory.ROOT_DOCS: "docs/02-architecture",
            FileCategory.SUBDIRECTORY_DOCS: "docs/05-reference",
            FileCategory.PHASE_DOCS: "docs/_archive/workspaces",
            FileCategory.ANALYSIS_REPORTS: "docs/_archive/reports",
            FileCategory.CONFIG_EXAMPLES: "docs/04-guides",
            FileCategory.PROTECTED: None,
            FileCategory.OTHER: "docs/05-reference"
        }
        return targets.get(category, None)


class DocumentationAnalyzer:
    """Analyzes discovered files and generates recommendations"""
    
    def __init__(self, discovered_files: List[DiscoveredFile]):
        self.files = discovered_files
        self.analysis = {}
    
    def analyze(self) -> Dict:
        """Analyze discovered files and generate statistics"""
        logger.info("Analyzing discovered files")
        
        # Group by category
        by_category = {}
        for file in self.files:
            if file.category not in by_category:
                by_category[file.category] = []
            by_category[file.category].append(file)
        
        # Generate analysis
        self.analysis = {
            'total_files': len(self.files),
            'by_category': {
                cat.value: len(files) 
                for cat, files in by_category.items()
            },
            'by_action': self._group_by_action(),
            'priority_files': self._identify_priority_files(),
            'statistics': self._calculate_statistics()
        }
        
        return self.analysis
    
    def _group_by_action(self) -> Dict[str, int]:
        """Count files by action"""
        actions = {}
        for file in self.files:
            actions[file.action] = actions.get(file.action, 0) + 1
        return actions
    
    def _identify_priority_files(self) -> List[str]:
        """Identify high-priority files"""
        priority_keywords = {'architecture', 'api', 'getting-started', 'deployment', 'tutorial'}
        priority = []
        
        for file in self.files:
            if any(keyword in file.path.lower() for keyword in priority_keywords):
                priority.append(file.path)
        
        return sorted(priority)[:10]
    
    def _calculate_statistics(self) -> Dict:
        """Calculate additional statistics"""
        return {
            'move_count': len([f for f in self.files if f.action == 'move']),
            'archive_count': len([f for f in self.files if f.action == 'archive']),
            'review_count': len([f for f in self.files if f.action == 'review']),
            'protect_count': len([f for f in self.files if f.action == 'protect']),
        }


class AutonomousOrchestrator:
    """Orchestrates the autonomous documentation restructuring workflow"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.scanner = DocumentationScanner(root_path)
        self.analyzer = None
        self.execution_log = {
            'timestamp': datetime.now().isoformat(),
            'phases': {}
        }
    
    def run(self):
        """Execute autonomous workflow"""
        logger.info("=" * 80)
        logger.info("CORTEX Documentation Restructuring Agent - AUTONOMOUS MODE")
        logger.info("=" * 80)
        
        # Phase 1: Scan
        discovered = self.scanner.scan()
        self.execution_log['phases']['scan'] = {
            'status': 'complete',
            'files_found': len(discovered)
        }
        
        # Phase 2: Analyze
        self.analyzer = DocumentationAnalyzer(discovered)
        analysis = self.analyzer.analyze()
        self.execution_log['phases']['analysis'] = {
            'status': 'complete',
            'analysis': analysis
        }
        
        logger.info("\n" + self._format_analysis(analysis))
        
        # Phase 3: Execute (autonomous - no user input needed)
        self._execute_restructuring(discovered)
        
        # Phase 4: Generate report
        self._generate_report(discovered, analysis)
        
        logger.info("=" * 80)
        logger.info("AUTONOMOUS WORKFLOW COMPLETE")
        logger.info("=" * 80)
    
    def _execute_restructuring(self, files: List[DiscoveredFile]):
        """Execute file movements and reorganization"""
        logger.info("\nPhase 3: Executing restructuring")
        
        move_count = 0
        archive_count = 0
        review_count = 0
        
        for file in files:
            if file.action == 'move' and file.target_dir:
                self._move_file(file)
                move_count += 1
            elif file.action == 'archive' and file.target_dir:
                self._archive_file(file)
                archive_count += 1
            elif file.action == 'review':
                review_count += 1
        
        self.execution_log['phases']['execution'] = {
            'status': 'complete',
            'moved': move_count,
            'archived': archive_count,
            'review_pending': review_count
        }
        
        logger.info(f"Moved: {move_count}, Archived: {archive_count}, Review pending: {review_count}")
    
    def _move_file(self, file: DiscoveredFile):
        """Move file to target directory"""
        try:
            source = Path(file.path)
            target_dir = Path(file.target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / source.name
            
            shutil.move(str(source), str(target))
            logger.info(f"Moved: {file.path} -> {target}")
        except Exception as e:
            logger.error(f"Error moving {file.path}: {e}")
    
    def _archive_file(self, file: DiscoveredFile):
        """Archive file with timestamp"""
        try:
            source = Path(file.path)
            target_dir = Path(file.target_dir)
            
            # Add timestamp to archived files
            timestamp = datetime.now().strftime('%Y%m%d')
            name_parts = source.name.rsplit('.', 1)
            archived_name = f"{name_parts[0]}-archived-{timestamp}.{name_parts[1]}" if len(name_parts) > 1 else f"{source.name}-archived-{timestamp}"
            
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / archived_name
            
            shutil.move(str(source), str(target))
            logger.info(f"Archived: {file.path} -> {target}")
        except Exception as e:
            logger.error(f"Error archiving {file.path}: {e}")
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis for display"""
        lines = ["ANALYSIS RESULTS", "-" * 40]
        lines.append(f"Total files found: {analysis['total_files']}")
        lines.append("\nBy Category:")
        for cat, count in analysis['by_category'].items():
            lines.append(f"  - {cat}: {count}")
        lines.append("\nBy Action:")
        for action, count in analysis['by_action'].items():
            lines.append(f"  - {action}: {count}")
        return "\n".join(lines)
    
    def _generate_report(self, files: List[DiscoveredFile], analysis: Dict):
        """Generate comprehensive report"""
        report_path = self.root_path / '.github' / 'agents' / 'doc-restructuring-report.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'files_discovered': [asdict(f) for f in files],
            'execution': self.execution_log['phases'].get('execution', {})
        }
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report generated: {report_path}")


def main():
    """Main entry point"""
    # Get workspace root
    root = os.environ.get('CORTEX_ROOT', '/Users/asifhussain/PROJECTS/CORTEX')
    if len(sys.argv) > 1:
        root = sys.argv[1]
    
    # Run autonomous orchestrator
    orchestrator = AutonomousOrchestrator(root)
    orchestrator.run()


if __name__ == '__main__':
    main()
