"""
Modular template blocks system for composable response generation.
Provides atomic blocks that can be individually used or composed.

Module: cortex.orchestrators.response.template_blocks
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

# ============================================================================
# ENUMERATIONS
# ============================================================================


class BlockCategory(str, Enum):
    """Block category enumeration."""

    HEADER = "header"
    """Response header block"""

    ANALYSIS = "analysis"
    """Analysis and findings blocks"""

    SYNTHESIS = "synthesis"
    """Synthesis and conclusions"""

    ACTION = "action"
    """Action blocks (next steps, decisions)"""


class BlockRole(str, Enum):
    """Target role for block rendering."""

    ENGINEER = "engineer"
    PRODUCT_MANAGER = "product_manager"
    BUSINESS = "business"
    ARCHITECT = "architect"
    SECURITY = "security"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class BlockVariables:
    """Variables for block rendering."""

    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get variable value."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set variable value."""
        self.data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.data.copy()


@dataclass
class TemplateBlock:
    """Base template block specification."""

    block_id: str
    """Unique block identifier"""

    name: str
    """Human-readable block name"""

    category: BlockCategory
    """Block category"""

    pattern: str
    """Template pattern (markdown with {variables})"""

    description: str
    """Block description"""

    enabled: bool = True
    """Whether block is enabled by default"""

    order_weight: int = 0
    """Rendering order (lower = earlier)"""

    required_variables: List[str] = field(default_factory=list)
    """Required variables for rendering"""

    optional_variables: List[str] = field(default_factory=list)
    """Optional variables"""

    applicable_roles: List[BlockRole] = field(default_factory=lambda: list(BlockRole))
    """Roles this block is applicable for"""

    dependencies: List[str] = field(default_factory=list)
    """Dependent block IDs"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""

    def render(self, variables: BlockVariables) -> str:
        """
        Render block with variables.

        Args:
            variables: BlockVariables with data

        Returns:
            Rendered block content

        Raises:
            ValueError: If required variables missing
        """
        # Check required variables
        for var in self.required_variables:
            if var not in variables.data:
                raise ValueError(f"Missing required variable: {var}")

        # Render pattern
        return self.pattern.format(**variables.data)

    def validate(self) -> bool:
        """Validate block specification."""
        return (
            bool(self.block_id)
            and bool(self.name)
            and bool(self.pattern)
            and isinstance(self.category, BlockCategory)
        )


# ============================================================================
# BLOCK REGISTRY
# ============================================================================


class BlockRegistry:
    """Registry for managing template blocks."""

    _instance: Optional["BlockRegistry"] = None
    _blocks: Dict[str, TemplateBlock] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, block: TemplateBlock) -> None:
        """
        Register a template block.

        Args:
            block: TemplateBlock to register

        Raises:
            ValueError: If block_id already registered
        """
        if block.block_id in self._blocks:
            raise ValueError(f"Block already registered: {block.block_id}")

        if not block.validate():
            raise ValueError(f"Invalid block: {block.block_id}")

        self._blocks[block.block_id] = block

    def get(self, block_id: str) -> Optional[TemplateBlock]:
        """Get block by ID."""
        return self._blocks.get(block_id)

    def list_blocks(self, category: Optional[BlockCategory] = None) -> List[TemplateBlock]:
        """
        List all blocks, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of blocks
        """
        blocks = list(self._blocks.values())
        if category:
            blocks = [b for b in blocks if b.category == category]
        return sorted(blocks, key=lambda b: b.order_weight)

    def enable_block(self, block_id: str) -> None:
        """Enable block."""
        if block_id in self._blocks:
            self._blocks[block_id].enabled = True

    def disable_block(self, block_id: str) -> None:
        """Disable block."""
        if block_id in self._blocks:
            self._blocks[block_id].enabled = False

    def get_applicable_blocks(self, role: BlockRole) -> List[TemplateBlock]:
        """Get blocks applicable for role."""
        blocks = self.list_blocks()
        return [b for b in blocks if b.enabled and role in b.applicable_roles]

    def clear(self) -> None:
        """Clear all blocks (for testing)."""
        self._blocks.clear()


# ============================================================================
# STANDARD BLOCKS
# ============================================================================


def create_standard_blocks() -> List[TemplateBlock]:
    """Create standard template blocks."""

    return [
        TemplateBlock(
            block_id="header",
            name="Header Block",
            category=BlockCategory.HEADER,
            pattern="## {icon} {title}\n**Author:** {author} | **Mode:** {mode} ✅\n\n---",
            description="Response header with icon, title, author, mode",
            order_weight=0,
            required_variables=["icon", "title", "author", "mode"],
            optional_variables=["orchestrator"],
        ),
        TemplateBlock(
            block_id="security",
            name="Security Analysis Block",
            category=BlockCategory.ANALYSIS,
            pattern="### 🔒 Security Analysis\n\n{findings}\n",
            description="P0-P2 security findings table",
            order_weight=10,
            required_variables=["findings"],
            applicable_roles=[BlockRole.ARCHITECT, BlockRole.SECURITY, BlockRole.ENGINEER],
        ),
        TemplateBlock(
            block_id="test_quality",
            name="Test Quality Block",
            category=BlockCategory.ANALYSIS,
            pattern="### 🧪 Test Quality\n\n{fluff_analysis}\n",
            description="FLUFF test detection results",
            order_weight=20,
            required_variables=["fluff_analysis"],
            applicable_roles=[BlockRole.ENGINEER, BlockRole.ARCHITECT],
        ),
        TemplateBlock(
            block_id="code_issues",
            name="Code Issues Block",
            category=BlockCategory.ANALYSIS,
            pattern="### ⚠️ Hidden Issues\n\n{issues}\n",
            description="Performance, memory, concurrency issues",
            order_weight=30,
            required_variables=["issues"],
            applicable_roles=[BlockRole.ENGINEER, BlockRole.ARCHITECT],
        ),
        TemplateBlock(
            block_id="business_context",
            name="Business Context Block",
            category=BlockCategory.SYNTHESIS,
            pattern="### 📊 Business Context\n\n{context}\n",
            description="Executive/PM/metrics summaries",
            order_weight=50,
            required_variables=["context"],
            applicable_roles=[BlockRole.PRODUCT_MANAGER, BlockRole.BUSINESS, BlockRole.ARCHITECT],
        ),
        TemplateBlock(
            block_id="verdict",
            name="Verdict Block",
            category=BlockCategory.ACTION,
            pattern="### ✅ Verdict\n\n{decision}\n",
            description="Final decision and approval gate",
            order_weight=90,
            required_variables=["decision"],
            applicable_roles=list(BlockRole),
        ),
        TemplateBlock(
            block_id="next_steps",
            name="Next Steps Block",
            category=BlockCategory.ACTION,
            pattern="### 🚀 Next Steps\n\n{actions}\n",
            description="Recommended actions and decision gates",
            order_weight=100,
            required_variables=["actions"],
            applicable_roles=list(BlockRole),
        ),
    ]


# ============================================================================
# BLOCK COMPOSER
# ============================================================================


class BlockComposer:
    """Assembles blocks into complete responses."""

    def __init__(self, registry: Optional[BlockRegistry] = None):
        self.registry = registry or BlockRegistry()

    def compose(
        self,
        role: BlockRole,
        variables: BlockVariables,
        block_ids: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> str:
        """
        Compose response from blocks.

        Args:
            role: Target role
            variables: Variables for rendering
            block_ids: Specific blocks to include (optional)
            include_all: Include all blocks regardless of role (optional)

        Returns:
            Composed response
        """
        blocks: List[TemplateBlock] = []

        if block_ids:
            # Use specific blocks
            for bid in block_ids:
                block = self.registry.get(bid)
                if block:
                    blocks.append(block)
        elif include_all:
            # Include all enabled blocks
            all_blocks = self.registry.list_blocks()
            blocks = [b for b in all_blocks if b.enabled]
        else:
            # Get applicable blocks for role
            blocks = self.registry.get_applicable_blocks(role)

        # Sort by order weight
        blocks = sorted(blocks, key=lambda b: b.order_weight)

        # Render blocks
        rendered = []
        for block in blocks:
            try:
                rendered.append(block.render(variables))
            except ValueError:
                # Skip blocks with missing variables
                pass

        return "\n".join(rendered)


# ============================================================================
# BLOCK CACHE
# ============================================================================


class BlockCache:
    """LRU cache for block renders with TTL."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple[str, datetime]] = {}

    def _make_key(self, block_id: str, variables: BlockVariables) -> str:
        """Create cache key from block ID and variables."""
        vars_json = json.dumps(variables.to_dict(), sort_keys=True, default=str)
        vars_hash = hashlib.md5(vars_json.encode()).hexdigest()
        return f"{block_id}:{vars_hash}"

    def get(self, block_id: str, variables: BlockVariables) -> Optional[str]:
        """Get cached block render."""
        key = self._make_key(block_id, variables)

        if key not in self.cache:
            return None

        rendered, timestamp = self.cache[key]

        # Check TTL
        if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            return None

        return rendered

    def set(self, block_id: str, variables: BlockVariables, rendered: str) -> None:
        """Cache block render."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        key = self._make_key(block_id, variables)
        self.cache[key] = (rendered, datetime.now())

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "BlockCategory",
    "BlockRole",
    "BlockVariables",
    "TemplateBlock",
    "BlockRegistry",
    "BlockComposer",
    "BlockCache",
    "create_standard_blocks",
]
