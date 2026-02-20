"""
Knowledge Synthesizer - Phase 12 S2

AC-PHASE71-008: Knowledge artifact generation from patterns

Synthesizes learned patterns into structured knowledge artifacts:
- Pattern templates for reuse
- Best practices YAML files
- Decision trees for pattern selection
- Knowledge categorization and organization

Output artifacts stored in cortex/knowledge/best-practices/ by category.

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.intelligence.learning.pattern_extractor import ExtractedPattern, PatternType

logger = logging.getLogger(__name__)


@dataclass
class PatternTemplate:
    """Template representation of a learned pattern."""

    name: str
    description: str
    pattern_type: str
    indicators: List[str]
    context: Dict[str, Any]
    effectiveness_score: float
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "pattern_type": self.pattern_type,
            "indicators": self.indicators,
            "context": self.context,
            "effectiveness_score": self.effectiveness_score,
            "evidence": self.evidence,
        }


@dataclass
class DecisionNode:
    """Node in a decision tree for pattern selection."""

    question: str
    yes_branch: Optional[DecisionNode] = None
    no_branch: Optional[DecisionNode] = None
    recommendation: Optional[str] = None


@dataclass
class KnowledgeArtifact:
    """Knowledge artifact for persistence."""

    filename: str
    category: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeSynthesizer:
    """
    Synthesizes learned patterns into structured knowledge artifacts.

    Creates:
    - Pattern templates for reuse
    - Best practices YAML files
    - Decision trees for pattern selection
    - Categorized knowledge repositories

    AC-PHASE71-008: Knowledge artifact generation
    """

    def __init__(self, knowledge_root: Optional[Path] = None):
        """
        Initialize knowledge synthesizer.

        Args:
            knowledge_root: Root directory for knowledge artifacts
        """
        self.knowledge_root = knowledge_root or Path("cortex/knowledge/best-practices")
        self.knowledge_root.mkdir(parents=True, exist_ok=True)

        # Create category subdirectories
        self._category_dirs = {
            "technical": self.knowledge_root / "technical",
            "business": self.knowledge_root / "business",
            "governance": self.knowledge_root / "governance",
            "performance": self.knowledge_root / "performance",
            "interaction": self.knowledge_root / "interaction"
        }

        for category_dir in self._category_dirs.values():
            category_dir.mkdir(parents=True, exist_ok=True)

    def generate_pattern_template(
        self,
        pattern: ExtractedPattern
    ) -> PatternTemplate:
        """
        Generate reusable template from extracted pattern.

        Args:
            pattern: ExtractedPattern to convert

        Returns:
            PatternTemplate for the pattern
        """
        # Derive template name from description
        name = self._generate_pattern_name(pattern)

        # Extract indicators from pattern data
        indicators = pattern.data.get("indicators", [])
        if not indicators and "refactoring_type" in pattern.data:
            indicators = [pattern.data["refactoring_type"]]

        # Build context from pattern data
        context = {
            k: v for k, v in pattern.data.items()
            if k not in ["indicators", "refactoring_type"]
        }

        template = PatternTemplate(
            name=name,
            description=pattern.description,
            pattern_type=pattern.pattern_type.name,
            indicators=indicators if isinstance(indicators, list) else [indicators],
            context=context,
            effectiveness_score=pattern.confidence,
            evidence=[]
        )

        logger.debug(f"Generated pattern template: {name}")
        return template

    def generate_best_practices_yaml(
        self,
        patterns: List[ExtractedPattern],
        category: str
    ) -> KnowledgeArtifact:
        """
        Generate best practices YAML artifact from patterns.

        Args:
            patterns: List of ExtractedPattern objects
            category: Category for the artifact

        Returns:
            KnowledgeArtifact with YAML content
        """
        # Generate templates for all patterns
        templates = [self.generate_pattern_template(p) for p in patterns]

        # Build YAML structure
        yaml_data = {
            "metadata": {
                "category": category,
                "generated_at": datetime.now().isoformat(),
                "pattern_count": len(templates),
                "source": "UniversalLearningLoop"
            },
            "patterns": [template.to_dict() for template in templates]
        }

        # Convert to YAML string
        content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

        # Create artifact
        filename = f"{category}-patterns-{datetime.now().strftime('%Y%m%d')}.yaml"
        artifact = KnowledgeArtifact(
            filename=filename,
            category=category,
            content=content,
            metadata=yaml_data["metadata"]
        )

        logger.info(f"Generated best practices YAML: {filename}")
        return artifact

    def synthesize_decision_tree(
        self,
        patterns: List[ExtractedPattern],
        context: str
    ) -> DecisionNode:
        """
        Synthesize decision tree for pattern selection.

        Args:
            patterns: List of patterns to organize
            context: Context for decision tree (e.g., "refactoring")

        Returns:
            Root DecisionNode of the decision tree
        """
        if not patterns:
            return DecisionNode(
                question=f"No patterns available for {context}",
                recommendation="Collect more data"
            )

        # Simple decision tree: select based on confidence
        if len(patterns) == 1:
            pattern = patterns[0]
            return DecisionNode(
                question=f"Apply {pattern.description}?",
                recommendation=pattern.description
            )

        # Sort by confidence
        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)

        # Create tree with highest confidence pattern at root
        best_pattern = sorted_patterns[0]
        other_patterns = sorted_patterns[1:]

        yes_branch = DecisionNode(
            question="Pattern applied successfully?",
            recommendation=best_pattern.description
        )

        no_branch = self.synthesize_decision_tree(other_patterns, context) if other_patterns else DecisionNode(
            question="Try alternative approach?",
            recommendation="Manual implementation"
        )

        root = DecisionNode(
            question=f"Does situation match {best_pattern.description}?",
            yes_branch=yes_branch,
            no_branch=no_branch
        )

        return root

    def save_artifact(self, artifact: KnowledgeArtifact) -> Path:
        """
        Save knowledge artifact to disk.

        Args:
            artifact: KnowledgeArtifact to save

        Returns:
            Path to saved file
        """
        # Determine target directory
        category_dir = self._category_dirs.get("technical")  # Default
        for key, dir_path in self._category_dirs.items():
            if key in artifact.category.lower():
                category_dir = dir_path
                break

        # Save file
        filepath = category_dir / artifact.filename
        filepath.write_text(artifact.content)

        logger.info(f"Saved knowledge artifact: {filepath}")
        return filepath

    def aggregate_patterns(
        self,
        patterns: List[ExtractedPattern]
    ) -> List[ExtractedPattern]:
        """
        Aggregate similar patterns to increase confidence.

        Args:
            patterns: List of patterns to aggregate

        Returns:
            List of aggregated patterns with boosted confidence
        """
        if not patterns:
            return []

        # Group by description similarity (simple string match for now)
        pattern_groups: Dict[str, List[ExtractedPattern]] = {}

        for pattern in patterns:
            # Use first few words as grouping key
            key = " ".join(pattern.description.split()[:5]).lower()

            if key not in pattern_groups:
                pattern_groups[key] = []
            pattern_groups[key].append(pattern)

        # Aggregate each group
        aggregated = []
        for group in pattern_groups.values():
            if len(group) == 1:
                aggregated.append(group[0])
            else:
                # Boost confidence based on frequency
                base_pattern = group[0]
                boost_factor = min(len(group) * 0.1, 0.3)  # Max 30% boost
                new_confidence = min(base_pattern.confidence + boost_factor, 1.0)

                # Create aggregated pattern
                aggregated_pattern = ExtractedPattern(
                    pattern_type=base_pattern.pattern_type,
                    description=base_pattern.description,
                    data=base_pattern.data,
                    confidence=new_confidence,
                    source_orchestrator=base_pattern.source_orchestrator,
                    source_operation=base_pattern.source_operation
                )
                aggregated.append(aggregated_pattern)

        logger.debug(f"Aggregated {len(patterns)} patterns into {len(aggregated)}")
        return aggregated

    def _generate_pattern_name(self, pattern: ExtractedPattern) -> str:
        """Generate kebab-case name from pattern description."""
        # Extract key words from description
        words = pattern.description.lower().split()[:5]

        # Remove common words
        stopwords = {"the", "a", "an", "for", "to", "of", "in", "on", "at"}
        words = [w for w in words if w not in stopwords]

        # Create kebab-case name
        name = "_".join(words)

        # Add type suffix if in data
        if "refactoring_type" in pattern.data:
            name = pattern.data["refactoring_type"]

        return name
