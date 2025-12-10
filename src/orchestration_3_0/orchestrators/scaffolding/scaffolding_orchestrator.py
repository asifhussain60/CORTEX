"""
Scaffolding Orchestrator
Main entry point for legacy application modernization.

Coordinates:
1. CodeAnalyzer - Deep AST-powered code analysis
2. ArchitectureIntelligence - Pattern recognition and recommendations
3. MigrationStrategist - Strangler Fig migration planning
4. ScaffoldGenerator - Modern folder structure + boilerplate
5. OrchestratorChain - Trigger downstream workflows

Usage:
    orchestrator = ScaffoldingOrchestrator()
    result = await orchestrator.orchestrate(repo_path="/path/to/legacy/app")
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from .code_analyzer import CodeAnalyzer
from .architecture_intelligence import ArchitectureIntelligence
from .migration_strategist import MigrationStrategist
from .scaffold_generator import ScaffoldGenerator
from .orchestrator_chain import OrchestratorChain

logger = logging.getLogger(__name__)


class ScaffoldingOrchestrator:
    """
    Main orchestrator for legacy application modernization.
    
    Workflow:
    1. ANALYZE: Deep code analysis using Tree-sitter AST
    2. ASSESS: Recognize patterns, recommend modern architecture
    3. PLAN: Generate Strangler Fig migration strategy
    4. GENERATE: Create modern scaffold (Clean Architecture)
    5. TRIGGER: Chain downstream orchestrators (Planning, TDD, QA, DevOps)
    
    Example:
        orchestrator = ScaffoldingOrchestrator()
        result = await orchestrator.orchestrate(
            repo_path="/path/to/legacy/app",
            output_path="/path/to/new/app",
            constraints={"timeline": 6, "team_size": 3}
        )
    """
    
    def __init__(self):
        """Initialize scaffolding orchestrator."""
        self.code_analyzer: Optional[CodeAnalyzer] = None
        self.architecture_intelligence = ArchitectureIntelligence()
        self.migration_strategist = MigrationStrategist()
        self.scaffold_generator: Optional[ScaffoldGenerator] = None
        self.orchestrator_chain = OrchestratorChain()
        
        self.execution_log: list[Dict[str, Any]] = []
    
    async def orchestrate(
        self,
        repo_path: str,
        output_path: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        exclusions: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete scaffolding workflow.
        
        Args:
            repo_path: Path to legacy repository
            output_path: Path for generated scaffold (defaults to repo_path_modern)
            constraints: User constraints (timeline, team_size, risk_tolerance, target_framework)
            exclusions: Glob patterns to exclude from analysis
        
        Returns:
            Dictionary with complete orchestration results
        """
        start_time = datetime.now()
        
        # Default output path
        if not output_path:
            output_path = f"{repo_path}_modern"
        
        constraints = constraints or {}
        
        logger.info(f"Starting scaffolding orchestration for {repo_path}")
        self._log_step("START", "Scaffolding orchestration initiated")
        
        try:
            # Phase 1: ANALYZE - Deep code analysis
            logger.info("Phase 1: ANALYZE")
            code_report = await self._analyze_phase(repo_path, exclusions)
            self._log_step("ANALYZE", f"Analyzed {code_report.modules} modules, found {len(code_report.anti_patterns)} anti-patterns")
            
            # Phase 2: ASSESS - Architecture pattern recognition
            logger.info("Phase 2: ASSESS")
            architecture_assessment = await self._assess_phase(code_report, constraints)
            self._log_step("ASSESS", f"Current: {architecture_assessment.current_pattern} → Recommended: {architecture_assessment.recommended_pattern}")
            
            # Phase 3: PLAN - Migration strategy
            logger.info("Phase 3: PLAN")
            migration_strategy = await self._plan_phase(architecture_assessment, constraints)
            self._log_step("PLAN", f"Migration strategy: {len(migration_strategy.phases)} phases, {migration_strategy.total_duration_weeks} weeks")
            
            # Phase 4: GENERATE - Scaffold creation
            logger.info("Phase 4: GENERATE")
            scaffold_result = await self._generate_phase(architecture_assessment, output_path)
            self._log_step("GENERATE", f"Generated {scaffold_result['files_created']} files at {scaffold_result['scaffold_path']}")
            
            # Phase 5: TRIGGER - Orchestrator chain
            logger.info("Phase 5: TRIGGER")
            chain_result = await self._trigger_phase(scaffold_result, migration_strategy)
            self._log_step("TRIGGER", f"Triggered {chain_result['total_triggered']} downstream orchestrators")
            
            # Build final result
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'success': True,
                'repo_path': repo_path,
                'output_path': output_path,
                'duration_seconds': duration,
                'phases': {
                    'analyze': self._serialize_code_report(code_report),
                    'assess': self._serialize_architecture_assessment(architecture_assessment),
                    'plan': self._serialize_migration_strategy(migration_strategy),
                    'generate': scaffold_result,
                    'trigger': chain_result
                },
                'execution_log': self.execution_log,
                'summary': self._generate_summary(code_report, architecture_assessment, migration_strategy, scaffold_result, chain_result)
            }
            
            logger.info(f"Scaffolding orchestration complete in {duration:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Scaffolding orchestration failed: {e}", exc_info=True)
            self._log_step("ERROR", str(e))
            
            return {
                'success': False,
                'error': str(e),
                'execution_log': self.execution_log
            }
    
    async def _analyze_phase(self, repo_path: str, exclusions: Optional[list[str]]) -> Any:
        """Phase 1: Code analysis."""
        self.code_analyzer = CodeAnalyzer(repo_path, exclusions)
        
        # Run in executor to avoid blocking (Tree-sitter parsing is CPU-intensive)
        loop = asyncio.get_event_loop()
        code_report = await loop.run_in_executor(None, self.code_analyzer.analyze)
        
        return code_report
    
    async def _assess_phase(self, code_report: Any, constraints: Dict[str, Any]) -> Any:
        """Phase 2: Architecture assessment."""
        code_report_dict = self.code_analyzer.to_dict(code_report)
        assessment = self.architecture_intelligence.assess(code_report_dict, constraints)
        
        return assessment
    
    async def _plan_phase(self, architecture_assessment: Any, constraints: Dict[str, Any]) -> Any:
        """Phase 3: Migration planning."""
        assessment_dict = self.architecture_intelligence.to_dict(architecture_assessment)
        strategy = self.migration_strategist.plan(assessment_dict, constraints)
        
        return strategy
    
    async def _generate_phase(self, architecture_assessment: Any, output_path: str) -> Dict[str, Any]:
        """Phase 4: Scaffold generation."""
        self.scaffold_generator = ScaffoldGenerator(Path(output_path))
        
        assessment_dict = self.architecture_intelligence.to_dict(architecture_assessment)
        scaffold_result = self.scaffold_generator.generate(assessment_dict)
        
        return scaffold_result
    
    async def _trigger_phase(self, scaffold_result: Dict[str, Any], migration_strategy: Any) -> Dict[str, Any]:
        """Phase 5: Trigger downstream orchestrators."""
        strategy_dict = self.migration_strategist.to_dict(migration_strategy)
        chain_result = self.orchestrator_chain.trigger(scaffold_result, strategy_dict)
        
        return chain_result
    
    def _log_step(self, phase: str, message: str):
        """Log execution step."""
        self.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'message': message
        })
    
    def _serialize_code_report(self, report: Any) -> Dict[str, Any]:
        """Serialize code report for JSON."""
        return self.code_analyzer.to_dict(report)
    
    def _serialize_architecture_assessment(self, assessment: Any) -> Dict[str, Any]:
        """Serialize architecture assessment for JSON."""
        return self.architecture_intelligence.to_dict(assessment)
    
    def _serialize_migration_strategy(self, strategy: Any) -> Dict[str, Any]:
        """Serialize migration strategy for JSON."""
        return self.migration_strategist.to_dict(strategy)
    
    def _generate_summary(
        self,
        code_report: Any,
        architecture_assessment: Any,
        migration_strategy: Any,
        scaffold_result: Dict[str, Any],
        chain_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable summary."""
        return f"""
Scaffolding Orchestration Summary
===================================

LEGACY CODEBASE ANALYSIS:
- Language: {code_report.language}
- Framework: {code_report.framework or 'Unknown'}
- Modules: {code_report.modules}
- Classes: {code_report.classes}
- Functions: {code_report.functions}
- Anti-patterns: {len(code_report.anti_patterns)}
- Hotspots: {len(code_report.hotspots)}

ARCHITECTURE ASSESSMENT:
- Current Pattern: {architecture_assessment.current_pattern} (confidence: {architecture_assessment.current_confidence:.2f})
- Recommended Pattern: {architecture_assessment.recommended_pattern}
- Rationale: {architecture_assessment.rationale}
- Service Candidates: {len(architecture_assessment.service_candidates)}

MIGRATION STRATEGY:
- Total Duration: {migration_strategy.total_duration_weeks} weeks
- Total Effort: {migration_strategy.total_effort_hours} hours
- Phases: {len(migration_strategy.phases)}
- Risk Summary: {migration_strategy.risk_summary}

SCAFFOLD GENERATED:
- Path: {scaffold_result['scaffold_path']}
- Files Created: {scaffold_result['files_created']}
- Language: {scaffold_result['language']}
- Framework: {scaffold_result['framework']}

DOWNSTREAM ORCHESTRATORS TRIGGERED:
{chr(10).join(f"- {orch}" for orch in chain_result['orchestrators_triggered'])}

Next Steps:
1. Review generated scaffold at {scaffold_result['scaffold_path']}
2. Review migration strategy (saved in scaffold README.md)
3. Monitor downstream orchestrator progress via CORTEX dashboard
4. Begin Phase 1 implementation (Infrastructure Setup)
"""


# Convenience factory function
def create_scaffolding_orchestrator() -> ScaffoldingOrchestrator:
    """Create and return a configured ScaffoldingOrchestrator instance."""
    return ScaffoldingOrchestrator()
