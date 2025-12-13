"""
Narrative Orchestrator - Coordinates all 7 narrative engines

Transforms technical code analysis into business-focused narratives
that product owners, leadership, and non-technical stakeholders can
understand without reading code.

Usage:
    >>> orchestrator = NarrativeOrchestrator()
    >>> narratives = orchestrator.generate_all(analysis_data)
    >>> # narratives contains: use_cases, problem_domain, business_flows,
    >>> # stakeholders, competitive_position, risks, evolution

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class NarrativeResult:
    """Container for all generated narratives."""
    use_cases: List[Dict[str, Any]] = field(default_factory=list)
    problem_domain: Dict[str, Any] = field(default_factory=dict)
    business_flows: List[Dict[str, Any]] = field(default_factory=list)
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)
    competitive_position: Dict[str, Any] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    evolution: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NarrativeOrchestrator:
    """
    Orchestrates all 7 narrative engines to transform code into business stories.
    
    This is the main entry point for narrative generation. It coordinates:
    1. Use Case Discovery - Extract workflows from endpoints/routes
    2. Problem Domain - Synthesize what problem the app solves
    3. Business Flows - Map technical calls to business processes
    4. Stakeholder Analysis - Identify who uses the app
    5. Competitive Position - Highlight technical advantages
    6. Risk Storytelling - Translate tech debt to business impact
    7. Evolution Story - Track transformation over time
    
    Example:
        >>> orchestrator = NarrativeOrchestrator()
        >>> analysis = {
        ...     'api_endpoints': [...],
        ...     'architecture': {...},
        ...     'tech_stack': {...},
        ...     'complexity': {...}
        ... }
        >>> narratives = orchestrator.generate_all(analysis)
        >>> print(narratives.use_cases[0]['title'])
        'Employee Reimbursement Submission'
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize narrative orchestrator with optional configuration.
        
        Args:
            config: Optional configuration for narrative generation
                   Can include: style preferences, length limits, audience level
        """
        self.config = config or {}
        self._engines = {}
        logger.info("🎭 NarrativeOrchestrator initialized")
    
    def generate_all(
        self,
        analysis_data: Dict[str, Any],
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> NarrativeResult:
        """
        Generate all 7 types of narratives from analysis data.
        
        Args:
            analysis_data: Complete analysis from CORTEX Lens collectors
            previous_analysis: Optional previous analysis for evolution narrative
        
        Returns:
            NarrativeResult containing all generated narratives
        """
        logger.info("🎭 Generating business narratives from code analysis")
        
        result = NarrativeResult()
        result.metadata = {
            'generated_at': datetime.now().isoformat(),
            'cortex_lens_version': '1.0.0',
            'analysis_quality': self._assess_data_quality(analysis_data)
        }
        
        try:
            # 1. Use Case Discovery
            logger.info("📋 Discovering use cases from endpoints and routes")
            result.use_cases = self._generate_use_cases(analysis_data)
            
            # 2. Problem Domain
            logger.info("🎯 Synthesizing problem domain narrative")
            result.problem_domain = self._generate_problem_domain(analysis_data)
            
            # 3. Business Flows
            logger.info("🔄 Mapping business flows from call chains")
            result.business_flows = self._generate_business_flows(analysis_data)
            
            # 4. Stakeholder Analysis
            logger.info("👥 Analyzing stakeholders and impact")
            result.stakeholders = self._generate_stakeholders(analysis_data)
            
            # 5. Competitive Position
            logger.info("🏆 Highlighting competitive advantages")
            result.competitive_position = self._generate_competitive_position(analysis_data)
            
            # 6. Risk Storytelling
            logger.info("⚠️ Translating technical risks to business impact")
            result.risks = self._generate_risks(analysis_data)
            
            # 7. Evolution Story (if previous data available)
            if previous_analysis:
                logger.info("📈 Generating evolution narrative")
                result.evolution = self._generate_evolution(analysis_data, previous_analysis)
            
            logger.info(f"✅ Generated {self._count_narratives(result)} narratives")
            
        except Exception as e:
            logger.error(f"❌ Narrative generation failed: {e}", exc_info=True)
            result.metadata['error'] = str(e)
        
        return result
    
    def _generate_use_cases(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate use case narratives from API endpoints and routes."""
        from .use_case_discoverer import UseCaseDiscoverer
        
        if 'use_case_discoverer' not in self._engines:
            self._engines['use_case_discoverer'] = UseCaseDiscoverer(self.config)
        
        return self._engines['use_case_discoverer'].discover(data)
    
    def _generate_problem_domain(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate problem domain narrative from comments and entities."""
        from .problem_domain_narrator import ProblemDomainNarrator
        
        if 'problem_domain' not in self._engines:
            self._engines['problem_domain'] = ProblemDomainNarrator(self.config)
        
        return self._engines['problem_domain'].narrate(data)
    
    def _generate_business_flows(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business flow narratives from call chains."""
        from .business_flow_mapper import BusinessFlowMapper
        
        if 'business_flow' not in self._engines:
            self._engines['business_flow'] = BusinessFlowMapper(self.config)
        
        return self._engines['business_flow'].map_flows(data)
    
    def _generate_stakeholders(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate stakeholder analysis from auth patterns and permissions."""
        from .stakeholder_analyzer import StakeholderAnalyzer
        
        if 'stakeholder' not in self._engines:
            self._engines['stakeholder'] = StakeholderAnalyzer(self.config)
        
        return self._engines['stakeholder'].analyze(data)
    
    def _generate_competitive_position(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate competitive positioning from tech stack and architecture."""
        from .competitive_position_narrator import CompetitivePositionNarrator
        
        if 'competitive' not in self._engines:
            self._engines['competitive'] = CompetitivePositionNarrator(self.config)
        
        return self._engines['competitive'].narrate(data)
    
    def _generate_risks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk narratives from complexity and security findings."""
        from .risk_narrator import RiskNarrator
        
        if 'risk' not in self._engines:
            self._engines['risk'] = RiskNarrator(self.config)
        
        return self._engines['risk'].narrate_risks(data)
    
    def _generate_evolution(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate evolution narrative comparing current vs previous analysis."""
        from .evolution_narrator import EvolutionNarrator
        
        if 'evolution' not in self._engines:
            self._engines['evolution'] = EvolutionNarrator(self.config)
        
        return self._engines['evolution'].tell_story(current, previous)
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Assess the quality of input data for narrative generation.
        
        Returns quality scores for different aspects:
        - endpoints: HIGH/MEDIUM/LOW/NONE
        - comments: HIGH/MEDIUM/LOW/NONE
        - architecture: HIGH/MEDIUM/LOW/NONE
        - tech_stack: HIGH/MEDIUM/LOW/NONE
        """
        quality = {}
        
        # Check API endpoints
        endpoints = data.get('api_endpoints', {}).get('endpoints', [])
        quality['endpoints'] = (
            'HIGH' if len(endpoints) > 10 else
            'MEDIUM' if len(endpoints) > 3 else
            'LOW' if endpoints else 'NONE'
        )
        
        # Check comments
        comments = data.get('comments', {}).get('total_comments', 0)
        quality['comments'] = (
            'HIGH' if comments > 100 else
            'MEDIUM' if comments > 20 else
            'LOW' if comments > 0 else 'NONE'
        )
        
        # Check architecture data
        architecture = data.get('architecture', {})
        quality['architecture'] = (
            'HIGH' if architecture.get('layers') else
            'MEDIUM' if architecture.get('patterns') else 'NONE'
        )
        
        # Check tech stack
        tech_stack = data.get('tech_stack', {})
        quality['tech_stack'] = (
            'HIGH' if tech_stack.get('languages') else 'NONE'
        )
        
        return quality
    
    def _count_narratives(self, result: NarrativeResult) -> int:
        """Count total narratives generated."""
        return (
            len(result.use_cases) +
            (1 if result.problem_domain else 0) +
            len(result.business_flows) +
            len(result.stakeholders) +
            (1 if result.competitive_position else 0) +
            len(result.risks) +
            (1 if result.evolution else 0)
        )
