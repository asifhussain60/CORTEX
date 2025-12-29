"""
Competitive Position Narrator - Highlight technical advantages in business terms

Translates tech stack and architecture choices into competitive advantages
that sales teams and leadership can articulate.

Example:
    Input: React 18, .NET 8, microservices, Docker
    Output: "Modern cloud-native architecture provides 10x faster deployment vs
            legacy competitors, enabling rapid feature delivery and 99.9% uptime"

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class CompetitivePositionNarrator:
    """Narrates competitive advantages from technical choices."""
    
    # Technology advantage mappings
    TECH_ADVANTAGES = {
        'react': {'advantage': 'Modern UI', 'business_value': 'Superior user experience'},
        'microservices': {'advantage': 'Scalable architecture', 'business_value': 'Handles 10x growth without redesign'},
        'docker': {'advantage': 'Cloud-native deployment', 'business_value': 'Deploy updates in minutes vs hours'},
        'postgresql': {'advantage': 'Enterprise database', 'business_value': 'Data integrity and performance'},
        'typescript': {'advantage': 'Type-safe code', 'business_value': 'Fewer production bugs'},
        'pytest': {'advantage': 'Comprehensive testing', 'business_value': '99%+ reliability'}
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize competitive position narrator."""
        self.config = config or {}
        logger.info("🏆 CompetitivePositionNarrator initialized")
    
    def narrate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate competitive positioning narrative.
        
        Args:
            analysis_data: Complete analysis with tech_stack, architecture
        
        Returns:
            Dictionary with competitive advantages and business value
        """
        logger.info("🏆 Generating competitive positioning narrative")
        
        tech_stack = analysis_data.get('tech_stack', {})
        architecture = analysis_data.get('architecture', {})
        
        # Extract advantages
        advantages = self._identify_advantages(tech_stack, architecture)
        
        narrative = {
            'summary': self._generate_summary(advantages),
            'key_advantages': advantages,
            'technology_highlights': self._extract_tech_highlights(tech_stack),
            'architecture_strengths': self._extract_architecture_strengths(architecture),
            'business_value_proposition': self._generate_value_proposition(advantages)
        }
        
        logger.info(f"✅ Identified {len(advantages)} competitive advantages")
        return narrative
    
    def _identify_advantages(
        self,
        tech_stack: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify technical advantages with business value."""
        advantages = []
        
        # Check tech stack for modern technologies
        frameworks = tech_stack.get('frameworks', [])
        for framework in frameworks:
            fw_lower = framework.lower()
            for tech_key, advantage_info in self.TECH_ADVANTAGES.items():
                if tech_key in fw_lower:
                    advantages.append({
                        'technology': framework,
                        'advantage': advantage_info['advantage'],
                        'business_value': advantage_info['business_value']
                    })
        
        # Check architecture patterns
        patterns = architecture.get('patterns', [])
        if 'microservices' in [p.lower() for p in patterns]:
            advantages.append({
                'technology': 'Microservices Architecture',
                'advantage': 'Independent service scaling',
                'business_value': 'Cost-effective scaling, faster feature delivery'
            })
        
        return advantages
    
    def _generate_summary(self, advantages: List[Dict[str, str]]) -> str:
        """Generate executive summary of competitive position."""
        if not advantages:
            return "Modern technology platform with solid architecture"
        
        count = len(advantages)
        return f"Application leverages {count} key technological advantages providing competitive differentiation"
    
    def _extract_tech_highlights(self, tech_stack: Dict[str, Any]) -> List[str]:
        """Extract technology highlights."""
        highlights = []
        
        languages = tech_stack.get('languages', [])
        if languages:
            highlights.append(f"Multi-language: {', '.join(languages[:3])}")
        
        frameworks = tech_stack.get('frameworks', [])
        if frameworks:
            highlights.append(f"Modern frameworks: {', '.join(frameworks[:3])}")
        
        return highlights
    
    def _extract_architecture_strengths(self, architecture: Dict[str, Any]) -> List[str]:
        """Extract architecture strengths."""
        strengths = []
        
        layers = architecture.get('layers', [])
        if len(layers) >= 3:
            strengths.append(f"Layered architecture ({len(layers)} layers) ensures separation of concerns")
        
        patterns = architecture.get('patterns', [])
        if patterns:
            strengths.append(f"Proven patterns: {', '.join(patterns)}")
        
        return strengths if strengths else ["Well-structured codebase"]
    
    def _generate_value_proposition(self, advantages: List[Dict[str, str]]) -> str:
        """Generate business value proposition."""
        if not advantages:
            return "Provides reliable foundation for business operations"
        
        values = [adv['business_value'] for adv in advantages[:3]]
        return "Delivers " + ", ".join(values)
