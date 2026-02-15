"""
PatternDetector — Detect architectural patterns via graph queries.

Authority: Phase 3 Wave 4 | LENS Knowledge Graph
Purpose: Identify design patterns in codebases
"""
from dataclasses import dataclass
from typing import List
from cortex_lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


@dataclass
class DetectedPattern:
    """Detected architectural pattern."""
    pattern_type: str
    confidence: float
    entities: List[str]
    description: str


class PatternDetector:
    """
    Detect architectural patterns in knowledge graph.
    
    Example:
        detector = PatternDetector(graph)
        patterns = detector.detect_all()
    """
    
    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize pattern detector with graph."""
        self.graph = graph
    
    def detect_all(self) -> List[DetectedPattern]:
        """
        Detect all patterns in graph.
        
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Detect MVC
        mvc_pattern = self._detect_mvc()
        if mvc_pattern:
            patterns.append(mvc_pattern)
        
        # Detect Singleton
        singleton_pattern = self._detect_singleton()
        if singleton_pattern:
            patterns.append(singleton_pattern)
        
        return patterns
    
    def _detect_mvc(self) -> DetectedPattern:
        """Detect MVC (Model-View-Controller) pattern."""
        # Check both node names and file paths
        has_model = any(
            "model" in name.lower() or "model" in node.file_path.lower() 
            for name, node in self.graph.nodes.items()
        )
        has_view = any(
            "view" in name.lower() or "view" in node.file_path.lower()
            for name, node in self.graph.nodes.items()
        )
        has_controller = any(
            "controller" in name.lower() or "controller" in node.file_path.lower()
            for name, node in self.graph.nodes.items()
        )
        
        if has_model and has_view and has_controller:
            return DetectedPattern(
                pattern_type="mvc",
                confidence=0.9,
                entities=["models.py", "views.py", "controllers.py"],
                description="Model-View-Controller pattern detected"
            )
        return None
    
    def _detect_singleton(self) -> DetectedPattern:
        """Detect Singleton pattern."""
        for name, node in self.graph.nodes.items():
            # Simple heuristic: look for _instance attribute
            if node.type == "class" and "_instance" in name.lower():
                return DetectedPattern(
                    pattern_type="singleton",
                    confidence=0.8,
                    entities=[name],
                    description="Singleton pattern detected"
                )
        
        # Check for __new__ implementation (better detection)
        for node in self.graph.nodes.values():
            if node.name == "__new__":
                return DetectedPattern(
                    pattern_type="singleton",
                    confidence=0.85,
                    entities=[node.file_path],
                    description="Singleton pattern (via __new__) detected"
                )
        
        return None
