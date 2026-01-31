"""
Lazy Module Loader for LENS Dashboard SPA.

Optimizes bundle loading by lazy-loading visualization libraries only when needed:
- Core bundle: Alpine.js (15KB) + app logic (160KB) = 175KB initial load
- D3.js modules: 250KB (lazy-loaded per tab)
- Mermaid module: 850KB (lazy-loaded per tab)
- Total full bundle: 1.5MB vs 3MB monolithic

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
Task: 019 - Lazy Module Loader
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional


class ModuleType(Enum):
    """Types of loadable modules."""
    CORE = "core"  # Alpine.js + app logic (always loaded)
    D3 = "d3"  # D3.js visualization library
    MERMAID = "mermaid"  # Mermaid diagram library
    TAILWIND = "tailwind"  # Tailwind CSS framework


@dataclass
class Module:
    """
    Represents a loadable JavaScript/CSS module.
    
    Attributes:
        name: Module name
        module_type: Type of module (core, d3, mermaid, etc.)
        file_path: Path to module file relative to vendor directory
        size_kb: Module size in KB
        dependencies: List of module names this module depends on
        load_priority: Loading priority (lower = higher priority)
    """
    name: str
    module_type: ModuleType
    file_path: str
    size_kb: int
    dependencies: List[str]
    load_priority: int = 10


# Module catalog with loading metadata
MODULES: Dict[str, Module] = {
    "alpine": Module(
        name="alpine",
        module_type=ModuleType.CORE,
        file_path="vendor/alpine-3.13.3.min.js",
        size_kb=15,
        dependencies=[],
        load_priority=1,
    ),
    "d3": Module(
        name="d3",
        module_type=ModuleType.D3,
        file_path="vendor/d3-7.8.5.min.js",
        size_kb=250,
        dependencies=[],
        load_priority=5,
    ),
    "mermaid": Module(
        name="mermaid",
        module_type=ModuleType.MERMAID,
        file_path="vendor/mermaid-10.6.1.min.js",
        size_kb=850,
        dependencies=[],
        load_priority=5,
    ),
    "tailwind": Module(
        name="tailwind",
        module_type=ModuleType.TAILWIND,
        file_path="vendor/tailwind-3.4.0.min.css",
        size_kb=80,
        dependencies=[],
        load_priority=2,
    ),
}


# Tab-to-module mapping (which tabs need which modules)
TAB_MODULE_REQUIREMENTS: Dict[str, List[str]] = {
    "repository_overview": ["alpine", "tailwind"],  # Tab 1 - Core only
    "dependency_graph": ["alpine", "tailwind", "d3"],  # Tab 2 - D3.js
    "class_diagram": ["alpine", "tailwind", "mermaid"],  # Tab 3 - Mermaid
    "git_timeline": ["alpine", "tailwind", "d3"],  # Tab 4 - D3.js
    "author_network": ["alpine", "tailwind", "d3"],  # Tab 5 - D3.js
    "impact_analysis": ["alpine", "tailwind", "d3"],  # Tab 5 - D3.js
    "brain_architecture": ["alpine", "tailwind", "mermaid"],  # Tab 6 - Mermaid
    "governance_heatmap": ["alpine", "tailwind", "d3"],  # Tab 7 - D3.js
    "orchestrator_constellation": ["alpine", "tailwind", "d3"],  # Tab 8 - D3.js
}


class LazyModuleLoader:
    """
    Manages lazy loading of dashboard modules.
    
    Tracks which modules are loaded and generates JavaScript code for
    lazy-loading modules when tabs are activated.
    
    Features:
    - Dependency resolution
    - Load priority ordering
    - Duplicate load prevention
    - Size estimation for initial vs lazy loads
    
    Example:
        ```python
        loader = LazyModuleLoader()
        
        # Get initial load modules (core bundle)
        initial = loader.get_initial_load_modules()
        # ['alpine', 'tailwind']
        
        # Get modules for a specific tab
        tab_modules = loader.get_tab_modules('dependency_graph')
        # ['d3'] (alpine/tailwind already loaded)
        
        # Generate JavaScript loader code
        js_code = loader.generate_loader_javascript()
        ```
    """
    
    def __init__(self):
        """Initialize lazy module loader."""
        self._loaded_modules: Set[str] = set()
    
    def get_initial_load_modules(self) -> List[str]:
        """
        Get modules for initial page load (core bundle).
        
        Returns:
            List of module names to load initially
        """
        core_modules = [
            name for name, module in MODULES.items()
            if module.module_type == ModuleType.CORE or module.module_type == ModuleType.TAILWIND
        ]
        
        # Sort by load priority
        core_modules.sort(key=lambda name: MODULES[name].load_priority)
        
        return core_modules
    
    def get_tab_modules(self, tab_id: str, include_loaded: bool = False) -> List[str]:
        """
        Get modules required for a specific tab.
        
        Args:
            tab_id: Tab identifier (e.g., 'dependency_graph')
            include_loaded: If False, exclude already-loaded modules
        
        Returns:
            List of module names needed for tab
        """
        if tab_id not in TAB_MODULE_REQUIREMENTS:
            return []
        
        required = TAB_MODULE_REQUIREMENTS[tab_id]
        
        if not include_loaded:
            # Filter out already-loaded modules
            required = [name for name in required if name not in self._loaded_modules]
        
        # Resolve dependencies and sort by priority
        with_deps = self._resolve_dependencies(required)
        with_deps.sort(key=lambda name: MODULES[name].load_priority)
        
        return with_deps
    
    def _resolve_dependencies(self, module_names: List[str]) -> List[str]:
        """
        Resolve module dependencies recursively.
        
        Args:
            module_names: List of module names
        
        Returns:
            List of module names including dependencies
        """
        resolved = set()
        
        def resolve(name: str):
            if name in resolved:
                return
            
            if name not in MODULES:
                return
            
            module = MODULES[name]
            
            # Resolve dependencies first
            for dep in module.dependencies:
                resolve(dep)
            
            resolved.add(name)
        
        for name in module_names:
            resolve(name)
        
        return list(resolved)
    
    def mark_as_loaded(self, module_name: str) -> None:
        """
        Mark a module as loaded.
        
        Args:
            module_name: Name of loaded module
        """
        self._loaded_modules.add(module_name)
    
    def is_loaded(self, module_name: str) -> bool:
        """
        Check if a module is loaded.
        
        Args:
            module_name: Module name to check
        
        Returns:
            True if module is loaded
        """
        return module_name in self._loaded_modules
    
    def estimate_bundle_sizes(self) -> Dict[str, int]:
        """
        Estimate bundle sizes for initial and full loads.
        
        Returns:
            Dict with 'initial_kb', 'd3_kb', 'mermaid_kb', 'total_kb'
        """
        initial = self.get_initial_load_modules()
        initial_size = sum(MODULES[name].size_kb for name in initial)
        
        d3_size = MODULES["d3"].size_kb if "d3" in MODULES else 0
        mermaid_size = MODULES["mermaid"].size_kb if "mermaid" in MODULES else 0
        
        total_size = sum(module.size_kb for module in MODULES.values())
        
        return {
            "initial_kb": initial_size,
            "d3_kb": d3_size,
            "mermaid_kb": mermaid_size,
            "total_kb": total_size,
        }
    
    def generate_loader_javascript(self, base_url: str = "/static/") -> str:
        """
        Generate JavaScript code for lazy module loading.
        
        Args:
            base_url: Base URL for static assets
        
        Returns:
            JavaScript code as string
        """
        js_lines = [
            "// CORTEX LENS Dashboard - Lazy Module Loader",
            "// Auto-generated by LazyModuleLoader",
            "",
            "const CortexModuleLoader = {",
            "  loadedModules: new Set(),",
            "  loadingPromises: new Map(),",
            "",
            "  async loadModule(moduleName) {",
            "    // Check if already loaded",
            "    if (this.loadedModules.has(moduleName)) {",
            "      return Promise.resolve();",
            "    }",
            "",
            "    // Check if currently loading",
            "    if (this.loadingPromises.has(moduleName)) {",
            "      return this.loadingPromises.get(moduleName);",
            "    }",
            "",
            "    const moduleConfig = {",
        ]
        
        # Add module configurations
        for name, module in MODULES.items():
            file_url = f"{base_url}{module.file_path}"
            is_css = module.file_path.endswith(".css")
            
            js_lines.append(f"      '{name}': {{")
            js_lines.append(f"        url: '{file_url}',")
            js_lines.append(f"        type: '{'css' if is_css else 'js'}',")
            js_lines.append(f"        size: {module.size_kb},")
            js_lines.append("      },")
        
        js_lines.extend([
            "    };",
            "",
            "    const config = moduleConfig[moduleName];",
            "    if (!config) {",
            "      return Promise.reject(`Unknown module: ${moduleName}`);",
            "    }",
            "",
            "    // Create loading promise",
            "    const loadPromise = new Promise((resolve, reject) => {",
            "      if (config.type === 'css') {",
            "        const link = document.createElement('link');",
            "        link.rel = 'stylesheet';",
            "        link.href = config.url;",
            "        link.onload = () => resolve();",
            "        link.onerror = () => reject(`Failed to load ${moduleName}`);",
            "        document.head.appendChild(link);",
            "      } else {",
            "        const script = document.createElement('script');",
            "        script.src = config.url;",
            "        script.onload = () => resolve();",
            "        script.onerror = () => reject(`Failed to load ${moduleName}`);",
            "        document.head.appendChild(script);",
            "      }",
            "    });",
            "",
            "    this.loadingPromises.set(moduleName, loadPromise);",
            "",
            "    try {",
            "      await loadPromise;",
            "      this.loadedModules.add(moduleName);",
            "      console.log(`✅ Loaded: ${moduleName} (${config.size} KB)`);",
            "    } catch (error) {",
            "      console.error(`❌ Failed to load ${moduleName}:`, error);",
            "      throw error;",
            "    } finally {",
            "      this.loadingPromises.delete(moduleName);",
            "    }",
            "  },",
            "",
            "  async loadModulesForTab(tabId) {",
            "    const tabRequirements = {",
        ])
        
        # Add tab requirements
        for tab_id, modules in TAB_MODULE_REQUIREMENTS.items():
            modules_str = ", ".join(f"'{m}'" for m in modules)
            js_lines.append(f"      '{tab_id}': [{modules_str}],")
        
        js_lines.extend([
            "    };",
            "",
            "    const modules = tabRequirements[tabId] || [];",
            "    const toLoad = modules.filter(m => !this.loadedModules.has(m));",
            "",
            "    if (toLoad.length === 0) {",
            "      return Promise.resolve();",
            "    }",
            "",
            "    console.log(`🔄 Loading modules for tab '${tabId}':`, toLoad);",
            "    return Promise.all(toLoad.map(m => this.loadModule(m)));",
            "  }",
            "};",
            "",
            "// Export to window",
            "window.CortexModuleLoader = CortexModuleLoader;",
        ])
        
        return "\n".join(js_lines)
    
    def generate_manifest_json(self) -> str:
        """
        Generate JSON manifest of all modules.
        
        Returns:
            JSON string with module metadata
        """
        import json
        
        manifest = {
            "version": "1.0.0",
            "modules": {
                name: {
                    "type": module.module_type.value,
                    "file": module.file_path,
                    "size_kb": module.size_kb,
                    "dependencies": module.dependencies,
                    "priority": module.load_priority,
                }
                for name, module in MODULES.items()
            },
            "tab_requirements": TAB_MODULE_REQUIREMENTS,
            "bundle_sizes": self.estimate_bundle_sizes(),
        }
        
        return json.dumps(manifest, indent=2)


def get_lazy_loader() -> LazyModuleLoader:
    """
    Get singleton lazy module loader instance.
    
    Returns:
        LazyModuleLoader instance
    """
    if not hasattr(get_lazy_loader, "_instance"):
        get_lazy_loader._instance = LazyModuleLoader()
    return get_lazy_loader._instance
