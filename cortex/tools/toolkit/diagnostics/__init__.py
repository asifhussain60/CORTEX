"""
CORTEX Toolkit - Diagnostics Module

Consolidates MCP health checks and environment diagnostics.

**Consolidated Scripts:**
- .cortex-runtime/diagnose-mcp.py
- .cortex-runtime/verify-mcp-setup.py
- .cortex-runtime/verify-mcp-tools.py
- .cortex-runtime/verify-mcp-fix.py

**Authority:** Phase 90 S-90-03
"""

from cortex.tools.toolkit.diagnostics.mcp_health import MCPHealthChecker

# Import consolidated diagnostics from Phase 90
try:
    from pathlib import Path
    
    # Import from sibling diagnostics.py file
    diagnostics_file = Path(__file__).parent.parent / "diagnostics.py"
    if diagnostics_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("toolkit_diagnostics", diagnostics_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            MCPDiagnostics = module.MCPDiagnostics
            DiagnosticResult = module.DiagnosticResult
            DiagnosticLevel = module.DiagnosticLevel
    else:
        # Fallback - use MCPHealthChecker as alias
        MCPDiagnostics = MCPHealthChecker
        DiagnosticResult = None
        DiagnosticLevel = None
except Exception:
    MCPDiagnostics = MCPHealthChecker
    DiagnosticResult = None
    DiagnosticLevel = None

__all__ = [
    "MCPHealthChecker",
    "MCPDiagnostics",
    "DiagnosticResult",
    "DiagnosticLevel",
]
