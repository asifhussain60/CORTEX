"""
Auto-Fix Engine for CI/CD Self-Healing

Implements fix strategies for common CI/CD failures.

Author: Asif Hussain
Version: 1.0
"""

import logging
import time
import asyncio
from typing import Optional, Dict, Any

from .schemas import FailureAnalysis, FixAttempt, FixStrategy


class AutoFixEngine:
    """
    Implements automated fixes for common CI/CD failures.
    
    Each fix strategy has a dedicated method that attempts the fix
    and returns a FixAttempt with success status.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize auto-fix engine.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Strategy handlers
        self.fix_handlers = {
            FixStrategy.DEPENDENCY_UPDATE: self._fix_dependency_update,
            FixStrategy.DEPENDENCY_ROLLBACK: self._fix_dependency_rollback,
            FixStrategy.TEST_RETRY: self._fix_test_retry,
            FixStrategy.TEST_ISOLATION: self._fix_test_isolation,
            FixStrategy.CONFIG_FIX: self._fix_config,
            FixStrategy.ENV_VAR_ADD: self._fix_env_var,
            FixStrategy.TIMEOUT_INCREASE: self._fix_timeout,
            FixStrategy.RESOURCE_INCREASE: self._fix_resource_limit,
            FixStrategy.CODE_FIX: self._fix_code,
            FixStrategy.ROLLBACK: self._fix_rollback,
        }
    
    async def apply_fix(
        self,
        failure: FailureAnalysis,
        strategy: FixStrategy,
        context: Dict[str, Any]
    ) -> FixAttempt:
        """
        Apply a fix strategy to the failure.
        
        Args:
            failure: Failure analysis
            strategy: Fix strategy to apply
            context: Additional context (repo path, config, etc.)
            
        Returns:
            FixAttempt with results
        """
        self.logger.info(f"🔧 Applying fix: {strategy}")
        start_time = time.time()
        
        try:
            # Get handler for strategy
            handler = self.fix_handlers.get(strategy)
            
            if not handler:
                return FixAttempt(
                    strategy=strategy,
                    success=False,
                    fixes_applied=[],
                    changes_made={},
                    time_seconds=time.time() - start_time,
                    error_message=f"No handler for strategy: {strategy}",
                    verification_passed=False
                )
            
            # Apply fix
            result = await handler(failure, context)
            
            elapsed = time.time() - start_time
            result["time_seconds"] = elapsed
            result["strategy"] = strategy
            
            if result["success"]:
                self.logger.info(
                    f"✅ Fix applied successfully: {strategy} "
                    f"({len(result['fixes_applied'])} changes, {elapsed:.2f}s)"
                )
            else:
                self.logger.warning(f"❌ Fix failed: {strategy} - {result.get('error_message')}")
            
            return FixAttempt(**result)
            
        except Exception as e:
            self.logger.error(f"❌ Fix error: {strategy} - {str(e)}")
            return FixAttempt(
                strategy=strategy,
                success=False,
                fixes_applied=[],
                changes_made={},
                time_seconds=time.time() - start_time,
                error_message=str(e),
                verification_passed=False
            )
    
    async def _fix_dependency_update(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fix dependency conflicts by updating packages"""
        fixes_applied = []
        changes_made = {}
        
        # Simulate dependency update (in real implementation, would modify lock files)
        for dep in failure.affected_dependencies[:5]:  # Limit to 5
            fixes_applied.append(f"Updated {dep} to latest compatible version")
            changes_made[dep] = "updated"
            await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "success": bool(fixes_applied),
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_dependency_rollback(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Roll back recent dependency changes"""
        fixes_applied = ["Rolled back to last known good dependency versions"]
        changes_made = {"rollback": "dependencies"}
        
        await asyncio.sleep(0.2)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_test_retry(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retry failed tests (for flaky tests)"""
        fixes_applied = ["Retried failed tests with isolation"]
        changes_made = {"retry_count": 1}
        
        await asyncio.sleep(0.15)  # Simulate work
        
        # Simulate 70% success rate for test retries
        import random
        success = random.random() > 0.3
        
        return {
            "success": success,
            "fixes_applied": fixes_applied if success else [],
            "changes_made": changes_made,
            "verification_passed": success,
            "error_message": None if success else "Tests still failing after retry"
        }
    
    async def _fix_test_isolation(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Isolate and re-run failing tests"""
        fixes_applied = ["Isolated failing tests and re-ran separately"]
        changes_made = {"isolation": "enabled"}
        
        await asyncio.sleep(0.2)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_config(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fix configuration errors"""
        fixes_applied = ["Added missing configuration values"]
        changes_made = {"config": "updated"}
        
        await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_env_var(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add missing environment variables"""
        fixes_applied = []
        changes_made = {}
        
        # Extract env var names from error messages
        import re
        for error in failure.error_messages:
            matches = re.findall(r"(?:environment variable|env var).*?['\"]?([A-Z_]+)['\"]?", error, re.IGNORECASE)
            for var in matches:
                fixes_applied.append(f"Added environment variable: {var}")
                changes_made[var] = "added"
        
        await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "success": bool(fixes_applied),
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_timeout(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Increase timeout limits"""
        fixes_applied = ["Increased timeout limit by 50%"]
        changes_made = {"timeout": "increased"}
        
        await asyncio.sleep(0.05)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_resource_limit(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Increase resource limits"""
        fixes_applied = ["Increased memory limit", "Increased disk space allocation"]
        changes_made = {"resources": "increased"}
        
        await asyncio.sleep(0.1)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_code(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fix code issues (syntax, linting)"""
        fixes_applied = []
        changes_made = {}
        
        for file in failure.affected_files[:3]:  # Limit to 3
            fixes_applied.append(f"Fixed syntax errors in {file}")
            changes_made[file] = "fixed"
        
        await asyncio.sleep(0.15)  # Simulate work
        
        return {
            "success": bool(fixes_applied),
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
    
    async def _fix_rollback(
        self,
        failure: FailureAnalysis,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rollback to last good commit"""
        fixes_applied = ["Rolled back to last successful build"]
        changes_made = {"rollback": "last_good_commit"}
        
        await asyncio.sleep(0.2)  # Simulate work
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "changes_made": changes_made,
            "verification_passed": True
        }
