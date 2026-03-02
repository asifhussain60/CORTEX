"""
Toolkit Discovery Module.

Scans scattered Python utilities and categorizes them by function.
Provides duplication detection and categorization matrix generation.

AC_START: AC-P90-S1-T1
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List
import re


class ToolCategory(str, Enum):
    """Tool categorization."""
    
    DIAGNOSTICS = "diagnostics"
    SETUP = "setup"
    CLEANUP = "cleanup"
    VALIDATION = "validation"
    AUTOMATION = "automation"


@dataclass
class ToolMetadata:
    """Metadata for a discovered tool."""
    
    name: str
    path: Path
    category: ToolCategory
    description: str = ""
    functions: List[str] = None
    
    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.functions is None:
            self.functions = []


class ToolkitDiscovery:
    """
    Discovery engine for scattered toolkit utilities.
    
    Scans .cortex-runtime/ and scripts/ directories, categorizes tools,
    and identifies duplicate functionality.
    """
    
    # Categorization patterns
    CATEGORY_PATTERNS = {
        ToolCategory.DIAGNOSTICS: [
            r"verify.*mcp",
            r"diagnose",
            r"check.*health",
            r"analyze.*root",
        ],
        ToolCategory.SETUP: [
            r"setup",
            r"install",
            r"configure",
            r"verify.*setup",
            r"autonomous.*setup",
        ],
        ToolCategory.CLEANUP: [
            r"vacuum",
            r"cleanup",
            r"remove",
            r"delete",
            r"purge",
            r"phase.*cleanup",
        ],
        ToolCategory.VALIDATION: [
            r"validate",
            r"audit",
            r"verify.*production",
            r"governance.*alignment",
            r"execute.*validation",
        ],
        ToolCategory.AUTOMATION: [
            r"generate",
            r"batch",
            r"autonomous.*phases",
            r"consolidate",
            r"enforce",
            r"fix.*duplicate",
        ],
    }
    
    def __init__(self, workspace_root: Path = Path.cwd()) -> None:
        """
        Initialize discovery.
        
        Args:
            workspace_root: CORTEX workspace root directory
        """
        self.workspace_root = workspace_root
    
    def discover_tools(self, directory: Path) -> List[ToolMetadata]:
        """
        Discover tools in a directory.
        
        Args:
            directory: Directory to scan (relative to workspace_root)
            
        Returns:
            List of discovered tool metadata
        """
        full_path = self.workspace_root / directory
        if not full_path.exists():
            return []
        
        tools = []
        for py_file in full_path.glob("*.py"):
            # Skip __init__.py and hidden files
            if py_file.name.startswith("__") or py_file.name.startswith("."):
                continue
            
            category = self.categorize_tool(py_file.name)
            description = self._extract_description(py_file)
            
            tool = ToolMetadata(
                name=py_file.stem,
                path=py_file,
                category=category,
                description=description,
            )
            tools.append(tool)
        
        return tools
    
    def discover_all(self) -> List[ToolMetadata]:
        """
        Discover all tools in .cortex-runtime/ and scripts/.
        
        Returns:
            Combined list of all discovered tools
        """
        cortex_tools = self.discover_tools(Path(".cortex-runtime"))
        scripts_tools = self.discover_tools(Path("scripts"))
        
        return cortex_tools + scripts_tools
    
    def categorize_tool(self, filename: str) -> ToolCategory:
        """
        Categorize a tool by filename pattern.
        
        Args:
            filename: Tool filename
            
        Returns:
            Categorized tool category
        """
        filename_lower = filename.lower()
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return category
        
        # Default to automation if no match
        return ToolCategory.AUTOMATION
    
    def find_duplicates(self, tools: List[ToolMetadata]) -> List[str]:
        """
        Identify duplicate functionality across tools.
        
        Args:
            tools: List of tools to analyze
            
        Returns:
            List of duplicate function groups
        """
        duplicates = []
        
        # Group by category
        by_category: Dict[ToolCategory, List[ToolMetadata]] = {}
        for tool in tools:
            if tool.category not in by_category:
                by_category[tool.category] = []
            by_category[tool.category].append(tool)
        
        # Find duplicates within each category
        for category, category_tools in by_category.items():
            if len(category_tools) <= 1:
                continue
            
            # Extract common keywords from tool names
            keywords: Dict[str, List[str]] = {}
            for tool in category_tools:
                # Split name on delimiters
                parts = re.split(r"[-_]", tool.name.lower())
                for part in parts:
                    if len(part) > 3:  # Ignore short words
                        if part not in keywords:
                            keywords[part] = []
                        keywords[part].append(tool.name)
            
            # Report groups with 2+ tools sharing keyword
            for keyword, tool_names in keywords.items():
                if len(tool_names) >= 2:
                    duplicates.append(f"{keyword}: {', '.join(tool_names)}")
        
        return duplicates
    
    def generate_matrix(
        self,
        tools: List[ToolMetadata]
    ) -> Dict[ToolCategory, List[ToolMetadata]]:
        """
        Generate categorization matrix.
        
        Args:
            tools: List of tools to categorize
            
        Returns:
            Matrix mapping categories to tools
        """
        matrix: Dict[ToolCategory, List[ToolMetadata]] = {
            category: [] for category in ToolCategory
        }
        
        for tool in tools:
            matrix[tool.category].append(tool)
        
        return matrix
    
    def _extract_description(self, file_path: Path) -> str:
        """
        Extract description from tool docstring.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            First line of module docstring, or empty string
        """
        try:
            content = file_path.read_text()
            # Find first docstring
            match = re.search(r'"""(.+?)"""', content, re.DOTALL)
            if match:
                # Get first non-empty line
                lines = match.group(1).strip().split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        return stripped
        except Exception:
            pass
        
        return ""


# AC_COMPLETE: AC-P90-S1-T1
