"""
Generate Missing MCP Adapters (Phase 2B)

Generates adapter implementations for 16 unwired orchestrators.
Uses template pattern from existing adapters.

AC-ID: AC-PHASE2B-001
"""

import os
from pathlib import Path
from typing import Dict, List

# Template for adapter generation
ADAPTER_TEMPLATE = '''"""
{description}

Generated adapter for {orchestrator_name}.
AC-ID: AC-PHASE2B-{adapter_id}
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from {module_path} import {class_name}
import logging
import time

logger = logging.getLogger(__name__)


def _get_orchestrator_from_wiring(name: str) -> Optional[Any]:
    """Get orchestrator from wiring system (CORE-035: Single execution path)."""
    try:
        from cortex.wiring import bootstrap_cortex
        registry = bootstrap_cortex()
        return registry.get_orchestrator(name)
    except Exception as e:
        logger.warning(f"Failed to get {{name}} from wiring: {{e}}")
        return None


class {adapter_class_name}(IOrchestratorAdapter):
    """
    MCP Adapter for {orchestrator_name}.
    
    Exposes capabilities:
{capability_list}
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[{class_name}] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("{orchestrator_name}")
        self.name = "{adapter_class_name}"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
{capabilities_metadata}
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> CapabilityResponse:
        """Execute a capability."""
        start = time.time()
        try:
            if not self.orchestrator:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error="Orchestrator not available",
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            
{execution_logic}
            
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=f"Unknown capability: {{capability_name}}",
                orchestrator="{orchestrator_name_lower}",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {{capability_name}}: {{e}}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="{orchestrator_name_lower}",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
'''

