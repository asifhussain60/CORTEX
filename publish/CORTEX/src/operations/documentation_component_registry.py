"""
Documentation Component Registry

Central registry to manage documentation generation components and execute
them individually or as a pipeline. Designed to be extensible as CORTEX evolves.

Author: Asif Hussain
Copyright: © 2024-2025
License: Proprietary - See LICENSE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import importlib.util
import logging


logger = logging.getLogger(__name__)


@dataclass
class DocumentationComponent:
    id: str
    name: str
    module_path: Path  # absolute path to the generator module file
    class_name: str
    dependencies: List[str] = field(default_factory=list)
    critical: bool = True
    natural_language: List[str] = field(default_factory=list)


class DocumentationComponentRegistry:
    """Central registry for documentation generation components."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.components: Dict[str, DocumentationComponent] = {}

        # Preload base generator types for type-safe configs
        self._package_name = "cortex_admin_docs"
        base_path = self.workspace_root / "cortex-brain" / "admin" / "documentation" / "generators" / "base_generator.py"
        self._base_module = self._import_module(
            base_path,
            module_name=f"{self._package_name}.base_generator",
        )
        if not self._base_module:
            raise RuntimeError("Failed to load base documentation generator module")

        self.GenerationConfig = getattr(self._base_module, "GenerationConfig")
        self.GeneratorType = getattr(self._base_module, "GeneratorType")
        self.GenerationProfile = getattr(self._base_module, "GenerationProfile")

    def register(self, component: DocumentationComponent):
        if component.id in self.components:
            logger.warning(f"Component already registered: {component.id} (overwriting)")
        self.components[component.id] = component

    def list_components(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": c.id,
                "name": c.name,
                "dependencies": c.dependencies,
                "critical": c.critical,
                "natural_language": c.natural_language,
            }
            for c in self.components.values()
        ]

    def get_dependents(self, component_id: str) -> List[str]:
        return [c.id for c in self.components.values() if component_id in c.dependencies]

    def execute(
        self,
        component_id: str,
        output_path: Optional[Path] = None,
        profile: str = "standard",
        force_regenerate: bool = False,
        validate_output: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a single documentation component."""

        if component_id not in self.components:
            raise KeyError(f"Unknown component: {component_id}")

        component = self.components[component_id]

        # Import generator module and class dynamically
        # Ensure component is imported under the same pseudo-package so relative imports work
        module = self._import_module(
            component.module_path,
            module_name=f"{self._package_name}.{component_id}_generator",
        )
        generator_cls = getattr(module, component.class_name)

        # Build config
        gen_type = self._map_generator_type(component_id)
        cfg = self.GenerationConfig(
            generator_type=gen_type,
            profile=self.GenerationProfile(profile) if isinstance(profile, str) else profile,
            output_path=output_path or (self.workspace_root / "docs"),
            force_regenerate=force_regenerate,
            validate_output=validate_output,
            metadata=metadata or {},
        )

        generator = generator_cls(cfg, workspace_root=self.workspace_root)
        result = generator.execute()
        return result.to_dict()

    def execute_pipeline(
        self,
        component_ids: List[str],
        output_path: Optional[Path] = None,
        profile: str = "standard",
        stop_on_failure: bool = True,
    ) -> Dict[str, Any]:
        """Execute multiple components in sequence respecting dependencies."""

        results: Dict[str, Any] = {"success": True, "components": []}
        executed: set[str] = set()

        for comp_id in component_ids:
            self._execute_with_dependencies(
                comp_id,
                executed,
                results,
                output_path=output_path,
                profile=profile,
                stop_on_failure=stop_on_failure,
            )

        # Consolidate
        results["all_success"] = all(c.get("success", False) for c in results["components"]) if results["components"] else True
        return results

    # Internal helpers
    def _execute_with_dependencies(
        self,
        component_id: str,
        executed: set[str],
        results: Dict[str, Any],
        output_path: Optional[Path],
        profile: str,
        stop_on_failure: bool,
    ):
        if component_id in executed:
            return
        if component_id not in self.components:
            raise KeyError(f"Unknown component: {component_id}")

        component = self.components[component_id]
        # Execute dependencies first
        for dep in component.dependencies:
            self._execute_with_dependencies(dep, executed, results, output_path, profile, stop_on_failure)

        # Execute component
        comp_result = self.execute(component_id, output_path=output_path, profile=profile)
        results["components"].append({"id": component_id, **comp_result})
        executed.add(component_id)

        if stop_on_failure and not comp_result.get("success", False) and component.critical:
            results["success"] = False
            raise RuntimeError(f"Critical component failed: {component_id}")

    def _import_module(self, file_path: Path, module_name: str):
        """Import a module from a file path under a pseudo-package so relative imports work."""
        import sys
        import types

        # Ensure parent package exists in sys.modules for relative imports (e.g., from .base_generator import ...)
        if "." in module_name:
            package_name = module_name.rsplit(".", 1)[0]
            if package_name not in sys.modules:
                pkg = types.ModuleType(package_name)
                # Treat the generators directory as the package path
                pkg.__path__ = [str(file_path.parent)]  # type: ignore[attr-defined]
                sys.modules[package_name] = pkg

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        return module

    def _map_generator_type(self, component_id: str):
        # Map registry IDs to GeneratorType enum values
        mapping = {
            "diagrams": self.GeneratorType.DIAGRAMS,
            "mkdocs": self.GeneratorType.MKDOCS,
            "feature_list": self.GeneratorType.FEATURE_LIST,
            "executive_summary": self.GeneratorType.EXECUTIVE_SUMMARY,
            "publish": self.GeneratorType.PUBLISH,
            "all": self.GeneratorType.ALL,
        }
        return mapping.get(component_id, self.GeneratorType.ALL)


def create_default_registry(workspace_root: Optional[Path] = None) -> DocumentationComponentRegistry:
    """Create a registry pre-populated with standard CORTEX documentation components."""
    root = workspace_root or Path.cwd()
    admin_gen_path = root / "cortex-brain" / "admin" / "documentation" / "generators"

    registry = DocumentationComponentRegistry(workspace_root=root)

    registry.register(
        DocumentationComponent(
            id="diagrams",
            name="Image Prompts & Mermaid Diagrams",
            module_path=admin_gen_path / "diagrams_generator.py",
            class_name="DiagramsGenerator",
            dependencies=[],
            critical=False,
            natural_language=["generate image prompts", "generate diagrams", "diagrams"],
        )
    )

    registry.register(
        DocumentationComponent(
            id="feature_list",
            name="CORTEX Feature List",
            module_path=admin_gen_path / "feature_list_generator.py",
            class_name="FeatureListGenerator",
            dependencies=[],
            critical=False,
            natural_language=["cortex feature list", "generate features", "features"],
        )
    )

    registry.register(
        DocumentationComponent(
            id="mkdocs",
            name="MkDocs Site",
            module_path=admin_gen_path / "mkdocs_generator.py",
            class_name="MkDocsGenerator",
            dependencies=[],
            critical=True,
            natural_language=["mkdocs", "publish docs", "build docs"],
        )
    )

    registry.register(
        DocumentationComponent(
            id="executive_summary",
            name="Executive Summary",
            module_path=admin_gen_path / "executive_summary_generator.py",
            class_name="ExecutiveSummaryGenerator",
            dependencies=[],
            critical=False,
            natural_language=["executive summary", "generate summary", "project summary"],
        )
    )

    registry.register(
        DocumentationComponent(
            id="publish",
            name="Publish to GitHub Pages",
            module_path=admin_gen_path / "publish_docs_generator.py",
            class_name="PublishDocsGenerator",
            dependencies=["mkdocs"],  # Requires MkDocs to be built first
            critical=True,
            natural_language=["publish to github pages", "deploy docs", "publish documentation"],
        )
    )

    return registry
