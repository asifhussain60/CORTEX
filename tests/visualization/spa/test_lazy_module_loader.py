"""
Tests for SPA Lazy Module Loader.

Phase: 14 - LENS Dashboard
Task: 017 - SPA Lazy Module Loader
"""

import pytest

from cortex.visualization.spa.lazy_module_loader import (
    LazyModuleLoader,
    ModuleConfig,
    create_default_loader,
)


class TestModuleConfig:
    """Test ModuleConfig dataclass."""

    def test_module_config_creation(self) -> None:
        """Test creating module configuration."""
        config = ModuleConfig(
            name="test",
            path="/static/test.js",
            dependencies=["dep1", "dep2"],
            priority=1,
            defer=True,
            async_load=False,
        )

        assert config.name == "test"
        assert config.path == "/static/test.js"
        assert config.dependencies == ["dep1", "dep2"]
        assert config.priority == 1
        assert config.defer is True
        assert config.async_load is False

    def test_module_config_defaults(self) -> None:
        """Test module config default values."""
        config = ModuleConfig(
            name="test", path="/static/test.js", dependencies=[]
        )

        assert config.priority == 2  # Normal priority
        assert config.defer is True
        assert config.async_load is False


class TestLazyModuleLoader:
    """Test LazyModuleLoader class."""

    def test_initialization(self) -> None:
        """Test loader initialization."""
        loader = LazyModuleLoader()

        assert len(loader.modules) == 0
        assert len(loader.loaded_modules) == 0

    def test_add_module(self) -> None:
        """Test adding module to loader."""
        loader = LazyModuleLoader()

        config = ModuleConfig(
            name="test", path="/static/test.js", dependencies=[]
        )
        loader.add_module(config)

        assert "test" in loader.modules
        assert loader.modules["test"] == config

    def test_add_multiple_modules(self) -> None:
        """Test adding multiple modules."""
        loader = LazyModuleLoader()

        configs = [
            ModuleConfig(name="alpine", path="/alpine.js", dependencies=[]),
            ModuleConfig(name="d3", path="/d3.js", dependencies=[]),
            ModuleConfig(name="mermaid", path="/mermaid.js", dependencies=["d3"]),
        ]

        for config in configs:
            loader.add_module(config)

        assert len(loader.modules) == 3
        assert "alpine" in loader.modules
        assert "d3" in loader.modules
        assert "mermaid" in loader.modules

    def test_generate_loader_script_empty(self) -> None:
        """Test generating script with no modules."""
        loader = LazyModuleLoader()

        script = loader.generate_loader_script()

        assert "No modules to load" in script

    def test_generate_loader_script_with_modules(self) -> None:
        """Test generating loader script with modules."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="alpine", path="/alpine.js", dependencies=[])
        )
        loader.add_module(
            ModuleConfig(name="d3", path="/d3.js", dependencies=[])
        )

        script = loader.generate_loader_script()

        # Verify script structure
        assert "Lazy Module Loader" in script
        assert "function loadModule" in script
        assert "function loadAll" in script
        assert "window.CortexLoader" in script

        # Verify module configurations
        assert "'alpine'" in script
        assert "'d3'" in script
        assert "'/alpine.js'" in script
        assert "'/d3.js'" in script

    def test_generate_loader_script_with_dependencies(self) -> None:
        """Test script generation with module dependencies."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="base", path="/base.js", dependencies=[])
        )
        loader.add_module(
            ModuleConfig(
                name="plugin", path="/plugin.js", dependencies=["base"]
            )
        )

        script = loader.generate_loader_script()

        assert "'base'" in script
        assert "'plugin'" in script
        assert "dependencies: ['base']" in script

    def test_generate_loader_script_priority_ordering(self) -> None:
        """Test modules are ordered by priority in script."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(
                name="low", path="/low.js", dependencies=[], priority=3
            )
        )
        loader.add_module(
            ModuleConfig(
                name="critical", path="/critical.js", dependencies=[], priority=0
            )
        )
        loader.add_module(
            ModuleConfig(
                name="high", path="/high.js", dependencies=[], priority=1
            )
        )

        script = loader.generate_loader_script()

        # Find positions in script
        critical_pos = script.find("'critical'")
        high_pos = script.find("'high'")
        low_pos = script.find("'low'")

        # Verify order: critical < high < low
        assert critical_pos < high_pos < low_pos

    def test_generate_inline_script(self) -> None:
        """Test generating inline script tag."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="test", path="/test.js", dependencies=[])
        )

        html = loader.generate_inline_script()

        assert html.startswith("<script>")
        assert html.endswith("</script>")
        assert "function loadModule" in html

    def test_get_load_order_no_dependencies(self) -> None:
        """Test load order with no dependencies."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(
                name="alpine", path="/alpine.js", dependencies=[], priority=0
            )
        )
        loader.add_module(
            ModuleConfig(
                name="d3", path="/d3.js", dependencies=[], priority=1
            )
        )

        order = loader.get_load_order()

        assert order == ["alpine", "d3"]

    def test_get_load_order_with_dependencies(self) -> None:
        """Test load order respects dependencies."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="base", path="/base.js", dependencies=[])
        )
        loader.add_module(
            ModuleConfig(
                name="plugin", path="/plugin.js", dependencies=["base"]
            )
        )
        loader.add_module(
            ModuleConfig(
                name="extension",
                path="/extension.js",
                dependencies=["plugin"],
            )
        )

        order = loader.get_load_order()

        # base must come before plugin, plugin before extension
        assert order.index("base") < order.index("plugin")
        assert order.index("plugin") < order.index("extension")

    def test_get_load_order_complex_dependencies(self) -> None:
        """Test load order with complex dependency graph."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="a", path="/a.js", dependencies=[])
        )
        loader.add_module(
            ModuleConfig(name="b", path="/b.js", dependencies=["a"])
        )
        loader.add_module(
            ModuleConfig(name="c", path="/c.js", dependencies=["a"])
        )
        loader.add_module(
            ModuleConfig(name="d", path="/d.js", dependencies=["b", "c"])
        )

        order = loader.get_load_order()

        # a must be first
        assert order[0] == "a"
        # b and c must come before d
        assert order.index("b") < order.index("d")
        assert order.index("c") < order.index("d")

    def test_format_js_array_empty(self) -> None:
        """Test formatting empty array."""
        loader = LazyModuleLoader()

        result = loader._format_js_array([])

        assert result == "[]"

    def test_format_js_array_single_item(self) -> None:
        """Test formatting single item array."""
        loader = LazyModuleLoader()

        result = loader._format_js_array(["item1"])

        assert result == "['item1']"

    def test_format_js_array_multiple_items(self) -> None:
        """Test formatting multiple items array."""
        loader = LazyModuleLoader()

        result = loader._format_js_array(["item1", "item2", "item3"])

        assert result == "['item1', 'item2', 'item3']"

    def test_script_includes_error_handling(self) -> None:
        """Test generated script includes error handling."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="test", path="/test.js", dependencies=[])
        )

        script = loader.generate_loader_script()

        assert "script.onerror" in script
        assert "reject" in script
        assert "console.error" in script

    def test_script_includes_caching_logic(self) -> None:
        """Test script includes module caching."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="test", path="/test.js", dependencies=[])
        )

        script = loader.generate_loader_script()

        assert "loadedModules" in script
        assert "loadingModules" in script
        assert "has(name)" in script

    def test_script_exposes_api(self) -> None:
        """Test script exposes loader API."""
        loader = LazyModuleLoader()

        loader.add_module(
            ModuleConfig(name="test", path="/test.js", dependencies=[])
        )

        script = loader.generate_loader_script()

        assert "window.CortexLoader" in script
        assert "loadModule" in script
        assert "loadAll" in script
        assert "isLoaded" in script


class TestDefaultLoader:
    """Test default loader factory."""

    def test_create_default_loader(self) -> None:
        """Test creating default loader."""
        loader = create_default_loader()

        assert len(loader.modules) > 0
        assert "alpine" in loader.modules
        assert "d3" in loader.modules
        assert "mermaid" in loader.modules

    def test_default_loader_alpine_config(self) -> None:
        """Test Alpine.js is configured as critical."""
        loader = create_default_loader()

        alpine = loader.modules["alpine"]

        assert alpine.priority == 0  # Critical
        assert alpine.defer is True
        assert alpine.async_load is False

    def test_default_loader_d3_config(self) -> None:
        """Test D3.js is configured as high priority."""
        loader = create_default_loader()

        d3 = loader.modules["d3"]

        assert d3.priority == 1  # High
        assert d3.defer is True

    def test_default_loader_mermaid_config(self) -> None:
        """Test Mermaid.js is configured as normal priority."""
        loader = create_default_loader()

        mermaid = loader.modules["mermaid"]

        assert mermaid.priority == 2  # Normal
        assert mermaid.async_load is True  # Can load async

    def test_default_loader_load_order(self) -> None:
        """Test default loader respects priority order."""
        loader = create_default_loader()

        order = loader.get_load_order()

        # Alpine (critical) should be first
        assert order[0] == "alpine"
        # D3 (high) should be before Mermaid (normal)
        assert order.index("d3") < order.index("mermaid")

    def test_default_loader_generates_valid_script(self) -> None:
        """Test default loader generates valid JavaScript."""
        loader = create_default_loader()

        script = loader.generate_loader_script()

        # Basic syntax checks
        assert script.count("(") == script.count(")")
        assert script.count("{") == script.count("}")
        assert script.count("[") == script.count("]")
        assert "syntax error" not in script.lower()
