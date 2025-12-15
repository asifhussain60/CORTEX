"""
Success Pattern Recommender

Suggests proven patterns based on historical successes.

Part of Phase 4: Historical Context Integration
Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""
from typing import Dict, List, Any
import logging
from pathlib import Path
import yaml

class SuccessPatternRecommender:
    """Recommends success patterns from historical data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.success_patterns = self._load_success_patterns()
    
    def _load_success_patterns(self) -> Dict[str, Any]:
        """
        Load success patterns from knowledge graph.
        
        Returns:
            Dict of proven success patterns with confidence scores
        """
        # Load from knowledge-graph.yaml if exists, otherwise use defaults
        kg_path = Path("cortex-brain/knowledge-graph.yaml")
        
        default_patterns = {
            'incremental_delivery': {
                'confidence': 0.95,
                'description': 'Break complex features into incremental phases',
                'applies_to': ['authentication', 'api', 'data_migration', 'complex_feature'],
                'success_rate': '95%',
                'example': 'Auth: Phase 1 (basic) → Phase 2 (OAuth) → Phase 3 (MFA)',
                'recommendation': 'Split into 3-5 phases, each delivering value'
            },
            'tdd_first': {
                'confidence': 0.92,
                'description': 'Write tests before implementation (RED→GREEN→REFACTOR)',
                'applies_to': ['all'],
                'success_rate': '92%',
                'example': 'Always start with failing test, then implement',
                'recommendation': 'Use RED→GREEN→REFACTOR cycle for all code changes'
            },
            'checkpoint_frequency': {
                'confidence': 0.88,
                'description': 'Git checkpoint every 2-4 hours',
                'applies_to': ['all'],
                'success_rate': '88%',
                'example': 'Frequent checkpoints enable easy rollback',
                'recommendation': 'Checkpoint after each sub-phase completion'
            },
            'acceptance_criteria_first': {
                'confidence': 0.90,
                'description': 'Define acceptance criteria before implementation',
                'applies_to': ['all'],
                'success_rate': '90%',
                'example': 'Clear criteria prevent scope creep and rework',
                'recommendation': 'List all acceptance criteria in planning phase'
            },
            'complexity_based_testing': {
                'confidence': 0.85,
                'description': 'Higher complexity requires higher test coverage',
                'applies_to': ['all'],
                'success_rate': '85%',
                'example': 'LOW: 70%, MEDIUM: 80%, HIGH: 90%, CRITICAL: 95%',
                'recommendation': 'Scale coverage target with complexity tier'
            }
        }
        
        if kg_path.exists():
            try:
                with open(kg_path, 'r') as f:
                    kg_data = yaml.safe_load(f)
                    # Extract success patterns from knowledge graph
                    patterns = kg_data.get('patterns', [])
                    for pattern in patterns:
                        if isinstance(pattern, dict) and pattern.get('confidence', 0) > 70:
                            pattern_id = pattern.get('name', '').replace('-', '_')
                            if pattern_id:
                                default_patterns[pattern_id] = {
                                    'confidence': pattern.get('confidence', 50) / 100.0,
                                    'description': pattern.get('description', ''),
                                    'applies_to': ['all'],
                                    'success_rate': f"{pattern.get('confidence', 50)}%",
                                    'example': pattern.get('description', ''),
                                    'recommendation': f"Apply {pattern.get('name')} pattern"
                                }
            except Exception as e:
                self.logger.warning(f"Could not load success patterns from knowledge graph: {e}")
        
        return default_patterns
    
    def get_recommendations(self, feature_type: str, complexity: str) -> List[Dict[str, Any]]:
        """
        Get pattern recommendations for feature type and complexity.
        
        Args:
            feature_type: Type of feature being planned (e.g., 'authentication', 'api')
            complexity: Complexity tier (HIGH, MEDIUM, LOW, CRITICAL)
        
        Returns:
            List of recommended patterns sorted by confidence
        """
        recommendations = []
        
        for pattern_id, pattern in self.success_patterns.items():
            # Check if pattern applies to this feature type
            applies_to = pattern.get('applies_to', [])
            if feature_type in applies_to or 'all' in applies_to:
                recommendations.append({
                    'pattern_id': pattern_id,
                    'confidence': pattern.get('confidence', 0.5),
                    'description': pattern.get('description', ''),
                    'success_rate': pattern.get('success_rate', 'Unknown'),
                    'example': pattern.get('example', ''),
                    'recommendation': pattern.get('recommendation', '')
                })
        
        # Sort by confidence (highest first)
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Filter by minimum confidence threshold
        min_confidence = 0.70 if complexity in ['HIGH', 'CRITICAL'] else 0.60
        recommendations = [r for r in recommendations if r['confidence'] >= min_confidence]
        
        self.logger.info(f"Found {len(recommendations)} pattern recommendations for {feature_type}/{complexity}")
        
        return recommendations
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of all success patterns.
        
        Returns:
            Dict with success pattern statistics
        """
        return {
            'total_patterns': len(self.success_patterns),
            'high_confidence': len([p for p in self.success_patterns.values() 
                                   if p.get('confidence', 0) >= 0.90]),
            'medium_confidence': len([p for p in self.success_patterns.values() 
                                     if 0.70 <= p.get('confidence', 0) < 0.90]),
            'patterns': self.success_patterns
        }
