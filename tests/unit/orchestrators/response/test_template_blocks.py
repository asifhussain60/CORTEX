"""
Test suite for modular template blocks system.

Module: tests.unit.orchestrators.response.test_template_blocks
Author: Asif Hussain
Created: 2026-02-07
"""

import pytest
from datetime import datetime, timedelta
from cortex.orchestrators.response.template_blocks import (
    BlockCategory,
    BlockRole,
    BlockVariables,
    TemplateBlock,
    BlockRegistry,
    BlockComposer,
    BlockCache,
    create_standard_blocks,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def registry():
    """Create fresh registry for testing."""
    reg = BlockRegistry()
    reg.clear()
    return reg


@pytest.fixture
def block_variables():
    """Create block variables."""
    return BlockVariables(data={
        "icon": "🧠",
        "title": "Test",
        "author": "Tester",
        "mode": "Test",
        "findings": "No findings",
        "context": "Test context",
        "decision": "Approved",
        "actions": "1. Do something\n2. Do another",
    })


@pytest.fixture
def standard_block():
    """Create a standard test block."""
    return TemplateBlock(
        block_id="test_block",
        name="Test Block",
        category=BlockCategory.HEADER,
        pattern="## {title}\nAuthor: {author}",
        description="Test block",
        required_variables=["title", "author"],
    )


# ============================================================================
# TESTS: TemplateBlock
# ============================================================================


class TestTemplateBlock:
    """Tests for TemplateBlock class."""
    
    def test_block_creation(self, standard_block):
        """Test block creation."""
        assert standard_block.block_id == "test_block"
        assert standard_block.name == "Test Block"
        assert standard_block.category == BlockCategory.HEADER
    
    def test_block_render_success(self, standard_block, block_variables):
        """Test successful block rendering."""
        rendered = standard_block.render(block_variables)
        assert "## Test" in rendered
        assert "Author: Tester" in rendered
    
    def test_block_render_missing_required_variable(self, standard_block):
        """Test rendering fails with missing required variable."""
        empty_vars = BlockVariables()
        with pytest.raises(ValueError, match="Missing required variable"):
            standard_block.render(empty_vars)
    
    def test_block_validation_success(self, standard_block):
        """Test block validation passes."""
        assert standard_block.validate() is True
    
    def test_block_validation_missing_id(self):
        """Test validation fails with missing block_id."""
        block = TemplateBlock(
            block_id="",
            name="Test",
            category=BlockCategory.HEADER,
            pattern="test",
            description="Test",
        )
        assert block.validate() is False
    
    def test_block_order_weight(self):
        """Test block order weight defaults to 0."""
        block = TemplateBlock(
            block_id="test",
            name="Test",
            category=BlockCategory.HEADER,
            pattern="test",
            description="Test",
        )
        assert block.order_weight == 0
    
    def test_block_enabled_by_default(self):
        """Test blocks are enabled by default."""
        block = TemplateBlock(
            block_id="test",
            name="Test",
            category=BlockCategory.HEADER,
            pattern="test",
            description="Test",
        )
        assert block.enabled is True


# ============================================================================
# TESTS: BlockVariables
# ============================================================================


class TestBlockVariables:
    """Tests for BlockVariables class."""
    
    def test_variables_creation(self):
        """Test variables creation."""
        vars = BlockVariables(data={"key": "value"})
        assert vars.get("key") == "value"
    
    def test_variables_get_missing(self):
        """Test getting missing variable returns None."""
        vars = BlockVariables()
        assert vars.get("missing") is None
    
    def test_variables_get_with_default(self):
        """Test getting missing variable with default."""
        vars = BlockVariables()
        assert vars.get("missing", "default") == "default"
    
    def test_variables_set(self):
        """Test setting variable."""
        vars = BlockVariables()
        vars.set("key", "value")
        assert vars.get("key") == "value"
    
    def test_variables_to_dict(self):
        """Test converting to dictionary."""
        vars = BlockVariables(data={"a": 1, "b": 2})
        d = vars.to_dict()
        assert d == {"a": 1, "b": 2}


# ============================================================================
# TESTS: BlockRegistry
# ============================================================================


class TestBlockRegistry:
    """Tests for BlockRegistry class."""
    
    def test_registry_singleton(self, registry):
        """Test registry is singleton."""
        registry2 = BlockRegistry()
        assert registry is registry2
    
    def test_register_block(self, registry, standard_block):
        """Test registering a block."""
        registry.register(standard_block)
        retrieved = registry.get("test_block")
        assert retrieved is standard_block
    
    def test_register_duplicate_fails(self, registry, standard_block):
        """Test registering duplicate block_id raises error."""
        registry.register(standard_block)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(standard_block)
    
    def test_register_invalid_block_fails(self, registry):
        """Test registering invalid block raises error."""
        invalid_block = TemplateBlock(
            block_id="",
            name="",
            category=BlockCategory.HEADER,
            pattern="",
            description="",
        )
        with pytest.raises(ValueError, match="Invalid block"):
            registry.register(invalid_block)
    
    def test_get_block(self, registry, standard_block):
        """Test getting registered block."""
        registry.register(standard_block)
        retrieved = registry.get("test_block")
        assert retrieved == standard_block
    
    def test_get_missing_block(self, registry):
        """Test getting missing block returns None."""
        assert registry.get("missing") is None
    
    def test_list_all_blocks(self, registry):
        """Test listing all blocks."""
        block1 = TemplateBlock(
            block_id="b1", name="Block 1", category=BlockCategory.HEADER,
            pattern="test", description="Test"
        )
        block2 = TemplateBlock(
            block_id="b2", name="Block 2", category=BlockCategory.ACTION,
            pattern="test", description="Test"
        )
        registry.register(block1)
        registry.register(block2)
        
        blocks = registry.list_blocks()
        assert len(blocks) == 2
    
    def test_list_blocks_by_category(self, registry):
        """Test listing blocks filtered by category."""
        block1 = TemplateBlock(
            block_id="b1", name="Block 1", category=BlockCategory.HEADER,
            pattern="test", description="Test"
        )
        block2 = TemplateBlock(
            block_id="b2", name="Block 2", category=BlockCategory.ACTION,
            pattern="test", description="Test"
        )
        registry.register(block1)
        registry.register(block2)
        
        header_blocks = registry.list_blocks(BlockCategory.HEADER)
        assert len(header_blocks) == 1
        assert header_blocks[0].block_id == "b1"
    
    def test_enable_disable_block(self, registry, standard_block):
        """Test enabling/disabling block."""
        registry.register(standard_block)
        
        registry.disable_block("test_block")
        block = registry.get("test_block")
        assert block.enabled is False
        
        registry.enable_block("test_block")
        block = registry.get("test_block")
        assert block.enabled is True
    
    def test_get_applicable_blocks_by_role(self, registry):
        """Test getting blocks applicable for role."""
        engineer_block = TemplateBlock(
            block_id="eng", name="Engineer Block",
            category=BlockCategory.ANALYSIS,
            pattern="test", description="Test",
            applicable_roles=[BlockRole.ENGINEER]
        )
        pm_block = TemplateBlock(
            block_id="pm", name="PM Block",
            category=BlockCategory.SYNTHESIS,
            pattern="test", description="Test",
            applicable_roles=[BlockRole.PRODUCT_MANAGER]
        )
        registry.register(engineer_block)
        registry.register(pm_block)
        
        eng_blocks = registry.get_applicable_blocks(BlockRole.ENGINEER)
        assert len(eng_blocks) == 1
        assert eng_blocks[0].block_id == "eng"


# ============================================================================
# TESTS: BlockComposer
# ============================================================================


class TestBlockComposer:
    """Tests for BlockComposer class."""
    
    def test_compose_with_specific_blocks(self, registry, block_variables):
        """Test composing response with specific blocks."""
        header_block = TemplateBlock(
            block_id="header", name="Header",
            category=BlockCategory.HEADER,
            pattern="## {title}",
            description="Test",
            required_variables=["title"]
        )
        registry.register(header_block)
        
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=block_variables,
            block_ids=["header"]
        )
        
        assert "## Test" in result
    
    def test_compose_with_role_filter(self, registry, block_variables):
        """Test composing with role-specific filtering."""
        eng_block = TemplateBlock(
            block_id="eng", name="Engineer",
            category=BlockCategory.ANALYSIS,
            pattern="Engineer content",
            description="Test",
            applicable_roles=[BlockRole.ENGINEER]
        )
        pm_block = TemplateBlock(
            block_id="pm", name="PM",
            category=BlockCategory.SYNTHESIS,
            pattern="PM content",
            description="Test",
            applicable_roles=[BlockRole.PRODUCT_MANAGER]
        )
        registry.register(eng_block)
        registry.register(pm_block)
        
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=block_variables,
        )
        
        assert "Engineer content" in result
        assert "PM content" not in result
    
    def test_compose_skips_disabled_blocks(self, registry, block_variables):
        """Test composition skips disabled blocks."""
        block = TemplateBlock(
            block_id="test", name="Test",
            category=BlockCategory.HEADER,
            pattern="content",
            description="Test",
        )
        registry.register(block)
        registry.disable_block("test")
        
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=block_variables,
            include_all=True
        )
        
        assert "content" not in result
    
    def test_compose_ordering_by_weight(self, registry, block_variables):
        """Test blocks are ordered by order_weight."""
        block1 = TemplateBlock(
            block_id="b1", name="First",
            category=BlockCategory.HEADER,
            pattern="First",
            description="Test",
            order_weight=10
        )
        block2 = TemplateBlock(
            block_id="b2", name="Second",
            category=BlockCategory.ANALYSIS,
            pattern="Second",
            description="Test",
            order_weight=5
        )
        registry.register(block1)
        registry.register(block2)
        
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=block_variables,
            include_all=True
        )
        
        # Second should appear before First
        assert result.index("Second") < result.index("First")
    
    def test_compose_handles_missing_variables_gracefully(self, registry):
        """Test composer skips blocks with missing required variables."""
        block = TemplateBlock(
            block_id="test", name="Test",
            category=BlockCategory.HEADER,
            pattern="Content: {missing_var}",
            description="Test",
            required_variables=["missing_var"]
        )
        registry.register(block)
        
        empty_vars = BlockVariables()
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=empty_vars,
            include_all=True
        )
        
        # Should not include content from block with missing variable
        assert "Content:" not in result
    
    def test_compose_include_all_flag(self, registry, block_variables):
        """Test include_all flag includes all enabled blocks."""
        block1 = TemplateBlock(
            block_id="b1", name="B1",
            category=BlockCategory.HEADER,
            pattern="B1",
            description="Test",
            applicable_roles=[BlockRole.ENGINEER]
        )
        block2 = TemplateBlock(
            block_id="b2", name="B2",
            category=BlockCategory.ANALYSIS,
            pattern="B2",
            description="Test",
            applicable_roles=[BlockRole.PRODUCT_MANAGER]
        )
        registry.register(block1)
        registry.register(block2)
        
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=block_variables,
            include_all=True
        )
        
        # Both blocks should be in result with include_all=True
        assert "B1" in result
        assert "B2" in result
    
    def test_compose_empty_result_with_no_applicable_blocks(self, registry):
        """Test composition returns empty string with no applicable blocks."""
        block = TemplateBlock(
            block_id="test", name="Test",
            category=BlockCategory.HEADER,
            pattern="content",
            description="Test",
            applicable_roles=[BlockRole.SECURITY]
        )
        registry.register(block)
        
        empty_vars = BlockVariables()
        composer = BlockComposer(registry)
        result = composer.compose(
            role=BlockRole.ENGINEER,
            variables=empty_vars,
        )
        
        assert result == ""


