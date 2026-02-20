"""
Tests for Knowledge Synthesizer - Phase 12 S2

AC-PHASE71-008: Knowledge artifact generation from patterns

Tests synthesis of learned patterns into structured knowledge:
- Pattern template generation
- Best practices YAML creation
- Decision tree synthesis
- Knowledge artifact validation

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

from cortex.intelligence.learning.knowledge_synthesizer import (
    DecisionNode,
    KnowledgeArtifact,
    KnowledgeSynthesizer,
    PatternTemplate,
)
from cortex.intelligence.learning.pattern_extractor import ExtractedPattern, PatternType


@pytest.fixture
def temp_knowledge_dir(tmp_path: Path) -> Path:
    """Create temporary knowledge directory."""
    knowledge_dir = tmp_path / "cortex" / "knowledge" / "best-practices"
    knowledge_dir.mkdir(parents=True)
    return knowledge_dir


@pytest.fixture
def synthesizer(temp_knowledge_dir: Path) -> KnowledgeSynthesizer:
    """Create KnowledgeSynthesizer instance."""
    return KnowledgeSynthesizer(knowledge_root=temp_knowledge_dir)


@pytest.fixture
def sample_pattern() -> ExtractedPattern:
    """Create sample extracted pattern."""
    return ExtractedPattern(
        pattern_type=PatternType.TECHNICAL,
        description="Extract method refactoring reduces complexity",
        data={
            "refactoring_type": "extract_method",
            "indicators": ["long_method", "high_complexity"],
            "benefits": ["readability", "testability"]
        },
        confidence=0.85,
        source_orchestrator="RefactoringOrchestrator",
        source_operation="refactor"
    )


class TestKnowledgeSynthesizerInitialization:
    """Test KnowledgeSynthesizer initialization."""

    def test_initialization(self, temp_knowledge_dir: Path) -> None:
        """Test synthesizer initialization."""
        synthesizer = KnowledgeSynthesizer(knowledge_root=temp_knowledge_dir)

        assert synthesizer.knowledge_root == temp_knowledge_dir
        assert synthesizer.knowledge_root.exists()

    def test_creates_subdirectories(self, temp_knowledge_dir: Path) -> None:
        """Test synthesizer creates category subdirectories."""
        synthesizer = KnowledgeSynthesizer(knowledge_root=temp_knowledge_dir)

        # Verify category directories exist
        for category in ["technical", "business", "governance", "performance"]:
            category_dir = temp_knowledge_dir / category
            assert category_dir.exists()


class TestPatternTemplateGeneration:
    """Test pattern template generation."""

    def test_generate_template_from_pattern(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test generating pattern template from extracted pattern."""
        template = synthesizer.generate_pattern_template(sample_pattern)

        assert isinstance(template, PatternTemplate)
        assert template.name == "extract_method"  # Name derived from refactoring_type in data
        assert "complexity" in template.description.lower()
        assert len(template.indicators) > 0

    def test_template_has_required_fields(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test template contains all required fields."""
        template = synthesizer.generate_pattern_template(sample_pattern)

        assert template.name is not None
        assert template.description is not None
        assert template.pattern_type is not None
        assert template.indicators is not None
        assert template.context is not None
        assert template.effectiveness_score >= 0.0

    def test_template_effectiveness_from_confidence(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test template effectiveness score derived from pattern confidence."""
        template = synthesizer.generate_pattern_template(sample_pattern)

        # Effectiveness should be related to confidence
        assert 0.0 <= template.effectiveness_score <= 1.0
        assert abs(template.effectiveness_score - sample_pattern.confidence) < 0.2


class TestBestPracticesYAMLGeneration:
    """Test best practices YAML generation."""

    def test_generate_yaml_artifact(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test generating YAML artifact from pattern."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        assert isinstance(artifact, KnowledgeArtifact)
        assert artifact.category == "refactoring"
        assert "refactoring" in artifact.filename

    def test_yaml_artifact_is_valid_yaml(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test generated YAML is parseable."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        # Should be valid YAML
        try:
            data = yaml.safe_load(artifact.content)
            assert isinstance(data, dict)
        except yaml.YAMLError:
            pytest.fail("Generated content is not valid YAML")

    def test_yaml_contains_pattern_information(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test YAML contains pattern information."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        data = yaml.safe_load(artifact.content)
        assert "patterns" in data
        assert len(data["patterns"]) > 0

    def test_yaml_includes_metadata(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test YAML includes metadata section."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        data = yaml.safe_load(artifact.content)
        assert "metadata" in data
        assert "category" in data["metadata"]
        assert "generated_at" in data["metadata"]


class TestDecisionTreeSynthesis:
    """Test decision tree synthesis."""

    def test_synthesize_decision_tree(
        self,
        synthesizer: KnowledgeSynthesizer
    ) -> None:
        """Test synthesizing decision tree from patterns."""
        patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Pattern A for condition X",
                data={"condition": "X", "action": "A"},
                confidence=0.8,
                source_orchestrator="TestOrch",
                source_operation="test"
            ),
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Pattern B for condition Y",
                data={"condition": "Y", "action": "B"},
                confidence=0.9,
                source_orchestrator="TestOrch",
                source_operation="test"
            )
        ]

        tree = synthesizer.synthesize_decision_tree(patterns, context="refactoring")

        assert isinstance(tree, DecisionNode)
        assert tree.question is not None

    def test_decision_tree_has_branches(
        self,
        synthesizer: KnowledgeSynthesizer
    ) -> None:
        """Test decision tree has branching logic."""
        patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Pattern {i}",
                data={"index": i},
                confidence=0.8,
                source_orchestrator="TestOrch",
                source_operation="test"
            )
            for i in range(3)
        ]

        tree = synthesizer.synthesize_decision_tree(patterns, context="testing")

        # Root should have branches
        assert tree.yes_branch is not None or tree.no_branch is not None

    def test_decision_tree_leaf_nodes_have_recommendations(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test leaf nodes contain pattern recommendations."""
        tree = synthesizer.synthesize_decision_tree([sample_pattern], context="refactoring")

        # Find a leaf node
        def find_leaf(node: DecisionNode) -> DecisionNode:
            if node.recommendation is not None:
                return node
            if node.yes_branch:
                return find_leaf(node.yes_branch)
            if node.no_branch:
                return find_leaf(node.no_branch)
            return node

        leaf = find_leaf(tree)
        assert leaf.recommendation is not None


class TestKnowledgeArtifactPersistence:
    """Test knowledge artifact persistence."""

    def test_save_artifact_to_disk(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test saving knowledge artifact to disk."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        filepath = synthesizer.save_artifact(artifact)

        assert filepath.exists()
        assert filepath.parent == synthesizer.knowledge_root / "technical"

    def test_saved_artifact_is_readable(
        self,
        synthesizer: KnowledgeSynthesizer,
        sample_pattern: ExtractedPattern
    ) -> None:
        """Test saved artifact can be read back."""
        artifact = synthesizer.generate_best_practices_yaml(
            patterns=[sample_pattern],
            category="refactoring"
        )

        filepath = synthesizer.save_artifact(artifact)

        # Read back and verify
        content = filepath.read_text()
        data = yaml.safe_load(content)
        assert isinstance(data, dict)

    def test_save_multiple_artifacts(
        self,
        synthesizer: KnowledgeSynthesizer
    ) -> None:
        """Test saving multiple artifacts."""
        patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description=f"Pattern {i}",
                data={},
                confidence=0.8,
                source_orchestrator="TestOrch",
                source_operation="test"
            )
            for i in range(3)
        ]

        filepaths = []
        for i, pattern in enumerate(patterns):
            artifact = synthesizer.generate_best_practices_yaml(
                patterns=[pattern],
                category=f"category_{i}"
            )
            filepath = synthesizer.save_artifact(artifact)
            filepaths.append(filepath)

        # All files should exist
        for filepath in filepaths:
            assert filepath.exists()


class TestPatternAggregation:
    """Test pattern aggregation across multiple sources."""

    def test_aggregate_similar_patterns(
        self,
        synthesizer: KnowledgeSynthesizer
    ) -> None:
        """Test aggregating similar patterns."""
        similar_patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Extract method for readability",
                data={"refactoring_type": "extract_method"},
                confidence=0.8,
                source_orchestrator="RefactoringOrchestrator",
                source_operation="refactor"
            ),
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Extract method to reduce complexity",
                data={"refactoring_type": "extract_method"},
                confidence=0.85,
                source_orchestrator="RefactoringOrchestrator",
                source_operation="refactor"
            )
        ]

        aggregated = synthesizer.aggregate_patterns(similar_patterns)

        # Should combine similar patterns
        assert len(aggregated) <= len(similar_patterns)

    def test_aggregation_increases_confidence(
        self,
        synthesizer: KnowledgeSynthesizer
    ) -> None:
        """Test pattern aggregation increases confidence scores."""
        patterns = [
            ExtractedPattern(
                pattern_type=PatternType.TECHNICAL,
                description="Common pattern",
                data={"type": "common"},
                confidence=0.6,
                source_orchestrator="TestOrch",
                source_operation="test"
            )
            for _ in range(5)  # Same pattern observed 5 times
        ]

        aggregated = synthesizer.aggregate_patterns(patterns)

        # Aggregated confidence should be higher than individual
        if aggregated:
            assert aggregated[0].confidence > 0.6


class TestKnowledgeArtifactDataClass:
    """Test KnowledgeArtifact data class."""

    def test_artifact_creation(self) -> None:
        """Test creating KnowledgeArtifact instance."""
        artifact = KnowledgeArtifact(
            filename="test-patterns.yaml",
            category="testing",
            content="test: content",
            metadata={"version": "1.0"}
        )

        assert artifact.filename == "test-patterns.yaml"
        assert artifact.category == "testing"
        assert artifact.content == "test: content"

    def test_artifact_with_yaml_content(self) -> None:
        """Test artifact with YAML content."""
        yaml_content = yaml.dump({"patterns": [{"name": "test"}]})
        artifact = KnowledgeArtifact(
            filename="patterns.yaml",
            category="general",
            content=yaml_content,
            metadata={}
        )

        # Should be parseable YAML
        data = yaml.safe_load(artifact.content)
        assert "patterns" in data


class TestPatternTemplateDataClass:
    """Test PatternTemplate data class."""

    def test_template_creation(self) -> None:
        """Test creating PatternTemplate instance."""
        template = PatternTemplate(
            name="test_pattern",
            description="Test pattern description",
            pattern_type="TECHNICAL",
            indicators=["indicator1", "indicator2"],
            context={"when": "always"},
            effectiveness_score=0.75,
            evidence=["file1.py", "file2.py"]
        )

        assert template.name == "test_pattern"
        assert len(template.indicators) == 2
        assert template.effectiveness_score == 0.75

    def test_template_to_dict(self) -> None:
        """Test converting template to dictionary."""
        template = PatternTemplate(
            name="test",
            description="desc",
            pattern_type="TECHNICAL",
            indicators=["ind"],
            context={},
            effectiveness_score=0.8,
            evidence=[]
        )

        data = template.to_dict()
        assert data["name"] == "test"
        assert data["effectiveness_score"] == 0.8


class TestDecisionNodeDataClass:
    """Test DecisionNode data class."""

    def test_decision_node_creation(self) -> None:
        """Test creating DecisionNode instance."""
        node = DecisionNode(
            question="Is complexity high?",
            yes_branch=None,
            no_branch=None,
            recommendation="Apply pattern X"
        )

        assert node.question == "Is complexity high?"
        assert node.recommendation == "Apply pattern X"

    def test_decision_node_with_branches(self) -> None:
        """Test decision node with child branches."""
        yes_node = DecisionNode(
            question="Sub-question",
            yes_branch=None,
            no_branch=None,
            recommendation="Pattern A"
        )

        no_node = DecisionNode(
            question="Other sub-question",
            yes_branch=None,
            no_branch=None,
            recommendation="Pattern B"
        )

        root = DecisionNode(
            question="Root question?",
            yes_branch=yes_node,
            no_branch=no_node,
            recommendation=None
        )

        assert root.yes_branch is not None
        assert root.no_branch is not None
        assert root.yes_branch.recommendation == "Pattern A"
