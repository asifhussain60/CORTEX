"""
Code Analyzer for Sanitization

Scans codebases to identify domain-specific terminology, sensitive data,
and structural elements requiring transformation.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import Counter

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes codebases to extract domain terminology and structure."""

    def __init__(self, source_directory: str, manifest: Dict[str, Any]):
        self.source_directory = Path(source_directory)
        self.manifest = manifest
        self.file_processing_config = manifest.get("file_processing", {})
        self.exclusions = self._compile_exclusions()

    def _compile_exclusions(self) -> List[re.Pattern]:
        """Compile exclusion patterns from manifest."""
        patterns = []
        for exclusion in self.file_processing_config.get("exclusions", []):
            pattern = exclusion.get("pattern", "").replace("**", ".*").replace("*", "[^/]*")
            patterns.append(re.compile(pattern))
        return patterns

    def scan_file_structure(self) -> Dict[str, Any]:
        """
        Scan directory structure and categorize files.

        Returns:
            Dict with file inventory by type and language
        """
        inventory = {
            "total_files": 0,
            "by_language": {},
            "by_type": {},
            "files": [],
        }

        for root, dirs, files in os.walk(self.source_directory):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                file_path = Path(root) / file
                
                if self._is_excluded(str(file_path)):
                    continue

                language = self._detect_language(file_path)
                file_info = {
                    "path": str(file_path),
                    "relative_path": str(file_path.relative_to(self.source_directory)),
                    "language": language,
                    "size": file_path.stat().st_size,
                }

                inventory["files"].append(file_info)
                inventory["total_files"] += 1
                
                inventory["by_language"][language] = inventory["by_language"].get(language, 0) + 1
                
                file_type = self._categorize_file(file_path)
                inventory["by_type"][file_type] = inventory["by_type"].get(file_type, 0) + 1

        logger.info(f"Scanned {inventory['total_files']} files")
        return inventory

    def extract_domain_terminology(self) -> Dict[str, Any]:
        """
        Extract domain-specific terms from code and documentation.

        Returns:
            Dict mapping terms to frequency and locations
        """
        domain_terms = {}
        terminology_categories = self.manifest.get("mapping_rules", {}).get("terminology_categories", {})
        
        all_terms = []
        for category, terms in terminology_categories.items():
            if category != "infrastructure_specific":  # Infrastructure handled separately
                all_terms.extend(terms)

        for file_info in self._get_analyzable_files():
            try:
                content = self._read_file(file_info["path"])
                
                for term in all_terms:
                    # Case-insensitive search with word boundaries
                    pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
                    matches = pattern.findall(content)
                    
                    if matches:
                        if term not in domain_terms:
                            domain_terms[term] = {
                                "count": 0,
                                "files": [],
                                "category": self._get_term_category(term, terminology_categories),
                            }
                        
                        domain_terms[term]["count"] += len(matches)
                        domain_terms[term]["files"].append(file_info["relative_path"])
            
            except Exception as e:
                logger.warning(f"Failed to analyze {file_info['path']}: {e}")

        logger.info(f"Extracted {len(domain_terms)} domain-specific terms")
        return domain_terms

    def extract_namespaces(self) -> Dict[str, List[str]]:
        """
        Extract namespaces/packages from code files.

        Returns:
            Dict mapping language to list of namespaces
        """
        namespaces = {
            "csharp": set(),
            "python": set(),
            "typescript": set(),
        }

        for file_info in self._get_analyzable_files():
            lang = file_info.get("language", "unknown")
            
            if lang == "csharp":
                ns_list = self._extract_csharp_namespaces(file_info["path"])
                namespaces["csharp"].update(ns_list)
            
            elif lang == "python":
                ns_list = self._extract_python_packages(file_info["path"])
                namespaces["python"].update(ns_list)
            
            elif lang == "typescript":
                ns_list = self._extract_typescript_modules(file_info["path"])
                namespaces["typescript"].update(ns_list)

        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in namespaces.items() if v}

    def detect_sensitive_data(self) -> Dict[str, Any]:
        """
        Detect potentially sensitive data in codebase.

        Returns:
            Dict with sensitive data locations and types
        """
        sensitive_patterns = {
            "connection_string": re.compile(r'(?i)(connectionstring|connection\s*string)\s*[=:]\s*["\']([^"\']+)["\']'),
            "api_key": re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']+)["\']'),
            "password": re.compile(r'(?i)(password|pwd)\s*[=:]\s*["\']([^"\']+)["\']'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "url": re.compile(r'https?://(?!example\.com|localhost|127\.0\.0\.1)[^\s<>"]+'),
        }

        findings = {
            "total": 0,
            "by_type": {},
            "locations": [],
        }

        for file_info in self._get_analyzable_files():
            try:
                content = self._read_file(file_info["path"])
                
                for data_type, pattern in sensitive_patterns.items():
                    matches = pattern.finditer(content)
                    
                    for match in matches:
                        finding = {
                            "type": data_type,
                            "file": file_info["relative_path"],
                            "matched_text": match.group(0)[:50],  # Truncate for safety
                            "line": content[:match.start()].count('\n') + 1,
                        }
                        
                        findings["locations"].append(finding)
                        findings["total"] += 1
                        findings["by_type"][data_type] = findings["by_type"].get(data_type, 0) + 1
            
            except Exception as e:
                logger.warning(f"Failed to scan {file_info['path']}: {e}")

        logger.info(f"Detected {findings['total']} potential sensitive data instances")
        return findings

    def generate_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Generate basic dependency graph (namespace/module dependencies).

        Returns:
            Dict mapping files to their dependencies
        """
        graph = {}
        
        # Simplified implementation - full version would use AST analysis
        logger.info("Generating dependency graph (simplified)")
        
        return graph

    def _get_analyzable_files(self) -> List[Dict[str, Any]]:
        """Get files that should be analyzed (code and docs)."""
        inventory = self.scan_file_structure()
        return [
            f for f in inventory["files"]
            if f["language"] in ["csharp", "python", "typescript", "documentation", "configuration"]
        ]

    def _is_excluded(self, path: str) -> bool:
        """Check if path matches exclusion patterns."""
        for pattern in self.exclusions:
            if pattern.search(path):
                return True
        return False

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext = file_path.suffix.lower()
        
        lang_map = {
            ".cs": "csharp",
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".md": "documentation",
            ".txt": "documentation",
            ".json": "configuration",
            ".yaml": "configuration",
            ".yml": "configuration",
            ".xml": "configuration",
        }
        
        return lang_map.get(ext, "unknown")

    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file by purpose."""
        path_str = str(file_path).lower()
        
        if "/test" in path_str or "\\test" in path_str:
            return "test"
        elif "/docs" in path_str or "\\docs" in path_str:
            return "documentation"
        elif file_path.suffix in [".json", ".yaml", ".yml", ".xml", ".config"]:
            return "configuration"
        else:
            return "source"

    def _read_file(self, file_path: str) -> str:
        """Read file content with encoding handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def _extract_csharp_namespaces(self, file_path: str) -> List[str]:
        """Extract C# namespaces from file."""
        content = self._read_file(file_path)
        pattern = re.compile(r'namespace\s+([\w.]+)')
        return [m.group(1) for m in pattern.finditer(content)]

    def _extract_python_packages(self, file_path: str) -> List[str]:
        """Extract Python package names from file."""
        content = self._read_file(file_path)
        # Extract from imports
        pattern = re.compile(r'(?:from|import)\s+([\w.]+)')
        imports = [m.group(1).split('.')[0] for m in pattern.finditer(content)]
        return imports

    def _extract_typescript_modules(self, file_path: str) -> List[str]:
        """Extract TypeScript module names from file."""
        content = self._read_file(file_path)
        pattern = re.compile(r'(?:from|import)\s+["\']([^"\']+)["\']')
        return [m.group(1) for m in pattern.finditer(content)]

    def _get_term_category(self, term: str, categories: Dict[str, List[str]]) -> str:
        """Determine which category a term belongs to."""
        for category, terms in categories.items():
            if term in terms:
                return category
        return "unknown"
