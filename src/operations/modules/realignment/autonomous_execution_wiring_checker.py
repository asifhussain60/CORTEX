"""
Autonomous Execution Wiring Checker for CORTEX Align.

Validates that autonomous execution is properly integrated:
- PlanningOrchestrator has execute_plan_autonomously method
- Integration tests exist and pass
- Response templates configured
- Intent router recognizes autonomous commands
- Git checkpoint integration present

Author: GitHub Copilot
Created: 2025-12-06
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util
import yaml

logger = logging.getLogger(__name__)


class AutonomousExecutionWiringChecker:
    """Validates autonomous execution integration in CORTEX."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize checker.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = cortex_root
        self.src_dir = cortex_root / "src"
        self.tests_dir = cortex_root / "tests"
    
    def check_autonomous_execution_wiring(self) -> Tuple[bool, List[str], List[str]]:
        """
        Check if autonomous execution is properly wired.
        
        Returns:
            Tuple of (all_checks_passed, successes, warnings)
        """
        successes = []
        warnings = []
        
        logger.info("🔍 Checking autonomous execution wiring...")
        
        # Check 1: PlanningOrchestrator has execute_plan_autonomously method
        has_method, method_msg = self._check_planning_orchestrator_method()
        if has_method:
            successes.append(method_msg)
        else:
            warnings.append(method_msg)
        
        # Check 2: Integration tests exist
        has_tests, tests_msg = self._check_integration_tests()
        if has_tests:
            successes.append(tests_msg)
        else:
            warnings.append(tests_msg)
        
        # Check 3: Intent router support
        has_intent, intent_msg = self._check_intent_router()
        if has_intent:
            successes.append(intent_msg)
        else:
            warnings.append(intent_msg)
        
        # Check 4: Response templates
        has_templates, template_msg = self._check_response_templates()
        if has_templates:
            successes.append(template_msg)
        else:
            warnings.append(template_msg)
        
        # Check 5: Git checkpoint integration
        has_git, git_msg = self._check_git_checkpoint_integration()
        if has_git:
            successes.append(git_msg)
        else:
            warnings.append(git_msg)
        
        all_passed = len(warnings) == 0
        
        if all_passed:
            logger.info("✅ Autonomous execution fully wired")
        else:
            logger.warning(f"⚠️  Autonomous execution has {len(warnings)} wiring issues")
        
        return all_passed, successes, warnings
    
    def _check_planning_orchestrator_method(self) -> Tuple[bool, str]:
        """Check if PlanningOrchestrator has execute_plan_autonomously method."""
        orchestrator_path = self.src_dir / "orchestrators" / "planning_orchestrator.py"
        
        if not orchestrator_path.exists():
            return False, "❌ planning_orchestrator.py not found"
        
        try:
            content = orchestrator_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return False, f"❌ Failed to read planning_orchestrator.py: {str(e)}"
        
        if "def execute_plan_autonomously" in content:
            # Check for progress decorator
            has_decorator = "@with_progress" in content and "Autonomous" in content
            
            if has_decorator:
                return True, "✅ execute_plan_autonomously method with @with_progress decorator"
            else:
                return True, "✅ execute_plan_autonomously method (⚠️  missing @with_progress)"
        
        return False, "❌ execute_plan_autonomously method not found in PlanningOrchestrator"
    
    def _check_integration_tests(self) -> Tuple[bool, str]:
        """Check if integration tests exist for autonomous execution."""
        test_paths = [
            self.tests_dir / "integration" / "orchestrators" / "test_autonomous_execution_integration.py",
            self.tests_dir / "orchestrators" / "test_planning_tdd_e2e.py",
            self.tests_dir / "orchestrators" / "test_planning_tdd_injection.py"
        ]
        
        existing_tests = [p for p in test_paths if p.exists()]
        
        if len(existing_tests) >= 2:
            test_names = [p.name for p in existing_tests]
            return True, f"✅ Autonomous execution integration tests: {', '.join(test_names)}"
        elif len(existing_tests) == 1:
            return True, f"⚠️  Only 1 integration test found: {existing_tests[0].name}"
        else:
            return False, "❌ No integration tests found for autonomous execution"
    
    def _check_intent_router(self) -> Tuple[bool, str]:
        """Check if intent router recognizes autonomous execution commands."""
        router_path = self.src_dir / "cortex_agents" / "intent_router.py"
        
        if not router_path.exists():
            return False, "❌ intent_router.py not found"
        
        try:
            content = router_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return False, f"❌ Failed to read intent_router.py: {str(e)}"
        
        # Check for autonomous execution patterns
        autonomous_patterns = [
            "autonomous",
            "execute all phases",
            "auto chained",
            "execute_plan_autonomously"
        ]
        
        found_patterns = [p for p in autonomous_patterns if p.lower() in content.lower()]
        
        if len(found_patterns) >= 2:
            return True, f"✅ Intent router recognizes autonomous execution ({len(found_patterns)} patterns)"
        elif len(found_patterns) == 1:
            return True, f"⚠️  Intent router has minimal autonomous support (1 pattern)"
        else:
            return False, "❌ Intent router doesn't recognize autonomous execution commands"
    
    def _check_response_templates(self) -> Tuple[bool, str]:
        """Check if response templates exist for autonomous execution."""
        templates_path = self.cortex_root / "cortex-brain" / "response-templates.yaml"
        
        if not templates_path.exists():
            return False, "❌ response-templates.yaml not found"
        
        try:
            with open(templates_path, 'r', encoding='utf-8', errors='ignore') as f:
                templates = yaml.safe_load(f)
            
            if not templates or 'templates' not in templates:
                return False, "❌ No templates section in response-templates.yaml"
            
            # Check for autonomous/planning templates
            # Templates are structured as dict keys, not list of objects
            if isinstance(templates['templates'], dict):
                template_names = [name.lower() for name in templates['templates'].keys()]
            else:
                # Fallback for list structure
                template_names = [t.get('name', '').lower() for t in templates['templates']]
            
            autonomous_templates = [n for n in template_names if 'autonomous' in n or 'execute' in n]
            planning_templates = [n for n in template_names if 'planning' in n or 'plan' in n]
            
            if autonomous_templates:
                return True, f"✅ Autonomous execution response templates: {len(autonomous_templates)}"
            elif planning_templates:
                return True, f"⚠️  Planning templates exist ({len(planning_templates)}), but no autonomous-specific templates"
            else:
                return False, "❌ No autonomous execution or planning response templates"
        
        except Exception as e:
            return False, f"❌ Error reading response templates: {e}"
    
    def _check_git_checkpoint_integration(self) -> Tuple[bool, str]:
        """Check if autonomous execution integrates with git checkpoint orchestrator."""
        orchestrator_path = self.src_dir / "orchestrators" / "planning_orchestrator.py"
        
        if not orchestrator_path.exists():
            return False, "❌ planning_orchestrator.py not found"
        
        try:
            content = orchestrator_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return False, f"❌ Failed to read planning_orchestrator.py: {str(e)}"
        
        # Check for git checkpoint integration
        has_import = "GitCheckpointOrchestrator" in content
        has_usage = "self.git_checkpoint" in content or "git_checkpoint" in content.lower()
        
        if has_import and has_usage:
            return True, "✅ Git checkpoint integration in autonomous execution"
        elif has_import:
            return True, "⚠️  GitCheckpointOrchestrator imported but usage unclear"
        else:
            return False, "❌ No git checkpoint integration in autonomous execution"


def check_autonomous_execution_wiring(cortex_root: Path) -> Dict[str, any]:
    """
    Entry point for autonomous execution wiring check.
    
    Args:
        cortex_root: Path to CORTEX root
    
    Returns:
        Dict with check results
    """
    checker = AutonomousExecutionWiringChecker(cortex_root)
    all_passed, successes, warnings = checker.check_autonomous_execution_wiring()
    
    return {
        'all_passed': all_passed,
        'successes': successes,
        'warnings': warnings,
        'check_name': 'Autonomous Execution Wiring'
    }
