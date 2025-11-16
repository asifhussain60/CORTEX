"""
UI Crawler for CORTEX

Discovers and analyzes UI components from various frameworks:
- React/JSX/TSX components
- Angular components
- Vue components
- HTML element IDs
- Routes and navigation
- Component dependencies

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

from .base_crawler import BaseCrawler, CrawlerPriority

logger = logging.getLogger(__name__)


@dataclass
class UIComponent:
    """UI component representation"""
    name: str
    type: str  # react, angular, vue, html
    file_path: str
    element_ids: List[str]
    routes: List[str]
    dependencies: List[str]
    props_or_inputs: List[str]


class UICrawler(BaseCrawler):
    """
    Crawler for discovering UI components and structure.
    
    Discovery Methods:
    1. React components (.jsx, .tsx files)
    2. Angular components (.component.ts files)
    3. Vue components (.vue files)
    4. HTML element IDs
    5. Route configurations
    6. Component dependencies (imports)
    
    Used for:
    - UI testing automation (finding element IDs)
    - Component inventory
    - Route mapping
    - Dependency analysis
    """
    
    def get_crawler_info(self) -> Dict[str, Any]:
        """Get crawler metadata"""
        return {
            'crawler_id': 'ui_crawler',
            'name': 'UI Component Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.HIGH,
            'dependencies': ['tooling_crawler'],
            'description': 'Discovers UI components, element IDs, and routes'
        }
    
    def validate(self) -> bool:
        """Validate crawler can execute"""
        if not self.workspace_path:
            logger.warning("No workspace path provided")
            return False
        
        workspace = Path(self.workspace_path)
        if not workspace.exists():
            logger.warning(f"Workspace path does not exist: {workspace}")
            return False
        
        # Check if UI frameworks detected by tooling crawler
        if 'previous_results' in self.config:
            tooling_result = self.config['previous_results'].get('tooling_crawler')
            if tooling_result and tooling_result.metadata:
                frameworks = tooling_result.metadata.get('frameworks', [])
                has_ui_framework = any(
                    fw in frameworks 
                    for fw in ['React', 'Angular', 'Vue', 'Next.js']
                )
                if not has_ui_framework:
                    logger.info("No UI frameworks detected - skipping UI crawler")
                    return False
        
        return True
    
    def crawl(self) -> Dict[str, Any]:
        """
        Execute UI component discovery.
        
        Returns:
            Dictionary with:
                - components: List[UIComponent]
                - element_ids: Set[str]
                - routes: Set[str]
                - framework_detected: str
        """
        logger.info("Starting UI component discovery...")
        
        workspace = Path(self.workspace_path)
        
        results = {
            'components': [],
            'element_ids': set(),
            'routes': set(),
            'framework_detected': None
        }
        
        # Detect framework
        results['framework_detected'] = self._detect_framework()
        logger.info(f"Framework detected: {results['framework_detected']}")
        
        # Discover components based on framework
        if 'react' in results['framework_detected'].lower():
            results['components'].extend(self._discover_react_components())
        
        if 'angular' in results['framework_detected'].lower():
            results['components'].extend(self._discover_angular_components())
        
        if 'vue' in results['framework_detected'].lower():
            results['components'].extend(self._discover_vue_components())
        
        # Extract element IDs from all components
        for component in results['components']:
            results['element_ids'].update(component.element_ids)
        
        # Extract routes
        results['routes'] = set(self._discover_routes())
        
        # Convert sets to lists for JSON serialization
        results['element_ids'] = sorted(list(results['element_ids']))
        results['routes'] = sorted(list(results['routes']))
        
        logger.info(f"Discovery complete:")
        logger.info(f"  - Components: {len(results['components'])}")
        logger.info(f"  - Element IDs: {len(results['element_ids'])}")
        logger.info(f"  - Routes: {len(results['routes'])}")
        
        return results
    
    def store_results(self, data: Dict[str, Any]) -> int:
        """
        Store UI discovery results in knowledge graph.
        
        Args:
            data: Discovery results from crawl()
            
        Returns:
            Number of patterns stored
        """
        if not self.knowledge_graph:
            return 0
        
        patterns_stored = 0
        
        # Store UI components as patterns
        for component in data['components']:
            pattern_id = self.knowledge_graph.add_pattern(
                title=f"UI Component: {component.name}",
                content=json.dumps(asdict(component), indent=2),
                scope="application",
                namespaces=[self.workspace_path.name],
                tags=["ui", "component", component.type, data['framework_detected'].lower()],
                confidence=0.9,
                source=f"ui_crawler:{component.type}"
            )
            if pattern_id:
                patterns_stored += 1
        
        # Store element IDs as a single pattern
        if data['element_ids']:
            pattern_id = self.knowledge_graph.add_pattern(
                title=f"UI Element IDs: {self.workspace_path.name}",
                content=json.dumps({
                    'element_ids': data['element_ids'],
                    'total_count': len(data['element_ids']),
                    'framework': data['framework_detected']
                }, indent=2),
                scope="application",
                namespaces=[self.workspace_path.name],
                tags=["ui", "element-ids", "testing", data['framework_detected'].lower()],
                confidence=0.95,
                source="ui_crawler:element_ids"
            )
            if pattern_id:
                patterns_stored += 1
        
        # Store routes as a pattern
        if data['routes']:
            pattern_id = self.knowledge_graph.add_pattern(
                title=f"UI Routes: {self.workspace_path.name}",
                content=json.dumps({
                    'routes': data['routes'],
                    'total_count': len(data['routes']),
                    'framework': data['framework_detected']
                }, indent=2),
                scope="application",
                namespaces=[self.workspace_path.name],
                tags=["ui", "routes", "navigation", data['framework_detected'].lower()],
                confidence=0.95,
                source="ui_crawler:routes"
            )
            if pattern_id:
                patterns_stored += 1
        
        return patterns_stored
    
    def _detect_framework(self) -> str:
        """Detect UI framework used"""
        # Check tooling crawler results first
        if 'previous_results' in self.config:
            tooling_result = self.config['previous_results'].get('tooling_crawler')
            if tooling_result and tooling_result.metadata:
                frameworks = tooling_result.metadata.get('frameworks', [])
                for framework in frameworks:
                    if framework in ['React', 'Angular', 'Vue', 'Next.js']:
                        return framework
        
        # Fallback: Check package.json
        workspace = Path(self.workspace_path)
        for package_json in workspace.rglob('package.json'):
            try:
                config = json.loads(package_json.read_text())
                dependencies = {
                    **config.get('dependencies', {}),
                    **config.get('devDependencies', {})
                }
                
                if 'react' in dependencies or 'next' in dependencies:
                    return 'React'
                if '@angular/core' in dependencies:
                    return 'Angular'
                if 'vue' in dependencies:
                    return 'Vue'
            except:
                continue
        
        return 'Unknown'
    
    def _discover_react_components(self) -> List[UIComponent]:
        """Discover React components"""
        components = []
        workspace = Path(self.workspace_path)
        
        # Find JSX/TSX files
        for pattern in ['**/*.jsx', '**/*.tsx']:
            for file_path in workspace.glob(pattern):
                if file_path.is_file() and file_path.stat().st_size < 500_000:
                    component = self._parse_react_component(file_path)
                    if component:
                        components.append(component)
        
        return components
    
    def _parse_react_component(self, file_path: Path) -> Optional[UIComponent]:
        """Parse React component file"""
        try:
            content = file_path.read_text(errors='ignore')
            
            # Extract component name from file or export
            component_name = file_path.stem
            
            # Find element IDs (id="..." or id='...')
            element_ids = re.findall(r'id=["\']([\w-]+)["\']', content)
            
            # Find routes (from react-router)
            routes = re.findall(r'<Route\s+path=["\']([\w/-]+)["\']', content)
            
            # Find imports/dependencies
            dependencies = re.findall(r'from\s+["\'](.+?)["\']', content)
            
            # Find props (simplified)
            props_match = re.search(r'(?:function|const)\s+\w+\s*\(\s*\{([^}]+)\}', content)
            props = []
            if props_match:
                props = [p.strip() for p in props_match.group(1).split(',')]
            
            return UIComponent(
                name=component_name,
                type='react',
                file_path=str(file_path.relative_to(self.workspace_path)),
                element_ids=list(set(element_ids)),
                routes=list(set(routes)),
                dependencies=[d for d in dependencies if not d.startswith('.')],
                props_or_inputs=props
            )
        
        except Exception as e:
            logger.debug(f"Error parsing React component {file_path}: {e}")
            return None
    
    def _discover_angular_components(self) -> List[UIComponent]:
        """Discover Angular components"""
        components = []
        workspace = Path(self.workspace_path)
        
        # Find .component.ts files
        for file_path in workspace.rglob('*.component.ts'):
            if file_path.is_file():
                component = self._parse_angular_component(file_path)
                if component:
                    components.append(component)
        
        return components
    
    def _parse_angular_component(self, file_path: Path) -> Optional[UIComponent]:
        """Parse Angular component file"""
        try:
            content = file_path.read_text(errors='ignore')
            
            # Extract component name
            component_name = file_path.stem.replace('.component', '')
            
            # Find template file
            template_match = re.search(r'templateUrl:\s*["\'](.+?)["\']', content)
            element_ids = []
            
            if template_match:
                template_path = file_path.parent / template_match.group(1)
                if template_path.exists():
                    template_content = template_path.read_text(errors='ignore')
                    element_ids = re.findall(r'id=["\']([\w-]+)["\']', template_content)
            
            # Find inline template
            if not element_ids:
                template_match = re.search(r'template:\s*`([^`]+)`', content, re.DOTALL)
                if template_match:
                    element_ids = re.findall(r'id=["\']([\w-]+)["\']', template_match.group(1))
            
            # Find routes
            routes = []
            route_match = re.search(r'path:\s*["\'](.+?)["\']', content)
            if route_match:
                routes.append(route_match.group(1))
            
            # Find inputs
            inputs = re.findall(r'@Input\(\)\s+(\w+)', content)
            
            # Find imports
            dependencies = re.findall(r'from\s+["\'](.+?)["\']', content)
            
            return UIComponent(
                name=component_name,
                type='angular',
                file_path=str(file_path.relative_to(self.workspace_path)),
                element_ids=list(set(element_ids)),
                routes=routes,
                dependencies=[d for d in dependencies if not d.startswith('.')],
                props_or_inputs=inputs
            )
        
        except Exception as e:
            logger.debug(f"Error parsing Angular component {file_path}: {e}")
            return None
    
    def _discover_vue_components(self) -> List[UIComponent]:
        """Discover Vue components"""
        components = []
        workspace = Path(self.workspace_path)
        
        # Find .vue files
        for file_path in workspace.rglob('*.vue'):
            if file_path.is_file():
                component = self._parse_vue_component(file_path)
                if component:
                    components.append(component)
        
        return components
    
    def _parse_vue_component(self, file_path: Path) -> Optional[UIComponent]:
        """Parse Vue component file"""
        try:
            content = file_path.read_text(errors='ignore')
            
            # Extract component name
            component_name = file_path.stem
            
            # Find element IDs in template section
            template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
            element_ids = []
            if template_match:
                template_content = template_match.group(1)
                element_ids = re.findall(r'id=["\']([\w-]+)["\']', template_content)
            
            # Find routes (from vue-router)
            routes = re.findall(r'path:\s*["\'](.+?)["\']', content)
            
            # Find props
            props_match = re.search(r'props:\s*\{([^}]+)\}', content)
            props = []
            if props_match:
                props = re.findall(r'(\w+):', props_match.group(1))
            
            # Find imports
            dependencies = re.findall(r'from\s+["\'](.+?)["\']', content)
            
            return UIComponent(
                name=component_name,
                type='vue',
                file_path=str(file_path.relative_to(self.workspace_path)),
                element_ids=list(set(element_ids)),
                routes=list(set(routes)),
                dependencies=[d for d in dependencies if not d.startswith('.')],
                props_or_inputs=props
            )
        
        except Exception as e:
            logger.debug(f"Error parsing Vue component {file_path}: {e}")
            return None
    
    def _discover_routes(self) -> List[str]:
        """Discover application routes"""
        routes = []
        workspace = Path(self.workspace_path)
        
        # Look for common route files
        route_files = [
            '**/routes.ts',
            '**/routes.js',
            '**/router.ts',
            '**/router.js',
            '**/app-routing.module.ts',
            '**/router/index.ts'
        ]
        
        for pattern in route_files:
            for file_path in workspace.glob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(errors='ignore')
                        
                        # React Router
                        routes.extend(re.findall(r'<Route\s+path=["\']([\w/-]+)["\']', content))
                        
                        # Vue Router
                        routes.extend(re.findall(r'\{\s*path:\s*["\'](.+?)["\']', content))
                        
                        # Angular Router
                        routes.extend(re.findall(r'\{\s*path:\s*["\'](.+?)["\']', content))
                        
                        # Express/API routes
                        routes.extend(re.findall(r'(?:get|post|put|delete|patch)\(["\'](.+?)["\']', content))
                    
                    except Exception as e:
                        logger.debug(f"Error parsing routes from {file_path}: {e}")
        
        return list(set(routes))
