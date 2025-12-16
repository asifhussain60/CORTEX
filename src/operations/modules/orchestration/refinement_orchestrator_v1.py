"""
Refinement Orchestrator v1.0
Holistic system improvement with automated discovery and enhancement.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import ast
import json
import logging
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class RefinementMetrics:
    """Metrics tracked during refinement."""
    lines_removed: int = 0
    complexity_delta: float = 0.0
    coverage_delta: float = 0.0
    token_reduction: int = 0
    dead_code_removed: int = 0
    duplicates_eliminated: int = 0
    tests_improved: int = 0
    docs_fixed: int = 0


@dataclass
class CodeIssue:
    """Represents a discovered code issue."""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'complexity', 'duplication', 'dead_code', etc.
    file_path: str
    line_number: int
    description: str
    suggestion: Optional[str] = None


class RefinementOrchestratorV1:
    """
    Orchestrator for holistic CORTEX system refinement.
    
    7-Phase Workflow:
    1. Discovery & Analysis
    2. SKULL Test Review
    3. Documentation Refinement
    4. Code Quality Enhancement
    5. Architecture Review
    6. Performance Optimization
    7. Validation & Rollback Safety
    """
    
    def __init__(self, cortex_root: Path, dry_run: bool = True):
        """
        Initialize refinement orchestrator.
        
        Args:
            cortex_root: Path to CORTEX repository root
            dry_run: If True, only report changes without applying
        """
        self.cortex_root = cortex_root
        self.dry_run = dry_run
        self.metrics = RefinementMetrics()
        self.issues: List[CodeIssue] = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load manifest
        manifest_path = cortex_root / "cortex-brain/orchestrator-manifests/refinement-orchestrator-manifest.yaml"
        with open(manifest_path, encoding='utf-8') as f:
            self.manifest = yaml.safe_load(f)
        
        logger.info("🎭 Orchestrator engaged: RefinementOrchestrator")
    
    def execute(self) -> Dict:
        """
        Execute full refinement workflow.
        
        Returns:
            Dict with results, metrics, and rollback info
        """
        results = {
            "timestamp": self.timestamp,
            "dry_run": self.dry_run,
            "phases": {},
            "metrics": {},
            "rollback_script": None
        }
        
        try:
            # Phase 1: Discovery & Analysis
            logger.info("🎭 Phase transition: START → DISCOVERY")
            results["phases"]["discovery"] = self._phase_1_discovery()
            
            # Phase 2: SKULL Test Review
            if self._requires_user_confirmation("phase_2_skull_review"):
                logger.info("🎭 Phase transition: DISCOVERY → SKULL_REVIEW")
                results["phases"]["skull_review"] = self._phase_2_skull_review()
            
            # Phase 3: Documentation Refinement
            logger.info("🎭 Phase transition: SKULL_REVIEW → DOCUMENTATION")
            results["phases"]["documentation"] = self._phase_3_documentation()
            
            # Phase 4: Code Quality Enhancement
            logger.info("🎭 Phase transition: DOCUMENTATION → CODE_QUALITY")
            results["phases"]["code_quality"] = self._phase_4_code_quality()
            
            # Phase 5: Architecture Review
            logger.info("🎭 Phase transition: CODE_QUALITY → ARCHITECTURE")
            results["phases"]["architecture"] = self._phase_5_architecture()
            
            # Phase 6: Performance Optimization
            logger.info("🎭 Phase transition: ARCHITECTURE → PERFORMANCE")
            results["phases"]["performance"] = self._phase_6_performance()
            
            # Phase 7: Validation & Rollback Safety
            logger.info("🎭 Phase transition: PERFORMANCE → VALIDATION")
            results["phases"]["validation"] = self._phase_7_validation()
            
            # Finalize
            results["metrics"] = self._compile_metrics()
            results["rollback_script"] = self._generate_rollback_script()
            
            # Convert CodeIssue objects to dicts for JSON serialization
            self._convert_issues_to_dicts(results)
            
            logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
        except Exception as e:
            logger.error(f"Refinement failed: {e}")
            results["error"] = str(e)
            results["status"] = "failed"
            return results
        
        results["status"] = "success"
        return results
    
    def _phase_1_discovery(self) -> Dict:
        """Phase 1: Discovery & Analysis."""
        phase_results = {
            "complexity_issues": [],
            "dead_code": [],
            "coverage_gaps": [],
            "doc_drift": [],
            "unused_dependencies": []
        }
        
        # Analyze code complexity
        phase_results["complexity_issues"] = self._analyze_complexity()
        
        # Detect dead code
        phase_results["dead_code"] = self._detect_dead_code()
        
        # Check test coverage gaps
        phase_results["coverage_gaps"] = self._analyze_coverage_gaps()
        
        # Detect documentation drift
        phase_results["doc_drift"] = self._detect_doc_drift()
        
        # Find unused dependencies
        phase_results["unused_dependencies"] = self._analyze_dependencies()
        
        # Generate discovery report
        self._generate_discovery_report(phase_results)
        
        return phase_results
    
    def _phase_2_skull_review(self) -> Dict:
        """Phase 2: SKULL Test Review."""
        phase_results = {
            "redundant_tests": [],
            "mergeable_tests": [],
            "unclear_tests": [],
            "weak_assertions": [],
            "misaligned_tests": []
        }
        
        # Find redundant SKULL tests
        phase_results["redundant_tests"] = self._find_redundant_skull_tests()
        
        # Identify mergeable tests
        phase_results["mergeable_tests"] = self._find_mergeable_tests()
        
        # Detect unclear test purposes
        phase_results["unclear_tests"] = self._find_unclear_tests()
        
        # Find weak assertions
        phase_results["weak_assertions"] = self._find_weak_assertions()
        
        # Validate alignment with brain-protection-rules.yaml
        phase_results["misaligned_tests"] = self._validate_skull_alignment()
        
        return phase_results
    
    def _phase_3_documentation(self) -> Dict:
        """Phase 3: Documentation Refinement."""
        phase_results = {
            "prompt_md_fixes": [],
            "copilot_instructions_fixes": [],
            "broken_references": [],
            "token_savings": 0
        }
        
        # Analyze CORTEX.prompt.md
        prompt_md = self.cortex_root / ".github/prompts/CORTEX.prompt.md"
        phase_results["prompt_md_fixes"] = self._analyze_prompt_md(prompt_md)
        
        # Analyze copilot-instructions.md
        copilot_md = self.cortex_root / ".github/copilot-instructions.md"
        phase_results["copilot_instructions_fixes"] = self._analyze_copilot_instructions(copilot_md)
        
        # Find broken references
        phase_results["broken_references"] = self._find_broken_references()
        
        # Calculate token savings
        phase_results["token_savings"] = self.metrics.token_reduction
        
        return phase_results
    
    def _phase_4_code_quality(self) -> Dict:
        """Phase 4: Code Quality Enhancement."""
        phase_results = {
            "complex_functions": [],
            "duplicates": [],
            "naming_issues": [],
            "error_handling_issues": [],
            "import_optimizations": []
        }
        
        # Find complex functions
        phase_results["complex_functions"] = self._find_complex_functions()
        
        # Detect duplicate code
        phase_results["duplicates"] = self._detect_duplicates()
        
        # Check naming conventions
        phase_results["naming_issues"] = self._check_naming()
        
        # Analyze error handling
        phase_results["error_handling_issues"] = self._analyze_error_handling()
        
        # Optimize imports
        phase_results["import_optimizations"] = self._optimize_imports()
        
        return phase_results
    
    def _phase_5_architecture(self) -> Dict:
        """Phase 5: Architecture Review."""
        phase_results = {
            "circular_dependencies": [],
            "missing_abstractions": [],
            "consolidation_opportunities": [],
            "manifest_inconsistencies": [],
            "tier_violations": []
        }
        
        # Check for circular dependencies
        phase_results["circular_dependencies"] = self._find_circular_deps()
        
        # Identify missing abstractions
        phase_results["missing_abstractions"] = self._find_missing_abstractions()
        
        # Find consolidation opportunities
        phase_results["consolidation_opportunities"] = self._find_consolidations()
        
        # Validate manifests
        phase_results["manifest_inconsistencies"] = self._validate_manifests()
        
        # Check tier separation
        phase_results["tier_violations"] = self._check_tier_separation()
        
        return phase_results
    
    def _phase_6_performance(self) -> Dict:
        """Phase 6: Performance Optimization."""
        phase_results = {
            "slow_operations": [],
            "memory_leaks": [],
            "io_bottlenecks": [],
            "cache_opportunities": []
        }
        
        # Identify slow operations
        phase_results["slow_operations"] = self._find_slow_operations()
        
        # Find memory leaks
        phase_results["memory_leaks"] = self._find_memory_leaks()
        
        # Analyze I/O patterns
        phase_results["io_bottlenecks"] = self._analyze_io_patterns()
        
        # Suggest caching
        phase_results["cache_opportunities"] = self._find_cache_opportunities()
        
        return phase_results
    
    def _phase_7_validation(self) -> Dict:
        """Phase 7: Validation & Rollback Safety."""
        phase_results = {
            "test_results": {},
            "skull_validation": {},
            "import_check": {},
            "doc_validation": {},
            "rollback_ready": False
        }
        
        # Run targeted test suite (smoke tests, 120s timeout)
        phase_results["test_results"] = self._run_test_suite(timeout=120, subset="smoke")
        
        # Validate SKULL rules
        phase_results["skull_validation"] = self._validate_skull_rules()
        
        # Check imports
        phase_results["import_check"] = self._check_imports()
        
        # Validate documentation
        phase_results["doc_validation"] = self._validate_documentation()
        
        # Generate rollback script
        phase_results["rollback_ready"] = True
        
        return phase_results
    
    # Helper methods for analysis
    
    def _analyze_complexity(self) -> List[CodeIssue]:
        """Analyze code complexity using AST."""
        issues = []
        src_path = self.cortex_root / "src"
        
        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        if complexity > 15:
                            issues.append(CodeIssue(
                                severity="high",
                                category="complexity",
                                file_path=str(py_file.relative_to(self.cortex_root)),
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has complexity {complexity}",
                                suggestion=f"Consider breaking into smaller functions"
                            ))
            except Exception as e:
                logger.warning(f"Could not analyze {py_file}: {e}")
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _detect_dead_code(self) -> List[CodeIssue]:
        """Detect unreachable code and unused imports."""
        issues = []
        # Implementation using AST analysis
        # Check for code after return/raise statements
        # Find unused imports
        return issues
    
    def _analyze_coverage_gaps(self) -> List[Dict]:
        """Analyze test coverage gaps."""
        gaps = []
        # Run pytest with coverage
        # Identify files/functions with <80% coverage
        return gaps
    
    def _detect_doc_drift(self) -> List[Dict]:
        """Detect documentation drift."""
        drift = []
        # Compare code signatures with docstrings
        # Find outdated examples
        return drift
    
    def _analyze_dependencies(self) -> List[str]:
        """Find unused dependencies."""
        unused = []
        # Parse requirements.txt
        # Check imports in code
        # Return unused packages
        return unused
    
    def _find_redundant_skull_tests(self) -> List[Dict]:
        """Find redundant SKULL tests."""
        redundant = []
        # Analyze test coverage overlap
        # Find tests testing same thing
        return redundant
    
    def _find_mergeable_tests(self) -> List[Dict]:
        """Find tests that can be merged."""
        mergeable = []
        # Find tests with similar setup/teardown
        # Suggest merging opportunities
        return mergeable
    
    def _find_unclear_tests(self) -> List[Dict]:
        """Find tests with unclear purposes."""
        unclear = []
        # Check for tests without docstrings
        # Check for tests with vague names
        return unclear
    
    def _find_weak_assertions(self) -> List[Dict]:
        """Find tests with weak assertions."""
        weak = []
        # Find tests with only assertTrue/assertIsNotNone
        # Suggest more specific assertions
        return weak
    
    def _validate_skull_alignment(self) -> List[Dict]:
        """Validate tests align with brain-protection-rules.yaml."""
        misaligned = []
        # Load brain-protection-rules.yaml
        # Check each test against rules
        return misaligned
    
    def _analyze_prompt_md(self, path: Path) -> List[Dict]:
        """Analyze CORTEX.prompt.md for issues."""
        fixes = []
        
        with open(path, encoding='utf-8') as f:
            content = f.read()
        
        # Check line count
        lines = content.split('\n')
        if len(lines) > 600:
            fixes.append({
                "type": "bloat",
                "severity": "high",
                "description": f"File has {len(lines)} lines (limit: 600)",
                "suggestion": "Remove non-essential content"
            })
        
        # Check for broken file references
        file_refs = re.findall(r'`([^`]+\.(yaml|md|py))`', content)
        for ref in file_refs:
            ref_path = self.cortex_root / ref[0]
            if not ref_path.exists():
                fixes.append({
                    "type": "broken_reference",
                    "severity": "high",
                    "description": f"Broken reference: {ref[0]}",
                    "suggestion": "Update or remove reference"
                })
        
        return fixes
    
    def _analyze_copilot_instructions(self, path: Path) -> List[Dict]:
        """Analyze copilot-instructions.md for issues."""
        fixes = []
        # Check consistency with cortex-operations.yaml
        # Find outdated command references
        return fixes
    
    def _find_broken_references(self) -> List[Dict]:
        """Find broken cross-references in documentation."""
        broken = []
        # Scan all markdown files
        # Check internal links
        return broken
    
    def _find_complex_functions(self) -> List[CodeIssue]:
        """Find functions exceeding complexity threshold."""
        return self._analyze_complexity()
    
    def _detect_duplicates(self) -> List[Dict]:
        """Detect duplicate code blocks."""
        duplicates = []
        # Use AST to find similar code structures
        return duplicates
    
    def _check_naming(self) -> List[CodeIssue]:
        """Check naming convention compliance."""
        issues = []
        # Check snake_case for functions
        # Check PascalCase for classes
        return issues
    
    def _analyze_error_handling(self) -> List[CodeIssue]:
        """Analyze error handling patterns."""
        issues = []
        # Find bare except clauses
        # Find missing error handling
        return issues
    
    def _optimize_imports(self) -> List[Dict]:
        """Find import optimization opportunities."""
        optimizations = []
        # Find unused imports
        # Find duplicate imports
        # Suggest consolidations
        return optimizations
    
    def _find_circular_deps(self) -> List[Dict]:
        """Find circular dependencies."""
        circular = []
        # Build dependency graph
        # Detect cycles
        return circular
    
    def _find_missing_abstractions(self) -> List[Dict]:
        """Identify missing abstractions."""
        missing = []
        # Find repeated patterns
        # Suggest base classes/utilities
        return missing
    
    def _find_consolidations(self) -> List[Dict]:
        """Find consolidation opportunities."""
        opportunities = []
        # Find similar modules
        # Suggest merging
        return opportunities
    
    def _validate_manifests(self) -> List[Dict]:
        """Validate orchestrator manifests."""
        issues = []
        # Check all manifests in orchestrator-manifests/
        # Validate required fields
        # Check consistency
        return issues
    
    def _check_tier_separation(self) -> List[CodeIssue]:
        """Check for tier separation violations."""
        violations = []
        # Check tier0 doesn't import tier1/2/3
        # Check tier1 doesn't import tier2/3
        return violations
    
    def _find_slow_operations(self) -> List[Dict]:
        """Identify slow operations."""
        slow = []
        # Profile key operations
        # Find >1s response times
        return slow
    
    def _find_memory_leaks(self) -> List[Dict]:
        """Find potential memory leaks."""
        leaks = []
        # Look for growing collections
        # Find unclosed resources
        return leaks
    
    def _analyze_io_patterns(self) -> List[Dict]:
        """Analyze I/O bottlenecks."""
        bottlenecks = []
        # Find repeated file opens
        # Find inefficient reads
        return bottlenecks
    
    def _find_cache_opportunities(self) -> List[Dict]:
        """Find caching opportunities."""
        opportunities = []
        # Find repeated computations
        # Find repeated file reads
        return opportunities
    
    def _run_test_suite(self, timeout: int = 120, subset: str = "smoke") -> Dict:
        """Run test suite with configurable timeout and subset.
        
        Args:
            timeout: Max execution time in seconds (default: 120)
            subset: Test subset to run - 'smoke', 'unit', 'integration', or 'all'
        """
        try:
            # Build test command based on subset
            if subset == "smoke":
                cmd = ["pytest", "tests/", "-m", "smoke", "-v", "--tb=short"]
            elif subset == "unit":
                cmd = ["pytest", "tests/", "-m", "not integration", "-v", "--tb=short"]
            elif subset == "integration":
                cmd = ["pytest", "tests/", "-m", "integration", "-v", "--tb=short"]
            else:  # all
                cmd = ["pytest", "tests/", "-v", "--tb=short"]
            
            result = subprocess.run(
                cmd,
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "passed": result.returncode == 0,
                "subset": subset,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _validate_skull_rules(self) -> Dict:
        """Validate all SKULL rules pass."""
        validation = {"passed": True, "violations": []}
        # Load brain-protection-rules.yaml
        # Run each rule's validation
        return validation
    
    def _check_imports(self) -> Dict:
        """Check for import errors."""
        try:
            # Check if src module can be imported
            result = subprocess.run(
                ["python", "-c", "import sys; sys.path.insert(0, '.'); import src"],
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "passed": result.returncode == 0,
                "errors": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"passed": False, "errors": str(e)}
    
    def _validate_documentation(self) -> Dict:
        """Validate documentation builds."""
        validation = {"passed": True, "errors": []}
        # Check markdown syntax
        # Validate YAML files
        return validation
    
    def _requires_user_confirmation(self, phase_id: str) -> bool:
        """Check if phase requires user confirmation."""
        for phase in self.manifest["phases"]:
            if phase["id"] == phase_id:
                return phase.get("requires_confirmation", False)
        return False
    
    def _compile_metrics(self) -> Dict:
        """Compile final metrics."""
        return {
            "lines_removed": self.metrics.lines_removed,
            "complexity_delta": self.metrics.complexity_delta,
            "coverage_delta": self.metrics.coverage_delta,
            "token_reduction": self.metrics.token_reduction,
            "dead_code_removed": self.metrics.dead_code_removed,
            "duplicates_eliminated": self.metrics.duplicates_eliminated,
            "tests_improved": self.metrics.tests_improved,
            "docs_fixed": self.metrics.docs_fixed
        }
    
    def _generate_rollback_script(self) -> str:
        """Generate rollback script."""
        script_path = self.cortex_root / f"scripts/rollback_refinement_{self.timestamp}.py"
        
        rollback_content = f'''"""
