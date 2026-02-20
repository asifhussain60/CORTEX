"""
Structure Analyzer - Detect file structure (sections, headers, versions).

AC_START: AC-ENH-101-005
Description: StructureAnalyzer for detecting file structure elements
Authority: ENH-101 Stage S2 - File Structure Detection
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Analyzes file content to detect:
    - Sections (markdown headers, Python classes/functions, YAML keys)
    - Version markers (header, footer, inline)
    - Structural hierarchy and nesting
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.orchestrators.validation.coherence_models import (
    FileStructure,
    Section,
    SectionType,
    VersionMarker,
)

logger = logging.getLogger(__name__)


@dataclass
class StructureMetrics:
    """Metrics about file structure.
    
    Attributes:
        total_sections: Total number of sections
        max_depth: Maximum nesting depth
        avg_section_length: Average lines per section
        total_lines: Total lines in file
    """
    
    total_sections: int = 0
    max_depth: int = 0
    avg_section_length: float = 0.0
    total_lines: int = 0


class StructureAnalyzer:
    """Analyzer for detecting file structure and organization.
    
    Supports multiple file types:
    - Markdown: Headers (H1-H6), code blocks
    - Python: Classes, functions, decorators
    - YAML: Top-level keys, nested structures
    - JSON: Object keys
    
    Example:
        >>> analyzer = StructureAnalyzer()
        >>> structure = analyzer.analyze("# Title\\n\\n## Section\\n\\nContent")
        >>> print(len(structure.sections))
        2
    """
    
    def __init__(self) -> None:
        """Initialize the StructureAnalyzer."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def analyze(
        self,
        content: str,
        file_path: Optional[str | Path] = None,
        file_type: Optional[str] = None,
    ) -> FileStructure:
        """Analyze content to detect file structure.
        
        Args:
            content: File content to analyze
            file_path: Optional path for metadata (string or Path)
            file_type: File type (auto-detected if not provided)
            
        Returns:
            FileStructure with detected sections and markers
        """
        # Convert to Path if string
        if isinstance(file_path, str):
            path = Path(file_path)
        else:
            path = file_path or Path("inline")
        
        # Detect file type if not provided
        if file_type is None:
            file_type = self._detect_type(path, content)
        
        lines = content.splitlines()
        
        # Parse based on file type
        sections = self._parse_sections(lines, file_type)
        version_markers = self._find_version_markers(lines)
        
        return FileStructure(
            file_path=str(path),
            file_type=file_type,
            sections=sections,
            version_markers=version_markers,
            total_lines=len(lines),
            metadata=self._extract_metadata(content, file_type),
        )
    
    def detect_sections(
        self,
        content: str,
        file_path: Optional[str | Path] = None,
    ) -> List[Section]:
        """Detect sections in content.
        
        Args:
            content: Content to parse
            file_path: Optional file path (for type detection)
            
        Returns:
            List of detected Section objects
        """
        # Detect file type from path
        if isinstance(file_path, str):
            path = Path(file_path)
        else:
            path = file_path or Path("inline")
        
        file_type = self._detect_type(path, content)
        
        lines = content.splitlines()
        return self._parse_sections(lines, file_type)
    
    def find_version_markers(self, content: str) -> List[VersionMarker]:
        """Find all version markers in content.
        
        Args:
            content: Content to search
            
        Returns:
            List of VersionMarker objects
        """
        lines = content.splitlines()
        return self._find_version_markers(lines)
    
    def get_structure_metrics(
        self,
        content: str,
        file_path: Optional[str | Path] = None,
    ) -> StructureMetrics:
        """Calculate metrics about file structure.
        
        Args:
            content: File content to analyze
            file_path: Optional file path
            
        Returns:
            StructureMetrics with calculated values
        """
        structure = self.analyze(content, file_path)
        sections = structure.sections
        
        if not sections:
            return StructureMetrics(
                total_sections=0,
                max_depth=0,
                avg_section_length=0.0,
                total_lines=structure.total_lines,
            )
        
        total = len(sections)
        max_depth = max(s.level for s in sections) if sections else 0
        
        # Calculate average section length
        total_section_lines = sum(s.end_line - s.start_line + 1 for s in sections)
        avg_length = total_section_lines / total if total > 0 else 0
        
        return StructureMetrics(
            total_sections=total,
            max_depth=max_depth,
            avg_section_length=avg_length,
            total_lines=structure.total_lines,
        )
    
    def get_section_hierarchy(self, sections: List[Section]) -> Dict[str, Any]:
        """Build a hierarchy tree of sections.
        
        Args:
            sections: List of sections to organize
            
        Returns:
            Dict mapping parent section names to children (nested dicts)
        """
        hierarchy: Dict[str, Any] = {}
        current_parents: Dict[int, str] = {}
        
        for section in sections:
            level = section.level
            
            # Find parent
            parent_level = level - 1
            while parent_level > 0 and parent_level not in current_parents:
                parent_level -= 1
            
            parent = current_parents.get(parent_level)
            
            # Add to hierarchy
            if parent is None:
                # Top-level section
                hierarchy[section.name] = {}
            else:
                # Find parent in hierarchy and add
                self._add_to_hierarchy(hierarchy, parent, section.name)
            
            # Update current parents
            current_parents[level] = section.name
        
        return hierarchy
    
    def _add_to_hierarchy(
        self,
        hierarchy: Dict[str, Any],
        parent: str,
        child: str,
    ) -> None:
        """Add a child section to parent in hierarchy.
        
        Args:
            hierarchy: Hierarchy dict to modify
            parent: Parent section name
            child: Child section name to add
        """
        for key, value in hierarchy.items():
            if key == parent:
                if isinstance(value, dict):
                    value[child] = {}
                return
            if isinstance(value, dict):
                self._add_to_hierarchy(value, parent, child)
        
        return hierarchy
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _detect_type(self, path: Path, content: str) -> str:
        """Detect file type from path or content.
        
        Args:
            path: File path
            content: File content
            
        Returns:
            Detected file type string
        """
        suffix = path.suffix.lower() if path else ""
        
        type_map = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".py": "python",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
        }
        
        if suffix in type_map:
            return type_map[suffix]
        
        # Content-based detection
        if content.startswith("#") or "##" in content[:100]:
            return "markdown"
        if "def " in content[:500] or "class " in content[:500]:
            return "python"
        if content.strip().startswith("{"):
            return "json"
        
        return "unknown"
    
    def _parse_sections(self, lines: List[str], file_type: str) -> List[Section]:
        """Parse sections based on file type.
        
        Args:
            lines: Lines of content
            file_type: Type of file
            
        Returns:
            List of Section objects
        """
        if file_type == "markdown":
            return self._parse_markdown(lines)
        elif file_type == "python":
            return self._parse_python(lines)
        elif file_type == "yaml":
            return self._parse_yaml(lines)
        elif file_type == "json":
            return self._parse_json(lines)
        else:
            return []
    
    def _parse_markdown(self, lines: List[str]) -> List[Section]:
        """Parse markdown headers into sections.
        
        Args:
            lines: Lines of markdown
            
        Returns:
            List of Section objects
        """
        sections: List[Section] = []
        current_section: Optional[Section] = None
        in_code_block = False
        
        for i, line in enumerate(lines, start=1):
            # Track code blocks to avoid false header detection
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            # Check for headers (H1-H6)
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            
            if header_match:
                level = len(header_match.group(1))
                name = header_match.group(2).strip()
                
                # Close previous section
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                
                # Determine section type
                type_map = {
                    1: SectionType.MARKDOWN_H1,
                    2: SectionType.MARKDOWN_H2,
                    3: SectionType.MARKDOWN_H3,
                }
                section_type = type_map.get(level, SectionType.UNKNOWN)
                
                current_section = Section(
                    name=name,
                    section_type=section_type,
                    start_line=i,
                    end_line=i,
                    level=level,
                )
        
        # Close last section
        if current_section:
            current_section.end_line = len(lines)
            sections.append(current_section)
        
        return sections
    
    def _parse_python(self, lines: List[str]) -> List[Section]:
        """Parse Python classes and functions into sections.
        
        Args:
            lines: Lines of Python code
            
        Returns:
            List of Section objects
        """
        sections: List[Section] = []
        
        for i, line in enumerate(lines, start=1):
            # Class definition
            class_match = re.match(r"^class\s+(\w+)", line)
            if class_match:
                sections.append(Section(
                    name=class_match.group(1),
                    section_type=SectionType.PYTHON_CLASS,
                    start_line=i,
                    end_line=i,
                    level=1,
                ))
            
            # Function definition (top-level)
            func_match = re.match(r"^def\s+(\w+)", line)
            if func_match:
                sections.append(Section(
                    name=func_match.group(1),
                    section_type=SectionType.PYTHON_FUNCTION,
                    start_line=i,
                    end_line=i,
                    level=2,
                ))
            
            # Method definition (indented)
            method_match = re.match(r"^\s{4}def\s+(\w+)", line)
            if method_match:
                sections.append(Section(
                    name=method_match.group(1),
                    section_type=SectionType.PYTHON_FUNCTION,
                    start_line=i,
                    end_line=i,
                    level=3,
                ))
        
        return sections
    
    def _parse_yaml(self, lines: List[str]) -> List[Section]:
        """Parse YAML top-level keys into sections.
        
        Args:
            lines: Lines of YAML
            
        Returns:
            List of Section objects
        """
        sections: List[Section] = []
        
        for i, line in enumerate(lines, start=1):
            # Skip comments
            if line.strip().startswith("#"):
                continue
            
            # Top-level key (no indentation)
            key_match = re.match(r"^(\w[\w_-]*)\s*:", line)
            if key_match:
                sections.append(Section(
                    name=key_match.group(1),
                    section_type=SectionType.YAML_KEY,
                    start_line=i,
                    end_line=i,
                    level=1,
                ))
        
        return sections
    
    def _parse_json(self, lines: List[str]) -> List[Section]:
        """Parse JSON object keys into sections.
        
        Args:
            lines: Lines of JSON
            
        Returns:
            List of Section objects
        """
        sections: List[Section] = []
        
        for i, line in enumerate(lines, start=1):
            # Top-level object key
            key_match = re.match(r'^\s*"(\w+)"\s*:', line)
            if key_match:
                sections.append(Section(
                    name=key_match.group(1),
                    section_type=SectionType.YAML_KEY,  # Reuse YAML type
                    start_line=i,
                    end_line=i,
                    level=1,
                ))
        
        return sections
    
    def _find_version_markers(self, lines: List[str]) -> List[VersionMarker]:
        """Find version markers throughout content.
        
        Args:
            lines: Lines of content
            
        Returns:
            List of VersionMarker objects
        """
        markers: List[VersionMarker] = []
        total_lines = len(lines)
        
        patterns = [
            (r"\*\*Version:\*\*\s*([\d.]+)", "bold_version"),
            (r"Version:\s*([\d.]+)", "plain_version"),
            (r"\bv([\d.]+)\b", "v_prefix"),
            (r"version\s*[:=]\s*['\"]?([\d.]+)", "yaml_version"),
        ]
        
        for i, line in enumerate(lines, start=1):
            for pattern, pattern_type in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    version = match.group(1)
                    
                    # Determine location
                    if i <= 5:
                        location = "header"
                    elif i >= total_lines - 5:
                        location = "footer"
                    else:
                        location = "inline"
                    
                    markers.append(VersionMarker(
                        version=version,
                        location=location,
                        line_number=i,
                        raw_text=line.strip(),
                    ))
                    break  # Only one match per line
        
        return markers
    
    def _extract_metadata(self, content: str, file_type: str) -> Dict[str, Any]:
        """Extract metadata from content.
        
        Args:
            content: File content
            file_type: Type of file
            
        Returns:
            Dict of extracted metadata
        """
        metadata: Dict[str, Any] = {
            "file_type": file_type,
            "line_count": len(content.splitlines()),
            "char_count": len(content),
        }
        
        # Extract author if present
        author_match = re.search(r"Author:\s*(.+?)(?:\||$)", content)
        if author_match:
            metadata["author"] = author_match.group(1).strip()
        
        # Extract date if present
        date_match = re.search(r"Updated:\s*([\d-]+)", content)
        if date_match:
            metadata["updated"] = date_match.group(1)
        
        return metadata


# AC_COMPLETE: AC-ENH-101-005 ✅ StructureAnalyzer implementation
