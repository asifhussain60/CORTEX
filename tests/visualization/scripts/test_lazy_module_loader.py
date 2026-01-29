"""
Tests for Lazy Module Loader.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
Task: 019 - Lazy Module Loader Tests
"""

import json
import pytest
from cortex.visualization.scripts.lazy_module_loader import (
    Module,
    ModuleType,
    LazyModuleLoader,
    MODULES,
    TAB_MODULE_REQUIREMENTS,
    get_lazy_loader,
)


class TestModule:
    """Test Module dataclass."""
    
    def test_create_module(self):
        """Test creating a module."""
        module = Module(
            name="test",
            module_type=ModuleType.CORE,
            file_path="vendor/test.js",
            size_kb=100,
            dependencies=["dep1"],
            load_priority=5,
        )
        
        assert module.name == "test"
        assert module.module_type == ModuleType.CORE
        assert module.size_kb == 100
        assert module.dependencies == ["dep1"]
    
    def test_module_default_priority(self):
        """Test module default load priority."""
        module = Module(
            name="test",
            module_type=ModuleType.D3,
            file_path="test.js",
            size_kb=50,
            dependencies=[],
        )
        
        assert module.load_priority == 10


class TestModulesCatalog:
    """Test MODULES catalog configuration."""
    
    def test_modules_catalog_exists(self):
        """Test MODULES catalog is defined."""
        assert len(MODULES) > 0
    
    def test_alpine_module_exists(self):
        """Test Alpine.js module is in catalog."""
        assert "alpine" in MODULES
        alpine = MODULES["alpine"]
        assert alpine.module_type == ModuleType.CORE
        assert alpine.size_kb == 15
    
    def test_d3_module_exists(self):
        """Test D3.js module is in catalog."""
        assert "d3" in MODULES
        d3 = MODULES["d3"]
        assert d3.module_type == ModuleType.D3
        assert d3.size_kb > 0
    
    def test_mermaid_module_exists(self):
        """Test Mermaid module is in catalog."""
        assert "mermaid" in MODULES
        mermaid = MODULES["mermaid"]
        assert mermaid.module_type == ModuleType.MERMAID
    
    def test_all_modules_have_file_paths(self):
        """Test all modules have valid file paths."""
        for name, module in MODULES.items():
            assert module.file_path
            assert module.file_path.startswith("vendor/")


class TestTabModuleRequirements:
    """Test TAB_MODULE_REQUIREMENTS configuration."""
    
    def test_requirements_catalog_exists(self):
        """Test tab requirements catalog is defined."""
        assert len(TAB_MODULE_REQUIREMENTS) > 0
    
    def test_all_tabs_require_alpine(self):
        """Test all tabs require Alpine.js (core)."""
        for tab_id, modules in TAB_MODULE_REQUIREMENTS.items():
            assert "alpine" in modules, f"Tab {tab_id} missing alpine"
    
    def test_dependency_graph_requires_d3(self):
        """Test dependency graph tab requires D3.js."""
        assert "d3" in TAB_MODULE_REQUIREMENTS["dependency_graph"]
    
    def test_class_diagram_requires_mermaid(self):
        """Test class diagram tab requires Mermaid."""
        assert "mermaid" in TAB_MODULE_REQUIREMENTS["class_diagram"]
    
    def test_all_required_modules_exist(self):
        """Test all required modules are in MODULES catalog."""
        for tab_id, modules in TAB_MODULE_REQUIREMENTS.items():
            for module_name in modules:
                assert module_name in MODULES, f"Module {module_name} not in catalog"


