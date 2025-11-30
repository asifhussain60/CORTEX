"""
View Discovery Agent - Issue #3 Fix (P0)
Purpose: Discover element IDs from Razor/Blazor views before test generation
Created: 2025-11-23
Author: Asif Hussain

This agent addresses the critical gap in TDD workflow where tests were generated
with assumed selectors instead of discovered element IDs, causing immediate failures.
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ElementMapping:
    """Represents a discovered UI element."""
    element_id: Optional[str]
    element_type: str  # button, input, select, div, etc.
    data_testid: Optional[str]
    css_classes: List[str]
    user_facing_text: Optional[str]
    selector_strategy: str  # Recommended selector
    file_path: str
    line_number: int
    attributes: Dict[str, str]  # All attributes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class NavigationFlow:
    """Represents a discovered navigation path."""
    flow_name: str
    route: str  # URL route from @page directive
    component_name: str
    element_mappings: List[ElementMapping]
    requires_auth: bool
    parent_components: List[str]
    

class ViewDiscoveryAgent:
    """
    Discovers element IDs and structure from Razor/Blazor views.
    
    Capabilities:
    1. Parse Razor files for element IDs and data-testid attributes
    2. Extract button text and map to element IDs
    3. Discover navigation routes (@page directives)
    4. Generate selector strategies (ID > data-testid > class > text)
    5. Flag components without IDs
    """
    
    # Regex patterns for element discovery
    ELEMENT_PATTERN = re.compile(
        r'<(?P<tag>\w+)(?P<attrs>[^>]*)>(?P<content>.*?)</\1>',
        re.DOTALL | re.IGNORECASE
    )
    
    SELF_CLOSING_PATTERN = re.compile(
        r'<(?P<tag>\w+)(?P<attrs>[^/>]*)/?>',
        re.IGNORECASE
    )
    
    ID_PATTERN = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    DATA_TESTID_PATTERN = re.compile(r'\bdata-testid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    CLASS_PATTERN = re.compile(r'\bclass\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    PAGE_ROUTE_PATTERN = re.compile(r'@page\s+"([^"]+)"', re.IGNORECASE)
    
    def __init__(self, project_root: Path = None, db_path: Path = None):
        """Initialize ViewDiscoveryAgent."""
        self.project_root = project_root or Path.cwd()
        self.discovered_elements: List[ElementMapping] = []
        self.navigation_flows: List[NavigationFlow] = []
        
        # Database connection for persistence
        if db_path is None:
            # Default to CORTEX brain Tier 2 database
            cortex_root = Path(__file__).parent.parent.parent
            db_path = cortex_root / "cortex-brain" / "tier2" / "knowledge_graph.db"
        
        self.db_path = db_path
        self.db_enabled = db_path and db_path.exists()
        
    def discover_views(
        self, 
        view_paths: List[Path],
        output_path: Optional[Path] = None,
        save_to_db: bool = True,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover all elements from specified view files.
        
        Args:
            view_paths: List of Razor/Blazor file paths to parse
            output_path: Optional path to save discovery results JSON
            save_to_db: Whether to save results to database (default: True)
            project_name: Project identifier for database storage
            
        Returns:
            Dictionary with discovered elements and navigation flows
        """
        # Use project root name as project_name if not provided
        if project_name is None:
            project_name = self.project_root.name
        
        results = {
            "discovery_timestamp": datetime.now().isoformat(),
            "files_processed": [],
            "elements_discovered": [],
            "navigation_flows": [],
            "components_without_ids": [],
            "selector_strategies": {},
            "warnings": []
        }
        
        for view_path in view_paths:
            if not view_path.exists():
                results["warnings"].append(f"File not found: {view_path}")
                continue
            
            try:
                file_results = self._parse_view_file(view_path)
                results["files_processed"].append(str(view_path))
                results["elements_discovered"].extend(file_results["elements"])
                
                if file_results["route"]:
                    results["navigation_flows"].append({
                        "route": file_results["route"],
                        "component": view_path.stem,
                        "file_path": str(view_path),
                        "elements": file_results["elements"]
                    })
                
                # Track components without IDs
                for elem in file_results["elements"]:
                    if not elem["element_id"] and not elem["data_testid"]:
                        results["components_without_ids"].append({
                            "file": str(view_path),
                            "line": elem["line_number"],
                            "type": elem["element_type"],
                            "text": elem["user_facing_text"]
                        })
                
            except Exception as e:
                results["warnings"].append(f"Error parsing {view_path}: {str(e)}")
        
        # Generate selector strategies
        results["selector_strategies"] = self._generate_selector_strategies(
            results["elements_discovered"]
        )
        
        # Save to database if enabled
        if save_to_db and self.db_enabled and results["elements_discovered"]:
            success = self.save_to_database(project_name, results["elements_discovered"])
            if success:
                results["saved_to_database"] = True
                results["database_project_name"] = project_name
        
        # Save to file if requested
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        
        return results
    
    def _parse_view_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single Razor/Blazor view file.
        
        Returns:
            Dictionary with route and discovered elements
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {
            "route": None,
            "elements": []
        }
        
        # Extract @page route
        route_match = self.PAGE_ROUTE_PATTERN.search(content)
        if route_match:
            results["route"] = route_match.group(1)
        
        # Find all elements with IDs or significant attributes
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            # Check for self-closing tags
            for match in self.SELF_CLOSING_PATTERN.finditer(line):
                element = self._extract_element_info(
                    match.group('tag'),
                    match.group('attrs'),
                    None,
                    file_path,
                    line_num
                )
                if element:
                    results["elements"].append(element)
            
            # Check for regular tags (simplified - full parsing would need proper HTML parser)
            for match in self.ELEMENT_PATTERN.finditer(line):
                element = self._extract_element_info(
                    match.group('tag'),
                    match.group('attrs'),
                    match.group('content'),
                    file_path,
                    line_num
                )
                if element:
                    results["elements"].append(element)
        
        return results
    
    def _extract_element_info(
        self,
        tag: str,
        attrs: str,
        content: Optional[str],
        file_path: Path,
        line_number: int
    ) -> Optional[Dict[str, Any]]:
        """Extract information about a discovered element."""
        # Only interested in interactive elements or elements with IDs
        if tag.lower() not in ['button', 'input', 'select', 'a', 'div', 'span', 'textarea']:
            # But always capture if it has an ID
            if not self.ID_PATTERN.search(attrs):
                return None
        
        element_id = None
        data_testid = None
        css_classes = []
        
        # Extract ID
        id_match = self.ID_PATTERN.search(attrs)
        if id_match:
            element_id = id_match.group(1)
        
        # Extract data-testid
        testid_match = self.DATA_TESTID_PATTERN.search(attrs)
        if testid_match:
            data_testid = testid_match.group(1)
        
        # Extract classes
        class_match = self.CLASS_PATTERN.search(attrs)
        if class_match:
            css_classes = class_match.group(1).split()
        
        # Extract user-facing text (simplified)
        user_text = None
        if content:
            # Remove HTML tags and Razor syntax, get plain text
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'@\w+', '', text)
            text = text.strip()
            if text and len(text) < 100:  # Reasonable text length
                user_text = text
        
        # Generate selector strategy
        selector = self._generate_selector(element_id, data_testid, css_classes, user_text, tag)
        
        return {
            "element_id": element_id,
            "element_type": tag.lower(),
            "data_testid": data_testid,
            "css_classes": css_classes,
            "user_facing_text": user_text,
            "selector_strategy": selector,
            "file_path": str(file_path),
            "line_number": line_number,
            "attributes": {"raw": attrs}
        }
    
    def _generate_selector(
        self,
        element_id: Optional[str],
        data_testid: Optional[str],
        css_classes: List[str],
        user_text: Optional[str],
        tag: str
    ) -> str:
        """
        Generate recommended selector strategy.
        
        Priority: ID > data-testid > class > text > tag
        """
        if element_id:
            return f"#{element_id}"
        elif data_testid:
            return f"[data-testid='{data_testid}']"
        elif css_classes:
            # Use most specific class (longest name usually)
            best_class = max(css_classes, key=len) if css_classes else None
            if best_class:
                return f"{tag}.{best_class}"
        elif user_text:
            # Text-based selector (least reliable)
            return f"{tag}:has-text('{user_text[:30]}')"
        else:
            return tag
    
    def _generate_selector_strategies(
        self,
        elements: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Generate a mapping of user-facing text/descriptions to selectors.
        
        This helps test generators quickly find the right selector for buttons
        like "Generate Token" -> "#openSessionBtn"
        """
        strategies = {}
        
        for elem in elements:
            # Map by user text
            if elem.get("user_facing_text"):
                strategies[elem["user_facing_text"]] = elem["selector_strategy"]
            
            # Map by element ID (if exists)
            if elem.get("element_id"):
                strategies[elem["element_id"]] = elem["selector_strategy"]
        
        return strategies
    
    def save_to_database(
        self,
        project_name: str,
        elements: List[Dict[str, Any]]
    ) -> bool:
        """
        Save discovered elements to Tier 2 database.
        
        Args:
            project_name: Project identifier
            elements: List of discovered element dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_enabled:
            return False
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            inserted = 0
            for elem in elements:
                # Determine selector priority
                if elem.get("element_id"):
                    priority = 1
                elif elem.get("data_testid"):
                    priority = 2
                elif elem.get("css_classes"):
                    priority = 3
                else:
                    priority = 4
                
                # Insert or update element mapping
                cursor.execute("""
                    INSERT OR REPLACE INTO tier2_element_mappings
                    (project_name, component_path, element_id, element_type, data_testid,
                     css_classes, selector_strategy, selector_priority, user_facing_text,
                     line_number, attributes, discovered_at, last_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    project_name,
                    elem.get("file_path", ""),
                    elem.get("element_id"),
                    elem.get("element_type", ""),
                    elem.get("data_testid"),
                    json.dumps(elem.get("css_classes", [])),
                    elem.get("selector_strategy", ""),
                    priority,
                    elem.get("user_facing_text"),
                    elem.get("line_number"),
                    json.dumps(elem.get("attributes", {}))
                ))
                inserted += 1
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False
    
    def load_from_database(
        self,
        project_name: str,
        component_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load previously discovered elements from database.
        
        Args:
            project_name: Project identifier
            component_path: Optional specific component path filter
            
        Returns:
            List of element dictionaries
        """
        if not self.db_enabled:
            return []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if component_path:
                cursor.execute("""
                    SELECT element_id, element_type, data_testid, css_classes,
                           selector_strategy, selector_priority, user_facing_text,
                           component_path, line_number, attributes
                    FROM tier2_element_mappings
                    WHERE project_name = ? AND component_path = ?
                    ORDER BY selector_priority, element_id
                """, (project_name, component_path))
            else:
                cursor.execute("""
                    SELECT element_id, element_type, data_testid, css_classes,
                           selector_strategy, selector_priority, user_facing_text,
                           component_path, line_number, attributes
                    FROM tier2_element_mappings
                    WHERE project_name = ?
                    ORDER BY selector_priority, element_id
                """, (project_name,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "element_id": row[0],
                    "element_type": row[1],
                    "data_testid": row[2],
                    "css_classes": json.loads(row[3]) if row[3] else [],
                    "selector_strategy": row[4],
                    "selector_priority": row[5],
                    "user_facing_text": row[6],
                    "file_path": row[7],
                    "line_number": row[8],
                    "attributes": json.loads(row[9]) if row[9] else {}
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error loading from database: {e}")
            return []


def discover_views_for_testing(
    view_directory: Path,
    pattern: str = "*.razor",
    output_file: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Convenience function to discover all views in a directory.
    
    Args:
        view_directory: Directory containing Razor/Blazor files
        pattern: File pattern to match (default: *.razor)
        output_file: Optional JSON output file path
        
    Returns:
        Discovery results dictionary
    """
    view_files = list(view_directory.rglob(pattern))
    
    agent = ViewDiscoveryAgent(project_root=view_directory.parent)
    results = agent.discover_views(view_files, output_path=output_file)
    
    return results
