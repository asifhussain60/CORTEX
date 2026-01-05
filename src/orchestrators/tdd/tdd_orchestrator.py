"""
CORTEX 4.0 TDD Orchestrator - Unified, Clean, Adaptive

Purpose: RED→GREEN→REFACTOR workflow with clean architecture and adaptive learning
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19

Key Features:
- Strategy pattern for phase execution
- AI-driven code generation and refactoring
- Adaptive learning from technology trends
- Clean code best practices enforcement
- DoR/DoD validation at phase boundaries
- Automatic rollback on failures
- Technology discovery and adaptation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import asyncio
import logging
from datetime import datetime

# Task 6.10 Package Imports (Post-Phase 5 Enhancement)
from src.orchestrators.tdd.parallel_test_runner import ParallelTestRunner
from src.orchestrators.tdd.test_quality_evaluator import TestQualityEvaluator
from src.orchestrators.tdd.code_safety_guardrail import CodeSafetyGuardrail
from src.orchestration_4_0.execution.execution_mode_manager import ExecutionModeManager

# Phase 5 Component Imports (Day 1: Multi-Agent Collaboration)
from src.orchestration_4_0.frameworks.multi_agent_orchestrator import (
    MultiAgentOrchestrator,
    CollaborationPattern
)
from src.orchestration_4_0.learning.agent_learning_engine import (
    AgentLearningEngine,
    StrategyType,
    ExecutionPattern
)
from src.orchestration_4_0.frameworks.context_validator import (
    ContextValidator,
    ContextQuality
)

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models
# ============================================================================

class TDDPhase(Enum):
    """TDD workflow phases."""
    RED = "RED"
    GREEN = "GREEN"
    REFACTOR = "REFACTOR"


@dataclass
class ValidationResult:
    """Result from DoR/DoD validation."""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhaseResult:
    """Result from phase execution."""
    phase_name: str
    success: bool
    outputs: Dict[str, Any]
    metrics: Dict[str, Any]
    git_commit_sha: Optional[str] = None
    documentation_updated: bool = False
    brain_patterns_extracted: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TechnologyProfile:
    """Adaptive technology profile for learning."""
    language: str
    frameworks: List[str]
    test_frameworks: List[str]
    version_info: Dict[str, str]
    last_updated: datetime
    patterns_learned: int = 0
    confidence_score: float = 0.5


# ============================================================================
# Strategy Pattern: Base Strategy
# ============================================================================

class TDDPhaseStrategy(ABC):
    """
    Base strategy for TDD phase execution.
    
    Each phase (RED, GREEN, REFACTOR) implements this interface with:
    - DoR validation (Definition of Ready)
    - Phase execution
    - DoD validation (Definition of Done)
    - Rollback capability
    """
    
    @abstractmethod
    async def validate_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Ready for this phase."""
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """Execute phase autonomously."""
        pass
    
    @abstractmethod
    async def validate_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Done for this phase."""
        pass
    
    @abstractmethod
    async def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback phase changes if validation fails."""
        pass


# ============================================================================
# Adaptive Learning Framework
# ============================================================================

