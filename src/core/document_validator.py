"""
Document Organization Validator

Enforces CORTEX document organization rules:
- All informational documents in cortex-brain/documents/[category]/
- Only whitelist files allowed in repository root
- File naming follows conventions
- Categories are valid and documented

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Valid categories as defined in cortex-brain/documents/README.md
VALID_CATEGORIES = {
    'reports': 'Formal status reports and completion documents',
    'analysis': 'Deep-dive analysis documents and investigations',
    'summaries': 'Quick overview and summary documents',
    'investigations': 'Investigation documents and research findings',
    'planning': 'Planning documents and roadmaps',
    'conversation-captures': 'Strategic conversation captures for learning',
    'implementation-guides': 'How-to guides and implementation instructions',
    'diagrams': 'Visual diagrams and architecture illustrations',
    'archived-scripts': 'Deprecated or replaced scripts',
    'guides': 'General guides and documentation'
}

# Files allowed in repository root (whitelist)
ROOT_WHITELIST = {
    'README.md',
    'LICENSE',
    'LICENSE.md',
    'CONTRIBUTING.md',
    'CHANGELOG.md',
    'CODE_OF_CONDUCT.md',
    '.gitignore',
    '.gitattributes',
    'mkdocs.yml',
    'package.json',
    'requirements.txt',
    'pytest.ini',
    'tsconfig.json',
    'cortex.config.json',
    'cortex.config.example.json',
    'cortex.config.template.json',
    'regenerate_story.py'
}

# Files allowed in cortex-brain root (legacy exceptions)
CORTEX_BRAIN_WHITELIST = {
    'README.md',
    'schema.sql',
    'migrate_brain_db.py',
    'anomalies.yaml',
    'brain-protection-rules.yaml',
    'capabilities.yaml',
    'cleanup-rules.yaml',
    'conversation-context.jsonl',
    'conversation-history.jsonl',
    'development-context.yaml',
    'doc-generation-rules.yaml',
    'file-relationships.yaml',
    'industry-standards.yaml',
    'knowledge-graph.yaml',
    'lessons-learned.yaml',
    'mkdocs-refresh-config.yaml',
    'module-definitions.yaml',
    'operations-config.yaml',
    'publish-config.yaml',
    'response-templates-condensed.yaml',
    'response-templates.yaml',
    'self-review-checklist.yaml',
    'TRUTH-SOURCES.yaml',
    'user-dictionary.yaml',
    'cortex-operations.yaml',
    'MILESTONE-0-BASELINE-COMPLETE.txt',
    'CLEANUP-DRY-RUN-REPORT.json',
    'hybrid-capture-simulation-results.json',
    'obsolete-tests-manifest.json',
    'track-integration-plan.json'
}


class DocumentValidator:
    """Validates document organization according to CORTEX rules"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize validator with workspace root path"""
        if workspace_root:
            self.workspace_root = Path(workspace_root)
        else:
            # Auto-detect workspace root (look for .git directory)
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.workspace_root = current
                    break
                current = current.parent
            else:
                self.workspace_root = Path.cwd()
    
    def validate_document_path(self, file_path: str) -> Dict:
        """
        Validate document follows organization rules
        
        Returns:
            dict with keys:
                - valid (bool): Is path valid?
                - category (str): Document category if valid
                - violation (str): Reason if invalid
                - suggestion (str): Suggested correct path if invalid
        """
        path = Path(file_path)
        
        # Not a markdown file - not our concern
        if path.suffix.lower() != '.md':
            return {
                'valid': True,
                'category': None,
                'violation': None,
                'suggestion': None,
                'reason': 'Not a markdown document'
            }
        
        # Handle both absolute and relative paths
        if path.is_absolute():
            # Get relative path from workspace root
            try:
                rel_path = path.relative_to(self.workspace_root)
            except ValueError:
                # Path is outside workspace
                return {
                    'valid': False,
                    'category': None,
                    'violation': 'Document outside workspace root',
                    'suggestion': None,
                    'reason': f'Path {file_path} is not within workspace'
                }
        else:
            # Assume relative paths are relative to workspace root
            rel_path = path
        
        parts = rel_path.parts
        
        # Check if in root directory
        if len(parts) == 1:
            if path.name in ROOT_WHITELIST:
                return {
                    'valid': True,
                    'category': 'root-whitelist',
                    'violation': None,
                    'suggestion': None,
                    'reason': 'Whitelisted root file'
                }
            else:
                return {
                    'valid': False,
                    'category': None,
                    'violation': 'Informational document in repository root',
                    'suggestion': self._suggest_correct_path(path),
                    'reason': f'Document {path.name} should be in cortex-brain/documents/[category]/'
                }
        
        # Check if in cortex-brain root
        if len(parts) == 2 and parts[0] == 'cortex-brain':
            if path.name in CORTEX_BRAIN_WHITELIST:
                return {
                    'valid': True,
                    'category': 'cortex-brain-whitelist',
                    'violation': None,
                    'suggestion': None,
                    'reason': 'Whitelisted cortex-brain file'
                }
            else:
                return {
                    'valid': False,
                    'category': None,
                    'violation': 'Document in cortex-brain root (not organized)',
                    'suggestion': self._suggest_correct_path(path),
                    'reason': f'Document {path.name} should be in cortex-brain/documents/[category]/'
                }
        
        # Check if in organized structure
        if len(parts) >= 4 and parts[0] == 'cortex-brain' and parts[1] == 'documents':
            category = parts[2]
            if category in VALID_CATEGORIES:
                return {
                    'valid': True,
                    'category': category,
                    'violation': None,
                    'suggestion': None,
                    'reason': f'Properly organized in {category}/'
                }
            else:
                return {
                    'valid': False,
                    'category': None,
                    'violation': f'Invalid category: {category}',
                    'suggestion': self._suggest_correct_path(path),
                    'reason': f'Category {category} not in valid categories: {", ".join(VALID_CATEGORIES.keys())}'
                }
        
        # Check if in docs/ directory (user-facing documentation)
        if len(parts) >= 1 and parts[0] == 'docs':
            return {
                'valid': True,
                'category': 'user-docs',
                'violation': None,
                'suggestion': None,
                'reason': 'User-facing documentation in docs/'
            }
        
        # Other locations (tests, src, etc.) - allow
        return {
            'valid': True,
            'category': 'other',
            'violation': None,
            'suggestion': None,
            'reason': f'Document in {parts[0]}/ directory (allowed)'
        }
    
    def _suggest_correct_path(self, path: Path) -> str:
        """Suggest correct path based on file name analysis"""
        name = path.stem.upper()
        
        # Reports
        if any(keyword in name for keyword in ['REPORT', 'COMPLETE', 'FINAL', 'STATUS']):
            return f'cortex-brain/documents/reports/{path.name}'
        
        # Analysis
        if any(keyword in name for keyword in ['ANALYSIS', 'INVESTIGATION', 'RESEARCH']):
            return f'cortex-brain/documents/analysis/{path.name}'
        
        # Summaries
        if any(keyword in name for keyword in ['SUMMARY', 'OVERVIEW', 'BRIEF']):
            return f'cortex-brain/documents/summaries/{path.name}'
        
        # Planning
        if any(keyword in name for keyword in ['PLAN', 'ROADMAP', 'STRATEGY']):
            return f'cortex-brain/documents/planning/{path.name}'
        
        # Guides
        if any(keyword in name for keyword in ['GUIDE', 'TUTORIAL', 'HOWTO', 'HOW-TO']):
            return f'cortex-brain/documents/implementation-guides/{path.name}'
        
        # Conversation captures
        if 'CONVERSATION' in name or 'CAPTURE' in name:
            return f'cortex-brain/documents/conversation-captures/{path.name}'
        
        # Default to reports for completion documents
        return f'cortex-brain/documents/reports/{path.name}'
    
    def get_category_from_path(self, file_path: str) -> Optional[str]:
        """Extract category from file path if in organized structure"""
        result = self.validate_document_path(file_path)
        return result.get('category')
    
    def is_organized_document(self, file_path: str) -> bool:
        """Check if document is in organized structure"""
        result = self.validate_document_path(file_path)
        return result['valid'] and result['category'] in VALID_CATEGORIES
    
    def scan_workspace(self) -> Dict[str, List[str]]:
        """
        Scan workspace for all markdown documents and categorize them
        
        Returns:
            dict with keys:
                - valid: List of valid document paths
                - violations: List of paths that violate organization rules
                - suggestions: Dict mapping violation paths to suggested paths
        """
        valid = []
        violations = []
        suggestions = {}
        
        # Scan for all .md files
        for md_file in self.workspace_root.rglob('*.md'):
            # Skip hidden directories and node_modules
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if 'node_modules' in md_file.parts:
                continue
            
            result = self.validate_document_path(str(md_file))
            
            if result['valid']:
                valid.append(str(md_file.relative_to(self.workspace_root)))
            else:
                violations.append(str(md_file.relative_to(self.workspace_root)))
                if result['suggestion']:
                    suggestions[str(md_file.relative_to(self.workspace_root))] = result['suggestion']
        
        return {
            'valid': valid,
            'violations': violations,
            'suggestions': suggestions
        }
    
    def validate_naming_convention(self, file_path: str) -> Dict:
        """
        Validate file naming follows conventions
        
        Convention patterns:
            reports: [COMPONENT]-[VERSION]-[TYPE]-REPORT.md
            analysis: [TOPIC]-ANALYSIS-[DATE].md
            summaries: [COMPONENT]-SUMMARY-[DATE].md
            investigations: [TOPIC]-INVESTIGATION-[STATUS].md
            planning: [COMPONENT]-[TYPE]-PLAN.md
            conversation-captures: CONVERSATION-CAPTURE-[DATE]-[TOPIC].md
            guides: [TOPIC]-[TYPE]-GUIDE.md
        """
        path = Path(file_path)
        result = self.validate_document_path(file_path)
        
        if not result['valid'] or not result['category']:
            return {
                'valid': False,
                'reason': 'Document not in organized structure'
            }
        
        category = result['category']
        name = path.stem
        
        # Skip validation for whitelisted files
        if category in ['root-whitelist', 'cortex-brain-whitelist', 'user-docs', 'other']:
            return {'valid': True, 'reason': 'Whitelist or non-organizational file'}
        
        # Naming convention patterns
        patterns = {
            'reports': r'^[A-Z0-9-]+-REPORT$',
            'analysis': r'^[A-Z0-9-]+-ANALYSIS',
            'summaries': r'^[A-Z0-9-]+-SUMMARY',
            'investigations': r'^[A-Z0-9-]+-INVESTIGATION',
            'planning': r'^[A-Z0-9-]+-PLAN$',
            'conversation-captures': r'^CONVERSATION-CAPTURE-\d{4}-\d{2}-\d{2}',
            'guides': r'^[A-Z0-9-]+-GUIDE$'
        }
        
        if category in patterns:
            pattern = patterns[category]
            if re.match(pattern, name.upper()):
                return {
                    'valid': True,
                    'reason': f'Follows {category} naming convention'
                }
            else:
                return {
                    'valid': False,
                    'reason': f'Does not follow {category} naming convention: {pattern}',
                    'suggestion': self._suggest_naming_fix(category, name)
                }
        
        # Category doesn't have strict naming requirements
        return {'valid': True, 'reason': f'Category {category} has flexible naming'}
    
    def _suggest_naming_fix(self, category: str, name: str) -> str:
        """Suggest corrected naming based on category"""
        name_upper = name.upper()
        
        if category == 'reports' and not name_upper.endswith('-REPORT'):
            return f'{name}-REPORT.md'
        elif category == 'analysis' and '-ANALYSIS' not in name_upper:
            return f'{name}-ANALYSIS.md'
        elif category == 'summaries' and '-SUMMARY' not in name_upper:
            return f'{name}-SUMMARY.md'
        elif category == 'planning' and not name_upper.endswith('-PLAN'):
            return f'{name}-PLAN.md'
        elif category == 'guides' and not name_upper.endswith('-GUIDE'):
            return f'{name}-GUIDE.md'
        
        return f'{name}.md'