# Orchestrator definitions with inferred capabilities
ORCHESTRATORS = [
    {
        'name': 'PhaseExecutor',
        'class': 'PhaseExecutor',
        'module': 'cortex.orchestrators.domain.phase_executor',
        'category': 'domain',
        'capabilities': [
            ('execute_phase', 'Execute a plan phase', ['phase_id', 'context']),
            ('get_phase_status', 'Get phase execution status', ['phase_id']),
        ],
    },
    {
        'name': 'AutonomousExecutionEngine',
        'class': 'AutonomousExecutionEngine',
        'module': 'cortex.orchestrators.domain.autonomous_execution_engine',
        'category': 'domain',
        'capabilities': [
            ('execute_autonomous', 'Execute autonomous operation', ['task', 'constraints']),
            ('get_execution_plan', 'Generate execution plan', ['objective']),
        ],
    },
    {
        'name': 'OrchestratorEventBus',
        'class': 'OrchestratorEventBus',
        'module': 'cortex.infrastructure.orchestrator_event_bus',
        'category': 'support',
        'capabilities': [
            ('publish_event', 'Publish event to bus', ['event_type', 'data']),
            ('subscribe', 'Subscribe to events', ['event_type', 'handler']),
            ('get_event_history', 'Get event history', ['filters']),
        ],
    },
    {
        'name': 'InteractionOrchestratorEnhancement',
        'class': 'InteractionOrchestratorEnhancement',
        'module': 'cortex.orchestrators.core.interaction_orchestrator_enhancement',
        'category': 'core',
        'capabilities': [
            ('enhance_interaction', 'Enhance user interaction', ['interaction_data']),
            ('analyze_patterns', 'Analyze interaction patterns', ['session_id']),
        ],
    },
    {
        'name': 'FuzzyIntentMatcher',
        'class': 'FuzzyIntentMatcher',
        'module': 'cortex.orchestrators.core.fuzzy_intent_matcher',
        'category': 'core',
        'capabilities': [
            ('match_intent', 'Fuzzy match user intent', ['query', 'threshold']),
            ('get_suggestions', 'Get intent suggestions', ['partial_query']),
        ],
    },
    {
        'name': 'ComprehensionSession',
        'class': 'ComprehensionSession',
        'module': 'cortex.orchestrators.core.comprehension_session',
        'category': 'core',
        'capabilities': [
            ('start_session', 'Start comprehension session', ['context']),
            ('track_understanding', 'Track user understanding', ['session_id', 'metrics']),
        ],
    },
    {
        'name': 'DoRApprovalGate',
        'class': 'DoRApprovalGate',
        'module': 'cortex.orchestrators.core.dor_approval_gate',
        'category': 'core',
        'capabilities': [
            ('check_readiness', 'Check Definition of Ready', ['request_data']),
            ('get_dor_status', 'Get DoR approval status', ['request_id']),
        ],
    },
    {
        'name': 'ChallengeEngine',
        'class': 'ChallengeEngine',
        'module': 'cortex.orchestrators.core.challenge_engine',
        'category': 'core',
        'capabilities': [
            ('generate_challenge', 'Generate design challenge', ['design_data']),
            ('evaluate_response', 'Evaluate challenge response', ['challenge_id', 'response']),
        ],
    },
    {
        'name': 'EducationalOrchestrator',
        'class': 'EducationalOrchestrator',
        'module': 'cortex.orchestrators.education.educational_orchestrator',
        'category': 'domain',
        'capabilities': [
            ('provide_guidance', 'Provide educational guidance', ['topic', 'level']),
            ('assess_understanding', 'Assess user understanding', ['topic', 'responses']),
        ],
    },
    {
        'name': 'DuplicationDetector',
        'class': 'DuplicationDetectorOrchestrator',
        'module': 'cortex.orchestrators.support.duplication_detector_orchestrator',
        'category': 'support',
        'capabilities': [
            ('detect_duplicates', 'Detect code duplications', ['file_paths']),
            ('get_duplication_report', 'Get duplication report', ['scope']),
        ],
    },
    {
        'name': 'RecommendationGate',
        'class': 'RecommendationGate',
        'module': 'cortex.orchestrators.core.recommendation_gate',
        'category': 'core',
        'capabilities': [
            ('validate_recommendation', 'Validate recommendation safety', ['recommendation']),
            ('check_rejection_history', 'Check rejection history', ['recommendation_id']),
        ],
    },
    {
        'name': 'VacuumOrchestrator',
        'class': 'VacuumOrchestrator',
        'module': 'cortex.orchestrators.support.vacuum_orchestrator',
        'category': 'support',
        'capabilities': [
            ('vacuum_artifacts', 'Clean up generated artifacts', ['scope']),
            ('get_cleanup_report', 'Get cleanup report', ['session_id']),
        ],
    },
    {
        'name': 'InstrumentationOrchestrator',
        'class': 'InstrumentationOrchestrator',
        'module': 'cortex.orchestrators.support.instrumentation_orchestrator',
        'category': 'support',
        'capabilities': [
            ('instrument_code', 'Add instrumentation to code', ['file_path', 'config']),
            ('collect_metrics', 'Collect instrumentation metrics', ['scope']),
        ],
    },
    {
        'name': 'DebuggingOrchestrator',
        'class': 'DebuggingOrchestrator',
        'module': 'cortex.orchestrators.support.debugging_orchestrator',
        'category': 'support',
        'capabilities': [
            ('inject_debug_markers', 'Inject debug markers', ['file_path', 'strategy']),
            ('analyze_debug_output', 'Analyze debug output', ['markers']),
        ],
    },
    {
        'name': 'OrchestratorVisibility',
        'class': 'OrchestratorVisibility',
        'module': 'cortex.orchestrators.support.orchestrator_visibility',
        'category': 'support',
        'capabilities': [
            ('get_visibility_report', 'Get orchestrator visibility report', ['scope']),
            ('track_usage', 'Track orchestrator usage', ['orchestrator_name']),
        ],
    },
    {
        'name': 'DigestEnhancementOrchestrator',
        'class': 'DigestEnhancementOrchestrator',
        'module': 'cortex.orchestrators.learning.digest_enhancement_orchestrator',
        'category': 'support',
        'capabilities': [
            ('digest_session', 'Digest session learnings', ['session_data']),
            ('extract_patterns', 'Extract learning patterns', ['digest_id']),
        ],
    },
]


def generate_capability_metadata(capability: tuple) -> str:
    """Generate CapabilityMetadata code."""
    name, description, params = capability
    param_schema = {p: {"type": "string", "description": f"{p} parameter"} for p in params}
    
    return f'''            CapabilityMetadata(
                name="{name}",
                orchestrator="{name.split('_')[0]}",
                description="{description}",
                input_schema={param_schema},
                output_schema={{"status": {{"type": "string"}}, "result": {{"type": "object"}}}},
                routing_keywords=["{name}", "{name.replace('_', ' ')}"],
                tags={{"generated", "phase2b"}},
            )'''