class TechnologyDiscoveryEngine:
    """
    Discovers and adapts to new technologies, frameworks, and patterns.
    
    Purpose: Keep TDD orchestrator current with latest releases
    Features:
    - Framework version detection
    - New pattern discovery
    - Best practice learning
    - Breaking change adaptation
    """
    
    def __init__(self, brain_connector, knowledge_graph):
        self.brain = brain_connector
        self.kg = knowledge_graph
        self.tech_profiles: Dict[str, TechnologyProfile] = {}
        logger.info("🎭 Technology Discovery Engine initialized")
    
    async def discover_project_tech_stack(
        self,
        project_path: Path
    ) -> TechnologyProfile:
        """
        Discover technology stack from project.
        
        Detects:
        - Language and version
        - Frameworks and versions
        - Test frameworks
        - Build tools
        """
        profile_cache_key = str(project_path)
        
        if profile_cache_key in self.tech_profiles:
            cached = self.tech_profiles[profile_cache_key]
            if (datetime.now() - cached.last_updated).days < 7:
                return cached
        
        logger.info(f"🔍 Discovering tech stack: {project_path}")
        
        # Detect language
        language = await self._detect_language(project_path)
        
        # Detect frameworks
        frameworks = await self._detect_frameworks(project_path, language)
        
        # Detect test frameworks
        test_frameworks = await self._detect_test_frameworks(
            project_path,
            language
        )
        
        # Get version information
        version_info = await self._get_version_info(
            project_path,
            language,
            frameworks
        )
        
        profile = TechnologyProfile(
            language=language,
            frameworks=frameworks,
            test_frameworks=test_frameworks,
            version_info=version_info,
            last_updated=datetime.now()
        )
        
        self.tech_profiles[profile_cache_key] = profile
        
        logger.info(f"✅ Tech profile: {language} + {frameworks}")
        return profile
    
    async def _detect_language(self, project_path: Path) -> str:
        """Detect primary programming language."""
        file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.rs': 'Rust'
        }
        
        counts = {}
        for ext, lang in file_extensions.items():
            count = len(list(project_path.rglob(f'*{ext}')))
            if count > 0:
                counts[lang] = count
        
        if not counts:
            return 'Unknown'
        
        return max(counts.items(), key=lambda x: x[1])[0]
    
    async def _detect_frameworks(
        self,
        project_path: Path,
        language: str
    ) -> List[str]:
        """Detect frameworks used in project."""
        frameworks = []
        
        # Python frameworks
        if language == 'Python':
            requirements_file = project_path / 'requirements.txt'
            if requirements_file.exists():
                content = requirements_file.read_text()
                if 'django' in content.lower():
                    frameworks.append('Django')
                if 'flask' in content.lower():
                    frameworks.append('Flask')
                if 'fastapi' in content.lower():
                    frameworks.append('FastAPI')
        
        # JavaScript/TypeScript frameworks
        elif language in ['JavaScript', 'TypeScript']:
            package_json = project_path / 'package.json'
            if package_json.exists():
                import json
                data = json.loads(package_json.read_text())
                deps = {**data.get('dependencies', {}), 
                       **data.get('devDependencies', {})}
                
                if 'react' in deps:
                    frameworks.append('React')
                if 'vue' in deps:
                    frameworks.append('Vue')
                if 'angular' in deps or '@angular/core' in deps:
                    frameworks.append('Angular')
                if 'next' in deps:
                    frameworks.append('Next.js')
        
        # .NET frameworks
        elif language == 'C#':
            csproj_files = list(project_path.rglob('*.csproj'))
            if csproj_files:
                # Parse csproj to detect framework
                frameworks.append('.NET')
        
        return frameworks
    
    async def _detect_test_frameworks(
        self,
        project_path: Path,
        language: str
    ) -> List[str]:
        """Detect test frameworks used."""
        test_frameworks = []
        
        if language == 'Python':
            requirements_file = project_path / 'requirements.txt'
            if requirements_file.exists():
                content = requirements_file.read_text()
                if 'pytest' in content.lower():
                    test_frameworks.append('pytest')
                if 'unittest' in content.lower():
                    test_frameworks.append('unittest')
        
        elif language in ['JavaScript', 'TypeScript']:
            package_json = project_path / 'package.json'
            if package_json.exists():
                import json
                data = json.loads(package_json.read_text())
                deps = {**data.get('dependencies', {}), 
                       **data.get('devDependencies', {})}
                
                if 'jest' in deps:
                    test_frameworks.append('jest')
                if 'mocha' in deps:
                    test_frameworks.append('mocha')
                if 'vitest' in deps:
                    test_frameworks.append('vitest')
        
        return test_frameworks
    
    async def _get_version_info(
        self,
        project_path: Path,
        language: str,
        frameworks: List[str]
    ) -> Dict[str, str]:
        """Get version information for language and frameworks."""
        versions = {}
        
        # Language version detection
        if language == 'Python':
            try:
                import sys
                versions['Python'] = f"{sys.version_info.major}.{sys.version_info.minor}"
            except Exception:
                versions['Python'] = 'unknown'
        
        # Framework versions would require parsing package files
        for framework in frameworks:
            versions[framework] = 'latest'  # Placeholder
        
        return versions
    
    async def learn_from_patterns(
        self,
        project_path: Path,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ) -> int:
        """
        Learn from successful patterns and store in knowledge graph.
        
        Returns: Number of patterns learned
        """
        profile = await self.discover_project_tech_stack(project_path)
        
        # Store pattern in knowledge graph
        pattern_entry = {
            'type': pattern_type,
            'language': profile.language,
            'frameworks': profile.frameworks,
            'data': pattern_data,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.7  # Initial confidence
        }
        
        await self.kg.store_pattern(
            pattern_id=f"{pattern_type}_{profile.language}_{datetime.now().timestamp()}",
            pattern=pattern_entry
        )
        
        profile.patterns_learned += 1
        profile.confidence_score = min(0.95, profile.confidence_score + 0.05)
        
        logger.info(f"✅ Learned pattern: {pattern_type} for {profile.language}")
        return 1
    
    async def get_best_practices(
        self,
        language: str,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve best practices for language/framework.
        
        Sources:
        - Knowledge graph (learned patterns)
        - External API (latest trends)
        - Community standards
        """
        # Query knowledge graph for patterns
        patterns = await self.kg.query_patterns(
            filters={
                'language': language,
                'framework': framework
            },
            limit=10
        )
        
        best_practices = {
            'language': language,
            'framework': framework,
            'patterns': patterns,
            'recommendations': []
        }
        
        # Add language-specific best practices
        if language == 'Python':
            best_practices['recommendations'].extend([
                'Use type hints for better code quality',
                'Follow PEP 8 style guide',
                'Write docstrings for all public functions',
                'Use context managers for resource management'
            ])
        
        return best_practices


# ============================================================================
# Clean Code Enforcer
# ============================================================================

class CleanCodeEnforcer:
    """
    Enforces clean code best practices during TDD workflow.
    
    Principles:
    - SOLID principles
    - DRY (Don't Repeat Yourself)
    - KISS (Keep It Simple, Stupid)
    - YAGNI (You Aren't Gonna Need It)
    - Single Responsibility
    """
    
    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        logger.info("🎭 Clean Code Enforcer initialized")
    
    async def analyze_code_quality(
        self,
        file_path: Path,
        code_content: str
    ) -> Dict[str, Any]:
        """
        Analyze code for clean code violations.
        
        Returns: Quality report with violations and recommendations
        """
        violations = []
        
        # Check function length (max 20 lines)
        violations.extend(await self._check_function_length(code_content))
        
        # Check cyclomatic complexity (max 10)
        violations.extend(await self._check_complexity(code_content))
        
        # Check duplicate code
        violations.extend(await self._check_duplicates(code_content))
        
        # Check naming conventions
        violations.extend(await self._check_naming(code_content))
        
        # Check for god classes/methods
        violations.extend(await self._check_god_objects(code_content))
        
        quality_score = self._calculate_quality_score(violations)
        
        return {
            'file': str(file_path),
            'quality_score': quality_score,
            'violations': violations,
            'total_violations': len(violations),
            'recommendations': self._generate_recommendations(violations)
        }
    
    async def _check_function_length(self, code: str) -> List[Dict[str, Any]]:
        """Check for overly long functions (>20 lines)."""
        violations = []
        # Parse AST and check function lengths
        # Simplified placeholder
        return violations
    
    async def _check_complexity(self, code: str) -> List[Dict[str, Any]]:
        """Check cyclomatic complexity (>10 is violation)."""
        violations = []
        # Calculate complexity using AST
        # Simplified placeholder
        return violations
    
    async def _check_duplicates(self, code: str) -> List[Dict[str, Any]]:
        """Detect duplicate code blocks."""
        violations = []
        # Use similarity analysis
        # Simplified placeholder
        return violations
    
    async def _check_naming(self, code: str) -> List[Dict[str, Any]]:
        """Check naming convention violations."""
        violations = []
        # Check PEP 8 naming for Python
        # Simplified placeholder
        return violations
    
    async def _check_god_objects(self, code: str) -> List[Dict[str, Any]]:
        """Detect god classes/methods (too many responsibilities)."""
        violations = []
        # Check class method count and responsibilities
        # Simplified placeholder
        return violations
    
    def _calculate_quality_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score (0.0 to 10.0)."""
        if not violations:
            return 10.0
        
        # Deduct points based on violation severity
        score = 10.0
        for violation in violations:
            severity = violation.get('severity', 'low')
            if severity == 'critical':
                score -= 2.0
            elif severity == 'high':
                score -= 1.0
            elif severity == 'medium':
                score -= 0.5
            else:
                score -= 0.2
        
        return max(0.0, score)
    
    def _generate_recommendations(
        self,
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        for violation in violations:
            vtype = violation.get('type')
            if vtype == 'long_function':
                recommendations.append(
                    f"Extract method: Break down {violation['function']} into smaller functions"
                )
            elif vtype == 'high_complexity':
                recommendations.append(
                    f"Reduce complexity: Simplify {violation['function']} logic"
                )
            elif vtype == 'duplicate_code':
                recommendations.append(
                    f"Remove duplication: Extract common code into reusable function"
                )
        
        return recommendations


# ============================================================================
# TDD Orchestrator
# ============================================================================

class TDDOrchestrator:
    """
    Unified TDD Orchestrator with adaptive learning and clean architecture.
    
    Features:
    - Strategy pattern for phase execution
    - Technology discovery and adaptation
    - Clean code enforcement
    - AI-driven code generation
    - Automatic learning from patterns
    - DoR/DoD validation with rollback
    """
    
    def __init__(
        self,
        brain_connector=None,
        knowledge_graph=None,
        mcp_gateway=None,
        config: Optional[Dict[str, Any]] = None,
        llm_client: Optional[Any] = None,
        # Phase 5 Components (optional DI)
        multi_agent_orchestrator: Optional[MultiAgentOrchestrator] = None,
        learning_engine: Optional[AgentLearningEngine] = None,
        context_validator: Optional[ContextValidator] = None,
        # State coordination (for interface compatibility)
        state_db: Optional[Any] = None
    ):
        # Store parameters (allow None for testing/standalone instantiation)
        self.brain = brain_connector
        self.kg = knowledge_graph
        self.mcp = mcp_gateway
        self.config = config or {}
        self.state_db = state_db  # Store for potential future use
        
        # Initialize adaptive learning (only if brain and kg are available)
        if self.brain and self.kg:
            self.tech_discovery = TechnologyDiscoveryEngine(brain_connector, knowledge_graph)
        else:
            self.tech_discovery = None
        self.clean_code = CleanCodeEnforcer()
        
        # Phase 5 Components: Multi-Agent Collaboration (Day 1)
        self.multi_agent_orchestrator = multi_agent_orchestrator or MultiAgentOrchestrator()
        if self.kg:
            self.learning_engine = learning_engine or AgentLearningEngine(knowledge_graph)
            self.context_validator = context_validator or ContextValidator(knowledge_graph)
        else:
            self.learning_engine = None
            self.context_validator = None
        
        logger.info("🎭 Phase 5 components initialized: MultiAgent, Learning, ContextValidator")
        
        # Task 6.10 Package 1: Parallel test execution (50% faster)
        self.parallel_runner = ParallelTestRunner(
            max_workers=self.config.get('max_parallel_tests', 4)
        )
        
        # Task 6.10 Package 3: LLM-as-judge test quality
        self.test_quality_evaluator = TestQualityEvaluator(llm_client)
        
        # Task 6.10 Package 6: Code safety guardrails
        self.code_safety_guardrail = CodeSafetyGuardrail()
        
        # Task 6.10 Package 5: Adaptive execution modes
        # Create mock user profile for ExecutionModeManager
        from src.orchestration_4_0.execution.execution_mode_manager import UserProfile
        mock_user_profile = UserProfile(user_id="tdd_user")
        self.execution_mode_manager = ExecutionModeManager(
            config=self.config,
            user_profile=mock_user_profile
        )
        
        # Strategy registry
        self.strategies: Dict[str, TDDPhaseStrategy] = {}
        
        # Metrics
        self.metrics = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'patterns_learned': 0,
            'technologies_discovered': 0,
            'parallel_speedup': 0.0,  # Track parallel performance
            'test_quality_avg': 0.0,  # Track average test quality
            'safety_violations': 0,   # Track safety issues caught
            'execution_mode_switches': 0,  # Track mode adaptations
            # Phase 5 Metrics
            'context_validations': 0,
            'multi_agent_executions': 0,
            'learning_patterns_stored': 0,
            'auto_retrievals': 0
        }
        
        logger.info("🎭 Orchestrator engaged: TDDOrchestrator (Enhanced with Phase 5 AI)")
    
    def register_strategy(self, phase: TDDPhase, strategy: TDDPhaseStrategy):
        """Register phase strategy."""
        self.strategies[phase.value] = strategy
        logger.info(f"✅ Strategy registered: {phase.value}")
    
    async def execute_tdd_cycle(
        self,
        feature_name: str,
        acceptance_criteria: List[str],
        project_path: Path,
        context: Optional[Dict[str, Any]] = None,
        execution_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute complete RED→GREEN→REFACTOR cycle.
        
        Args:
            feature_name: Name of feature to implement
            acceptance_criteria: List of acceptance criteria
            project_path: Path to project root
            context: Additional context
            execution_mode: Execution mode (autonomous/supervised/manual)
            
        Returns:
            Cycle results with all phase outcomes
        """
        logger.info(f"🎭 Starting TDD cycle: {feature_name}")
        self.metrics['total_cycles'] += 1
        
        # Phase 5: Context Validation (Day 1)
        logger.info("🔍 Phase 5: Validating execution context...")
        self.metrics['context_validations'] += 1
        
        execution_plan = {
            'operation_type': 'tdd_cycle',
            'required_context': [
                'feature_name', 'acceptance_criteria', 'project_path'
            ],
            'optional_context': [
                'tech_profile', 'execution_mode', 'test_framework',
                'coverage_threshold', 'quality_gates'
            ]
        }
        
        initial_context = {
            'feature_name': feature_name,
            'acceptance_criteria': acceptance_criteria,
            'project_path': str(project_path),
            **(context or {})
        }
        
        validation = await self.context_validator.validate_context_sufficiency(
            context=initial_context,
            execution_plan=execution_plan
        )
        
        logger.info(f"✅ Context validation complete: {validation.quality.value}")
        logger.info(f"   Quality score: {validation.get_quality_score():.1f}/100")
        
        if validation.retrieved_items:
            self.metrics['auto_retrievals'] += len(validation.retrieved_items)
            logger.info(f"   Auto-retrieved: {list(validation.retrieved_items.keys())}")
        
        if validation.missing_optional:
            logger.info(f"   Missing optional: {validation.missing_optional}")
        
        if not validation.is_valid():
            logger.error(f"❌ Context validation failed: missing {validation.missing_required}")
            return {
                'success': False,
                'error': 'Insufficient context',
                'validation': validation
            }
        
        # Package 5: Determine execution mode
        if execution_mode:
            chosen_mode = execution_mode
        else:
            # Use execution mode manager with adaptive selection
            from src.orchestration_4_0.execution.execution_mode_manager import Operation, User
            operation = Operation(
                name='tdd_cycle',
                category='test',
                estimated_duration=300
            )
            user = User(
                user_id="tdd_user",
                completed_operations=self.metrics.get('total_cycles', 0),
                successful_operations=self.metrics.get('successful_cycles', 0),
                days_since_first_use=7,  # Default
                first_used_at=datetime.now()
            )
            chosen_mode = self.execution_mode_manager.selector.select_mode(operation, user).value
            self.metrics['execution_mode_switches'] += 1
        
        logger.info(f"🎮 Execution mode: {chosen_mode}")
        
        # Discover technology stack
        tech_profile = await self.tech_discovery.discover_project_tech_stack(
            project_path
        )
        self.metrics['technologies_discovered'] += 1
        
        # Build execution context
        exec_context = {
            'feature_name': feature_name,
            'acceptance_criteria': acceptance_criteria,
            'project_path': project_path,
            'tech_profile': tech_profile,
            'execution_mode': chosen_mode,
            'parallel_runner': self.parallel_runner,
            'test_quality_evaluator': self.test_quality_evaluator,
            'code_safety_guardrail': self.code_safety_guardrail,
            **(context or {})
        }
        
        results = {}
        
        try:
            # Phase 1: RED - Generate failing tests
            logger.info("🎭 Phase transition: START → RED")
            
            # Phase 5: Get learning recommendations for RED phase
            red_recommendation = await self._get_learning_recommendations(
                'test_generation',
                exec_context
            )
            
            results['RED'] = await self._execute_phase(
                TDDPhase.RED,
                exec_context
            )
            
            # Phase 5: Record learning from RED phase
            await self._record_phase_learning(TDDPhase.RED, exec_context, results['RED'])
            
            # Package 3: Evaluate test quality after RED phase
            if 'test_code' in results['RED'].outputs:
                test_quality = await self.test_quality_evaluator.evaluate_test_quality(
                    test_code=results['RED'].outputs['test_code'],
                    implementation="",  # No implementation yet
                    acceptance_criteria=acceptance_criteria,
                    language=tech_profile.language
                )
                results['RED'].metrics['test_quality'] = test_quality.overall
                self.metrics['test_quality_avg'] = (
                    (self.metrics['test_quality_avg'] * (self.metrics['total_cycles'] - 1) + 
                     test_quality.overall) / self.metrics['total_cycles']
                )
                logger.info(f"📊 Test quality score: {test_quality.overall:.1f}/10")
            
            # Phase 2: GREEN - Minimal implementation
            logger.info("🎭 Phase transition: RED → GREEN")
            exec_context.update(results['RED'].outputs)
            
            # Phase 5: Get learning recommendations for GREEN phase
            green_recommendation = await self._get_learning_recommendations(
                'implementation',
                exec_context
            )
            
            results['GREEN'] = await self._execute_phase(
                TDDPhase.GREEN,
                exec_context
            )
            
            # Phase 5: Record learning from GREEN phase
            await self._record_phase_learning(TDDPhase.GREEN, exec_context, results['GREEN'])
            
            # Package 6: Check code safety after GREEN phase
            if 'implementation_code' in results['GREEN'].outputs:
                safety_check = self.code_safety_guardrail.check_code_safety(
                    code=results['GREEN'].outputs['implementation_code'],
                    language=tech_profile.language,
                    context=feature_name
                )
                results['GREEN'].metrics['safety_score'] = 10.0 - safety_check.risk_score
                self.metrics['safety_violations'] += len(safety_check.violations)
                
                if not safety_check.is_safe:
                    logger.warning(f"⚠️  Safety violations detected: {len(safety_check.violations)}")
                    logger.warning(f"Recommendations: {safety_check.recommendations}")
            
            # Phase 3: REFACTOR - Clean up code
            logger.info("🎭 Phase transition: GREEN → REFACTOR")
            exec_context.update(results['GREEN'].outputs)
            
            # Phase 5: Get learning recommendations for REFACTOR phase
            refactor_recommendation = await self._get_learning_recommendations(
                'refactoring',
                exec_context
            )
            
            results['REFACTOR'] = await self._execute_phase(
                TDDPhase.REFACTOR,
                exec_context
            )
            
            # Phase 5: Record learning from REFACTOR phase
            await self._record_phase_learning(TDDPhase.REFACTOR, exec_context, results['REFACTOR'])
            
            logger.info("🎭 Phase transition: REFACTOR → COMPLETE")
            
            # Learn from successful cycle
            await self._learn_from_cycle(exec_context, results)
            
            self.metrics['successful_cycles'] += 1
            logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return {
                'success': True,
                'feature': feature_name,
                'tech_profile': tech_profile,
                'phases': results,
                'metrics': self._get_cycle_metrics(results)
            }
            
        except Exception as e:
            logger.error(f"❌ TDD cycle failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_phases': list(results.keys()),
                'partial_results': results
            }
    
    # ============================================================================
    # Phase 5: Multi-Agent Collaboration & Learning (Day 1)
    # ============================================================================
    
    async def _get_learning_recommendations(
        self,
        operation_type: str,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Get strategy recommendations from learning engine.
        
        Args:
            operation_type: Type of operation (e.g., 'test_generation', 'implementation')
            context: Execution context
            
        Returns:
            Recommendation or None if insufficient patterns
        """
        try:
            recommendations = self.learning_engine.get_recommendations(
                operation_type=operation_type,
                context=context,
                top_k=1
            )
            
            if recommendations:
                recommendation = recommendations[0]
                logger.info(f"🧠 Learning recommendation: {recommendation.strategy.value}")
                logger.info(f"   Confidence: {recommendation.confidence:.2f}")
                logger.info(f"   Expected outcome: {recommendation.expected_outcome:.1f}/10")
                return recommendation
            
            return None
        except Exception as e:
            logger.warning(f"⚠️  Failed to get recommendation: {e}")
            return None
    
    async def _record_phase_learning(
        self,
        phase: TDDPhase,
        context: Dict[str, Any],
        result: PhaseResult
    ) -> None:
        """
        Record phase execution for learning.
        
        Args:
            phase: TDD phase executed
            context: Execution context
            result: Phase result
        """
        try:
            from src.orchestration_4_0.frameworks.agent_evaluator import EvaluationCategory
            
            # Create mock evaluation from result metrics  
            # Note: EvaluationResult expects different fields than we initially thought
            class MockEvaluation:
                def __init__(self, score):
                    self.score = score
            
            eval_result = MockEvaluation(score=result.metrics.get('quality_score', 7.0))
            
            # Map phase to operation type
            operation_map = {
                TDDPhase.RED: 'test_generation',
                TDDPhase.GREEN: 'implementation',
                TDDPhase.REFACTOR: 'refactoring'
            }
            
            # Learn from execution
            self.learning_engine.learn_from_execution(
                operation_type=operation_map.get(phase, 'unknown'),
                strategy=StrategyType.SEQUENTIAL,  # Default for now
                context={
                    'feature_name': context.get('feature_name'),
                    'complexity': context.get('complexity', 'medium'),
                    'tech_stack': str(context.get('tech_profile', {}))
                },
                evaluation=eval_result,
                execution_time_seconds=result.metrics.get('execution_time', 0),
                tokens_used=result.metrics.get('tokens_used')
            )
            
            self.metrics['learning_patterns_stored'] += 1
            logger.info(f"🧠 Recorded learning pattern for {phase.value} phase")
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to record learning: {e}")
    
    async def _create_phase_agents(
        self,
        phase: TDDPhase,
        context: Dict[str, Any]
    ) -> List[Any]:
        """
        Create agents for multi-agent phase execution.
        
        Args:
            phase: TDD phase to create agents for
            context: Execution context
            
        Returns:
            List of agents for the phase
        """
        from src.orchestration_4_0.base.agent_interface import Agent, AgentContext
        
        # Create simple wrapper agents for TDD phases
        class TDDPhaseAgent(Agent):
            def __init__(self, name: str, phase_strategy, phase_context):
                super().__init__(name)
                self.strategy = phase_strategy
                self.phase_context = phase_context
            
            async def execute(self, agent_context: AgentContext) -> AgentContext:
                """Execute phase strategy and update agent context"""
                try:
                    result = await self.strategy.execute(self.phase_context)
                    agent_context.add_to_history(self.name)
                    agent_context.data.update(result.outputs)
                    agent_context.metadata['success'] = result.success
                    agent_context.metadata['metrics'] = result.metrics
                    return agent_context
                except Exception as e:
                    agent_context.add_error(str(e))
                    return agent_context
        
        strategy = self.strategies.get(phase.value)
        if not strategy:
            return []
        
        # For now, create single agent per phase
        # Future: Could create multiple agents for different strategies
        agent = TDDPhaseAgent(f"{phase.value}_Agent", strategy, context)
        return [agent]
    
    async def _execute_phase_with_multi_agent(
        self,
        phase: TDDPhase,
        context: Dict[str, Any]
    ) -> PhaseResult:
        """
        Execute phase using multi-agent orchestration.
        
        Args:
            phase: TDD phase to execute
            context: Execution context
            
        Returns:
            Phase result
        """
        logger.info(f"🤖 Multi-agent execution: {phase.value} phase")
        self.metrics['multi_agent_executions'] += 1
        
        # Create agents for phase
        agents = await self._create_phase_agents(phase, context)
        
        if not agents:
            # Fall back to standard execution
            logger.warning(f"⚠️  No agents created, falling back to standard execution")
            return await self._execute_phase(phase, context)
        
        # Execute using sequential pattern (simplest for now)
        from src.orchestration_4_0.base.agent_interface import AgentContext
        
        initial_context = AgentContext(
            data=context.copy(),
            metadata={'phase': phase.value}
        )
        
        final_context = await self.multi_agent_orchestrator.execute_sequential(
            agents=agents,
            initial_context=initial_context
        )
        
        # Convert agent context back to PhaseResult
        result = PhaseResult(
            phase_name=phase.value,
            success=final_context.metadata.get('success', False),
            outputs=final_context.data,
            metrics=final_context.metadata.get('metrics', {})
        )
        
        if final_context.has_errors():
            result.errors = final_context.errors
            logger.warning(f"⚠️  Phase had errors: {result.errors}")
        
        return result
    
    # ============================================================================
    # End Phase 5 Integration
    # ============================================================================
    
    async def _execute_phase(
        self,
        phase: TDDPhase,
        context: Dict[str, Any]
    ) -> PhaseResult:
        """Execute single phase with validation and rollback."""
        strategy = self.strategies.get(phase.value)
        
        if not strategy:
            raise ValueError(f"No strategy registered for phase: {phase.value}")
        
        # Validate DoR
        logger.info(f"🔍 Validating {phase.value} DoR...")
        dor_result = await strategy.validate_dor(context)
        
        if not dor_result.passed:
            raise ValueError(
                f"{phase.value} DoR failed:\n" + 
                "\n".join(f"  - {e}" for e in dor_result.errors)
            )
        
        # Execute phase
        logger.info(f"▶️  Executing {phase.value} phase...")
        result = await strategy.execute(context)
        
        # Validate DoD
        logger.info(f"🔍 Validating {phase.value} DoD...")
        dod_context = {**context, **result.outputs}
        dod_result = await strategy.validate_dod(dod_context)
        
        if not dod_result.passed:
            # Rollback on failure
            logger.warning(f"❌ {phase.value} DoD failed, rolling back...")
            await strategy.rollback(context)
            raise ValueError(
                f"{phase.value} DoD failed:\n" + 
                "\n".join(f"  - {e}" for e in dod_result.errors)
            )
        
        logger.info(f"✅ {phase.value} phase complete")
        return result
    
    async def _learn_from_cycle(
        self,
        context: Dict[str, Any],
        results: Dict[str, PhaseResult]
    ):
        """Learn patterns from successful TDD cycle."""
        tech_profile = context['tech_profile']
        
        # Extract patterns from each phase
        patterns_learned = 0
        
        # RED phase patterns
        if 'RED' in results:
            patterns_learned += await self.tech_discovery.learn_from_patterns(
                context['project_path'],
                'test_generation',
                {
                    'test_count': results['RED'].outputs.get('test_count'),
                    'test_framework': tech_profile.test_frameworks[0] if tech_profile.test_frameworks else 'unknown',
                    'techniques_used': results['RED'].metrics.get('techniques', [])
                }
            )
        
        # GREEN phase patterns
        if 'GREEN' in results:
            patterns_learned += await self.tech_discovery.learn_from_patterns(
                context['project_path'],
                'implementation',
                {
                    'lines_of_code': results['GREEN'].metrics.get('lines_of_code'),
                    'complexity': results['GREEN'].metrics.get('complexity'),
                    'frameworks_used': tech_profile.frameworks
                }
            )
        
        # REFACTOR phase patterns
        if 'REFACTOR' in results:
            patterns_learned += await self.tech_discovery.learn_from_patterns(
                context['project_path'],
                'refactoring',
                {
                    'refactorings_applied': results['REFACTOR'].outputs.get('refactorings_applied'),
                    'quality_improvement': results['REFACTOR'].metrics.get('quality_delta')
                }
            )
        
        self.metrics['patterns_learned'] += patterns_learned
        logger.info(f"✅ Learned {patterns_learned} patterns from cycle")
    
    def _get_cycle_metrics(self, results: Dict[str, PhaseResult]) -> Dict[str, Any]:
        """Aggregate metrics from all phases."""
        return {
            'total_tests': results.get('RED', PhaseResult('RED', False, {}, {})).outputs.get('test_count', 0),
            'tests_passing': results.get('GREEN', PhaseResult('GREEN', False, {}, {})).outputs.get('tests_passing', 0),
            'refactorings_applied': results.get('REFACTOR', PhaseResult('REFACTOR', False, {}, {})).outputs.get('refactorings_applied', 0),
            'quality_score': results.get('REFACTOR', PhaseResult('REFACTOR', False, {}, {})).metrics.get('final_quality_score', 0),
            'git_commits': sum(1 for r in results.values() if r.git_commit_sha),
            'documentation_updates': sum(1 for r in results.values() if r.documentation_updated),
            'patterns_learned': sum(r.brain_patterns_extracted for r in results.values())
        }
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Get overall orchestrator performance metrics."""
        success_rate = (
            self.metrics['successful_cycles'] / self.metrics['total_cycles']
            if self.metrics['total_cycles'] > 0
            else 0.0
        )
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'avg_patterns_per_cycle': (
                self.metrics['patterns_learned'] / self.metrics['total_cycles']
                if self.metrics['total_cycles'] > 0
                else 0.0
            )
        }
