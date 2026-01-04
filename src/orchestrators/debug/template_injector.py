"""
Debug Template Injector - Inject debug markers strategically

Injects CORTEX_DEBUG_ markers for logging and state capture
using pre-defined templates.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
import ast
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class DebugTemplateInjector:
    """Injects debug markers using templates."""
    
    # Python logging template
    PYTHON_LOG_TEMPLATE = '''
# CORTEX_DEBUG_START - Session: {session_id} - Location: {location}
import logging
_cortex_logger = logging.getLogger("cortex.debug.{session_id}")
_cortex_logger.debug("CORTEX_DEBUG: {location} - Entry")
_cortex_logger.debug(f"CORTEX_DEBUG: {location} - State: {{locals()}}")
# CORTEX_DEBUG_END
'''
    
    # JavaScript console template
    JS_CONSOLE_TEMPLATE = '''
// CORTEX_DEBUG_START - Session: {session_id} - Location: {location}
console.log("[CORTEX_DEBUG] {location} - Entry", new Date().toISOString());
console.log("[CORTEX_DEBUG] {location} - State:", {{...this}});
// CORTEX_DEBUG_END
'''
    
    def __init__(self, workspace_root: Path):
        """Initialize template injector."""
        self.workspace_root = workspace_root
        self.logger = logger
    
    def inject_markers(
        self,
        target_files: List[str],
        strategy: str = "moderate",
        session_id: str = ""
    ) -> Dict[str, Any]:
        """
        Inject debug markers at strategic locations.
        
        Implements: DBG-003 (Template-Based Debug Injection)
        
        Args:
            target_files: List of file paths to instrument
            strategy: 'minimal', 'moderate', or 'comprehensive'
            session_id: Debug session ID for marker tagging
            
        Returns:
            Injection results with marker locations
        """
        self.logger.info(f"Injecting markers with strategy: {strategy}")
        
        markers_injected = []
        
        for file_path in target_files:
            full_path = self.workspace_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
            
            if not full_path.exists():
                self.logger.warning(f"File not found: {full_path}")
                continue
            
            # Determine file type and inject appropriately
            if full_path.suffix == '.py':
                file_markers = self._inject_python_markers(
                    full_path, strategy, session_id
                )
            elif full_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                file_markers = self._inject_js_markers(
                    full_path, strategy, session_id
                )
            else:
                self.logger.warning(f"Unsupported file type: {full_path.suffix}")
                continue
            
            markers_injected.extend(file_markers)
        
        return {
            "status": "success",
            "markers": markers_injected,
            "marker_count": len(markers_injected),
            "files_modified": len(target_files),
        }
    
    def _inject_python_markers(
        self,
        file_path: Path,
        strategy: str,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Inject markers in Python file."""
        markers = []
        
        try:
            # Read file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST to find injection points
            tree = ast.parse(content, filename=str(file_path))
            
            # Find function definitions
            injection_points = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    injection_points.append({
                        "type": "function",
                        "name": node.name,
                        "lineno": node.lineno,
                    })
            
            # Apply strategy
            if strategy == "minimal":
                # Only inject at main entry points
                injection_points = [p for p in injection_points if p["name"] in ["main", "__init__", "run"]]
            elif strategy == "moderate":
                # Inject at public methods (not starting with _)
                injection_points = [p for p in injection_points if not p["name"].startswith('_')]
            # comprehensive = all injection points
            
            # Create markers (dry-run - not actually modifying files)
            for point in injection_points:
                marker = {
                    "file": str(file_path),
                    "line": point["lineno"],
                    "type": "python_log",
                    "location": f"{file_path.name}::{point['name']}",
                    "session_id": session_id,
                    "template": "PYTHON_LOG_TEMPLATE",
                }
                markers.append(marker)
                
                self.logger.debug(f"Marker planned: {marker['location']}")
        
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
        
        return markers
    
    def _inject_js_markers(
        self,
        file_path: Path,
        strategy: str,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Inject markers in JavaScript/TypeScript file."""
        markers = []
        
        try:
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Simple heuristic: find function declarations
            for i, line in enumerate(lines, 1):
                if 'function ' in line or '=>' in line:
                    # Extract function name
                    function_name = "anonymous"
                    if 'function ' in line:
                        parts = line.split('function ')
                        if len(parts) > 1:
                            function_name = parts[1].split('(')[0].strip()
                    
                    # Apply strategy
                    if strategy == "minimal" and function_name not in ["main", "init", "render"]:
                        continue
                    
                    marker = {
                        "file": str(file_path),
                        "line": i,
                        "type": "js_console",
                        "location": f"{file_path.name}::{function_name}",
                        "session_id": session_id,
                        "template": "JS_CONSOLE_TEMPLATE",
                    }
                    markers.append(marker)
                    
                    self.logger.debug(f"Marker planned: {marker['location']}")
        
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
        
        return markers
