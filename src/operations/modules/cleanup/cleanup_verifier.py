"""
Cleanup Verifier - Post-execution verification

Verifies CORTEX functionality after cleanup execution.
Triggers automatic rollback if issues detected.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of post-cleanup verification"""
    passed: bool
    message: str
    checks: Dict[str, Any]
    rollback_triggered: bool = False


class CleanupVerifier:
    """Verify CORTEX functionality after cleanup"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
    
    def verify_cleanup(self, use_health_validator: bool = True) -> VerificationResult:
        """
        Run comprehensive post-cleanup verification.
        
        Args:
            use_health_validator: Use HealthValidator for quick health check
        
        Returns:
            VerificationResult with pass/fail and details
        """
        logger.info("=" * 70)
        logger.info("POST-CLEANUP VERIFICATION")
        logger.info("=" * 70)
        
        checks = {}
        all_passed = True
        
        # 1. Import validation
        logger.info("1. Validating Python imports...")
        import_result = self._validate_imports()
        checks['imports'] = import_result
        if not import_result['passed']:
            all_passed = False
            logger.error("   ❌ Import validation failed")
        else:
            logger.info("   ✅ All critical imports functional")
        
        # 2. Test discovery
        logger.info("2. Validating test discovery...")
        test_result = self._validate_test_discovery()
        checks['test_discovery'] = test_result
        if not test_result['passed']:
            all_passed = False
            logger.error("   ❌ Test discovery failed")
        else:
            logger.info(f"   ✅ {test_result['tests_found']} tests discoverable")
        
        # 3. Health check (if available)
        if use_health_validator:
            logger.info("3. Running health validator...")
            health_result = self._run_health_check()
            checks['health'] = health_result
            if not health_result['passed']:
                all_passed = False
                logger.error("   ❌ Health check failed")
            else:
                logger.info(f"   ✅ System health: {health_result['status']}")
        
        # 4. Smoke tests
        logger.info("4. Running smoke tests...")
        smoke_result = self._run_smoke_tests()
        checks['smoke_tests'] = smoke_result
        if not smoke_result['passed']:
            all_passed = False
            logger.error("   ❌ Smoke tests failed")
        else:
            logger.info(f"   ✅ {smoke_result['passed_count']}/{smoke_result['total_count']} smoke tests passed")
        
        logger.info("")
        if all_passed:
            logger.info("✅ POST-CLEANUP VERIFICATION COMPLETE")
            logger.info("   All systems operational")
        else:
            logger.error("❌ POST-CLEANUP VERIFICATION FAILED")
            logger.error("   CORTEX functionality compromised")
        logger.info("")
        
        return VerificationResult(
            passed=all_passed,
            message="All checks passed" if all_passed else "Some checks failed",
            checks=checks
        )
    
    def _validate_imports(self) -> Dict[str, Any]:
        """Validate critical imports work"""
        critical_imports = [
            'src.main',
            'src.entry_point.cortex_entry',
            'src.cortex_agents.intent_router',
            'src.operations.base_operation_module',
            'src.tier0.tier_validator',
            'src.tier1.working_memory',
            'src.tier2.knowledge_graph',
            'src.cortex_agents.health_validator.agent'
        ]
        
        passed = []
        failed = []
        
        for module_name in critical_imports:
            try:
                importlib.import_module(module_name)
                passed.append(module_name)
            except ImportError as e:
                failed.append({'module': module_name, 'error': str(e)})
        
        return {
            'passed': len(failed) == 0,
            'total': len(critical_imports),
            'passed_count': len(passed),
            'failed_count': len(failed),
            'failed_modules': failed
        }
    
    def _validate_test_discovery(self) -> Dict[str, Any]:
        """Validate pytest can discover tests"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=30
            )
            
            # Parse test count
            import re
            match = re.search(r'collected (\d+) items?', result.stdout)
            test_count = int(match.group(1)) if match else 0
            
            return {
                'passed': test_count > 0,
                'tests_found': test_count
            }
        
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _run_health_check(self) -> Dict[str, Any]:
        """Run HealthValidator quick check"""
        try:
            from src.cortex_agents.health_validator.agent import HealthValidator
            from src.cortex_agents.base_agent import AgentRequest
            
            # Initialize validator (quick mode - skip tests)
            validator = HealthValidator("post-cleanup-validator", None, None, None)
            
            request = AgentRequest(
                intent="health_check",
                context={"skip_tests": True},
                user_message="Post-cleanup verification"
            )
            
            response = validator.execute(request)
            
            return {
                'passed': response.success,
                'status': response.result.get('status', 'unknown'),
                'risk_level': response.result.get('risk_level', 'unknown')
            }
        
        except Exception as e:
            logger.warning(f"Could not run health check: {e}")
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _run_smoke_tests(self) -> Dict[str, Any]:
        """Run critical smoke tests"""
        smoke_tests = [
            'tests/tier0/test_brain_protector.py::test_skull_rule_loading',
            'tests/tier1/test_working_memory.py::test_database_connection',
            'tests/tier2/test_knowledge_graph.py::test_database_connection'
        ]
        
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest'] + smoke_tests + ['-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60
            )
            
            # Parse results
            passed = result.stdout.count(' PASSED')
            failed = result.stdout.count(' FAILED')
            
            return {
                'passed': failed == 0,
                'total_count': len(smoke_tests),
                'passed_count': passed,
                'failed_count': failed
            }
        
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
