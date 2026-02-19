"""
Semantic Block Loader & Assembly Engine.

Brain terminology (HIGH-LEVEL):
- Perception: Load blocks from registry (cortex_intelligence perception)
- Reasoning: Validate composition + anti-duplication (cortex_intelligence reasoning)
- Action: Assemble + render blocks (cortex_intelligence action)

Authority: ENH-089 | Production-ready block assembly with personality enforcement
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class BlockAssemblyError(Exception):
    """Raised when block assembly violates composition rules."""

    pass


class PersonalityError(Exception):
    """Raised when personality guidelines are violated."""

    pass


@dataclass
class Block:
    """Semantic response block with personality guardrails."""

    id: str
    name: str
    length_words: int
    purpose: str
    content_template: str
    format_spec: Dict
    personality_guidelines: Dict
    usage_rules: List[str]
    vscode_rendering: Dict = field(default_factory=dict)


@dataclass
class AssemblyResult:
    """Result of block assembly operation."""

    blocks_assembled: List[str]
    total_words: int
    personality_consistent: bool
    duplication_check_passed: bool
    rendering_valid: bool
    assembled_content: str = ""
    warnings: List[str] = field(default_factory=list)


class SemanticBlockLoader:
    """
    Perception layer: Load and validate semantic blocks from registry.

    Neurocognitive mapping:
    - Discovers blocks from cortex_intelligence (distributed storage)
    - Validates metadata completeness
    - Ensures personality guidelines present
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize loader with registry path."""
        if registry_path is None:
            # Find registry relative to this file
            base = Path(__file__).parent
            registry_path = (
                base.parent.parent
                / "cortex-registry/artifacts/templates/content-blocks.yaml"
            )

        self.registry_path = registry_path
        self._blocks: Optional[Dict[str, Block]] = None
        self._personality_charter: Optional[Dict] = None

    def load_blocks(self) -> Dict[str, Block]:
        """Load all blocks from registry."""
        if self._blocks is not None:
            return self._blocks

        with open(self.registry_path) as f:
            registry = yaml.safe_load(f)

        # Load personality charter first (before loading blocks)
        if "personality_charter" in registry:
            self._personality_charter = registry["personality_charter"]

        blocks_data = registry.get("blocks", {})

        self._blocks = {}
        for block_key, block_data in blocks_data.items():
            block = Block(
                id=block_data["id"],
                name=block_data["name"],
                length_words=block_data.get("length_words", 0)
                if isinstance(block_data.get("length_words"), int)
                else 0,
                purpose=block_data["purpose"],
                content_template=block_data.get("content_template", ""),
                format_spec=block_data.get("format", {}),
                personality_guidelines=block_data.get("personality_guidelines", {}),
                usage_rules=block_data.get("usage_rules", []),
                vscode_rendering=block_data.get("format", {}).get(
                    "vscode_rendering", {}
                ),
            )
            self._blocks[block_key] = block

        return self._blocks

    def get_personality_charter(self) -> Dict:
        """Get global personality guidelines."""
        if self._personality_charter is None:
            self.load_blocks()
        return self._personality_charter or {}


class SemanticBlockReasoner:
    """
    Reasoning layer: Validate block composition and anti-duplication.

    Neurocognitive mapping:
    - Analyzes block compatibility (reasoning)
    - Detects duplication violations (error detection)
    - Validates assembly rules (constraint satisfaction)
    """

    def __init__(self, loader: SemanticBlockLoader):
        """Initialize reasoner with loader."""
        self.loader = loader
        self.blocks = loader.load_blocks()
        self._assembly_rules = self._load_assembly_rules()

    def _load_assembly_rules(self) -> Dict:
        """Load assembly rules from registry."""
        with open(self.loader.registry_path) as f:
            registry = yaml.safe_load(f)
        return registry.get("assembly_rules", {})

    def validate_composition(
        self, block_names: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate block composition rules.

        Returns: (is_valid, warnings_list)
        """
        warnings = []

        # Rule 1: No more than 800 words total
        total_words = sum(
            self.blocks[name].length_words
            for name in block_names
            if name in self.blocks
        )
        if total_words > 800:
            warnings.append(f"Total words {total_words} exceeds 800-word limit")

        # Rule 2: NEXT-STEPS only once, at end
        next_steps_count = block_names.count("next_steps")
        if next_steps_count > 1:
            warnings.append("NEXT-STEPS block appears multiple times (should be once)")
        if next_steps_count == 1 and block_names[-1] != "next_steps":
            warnings.append("NEXT-STEPS block must appear at end")

        # Rule 3: Check compatibility pairs
        with open(self.loader.registry_path) as f:
            registry = yaml.safe_load(f)
        compat = registry.get("compatibility", {})

        for i, block_name in enumerate(block_names):
            if block_name not in compat:
                continue

            block_compat = compat[block_name]
            avoid_list = block_compat.get("avoid_with", [])

            # Check if any following blocks are in avoid_with list
            for other_name in block_names[i + 1 :]:
                if other_name in avoid_list:
                    warnings.append(
                        f"Incompatible blocks: '{block_name}' should avoid "
                        f"'{other_name}'"
                    )

        return len(warnings) == 0, warnings

    def check_duplication(self, block_names: List[str]) -> Tuple[bool, List[str]]:
        """
        Check for content duplication across blocks.

        Returns: (is_clean, duplication_warnings)
        """
        warnings = []

        # Simple check: verify no duplicate block names
        seen = set()
        for name in block_names:
            if name in seen:
                warnings.append(f"Block '{name}' appears multiple times")
            seen.add(name)

        # Check for duplicate headers (in actual rendering)
        # This would require parsing content, so keep simple for now
        headers = []
        for name in block_names:
            if name in self.blocks:
                template = self.blocks[name].content_template
                # Extract ## headers
                for line in template.split("\n"):
                    if line.startswith("##"):
                        headers.append(line)

        seen_headers = set()
        for header in headers:
            if header in seen_headers:
                warnings.append(f"Duplicate header found: {header}")
            seen_headers.add(header)

        return len(warnings) == 0, warnings


