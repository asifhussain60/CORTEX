"""
MCP-FIRST Violation Detector - Ensures all IMPLEMENT/FIX/REFACTOR operations
route through MCP tools instead of direct file operations.

AC_START: AC-WAVE-K-004
Description: MCP-FIRST architecture compliance verification
Authority: copilot-instructions.md § COPILOT NATIVE TOOL RESTRICTIONS
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set
import ast
import re


@dataclass
class MCPViolation:
    """Represents a violation of MCP-FIRST architecture."""
    
    file_path: str
    line_number: int
    violation_type: str
    description: str
    detected_at: datetime
    severity: str = "P0"  # MCP-FIRST is always critical


@dataclass
class MCPComplianceReport:
    """Report of MCP-FIRST compliance check."""
    
    files_checked: int
    violations: List[MCPViolation]
    compliance_rate: float
    timestamp: datetime
    
    def is_compliant(self) -> bool:
        """Check if 100% MCP-FIRST compliant."""
        return len(self.violations) == 0


class MCPFirstDetector:
    """
    Detects violations of MCP-FIRST architecture.
    
    MCP-FIRST Rule:
    - All IMPLEMENT/FIX/REFACTOR intents MUST use cortex_process_request
    - NO direct file creation via native tools (create_file, replace_string_in_file)
    - NO terminal file operations in implementation contexts
    
    AC_START: AC-WAVE-K-005
    Description: MCP-FIRST violation detection implementation
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize MCP-FIRST detector.
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.violations: List[MCPViolation] = []
        self.files_checked = 0
        
        # Forbidden operations in implementation context
        self.forbidden_patterns = {
            "create_file": "Direct file creation (use cortex_process_request)",
            "replace_string_in_file": "Direct file edit (use cortex_process_request)",
            "edit_files": "Direct file edit (use cortex_process_request)",
            "run_in_terminal.*>": "File operation via terminal (use cortex_process_request)",
            "edit_notebook_file": "Direct notebook edit (use cortex_process_request)",
        }
        
        # Intent keywords that trigger MCP-FIRST requirement
        self.implementation_intents = [
            "IMPLEMENT",
            "FIX",
            "REFACTOR",
            "implement",
            "fix",
            "refactor",
        ]
    
    def detect_violations(self) -> MCPComplianceReport:
        """
        Detect all MCP-FIRST violations in workspace.
        
        Returns:
            MCPComplianceReport with violations
        """
        self.violations = []
        self.files_checked = 0
        
        # Check Python files for direct file operations
        cortex_dir = self.workspace_root / "cortex"
        if cortex_dir.exists():
            self._check_python_files(cortex_dir)
        
        # Check orchestrator files (high-risk area)
        orchestrators_dir = self.workspace_root / "cortex" / "orchestrators"
        if orchestrators_dir.exists():
            self._check_orchestrators(orchestrators_dir)
        
        # Calculate compliance rate
        compliance_rate = (
            ((self.files_checked - len(self.violations)) / self.files_checked * 100)
            if self.files_checked > 0 else 100.0
        )
        
        return MCPComplianceReport(
            files_checked=self.files_checked,
            violations=self.violations,
            compliance_rate=compliance_rate,
            timestamp=datetime.now()
        )
    
    def _check_python_files(self, directory: Path):
        """
        Check Python files for direct file operations.
        
        Args:
            directory: Directory to scan
        """
        for py_file in directory.rglob("*.py"):
            self.files_checked += 1
            
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                
                # Check for forbidden patterns
                for pattern, description in self.forbidden_patterns.items():
                    matches = list(re.finditer(pattern, content))
                    
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Check if in implementation context
                        if self._is_implementation_context(content, match.start()):
                            self.violations.append(MCPViolation(
                                file_path=str(py_file.relative_to(self.workspace_root)),
                                line_number=line_num,
                                violation_type="DIRECT_FILE_OPERATION",
                                description=f"{pattern}: {description}",
                                detected_at=datetime.now(),
                                severity="P0"
                            ))
            except Exception:
                # Skip files that can't be read
                pass
    
    def _check_orchestrators(self, directory: Path):
        """
        Check orchestrator files for MCP routing compliance.
        
        Orchestrators should delegate to MCP tools, not perform direct operations.
        
        Args:
            directory: Orchestrators directory
        """
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Check for direct file I/O operations
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Check for open() calls
                        if self._is_open_call(node):
                            self.violations.append(MCPViolation(
                                file_path=str(py_file.relative_to(self.workspace_root)),
                                line_number=node.lineno,
                                violation_type="DIRECT_FILE_IO",
                                description="Direct file I/O (use MCP tool instead)",
                                detected_at=datetime.now(),
                                severity="P0"
                            ))
                        
                        # Check for Path().write_text() calls
                        if self._is_path_write(node):
                            self.violations.append(MCPViolation(
                                file_path=str(py_file.relative_to(self.workspace_root)),
                                line_number=node.lineno,
                                violation_type="DIRECT_PATH_WRITE",
                                description="Direct Path.write_text() (use MCP tool)",
                                detected_at=datetime.now(),
                                severity="P0"
                            ))
            except Exception:
                pass
    
    def _is_implementation_context(self, content: str, position: int) -> bool:
        """
        Check if position in content is within implementation context.
        
        Implementation context = function/method that handles IMPLEMENT/FIX/REFACTOR.
        
        Args:
            content: File content
            position: Character position to check
        
        Returns:
            True if in implementation context
        """
        # Get surrounding context (500 chars before)
        context_start = max(0, position - 500)
        context = content[context_start:position]
        
        # Check for implementation intent keywords
        for intent in self.implementation_intents:
            if intent in context:
                return True
        
        # Check for orchestrator execute/process methods
        if "def execute(" in context or "def process(" in context:
            return True
        
        return False
    
    def _is_open_call(self, node: ast.Call) -> bool:
        """
        Check if AST node is an open() call.
        
        Args:
            node: AST Call node
        
        Returns:
            True if open() call with write mode
        """
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            # Check for write mode ('w', 'a', 'w+')
            if len(node.args) >= 2:
                if isinstance(node.args[1], ast.Constant):
                    mode = node.args[1].value
                    if isinstance(mode, str) and ('w' in mode or 'a' in mode):
                        return True
        
        return False
    
    def _is_path_write(self, node: ast.Call) -> bool:
        """
        Check if AST node is a Path().write_text() call.
        
        Args:
            node: AST Call node
        
        Returns:
            True if Path write operation
        """
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["write_text", "write_bytes"]:
                return True
        
        return False
    
    def check_intent_routing(self, intent: str) -> bool:
        """
        Check if intent requires MCP routing.
        
        Args:
            intent: User intent string
        
        Returns:
            True if MCP routing required
        """
        return any(kw in intent for kw in self.implementation_intents)
    
    def get_violation_summary(self) -> dict:
        """
        Get summary of violations by type.
        
        Returns:
            Dictionary mapping violation types to counts
        """
        summary = {}
        
        for violation in self.violations:
            vtype = violation.violation_type
            summary[vtype] = summary.get(vtype, 0) + 1
        
        return summary


# AC_COMPLETE: AC-WAVE-K-005 ✅
