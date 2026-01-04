"""
Phase 1: Code Quality Assessment

Analyzes code quality using linters, complexity metrics, and pattern detection.

Author: Asif Hussain
Created: January 3, 2026
"""

import ast
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class QualityAssessmentPhase:
    """Phase 1: Assess code quality using multiple analyzers."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.target_path = orchestrator.target_path
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute quality assessment.
        
        Returns:
            Dictionary containing quality metrics and issues
        """
        logger.info("Phase 1: Starting code quality assessment")
        
        results = {
            "quality_score": 0,
            "issues": [],
            "metrics": {},
            "files_analyzed": 0
        }
        
        try:
            files = self._get_python_files()
            results["files_analyzed"] = len(files)
            
            for file_path in files:
                file_results = self._analyze_file(file_path)
                results["issues"].extend(file_results["issues"])
                
                # Aggregate metrics
                for key, value in file_results["metrics"].items():
                    if key not in results["metrics"]:
                        results["metrics"][key] = 0
                    results["metrics"][key] += value
            
            # Calculate overall quality score (0-100)
            results["quality_score"] = self._calculate_quality_score(results)
            
            logger.info(f"Quality assessment complete: Score {results['quality_score']}/100, "
                       f"{len(results['issues'])} issues found")
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _get_python_files(self) -> List[Path]:
        """Get list of Python files to analyze."""
        if self.target_path.is_file():
            return [self.target_path]
        
        python_files = list(self.target_path.rglob("*.py"))
        # Exclude test files, migrations, etc.
        excluded = ["__pycache__", ".venv", "venv", "migrations", ".git"]
        return [f for f in python_files if not any(ex in str(f) for ex in excluded)]
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file."""
        results = {
            "file": str(file_path),
            "issues": [],
            "metrics": {
                "lines_of_code": 0,
                "cyclomatic_complexity": 0,
                "cognitive_complexity": 0,
                "maintainability_index": 0
            }
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            results["metrics"]["lines_of_code"] = len(content.splitlines())
            
            # AST-based analysis
            try:
                tree = ast.parse(content)
                results["metrics"]["cyclomatic_complexity"] = self._calculate_complexity(tree)
                results["issues"].extend(self._detect_code_smells(tree, file_path))
            except SyntaxError as e:
                results["issues"].append({
                    "file": str(file_path),
                    "line": e.lineno,
                    "severity": "error",
                    "message": f"Syntax error: {e.msg}"
                })
            
            # Run pylint if available
            pylint_issues = self._run_pylint(file_path)
            results["issues"].extend(pylint_issues)
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
            results["error"] = str(e)
        
        return results
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _detect_code_smells(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Detect common code smells."""
        issues = []
        
        for node in ast.walk(tree):
            # Long functions
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'body') and len(node.body) > 50:
                    issues.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "severity": "warning",
                        "message": f"Function '{node.name}' is too long ({len(node.body)} statements)"
                    })
            
            # Too many parameters
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    issues.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "severity": "warning",
                        "message": f"Function '{node.name}' has too many parameters ({len(node.args.args)})"
                    })
            
            # Nested loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child != node and isinstance(child, (ast.For, ast.While)):
                        issues.append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "severity": "info",
                            "message": "Nested loops detected - consider refactoring"
                        })
                        break
        
        return issues
    
    def _run_pylint(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run pylint on file."""
        issues = []
        
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                import json
                pylint_output = json.loads(result.stdout)
                
                for issue in pylint_output:
                    issues.append({
                        "file": str(file_path),
                        "line": issue.get("line", 0),
                        "severity": issue.get("type", "convention"),
                        "message": issue.get("message", ""),
                        "symbol": issue.get("symbol", "")
                    })
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Pylint not available or failed
            pass
        except Exception as e:
            logger.debug(f"Pylint analysis failed for {file_path}: {e}")
        
        return issues
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall quality score (0-100)."""
        if results["files_analyzed"] == 0:
            return 0
        
        # Start with perfect score
        score = 100
        
        # Deduct points for issues
        issue_penalties = {
            "error": 10,
            "warning": 5,
            "convention": 2,
            "info": 1
        }
        
        for issue in results["issues"]:
            severity = issue.get("severity", "info")
            score -= issue_penalties.get(severity, 1)
        
        # Deduct for high complexity
        avg_complexity = results["metrics"].get("cyclomatic_complexity", 0) / max(results["files_analyzed"], 1)
        if avg_complexity > 10:
            score -= min(20, int(avg_complexity - 10))
        
        return max(0, min(100, score))