# ============================================================================
# TESTS: BlockCache
# ============================================================================


class TestBlockCache:
    """Tests for BlockCache class."""
    
    def test_cache_set_and_get(self):
        """Test caching and retrieval."""
        cache = BlockCache()
        vars = BlockVariables(data={"key": "value"})
        
        cache.set("block1", vars, "rendered content")
        result = cache.get("block1", vars)
        
        assert result == "rendered content"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = BlockCache()
        vars = BlockVariables(data={"key": "value"})
        
        result = cache.get("missing", vars)
        assert result is None
    
    def test_cache_ttl_expiration(self):
        """Test cache entry expires after TTL."""
        cache = BlockCache(ttl_seconds=1)
        vars = BlockVariables(data={"key": "value"})
        
        cache.set("block1", vars, "content")
        # Manually set timestamp to past
        key = list(cache.cache.keys())[0]
        cache.cache[key] = ("content", datetime.now() - timedelta(seconds=2))
        
        result = cache.get("block1", vars)
        assert result is None
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = BlockCache()
        vars = BlockVariables(data={"key": "value"})
        cache.set("block1", vars, "content")
        
        cache.clear()
        assert cache.get("block1", vars) is None


# ============================================================================
# TESTS: Standard Blocks Creation
# ============================================================================


class TestStandardBlocks:
    """Tests for standard blocks creation."""
    
    def test_create_standard_blocks(self):
        """Test creating standard blocks."""
        blocks = create_standard_blocks()
        assert len(blocks) > 0
    
    def test_standard_blocks_have_unique_ids(self):
        """Test standard blocks have unique IDs."""
        blocks = create_standard_blocks()
        ids = [b.block_id for b in blocks]
        assert len(ids) == len(set(ids))
    
    def test_standard_blocks_are_valid(self):
        """Test all standard blocks are valid."""
        blocks = create_standard_blocks()
        for block in blocks:
            assert block.validate() is True
    
    def test_standard_blocks_have_categories(self):
        """Test standard blocks have valid categories."""
        blocks = create_standard_blocks()
        for block in blocks:
            assert block.category in BlockCategory
    
    def test_standard_blocks_ordered(self):
        """Test standard blocks have increasing order weights."""
        blocks = create_standard_blocks()
        weights = [b.order_weight for b in blocks]
        # Should be sorted (non-strictly, can have ties)
        for i in range(len(weights) - 1):
            assert weights[i] <= weights[i + 1]
    
    def test_standard_header_block_exists(self):
        """Test standard blocks include header block."""
        blocks = create_standard_blocks()
        block_ids = [b.block_id for b in blocks]
        assert "header" in block_ids
    
    def test_standard_blocks_have_required_variables(self):
        """Test standard blocks specify required variables."""
        blocks = create_standard_blocks()
        for block in blocks:
            # All blocks should have required_variables list (even if empty)
            assert isinstance(block.required_variables, list)
    
    def test_standard_security_block_exists(self):
        """Test standard blocks include security block."""
        blocks = create_standard_blocks()
        block_ids = [b.block_id for b in blocks]
        assert "security" in block_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
