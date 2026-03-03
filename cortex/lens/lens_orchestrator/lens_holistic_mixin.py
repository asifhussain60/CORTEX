"""
LensHolisticMixin — repository-level holistic analysis for LENSOrchestrator.

Covers:
  - analyze_repository_holistic  (9-analyzer flagship method)
  - _analyze_repository_summary
  - _analyze_codebase_structure
  - _analyze_configurations
  - _analyze_database_artifacts
  - _analyze_api_specs
  - _analyze_visual_artifacts
  - _synthesize_security_findings
  - _generate_holistic_recommendations

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, LENS-003
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

__all__ = ["LensHolisticMixin"]


class LensHolisticMixin:
    """
    Mixin providing repository-level holistic analysis.

    Requires the host class to have:
        self.repo_path: Path
        self.git_analyzer: GitHistoryAnalyzer
        self.ast_analyzer: ASTAnalyzer
        self.comment_extractor: CommentExtractor
        self.config_analyzer: ConfigAnalyzer
        self.database_analyzer: DatabaseAnalyzer
        self.api_analyzer: APIAnalyzer
    """

    def analyze_repository_holistic(
        self,
        include_vision: bool = False,
        include_security: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform holistic repository analysis integrating all 9 LENS v2.0 analyzers.

        Args:
            include_vision: Whether to analyze images (slower, requires Vision API)
            include_security: Whether to run security analysis (recommended: True)

        Returns:
            Dict with repository_summary, code_analysis, security_analysis,
            config_analysis, database_analysis, api_analysis, vision_analysis,
            recommendations, metadata.
        """
        start_time = time.time()

        result: Dict[str, Any] = {
            "repository_summary": {},
            "code_analysis": {},
            "security_analysis": {},
            "config_analysis": {},
            "database_analysis": {},
            "api_analysis": {},
            "vision_analysis": {},
            "recommendations": [],
            "metadata": {
                "analysis_start": time.strftime("%Y-%m-%d %H:%M:%S"),
                "analyzers_enabled": [],
            },
        }

        try:
            result["metadata"]["analyzers_enabled"].append("git")
            result["repository_summary"] = self._analyze_repository_summary()

            result["metadata"]["analyzers_enabled"].extend(["ast", "comment"])
            result["code_analysis"] = self._analyze_codebase_structure()

            if include_security:
                result["metadata"]["analyzers_enabled"].append("config")
                result["config_analysis"] = self._analyze_configurations()

            result["metadata"]["analyzers_enabled"].append("database")
            result["database_analysis"] = self._analyze_database_artifacts()

            result["metadata"]["analyzers_enabled"].append("api")
            result["api_analysis"] = self._analyze_api_specs()

            if include_vision:
                result["metadata"]["analyzers_enabled"].append("vision")
                result["vision_analysis"] = self._analyze_visual_artifacts()

            if include_security:
                result["metadata"]["analyzers_enabled"].append("security")
                result["security_analysis"] = self._synthesize_security_findings(
                    result["config_analysis"],
                    result["database_analysis"],
                    result["api_analysis"],
                )

            result["recommendations"] = self._generate_holistic_recommendations(result)

            analysis_time_ms = (time.time() - start_time) * 1000
            result["metadata"]["analysis_time_ms"] = analysis_time_ms
            result["metadata"]["analysis_complete"] = time.strftime("%Y-%m-%d %H:%M:%S")
            result["metadata"]["success"] = True

        except Exception as e:
            result["metadata"]["success"] = False
            result["metadata"]["error"] = str(e)
            result["metadata"]["analysis_time_ms"] = (time.time() - start_time) * 1000

        return result

    def _analyze_repository_summary(self) -> Dict[str, Any]:
        """Get repository-level git statistics and multi-language file counts."""
        try:
            language_extensions = {
                "Python": [".py"],
                "JavaScript": [".js", ".jsx", ".mjs"],
                "TypeScript": [".ts", ".tsx"],
                "C#": [".cs"],
                "VB.NET": [".vb"],
                "Java": [".java"],
                "Go": [".go"],
                "Rust": [".rs"],
                "Ruby": [".rb"],
                "PHP": [".php"],
                "ASP.NET": [".aspx", ".ascx", ".asmx"],
                "HTML": [".html", ".htm"],
                "CSS": [".css", ".scss", ".sass"],
                "SQL": [".sql"],
                "Config": [".yaml", ".yml", ".json", ".xml", ".config"],
            }
            SKIP_DIRS = {
                "node_modules", "bower_components", ".git",
                "__pycache__", ".venv", "venv", "dist", "build", "out",
            }
            file_counts: Dict[str, int] = {}
            total_source_files = 0
            for lang, exts in language_extensions.items():
                count = 0
                for ext in exts:
                    for fp in self.repo_path.rglob(f"*{ext}"):  # type: ignore[attr-defined]
                        if not any(s in fp.parts for s in SKIP_DIRS):
                            count += 1
                if count > 0:
                    file_counts[lang] = count
                    total_source_files += count

            result = self.git_analyzer.get_recent_commits(max_commits=1000)  # type: ignore[attr-defined]
            if result.success:
                commits = result.commits
                contributors = {commit.author for commit in commits}
                primary_language = max(file_counts, key=file_counts.get) if file_counts else "Unknown"
                return {
                    "total_commits": len(commits),
                    "total_contributors": len(contributors),
                    "contributors": sorted(contributors),
                    "total_source_files": total_source_files,
                    "primary_language": primary_language,
                    "file_counts_by_language": file_counts,
                    "recent_commit": commits[0].message if commits else "N/A",
                    "repo_path": str(self.repo_path),  # type: ignore[attr-defined]
                }
            else:
                return {
                    "error": result.error,
                    "total_source_files": total_source_files,
                    "file_counts_by_language": file_counts,
                    "primary_language": max(file_counts, key=file_counts.get) if file_counts else "Unknown",
                }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_codebase_structure(self) -> Dict[str, Any]:
        """Analyze code structure across all supported languages."""
        try:
            python_files = list(self.repo_path.rglob("*.py"))[:100]  # type: ignore[attr-defined]
            total_functions = 0
            total_classes = 0
            total_todos = 0
            complex_files: List[Dict[str, Any]] = []

            for py_file in python_files:
                try:
                    ast_result = self.ast_analyzer.analyze_file(py_file)  # type: ignore[attr-defined]
                    if ast_result.success:
                        total_functions += len(ast_result.functions)
                        total_classes += len(ast_result.classes)
                        if len(ast_result.functions) > 10 or len(ast_result.classes) > 5:
                            complex_files.append({
                                "file": str(py_file.relative_to(self.repo_path)),  # type: ignore[attr-defined]
                                "functions": len(ast_result.functions),
                                "classes": len(ast_result.classes),
                            })
                    comment_result = self.comment_extractor.extract_from_file(py_file)  # type: ignore[attr-defined]
                    if comment_result.success:
                        total_todos += len(comment_result.todos)
                except Exception:
                    continue

            language_file_counts: Dict[str, int] = {}
            source_patterns = {
                "Python": "**/*.py",
                "JavaScript": "**/*.js",
                "TypeScript": "**/*.ts",
                "C#": "**/*.cs",
                "VB.NET": "**/*.vb",
                "Java": "**/*.java",
                "ASP.NET": "**/*.aspx",
            }
            for lang, pattern in source_patterns.items():
                files = list(self.repo_path.rglob(pattern.replace("**/", "")))  # type: ignore[attr-defined]
                if files:
                    language_file_counts[lang] = len(files)

            todo_locations: List[Dict[str, Any]] = []
            for pat in ["**/*.cs", "**/*.vb", "**/*.js", "**/*.ts", "**/*.java"]:
                for f in list(self.repo_path.rglob(pat.replace("**/", "")))[:50]:  # type: ignore[attr-defined]
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        for i, line in enumerate(content.splitlines(), 1):
                            if "TODO" in line.upper() or "FIXME" in line.upper():
                                total_todos += 1
                                if len(todo_locations) < 20:
                                    todo_locations.append({
                                        "file": str(f.relative_to(self.repo_path)),  # type: ignore[attr-defined]
                                        "line": i,
                                        "text": line.strip()[:100],
                                    })
                    except Exception:
                        continue

            return {
                "files_analyzed": len(python_files),
                "language_file_counts": language_file_counts,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "total_todos": total_todos,
                "complex_files": complex_files[:10],
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_configurations(self) -> Dict[str, Any]:
        """Analyze configuration files for security issues."""
        try:
            config_result = self.config_analyzer.analyze_repository(self.repo_path)  # type: ignore[attr-defined]
            p0_findings = config_result.get("p0_findings", [])
            p1_findings = config_result.get("p1_findings", [])
            p2_findings = config_result.get("p2_findings", [])
            all_findings = p0_findings + p1_findings + p2_findings
            return {
                "files_analyzed": config_result.get("analyzed_files", 0),
                "findings_count": len(all_findings),
                "p0_count": len(p0_findings),
                "p1_count": len(p1_findings),
                "p2_count": len(p2_findings),
                "findings": all_findings[:20],
                "summary": config_result.get("summary", ""),
            }
        except Exception as e:
            logger.warning("Config analysis failed: %s", e)
            return {"error": str(e)}

    def _analyze_database_artifacts(self) -> Dict[str, Any]:
        """Analyze database migrations and schemas."""
        try:
            migration_paths = [
                self.repo_path / "migrations",  # type: ignore[attr-defined]
                self.repo_path / "alembic" / "versions",  # type: ignore[attr-defined]
                self.repo_path / "db" / "migrations",  # type: ignore[attr-defined]
            ]
            for migration_path in migration_paths:
                if migration_path.exists():
                    db_result = self.database_analyzer.analyze_migrations(migration_path)  # type: ignore[attr-defined]
                    if db_result.success:
                        return {
                            "migrations_found": len(db_result.migrations),
                            "reversible_count": len(
                                [m for m in db_result.migrations if m.is_reversible]
                            ),
                            "recommendations_count": len(db_result.recommendations),
                            "recommendations": [
                                {
                                    "priority": r["priority"],
                                    "category": r["category"],
                                    "description": r["description"],
                                }
                                for r in db_result.recommendations
                            ],
                        }
            return {"migrations_found": 0, "note": "No migration directories detected"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_api_specs(self) -> Dict[str, Any]:
        """Analyze OpenAPI specifications."""
        try:
            spec_patterns = [
                "openapi.yaml", "openapi.yml", "openapi.json",
                "swagger.yaml", "swagger.json",
            ]
            for pattern in spec_patterns:
                for spec_file in self.repo_path.rglob(pattern):  # type: ignore[attr-defined]
                    api_result = self.api_analyzer.analyze_openapi_spec(spec_file)  # type: ignore[attr-defined]
                    if api_result.success:
                        return {
                            "spec_found": True,
                            "spec_file": str(spec_file.relative_to(self.repo_path)),  # type: ignore[attr-defined]
                            "spec_version": api_result.spec_version.value,
                            "endpoints_count": len(api_result.endpoints),
                            "security_schemes_count": len(api_result.security_schemes),
                            "findings_count": len(api_result.security_findings),
                            "p0_count": len(
                                [f for f in api_result.security_findings if f.priority.value == "P0"]
                            ),
                            "p1_count": len(
                                [f for f in api_result.security_findings if f.priority.value == "P1"]
                            ),
                            "findings": [
                                {
                                    "priority": f.priority.value,
                                    "category": f.category,
                                    "endpoint": f.endpoint,
                                    "description": f.description,
                                    "owasp": f.owasp_api_top_10,
                                }
                                for f in api_result.security_findings[:20]
                            ],
                        }
            return {"spec_found": False, "note": "No OpenAPI spec detected"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_visual_artifacts(self) -> Dict[str, Any]:
        """Analyze images and diagrams (optional)."""
        try:
            images: List[Path] = []
            for pattern in ["*.png", "*.jpg", "*.jpeg"]:
                images.extend(list(self.repo_path.rglob(pattern)))  # type: ignore[attr-defined]
            return {
                "images_found": len(images),
                "note": "Vision analysis requires explicit image paths",
            }
        except Exception as e:
            return {"error": str(e)}

    def _synthesize_security_findings(
        self,
        config_analysis: Dict[str, Any],
        database_analysis: Dict[str, Any],
        api_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize all security findings into unified report."""
        all_findings: List[Dict[str, Any]] = []

        for f in config_analysis.get("findings", []):
            file_path = f.get("file") or f.get("file_path", "unknown")
            line_num = f.get("line") or f.get("line_number", 0)
            all_findings.append({
                "source": "config",
                "priority": f.get("severity", "P2"),
                "category": f.get("category", "security"),
                "location": f"{file_path}:{line_num}",
                "description": f.get("description", ""),
                "recommendation": f.get("recommendation", "Review and fix"),
            })

        for r in database_analysis.get("recommendations", []):
            all_findings.append({
                "source": "database",
                "priority": r["priority"],
                "category": r["category"],
                "location": "migrations",
                "description": r["description"],
                "recommendation": r.get("recommendation", "Review and address"),
            })

        for f in api_analysis.get("findings", []):
            all_findings.append({
                "source": "api",
                "priority": f["priority"],
                "category": f["category"],
                "location": f.get("endpoint", "API spec"),
                "description": f["description"],
                "recommendation": f.get("recommendation", "Review OWASP API guidelines"),
                "owasp": f.get("owasp"),
            })

        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        all_findings.sort(key=lambda x: priority_order.get(x["priority"], 99))

        p0 = [f for f in all_findings if f["priority"] == "P0"]
        p1 = [f for f in all_findings if f["priority"] == "P1"]
        p2 = [f for f in all_findings if f["priority"] == "P2"]
        p3 = [f for f in all_findings if f["priority"] == "P3"]

        return {
            "total_findings": len(all_findings),
            "p0_count": len(p0),
            "p1_count": len(p1),
            "p2_count": len(p2),
            "p3_count": len(p3),
            "findings": all_findings,
            "p0_findings": p0,
            "p1_findings": p1[:10],
            "p2_findings": p2[:10],
            "critical_action_required": len(p0) > 0,
        }

    def _generate_holistic_recommendations(
        self, analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on holistic analysis."""
        recommendations: List[Dict[str, Any]] = []

        security = analysis_result.get("security_analysis", {})
        if security.get("p0_count", 0) > 0:
            recommendations.append({
                "priority": "P0",
                "category": "security",
                "title": f"Address {security['p0_count']} critical security issue(s)",
                "description": "P0 security vulnerabilities detected that must be fixed immediately",
                "action": "Review security_analysis.p0_findings and remediate",
            })
        if security.get("p1_count", 0) > 0:
            recommendations.append({
                "priority": "P1",
                "category": "security",
                "title": f"Review {security['p1_count']} high-priority security finding(s)",
                "description": "P1 security issues should be addressed in next sprint",
                "action": "Review security_analysis.p1_findings and plan remediation",
            })

        code = analysis_result.get("code_analysis", {})
        if code.get("total_todos", 0) > 50:
            recommendations.append({
                "priority": "P2",
                "category": "code_quality",
                "title": f"Address {code['total_todos']} TODOs",
                "description": "High number of TODO comments indicates pending work",
                "action": "Review and resolve TODO items or convert to tracked issues",
            })
        if len(code.get("complex_files", [])) > 5:
            recommendations.append({
                "priority": "P2",
                "category": "code_quality",
                "title": f"Refactor {len(code['complex_files'])} complex file(s)",
                "description": "Files with high function/class count may benefit from refactoring",
                "action": "Review complex_files list and apply SOLID principles",
            })

        db = analysis_result.get("database_analysis", {})
        if db.get("recommendations_count", 0) > 0:
            recommendations.append({
                "priority": "P2",
                "category": "database",
                "title": "Review database migration recommendations",
                "description": f"{db['recommendations_count']} migration issue(s) detected",
                "action": "Review database_analysis.recommendations",
            })

        api = analysis_result.get("api_analysis", {})
        if api.get("p0_count", 0) > 0:
            recommendations.append({
                "priority": "P0",
                "category": "api_security",
                "title": f"Fix {api['p0_count']} critical API security issue(s)",
                "description": "OWASP API Top 10 vulnerabilities detected",
                "action": "Review api_analysis.findings and implement security controls",
            })

        return recommendations