def validate_document(file_path: str, workspace_root: Optional[str] = None) -> Dict:
    """
    Convenience function to validate a single document
    
    Args:
        file_path: Path to document to validate
        workspace_root: Optional workspace root path
    
    Returns:
        Validation result dictionary
    """
    validator = DocumentValidator(workspace_root)
    return validator.validate_document_path(file_path)


def scan_workspace_documents(workspace_root: Optional[str] = None) -> Dict:
    """
    Convenience function to scan all workspace documents
    
    Args:
        workspace_root: Optional workspace root path
    
    Returns:
        Scan results dictionary
    """
    validator = DocumentValidator(workspace_root)
    return validator.scan_workspace()


if __name__ == '__main__':
    # CLI usage
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = validate_document(file_path)
        print(f"Validation result for {file_path}:")
        print(f"  Valid: {result['valid']}")
        if result['category']:
            print(f"  Category: {result['category']}")
        if result['violation']:
            print(f"  Violation: {result['violation']}")
            print(f"  Reason: {result['reason']}")
        if result['suggestion']:
            print(f"  Suggested path: {result['suggestion']}")
    else:
        # Scan workspace
        results = scan_workspace_documents()
        print(f"Workspace document scan:")
        print(f"  Valid documents: {len(results['valid'])}")
        print(f"  Violations: {len(results['violations'])}")
        
        if results['violations']:
            print("\nViolations:")
            for violation in results['violations']:
                print(f"  ❌ {violation}")
                if violation in results['suggestions']:
                    print(f"     → Suggested: {results['suggestions'][violation]}")
