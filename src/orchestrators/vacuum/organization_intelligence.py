"""
Organization Intelligence Engine for Vacuum Orchestrator v2.

Provides intelligent file organization and folder structure optimization
based on CORTEX standards and best practices.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class OrganizationRule:
    """Organization rule for file placement."""
    name: str
    patterns: List[str]
    target_folder: str
    priority: int
    description: str


class FolderStructureOptimizer:
    """Optimize folder structure according to CORTEX standards."""
    
    # CORTEX standard folder structure
    CORTEX_STRUCTURE = {
        'cortex-brain/documents/': {
            'subfolders': [
                'reports/', 'analysis/', 'summaries/', 'investigations/',
                'planning/', 'implementation-guides/', 'architecture/',
                'governance/', 'reviews/', 'standards/', 'updates/',
                'learning/', 'features/', 'diagrams/'
            ],
            'file_types': ['.md', '.txt', '.rst', '.pdf']
        },
        'cortex-brain/config/': {
            'subfolders': ['schemas/', 'templates/'],
            'file_types': ['.yaml', '.yml', '.json', '.toml', '.ini']
        },
        'cortex-brain/archives/': {
            'subfolders': ['backups/', 'deprecated/', 'obsolete/', 'planning/'],
            'file_types': ['*']
        },
        'cortex-brain/manifests/': {
            'subfolders': ['orchestrators/', 'operations/', 'schemas/', 'examples/'],
            'file_types': ['.yaml', '.yml', '.json']
        },
        'src/': {
            'subfolders': [
                'orchestrators/', 'operations/', 'database/',
                'cortex_agents/', 'mcp/', 'entry_point/',
                'response_templates/', 'utilities/'
            ],
            'file_types': ['.py']
        },
        'scripts/': {
            'subfolders': [],
            'file_types': ['.py', '.sh', '.ps1', '.bat']
        },
        'tests/': {
            'subfolders': ['unit/', 'integration/', 'e2e/', 'fixtures/'],
            'file_types': ['.py']
        },
        'docs/': {
            'subfolders': ['api/', 'guides/', 'tutorials/', 'reference/'],
            'file_types': ['.md', '.rst', '.html']
        }
    }
    
    def __init__(self, workspace_root: Path):
        """
        Initialize folder structure optimizer.
        
        Args:
            workspace_root: Root path of workspace
        """
        self.workspace_root = Path(workspace_root)
        self.organization_rules = self._build_organization_rules()
    
    def _build_organization_rules(self) -> List[OrganizationRule]:
        """
        Build organization rules from CORTEX structure.
        
        Returns:
            List of organization rules sorted by priority
        """
        rules = []
        
        # Rule 1: Backups → archives/backups/ (HIGH priority)
        rules.append(OrganizationRule(
            name='backup_files',
            patterns=['backup', '.bak', '.backup-', 'auto-backup-'],
            target_folder='cortex-brain/archives/backups/',
            priority=10,
            description='Move backup files to archives'
        ))
        
        # Rule 2: Reports → documents/reports/ (HIGH priority)
        rules.append(OrganizationRule(
            name='report_files',
            patterns=['report', '-report.md', 'summary.md'],
            target_folder='cortex-brain/documents/reports/',
            priority=9,
            description='Move reports to documents/reports/'
        ))
        
        # Rule 3: Configuration files → config/ (MEDIUM priority)
        rules.append(OrganizationRule(
            name='config_files',
            patterns=['.yaml', '.yml', '.json', '.toml', '.ini', '.env'],
            target_folder='cortex-brain/config/',
            priority=8,
            description='Move config files to cortex-brain/config/'
        ))
        
        # Rule 4: Analysis docs → documents/analysis/ (MEDIUM priority)
        rules.append(OrganizationRule(
            name='analysis_docs',
            patterns=['analysis', 'investigation', 'review'],
            target_folder='cortex-brain/documents/analysis/',
            priority=7,
            description='Move analysis docs to documents/analysis/'
        ))
        
        # Rule 5: Scripts → scripts/ (MEDIUM priority)
        rules.append(OrganizationRule(
            name='script_files',
            patterns=['.sh', '.ps1', '.bat', '.cmd'],
            target_folder='scripts/',
            priority=6,
            description='Move scripts to scripts/'
        ))
        
        # Rule 6: Python source → src/ (LOW priority, manual review)
        rules.append(OrganizationRule(
            name='python_source',
            patterns=['.py'],
            target_folder='src/',
            priority=5,
            description='Move Python source to src/ (review required)'
        ))
        
        # Rule 7: Documentation → docs/ (LOW priority)
        rules.append(OrganizationRule(
            name='general_docs',
            patterns=['.md', '.txt', '.rst'],
            target_folder='docs/',
            priority=4,
            description='Move documentation to docs/'
        ))
        
        return sorted(rules, key=lambda r: r.priority, reverse=True)
    
    def suggest_location(self, filepath: str) -> Tuple[str, OrganizationRule]:
        """
        Suggest optimal location for file based on organization rules.
        
        Args:
            filepath: Current file path
        
        Returns:
            Tuple of (suggested_path, matching_rule)
        """
        path = Path(filepath)
        name_lower = filepath.lower()
        
        # Apply rules in priority order
        for rule in self.organization_rules:
            for pattern in rule.patterns:
                if pattern in name_lower:
                    # Build suggested path
                    suggested = Path(rule.target_folder) / path.name
                    return str(suggested), rule
        
        # No rule matched - keep current location
        return filepath, None
    
    def validate_structure(self, paths: List[str]) -> Dict[str, List[str]]:
        """
        Validate files against CORTEX folder structure.
        
        Args:
            paths: List of file paths to validate
        
        Returns:
            Dictionary of validation results:
                - 'correct': Files in correct locations
                - 'misplaced': Files that should be relocated
                - 'unknown': Files with no clear placement rule
        """
        results = {
            'correct': [],
            'misplaced': [],
            'unknown': []
        }
        
        for filepath in paths:
            suggested, rule = self.suggest_location(filepath)
            
            if suggested == filepath:
                if rule:
                    results['correct'].append(filepath)
                else:
                    results['unknown'].append(filepath)
            else:
                results['misplaced'].append({
                    'current': filepath,
                    'suggested': suggested,
                    'rule': rule.name if rule else 'unknown',
                    'reason': rule.description if rule else 'No matching rule'
                })
        
        return results
    
    def generate_relocation_plan(self, misplaced_files: List[str]) -> Dict[str, Dict]:
        """
        Generate comprehensive relocation plan.
        
        Args:
            misplaced_files: List of misplaced file paths
        
        Returns:
            Dictionary mapping old paths to relocation details
        """
        plan = {}
        
        for filepath in misplaced_files:
            suggested, rule = self.suggest_location(filepath)
            
            if suggested != filepath:
                plan[filepath] = {
                    'destination': suggested,
                    'rule': rule.name if rule else 'manual',
                    'priority': rule.priority if rule else 0,
                    'description': rule.description if rule else 'Manual review required',
                    'safe': rule.priority >= 7 if rule else False  # Auto-relocate high priority
                }
        
        return plan


class FileTypeClassifier:
    """Classify files by type and purpose."""
    
    CLASSIFICATIONS = {
        'source_code': {
            'extensions': ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs'],
            'purpose': 'Source code',
            'preservation': 'HIGH'
        },
        'configuration': {
            'extensions': ['.yaml', '.yml', '.json', '.toml', '.ini', '.env', '.config'],
            'purpose': 'Configuration',
            'preservation': 'HIGH'
        },
        'documentation': {
            'extensions': ['.md', '.txt', '.rst', '.pdf', '.html'],
            'purpose': 'Documentation',
            'preservation': 'HIGH'
        },
        'data': {
            'extensions': ['.csv', '.xml', '.sql', '.db', '.sqlite'],
            'purpose': 'Data files',
            'preservation': 'MEDIUM'
        },
        'scripts': {
            'extensions': ['.sh', '.bash', '.ps1', '.bat', '.cmd'],
            'purpose': 'Scripts',
            'preservation': 'HIGH'
        },
        'temp_cache': {
            'extensions': ['.pyc', '.pyo', '.cache', '.tmp', '.swp', '.swo'],
            'purpose': 'Temporary/cache',
            'preservation': 'NONE'
        },
        'build_artifacts': {
            'extensions': ['.o', '.obj', '.exe', '.dll', '.so', '.dylib'],
            'purpose': 'Build artifacts',
            'preservation': 'NONE'
        },
        'logs': {
            'extensions': ['.log', '.jsonl'],
            'purpose': 'Logs',
            'preservation': 'LOW'
        },
        'backups': {
            'extensions': ['.bak', '.backup'],
            'purpose': 'Backups',
            'preservation': 'MEDIUM'
        }
    }
    
    @staticmethod
    def classify(filepath: str) -> Tuple[str, str, str]:
        """
        Classify file by type.
        
        Args:
            filepath: File path to classify
        
        Returns:
            Tuple of (classification, purpose, preservation_level)
        """
        path = Path(filepath)
        suffix = path.suffix.lower()
        name_lower = filepath.lower()
        
        # Check by extension
        for classification, info in FileTypeClassifier.CLASSIFICATIONS.items():
            if suffix in info['extensions']:
                return classification, info['purpose'], info['preservation']
        
        # Check by name patterns
        if 'backup' in name_lower:
            return 'backups', 'Backups', 'MEDIUM'
        if '__pycache__' in name_lower:
            return 'temp_cache', 'Python cache', 'NONE'
        if any(x in name_lower for x in ['build/', 'dist/', 'bin/', 'obj/']):
            return 'build_artifacts', 'Build output', 'NONE'
        
        return 'unknown', 'Unknown', 'HIGH'


class OrganizationIntelligence:
    """
    Main intelligence engine coordinating all organization operations.
    
    Integrates:
    - Folder structure optimization
    - File type classification
    - Relocation planning
    - Validation
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize organization intelligence.
        
        Args:
            workspace_root: Root path of workspace
        """
        self.workspace_root = Path(workspace_root)
        self.optimizer = FolderStructureOptimizer(workspace_root)
        self.classifier = FileTypeClassifier()
    
    def analyze_files(self, filepaths: List[str]) -> Dict[str, any]:
        """
        Perform comprehensive file analysis.
        
        Args:
            filepaths: List of file paths to analyze
        
        Returns:
            Analysis results dictionary
        """
        results = {
            'total_files': len(filepaths),
            'by_classification': defaultdict(list),
            'by_preservation': defaultdict(list),
            'relocations': {},
            'validation': {}
        }
        
        # Classify all files
        for filepath in filepaths:
            classification, purpose, preservation = self.classifier.classify(filepath)
            results['by_classification'][classification].append(filepath)
            results['by_preservation'][preservation].append(filepath)
        
        # Generate relocation plan
        validation = self.optimizer.validate_structure(filepaths)
        results['validation'] = validation
        
        # Get specific relocations for misplaced files
        if validation['misplaced']:
            misplaced_paths = [item['current'] for item in validation['misplaced']]
            results['relocations'] = self.optimizer.generate_relocation_plan(misplaced_paths)
        
        return results
    
    def generate_organization_report(self, analysis: Dict) -> str:
        """
        Generate human-readable organization report.
        
        Args:
            analysis: Analysis results from analyze_files()
        
        Returns:
            Markdown formatted report
        """
        lines = []
        
        lines.append("# 📁 File Organization Analysis")
        lines.append(f"\n**Total Files:** {analysis['total_files']}\n")
        
        # By classification
        lines.append("## Classification Breakdown\n")
        for classification, files in analysis['by_classification'].items():
            lines.append(f"- **{classification}:** {len(files)} files")
        
        # By preservation level
        lines.append("\n## Preservation Priority\n")
        for level in ['HIGH', 'MEDIUM', 'LOW', 'NONE']:
            count = len(analysis['by_preservation'].get(level, []))
            lines.append(f"- **{level}:** {count} files")
        
        # Relocations
        if analysis['relocations']:
            lines.append(f"\n## Relocation Plan ({len(analysis['relocations'])} files)\n")
            for old_path, details in list(analysis['relocations'].items())[:20]:
                lines.append(f"- `{old_path}`")
                lines.append(f"  → `{details['destination']}`")
                lines.append(f"  *{details['description']}* (Priority: {details['priority']})")
        
        return '\n'.join(lines)
