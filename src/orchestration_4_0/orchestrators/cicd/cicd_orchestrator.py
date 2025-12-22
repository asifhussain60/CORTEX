"""
CI/CD Self-Healing Orchestrator

Intelligent CI/CD automation with self-healing capabilities.

Author: Asif Hussain
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ...base.base_orchestrator import BaseOrchestrator
from ..devops.devops_orchestrator import DevOpsOrchestrator
from ..devops.schemas import PipelineRun, PipelineStatus
from .schemas import (
    FailureAnalysis,
    FixAttempt,
    HealingResult,
    EscalationRequest,
    FixStrategy
)
from .failure_analyzer import FailureAnalyzer
from .auto_fix_engine import AutoFixEngine


class CICDSelfHealingOrchestrator(BaseOrchestrator):
    """
    Orchestrates CI/CD pipelines with self-healing capabilities.
    
    Monitors builds, analyzes failures, applies automatic fixes,
    and escalates complex issues when needed.
    """
    
    def __init__(
        self,
        name: str = "cicd_self_healing",
        devops_orchestrator: Optional[DevOpsOrchestrator] = None,
        max_fix_attempts: int = 3,
        escalation_threshold: float = 0.5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            name: Orchestrator name
            devops_orchestrator: DevOps orchestrator for pipeline operations
            max_fix_attempts: Maximum auto-fix attempts per failure
            escalation_threshold: Confidence threshold for escalation (0.0-1.0)
            logger: Optional logger instance
        """
        super().__init__(name, logger)
        self.devops_orchestrator = devops_orchestrator
        self.max_fix_attempts = max_fix_attempts
        self.escalation_threshold = escalation_threshold
        
        self.failure_analyzer = FailureAnalyzer(logger=self.logger)
        self.auto_fix_engine = AutoFixEngine(logger=self.logger)
        
        self.healing_history: List[HealingResult] = []
    
    def _setup(self) -> bool:
        """Setup phase - validate dependencies"""
        self.logger.info("🔧 Setting up CI/CD Self-Healing Orchestrator")
        
        if not self.devops_orchestrator:
            self.logger.warning("⚠️ No DevOps orchestrator provided - limited functionality")
        
        return True
    
    def _register_phases(self):
        """Register orchestration phases"""
        self.phases = [
            {
                "name": "monitor",
                "description": "Monitor CI/CD pipelines for failures",
                "required": True
            },
            {
                "name": "analyze",
                "description": "Analyze failures and determine root cause",
                "required": True
            },
            {
                "name": "heal",
                "description": "Apply automatic fixes to resolve failures",
                "required": True
            },
            {
                "name": "verify",
                "description": "Verify fixes and check pipeline health",
                "required": True
            },
            {
                "name": "escalate",
                "description": "Escalate complex issues to humans",
                "required": False
            }
        ]
    
    async def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific phase"""
        if phase_name == "monitor":
            return await self._monitor_pipelines(context)
        elif phase_name == "analyze":
            return await self._analyze_failures(context)
        elif phase_name == "heal":
            return await self._apply_healing(context)
        elif phase_name == "verify":
            return await self._verify_fixes(context)
        elif phase_name == "escalate":
            return await self._escalate_issues(context)
        else:
            return {"success": False, "error": f"Unknown phase: {phase_name}"}
    
    def _teardown(self) -> bool:
        """Cleanup phase"""
        self.logger.info(f"✅ CI/CD Self-Healing Orchestrator complete - {len(self.healing_history)} healing attempts")
        return True
    
    # --- Core Workflow Methods ---
    
    async def monitor_and_heal(
        self,
        pipeline_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HealingResult:
        """
        Monitor a pipeline and apply healing if failures occur.
        
        Args:
            pipeline_id: Pipeline identifier
            context: Additional context (repo path, config, etc.)
            
        Returns:
            HealingResult with outcome
        """
        start_time = datetime.now()
        ctx = context or {}
        ctx["pipeline_id"] = pipeline_id
        
        self.logger.info(f"🔍 Monitoring pipeline: {pipeline_id}")
        
        # Monitor
        monitor_result = await self._monitor_pipelines(ctx)
        if not monitor_result.get("has_failures"):
            return HealingResult(
                run_id=pipeline_id,
                platform=ctx.get("platform", "unknown"),
                initial_failure=None,  # No failure
                fix_attempts=[],
                final_status="success",
                healed=False,  # Nothing to heal
                total_healing_time_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=start_time
            )
        
        # Analyze
        analyze_result = await self._analyze_failures(ctx)
        failure = analyze_result.get("failure_analysis")
        
        if not failure:
            return HealingResult(
                run_id=pipeline_id,
                platform=ctx.get("platform", "unknown"),
                initial_failure=None,
                fix_attempts=[],
                final_status="analysis_failed",
                healed=False,
                total_healing_time_seconds=(datetime.now() - start_time).total_seconds(),
                human_escalation_triggered=True,
                timestamp=start_time
            )
        
        # Heal
        heal_result = await self._apply_healing({"failure": failure, **ctx})
        fix_attempts = heal_result.get("fix_attempts", [])
        
        # Verify
        verify_result = await self._verify_fixes({"fix_attempts": fix_attempts, **ctx})
        
        # Escalate if needed
        escalated = False
        escalation_reason = None
        if not verify_result.get("all_passed") or failure.confidence < self.escalation_threshold:
            escalate_result = await self._escalate_issues({"failure": failure, **ctx})
            escalated = escalate_result.get("escalated", False)
            escalation_reason = escalate_result.get("reason")
        
        result = HealingResult(
            run_id=pipeline_id,
            platform=ctx.get("platform", "unknown"),
            initial_failure=failure,
            fix_attempts=fix_attempts,
            final_status="success" if verify_result.get("all_passed", False) else "failed",
            healed=verify_result.get("all_passed", False),
            total_healing_time_seconds=(datetime.now() - start_time).total_seconds(),
            human_escalation_triggered=escalated,
            timestamp=start_time
        )
        
        self.healing_history.append(result)
        return result
    
    async def _monitor_pipelines(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor pipelines for failures"""
        pipeline_id = context.get("pipeline_id")
        
        if not self.devops_orchestrator:
            # Simulate monitoring
            return {
                "has_failures": True,
                "pipeline_id": pipeline_id,
                "status": "failed"
            }
        
        # Real monitoring (placeholder)
        # In real implementation, would poll pipeline status
        await asyncio.sleep(0.1)
        
        return {
            "has_failures": True,
            "pipeline_id": pipeline_id,
            "status": "failed"
        }
    
    async def _analyze_failures(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pipeline failures"""
        pipeline_id = context.get("pipeline_id")
        
        # Get build logs (simulated)
        logs = context.get("logs", [
            "ERROR: Dependency conflict: package-a 1.0 requires package-b <2.0, but 2.1 is installed",
            "Test suite failed: test_user_authentication FAILED",
            "Configuration error: Missing DATABASE_URL environment variable"
        ])
        
        # Analyze
        failure = await self.failure_analyzer.analyze(logs, context)
        
        return {
            "failure_analysis": failure,
            "pipeline_id": pipeline_id
        }
    
    async def _apply_healing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic fixes"""
        failure: FailureAnalysis = context.get("failure")
        fix_attempts = []
        
        # Try each suggested fix strategy
        for strategy in failure.suggested_fixes[:self.max_fix_attempts]:
            attempt = await self.auto_fix_engine.apply_fix(failure, strategy, context)
            fix_attempts.append(attempt)
            
            if attempt.success and attempt.verification_passed:
                self.logger.info(f"✅ Healing successful with strategy: {strategy}")
                break
        
        return {
            "fix_attempts": fix_attempts,
            "healing_applied": any(a.success for a in fix_attempts)
        }
    
    async def _verify_fixes(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify that fixes resolved the issue"""
        fix_attempts: List[FixAttempt] = context.get("fix_attempts", [])
        
        # Check if any fix succeeded
        all_passed = any(a.success and a.verification_passed for a in fix_attempts)
        
        if all_passed:
            self.logger.info("✅ Verification passed - pipeline should succeed now")
        else:
            self.logger.warning("⚠️ Verification failed - may need escalation")
        
        return {
            "all_passed": all_passed,
            "verified_count": sum(1 for a in fix_attempts if a.verification_passed)
        }
    
    async def _escalate_issues(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate complex issues to humans"""
        failure: FailureAnalysis = context.get("failure")
        
        if not failure or failure.confidence >= self.escalation_threshold:
            return {"escalated": False}
        
        reason = f"Low confidence ({failure.confidence:.2f}) in analysis"
        
        escalation = EscalationRequest(
            run_id=context.get("pipeline_id", "unknown"),
            platform=context.get("platform", "unknown"),
            failure=failure,
            failed_fixes=[],
            urgency="HIGH" if failure.confidence < 0.3 else "MEDIUM",
            timestamp=datetime.now()
        )
        
        self.logger.warning(f"🚨 Escalating issue: {reason}")
        
        # In real implementation, would create ticket/alert
        
        return {
            "escalated": True,
            "reason": reason,
            "escalation": escalation
        }
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get statistics about healing operations"""
        if not self.healing_history:
            return {"total_attempts": 0, "success_rate": 0.0}
        
        total = len(self.healing_history)
        successful = sum(1 for h in self.healing_history if h.healed)
        escalated = sum(1 for h in self.healing_history if h.human_escalation_triggered)
        
        return {
            "total_attempts": total,
            "successful": successful,
            "escalated": escalated,
            "success_rate": successful / total if total > 0 else 0.0,
            "escalation_rate": escalated / total if total > 0 else 0.0,
            "avg_time_seconds": sum(h.total_healing_time_seconds for h in self.healing_history) / total
        }
