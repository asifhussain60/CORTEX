"""
CORTEX Toolkit Request Analyzer

Analyzes tool creation requests to prevent duplication.
Provides semantic analysis and recommendations.
"""
from typing import List, Optional, Dict, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from .capability_matrix import CapabilityMatrix, ToolMatch

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Type of recommendation from analysis."""
    ALLOW = "allow"              # No overlap, creation allowed
    WARN = "warn"                # Some overlap, warn but allow
    SUGGEST = "suggest"          # Significant overlap, suggest existing
    BLOCK = "block"              # High overlap, block creation


@dataclass
class ToolRequest:
    """Request to create a new tool."""
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    def __post_init__(self):
        # Auto-extract capabilities if not provided
        if not self.capabilities:
            self.capabilities = []


@dataclass
class AnalysisResult:
    """Result of analyzing a tool request."""
    can_create: bool
    recommendation_type: RecommendationType
    overlapping_tools: List[ToolMatch]
    recommendation: str
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    extracted_intent: List[str] = field(default_factory=list)
    
    @property
    def top_match(self) -> Optional[ToolMatch]:
        """Get the highest-similarity matching tool."""
        if self.overlapping_tools:
            return max(self.overlapping_tools, key=lambda t: t.similarity)
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "can_create": self.can_create,
            "recommendation_type": self.recommendation_type.value,
            "recommendation": self.recommendation,
            "overlapping_tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "similarity": t.similarity,
                    "matched_capabilities": list(t.matched_capabilities)
                }
                for t in self.overlapping_tools
            ],
            "similarity_scores": self.similarity_scores,
            "extracted_intent": self.extracted_intent
        }


class RequestAnalyzer:
    """
    Analyzes tool requests to prevent duplication.
    
    Features:
    - Intent extraction from descriptions
    - Capability overlap detection
    - Semantic similarity scoring
    - Creation recommendations
    
    Usage:
        analyzer = RequestAnalyzer(registry)
        request = ToolRequest(name="my-cleanup", description="Clean cache files")
        result = analyzer.analyze_request(request)
        if not result.can_create:
            print(f"Recommendation: {result.recommendation}")
    """
    
    # Similarity thresholds for recommendations
    WARN_THRESHOLD = 0.5       # Warn if similarity >= 50%
    SUGGEST_THRESHOLD = 0.7    # Suggest existing if similarity >= 70%
    BLOCK_THRESHOLD = 0.9      # Block creation if similarity >= 90%
    
    def __init__(self, registry=None):
        """
        Initialize RequestAnalyzer.
        
        Args:
            registry: Optional ToolkitRegistry for capability matrix.
        """
        self.registry = registry
        self.capability_matrix = CapabilityMatrix(registry)
        
        logger.info("RequestAnalyzer initialized")
    
    def analyze_request(self, request: ToolRequest) -> AnalysisResult:
        """
        Analyze if a tool request can be fulfilled by existing tools.
        
        Args:
            request: Tool creation request.
            
        Returns:
            AnalysisResult with recommendation.
        """
        # 1. Extract intent keywords
        intent = self._extract_intent(request)
        
        # 2. Find overlapping tools
        overlaps = self.capability_matrix.find_overlaps(intent)
        
        # 3. Calculate similarity scores
        request_caps = set(intent)
        for tool in overlaps:
            tool_caps = self.capability_matrix.get_tool_capabilities(tool.name)
            if tool_caps:
                tool.similarity = self._calculate_weighted_similarity(
                    request_caps,
                    tool_caps.all_capabilities,
                    tool.matched_capabilities
                )
        
        # Sort by similarity
        overlaps.sort(key=lambda t: t.similarity, reverse=True)
        
        # 4. Determine recommendation
        recommendation_type, can_create, recommendation = self._generate_recommendation(
            request, overlaps
        )
        
        # 5. Build similarity scores dict
        similarity_scores = {t.name: t.similarity for t in overlaps if t.similarity > 0}
        
        # Log the analysis
        logger.info(
            f"Analyzed request '{request.name}': "
            f"intent={intent}, overlaps={len(overlaps)}, "
            f"recommendation={recommendation_type.value}"
        )
        
        return AnalysisResult(
            can_create=can_create,
            recommendation_type=recommendation_type,
            overlapping_tools=overlaps[:5],  # Top 5 matches
            recommendation=recommendation,
            similarity_scores=similarity_scores,
            extracted_intent=intent
        )
    
    def _extract_intent(self, request: ToolRequest) -> List[str]:
        """Extract intent keywords from the request."""
        # Start with provided capabilities
        intent = list(request.capabilities)
        
        # Add name-based keywords
        name_parts = request.name.lower().replace('-', ' ').replace('_', ' ').split()
        intent.extend(name_parts)
        
        # Extract from description
        if request.description:
            desc_intent = self.capability_matrix.extract_intent(request.description)
            intent.extend(desc_intent)
        
        # Deduplicate while preserving order
        seen = set()
        unique_intent = []
        for kw in intent:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_intent.append(kw_lower)
        
        return unique_intent
    
    def _calculate_weighted_similarity(
        self,
        request_caps: Set[str],
        tool_caps: Set[str],
        matched_caps: Set[str]
    ) -> float:
        """
        Calculate weighted similarity score.
        
        Combines:
        - Jaccard similarity of capabilities
        - Bonus for direct keyword matches
        """
        # Base Jaccard similarity
        base_sim = self.capability_matrix.calculate_similarity(request_caps, tool_caps)
        
        # Match bonus (each match adds to score)
        match_bonus = min(len(matched_caps) * 0.1, 0.3)  # Max 30% bonus
        
        # Combined score (capped at 1.0)
        return min(base_sim + match_bonus, 1.0)
    
    def _generate_recommendation(
        self,
        request: ToolRequest,
        overlaps: List[ToolMatch]
    ) -> tuple:
        """
        Generate recommendation based on overlap analysis.
        
        Returns:
            Tuple of (RecommendationType, can_create, recommendation_text)
        """
        if not overlaps:
            return (
                RecommendationType.ALLOW,
                True,
                f"No overlapping tools found. '{request.name}' can be created."
            )
        
        # Check highest similarity
        top_match = overlaps[0]
        max_similarity = top_match.similarity
        
        if max_similarity >= self.BLOCK_THRESHOLD:
            return (
                RecommendationType.BLOCK,
                False,
                f"Tool '{request.name}' has {max_similarity:.0%} overlap with '{top_match.name}'. "
                f"Use existing tool: {top_match.name} ({top_match.description})"
            )
        
        if max_similarity >= self.SUGGEST_THRESHOLD:
            similar_tools = [t.name for t in overlaps if t.similarity >= self.SUGGEST_THRESHOLD]
            return (
                RecommendationType.SUGGEST,
                True,  # Allow but strongly suggest
                f"Consider using existing tools instead of creating '{request.name}': "
                f"{', '.join(similar_tools)}. Overlap: {max_similarity:.0%}"
            )
        
        if max_similarity >= self.WARN_THRESHOLD:
            return (
                RecommendationType.WARN,
                True,
                f"Tool '{request.name}' has some overlap ({max_similarity:.0%}) with: "
                f"{top_match.name}. Review before creating."
            )
        
        return (
            RecommendationType.ALLOW,
            True,
            f"'{request.name}' has minimal overlap with existing tools. Creation allowed."
        )
    
    def check_exact_duplicate(self, name: str) -> Optional[str]:
        """
        Check if a tool with the exact name already exists.
        
        Args:
            name: Tool name to check.
            
        Returns:
            Existing tool name if found, None otherwise.
        """
        if not self.registry:
            return None
        
        existing = self.registry.get_tool(name)
        if existing:
            return name
        
        # Also check similar names (case-insensitive, with/without hyphens)
        name_normalized = name.lower().replace('-', '').replace('_', '')
        
        for tool in self.registry.list_tools():
            tool_normalized = tool['name'].lower().replace('-', '').replace('_', '')
            if tool_normalized == name_normalized:
                return tool['name']
        
        return None
    
    def suggest_alternatives(self, description: str, limit: int = 5) -> List[ToolMatch]:
        """
        Suggest existing tools that might meet the described need.
        
        Args:
            description: Natural language description of needed functionality.
            limit: Maximum number of suggestions.
            
        Returns:
            List of matching tools.
        """
        intent = self.capability_matrix.extract_intent(description)
        overlaps = self.capability_matrix.find_overlaps(intent)
        
        # Calculate similarity for each
        request_caps = set(intent)
        for tool in overlaps:
            tool_caps = self.capability_matrix.get_tool_capabilities(tool.name)
            if tool_caps:
                tool.similarity = self._calculate_weighted_similarity(
                    request_caps,
                    tool_caps.all_capabilities,
                    tool.matched_capabilities
                )
        
        # Sort and limit
        overlaps.sort(key=lambda t: t.similarity, reverse=True)
        return overlaps[:limit]
    
    def get_capability_report(self) -> Dict[str, List[str]]:
        """
        Generate a report of tools grouped by capability.
        
        Returns:
            Dict mapping capabilities to tool names.
        """
        report = {}
        for capability in self.capability_matrix.get_all_capabilities():
            tools = self.capability_matrix.get_tools_by_capability(capability)
            if tools:
                report[capability] = sorted(tools)
        return report
