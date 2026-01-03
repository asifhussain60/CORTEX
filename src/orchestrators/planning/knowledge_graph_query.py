"""
Knowledge Graph Query - Tier 2 Knowledge Graph Integration.

Queries cortex-brain/tier2 knowledge graphs for feature relationships.
Provides context about existing features, dependencies, and patterns.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KnowledgeContext:
    """Context from knowledge graph queries."""
    related_features: List[str]
    dependencies: List[str]
    patterns: List[str]
    risks: List[str]
    recommendations: List[str]


class KnowledgeGraphQuery:
    """
    Query Tier 2 knowledge graphs for planning context.
    
    Features:
    - Load knowledge-graph.yaml (tier 2)
    - Find related features
    - Identify dependency chains
    - Discover architectural patterns
    - Surface risks and recommendations
    
    Usage:
        query = KnowledgeGraphQuery()
        context = query.get_feature_context("Authentication API")
        
        print(f"Related: {context.related_features}")
        print(f"Dependencies: {context.dependencies}")
    """
    
    def __init__(self, graph_path: Optional[Path] = None):
        """
        Initialize knowledge graph query.
        
        Args:
            graph_path: Path to knowledge-graph.yaml
                       (default: cortex-brain/knowledge-graph.yaml)
        """
        self.logger = logging.getLogger(__name__)
        
        if graph_path is None:
            graph_path = Path("cortex-brain/knowledge-graph.yaml")
        
        self.graph_path = graph_path
        self.graph: Dict[str, Any] = {}
        
        if self.graph_path.exists():
            self._load_knowledge_graph()
        else:
            self.logger.warning(f"Knowledge graph not found: {self.graph_path}")
    
    def _load_knowledge_graph(self) -> None:
        """Load knowledge graph from YAML."""
        try:
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                self.graph = yaml.safe_load(f) or {}
            
            self.logger.info(f"Loaded knowledge graph with {len(self.graph)} entries")
        
        except Exception as e:
            self.logger.error(f"Failed to load knowledge graph: {e}")
            self.graph = {}
    
    def get_feature_context(self, feature_name: str) -> KnowledgeContext:
        """
        Get knowledge context for feature planning.
        
        Args:
            feature_name: Name of feature being planned
        
        Returns:
            KnowledgeContext with related info
        """
        # Query knowledge graph for related features
        related = self._find_related_features(feature_name)
        dependencies = self._find_dependencies(feature_name)
        patterns = self._find_patterns(feature_name)
        risks = self._identify_risks(feature_name, dependencies)
        recommendations = self._generate_recommendations(feature_name, patterns)
        
        return KnowledgeContext(
            related_features=related,
            dependencies=dependencies,
            patterns=patterns,
            risks=risks,
            recommendations=recommendations
        )
    
    def _find_related_features(self, feature_name: str) -> List[str]:
        """Find features related to given feature."""
        related = []
        feature_lower = feature_name.lower()
        
        # Search through graph entries
        for key, value in self.graph.items():
            if isinstance(value, dict):
                # Check for explicit relationships
                if 'related' in value:
                    related_items = value['related']
                    if isinstance(related_items, list):
                        for item in related_items:
                            if feature_lower in str(item).lower():
                                related.append(key)
                                break
                
                # Check for name similarity
                if feature_lower in key.lower():
                    related.append(key)
        
        return list(set(related))  # Deduplicate
    
    def _find_dependencies(self, feature_name: str) -> List[str]:
        """Find dependencies for feature."""
        dependencies = []
        feature_lower = feature_name.lower()
        
        # Query graph for dependency chains
        for key, value in self.graph.items():
            if isinstance(value, dict):
                if 'dependencies' in value:
                    deps = value['dependencies']
                    if isinstance(deps, list):
                        for dep in deps:
                            if feature_lower in str(dep).lower():
                                dependencies.append(key)
                                break
                
                # Check if this feature matches
                if feature_lower in key.lower() and 'dependencies' in value:
                    deps = value['dependencies']
                    if isinstance(deps, list):
                        dependencies.extend([str(d) for d in deps])
        
        return list(set(dependencies))  # Deduplicate
    
    def _find_patterns(self, feature_name: str) -> List[str]:
        """Find architectural patterns applicable to feature."""
        patterns = []
        feature_lower = feature_name.lower()
        
        # Pattern matching based on feature type
        if any(keyword in feature_lower for keyword in ['api', 'endpoint', 'rest']):
            patterns.append("RESTful API pattern")
        
        if any(keyword in feature_lower for keyword in ['auth', 'authentication', 'login']):
            patterns.append("Authentication middleware pattern")
        
        if any(keyword in feature_lower for keyword in ['database', 'db', 'storage']):
            patterns.append("Repository pattern")
        
        if any(keyword in feature_lower for keyword in ['orchestrator', 'workflow']):
            patterns.append("Orchestrator pattern")
        
        if any(keyword in feature_lower for keyword in ['test', 'testing', 'tdd']):
            patterns.append("Test-driven development pattern")
        
        # Check graph for explicit patterns
        for key, value in self.graph.items():
            if isinstance(value, dict) and 'patterns' in value:
                if feature_lower in key.lower():
                    graph_patterns = value['patterns']
                    if isinstance(graph_patterns, list):
                        patterns.extend([str(p) for p in graph_patterns])
        
        return list(set(patterns))  # Deduplicate
    
    def _identify_risks(self, feature_name: str, dependencies: List[str]) -> List[str]:
        """Identify risks based on knowledge graph."""
        risks = []
        
        if len(dependencies) > 5:
            risks.append(f"High dependency count ({len(dependencies)}) may increase maintenance complexity")
        
        if len(dependencies) > 10:
            risks.append("Excessive dependencies detected - consider refactoring")
        
        # Check for known risky patterns
        feature_lower = feature_name.lower()
        
        if 'migration' in feature_lower or 'refactor' in feature_lower:
            risks.append("Migration/refactoring requires careful rollback planning")
        
        if 'database' in feature_lower or 'schema' in feature_lower:
            risks.append("Database changes require migration scripts and backups")
        
        if 'auth' in feature_lower or 'security' in feature_lower:
            risks.append("Security-critical feature requires thorough testing")
        
        # Check graph for explicit risks
        for key, value in self.graph.items():
            if isinstance(value, dict) and 'risks' in value:
                if feature_lower in key.lower():
                    graph_risks = value['risks']
                    if isinstance(graph_risks, list):
                        risks.extend([str(r) for r in graph_risks])
        
        return list(set(risks))  # Deduplicate
    
    def _generate_recommendations(self, feature_name: str, patterns: List[str]) -> List[str]:
        """Generate recommendations from knowledge graph."""
        recommendations = []
        
        if patterns:
            recommendations.append(f"Consider using established patterns: {', '.join(patterns[:3])}")
        
        feature_lower = feature_name.lower()
        
        if 'test' not in feature_lower:
            recommendations.append("Include comprehensive test coverage (TDD)")
        
        if 'orchestrator' in feature_lower:
            recommendations.append("Leverage BaseOrchestrator v4.1 for config-driven execution")
        
        if 'database' in feature_lower or 'db' in feature_lower:
            recommendations.append("Use ACID transactions and include migration scripts")
        
        # Check graph for explicit recommendations
        for key, value in self.graph.items():
            if isinstance(value, dict) and 'recommendations' in value:
                if feature_lower in key.lower():
                    graph_recs = value['recommendations']
                    if isinstance(graph_recs, list):
                        recommendations.extend([str(r) for r in graph_recs])
        
        return list(set(recommendations))  # Deduplicate
    
    def query_feature(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Query graph for specific feature entry.
        
        Args:
            feature_name: Name of feature to query
        
        Returns:
            Feature data dict if found, None otherwise
        """
        feature_lower = feature_name.lower()
        
        for key, value in self.graph.items():
            if feature_lower in key.lower():
                return value if isinstance(value, dict) else None
        
        return None
    
    def get_all_features(self) -> List[str]:
        """Get list of all features in knowledge graph."""
        return list(self.graph.keys())
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        total_entries = len(self.graph)
        entries_with_deps = 0
        entries_with_patterns = 0
        entries_with_risks = 0
        
        for value in self.graph.values():
            if isinstance(value, dict):
                if 'dependencies' in value:
                    entries_with_deps += 1
                if 'patterns' in value:
                    entries_with_patterns += 1
                if 'risks' in value:
                    entries_with_risks += 1
        
        return {
            "total_entries": total_entries,
            "entries_with_dependencies": entries_with_deps,
            "entries_with_patterns": entries_with_patterns,
            "entries_with_risks": entries_with_risks
        }