class SemanticBlockAssembler:
    """
    Action layer: Assemble and render semantic blocks with personality consistency.

    Neurocognitive mapping:
    - Selects appropriate blocks (action selection)
    - Assembles with personality enforcement (personality_charter)
    - Renders for VSCode (rendering_standards)
    """

    def __init__(self, loader: SemanticBlockLoader, reasoner: SemanticBlockReasoner):
        """Initialize assembler with loader and reasoner."""
        self.loader = loader
        self.reasoner = reasoner
        self.blocks = loader.load_blocks()
        self.personality_charter = loader.get_personality_charter()

    def assemble(
        self, block_names: List[str], enforce_personality: bool = True
    ) -> AssemblyResult:
        """
        Assemble blocks into final response.

        Args:
            block_names: List of block keys to assemble
            enforce_personality: Whether to enforce personality guidelines

        Returns:
            AssemblyResult with assembled content and validation status
        """
        # Validate composition
        comp_valid, comp_warnings = self.reasoner.validate_composition(block_names)

        # Check duplication
        dup_valid, dup_warnings = self.reasoner.check_duplication(block_names)

        # Check rendering compatibility
        render_valid = self._validate_rendering(block_names)

        # Check personality consistency
        personality_valid = True
        if enforce_personality:
            personality_valid = self._validate_personality(block_names)

        # Assemble content
        assembled_content = self._render_blocks(block_names)

        # Calculate totals
        total_words = sum(
            self.blocks[name].length_words
            for name in block_names
            if name in self.blocks
        )

        all_warnings = comp_warnings + dup_warnings
        if not personality_valid:
            all_warnings.append("Personality consistency warnings detected")

        return AssemblyResult(
            blocks_assembled=block_names,
            total_words=total_words,
            personality_consistent=personality_valid,
            duplication_check_passed=dup_valid,
            rendering_valid=render_valid,
            assembled_content=assembled_content,
            warnings=all_warnings,
        )

    def _validate_rendering(self, block_names: List[str]) -> bool:
        """Verify VSCode rendering compatibility."""
        for name in block_names:
            if name not in self.blocks:
                return False

            block = self.blocks[name]
            # Check for forbidden rendering patterns in template (not in code examples)
            # Tree chars in code blocks (```) are allowed; in content they're not
            lines = block.content_template.split("\n")
            in_code_block = False
            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                elif not in_code_block and ("├─" in line or "└─" in line):
                    return False  # Tree chars not allowed outside code blocks

        return True

    def _validate_personality(self, block_names: List[str]) -> bool:
        """Verify personality guidelines are consistent."""
        if not self.personality_charter:
            return True  # No charter defined

        # All blocks should follow core_traits from charter
        core_traits = self.personality_charter.get("core_traits", [])

        for name in block_names:
            if name not in self.blocks:
                continue

            block = self.blocks[name]
            guidelines = block.personality_guidelines

            # Verify each block has personality_guidelines defined
            if not guidelines:
                return False

            # Could do more sophisticated checking here
            # For now, just verify the section exists

        return True

    def _render_blocks(self, block_names: List[str]) -> str:
        """Render assembled blocks into final content."""
        content_parts = []

        for name in block_names:
            if name not in self.blocks:
                continue

            block = self.blocks[name]
            content_parts.append(block.content_template)

        return "\n\n".join(content_parts)