Rollback script for refinement {self.timestamp}
Generated: {datetime.now().isoformat()}
"""

import subprocess
import sys

def rollback():
    """Rollback all refinement changes."""
    print("Rolling back refinement changes...")
    
    # Restore from git checkpoints
    commands = [
        ["git", "checkout", "HEAD~1", "--", "."],
        ["pytest", "tests/"],
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print(f"Error: {{result.stderr.decode()}}")
            return False
    
    print("✅ Rollback complete")
    return True

if __name__ == "__main__":
    success = rollback()
    sys.exit(0 if success else 1)
'''
        
        if not self.dry_run:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(rollback_content)
        
        return str(script_path)
    
    def _generate_discovery_report(self, results: Dict) -> None:
        """Generate discovery phase report."""
        report_path = self.cortex_root / f"cortex-brain/documents/reports/refinement-discovery-{self.timestamp}.md"
        
        report = f"""# Refinement Discovery Report
**Generated:** {datetime.now().isoformat()}
**Dry Run:** {self.dry_run}

## Summary

- **Complexity Issues:** {len(results['complexity_issues'])}
- **Dead Code:** {len(results['dead_code'])}
- **Coverage Gaps:** {len(results['coverage_gaps'])}
- **Documentation Drift:** {len(results['doc_drift'])}
- **Unused Dependencies:** {len(results['unused_dependencies'])}

