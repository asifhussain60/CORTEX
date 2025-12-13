"""
CORTEX Lens Narrative Generators

Transform technical code analysis into business-focused narratives that
non-technical stakeholders can understand and act upon.

7 Narrative Engines:
    1. UseCaseDiscoverer - Extract business workflows from code
    2. ProblemDomainNarrator - Explain what problem the app solves
    3. BusinessFlowMapper - Map code to business processes
    4. StakeholderAnalyzer - Identify who uses the app and how
    5. CompetitivePositionNarrator - Highlight technical advantages
    6. RiskNarrator - Translate technical debt to business impact
    7. EvolutionNarrator - Tell the transformation story over time

Example:
    >>> from cortex_lens.narratives import NarrativeOrchestrator
    >>> orchestrator = NarrativeOrchestrator()
    >>> narratives = orchestrator.generate_all(analysis_data)
    >>> print(narratives['use_cases'])

Author: Asif Hussain
Version: 1.0.0
"""

__all__ = [
    'NarrativeOrchestrator',
    'UseCaseDiscoverer',
    'ProblemDomainNarrator',
    'BusinessFlowMapper',
    'StakeholderAnalyzer',
    'CompetitivePositionNarrator',
    'RiskNarrator',
    'EvolutionNarrator',
]

def __getattr__(name):
    """Lazy import narrative engines."""
    if name == 'NarrativeOrchestrator':
        from .orchestrator import NarrativeOrchestrator
        return NarrativeOrchestrator
    elif name == 'UseCaseDiscoverer':
        from .use_case_discoverer import UseCaseDiscoverer
        return UseCaseDiscoverer
    elif name == 'ProblemDomainNarrator':
        from .problem_domain_narrator import ProblemDomainNarrator
        return ProblemDomainNarrator
    elif name == 'BusinessFlowMapper':
        from .business_flow_mapper import BusinessFlowMapper
        return BusinessFlowMapper
    elif name == 'StakeholderAnalyzer':
        from .stakeholder_analyzer import StakeholderAnalyzer
        return StakeholderAnalyzer
    elif name == 'CompetitivePositionNarrator':
        from .competitive_position_narrator import CompetitivePositionNarrator
        return CompetitivePositionNarrator
    elif name == 'RiskNarrator':
        from .risk_narrator import RiskNarrator
        return RiskNarrator
    elif name == 'EvolutionNarrator':
        from .evolution_narrator import EvolutionNarrator
        return EvolutionNarrator
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
