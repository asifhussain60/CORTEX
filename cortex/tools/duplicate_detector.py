"""
Duplicate Implementation Detector for CORTEX.

Implements AC-PERMANENT-FIX-007 and CORE-035 enforcement.
Detects conflicting implementations that violate Single Canonical Implementation principle.

Author: CORTEX Framework
"""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DuplicateViolation:
    """Represents a duplicate implementation violation."""
    class_name: str
    paths: List[Path]
    violation_type: str  # "class_definition", "interface_implementation", "mcp_tool"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM"
    description: str
    remediation: str


class DuplicateDetector:
    """Detects duplicate implementations across CORTEX codebase."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.cortex_root = workspace_root / "cortex"
        self.violations: List[DuplicateViolation] = []

    def detect_all_duplicates(self) -> List[DuplicateViolation]:
        """Detect all types of duplicate implementations."""
        logger.info("Starting comprehensive duplicate detection...")

        # Reset violations
        self.violations = []

        # Detect different types of duplicates
        self._detect_class_duplicates()
        self._detect_interface_duplicates()
        self._detect_mcp_tool_duplicates()

        logger.info(f"Found {len(self.violations)} duplicate violations")
        return self.violations

    def _detect_class_duplicates(self) -> None:
        """Detect duplicate class definitions."""
        class_locations: Dict[str, List[Path]] = defaultdict(list)

        # Scan all Python files for class definitions
        for py_file in self.cortex_root.rglob("*.py"):
            if py_file.name.startswith("test_") or "/test" in str(py_file):
                continue  # Skip test files

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_locations[node.name].append(py_file)

            except (SyntaxError, UnicodeDecodeError) as e:
                logger.warning(f"Could not parse {py_file}: {e}")

        # Find duplicates
        for class_name, paths in class_locations.items():
            if len(paths) > 1:
                # Special handling for known critical classes
                severity = "CRITICAL" if class_name in {
                    "ConversationProtocol", "MasterOrchestrator", "InteractionOrchestrator"
                } else "HIGH"

                violation = DuplicateViolation(
                    class_name=class_name,
                    paths=paths,
                    violation_type="class_definition",
                    severity=severity,
                    description=f"Class {class_name} defined in {len(paths)} locations: {[str(p) for p in paths]}",
                    remediation=f"Consolidate {class_name} into single canonical implementation"
                )
                self.violations.append(violation)

    def _detect_interface_duplicates(self) -> None:
        """Detect multiple implementations of same interface with different behavior."""
        # Look for common interface patterns
        interface_patterns = [
            ("IOrchestrator", "process"),
            ("Tool", "definition"),
            ("ConversationProtocol", "execute_turn")
        ]

        for interface_name, method_name in interface_patterns:
            implementations = self._find_interface_implementations(interface_name, method_name)
            if len(implementations) > 1:
                # Check if they have different implementations
                if self._implementations_differ(implementations):
                    violation = DuplicateViolation(
                        class_name=f"{interface_name} implementations",
                        paths=[Path(impl["file"]) for impl in implementations],
                        violation_type="interface_implementation",
                        severity="HIGH",
                        description=f"Multiple conflicting implementations of {interface_name}.{method_name}",
                        remediation=f"Standardize {interface_name} implementation behavior"
                    )
                    self.violations.append(violation)

    def _detect_mcp_tool_duplicates(self) -> None:
        """Detect duplicate MCP tool names or schemas."""
        tool_names: Dict[str, List[Path]] = defaultdict(list)

        # Scan for MCP tool definitions
        mcp_patterns = ["get_mcp_tools", "ToolDefinition", "name="]

        for py_file in self.cortex_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple pattern matching for tool names
                if any(pattern in content for pattern in mcp_patterns):
                    # Extract tool names (simplified approach)
                    lines = content.split('\n')
                    for line in lines:
                        if 'name="' in line or "name='" in line:
                            # Extract tool name
                            start = line.find('name="') + 6 if 'name="' in line else line.find("name='") + 6
                            end = line.find('"', start) if 'name="' in line else line.find("'", start)
                            if start > 5 and end > start:
                                tool_name = line[start:end]
                                if tool_name.startswith("cortex_"):
                                    tool_names[tool_name].append(py_file)

            except (UnicodeDecodeError, FileNotFoundError):
                continue

        # Find tool name duplicates
        for tool_name, paths in tool_names.items():
            if len(paths) > 1:
                violation = DuplicateViolation(
                    class_name=f"MCP Tool: {tool_name}",
                    paths=paths,
                    violation_type="mcp_tool",
                    severity="MEDIUM",
                    description=f"MCP tool {tool_name} defined in {len(paths)} locations",
                    remediation=f"Consolidate MCP tool {tool_name} to single definition"
                )
                self.violations.append(violation)

    def _find_interface_implementations(self, interface_name: str, method_name: str) -> List[Dict]:
        """Find all implementations of a given interface method."""
        implementations = []

        for py_file in self.cortex_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if interface_name in content and f"def {method_name}" in content:
                    implementations.append({
                        "file": str(py_file),
                        "content": content
                    })

            except (UnicodeDecodeError, FileNotFoundError):
                continue

        return implementations

    def _implementations_differ(self, implementations: List[Dict]) -> bool:
        """Check if implementations have significantly different behavior."""
        # Simplified heuristic: check if method bodies are significantly different
        if len(implementations) < 2:
            return False

        # Compare method body lengths as simple heuristic
        contents = [impl["content"] for impl in implementations]
        lengths = [len(content) for content in contents]

        # If implementations vary by more than 50%, consider them different
        min_len, max_len = min(lengths), max(lengths)
        return (max_len - min_len) / max_len > 0.5 if max_len > 0 else False


def detect_class_conflicts() -> List[DuplicateViolation]:
    """Entry point for governance rule validation."""
    detector = DuplicateDetector(Path.cwd())
    return detector.detect_all_duplicates()


def main():
    """CLI entry point for duplicate detection."""
    import sys

    detector = DuplicateDetector(Path.cwd())
    violations = detector.detect_all_duplicates()

    if violations:
        print(f"🚨 CORE-035 VIOLATIONS: Found {len(violations)} duplicate implementations")
        for violation in violations:
            print(f"  - {violation.severity}: {violation.description}")
            print(f"    Remediation: {violation.remediation}")
        sys.exit(1)
    else:
        print("✅ No duplicate implementations found")
        sys.exit(0)


if __name__ == "__main__":
    main()
