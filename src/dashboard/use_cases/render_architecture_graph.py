"""
Use Case: Render Architecture Graph

Business logic for rendering architecture visualization with D3.js.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from typing import Dict, Any, List
import logging

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IDependencyRepository,
    IHealthScoreRepository
)

logger = logging.getLogger(__name__)


class RenderArchitectureGraphUseCase:
    """
    Use case for rendering architecture graph data.
    
    Prepares data in D3.js force-directed graph format.
    """
    
    def __init__(
        self,
        component_repo: IComponentRepository,
        dependency_repo: IDependencyRepository,
        health_repo: IHealthScoreRepository
    ):
        """
        Initialize use case with repository dependencies.
        
        Args:
            component_repo: Component data access
            dependency_repo: Dependency data access
            health_repo: Health score data access
        """
        self.component_repo = component_repo
        self.dependency_repo = dependency_repo
        self.health_repo = health_repo
    
    def execute(self, filter_by: str = None) -> Dict[str, Any]:
        """
        Execute use case to generate architecture graph data.
        
        Args:
            filter_by: Optional filter (e.g., 'critical', 'security')
        
        Returns:
            Dict containing nodes and links for D3.js
        """
        logger.info(f"Rendering architecture graph (filter: {filter_by})")
        
        try:
            components = self.component_repo.get_all()
            dependencies = self.dependency_repo.get_all()
            
            # Apply filtering
            if filter_by:
                components = self._apply_filter(components, filter_by)
                # Only include dependencies between filtered components
                component_paths = {c.path for c in components}
                dependencies = [
                    d for d in dependencies
                    if d.source in component_paths and d.target in component_paths
                ]
            
            # Build nodes (components with health data)
            nodes = []
            for component in components:
                health = self.health_repo.get_component_health(component.path)
                
                node = {
                    'id': component.path,
                    'name': component.name,
                    'type': component.type.value,
                    'health_score': component.health_score,
                    'health_color': component.health_color,
                    'health_category': component.health_category,
                    'lines_of_code': component.lines_of_code,
                    'complexity': component.complexity,
                    'test_coverage': component.test_coverage,
                    'total_issues': component.total_issues,
                    'dependencies_count': len(component.dependencies),
                    'dependents_count': len(component.dependents),
                }
                
                # Add health layer breakdown if available
                if health:
                    node['layer_scores'] = health.to_dict()['layers']
                
                nodes.append(node)
            
            # Build links (dependencies)
            links = []
            for dependency in dependencies:
                link = {
                    'source': dependency.source,
                    'target': dependency.target,
                    'type': dependency.type.value,
                    'strength': dependency.strength.value,
                    'weight': dependency.strength_weight,
                    'usage_count': dependency.usage_count,
                    'is_circular': dependency.is_circular,
                    'is_cross_layer': dependency.is_cross_layer,
                    'edge_color': dependency.edge_color
                }
                links.append(link)
            
            circular_deps = [d for d in dependencies if d.is_circular]
            cross_layer_deps = [d for d in dependencies if d.is_cross_layer]
            
            graph_data = {
                'nodes': nodes,
                'links': links,
                'statistics': {
                    'total_nodes': len(nodes),
                    'total_links': len(links),
                    'circular_dependencies': len(circular_deps),
                    'cross_layer_violations': len(cross_layer_deps),
                    'avg_dependencies_per_node': (
                        sum(len(c.dependencies) for c in components) / len(components)
                        if components else 0
                    )
                },
                'filter_applied': filter_by
            }
            
            logger.info(f"Architecture graph rendered: {len(nodes)} nodes, {len(links)} links")
            return graph_data
            
        except Exception as e:
            logger.error(f"Error rendering architecture graph: {e}")
            raise
    
    def _apply_filter(self, components: List, filter_by: str) -> List:
        """Apply filter to components list"""
        if filter_by == 'critical':
            return [c for c in components if c.health_category == 'critical']
        elif filter_by == 'warning':
            return [c for c in components if c.health_category == 'warning']
        elif filter_by == 'healthy':
            return [c for c in components if c.health_category == 'healthy']
        elif filter_by == 'security':
            return [c for c in components if c.security_issues > 0]
        else:
            return components
