"""
Test Generation Engine for CORTEX Integration Tests.

Generates integration tests from component signatures using Jinja2 templates.
Leverages Tier 2 knowledge graph for pattern-based test enhancement.

Author: GitHub Copilot
Created: 2025-12-06
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader, Template

from src.test_discovery.component_discovery import (
    Component,
    ComponentSignature,
    IntegrationPoint,
    ComponentDiscoveryEngine
)
from src.test_discovery.test_manifest import TestManifest

logger = logging.getLogger(__name__)


@dataclass
class GeneratedTest:
    """Metadata for a generated test."""
    test_file: str
    test_name: str
    component: str
    category: str
    template_used: str
    lines_generated: int
    timestamp: datetime


class TestGenerationEngine:
    """Generates integration tests from component signatures."""
    
    def __init__(self, cortex_root: str):
        """
        Initialize test generation engine.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.template_dir = self.cortex_root / "src" / "test_discovery" / "templates"
        self.output_dir = self.cortex_root / "tests" / "integration"
        self.manifest = TestManifest(cortex_root)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Category to template mapping
        self.category_templates = {
            "orchestrators": "orchestrator_integration.py.j2",
            "agents": "agent_integration.py.j2",
            "brain_tiers": "brain_tier_integration.py.j2",
            "learning": "learning_integration.py.j2",
            "endpoints": "endpoint_integration.py.j2",
            "error_handling": "error_handling_integration.py.j2",
            "configuration": "configuration_integration.py.j2",
            "deployment": "deployment_integration.py.j2",
            "performance": "performance_integration.py.j2",
            "security": "security_integration.py.j2",
            "e2e": "e2e_integration.py.j2"
        }
        
        logger.info(f"TestGenerationEngine initialized for {cortex_root}")
    
    def generate_tests_for_component(
        self,
        component: Component,
        force: bool = False
    ) -> Optional[GeneratedTest]:
        """
        Generate integration test for a single component.
        
        Args:
            component: Component to generate tests for
            force: Regenerate even if test exists
            
        Returns:
            GeneratedTest metadata if successful, None otherwise
        """
        # Check if test already exists
        if component.test_file and os.path.exists(component.test_file) and not force:
            logger.info(f"Test already exists for {component.name}, skipping")
            return None
        
        # Get template for category
        template_name = self.category_templates.get(component.category)
        if not template_name:
            logger.warning(f"No template for category {component.category}")
            return None
        
        try:
            template = self.jinja_env.get_template(template_name)
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None
        
        # Prepare template context
        context = self._prepare_context(component)
        
        # Render test code
        try:
            test_code = template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template for {component.name}: {e}")
            return None
        
        # Determine output path
        test_file = self._get_test_file_path(component)
        
        # Write test file
        try:
            os.makedirs(test_file.parent, exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)
            logger.info(f"Generated test: {test_file}")
        except Exception as e:
            logger.error(f"Failed to write test file {test_file}: {e}")
            return None
        
        # Create metadata
        generated = GeneratedTest(
            test_file=str(test_file),
            test_name=f"test_{component.name.lower()}_integration",
            component=component.name,
            category=component.category,
            template_used=template_name,
            lines_generated=len(test_code.splitlines()),
            timestamp=datetime.now()
        )
        
        # Update manifest
        self.manifest.update_component(
            component.name,
            test_file=str(test_file),
            test_status="generated",
            risk_score=component.risk_score
        )
        
        return generated
    
    def generate_tests_for_category(
        self,
        category: str,
        max_tests: Optional[int] = None,
        force: bool = False
    ) -> List[GeneratedTest]:
        """
        Generate tests for all untested components in a category.
        
        Args:
            category: Category to generate tests for
            max_tests: Maximum number of tests to generate
            force: Regenerate existing tests
            
        Returns:
            List of generated test metadata
        """
        logger.info(f"Generating tests for category: {category}")
        
        # Discover components
        discovery_engine = ComponentDiscoveryEngine(self.cortex_root)
        components = discovery_engine.discover_by_category(category)
        
        # Filter untested components
        untested = [c for c in components if c.test_status == "untested" or force]
        
        if max_tests:
            untested = untested[:max_tests]
        
        logger.info(f"Found {len(untested)} untested components in {category}")
        
        # Generate tests
        generated_tests = []
        for component in untested:
            result = self.generate_tests_for_component(component, force=force)
            if result:
                generated_tests.append(result)
        
        logger.info(f"Generated {len(generated_tests)} tests for {category}")
        return generated_tests
    
    def generate_all_tests(
        self,
        max_per_category: int = 10,
        force: bool = False
    ) -> Dict[str, List[GeneratedTest]]:
        """
        Generate tests for all categories.
        
        Args:
            max_per_category: Maximum tests per category
            force: Regenerate existing tests
            
        Returns:
            Dictionary mapping categories to generated tests
        """
        logger.info("Starting full test generation")
        
        results = {}
        for category in self.category_templates.keys():
            generated = self.generate_tests_for_category(
                category,
                max_tests=max_per_category,
                force=force
            )
            if generated:
                results[category] = generated
        
        # Save manifest
        self.manifest.save()
        
        logger.info(f"Generated {sum(len(tests) for tests in results.values())} total tests")
        return results
    
    def _prepare_context(self, component: Component) -> Dict[str, Any]:
        """
        Prepare Jinja2 template context from component.
        
        Args:
            component: Component to prepare context for
            
        Returns:
            Dictionary of template variables
        """
        context = {
            "component_name": component.name,
            "component_name_lower": component.name.lower(),
            "component_type": component.component_type,
            "component_path": component.path,
            "category": component.category,
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "integration_points": [
                {
                    "name": ip.component if isinstance(ip, IntegrationPoint) else ip.get("component", "Unknown"),
                    "name_lower": (ip.component if isinstance(ip, IntegrationPoint) else ip.get("component", "unknown")).lower(),
                    "type": ip.type if isinstance(ip, IntegrationPoint) else ip.get("type", "unknown"),
                    "method": ip.method if isinstance(ip, IntegrationPoint) else ip.get("method"),
                    "path": None,  # Can be enhanced later
                    "component": ip.component if isinstance(ip, IntegrationPoint) else ip.get("component", "Unknown")
                }
                for ip in component.integration_points
            ],
            "methods": component.signature.methods,
            "dependencies": component.dependencies,
            "docstring": component.signature.docstring or f"Integration tests for {component.name}",
            "has_async": any(m.get("is_async", False) for m in component.signature.methods),
        }
        
        # Add category-specific context
        if component.category == "orchestrators":
            # Extract module name from path
            path_parts = Path(component.path).parts
            if "orchestrators" in path_parts:
                idx = path_parts.index("orchestrators")
                module_name = path_parts[idx + 1].replace(".py", "") if len(path_parts) > idx + 1 else component.name.lower()
            else:
                module_name = component.name.lower()
            
            context["orchestrator_name"] = component.name
            context["orchestrator_name_lower"] = component.name.lower()
            context["orchestrator_module"] = module_name
            context["tier_name"] = self._extract_tier_name(component.name)
            context["has_database"] = "database" in component.name.lower() or "db" in component.name.lower()
        
        elif component.category == "orchestrators":
            context["has_git_checkpoint"] = any(
                "git" in ip.component.lower() for ip in component.integration_points
            )
            context["has_brain_integration"] = any(
                "tier" in ip.component.lower() for ip in component.integration_points
            )
        
        elif component.category == "agents":
            context["agent_type"] = self._extract_agent_type(component.name)
            context["has_brain_access"] = any(
                "tier" in ip.component.lower() or "knowledge" in ip.component.lower()
                for ip in component.integration_points
            )
        
        return context
    
    def _get_test_file_path(self, component: Component) -> Path:
        """
        Determine output path for test file.
        
        Args:
            component: Component to generate path for
            
        Returns:
            Path to test file
        """
        # Use component's test_file if specified
        if component.test_file:
            return Path(component.test_file)
        
        # Generate path based on category and name
        category_dir = self.output_dir / component.category
        test_name = f"test_{component.name.lower()}_integration.py"
        return category_dir / test_name
    
    def _extract_tier_name(self, component_name: str) -> str:
        """Extract tier name from component name."""
        if "tier1" in component_name.lower() or "working_memory" in component_name.lower():
            return "tier1"
        elif "tier2" in component_name.lower() or "knowledge_graph" in component_name.lower():
            return "tier2"
        elif "tier3" in component_name.lower() or "development_context" in component_name.lower():
            return "tier3"
        return "unknown"
    
    def _extract_agent_type(self, component_name: str) -> str:
        """Extract agent type from component name."""
        name_lower = component_name.lower()
        if "router" in name_lower or "intent" in name_lower:
            return "router"
        elif "planning" in name_lower or "planner" in name_lower:
            return "planner"
        elif "executor" in name_lower or "execution" in name_lower:
            return "executor"
        elif "learning" in name_lower:
            return "learning"
        return "generic"
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about test generation.
        
        Returns:
            Dictionary of statistics
        """
        manifest_data = self.manifest.load()
        
        total_components = sum(
            cat["discovered"] for cat in manifest_data["categories"].values()
        )
        total_tested = sum(
            cat["tested"] for cat in manifest_data["categories"].values()
        )
        total_generated = sum(
            1 for cat in manifest_data["categories"].values()
            for comp in cat.get("components", [])
            if comp.get("status") == "generated"
        )
        
        return {
            "total_components": total_components,
            "total_tested": total_tested,
            "total_generated": total_generated,
            "coverage_percentage": (total_tested / total_components * 100) if total_components > 0 else 0,
            "categories": {
                name: {
                    "discovered": cat["discovered"],
                    "tested": cat["tested"],
                    "untested": cat["untested"]
                }
                for name, cat in manifest_data["categories"].items()
            }
        }


def main():
    """CLI entry point for test generation."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.test_discovery.test_generator <category|all> [--force]")
        sys.exit(1)
    
    cortex_root = os.getcwd()
    engine = TestGenerationEngine(cortex_root)
    
    category = sys.argv[1]
    force = "--force" in sys.argv
    
    if category == "all":
        results = engine.generate_all_tests(force=force)
        print(f"\nGenerated tests for {len(results)} categories:")
        for cat, tests in results.items():
            print(f"  {cat}: {len(tests)} tests")
    else:
        results = engine.generate_tests_for_category(category, force=force)
        print(f"\nGenerated {len(results)} tests for {category}")
    
    stats = engine.get_generation_stats()
    print(f"\nCoverage: {stats['coverage_percentage']:.1f}% ({stats['total_tested']}/{stats['total_components']})")


if __name__ == "__main__":
    main()