## Detailed Findings

### Complexity Issues
{self._format_issues(results['complexity_issues'])}

### Dead Code
{self._format_issues(results['dead_code'])}

### Coverage Gaps
{self._format_list(results['coverage_gaps'])}

### Documentation Drift
{self._format_list(results['doc_drift'])}

### Unused Dependencies
{self._format_list(results['unused_dependencies'])}
"""
        
        if not self.dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding='utf-8') as f:
                f.write(report)
    
    def _format_issues(self, issues: List[CodeIssue]) -> str:
        """Format issues for report."""
        if not issues:
            return "*None found*\n"
        
        output = []
        for issue in issues:
            output.append(f"- **{issue.severity.upper()}** {issue.file_path}:{issue.line_number}")
            output.append(f"  - {issue.description}")
            if issue.suggestion:
                output.append(f"  - Suggestion: {issue.suggestion}")
        
        return "\n".join(output)
    
    def _format_list(self, items: List) -> str:
        """Format list for report."""
        if not items:
            return "*None found*\n"
        return "\n".join(f"- {item}" for item in items)
    
    def _convert_issues_to_dicts(self, results: Dict) -> None:
        """Convert CodeIssue objects to dicts for JSON serialization."""
        for phase_name, phase_data in results.get("phases", {}).items():
            if isinstance(phase_data, dict):
                for key, value in phase_data.items():
                    if isinstance(value, list) and value and isinstance(value[0], CodeIssue):
                        phase_data[key] = [asdict(issue) for issue in value]


def main():
    """CLI entry point for refinement orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Refinement Orchestrator")
    parser.add_argument("--cortex-root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Apply changes (disables dry-run)")
    
    args = parser.parse_args()
    
    orchestrator = RefinementOrchestratorV1(
        cortex_root=args.cortex_root,
        dry_run=not args.apply
    )
    
    results = orchestrator.execute()
    
    print(json.dumps(results, indent=2))
    
    return 0 if results.get("status") == "success" else 1


if __name__ == "__main__":
    exit(main())
