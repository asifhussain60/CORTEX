"""
Code Organization Collector

Analyzes code organization, complexity, and identifies hotspots.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import subprocess
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.dashboard.data.base_collector import BaseDataCollector
from src.dashboard.utils.recursive_scanner import RecursiveScanner


class CodeOrganizationCollector(BaseDataCollector):
    """
    Collects code organization metrics and identifies hotspots.
    
    Analyzes:
    - File complexity (cyclomatic complexity, LOC)
    - Change frequency (git history)
    - Hotspot identification (high complexity + high change frequency)
    - Module structure
    
    Data Source: CURRENT STATE ONLY - Real code metrics from analysis.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect code organization data.
        
        Returns:
            Dict with keys: heatmap, hotspots, module_structure, summary, 
                          file_complexity, duplications, maintainability, technical_debt
        """
        self.logger.info("Collecting code organization data...")
        
        # Generate complexity heatmap
        heatmap = self._generate_heatmap()
        
        # Identify hotspots
        hotspots = self._identify_hotspots(heatmap)
        
        # Analyze module structure
        module_structure = self._analyze_module_structure()
        
        # Detect code duplications
        duplications = self._detect_duplications()
        
        # Calculate maintainability index
        maintainability = self._calculate_maintainability(heatmap)
        
        # Estimate technical debt
        technical_debt = self._estimate_technical_debt(heatmap, duplications)
        
        # Analyze file sizes and growth
        file_sizes = self._analyze_file_sizes()
        
        # Detect code smells
        code_smells = self._detect_code_smells(heatmap)
        
        code_org_data = {
            "heatmap": heatmap,
            "hotspots": hotspots,
            "module_structure": module_structure,
            "file_complexity": heatmap[:50],  # Top 50 files by complexity
            "duplications": duplications,
            "maintainability": maintainability,
            "technical_debt": technical_debt,
            "file_sizes": file_sizes,
            "code_smells": code_smells,
            "summary": {
                "total_files": len(heatmap),
                "high_complexity_files": len([f for f in heatmap if f["complexity"] > 20]),
                "hotspot_count": len(hotspots),
                "avg_complexity": sum(f["complexity"] for f in heatmap) / len(heatmap) if heatmap else 0,
                "total_loc": sum(f["loc"] for f in heatmap),
                "duplication_percentage": duplications.get("duplication_rate", 0),
                "maintainability_score": maintainability.get("overall_score", 0),
                "technical_debt_hours": technical_debt.get("total_hours", 0),
                "code_smell_count": len(code_smells)
            }
        }
        
        self.logger.info(f"Code organization analysis complete. {len(hotspots)} hotspots, "
                        f"{len(code_smells)} code smells, {technical_debt.get('total_hours', 0):.1f}h debt")
        return code_org_data
    
    def _generate_heatmap(self) -> List[Dict[str, Any]]:
        """
        Generate complexity heatmap for all code files (multi-language support).
        
        Supports: Python, C#, Java, TypeScript, JavaScript, React, Angular, Vue, Go, Rust,
                 PHP, Ruby, Swift, Kotlin, C, C++, Objective-C, Scala, Perl, R, Shell, etc.
        
        Returns:
            List of file data with complexity, LOC, change frequency
        """
        heatmap = []
        
        # Define language file patterns (comprehensive list)
        file_patterns = [
            # Modern Web
            ('**/*.py', 'python'),
            ('**/*.js', 'javascript'),
            ('**/*.jsx', 'react'),
            ('**/*.ts', 'typescript'),
            ('**/*.tsx', 'react-typescript'),
            ('**/*.vue', 'vue'),
            
            # .NET Stack
            ('**/*.cs', 'csharp'),
            ('**/*.vb', 'vb.net'),
            ('**/*.fs', 'fsharp'),
            
            # JVM Languages
            ('**/*.java', 'java'),
            ('**/*.kt', 'kotlin'),
            ('**/*.scala', 'scala'),
            ('**/*.groovy', 'groovy'),
            
            # Systems Programming
            ('**/*.c', 'c'),
            ('**/*.cpp', 'cpp'),
            ('**/*.cc', 'cpp'),
            ('**/*.cxx', 'cpp'),
            ('**/*.h', 'c-header'),
            ('**/*.hpp', 'cpp-header'),
            ('**/*.go', 'go'),
            ('**/*.rs', 'rust'),
            
            # Mobile
            ('**/*.swift', 'swift'),
            ('**/*.m', 'objective-c'),
            ('**/*.mm', 'objective-cpp'),
            
            # Web Backend
            ('**/*.php', 'php'),
            ('**/*.rb', 'ruby'),
            ('**/*.pl', 'perl'),
            ('**/*.pm', 'perl'),
            
            # Scripting
            ('**/*.sh', 'shell'),
            ('**/*.bash', 'bash'),
            ('**/*.ps1', 'powershell'),
            ('**/*.r', 'r'),
            ('**/*.R', 'r'),
            
            # Other
            ('**/*.sql', 'sql'),
            ('**/*.lua', 'lua'),
            ('**/*.dart', 'dart')
        ]
        
        # Analyze files from project root
        for pattern, language in file_patterns:
            for code_file in self.project_root.glob(pattern):
                # Skip common non-source directories
                path_str = str(code_file)
                if any(skip in path_str for skip in ['venv', '__pycache__', 'node_modules', 'bin', 'obj', '.git', 'packages']):
                    continue
            
                try:
                    complexity = self._calculate_complexity_generic(code_file, language)
                    loc = self._count_loc(code_file)
                    change_freq = self._get_change_frequency(code_file)
                    last_modified = self._get_last_modified(code_file)
                    
                    # Calculate risk score (complexity × change_frequency)
                    risk_score = min(complexity * (change_freq / 10), 100) if change_freq > 0 else complexity
                    
                    heatmap.append({
                        "file": str(code_file.relative_to(self.project_root)),
                        "complexity": complexity,
                        "loc": loc,
                        "change_frequency": change_freq,
                        "last_modified": last_modified,
                        "risk_score": int(risk_score),
                        "language": language
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Error analyzing {code_file}: {e}")
                    continue
        
        # Sort by risk score descending
        heatmap.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return heatmap
    
    def _calculate_complexity(self, file_path: Path) -> int:
        """
        Calculate cyclomatic complexity for Python files (legacy method).
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Cyclomatic complexity score
        """
        return self._calculate_complexity_generic(file_path, 'python')
    
    def _calculate_complexity_generic(self, file_path: Path, language: str) -> int:
        """
        Calculate cyclomatic complexity for multiple languages.
        
        Uses pattern matching for decision points (if, for, while, switch, case, catch, etc.)
        Language-agnostic approach works for most C-style and modern languages.
        
        Args:
            file_path: Path to code file
            language: Programming language identifier
            
        Returns:
            Cyclomatic complexity score
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if language == 'python':
                # Use AST for Python (most accurate)
                try:
                    tree = ast.parse(content)
                    complexity = 1
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                            complexity += 1
                        elif isinstance(node, ast.BoolOp):
                            complexity += len(node.values) - 1
                    return complexity
                except:
                    pass
            
            # Pattern-based complexity for C#, Java, TypeScript, JavaScript
            complexity = 1  # Base complexity
            
            # Decision point patterns (language-agnostic)
            patterns = [
                r'\bif\s*\(',           # if statements
                r'\belse\s+if\s*\(',    # else if
                r'\bfor\s*\(',          # for loops
                r'\bforeach\s*\(',      # foreach (C#)
                r'\bwhile\s*\(',        # while loops
                r'\bswitch\s*\(',       # switch statements
                r'\bcase\s+',           # case statements
                r'\bcatch\s*[\(\{]',    # catch blocks
                r'\b\&\&\b',            # logical AND
                r'\b\|\|\b',            # logical OR
                r'\?.*:',               # ternary operators
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                complexity += len(matches)
            
            return max(complexity, 1)
            
        except PermissionError:
            # Skip files/directories with permission issues (symlinks, restricted dirs)
            return 1
        except Exception as e:
            self.logger.debug(f"Error calculating complexity for {file_path}: {e}")
            return 1
    
    def _count_loc(self, file_path: Path) -> int:
        """Count lines of code (excluding comments and blanks) - multi-language."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            loc = 0
            in_block_comment = False
            
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    continue
                
                # Handle block comments (/* */ or """ """)
                if '/*' in stripped or stripped.startswith('"""') or stripped.startswith("'''"):
                    in_block_comment = True
                if '*/' in stripped or stripped.endswith('"""') or stripped.endswith("'''"):
                    in_block_comment = False
                    continue
                
                if in_block_comment:
                    continue
                
                # Skip single-line comments
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                    continue
                
                loc += 1
            
            return loc
            
        except Exception:
            return 0
    
    def _get_change_frequency(self, file_path: Path) -> int:
        """
        Get change frequency from git history.
        Skip git operations to avoid subprocess hanging issues.
        
        Args:
            file_path: Path to file
            
        Returns:
            Number of commits modifying this file (currently returns 0)
        """
        # Disabled git operations due to subprocess hanging issues
        # Can be re-enabled with GitPython library or proper subprocess handling
        return 0
    
    def _get_last_modified(self, file_path: Path) -> str:
        """
        Get last modified date from file system.
        Git operations disabled to avoid subprocess hanging issues.
        
        Args:
            file_path: Path to file
            
        Returns:
            ISO format date string
        """
        # Use file system modification time (git operations disabled)
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except Exception:
            return "unknown"
    
    def _identify_hotspots(self, heatmap: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify hotspots (high complexity + high change frequency).
        
        Args:
            heatmap: List of file data
            
        Returns:
            List of hotspot files
        """
        # Files with risk score > 50 are considered hotspots
        hotspots = [
            {
                "file": f["file"],
                "risk_score": f["risk_score"],
                "complexity": f["complexity"],
                "change_frequency": f["change_frequency"],
                "recommendation": self._generate_recommendation(f)
            }
            for f in heatmap 
            if f["risk_score"] > 50
        ]
        
        return hotspots[:20]  # Top 20 hotspots
    
    def _generate_recommendation(self, file_data: Dict[str, Any]) -> str:
        """
        Generate refactoring recommendation for a file.
        
        Args:
            file_data: File metrics data
            
        Returns:
            Recommendation string
        """
        complexity = file_data["complexity"]
        change_freq = file_data["change_frequency"]
        loc = file_data["loc"]
        
        if complexity > 50 and loc > 500:
            return "High complexity & large file - consider splitting into smaller modules"
        elif complexity > 30:
            return "High complexity - refactor to reduce cyclomatic complexity"
        elif change_freq > 50:
            return "Frequent changes - stabilize with comprehensive tests"
        elif loc > 1000:
            return "Large file - consider breaking into smaller components"
        else:
            return "Monitor for complexity growth"
    
    def _analyze_module_structure(self) -> Dict[str, Any]:
        """
        Analyze module structure and organization.
        
        Returns:
            Dict with module hierarchy and metrics
        """
        structure = {
            "modules": [],
            "depth": 0,
            "total_directories": 0
        }
        
        # Use RecursiveScanner to find all code files (not just Python)
        scanner = RecursiveScanner(self.project_root, logger=self.logger)
        all_files = scanner.scan_files()  # Scans from root, all languages
        
        if not all_files:
            return structure
        
        # Group files by directory
        dir_groups = {}
        for file_path in all_files:
            parent = file_path.parent
            if parent not in dir_groups:
                dir_groups[parent] = []
            dir_groups[parent].append(file_path)
        
        # Build structure
        max_depth = 0
        for directory, files in dir_groups.items():
            try:
                rel_path = directory.relative_to(self.project_root)
                depth = len(rel_path.parts)
                max_depth = max(max_depth, depth)
                
                structure["modules"].append({
                    "path": str(rel_path),
                    "file_count": len(files),
                    "subdirectories": len([d for d in directory.iterdir() if d.is_dir()])
                })
            except ValueError:
                # Directory outside project root, skip
                continue
        
        structure["depth"] = max_depth
        structure["total_directories"] = len(structure["modules"])
        
        return structure
    
    def _detect_duplications(self) -> Dict[str, Any]:
        """
        Detect code duplications using simple hash-based approach.
        
        Returns:
            Dict with duplication metrics
        """
        # Use RecursiveScanner to find all Python files from root
        scanner = RecursiveScanner(self.project_root, logger=self.logger)
        py_files = scanner.scan_python_files()
        
        if not py_files:
            return {"duplication_rate": 0, "duplicate_blocks": []}
        
        # Track line hashes
        line_hashes = defaultdict(list)
        total_lines = 0
        duplicate_lines = 0
        
        for py_file in py_files:
            
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#'):
                        continue
                    
                    total_lines += 1
                    line_hash = hash(stripped)
                    line_hashes[line_hash].append((str(py_file.relative_to(self.project_root)), i, stripped))
                    
            except Exception as e:
                self.logger.debug(f"Error analyzing {py_file} for duplications: {e}")
                continue
        
        # Find duplicates
        duplicate_blocks = []
        for line_hash, occurrences in line_hashes.items():
            if len(occurrences) > 1:
                duplicate_lines += len(occurrences)
                if len(occurrences) > 2:  # Report if duplicated more than twice
                    duplicate_blocks.append({
                        "line": occurrences[0][2][:80],  # Truncate long lines
                        "count": len(occurrences),
                        "locations": [f"{loc[0]}:{loc[1]}" for loc in occurrences[:5]]  # Top 5
                    })
        
        duplication_rate = (duplicate_lines / total_lines * 100) if total_lines > 0 else 0
        
        return {
            "duplication_rate": round(duplication_rate, 2),
            "duplicate_blocks": sorted(duplicate_blocks, key=lambda x: x["count"], reverse=True)[:20],
            "total_lines_analyzed": total_lines,
            "duplicate_lines": duplicate_lines
        }
    
    def _calculate_maintainability(self, heatmap: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate maintainability index for the codebase.
        
        Args:
            heatmap: File complexity data
            
        Returns:
            Dict with maintainability scores
        """
        if not heatmap:
            return {"overall_score": 0, "grade": "F", "factors": {}}
        
        # Maintainability Index = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        # Simplified version: weight complexity, LOC, and comments
        
        total_loc = sum(f["loc"] for f in heatmap)
        avg_complexity = sum(f["complexity"] for f in heatmap) / len(heatmap)
        
        # Simple scoring: 100 - penalties for complexity and size
        score = 100
        score -= min(avg_complexity * 0.5, 30)  # Complexity penalty (max 30)
        score -= min(total_loc / 1000, 20)  # Size penalty (max 20)
        
        # Determine grade
        if score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 55:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(max(score, 0), 1),
            "grade": grade,
            "factors": {
                "avg_complexity": round(avg_complexity, 2),
                "total_loc": total_loc,
                "file_count": len(heatmap)
            }
        }
    
    def _estimate_technical_debt(self, heatmap: List[Dict[str, Any]], 
                                duplications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate technical debt in hours.
        
        Args:
            heatmap: File complexity data
            duplications: Duplication analysis
            
        Returns:
            Dict with technical debt estimation
        """
        debt_hours = 0.0
        debt_items = []
        
        # High complexity files (15 min per 10 complexity points above 20)
        for file_data in heatmap:
            complexity = file_data.get("complexity", 0)
            if complexity > 20:
                excess_complexity = complexity - 20
                hours = (excess_complexity / 10) * 0.25  # 15 min per 10 points
                debt_hours += hours
                if hours > 0.5:  # Report significant debt
                    debt_items.append({
                        "file": file_data["file"],
                        "type": "high_complexity",
                        "hours": round(hours, 2),
                        "description": f"Complexity {complexity} (threshold: 20)"
                    })
        
        # Code duplications (10 min per duplicate block)
        duplication_rate = duplications.get("duplication_rate", 0)
        if duplication_rate > 5:
            hours = (duplication_rate / 5) * 0.5  # 30 min per 5%
            debt_hours += hours
            debt_items.append({
                "file": "codebase",
                "type": "code_duplication",
                "hours": round(hours, 2),
                "description": f"{duplication_rate}% duplication detected"
            })
        
        # Large files (30 min per 500 LOC above 500)
        for file_data in heatmap:
            loc = file_data.get("loc", 0)
            if loc > 500:
                excess_loc = loc - 500
                hours = (excess_loc / 500) * 0.5
                debt_hours += hours
                if hours > 0.5:
                    debt_items.append({
                        "file": file_data["file"],
                        "type": "large_file",
                        "hours": round(hours, 2),
                        "description": f"{loc} LOC (threshold: 500)"
                    })
        
        return {
            "total_hours": round(debt_hours, 1),
            "items": sorted(debt_items, key=lambda x: x["hours"], reverse=True)[:15],
            "cost_estimate": round(debt_hours * 75, 0)  # $75/hour average
        }
    
    def _detect_code_smells(self, heatmap: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect common code smells.
        
        Args:
            heatmap: File complexity data
            
        Returns:
            List of detected code smells
        """
        smells = []
        
        for file_data in heatmap:
            file_path = self.project_root / file_data["file"]
            
            try:
                content = file_path.read_text()
                
                # Long method detection (methods > 50 LOC)
                long_methods = re.findall(r'def\s+(\w+)\([^)]*\):', content)
                if len(long_methods) > 10:
                    smells.append({
                        "file": file_data["file"],
                        "type": "god_object",
                        "severity": "high",
                        "description": f"{len(long_methods)} methods detected - possible God Object"
                    })
                
                # Missing docstrings
                if '"""' not in content and "'''" not in content:
                    smells.append({
                        "file": file_data["file"],
                        "type": "missing_documentation",
                        "severity": "medium",
                        "description": "No docstrings found"
                    })
                
                # Long parameter lists
                long_params = re.findall(r'def\s+\w+\(([^)]{50,})\):', content)
                if long_params:
                    smells.append({
                        "file": file_data["file"],
                        "type": "long_parameter_list",
                        "severity": "medium",
                        "description": f"{len(long_params)} methods with long parameter lists"
                    })
                
            except Exception as e:
                self.logger.debug(f"Error detecting smells in {file_path}: {e}")
                continue
        
        return smells[:30]  # Top 30 smells
    
    def _detect_duplications(self) -> Dict[str, Any]:
        """
        Detect code duplications across files.
        
        Returns:
            Dict with duplication statistics
        """
        duplications = {
            "duplicate_blocks": [],
            "duplication_rate": 0,
            "files_with_duplicates": 0
        }
        
        # Use RecursiveScanner to find all Python files from root
        scanner = RecursiveScanner(self.project_root, logger=self.logger)
        py_files = scanner.scan_python_files()
        
        if not py_files:
            return duplications
        
        # Simple duplication detection: look for identical function signatures
        function_hashes = {}
        total_functions = 0
        duplicate_count = 0
        
        for py_file in py_files:
            
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        # Create simple hash from function body size and name
                        func_hash = f"{node.name}_{len(ast.dump(node))}"
                        
                        if func_hash in function_hashes:
                            duplicate_count += 1
                            duplications["duplicate_blocks"].append({
                                "function": node.name,
                                "file1": function_hashes[func_hash],
                                "file2": str(py_file.relative_to(self.project_root)),
                                "lines": len(ast.dump(node).split('\n'))
                            })
                        else:
                            function_hashes[func_hash] = str(py_file.relative_to(self.project_root))
                            
            except Exception as e:
                self.logger.debug(f"Error analyzing {py_file} for duplications: {e}")
                continue
        
        if total_functions > 0:
            duplications["duplication_rate"] = round((duplicate_count / total_functions) * 100, 2)
        
        duplications["files_with_duplicates"] = len(set(d["file2"] for d in duplications["duplicate_blocks"]))
        duplications["duplicate_blocks"] = duplications["duplicate_blocks"][:20]  # Top 20
        
        return duplications
    
    def _calculate_maintainability(self, heatmap: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate maintainability index for codebase.
        
        Maintainability Index = 171 - 5.2 * ln(Halstead Volume) 
                                - 0.23 * (Cyclomatic Complexity) 
                                - 16.2 * ln(Lines of Code)
        
        Simplified version using available metrics.
        
        Args:
            heatmap: File complexity data
            
        Returns:
            Dict with maintainability scores
        """
        maintainability = {
            "overall_score": 0,
            "files_by_category": {
                "excellent": 0,  # > 85
                "good": 0,       # 65-85
                "fair": 0,       # 50-65
                "poor": 0        # < 50
            },
            "worst_files": []
        }
        
        if not heatmap:
            return maintainability
        
        file_scores = []
        
        for file_data in heatmap:
            complexity = file_data["complexity"]
            loc = file_data["loc"]
            
            # Simplified maintainability calculation
            if loc > 0 and complexity > 0:
                # Score based on complexity-to-LOC ratio
                complexity_ratio = complexity / max(loc / 100, 1)  # Complexity per 100 LOC
                
                # Calculate score (0-100, inverted so lower complexity = higher score)
                score = max(0, 100 - (complexity_ratio * 10))
                
                file_scores.append({
                    "file": file_data["file"],
                    "score": int(score),
                    "complexity": complexity,
                    "loc": loc
                })
                
                # Categorize
                if score > 85:
                    maintainability["files_by_category"]["excellent"] += 1
                elif score > 65:
                    maintainability["files_by_category"]["good"] += 1
                elif score > 50:
                    maintainability["files_by_category"]["fair"] += 1
                else:
                    maintainability["files_by_category"]["poor"] += 1
        
        # Calculate overall score
        if file_scores:
            maintainability["overall_score"] = int(sum(f["score"] for f in file_scores) / len(file_scores))
        
        # Get worst files
        file_scores.sort(key=lambda x: x["score"])
        maintainability["worst_files"] = file_scores[:10]
        
        return maintainability
    
    def _estimate_technical_debt(self, heatmap: List[Dict[str, Any]], 
                                 duplications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate technical debt in hours.
        
        Based on SQALE methodology:
        - High complexity files: 0.5h per 10 complexity points
        - Code duplications: 0.25h per duplicate block
        - Large files (>500 LOC): 0.1h per 100 LOC over threshold
        
        Args:
            heatmap: File complexity data
            duplications: Duplication data
            
        Returns:
            Dict with debt estimation
        """
        debt = {
            "total_hours": 0,
            "by_category": {
                "complexity": 0,
                "duplication": 0,
                "size": 0,
                "change_frequency": 0
            },
            "high_debt_files": []
        }
        
        file_debts = []
        
        # Calculate debt per file
        for file_data in heatmap:
            file_debt = 0
            
            # Complexity debt (high complexity = more refactoring time)
            complexity = file_data["complexity"]
            if complexity > 20:
                complexity_debt = (complexity - 20) * 0.05  # 0.05h per point over 20
                file_debt += complexity_debt
                debt["by_category"]["complexity"] += complexity_debt
            
            # Size debt (large files harder to understand)
            loc = file_data["loc"]
            if loc > 500:
                size_debt = ((loc - 500) / 100) * 0.1  # 0.1h per 100 LOC over 500
                file_debt += size_debt
                debt["by_category"]["size"] += size_debt
            
            # Change frequency debt (unstable code needs stabilization)
            change_freq = file_data.get("change_frequency", 0)
            if change_freq > 20:
                change_debt = (change_freq - 20) * 0.02  # 0.02h per commit over 20
                file_debt += change_debt
                debt["by_category"]["change_frequency"] += change_debt
            
            if file_debt > 0:
                file_debts.append({
                    "file": file_data["file"],
                    "debt_hours": round(file_debt, 2),
                    "complexity": complexity,
                    "loc": loc,
                    "change_frequency": change_freq
                })
        
        # Duplication debt
        dup_count = len(duplications.get("duplicate_blocks", []))
        duplication_debt = dup_count * 0.25
        debt["by_category"]["duplication"] = round(duplication_debt, 2)
        
        # Calculate total
        debt["total_hours"] = round(sum(debt["by_category"].values()), 2)
        
        # Sort files by debt
        file_debts.sort(key=lambda x: x["debt_hours"], reverse=True)
        debt["high_debt_files"] = file_debts[:15]
        
        return debt
    
    def _analyze_file_sizes(self) -> Dict[str, Any]:
        """
        Analyze file sizes and identify oversized files (multi-language support).
        
        Supports all languages defined in _generate_heatmap() method.
        
        Returns:
            Dict with file size statistics
        """
        sizes = {
            "distribution": {
                "small": 0,      # < 100 LOC
                "medium": 0,     # 100-300 LOC
                "large": 0,      # 300-500 LOC
                "very_large": 0  # > 500 LOC
            },
            "largest_files": []
        }
        
        file_list = []
        
        # Use same multi-language patterns as _generate_heatmap
        file_patterns = [
            '**/*.py', '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx', '**/*.vue',
            '**/*.cs', '**/*.vb', '**/*.fs',
            '**/*.java', '**/*.kt', '**/*.scala', '**/*.groovy',
            '**/*.c', '**/*.cpp', '**/*.cc', '**/*.cxx', '**/*.h', '**/*.hpp',
            '**/*.go', '**/*.rs',
            '**/*.swift', '**/*.m', '**/*.mm',
            '**/*.php', '**/*.rb', '**/*.pl', '**/*.pm',
            '**/*.sh', '**/*.bash', '**/*.ps1', '**/*.r', '**/*.R',
            '**/*.sql', '**/*.lua', '**/*.dart'
        ]
        
        for pattern in file_patterns:
            for code_file in self.project_root.glob(pattern):
                # Skip common non-source directories
                path_str = str(code_file)
                if any(skip in path_str for skip in ['venv', '__pycache__', 'node_modules', 'bin', 'obj', '.git', 'packages']):
                    continue
                
                try:
                    loc = self._count_loc(code_file)
                    file_size_kb = code_file.stat().st_size / 1024
                    
                    file_list.append({
                        "file": str(code_file.relative_to(self.project_root)),
                        "loc": loc,
                        "size_kb": round(file_size_kb, 2)
                    })
                    
                    # Categorize
                    if loc < 100:
                        sizes["distribution"]["small"] += 1
                    elif loc < 300:
                        sizes["distribution"]["medium"] += 1
                    elif loc < 500:
                        sizes["distribution"]["large"] += 1
                    else:
                        sizes["distribution"]["very_large"] += 1
                        
                except Exception as e:
                    self.logger.debug(f"Error analyzing size of {code_file}: {e}")
                    continue
        
        # Get largest files
        file_list.sort(key=lambda x: x["loc"], reverse=True)
        sizes["largest_files"] = file_list[:15]
        
        return sizes
    
    def _detect_code_smells(self, heatmap: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect common code smells.
        
        Code smells detected:
        - God Class (very large files with high complexity)
        - Long Method (high complexity concentration)
        - Feature Envy (frequent changes)
        - Dead Code (no recent changes)
        
        Args:
            heatmap: File complexity data
            
        Returns:
            List of code smells with details
        """
        smells = []
        
        for file_data in heatmap:
            file_path = file_data["file"]
            complexity = file_data["complexity"]
            loc = file_data["loc"]
            change_freq = file_data.get("change_frequency", 0)
            
            # God Class: Large file with high complexity
            if loc > 500 and complexity > 30:
                smells.append({
                    "type": "God Class",
                    "severity": "high",
                    "file": file_path,
                    "description": f"Large file ({loc} LOC) with high complexity ({complexity})",
                    "recommendation": "Split into smaller, focused modules",
                    "metrics": {
                        "loc": loc,
                        "complexity": complexity
                    }
                })
            
            # Long Method indicator: Very high complexity
            elif complexity > 50:
                smells.append({
                    "type": "Long Method",
                    "severity": "medium",
                    "file": file_path,
                    "description": f"Excessively high complexity ({complexity})",
                    "recommendation": "Extract smaller methods, reduce nesting",
                    "metrics": {
                        "complexity": complexity
                    }
                })
            
            # Feature Envy: Frequent changes
            if change_freq > 50:
                smells.append({
                    "type": "Feature Envy",
                    "severity": "medium",
                    "file": file_path,
                    "description": f"Frequently modified ({change_freq} commits)",
                    "recommendation": "Stabilize with comprehensive tests, reduce coupling",
                    "metrics": {
                        "change_frequency": change_freq
                    }
                })
            
            # Dead Code: No changes and low complexity (might be unused)
            if change_freq == 0 and complexity < 5 and loc > 50:
                smells.append({
                    "type": "Potential Dead Code",
                    "severity": "low",
                    "file": file_path,
                    "description": f"No recent changes, low complexity ({complexity})",
                    "recommendation": "Review if still needed, consider removal",
                    "metrics": {
                        "complexity": complexity,
                        "change_frequency": change_freq
                    }
                })
        
        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        smells.sort(key=lambda x: (severity_order.get(x["severity"], 3), x["file"]))
        
        return smells[:25]  # Top 25 code smells
