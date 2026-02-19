"""Health Orchestrator - Coordinates Health Agents

Main orchestrator that coordinates specialized health agents to detect
and report repository health issues. Provides integration with CI/CD,
pre-commit hooks, and MCP tools.

Architecture (post-refactor):
    PHASE-92 HealthOrchestrator.run_health_check()
        └── delegates file-system walk to Phase-48 HealthOrchestrator.scan()
                via a shared FileContext (single rglob, zero subprocess spawns)
        └── returns HealthReport for backward compatibility

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agents.base_agent import BaseHealthAgent, HealthCheckResult
from .reports.health_report import HealthReport, HealthMetrics
from .intelligence import HealthIntelligence
from cortex.orchestrators.support.health_orchestrator import (
    HealthOrchestrator as _Phase48Orchestrator,
)

class HealthOrchestrator:
    """Main orchestrator for repository health management.
    
    Coordinates multiple health agents to scan the repository for issues,
    generates comprehensive reports, and provides actionable recommendations.
    
    Attributes:
        workspace_root: Root path of workspace to check
        agents: List of registered health agents
        config: Orchestrator configuration
        enabled: Whether orchestrator is enabled
    
    Usage:
        ```python
        orchestrator = HealthOrchestrator(Path("/path/to/repo"))
        
        # Register agents
        orchestrator.register_agent(DuplicateDetectionAgent())
        orchestrator.register_agent(StubDetectionAgent())
        
        # Run health check
        report = orchestrator.run_health_check()
        
        # Get recommendations
        recommendations = report.generate_recommendations()
        ```
    """
    
    def __init__(
        self,
        workspace_root: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize Health Orchestrator.
        
        Args:
            workspace_root: Root path of workspace to check
            config: Optional configuration dictionary
        """
        self.workspace_root = Path(workspace_root)
        self.agents: List[BaseHealthAgent] = []
        self.config = config or {}
        self.enabled = True
        
        if not self.workspace_root.exists():
            raise ValueError(f"Workspace root does not exist: {self.workspace_root}")
        
        # Initialize intelligence layer (after existence check — mkdir(parents=True)
        # inside HealthIntelligence would create the workspace dir otherwise)
        self.intelligence = HealthIntelligence(self.workspace_root)
    
    def register_agent(self, agent: BaseHealthAgent) -> None:
        """Register a health agent.
        
        Args:
            agent: Health agent instance to register
        """
        self.agents.append(agent)
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister a health agent by name.
        
        Args:
            agent_name: Name of agent to unregister
        
        Returns:
            True if agent was found and removed, False otherwise
        """
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[BaseHealthAgent]:
        """Get agent by name.
        
        Args:
            agent_name: Name of agent to find
        
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None
    
    def list_agents(self) -> List[str]:
        """List all registered agent names.
        
        Returns:
            List of agent names
        """
        return [agent.name for agent in self.agents]
    
    def run_health_check(
        self,
        agent_names: Optional[List[str]] = None,
        use_intelligence: bool = True,
    ) -> HealthReport:
        """Run health check with registered agents.

        Delegates the filesystem walk to the Phase-48 HealthOrchestrator
        (single ``rglob`` via ``FileContext``) then runs PHASE-92 agents
        against the shared context so no additional disk I/O is needed.

        Args:
            agent_names: Optional list of specific agents to run.
                        If None, runs all enabled agents.
            use_intelligence: Whether to use intelligence layer for
                            caching and false positive suppression

        Returns:
            HealthReport with aggregated results
        """
        from cortex.orchestrators.support.health_orchestrator import FileContext  # noqa: F401 (kept for type checking)

        start_time = time.time()
        report = HealthReport(workspace_root=self.workspace_root)

        # --- Phase-48 delegation: single rglob walk --------------------------
        phase48 = _Phase48Orchestrator(workspace_root=self.workspace_root)
        phase48_result = phase48.scan()

        # Expose Phase-48 ScanResult on the report for callers that need it
        report.metadata["phase48_scan"] = {
            "total_files": phase48_result.total_files_scanned,
            "issues_found": phase48_result.issues_found,
            "duration_ms": phase48_result.scan_duration_ms,
        }

        # Reuse the FileContext built inside Phase-48 scan() — zero extra rglob
        ctx = phase48.last_ctx

        # --- PHASE-92 agents -------------------------------------------------
        # Determine which agents to run
        agents_to_run = self.agents
        if agent_names:
            agents_to_run = [
                agent for agent in self.agents
                if agent.name in agent_names
            ]

        # Run each agent
        for agent in agents_to_run:
            # Skip disabled agents AND check orchestrator enabled status
            if not self.enabled or not agent.is_enabled():
                continue

            try:
                # Check intelligence cache if enabled
                if use_intelligence:
                    cached_files = 0
                    for file_path in ctx.files:
                        if file_path.suffix == ".py" and self.intelligence.should_skip_file(
                            file_path, agent.name
                        ):
                            cached_files += 1

                    if cached_files > 0:
                        print(f"  {agent.name}: Skipped {cached_files} unchanged files (cached)")

                # Run agent — pass ctx if agent supports it
                try:
                    result = agent.check(self.workspace_root, ctx=ctx)
                except TypeError:
                    # Agent doesn't accept ctx yet — backward compat
                    result = agent.check(self.workspace_root)

                # Filter false positives using intelligence
                if use_intelligence and result.issues:
                    original_count = len(result.issues)
                    filtered_issues = [
                        issue for issue in result.issues
                        if not self.intelligence.is_false_positive(
                            issue.file_path,
                            issue.category.value,
                            issue.description,
                        )
                    ]
                    result.issues = filtered_issues

                    if len(filtered_issues) < original_count:
                        suppressed = original_count - len(filtered_issues)
                        print(f"  {agent.name}: Suppressed {suppressed} known false positives")

                # Cache result
                if use_intelligence:
                    self.intelligence.cache_result(
                        agent_name=agent.name,
                        result=result,
                    )

                report.add_agent_result(result)
            except Exception as e:
                print(f"Error running {agent.name}: {str(e)}")
                error_result = HealthCheckResult(
                    agent_name=agent.name,
                    issues=[],
                    files_scanned=0,
                    duration_seconds=0.0,
                    metadata={"error": str(e)},
                )
                report.add_agent_result(error_result)
        
        # Generate recommendations with intelligence
        report.generate_recommendations()
        
        # Update total duration
        report.metadata["total_duration_seconds"] = time.time() - start_time
        
        # Add intelligence stats
        if use_intelligence:
            intel_stats = self.intelligence.get_efficiency_stats()
            report.metadata["intelligence"] = intel_stats
        
        return report
    
    def run_agent(self, agent_name: str) -> Optional[HealthCheckResult]:
        """Run a specific agent by name.
        
        Args:
            agent_name: Name of agent to run
        
        Returns:
            HealthCheckResult or None if agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return None
        
        if not agent.is_enabled():
            return None
        
        return agent.check(self.workspace_root)
    
    def enable_agent(self, agent_name: str) -> bool:
        """Enable a specific agent.
        
        Args:
            agent_name: Name of agent to enable
        
        Returns:
            True if agent was found, False otherwise
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.enable()
            return True
        return False
    
    def disable_agent(self, agent_name: str) -> bool:
        """Disable a specific agent.
        
        Args:
            agent_name: Name of agent to disable
        
        Returns:
            True if agent was found, False otherwise
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.disable()
            return True
        return False
    
    def scan(self) -> Any:
        """Proxy to Phase-48 HealthOrchestrator.scan() for unified API.

        Exposes the raw filesystem scan result from the Phase-48 engine,
        allowing callers to access low-level ScanResult without also needing
        to import from cortex.orchestrators.support.

        Returns:
            ScanResult from Phase-48 HealthOrchestrator.scan()

        AC: GP50-004 / GP50-005 — Phase 50 unified scan() API
        """
        phase48 = _Phase48Orchestrator(workspace_root=self.workspace_root)
        return phase48.scan()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of orchestrator state.
        
        Returns:
            Dictionary with orchestrator summary
        """
        return {
            "workspace_root": str(self.workspace_root),
            "agents_registered": len(self.agents),
            "agents_enabled": sum(1 for agent in self.agents if agent.is_enabled()),
            "agent_names": self.list_agents(),
            "enabled": self.enabled,
        }
    
    def check_definition_of_done(
        self,
        min_score: float = 80.0,
        blocking_agents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Check if Definition of Done (DoD) gate is satisfied.
        
        This gate enforces production-ready code quality by validating
        health score and critical agent checks.
        
        Args:
            min_score: Minimum health score required (0-100)
            blocking_agents: List of agent names that must pass (no issues)
                           Default: DuplicateDetectionAgent, StubDetectionAgent
        
        Returns:
            Dictionary with DoD check results:
                - passed: bool - Whether DoD gate passed
                - health_score: float - Overall health score
                - blocking_failures: List[str] - Failed blocking agents
                - recommendation: str - Action to take
        
        Usage:
            ```python
            orchestrator = HealthOrchestrator(Path("."))
            dod_result = orchestrator.check_definition_of_done(min_score=80.0)
            
            if not dod_result["passed"]:
                print(f"DoD FAILED: {dod_result['recommendation']}")
                sys.exit(1)
            ```
        """
        # Default blocking agents (P0 violations)
        if blocking_agents is None:
            blocking_agents = [
                "DuplicateDetectionAgent",
                "StubDetectionAgent",
            ]
        
        # Run health check
        report = self.run_health_check()
        
        # Calculate health score (already calculated during metric updates)
        health_score = report.metrics.health_score
        
        # Check blocking agents
        blocking_failures: List[str] = []
        for agent_name in blocking_agents:
            agent_result = next(
                (r for r in report.agent_results if r.agent_name == agent_name),
                None
            )
            if agent_result and len(agent_result.issues) > 0:
                blocking_failures.append(
                    f"{agent_name}: {len(agent_result.issues)} issues"
                )
        
        # Determine if DoD passed
        passed = health_score >= min_score and len(blocking_failures) == 0
        
        # Generate recommendation
        if passed:
            recommendation = "✅ DoD PASSED - Code meets production quality standards"
        else:
            reasons = []
            if health_score < min_score:
                reasons.append(f"Health score {health_score:.1f} < {min_score}")
            if blocking_failures:
                reasons.append(f"Blocking failures: {', '.join(blocking_failures)}")
            recommendation = f"❌ DoD FAILED - {' | '.join(reasons)}"
        
        return {
            "passed": passed,
            "health_score": health_score,
            "min_score_required": min_score,
            "blocking_failures": blocking_failures,
            "total_issues": report.metrics.total_issues,
            "critical_issues": report.metrics.critical_issues,
            "recommendation": recommendation,
        }


__all__ = ["HealthOrchestrator"]
