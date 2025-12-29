"""
Evolution Narrator - Tell the transformation story over time

Compares repository versions to generate "how we got here" narratives
showing the business journey from v1.0 to current state.

Example:
    Input: v1.0 (Monolith, 35K LOC, 500 users) → Current (Microservices, 85K LOC, 10K users)
    Output: "Transformed from monolithic architecture to microservices, enabling
            20x user growth while improving deployment speed from weeks to hours"

Author: Asif Hussain
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class EvolutionNarrator:
    """Narrates application evolution and transformation story."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evolution narrator."""
        self.config = config or {}
        logger.info("📈 EvolutionNarrator initialized")
    
    def tell_story(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate evolution narrative comparing two analysis snapshots.
        
        Args:
            current: Current repository analysis
            previous: Previous repository analysis
        
        Returns:
            Dictionary with evolution story, milestones, and business outcomes
        """
        logger.info("📈 Generating evolution narrative")
        
        # Calculate changes
        changes = self._calculate_changes(current, previous)
        
        # Generate narrative
        narrative = {
            'summary': self._generate_summary(changes),
            'milestones': self._identify_milestones(changes),
            'metrics_evolution': changes,
            'business_outcomes': self._infer_business_outcomes(changes),
            'transformation_type': self._classify_transformation(changes)
        }
        
        logger.info("✅ Generated evolution narrative")
        return narrative
    
    def _calculate_changes(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate key metrics changes."""
        changes = {}
        
        # LOC change
        curr_health = current.get('health', {})
        prev_health = previous.get('health', {})
        
        curr_loc = curr_health.get('total_loc', 0)
        prev_loc = prev_health.get('total_loc', 1)  # Avoid division by zero
        
        changes['loc_change'] = {
            'previous': prev_loc,
            'current': curr_loc,
            'delta': curr_loc - prev_loc,
            'percent': ((curr_loc - prev_loc) / prev_loc * 100) if prev_loc > 0 else 0
        }
        
        # File count change
        curr_files = curr_health.get('total_files', 0)
        prev_files = prev_health.get('total_files', 1)
        
        changes['file_change'] = {
            'previous': prev_files,
            'current': curr_files,
            'delta': curr_files - prev_files,
            'percent': ((curr_files - prev_files) / prev_files * 100) if prev_files > 0 else 0
        }
        
        # Architecture evolution
        curr_arch = current.get('architecture', {})
        prev_arch = previous.get('architecture', {})
        
        changes['architecture_evolution'] = {
            'previous_patterns': prev_arch.get('patterns', []),
            'current_patterns': curr_arch.get('patterns', []),
            'new_patterns': list(set(curr_arch.get('patterns', [])) - set(prev_arch.get('patterns', [])))
        }
        
        return changes
    
    def _generate_summary(self, changes: Dict[str, Any]) -> str:
        """Generate executive summary of evolution."""
        loc_change = changes.get('loc_change', {})
        delta = loc_change.get('delta', 0)
        percent = loc_change.get('percent', 0)
        
        if delta > 0:
            growth = f"grew by {abs(percent):.0f}%"
        else:
            growth = f"reduced by {abs(percent):.0f}%"
        
        return f"Application {growth}, reflecting active development and evolution"
    
    def _identify_milestones(self, changes: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify key milestones in evolution."""
        milestones = []
        
        # Architecture changes
        arch_changes = changes.get('architecture_evolution', {})
        new_patterns = arch_changes.get('new_patterns', [])
        
        for pattern in new_patterns:
            milestones.append({
                'type': 'Architecture',
                'description': f"Adopted {pattern} pattern",
                'business_impact': 'Improved scalability and maintainability'
            })
        
        # Significant LOC changes
        loc_change = changes.get('loc_change', {})
        if abs(loc_change.get('percent', 0)) > 50:
            if loc_change.get('delta', 0) > 0:
                milestones.append({
                    'type': 'Growth',
                    'description': 'Major feature expansion',
                    'business_impact': 'Enhanced product capabilities'
                })
            else:
                milestones.append({
                    'type': 'Refactoring',
                    'description': 'Code optimization and cleanup',
                    'business_impact': 'Improved maintainability'
                })
        
        return milestones if milestones else [{'type': 'Evolution', 'description': 'Continuous improvement', 'business_impact': 'Ongoing enhancement'}]
    
    def _infer_business_outcomes(self, changes: Dict[str, Any]) -> List[str]:
        """Infer business outcomes from technical changes."""
        outcomes = []
        
        loc_change = changes.get('loc_change', {})
        if loc_change.get('delta', 0) > 0:
            outcomes.append("Expanded product capabilities")
        
        arch_changes = changes.get('architecture_evolution', {})
        if arch_changes.get('new_patterns'):
            outcomes.append("Enhanced architectural maturity")
        
        return outcomes if outcomes else ["Maintained stable platform"]
    
    def _classify_transformation(self, changes: Dict[str, Any]) -> str:
        """Classify type of transformation."""
        loc_percent = abs(changes.get('loc_change', {}).get('percent', 0))
        
        if loc_percent > 100:
            return "Major Transformation"
        elif loc_percent > 50:
            return "Significant Evolution"
        elif loc_percent > 20:
            return "Moderate Growth"
        else:
            return "Steady Maintenance"
