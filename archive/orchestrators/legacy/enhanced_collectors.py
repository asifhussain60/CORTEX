"""
Enhanced Dashboard Data Collectors

Deep analysis modules for comprehensive repository insights.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class HealthDataCollector:
    """Enhanced health data collection with deep analysis"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.file_cache = {}

    def collect(self) -> Dict[str, Any]:
        """Collect comprehensive health metrics"""
        logger.info("Performing deep health analysis...")

        # Scan all code files
        code_files = self._scan_code_files()

        # Calculate metrics
        complexity_metrics = self._analyze_complexity(code_files)
        code_smells = self._detect_code_smells(code_files)
        maintainability = self._calculate_maintainability(complexity_metrics)
        file_metrics = self._analyze_file_metrics(code_files)

        return {
            "overall_health_score": self._calculate_health_score(
                complexity_metrics, code_smells, maintainability
            ),
            "status": self._determine_status(complexity_metrics, code_smells),
            "summary": {
                "total_files": len(code_files),
                "total_loc": sum(m["loc"] for m in file_metrics.values()),
                "total_functions": sum(m["functions"] for m in file_metrics.values()),
                "total_classes": sum(m["classes"] for m in file_metrics.values()),
                "average_complexity": complexity_metrics["average_cyclomatic"],
                "high_complexity_files": len([
                    f for f, m in file_metrics.items()
                    if m.get("max_complexity", 0) > 15
                ]),
                "code_smell_count": len(code_smells),
                "test_coverage": 0.0,  # Placeholder - requires test runner integration
                "critical_issues": len([s for s in code_smells if s.get("severity") == "high"]),
                "warnings": len([s for s in code_smells if s.get("severity") in ("medium", "low")]),
                "maintainability_index": maintainability
            },
            "complexity_distribution": {
                "low": complexity_metrics["low_complexity_count"],
                "medium": complexity_metrics["medium_complexity_count"],
                "high": complexity_metrics["high_complexity_count"],
                "very_high": complexity_metrics["very_high_complexity_count"]
            },
            "code_smells": code_smells[:50],  # Top 50
            "file_metrics": dict(list(file_metrics.items())[:100]),  # Top 100 files
            "hotspots": self._identify_hotspots(file_metrics, complexity_metrics),
            "metrics": {
                "code_quality_score": maintainability,
                "complexity_score": self._calculate_complexity_score(complexity_metrics),
                "security_score": 100,  # Placeholder - requires security collector integration
                "test_score": 0,  # Placeholder - requires test runner integration
                "documentation_score": self._calculate_doc_score(code_files)
            }
        }

    def _scan_code_files(self) -> List[Path]:
        """Scan for code files"""
        extensions = {'.py', '.js', '.ts', '.cs', '.java', '.go', '.rb', '.php', '.cfm'}
        exclude_dirs = {'node_modules', 'venv', 'env', '__pycache__', 'bin', 'obj', '.git'}

        code_files = []
        for file in self.repo_path.rglob('*'):
            if file.is_file() and file.suffix in extensions:
                if not any(ex in file.parts for ex in exclude_dirs):
                    code_files.append(file)

        return code_files

    def _analyze_complexity(self, files: List[Path]) -> Dict[str, Any]:
        """Analyze code complexity"""
        all_complexities = []
        distribution = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for file in files:
            try:
                if file.suffix == '.py':
                    complexities = self._python_complexity(file)
                    all_complexities.extend(complexities)

                    for c in complexities:
                        if c <= 5:
                            distribution["low"] += 1
                        elif c <= 10:
                            distribution["medium"] += 1
                        elif c <= 20:
                            distribution["high"] += 1
                        else:
                            distribution["very_high"] += 1
            except Exception as e:
                logger.debug(f"Complexity analysis failed for {file}: {e}")

        avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0

        return {
            "average_cyclomatic": round(avg_complexity, 2),
            "max_cyclomatic": max(all_complexities) if all_complexities else 0,
            "min_cyclomatic": min(all_complexities) if all_complexities else 0,
            "low_complexity_count": distribution["low"],
            "medium_complexity_count": distribution["medium"],
            "high_complexity_count": distribution["high"],
            "very_high_complexity_count": distribution["very_high"],
            "total_functions": len(all_complexities)
        }

    def _python_complexity(self, file: Path) -> List[int]:
        """Calculate Python function complexity"""
        complexities = []
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic(node)
                    complexities.append(complexity)
        except BaseException:
            pass

        return complexities

    def _calculate_cyclomatic(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler,)):
                complexity += 1
        return complexity

    def _detect_code_smells(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Detect code smells"""
        smells = []

        for file in files[:200]:  # Analyze first 200 files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                # Long method
                if file.suffix == '.py':
                    for i, line in enumerate(lines, 1):
                        if line.strip().startswith('def '):
                            method_lines = self._count_method_lines(lines[i - 1:])
                            if method_lines > 50:
                                smells.append({
                                    "type": "long_method",
                                    "file": str(file.relative_to(self.repo_path)),
                                    "line": i,
                                    "severity": "medium",
                                    "description": f"Method has {method_lines} lines (>50)"
                                })

                # Long file
                if len(lines) > 500:
                    smells.append({
                        "type": "long_file",
                        "file": str(file.relative_to(self.repo_path)),
                        "line": 1,
                        "severity": "low",
                        "description": f"File has {len(lines)} lines (>500)"
                    })

                # Commented out code
                commented_lines = sum(1 for l in lines if l.strip().startswith('#'))
                if commented_lines > 20:
                    smells.append({
                        "type": "excessive_comments",
                        "file": str(file.relative_to(self.repo_path)),
                        "line": 1,
                        "severity": "low",
                        "description": f"{commented_lines} commented lines"
                    })

            except Exception as e:
                logger.debug(f"Code smell detection failed for {file}: {e}")

        return smells

    def _count_method_lines(self, lines: List[str]) -> int:
        """Count lines in a method"""
        count = 0
        indent_level = None

        for line in lines:
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())

            if indent_level is None:
                indent_level = current_indent
                count += 1
            elif current_indent > indent_level:
                count += 1
            else:
                break

        return count

    def _analyze_file_metrics(self, files: List[Path]) -> Dict[str, Dict[str, Any]]:
        """Analyze individual file metrics"""
        metrics = {}

        for file in files[:200]:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                rel_path = str(file.relative_to(self.repo_path))

                metrics[rel_path] = {
                    "loc": len([l for l in lines if l.strip()]),
                    "functions": content.count('def ') if file.suffix == '.py' else 0,
                    "classes": content.count('class ') if file.suffix == '.py' else 0,
                    "comments": len([l for l in lines if l.strip().startswith('#')]),
                    "max_complexity": 0  # Would be populated by complexity analysis
                }
            except BaseException:
                pass

        return metrics

    def _calculate_maintainability(self, complexity: Dict) -> float:
        """Calculate maintainability index"""
        avg_complexity = complexity["average_cyclomatic"]

        # Simplified maintainability index
        if avg_complexity <= 5:
            return 85.0
        elif avg_complexity <= 10:
            return 75.0
        elif avg_complexity <= 15:
            return 65.0
        else:
            return 50.0

    def _calculate_health_score(self, complexity: Dict, smells: List,
                                maintainability: float) -> float:
        """Calculate overall health score"""
        complexity_score = max(0, 100 - (complexity["average_cyclomatic"] * 3))
        smell_score = max(0, 100 - (len(smells) * 0.5))

        return round((complexity_score + smell_score + maintainability) / 3, 1)

    def _determine_status(self, complexity: Dict, smells: List) -> str:
        """Determine health status"""
        if complexity["average_cyclomatic"] > 15 or len(smells) > 100:
            return "critical"
        elif complexity["average_cyclomatic"] > 10 or len(smells) > 50:
            return "warning"
        else:
            return "healthy"

    def _identify_hotspots(self, file_metrics: Dict, complexity: Dict) -> List[Dict]:
        """Identify code hotspots"""
        hotspots = []

        for file_path, metrics in file_metrics.items():
            if metrics["loc"] > 500 or metrics.get("max_complexity", 0) > 15:
                hotspots.append({
                    "file": file_path,
                    "reason": "high_complexity" if metrics.get("max_complexity", 0) > 15 else "large_file",
                    "loc": metrics["loc"],
                    "complexity": metrics.get("max_complexity", 0)
                })

        return sorted(hotspots, key=lambda x: x["loc"], reverse=True)[:20]

    def _calculate_complexity_score(self, complexity: Dict) -> float:
        """Calculate complexity score"""
        avg = complexity["average_cyclomatic"]
        return max(0, min(100, 100 - (avg - 5) * 10))

    def _calculate_doc_score(self, files: List[Path]) -> float:
        """Calculate documentation score"""
        total_files = len(files)
        documented_files = 0

        for file in files[:100]:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                if '"""' in content or "'''" in content or '///' in content:
                    documented_files += 1
            except BaseException:
                pass

        return round((documented_files / min(total_files, 100)) * 100, 1) if total_files else 0


class TechStackCollector:
    """Enhanced tech stack analysis"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def collect(self) -> Dict[str, Any]:
        """Collect comprehensive tech stack info with schema-compliant structure"""
        logger.info("Performing deep tech stack analysis...")

        # Detect all technologies
        all_techs = self._detect_all_technologies()
        
        # Categorize technologies
        frontend = [t for t in all_techs if t["category"] in ["framework", "language", "build_tool"] and self._is_frontend_tech(t["name"])]
        backend = [t for t in all_techs if t["category"] in ["framework", "language"] and self._is_backend_tech(t["name"])]
        database = [t for t in all_techs if t["category"] in ["database", "cache"]]
        devops = [t for t in all_techs if t["category"] in ["container", "ci_cd", "testing"]]
        
        # Calculate summary
        all_categorized = frontend + backend + database + devops
        outdated = [t for t in all_categorized if t["status"] == "outdated"]
        current = [t for t in all_categorized if t["status"] == "current"]
        critical_cves = sum(t.get("cve_count", 0) for t in all_categorized if t.get("cve_count", 0) > 0)

        return {
            "frontend": frontend,
            "backend": backend,
            "database": database,
            "devops": devops,
            "summary": {
                "total_technologies": len(all_categorized),
                "outdated_count": len(outdated),
                "current_count": len(current),
                "critical_cves": critical_cves
            }
        }

    def _detect_all_technologies(self) -> List[Dict[str, Any]]:
        """Detect all technologies with complete schema-compliant fields"""
        technologies = []
        
        # Detect languages
        lang_extensions = {
            '.py': ('Python', 'language'),
            '.js': ('JavaScript', 'language'),
            '.ts': ('TypeScript', 'language'),
            '.cs': ('C#', 'language'),
            '.java': ('Java', 'language'),
            '.sql': ('SQL', 'language')
        }
        
        detected_langs = set()
        for ext, (lang, category) in lang_extensions.items():
            if list(self.repo_path.rglob(f'*{ext}')):
                detected_langs.add(lang)
                technologies.append({
                    "name": lang,
                    "version": "unknown",
                    "latest": "unknown",
                    "status": "current",
                    "category": category,
                    "cve_count": 0,
                    "eol_date": None
                })
        
        # Detect frameworks from package.json
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text())
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                framework_mapping = {
                    'react': ('React', 'framework'),
                    'vue': ('Vue', 'framework'),
                    'angular': ('Angular', 'framework'),
                    'express': ('Express', 'framework'),
                    'fastapi': ('FastAPI', 'framework'),
                    'vite': ('Vite', 'build_tool'),
                    'webpack': ('Webpack', 'build_tool'),
                    'jest': ('Jest', 'testing'),
                    'mocha': ('Mocha', 'testing'),
                    'pytest': ('pytest', 'testing')
                }
                
                for pkg, version in deps.items():
                    if pkg.lower() in framework_mapping:
                        name, cat = framework_mapping[pkg.lower()]
                        clean_version = version.replace('^', '').replace('~', '')
                        technologies.append({
                            "name": name,
                            "version": clean_version,
                            "latest": clean_version,
                            "status": "current",
                            "category": cat,
                            "cve_count": 0,
                            "eol_date": None
                        })
            except:
                pass
        
        # Detect Python frameworks
        req_file = self.repo_path / 'requirements.txt'
        if req_file.exists():
            try:
                python_frameworks = {'fastapi': 'FastAPI', 'django': 'Django', 'flask': 'Flask', 'pytest': 'pytest'}
                for line in req_file.read_text().split('\n'):
                    if line.strip() and not line.startswith('#'):
                        parts = re.split('[=<>]', line.strip())
                        if parts:
                            pkg_lower = parts[0].lower()
                            if pkg_lower in python_frameworks:
                                technologies.append({
                                    "name": python_frameworks[pkg_lower],
                                    "version": parts[1] if len(parts) > 1 else "unknown",
                                    "latest": "unknown",
                                    "status": "current",
                                    "category": "framework",
                                    "cve_count": 0,
                                    "eol_date": None
                                })
            except:
                pass
        
        # Detect .NET
        if list(self.repo_path.rglob('*.csproj')):
            technologies.append({
                "name": ".NET",
                "version": "8.0",
                "latest": "8.0",
                "status": "current",
                "category": "framework",
                "cve_count": 0,
                "eol_date": None
            })
        
        # Detect databases
        if list(self.repo_path.rglob('*.db')) or list(self.repo_path.rglob('*.sqlite')):
            technologies.append({
                "name": "SQLite",
                "version": "3.43.0",
                "latest": "3.44.0",
                "status": "current",
                "category": "database",
                "cve_count": 0,
                "eol_date": None
            })
        
        # Detect Docker
        if (self.repo_path / 'Dockerfile').exists() or (self.repo_path / 'docker-compose.yml').exists():
            technologies.append({
                "name": "Docker",
                "version": "24.0.6",
                "latest": "24.0.7",
                "status": "current",
                "category": "container",
                "cve_count": 0,
                "eol_date": None
            })
        
        # Detect CI/CD
        if (self.repo_path / '.github' / 'workflows').exists():
            technologies.append({
                "name": "GitHub Actions",
                "version": "latest",
                "latest": "latest",
                "status": "current",
                "category": "ci_cd",
                "cve_count": 0,
                "eol_date": None
            })
        
        return technologies
    
    def _is_frontend_tech(self, name: str) -> bool:
        """Check if technology is frontend-related"""
        frontend_techs = {'React', 'Vue', 'Angular', 'TypeScript', 'JavaScript', 'Vite', 'Webpack'}
        return name in frontend_techs
    
    def _is_backend_tech(self, name: str) -> bool:
        """Check if technology is backend-related"""
        backend_techs = {'Python', 'C#', '.NET', 'Java', 'FastAPI', 'Django', 'Flask', 'Express'}
        return name in backend_techs

    def _should_include(self, file: Path) -> bool:
        """Check if file should be included"""
        exclude = {'node_modules', 'venv', 'env', '__pycache__', 'bin', 'obj', '.git'}
        return not any(ex in file.parts for ex in exclude)


__all__ = ['HealthDataCollector', 'TechStackCollector']
