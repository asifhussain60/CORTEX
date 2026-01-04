"""
Phase -2: Setup Verification Module (CORTEX v5 Universal Pattern)

This middleware runs BEFORE any orchestrator execution to verify:
1. Dependencies are ACTUALLY complete (not just file existence)
2. False positive detection (files exist but broken)
3. VSCode cache state check
4. Governance compliance validation

Author: CORTEX v5
Date: January 4, 2026
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DependencyValidation:
    """Result of dependency validation."""
    
    dependency_id: str
    exists: bool
    functional: bool  # NEW: Not just existence, but functionality
    false_positive: bool
    error_message: Optional[str] = None


@dataclass
class CacheCheckResult:
    """Result of VSCode cache check."""
    
    cache_exists: bool
    cache_age_days: int
    should_clear: bool
    brittle_indicators: List[str]


@dataclass
class SetupVerificationResult:
    """Complete setup verification result."""
    
    passed: bool
    dependencies_validated: List[DependencyValidation]
    cache_check: CacheCheckResult
    governance_compliant: bool
    errors: List[str]
    timestamp: str


class SetupVerifier:
    """
    Phase -2: Setup Verification Middleware
    
    Universal CORTEX v5 pattern - runs before ALL orchestrator executions.
    """
    
    def __init__(
        self,
        workspace_root: Path,
        brain_rules_path: Optional[Path] = None,
    ):
        self.workspace_root = Path(workspace_root)
        self.brain_rules_path = brain_rules_path or self.workspace_root / "cortex-brain" / "brain-protection-rules.yaml"
    
    def verify_setup(
        self,
        orchestrator_name: str,
        dependencies: List[str],
        cache_check_enabled: bool = True,
    ) -> SetupVerificationResult:
        """
        Run complete setup verification.
        
        Args:
            orchestrator_name: Name of orchestrator being executed
            dependencies: List of dependency IDs to validate
            cache_check_enabled: Whether to check VSCode cache state
        
        Returns:
            SetupVerificationResult with validation details
        """
        logger.info(f"Phase -2: Setup Verification for {orchestrator_name}")
        
        errors = []
        
        # Step 1: Validate dependencies (implementation test, not just file check)
        dependency_results = self._validate_dependencies_implementation(dependencies)
        
        # Step 2: Detect false positives
        false_positives = self._detect_false_positives(dependency_results)
        if false_positives:
            errors.extend([f"False positive detected: {fp}" for fp in false_positives])
        
        # Step 3: Check VSCode cache state
        cache_check = None
        if cache_check_enabled:
            cache_check = self._check_vscode_cache_state()
            if cache_check.should_clear:
                logger.warning(f"VSCode cache should be cleared: {cache_check.brittle_indicators}")
        
        # Step 4: Validate governance compliance
        governance_compliant = self._validate_governance_compliance(orchestrator_name)
        if not governance_compliant:
            errors.append("Governance compliance check failed")
        
        # Determine if setup verification passed
        passed = (
            all(dep.functional and not dep.false_positive for dep in dependency_results)
            and governance_compliant
            and len(errors) == 0
        )
        
        result = SetupVerificationResult(
            passed=passed,
            dependencies_validated=dependency_results,
            cache_check=cache_check,
            governance_compliant=governance_compliant,
            errors=errors,
            timestamp=datetime.now().isoformat(),
        )
        
        # Log result
        if passed:
            logger.info(f"✅ Setup verification PASSED for {orchestrator_name}")
        else:
            logger.error(f"❌ Setup verification FAILED for {orchestrator_name}: {errors}")
        
        return result
    
    def _validate_dependencies_implementation(
        self, dependencies: List[str]
    ) -> List[DependencyValidation]:
        """
        Validate dependencies with IMPLEMENTATION tests, not just file checks.
        
        This is the KEY difference from traditional dependency validation:
        - OLD: Check if file exists
        - NEW: Check if file exists AND is functional (import test, execution test)
        """
        results = []
        
        for dep_id in dependencies:
            logger.debug(f"Validating dependency: {dep_id}")
            
            # Check file existence
            dep_path = self._resolve_dependency_path(dep_id)
            exists = dep_path.exists() if dep_path else False
            
            # NEW: Implementation test
            functional = False
            false_positive = False
            error_message = None
            
            if exists:
                # Try to import/execute to verify functionality
                functional, error_message = self._test_dependency_functionality(dep_path)
                false_positive = exists and not functional
            
            results.append(
                DependencyValidation(
                    dependency_id=dep_id,
                    exists=exists,
                    functional=functional,
                    false_positive=false_positive,
                    error_message=error_message,
                )
            )
        
        return results
    
    def _resolve_dependency_path(self, dep_id: str) -> Optional[Path]:
        """Resolve dependency ID to file path."""
        # Common patterns
        if dep_id.endswith(".py"):
            return self.workspace_root / "src" / dep_id
        elif dep_id.startswith("C50-"):
            return self.workspace_root / "cortex-brain" / "documents" / "planning" / "active" / "C50-cortex-v5-remediation" / dep_id
        else:
            # Try direct path
            return self.workspace_root / dep_id
    
    def _test_dependency_functionality(self, dep_path: Path) -> tuple[bool, Optional[str]]:
        """
        Test if dependency is FUNCTIONAL, not just present.
        
        Returns:
            (functional, error_message)
        """
        if not dep_path.exists():
            return False, "File does not exist"
        
        # Python file: try import test
        if dep_path.suffix == ".py":
            return self._test_python_import(dep_path)
        
        # JSON/YAML: try parse test
        elif dep_path.suffix in [".json", ".yaml", ".yml"]:
            return self._test_file_parse(dep_path)
        
        # Markdown: basic syntax check
        elif dep_path.suffix == ".md":
            return self._test_markdown_syntax(dep_path)
        
        # Default: file exists = functional
        else:
            return True, None
    
    def _test_python_import(self, py_file: Path) -> tuple[bool, Optional[str]]:
        """Test if Python file can be imported without errors."""
        try:
            # Run: python -c "import module"
            module_path = str(py_file.relative_to(self.workspace_root))
            module_name = module_path.replace("/", ".").replace(".py", "")
            
            result = subprocess.run(
                ["python", "-c", f"import {module_name}"],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, f"Import failed: {result.stderr[:200]}"
        
        except subprocess.TimeoutExpired:
            return False, "Import test timed out"
        except Exception as e:
            return False, f"Import test error: {str(e)}"
    
    def _test_file_parse(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Test if JSON/YAML file can be parsed."""
        try:
            content = file_path.read_text()
            
            if file_path.suffix == ".json":
                json.loads(content)
            elif file_path.suffix in [".yaml", ".yml"]:
                import yaml
                yaml.safe_load(content)
            
            return True, None
        
        except json.JSONDecodeError as e:
            return False, f"JSON parse error: {str(e)}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    def _test_markdown_syntax(self, md_file: Path) -> tuple[bool, Optional[str]]:
        """Basic markdown syntax check."""
        try:
            content = md_file.read_text()
            
            # Check for common syntax errors
            if content.count("```") % 2 != 0:
                return False, "Unclosed code block"
            
            return True, None
        
        except Exception as e:
            return False, f"Markdown check error: {str(e)}"
    
    def _detect_false_positives(
        self, dependency_results: List[DependencyValidation]
    ) -> List[str]:
        """
        Detect false positives (files exist but broken).
        
        Returns:
            List of false positive dependency IDs
        """
        return [
            dep.dependency_id
            for dep in dependency_results
            if dep.false_positive
        ]
    
    def _check_vscode_cache_state(self) -> CacheCheckResult:
        """
        Check VSCode cache state and determine if clearing is needed.
        """
        cache_dir = self.workspace_root / ".vscode" / "cache"
        
        if not cache_dir.exists():
            return CacheCheckResult(
                cache_exists=False,
                cache_age_days=0,
                should_clear=False,
                brittle_indicators=[],
            )
        
        # Check cache age
        cache_mtime = datetime.fromtimestamp(cache_dir.stat().st_mtime)
        cache_age_days = (datetime.now() - cache_mtime).days
        
        # Check for brittleness indicators
        brittle_indicators = []
        
        # Indicator 1: Cache older than 30 days
        if cache_age_days > 30:
            brittle_indicators.append("Cache older than 30 days")
        
        # Indicator 2: Large cache size (>100MB)
        cache_size_mb = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()) / (1024 * 1024)
        if cache_size_mb > 100:
            brittle_indicators.append(f"Cache size {cache_size_mb:.1f}MB > 100MB")
        
        # Indicator 3: Test failures in recent runs
        test_failure_log = self.workspace_root / "logs" / "test-failures.log"
        if test_failure_log.exists():
            brittle_indicators.append("Test failures detected in logs")
        
        should_clear = len(brittle_indicators) > 0
        
        return CacheCheckResult(
            cache_exists=True,
            cache_age_days=cache_age_days,
            should_clear=should_clear,
            brittle_indicators=brittle_indicators,
        )
    
    def _validate_governance_compliance(self, orchestrator_name: str) -> bool:
        """
        Validate governance compliance (SKULL rules).
        
        This is a basic check - full governance validation happens at runtime
        via governance_checkpoint.py middleware.
        """
        if not self.brain_rules_path.exists():
            logger.warning(f"Brain protection rules not found: {self.brain_rules_path}")
            return True  # Don't block if rules file missing
        
        # Basic validation: check if orchestrator follows naming conventions
        valid_prefixes = ["planning_", "ado_", "vacuum_", "cleanup_", "sanitization_", "tdd_", "debug_", "refinement_"]
        
        if not any(orchestrator_name.startswith(prefix) for prefix in valid_prefixes):
            logger.warning(f"Orchestrator name doesn't follow conventions: {orchestrator_name}")
            return False
        
        return True
    
    def save_report(self, result: SetupVerificationResult, output_path: Path):
        """Save setup verification report to markdown."""
        report = f"""# Phase -2: Setup Verification Report

**Timestamp:** {result.timestamp}  
**Overall Status:** {"✅ PASSED" if result.passed else "❌ FAILED"}

---

## Dependency Validation

| Dependency | Exists | Functional | False Positive | Error |
|------------|--------|------------|----------------|-------|
"""
        
        for dep in result.dependencies_validated:
            status_exists = "✅" if dep.exists else "❌"
            status_functional = "✅" if dep.functional else "❌"
            status_fp = "🚨" if dep.false_positive else "—"
            error_msg = dep.error_message or "—"
            
            report += f"| {dep.dependency_id} | {status_exists} | {status_functional} | {status_fp} | {error_msg[:50]} |\n"
        
        report += f"""
---

## VSCode Cache Check

"""
        
        if result.cache_check:
            cache = result.cache_check
            report += f"""- **Cache Exists:** {"Yes" if cache.cache_exists else "No"}
- **Cache Age:** {cache.cache_age_days} days
- **Should Clear:** {"⚠️ YES" if cache.should_clear else "No"}
- **Brittleness Indicators:**
"""
            for indicator in cache.brittle_indicators:
                report += f"  - {indicator}\n"
        else:
            report += "Cache check disabled.\n"
        
        report += f"""
---

## Governance Compliance

**Status:** {"✅ COMPLIANT" if result.governance_compliant else "❌ NON-COMPLIANT"}

---

## Errors

"""
        
        if result.errors:
            for error in result.errors:
                report += f"- ❌ {error}\n"
        else:
            report += "No errors detected.\n"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        logger.info(f"Setup verification report saved to {output_path}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    verifier = SetupVerifier(workspace_root=Path("."))
    
    result = verifier.verify_setup(
        orchestrator_name="planning_v5",
        dependencies=["src/orchestrators/planning/planning_orchestrator_v5.py", "C50-00A"],
        cache_check_enabled=True,
    )
    
    print(f"Setup verification: {'PASSED' if result.passed else 'FAILED'}")
    print(f"Dependencies validated: {len(result.dependencies_validated)}")
    print(f"Errors: {result.errors}")
    
    # Save report
    verifier.save_report(result, Path("cortex-brain/documents/planning/active/test/analysis/setup-verification-report.md"))
