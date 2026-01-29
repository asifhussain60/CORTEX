"""
SPA Lazy Module Loader for LENS Dashboard.

Implements progressive JavaScript loading with browser caching optimization
and graceful degradation for better performance.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
Task: 017 - SPA Lazy Module Loader
AC-ID: LENS-DASH-017
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ModuleConfig:
    """
    Lazy-loaded module configuration.

    Attributes:
        name: Module identifier (e.g., "d3", "mermaid")
        path: Relative path to module file
        dependencies: List of module names this depends on
        priority: Load priority (0=critical, 1=high, 2=normal, 3=low)
        defer: Whether to defer loading until DOM ready
        async_load: Whether to load asynchronously
    """

    name: str
    path: str
    dependencies: List[str]
    priority: int = 2  # Default: normal priority
    defer: bool = True
    async_load: bool = False


class LazyModuleLoader:
    """
    Generates JavaScript for lazy loading frontend modules.

    Optimizes dashboard load time by:
    - Loading critical modules first
    - Deferring non-critical modules
    - Caching with version fingerprints
    - Graceful degradation on errors

    Example:
        ```python
        loader = LazyModuleLoader()
        loader.add_module(ModuleConfig(
            name="alpine",
            path="/static/vendor/alpine-3.13.3.min.js",
            dependencies=[],
            priority=0  # Critical
        ))
        script = loader.generate_loader_script()
        ```
    """

    def __init__(self) -> None:
        """Initialize lazy module loader."""
        self.modules: Dict[str, ModuleConfig] = {}
        self.loaded_modules: set = set()

    def add_module(self, config: ModuleConfig) -> None:
        """
        Add module to lazy loading configuration.

        Args:
            config: Module configuration

        Example:
            ```python
            loader = LazyModuleLoader()
            loader.add_module(ModuleConfig(
                name="d3",
                path="/static/vendor/d3-7.8.5.min.js",
                dependencies=[],
                priority=1
            ))
            ```
        """
        self.modules[config.name] = config

    def generate_loader_script(self) -> str:
        """
        Generate JavaScript loader script.

        Returns:
            JavaScript code for lazy loading modules

        Example:
            ```python
            loader = LazyModuleLoader()
            # ... add modules ...
            script = loader.generate_loader_script()
            # Inject into HTML: <script>{script}</script>
            ```
        """
        if not self.modules:
            return "// No modules to load"

        # Sort modules by priority
        sorted_modules = sorted(
            self.modules.values(), key=lambda m: (m.priority, m.name)
        )

        script_parts = [
            "// CORTEX LENS Dashboard - Lazy Module Loader",
            "// Auto-generated lazy loading script",
            "",
            "(function() {",
            "  'use strict';",
            "",
            "  const loadedModules = new Set();",
            "  const loadingModules = new Map();",
            "",
            "  // Module configurations",
            "  const modules = {",
        ]

        # Add module configurations
        for module in sorted_modules:
            script_parts.append(f"    '{module.name}': {{")
            script_parts.append(f"      path: '{module.path}',")
            script_parts.append(
                f"      dependencies: {self._format_js_array(module.dependencies)},"
            )
            script_parts.append(f"      priority: {module.priority},")
            script_parts.append(f"      defer: {str(module.defer).lower()},")
            script_parts.append(f"      async: {str(module.async_load).lower()}")
            script_parts.append("    },")

        script_parts.extend(
            [
                "  };",
                "",
                "  // Load a single module",
                "  function loadModule(name) {",
                "    if (loadedModules.has(name)) {",
                "      return Promise.resolve();",
                "    }",
                "",
                "    if (loadingModules.has(name)) {",
                "      return loadingModules.get(name);",
                "    }",
                "",
                "    const config = modules[name];",
                "    if (!config) {",
                "      console.error(`Module not found: ${name}`);",
                "      return Promise.reject(new Error(`Module not found: ${name}`));",
                "    }",
                "",
                "    // Load dependencies first",
                "    const depPromises = config.dependencies.map(dep => loadModule(dep));",
                "",
                "    const promise = Promise.all(depPromises)",
                "      .then(() => {",
                "        return new Promise((resolve, reject) => {",
                "          const script = document.createElement('script');",
                "          script.src = config.path;",
                "          script.defer = config.defer;",
                "          script.async = config.async;",
                "",
                "          script.onload = () => {",
                "            loadedModules.add(name);",
                "            console.log(`✓ Loaded module: ${name}`);",
                "            resolve();",
                "          };",
                "",
                "          script.onerror = () => {",
                "            console.error(`✗ Failed to load module: ${name}`);",
                "            reject(new Error(`Failed to load: ${name}`));",
                "          };",
                "",
                "          document.head.appendChild(script);",
                "        });",
                "      });",
                "",
                "    loadingModules.set(name, promise);",
                "    return promise;",
                "  }",
                "",
                "  // Load all modules in priority order",
                "  function loadAll() {",
                "    const moduleNames = Object.keys(modules);",
                "    const sortedNames = moduleNames.sort((a, b) => {",
                "      return modules[a].priority - modules[b].priority;",
                "    });",
                "",
                "    return sortedNames.reduce((chain, name) => {",
                "      return chain.then(() => loadModule(name));",
                "    }, Promise.resolve());",
                "  }",
                "",
                "  // Expose loader API",
                "  window.CortexLoader = {",
                "    loadModule,",
                "    loadAll,",
                "    isLoaded: (name) => loadedModules.has(name)",
                "  };",
                "",
                "  // Auto-load on DOM ready",
                "  if (document.readyState === 'loading') {",
                "    document.addEventListener('DOMContentLoaded', loadAll);",
                "  } else {",
                "    loadAll();",
                "  }",
                "})();",
            ]
        )

        return "\n".join(script_parts)

    def generate_inline_script(self) -> str:
        """
        Generate inline script tag with loader.

        Returns:
            HTML script tag with loader JavaScript

        Example:
            ```python
            loader = LazyModuleLoader()
            # ... add modules ...
            html = loader.generate_inline_script()
            # Returns: <script>...</script>
            ```
        """
        script = self.generate_loader_script()
        return f"<script>\n{script}\n</script>"

    def get_load_order(self) -> List[str]:
        """
        Get module load order based on priority and dependencies.

        Returns:
            List of module names in load order

        Example:
            ```python
            loader = LazyModuleLoader()
            # ... add modules ...
            order = loader.get_load_order()
            # ['alpine', 'd3', 'mermaid']
            ```
        """
        # Topological sort with priority
        order = []
        visited = set()

        def visit(name: str) -> None:
            if name in visited:
                return

            visited.add(name)
            config = self.modules.get(name)

            if config:
                # Visit dependencies first
                for dep in config.dependencies:
                    visit(dep)

                order.append(name)

        # Visit all modules sorted by priority
        sorted_names = sorted(
            self.modules.keys(), key=lambda n: self.modules[n].priority
        )

        for name in sorted_names:
            visit(name)

        return order

    def _format_js_array(self, items: List[str]) -> str:
        """
        Format Python list as JavaScript array.

        Args:
            items: List of strings

        Returns:
            JavaScript array literal
        """
        if not items:
            return "[]"
        formatted = ", ".join(f"'{item}'" for item in items)
        return f"[{formatted}]"


def create_default_loader() -> LazyModuleLoader:
    """
    Create loader with default LENS Dashboard modules.

    Returns:
        LazyModuleLoader configured for LENS Dashboard

    Example:
        ```python
        from cortex.visualization.spa.lazy_module_loader import create_default_loader
        
        loader = create_default_loader()
        script = loader.generate_loader_script()
        ```
    """
    loader = LazyModuleLoader()

    # Alpine.js - Critical (reactive UI foundation)
    loader.add_module(
        ModuleConfig(
            name="alpine",
            path="/static/vendor/alpine-3.13.3.min.js",
            dependencies=[],
            priority=0,  # Critical
            defer=True,
            async_load=False,
        )
    )

    # D3.js - High priority (used in multiple tabs)
    loader.add_module(
        ModuleConfig(
            name="d3",
            path="/static/vendor/d3-7.8.5.min.js",
            dependencies=[],
            priority=1,  # High
            defer=True,
            async_load=False,
        )
    )

    # Mermaid.js - Normal priority (used in specific tabs)
    loader.add_module(
        ModuleConfig(
            name="mermaid",
            path="/static/vendor/mermaid-10.6.1.min.js",
            dependencies=[],
            priority=2,  # Normal
            defer=True,
            async_load=True,  # Can load async
        )
    )

    return loader
