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
        """Collect comprehensive tech stack info"""
        logger.info("Performing deep tech stack analysis...")

        languages = self._detect_languages_detailed()
        frameworks = self._detect_frameworks_detailed()
        dependencies = self._analyze_dependencies()
        versions = self._detect_versions()

        return {
            "languages": languages,
            "frontend": frameworks["frontend"],
            "backend": frameworks["backend"],
            "databases": frameworks["databases"],
            "testing": frameworks["testing"],
            "infrastructure": frameworks["infrastructure"],
            "dependencies": dependencies,
            "versions": versions,
            "summary": {
                "primary_language": languages[0]["name"] if languages else "Unknown",
                "total_frameworks": sum(len(v) for v in frameworks.values()),
                "total_dependencies": len(dependencies),
                "modernization_score": self._calculate_modernization_score(versions)
            }
        }

    def _detect_languages_detailed(self) -> List[Dict]:
        """Detect languages with detailed metrics"""
        extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.cs': 'C#', '.java': 'Java', '.go': 'Go', '.rb': 'Ruby',
            '.php': 'PHP', '.cfm': 'ColdFusion', '.sql': 'SQL',
            '.html': 'HTML', '.css': 'CSS', '.cpp': 'C++', '.c': 'C'
        }

        lang_stats = defaultdict(lambda: {"files": 0, "loc": 0})

        for ext, lang in extensions.items():
            for file in self.repo_path.rglob(f'*{ext}'):
                if self._should_include(file):
                    lang_stats[lang]["files"] += 1
                    try:
                        content = file.read_text(encoding='utf-8', errors='ignore')
                        lang_stats[lang]["loc"] += len(
                            [l for l in content.split('\n') if l.strip()])
                    except BaseException:
                        pass

        total_loc = sum(s["loc"] for s in lang_stats.values())

        return sorted([
            {
                "name": lang,
                "file_count": stats["files"],
                "loc": stats["loc"],
                "percentage": round((stats["loc"] / total_loc * 100), 1) if total_loc else 0
            }
            for lang, stats in lang_stats.items()
        ], key=lambda x: x["loc"], reverse=True)

    def _detect_frameworks_detailed(self) -> Dict[str, List[Dict]]:
        """Detect frameworks with versions"""
        frameworks = {
            "frontend": [],
            "backend": [],
            "databases": [],
            "testing": [],
            "infrastructure": []
        }

        # Package.json (Node/JS)
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text())
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                for pkg, version in list(deps.items())[:20]:
                    if pkg in ['react', 'vue', 'angular']:
                        frameworks["frontend"].append({"name": pkg, "version": version})
                    elif pkg in ['express', 'fastify', 'koa']:
                        frameworks["backend"].append({"name": pkg, "version": version})
                    elif pkg in ['jest', 'mocha', 'chai']:
                        frameworks["testing"].append({"name": pkg, "version": version})
            except BaseException:
                pass

        # Requirements.txt (Python)
        req_file = self.repo_path / 'requirements.txt'
        if req_file.exists():
            try:
                for line in req_file.read_text().split('\n'):
                    if line.strip() and not line.startswith('#'):
                        parts = re.split('[=<>]', line.strip())
                        if parts:
                            frameworks["backend"].append({"name": parts[0], "version": "unknown"})
            except BaseException:
                pass

        # .csproj (.NET)
        for csproj in self.repo_path.rglob('*.csproj'):
            frameworks["backend"].append({"name": ".NET", "version": "unknown"})
            break

        return frameworks

    def _analyze_dependencies(self) -> List[Dict]:
        """Analyze project dependencies"""
        dependencies = []

        # Simple implementation - would be enhanced with actual dependency parsing
        package_files = [
            self.repo_path / 'package.json',
            self.repo_path / 'requirements.txt',
            self.repo_path / 'Gemfile',
            self.repo_path / 'pom.xml'
        ]

        for pkg_file in package_files:
            if pkg_file.exists():
                dependencies.append({
                    "source": pkg_file.name,
                    "count": len(pkg_file.read_text().split('\n'))
                })

        return dependencies

    def _detect_versions(self) -> Dict[str, str]:
        """Detect technology versions"""
        versions = {}

        # Node version
        nvmrc = self.repo_path / '.nvmrc'
        if nvmrc.exists():
            versions["node"] = nvmrc.read_text().strip()

        # Python version
        python_version = self.repo_path / '.python-version'
        if python_version.exists():
            versions["python"] = python_version.read_text().strip()

        return versions

    def _calculate_modernization_score(self, versions: Dict) -> float:
        """Calculate modernization score"""
        # Simplified - would check against latest versions
        return 75.0

    def _should_include(self, file: Path) -> bool:
        """Check if file should be included"""
        exclude = {'node_modules', 'venv', 'env', '__pycache__', 'bin', 'obj', '.git'}
        return not any(ex in file.parts for ex in exclude)


__all__ = ['HealthDataCollector', 'TechStackCollector']
