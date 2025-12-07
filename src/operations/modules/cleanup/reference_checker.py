"""
Reference Checker for CORTEX Cleanup Operations

Checks and updates references when files are reorganized or consolidated.
Handles Python imports, file paths, markdown links, and config references.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ReferenceChecker:
    """
    Checks and updates file references after reorganization.
    
    Handles:
    - Python imports (from X import Y)
    - File paths (Path("..."), os.path.join(...))
    - Markdown links ([text](path))
    - Config references (in YAML, JSON)
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reference_map: Dict[str, List[Tuple[Path, int, str]]] = {}
        
    def scan_references(self, old_path: str) -> List[Tuple[Path, int, str, str]]:
        """
        Scan for references to a file that will be moved/deleted.
        
        Args:
            old_path: Relative path of file being moved/deleted
            
        Returns:
            List of (file_path, line_number, line_content, reference_type)
        """
        references = []
        old_path_norm = Path(old_path).as_posix()
        old_name = Path(old_path).name
        
        # Search patterns
        patterns = {
            'python_import': self._find_python_imports,
            'markdown_link': self._find_markdown_links,
            'file_path': self._find_file_paths,
            'config_ref': self._find_config_refs
        }
        
        # Scan all relevant files
        scan_extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.txt', '.rst'}
        
        for file_path in self.project_root.rglob('*'):
            if file_path.suffix not in scan_extensions:
                continue
            
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for ref_type, finder_func in patterns.items():
                        matches = finder_func(line, old_path_norm, old_name)
                        
                        for match in matches:
                            references.append((file_path, line_num, line.strip(), ref_type))
                            
            except Exception as e:
                logger.debug(f"Could not scan {file_path}: {e}")
                continue
        
        return references
    
    def update_references(
        self,
        old_path: str,
        new_path: str,
        references: List[Tuple[Path, int, str, str]],
        dry_run: bool = True
    ) -> Dict[str, int]:
        """
        Update references after file reorganization.
        
        Args:
            old_path: Old relative path
            new_path: New relative path
            references: List from scan_references()
            dry_run: If True, only simulate updates
            
        Returns:
            Dict with update counts by type
        """
        old_path_norm = Path(old_path).as_posix()
        new_path_norm = Path(new_path).as_posix()
        
        updates = {
            'python_import': 0,
            'markdown_link': 0,
            'file_path': 0,
            'config_ref': 0
        }
        
        files_to_update: Dict[Path, List[str]] = {}
        
        # Group references by file
        for file_path, line_num, line_content, ref_type in references:
            if file_path not in files_to_update:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    files_to_update[file_path] = content.split('\n')
                except:
                    continue
            
            lines = files_to_update[file_path]
            
            if line_num <= len(lines):
                old_line = lines[line_num - 1]
                new_line = self._replace_reference(old_line, old_path_norm, new_path_norm, ref_type)
                
                if old_line != new_line:
                    lines[line_num - 1] = new_line
                    updates[ref_type] += 1
        
        # Write updated files
        if not dry_run:
            for file_path, lines in files_to_update.items():
                try:
                    file_path.write_text('\n'.join(lines), encoding='utf-8')
                    logger.info(f"  ✓ Updated references in {file_path.relative_to(self.project_root)}")
                except Exception as e:
                    logger.warning(f"  ✗ Failed to update {file_path}: {e}")
        
        return updates
    
    def _find_python_imports(self, line: str, old_path: str, old_name: str) -> List[str]:
        """Find Python import statements"""
        matches = []
        
        # Convert path to Python module notation
        module_path = old_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
        # Patterns: from X import Y, import X, from X.Y import Z
        patterns = [
            rf'from\s+{re.escape(module_path)}\s+import',
            rf'import\s+{re.escape(module_path)}',
            rf'from\s+[\'"]?{re.escape(old_path)}[\'"]?',
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                matches.append(line)
                break
        
        return matches
    
    def _find_markdown_links(self, line: str, old_path: str, old_name: str) -> List[str]:
        """Find markdown links"""
        matches = []
        
        # Patterns: [text](path), <path>, [text](path "title")
        patterns = [
            rf'\[([^\]]+)\]\(([^\)]*{re.escape(old_path)}[^\)]*)\)',
            rf'\[([^\]]+)\]\(([^\)]*{re.escape(old_name)}[^\)]*)\)',
            rf'<[^>]*{re.escape(old_path)}[^>]*>',
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                matches.append(line)
                break
        
        return matches
    
    def _find_file_paths(self, line: str, old_path: str, old_name: str) -> List[str]:
        """Find file path references"""
        matches = []
        
        # Patterns: Path("..."), "path/to/file", 'path/to/file'
        patterns = [
            rf'Path\([\'"]?[^\'"]*{re.escape(old_path)}[^\'"]*[\'"]?\)',
            rf'[\'"][^\'"]*{re.escape(old_path)}[^\'"]*[\'"]',
            rf'[\'"][^\'"]*{re.escape(old_name)}[^\'"]*[\'"]',
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                matches.append(line)
                break
        
        return matches
    
    def _find_config_refs(self, line: str, old_path: str, old_name: str) -> List[str]:
        """Find config file references (YAML, JSON)"""
        matches = []
        
        # Look for path-like values in config files
        if old_path in line or old_name in line:
            # Simple check - if line contains path and has config-like syntax
            if ':' in line or '=' in line:
                matches.append(line)
        
        return matches
    
    def _replace_reference(
        self,
        line: str,
        old_path: str,
        new_path: str,
        ref_type: str
    ) -> str:
        """Replace a single reference in a line"""
        
        if ref_type == 'python_import':
            # Convert paths to module notation
            old_module = old_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            new_module = new_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            return line.replace(old_module, new_module)
        
        elif ref_type in ['markdown_link', 'file_path', 'config_ref']:
            # Simple path replacement
            return line.replace(old_path, new_path)
        
        return line
    
    def generate_reference_report(
        self,
        old_path: str,
        references: List[Tuple[Path, int, str, str]]
    ) -> str:
        """Generate a report of all references found"""
        
        if not references:
            return f"No references found to {old_path}"
        
        report = [
            f"References to {old_path}:",
            f"Total: {len(references)} references",
            ""
        ]
        
        # Group by file
        by_file: Dict[Path, List[Tuple[int, str, str]]] = {}
        
        for file_path, line_num, line_content, ref_type in references:
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append((line_num, line_content, ref_type))
        
        for file_path, refs in sorted(by_file.items()):
            rel_path = file_path.relative_to(self.project_root)
            report.append(f"\n{rel_path} ({len(refs)} references):")
            
            for line_num, line_content, ref_type in refs:
                report.append(f"  Line {line_num} [{ref_type}]: {line_content[:80]}")
        
        return '\n'.join(report)
