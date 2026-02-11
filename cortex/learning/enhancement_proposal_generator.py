"""
AC-PHASE41-003: EnhancementProposalGenerator creates valid enhancement specs

EnhancementProposalGenerator - Extract and classify enhancements from chat content.

Analyzes chat conversations to identify:
- Governance enhancements (CORE rules, type hints, docstrings)
- Capability enhancements (new MCP tools, orchestrators)
- Workflow enhancements (TDD improvements, automation)

Generates structured enhancement proposals with confidence scoring.
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set


class EnhancementCategory(Enum):
    """Categories of enhancements."""
    GOVERNANCE = "GOVERNANCE"
    CAPABILITY = "CAPABILITY"
    WORKFLOW = "WORKFLOW"
    DOCUMENTATION = "DOCUMENTATION"
    PERFORMANCE = "PERFORMANCE"
    TESTING = "TESTING"


@dataclass
class EnhancementProposal:
    """
    Structured enhancement proposal extracted from chat.

    Attributes:
        id: Unique identifier (ENH-XXX format)
        description: Human-readable description
        category: Enhancement category
        confidence_score: Confidence rating (5-10 scale)
        source_file: Origin file path
        timestamp: When extracted
        core_rule_ref: Referenced CORE rule (if any)
        context: Additional context from chat
        code_references: Code snippets or file references
    """
    id: str
    description: str
    category: EnhancementCategory
    confidence_score: float
    source_file: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    core_rule_ref: Optional[str] = None
    context: Optional[str] = None
    code_references: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category.value,
            "confidence_score": self.confidence_score,
            "source_file": self.source_file,
            "timestamp": self.timestamp,
            "core_rule_ref": self.core_rule_ref,
            "context": self.context,
            "code_references": self.code_references,
        }


class EnhancementProposalGenerator:
    """
    Generate enhancement proposals from chat content.

    Uses pattern matching and keyword analysis to identify and classify
    enhancements mentioned in Copilot chat conversations.

    Achieves high precision through:
    - Multi-pattern matching for each category
    - Context window analysis
    - CORE rule reference extraction
    - Confidence scoring based on evidence
    """

    def __init__(self):
        """Initialize generator with patterns and keywords."""
        self.patterns = self._compile_patterns()
        self.keywords = self._build_keyword_map()
        self._seen_hashes: Set[str] = set()

    def _compile_patterns(self) -> dict:
        """
        Compile regex patterns for enhancement detection.

        Returns:
            Dictionary mapping categories to detection patterns
        """
        return {
            "governance": [
                re.compile(r'type\s+hints?', re.IGNORECASE),
                re.compile(r'docstrings?', re.IGNORECASE),
                re.compile(r'CORE-\d+', re.IGNORECASE),
                re.compile(r'governance|compliance', re.IGNORECASE),
                re.compile(r'audit\s+trail', re.IGNORECASE),
            ],
            "capability": [
                re.compile(r'MCP\s+tool', re.IGNORECASE),
                re.compile(r'cortex_\w+', re.IGNORECASE),
                re.compile(r'new\s+(orchestrator|capability|feature)', re.IGNORECASE),
                re.compile(r'orchestrator\s+created', re.IGNORECASE),
            ],
            "workflow": [
                re.compile(r'TDD|test[-\s]driven', re.IGNORECASE),
                re.compile(r'automation|automat(e|ic)', re.IGNORECASE),
                re.compile(r'RED→GREEN→REFACTOR', re.IGNORECASE),
                re.compile(r'workflow\s+improvement', re.IGNORECASE),
            ],
            "documentation": [
                re.compile(r'documentation|docs?', re.IGNORECASE),
                re.compile(r'README|guide', re.IGNORECASE),
            ],
            "performance": [
                re.compile(r'performance|optimization', re.IGNORECASE),
                re.compile(r'caching|cache', re.IGNORECASE),
            ],
            "testing": [
                re.compile(r'\d+\s+tests?\s+passing', re.IGNORECASE),
                re.compile(r'test\s+coverage', re.IGNORECASE),
                re.compile(r'unit\s+tests?', re.IGNORECASE),
            ],
        }

    def _build_keyword_map(self) -> dict:
        """
        Build keyword map for category classification.

        Returns:
            Dictionary mapping categories to keyword lists
        """
        return {
            EnhancementCategory.GOVERNANCE: [
                "type hint", "docstring", "CORE-", "governance", "compliance",
                "audit trail", "enforcement", "validation", "security"
            ],
            EnhancementCategory.CAPABILITY: [
                "MCP tool", "cortex_", "orchestrator", "capability", "feature",
                "integration", "API", "endpoint"
            ],
            EnhancementCategory.WORKFLOW: [
                "TDD", "automation", "workflow", "pipeline", "CI/CD",
                "deployment", "RED→GREEN→REFACTOR"
            ],
            EnhancementCategory.DOCUMENTATION: [
                "documentation", "docs", "README", "guide", "tutorial"
            ],
            EnhancementCategory.PERFORMANCE: [
                "performance", "optimization", "caching", "speed", "latency"
            ],
            EnhancementCategory.TESTING: [
                "test", "coverage", "unit test", "integration test", "e2e"
            ],
        }

    def generate_proposals(
        self,
        content: str,
        source_file: str = "unknown",
        deduplicate: bool = True
    ) -> List[EnhancementProposal]:
        """
        Generate enhancement proposals from content.

        Args:
            content: Chat content to analyze
            source_file: Source file path
            deduplicate: Remove duplicate proposals

        Returns:
            List of enhancement proposals
        """
        proposals = []
        lines = content.split('\n')

        # Extract completion markers (✅ lines indicate enhancements)
        completion_lines = []
        for i, line in enumerate(lines):
            if '✅' in line and len(line.strip()) > 3:
                completion_lines.append((i, line.strip()))

        # Generate proposals from completion lines
        for line_num, line in completion_lines:
            # Get context window (3 lines before, current, 2 after)
            context_start = max(0, line_num - 3)
            context_end = min(len(lines), line_num + 3)
            context = '\n'.join(lines[context_start:context_end])

            # Extract description (remove ✅ marker)
            description = line.replace('✅', '').strip()

            if len(description) < 10:  # Skip very short descriptions
                continue

            # Classify enhancement
            category = self.classify_enhancement(description + "\n" + context)

            # Extract CORE rule reference if present
            core_rule = self._extract_core_rule(description + "\n" + context)

            # Calculate confidence score
            confidence = self._calculate_confidence(description, context, core_rule)

            # Generate unique ID
            proposal_id = self._generate_id(description, proposals)

            # Extract code references
            code_refs = self._extract_code_references(context)

            proposal = EnhancementProposal(
                id=proposal_id,
                description=description,
                category=category,
                confidence_score=confidence,
                source_file=source_file,
                core_rule_ref=core_rule,
                context=context,
                code_references=code_refs
            )

            # Deduplicate if enabled
            if deduplicate:
                proposal_hash = self._hash_proposal(proposal)
                if proposal_hash in self._seen_hashes:
                    continue  # Skip duplicate
                self._seen_hashes.add(proposal_hash)

            proposals.append(proposal)

        return proposals

    def classify_enhancement(self, text: str) -> EnhancementCategory:
        """
        Classify enhancement by analyzing keywords and patterns.

        Args:
            text: Text to analyze

        Returns:
            Most likely enhancement category
        """
        category_scores = {cat: 0 for cat in EnhancementCategory}

        text_lower = text.lower()

        # Score by keyword matching
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    category_scores[category] += 1

        # Score by pattern matching
        for category_name, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    # Map category name to enum
                    if category_name == "governance":
                        category_scores[EnhancementCategory.GOVERNANCE] += 2
                    elif category_name == "capability":
                        category_scores[EnhancementCategory.CAPABILITY] += 2
                    elif category_name == "workflow":
                        category_scores[EnhancementCategory.WORKFLOW] += 2
                    elif category_name == "documentation":
                        category_scores[EnhancementCategory.DOCUMENTATION] += 2
                    elif category_name == "performance":
                        category_scores[EnhancementCategory.PERFORMANCE] += 2
                    elif category_name == "testing":
                        category_scores[EnhancementCategory.TESTING] += 2

        # Return category with highest score
        if max(category_scores.values()) == 0:
            return EnhancementCategory.WORKFLOW  # Default

        return max(category_scores.items(), key=lambda x: x[1])[0]

    def _extract_core_rule(self, text: str) -> Optional[str]:
        """
        Extract CORE rule reference from text.

        Args:
            text: Text to analyze

        Returns:
            CORE rule ID (e.g., "CORE-011") or None
        """
        pattern = re.compile(r'CORE-\d+')
        match = pattern.search(text)
        return match.group(0) if match else None

    def _calculate_confidence(
        self,
        description: str,
        context: str,
        core_rule: Optional[str]
    ) -> float:
        """
        Calculate confidence score for enhancement proposal.

        Factors:
        - Description length and detail (0-3 points)
        - Context richness (0-3 points)
        - CORE rule reference (+2 points)
        - Test evidence (0-2 points)

        Args:
            description: Enhancement description
            context: Context window
            core_rule: CORE rule reference if present

        Returns:
            Confidence score (5.0-10.0)
        """
        score = 5.0  # Base score

        # Description quality (0-3 points)
        if len(description) > 50:
            score += 1.0
        if len(description) > 100:
            score += 1.0
        if re.search(r'\d+\s+(LOC|tests?|files?)', description, re.IGNORECASE):
            score += 1.0

        # Context richness (0-3 points)
        context_lines = len(context.split('\n'))
        if context_lines >= 3:
            score += 1.0
        if context_lines >= 5:
            score += 1.0
        if '**User:**' in context and '**GitHub Copilot:**' in context:
            score += 1.0

        # CORE rule reference (+2 points)
        if core_rule:
            score += 2.0

        # Test evidence (0-2 points)
        if re.search(r'\d+\s+tests?\s+passing', context, re.IGNORECASE):
            score += 2.0
        elif 'test' in context.lower():
            score += 1.0

        # Clamp to 5-10 range
        return min(10.0, max(5.0, score))

    def _generate_id(self, description: str, existing: List[EnhancementProposal]) -> str:
        """
        Generate unique enhancement ID.

        Args:
            description: Enhancement description
            existing: List of existing proposals

        Returns:
            Unique ID in format ENH-XXX
        """
        # Use hash of description for deterministic ID
        desc_hash = hashlib.md5(description.encode()).hexdigest()[:6]
        base_id = f"ENH-{desc_hash.upper()}"

        # Ensure uniqueness
        existing_ids = {p.id for p in existing}
        if base_id not in existing_ids:
            return base_id

        # Add suffix if collision
        counter = 1
        while f"{base_id}-{counter}" in existing_ids:
            counter += 1
        return f"{base_id}-{counter}"

    def _extract_code_references(self, context: str) -> List[str]:
        """
        Extract code references from context.

        Args:
            context: Context text

        Returns:
            List of code references (file paths, function names)
        """
        refs = []

        # Extract file paths
        file_pattern = re.compile(r'[\w/]+\.py')
        refs.extend(file_pattern.findall(context))

        # Extract cortex_ tool names
        tool_pattern = re.compile(r'cortex_\w+')
        refs.extend(tool_pattern.findall(context))

        # Extract orchestrator names
        orch_pattern = re.compile(r'(\w+Orchestrator)')
        refs.extend(orch_pattern.findall(context))

        return list(set(refs))  # Remove duplicates

    def _hash_proposal(self, proposal: EnhancementProposal) -> str:
        """
        Generate hash for proposal to detect duplicates.

        Args:
            proposal: Enhancement proposal

        Returns:
            Hash string
        """
        # Hash based on description and category
        content = f"{proposal.description}_{proposal.category.value}"
        return hashlib.md5(content.encode()).hexdigest()