class TestLazyModuleLoader:
    """Test LazyModuleLoader class."""
    
    @pytest.fixture
    def loader(self):
        """Create fresh LazyModuleLoader instance."""
        return LazyModuleLoader()
    
    def test_init(self, loader):
        """Test loader initialization."""
        assert len(loader._loaded_modules) == 0
    
    def test_get_initial_load_modules(self, loader):
        """Test getting initial load modules (core bundle)."""
        initial = loader.get_initial_load_modules()
        
        assert len(initial) > 0
        assert "alpine" in initial
        assert "tailwind" in initial
    
    def test_initial_modules_sorted_by_priority(self, loader):
        """Test initial modules are sorted by priority."""
        initial = loader.get_initial_load_modules()
        
        # Verify priority ordering
        priorities = [MODULES[name].load_priority for name in initial]
        assert priorities == sorted(priorities)
    
    def test_get_tab_modules_basic(self, loader):
        """Test getting modules for a tab."""
        modules = loader.get_tab_modules("dependency_graph", include_loaded=True)
        
        assert "alpine" in modules
        assert "d3" in modules
    
    def test_get_tab_modules_exclude_loaded(self, loader):
        """Test excluding already-loaded modules."""
        loader.mark_as_loaded("alpine")
        loader.mark_as_loaded("tailwind")
        
        modules = loader.get_tab_modules("dependency_graph", include_loaded=False)
        
        assert "alpine" not in modules
        assert "tailwind" not in modules
        assert "d3" in modules
    
    def test_get_tab_modules_unknown_tab(self, loader):
        """Test getting modules for unknown tab returns empty list."""
        modules = loader.get_tab_modules("unknown_tab_id")
        assert modules == []
    
    def test_mark_as_loaded(self, loader):
        """Test marking module as loaded."""
        loader.mark_as_loaded("alpine")
        
        assert loader.is_loaded("alpine")
        assert not loader.is_loaded("d3")
    
    def test_is_loaded(self, loader):
        """Test checking if module is loaded."""
        assert not loader.is_loaded("alpine")
        
        loader.mark_as_loaded("alpine")
        assert loader.is_loaded("alpine")
    
    def test_resolve_dependencies_no_deps(self, loader):
        """Test resolving modules with no dependencies."""
        resolved = loader._resolve_dependencies(["alpine"])
        assert resolved == ["alpine"]
    
    def test_resolve_dependencies_with_deps(self, loader):
        """Test resolving modules with dependencies."""
        # Add a module with dependencies for testing
        MODULES["test_module"] = Module(
            name="test_module",
            module_type=ModuleType.CORE,
            file_path="test.js",
            size_kb=10,
            dependencies=["alpine"],
            load_priority=5,
        )
        
        resolved = loader._resolve_dependencies(["test_module"])
        
        assert "alpine" in resolved
        assert "test_module" in resolved
        
        # Cleanup
        del MODULES["test_module"]
    
    def test_estimate_bundle_sizes(self, loader):
        """Test estimating bundle sizes."""
        sizes = loader.estimate_bundle_sizes()
        
        assert "initial_kb" in sizes
        assert "d3_kb" in sizes
        assert "mermaid_kb" in sizes
        assert "total_kb" in sizes
        
        # Verify totals make sense
        assert sizes["initial_kb"] > 0
        assert sizes["total_kb"] >= sizes["initial_kb"]
    
    def test_initial_bundle_smaller_than_total(self, loader):
        """Test initial bundle is smaller than total."""
        sizes = loader.estimate_bundle_sizes()
        
        assert sizes["initial_kb"] < sizes["total_kb"]
    
    def test_generate_loader_javascript(self, loader):
        """Test generating JavaScript loader code."""
        js_code = loader.generate_loader_javascript()
        
        assert "CortexModuleLoader" in js_code
        assert "loadModule" in js_code
        assert "loadModulesForTab" in js_code
        assert "alpine" in js_code
        assert "d3" in js_code
    
    def test_loader_javascript_has_module_configs(self, loader):
        """Test JavaScript loader includes module configurations."""
        js_code = loader.generate_loader_javascript()
        
        # Check for module configurations
        assert "'alpine'" in js_code
        assert "'d3'" in js_code
        assert "'mermaid'" in js_code
        assert "url:" in js_code
        assert "type:" in js_code
    
    def test_loader_javascript_has_tab_requirements(self, loader):
        """Test JavaScript loader includes tab requirements."""
        js_code = loader.generate_loader_javascript()
        
        assert "'dependency_graph'" in js_code
        assert "'class_diagram'" in js_code
    
    def test_loader_javascript_custom_base_url(self, loader):
        """Test JavaScript loader with custom base URL."""
        js_code = loader.generate_loader_javascript(base_url="/custom/")
        
        assert "/custom/vendor/" in js_code
    
    def test_generate_manifest_json(self, loader):
        """Test generating JSON manifest."""
        manifest_str = loader.generate_manifest_json()
        manifest = json.loads(manifest_str)
        
        assert "version" in manifest
        assert "modules" in manifest
        assert "tab_requirements" in manifest
        assert "bundle_sizes" in manifest
    
    def test_manifest_contains_all_modules(self, loader):
        """Test manifest contains all modules from catalog."""
        manifest_str = loader.generate_manifest_json()
        manifest = json.loads(manifest_str)
        
        for module_name in MODULES.keys():
            assert module_name in manifest["modules"]
    
    def test_manifest_module_structure(self, loader):
        """Test manifest module structure."""
        manifest_str = loader.generate_manifest_json()
        manifest = json.loads(manifest_str)
        
        alpine_info = manifest["modules"]["alpine"]
        assert "type" in alpine_info
        assert "file" in alpine_info
        assert "size_kb" in alpine_info
        assert "dependencies" in alpine_info
        assert "priority" in alpine_info


class TestGetLazyLoader:
    """Test get_lazy_loader singleton function."""
    
    def test_get_lazy_loader_returns_instance(self):
        """Test get_lazy_loader returns LazyModuleLoader instance."""
        loader = get_lazy_loader()
        assert isinstance(loader, LazyModuleLoader)
    
    def test_get_lazy_loader_singleton(self):
        """Test get_lazy_loader returns same instance."""
        loader1 = get_lazy_loader()
        loader2 = get_lazy_loader()
        
        assert loader1 is loader2
    
    def test_singleton_persists_state(self):
        """Test singleton persists state across calls."""
        loader1 = get_lazy_loader()
        loader1.mark_as_loaded("test_module")
        
        loader2 = get_lazy_loader()
        assert loader2.is_loaded("test_module")


class TestBundleOptimization:
    """Test bundle size optimization scenarios."""
    
    def test_initial_load_under_200kb(self):
        """Test initial load is under 200KB target."""
        loader = LazyModuleLoader()
        sizes = loader.estimate_bundle_sizes()
        
        # Target: Initial load < 200KB (Alpine 15KB + Tailwind 80KB + app 160KB)
        assert sizes["initial_kb"] < 200
    
    def test_d3_lazy_loaded(self):
        """Test D3.js is not in initial bundle."""
        loader = LazyModuleLoader()
        initial = loader.get_initial_load_modules()
        
        assert "d3" not in initial
    
    def test_mermaid_lazy_loaded(self):
        """Test Mermaid is not in initial bundle."""
        loader = LazyModuleLoader()
        initial = loader.get_initial_load_modules()
        
        assert "mermaid" not in initial
    
    def test_total_bundle_under_2mb(self):
        """Test total bundle is under 2MB."""
        loader = LazyModuleLoader()
        sizes = loader.estimate_bundle_sizes()
        
        # Target: Total < 2MB (1.5MB actual)
        assert sizes["total_kb"] < 2048