def generate_execution_logic(capabilities: List[tuple]) -> str:
    """Generate execution logic for capabilities."""
    logic_parts = []
    for i, (name, desc, params) in enumerate(capabilities):
        if_clause = "if" if i == 0 else "elif"
        param_access = ", ".join([f"{p}=parameters.get('{p}')" for p in params])
        
        logic = f'''            {if_clause} capability_name == "{name}":
                result = self.orchestrator.{name}({param_access})
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{{orchestrator_name_lower}}",
                    duration_ms=(time.time() - start) * 1000,
                )'''
        logic_parts.append(logic)
    
    return "\n".join(logic_parts)


def generate_adapter(orchestrator: Dict, adapter_id: int) -> str:
    """Generate adapter code for an orchestrator."""
    capabilities = orchestrator['capabilities']
    
    # Generate capability list for docstring
    capability_list = "\n".join([f"    - {name}: {desc}" for name, desc, _ in capabilities])
    
    # Generate capabilities metadata
    capabilities_metadata = ",\n".join([generate_capability_metadata(cap) for cap in capabilities])
    
    # Generate execution logic
    execution_logic = generate_execution_logic(capabilities)
    
    return ADAPTER_TEMPLATE.format(
        description=f"MCP Adapter for {orchestrator['name']}",
        orchestrator_name=orchestrator['name'],
        adapter_id=f"{adapter_id:03d}",
        module_path=orchestrator['module'],
        class_name=orchestrator['class'],
        adapter_class_name=f"{orchestrator['name']}Adapter",
        capability_list=capability_list,
        capabilities_metadata=capabilities_metadata,
        execution_logic=execution_logic,
        orchestrator_name_lower=orchestrator['name'].lower(),
    )


def main():
    """Generate all missing adapters."""
    output_dir = Path("cortex/mcp/adapters/generated")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Generating 16 missing MCP adapters...\n")
    
    for i, orch in enumerate(ORCHESTRATORS, 1):
        adapter_code = generate_adapter(orch, i)
        filename = f"{orch['name'].lower()}_adapter.py"
        output_path = output_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(adapter_code)
        
        print(f"  ✅ {i:2d}. {orch['name']:35s} → {filename}")
    
    # Generate __init__.py for the package
    init_content = '''"""
Generated MCP Adapters (Phase 2B)

Auto-generated adapters for unwired orchestrators.
"""

from .phaseexecutor_adapter import PhaseExecutorAdapter
from .autonomousexecutionengine_adapter import AutonomousExecutionEngineAdapter
from .orchestratoreventbus_adapter import OrchestratorEventBusAdapter
from .interactionorchestratorenhancement_adapter import InteractionOrchestratorEnhancementAdapter
from .fuzzyintentmatcher_adapter import FuzzyIntentMatcherAdapter
from .comprehensionsession_adapter import ComprehensionSessionAdapter
from .dorapprovalgate_adapter import DoRApprovalGateAdapter
from .challengeengine_adapter import ChallengeEngineAdapter
from .educationalorchestrator_adapter import EducationalOrchestratorAdapter
from .duplicationdetector_adapter import DuplicationDetectorAdapter
from .recommendationgate_adapter import RecommendationGateAdapter
from .vacuumorchestrator_adapter import VacuumOrchestratorAdapter
from .instrumentationorchestrator_adapter import InstrumentationOrchestratorAdapter
from .debuggingorchestrator_adapter import DebuggingOrchestratorAdapter
from .orchestratorvisibility_adapter import OrchestratorVisibilityAdapter
from .digestenhancementorchestrator_adapter import DigestEnhancementOrchestratorAdapter

__all__ = [
    "PhaseExecutorAdapter",
    "AutonomousExecutionEngineAdapter",
    "OrchestratorEventBusAdapter",
    "InteractionOrchestratorEnhancementAdapter",
    "FuzzyIntentMatcherAdapter",
    "ComprehensionSessionAdapter",
    "DoRApprovalGateAdapter",
    "ChallengeEngineAdapter",
    "EducationalOrchestratorAdapter",
    "DuplicationDetectorAdapter",
    "RecommendationGateAdapter",
    "VacuumOrchestratorAdapter",
    "InstrumentationOrchestratorAdapter",
    "DebuggingOrchestratorAdapter",
    "OrchestratorVisibilityAdapter",
    "DigestEnhancementOrchestratorAdapter",
]
'''
    
    init_path = output_dir / "__init__.py"
    with open(init_path, 'w') as f:
        f.write(init_content)
    
    print(f"\n✅ Generated {len(ORCHESTRATORS)} adapters in {output_dir}/")
    print(f"✅ Created {init_path}")


if __name__ == "__main__":
    main()
