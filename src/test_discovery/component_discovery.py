"""
Component Discovery Engine for CORTEX Integration Tests.

Discovers components via AST parsing, extracts signatures, and identifies
integration points. Leverages Tier 2 knowledge graph for risk analysis.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import importlib.util


@dataclass
class ComponentSignature:
    """Component signature extracted from AST."""
    name: str
    type: str  # class, function, agent, orchestrator
    methods: List[Dict[str, Any]] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class IntegrationPoint:
    """Integration point between components."""
    component: str
    type: str  # import, method_call, event, database
    file: Optional[str] = None
    method: Optional[str] = None


@dataclass
class Component:
    """Discovered component with full metadata."""
    name: str
    path: str
    category: str
    component_type: str
    signature: ComponentSignature
    integration_points: List[IntegrationPoint] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    test_file: Optional[str] = None
    test_status: str = "untested"
    risk_score: float = 0.0
    last_modified: Optional[str] = None


class ComponentDiscoveryEngine:
    """Discovers CORTEX components via AST analysis."""
    
    COMPONENT_CATEGORIES = {
        "orchestrators": "src/orchestrators",
        "agents": "src/cortex_agents",
        "brain_tiers": ["src/tier0", "src/tier1", "src/tier2", "src/tier3"],
        "workflows": "src/workflows",
        "response_templates": "src/response_templates",
        "utilities": "src/utils",
        "validation": "src/validation",
        "sessions": "src/sessions",
        "config": "src/config",
        "learning": "src/learning"
    }
    
    AGENT_BASE_CLASSES = {"BaseAgent", "SpecialistAgent"}
    ORCHESTRATOR_PATTERNS = ["Orchestrator", "Manager", "Coordinator"]
    
    def __init__(self, project_root: str):
        """Initialize discovery engine."""
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.discovered_components: List[Component] = []
        
    def discover_all(self) -> List[Component]:
        """Discover all components in the project."""
        self.discovered_components = []
        
        for category, paths in self.COMPONENT_CATEGORIES.items():
            if isinstance(paths, list):
                for path in paths:
                    self._discover_in_directory(path, category)
            else:
                self._discover_in_directory(paths, category)
        
        # Extract integration points
        self._analyze_integration_points()
        
        return self.discovered_components
    
    def _discover_in_directory(self, relative_path: str, category: str):
        """Discover components in a specific directory."""
        dir_path = self.project_root / relative_path
        
        if not dir_path.exists():
            return
        
        for py_file in dir_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            components = self._analyze_file(py_file, category)
            self.discovered_components.extend(components)
    
    def _analyze_file(self, file_path: Path, category: str) -> List[Component]:
        """Analyze a Python file and extract components."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            components = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    component = self._extract_class_component(
                        node, file_path, category
                    )
                    if component:
                        components.append(component)
                
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions (not class methods)
                    if self._is_top_level_function(node, tree):
                        component = self._extract_function_component(
                            node, file_path, category
                        )
                        if component:
                            components.append(component)
            
            return components
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def _extract_class_component(
        self, node: ast.ClassDef, file_path: Path, category: str
    ) -> Optional[Component]:
        """Extract component from class definition."""
        # Determine component type
        component_type = self._determine_class_type(node)
        
        # Extract signature
        signature = ComponentSignature(
            name=node.name,
            type="class",
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_sig = self._extract_method_signature(item)
                signature.methods.append(method_sig)
        
        # Create component
        component = Component(
            name=node.name,
            path=str(file_path.relative_to(self.project_root)),
            category=category,
            component_type=component_type,
            signature=signature,
            dependencies={"internal": [], "external": []},
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        )
        
        # Extract dependencies from imports
        self._extract_dependencies(file_path, component)
        
        return component
    
    def _extract_function_component(
        self, node: ast.FunctionDef, file_path: Path, category: str
    ) -> Optional[Component]:
        """Extract component from function definition."""
        # Only track decorated functions or validators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        if not decorators and not node.name.startswith("validate_"):
            return None
        
        signature = ComponentSignature(
            name=node.name,
            type="function",
            docstring=ast.get_docstring(node),
            decorators=decorators,
            parameters=self._extract_parameters(node),
            return_type=self._extract_return_type(node)
        )
        
        component = Component(
            name=node.name,
            path=str(file_path.relative_to(self.project_root)),
            category=category,
            component_type="function",
            signature=signature,
            dependencies={"internal": [], "external": []},
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        )
        
        self._extract_dependencies(file_path, component)
        
        return component
    
    def _determine_class_type(self, node: ast.ClassDef) -> str:
        """Determine the type of class component."""
        # Check base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in self.AGENT_BASE_CLASSES:
                    return "agent"
        
        # Check name patterns
        for pattern in self.ORCHESTRATOR_PATTERNS:
            if pattern in node.name:
                return "orchestrator"
        
        # Check for dataclass decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                return "dataclass"
        
        return "class"
    
    def _extract_method_signature(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract method signature."""
        return {
            "name": node.name,
            "parameters": self._extract_parameters(node),
            "return_type": self._extract_return_type(node),
            "docstring": ast.get_docstring(node),
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function/method parameters."""
        params = []
        
        for arg in node.args.args:
            param = {"name": arg.arg}
            
            # Extract type annotation
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            
            params.append(param)
        
        return params
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if node.returns:
            return ast.unparse(node.returns)
        return None
    
    def _extract_dependencies(self, file_path: Path, component: Component):
        """Extract dependencies from file imports."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._categorize_dependency(alias.name, component)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._categorize_dependency(node.module, component)
        
        except Exception:
            pass
    
    def _categorize_dependency(self, module: str, component: Component):
        """Categorize dependency as internal or external."""
        if module.startswith("src."):
            component.dependencies["internal"].append(module)
        elif not module.startswith("_"):  # Skip builtins
            component.dependencies["external"].append(module)
    
    def _analyze_integration_points(self):
        """Analyze integration points between components."""
        for component in self.discovered_components:
            # Analyze internal dependencies for integration points
            for dep in component.dependencies.get("internal", []):
                integration_point = IntegrationPoint(
                    component=dep.replace("src.", "").replace(".", "/"),
                    type="import"
                )
                component.integration_points.append(integration_point)
            
            # Identify database interactions
            if any("tier" in dep for dep in component.dependencies.get("internal", [])):
                tier_deps = [d for d in component.dependencies["internal"] if "tier" in d]
                for tier_dep in tier_deps:
                    integration_point = IntegrationPoint(
                        component=tier_dep,
                        type="database"
                    )
                    component.integration_points.append(integration_point)
    
    def _is_top_level_function(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if function is top-level (not a method)."""
        for item in tree.body:
            if item == node:
                return True
        return False
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return "unknown"
    
    def get_components_by_category(self, category: str) -> List[Component]:
        """Get all components in a specific category."""
        return [c for c in self.discovered_components if c.category == category]
    
    def get_untested_components(self) -> List[Component]:
        """Get all components without tests."""
        return [c for c in self.discovered_components if c.test_status == "untested"]
    
    def calculate_coverage(self) -> Dict[str, Any]:
        """Calculate test coverage statistics."""
        total = len(self.discovered_components)
        tested = len([c for c in self.discovered_components if c.test_status == "tested"])
        
        category_stats = {}
        for category in self.COMPONENT_CATEGORIES.keys():
            category_components = self.get_components_by_category(category)
            category_total = len(category_components)
            category_tested = len([c for c in category_components if c.test_status == "tested"])
            
            category_stats[category] = {
                "total": category_total,
                "tested": category_tested,
                "untested": category_total - category_tested,
                "coverage": (category_tested / category_total * 100) if category_total > 0 else 0
            }
        
        return {
            "total_components": total,
            "tested_components": tested,
            "untested_components": total - tested,
            "coverage_percentage": (tested / total * 100) if total > 0 else 0,
            "categories": category_stats
        }
