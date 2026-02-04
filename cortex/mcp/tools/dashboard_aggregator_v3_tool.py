"""
MCP Tool for Dashboard Data Aggregation v3 (JSON-First).

Provides MCP-compatible wrapper for DashboardDataAggregatorV3 to generate
dashboard-data.json files for repository analysis visualization.

Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
AC-ID: DASHBOARD-V3-MCP-001
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_aggregate_dashboard_data_v3",
    description="Generate dashboard-data.json (v3 schema) for repository - JSON-first, SQLite optional",
    parameters={
        "repo_path": "string",
        "output_path": "string",
        "include_code_snippets": "boolean",
        "max_files": "number",
    }
)
def cortex_aggregate_dashboard_data_v3(
    repo_path: str,
    output_path: Optional[str] = None,
    include_code_snippets: bool = False,
    max_files: int = 1000,
) -> Dict[str, Any]:
    """
    Generate dashboard-data.json for repository intelligence dashboard.
    
    This tool aggregates repository data into a JSON file compatible with
    the CORTEX v3.0 dashboard SPA. The dashboard supports:
    - 13 tabs: Executive, Overview, Use Cases, Entities, Components, Files,
      Packages, Security, Quality, Testing, LENS Insights, Refactoring,
      Code Snippets
    - Dual-format support: JSON (generated) + SQLite (optional migration)
    - Browser-based: Vanilla JS + ECharts + Mermaid.js + Fuse.js
    - Offline-first: All data embedded, no fetch() calls
    
    JSON Schema v3.0 Features:
    - Snake_case field names (repo_summary, metrics_summary)
    - Pydantic v2 validation
    - 19 enums, 17 models
    - Full normalization (IDs for relationships)
    - Extensible for SQLite migration
    
    Args:
        repo_path: Absolute path to repository root
        output_path: Output path for dashboard-data.json
                    (default: company/dashboards/spa/{repo_slug}/dashboard-data.json)
        include_code_snippets: Whether to include code snippet samples
                              (WARNING: increases JSON size significantly)
        max_files: Maximum files to include in files array (default 1000)
        
    Returns:
        Dict with:
        - success: bool
        - output_path: str (path to generated JSON)
        - duration_seconds: float
        - stats: Dict with:
            - total_loc: int
            - total_files: int
            - health_score: int (0-100)
            - data_size_mb: float
        - error: Optional[str]
        
    Example:
        >>> result = cortex_aggregate_dashboard_data_v3(
        ...     repo_path="D:/PROJECTS/KSESSIONS",
        ...     output_path="company/dashboards/spa/KSESSIONS/dashboard-data.json",
        ...     include_code_snippets=False,
        ...     max_files=1000
        ... )
        >>> print(f"Generated: {result['output_path']}")
        >>> print(f"Health score: {result['stats']['health_score']}")
        
    MCP Usage:
        ```json
        {
            "tool": "cortex_aggregate_dashboard_data_v3",
            "parameters": {
                "repo_path": "/projects/my-repo",
                "output_path": "dashboards/my-repo/dashboard-data.json",
                "include_code_snippets": false,
                "max_files": 1000
            }
        }
        ```
        
    Related MCP Tools:
        - cortex_onboard_repository: Full onboarding + dashboard generation
        - cortex_generate_dashboard_suite: Multi-repo dashboard suite
        - cortex_serve_dashboard: Serve dashboard via HTTP
    """
    try:
        from cortex.lens.dashboard_data_aggregator_v3 import DashboardDataAggregatorV3
        
        # Validate repo path exists
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            return {
                "success": False,
                "output_path": None,
                "duration_seconds": 0.0,
                "stats": {},
                "error": f"Repository path not found: {repo_path}",
            }
        
        # Determine output path
        if output_path is None:
            repo_slug = repo_path_obj.name.lower()
            output_path = f"company/dashboards/spa/{repo_slug}/dashboard-data.json"
        
        output_path_obj = Path(output_path)
        
        # Create aggregator instance
        aggregator = DashboardDataAggregatorV3()
        
        # Execute aggregation
        logger.info(f"Aggregating dashboard data for: {repo_path}")
        result = aggregator.aggregate(repo_path_obj)
        
        if not result.success:
            return {
                "success": False,
                "output_path": None,
                "duration_seconds": result.duration_seconds,
                "stats": {},
                "error": result.error or "Aggregation failed",
            }
        
        # Write to file
        result.write_to_file(output_path_obj)
        
        # Calculate file size
        file_size_mb = output_path_obj.stat().st_size / (1024 * 1024)
        
        logger.info(
            f"Dashboard data generated: {output_path} "
            f"({file_size_mb:.2f} MB, {result.duration_seconds:.2f}s)"
        )
        
        return {
            "success": True,
            "output_path": str(output_path_obj.absolute()),
            "duration_seconds": result.duration_seconds,
            "stats": {
                "total_loc": result.data.get("metrics_summary", {}).get("total_loc", 0),
                "total_files": result.data.get("repo_summary", {}).get("total_files", 0),
                "health_score": result.data.get("repo_summary", {}).get("health_score", 0),
                "data_size_mb": round(file_size_mb, 2),
            },
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"cortex_aggregate_dashboard_data_v3 failed: {e}", exc_info=True)
        return {
            "success": False,
            "output_path": None,
            "duration_seconds": 0.0,
            "stats": {},
            "error": str(e),
        }


@mcp_tool(
    name="cortex_serve_dashboard",
    description="Serve dashboard SPA via HTTP server (Python http.server)",
    parameters={
        "port": "number",
        "directory": "string",
    }
)
def cortex_serve_dashboard(
    port: int = 8888,
    directory: str = "company/dashboards/spa",
) -> Dict[str, Any]:
    """
    Start HTTP server to serve dashboard SPA.
    
    This tool starts a simple HTTP server (Python's http.server module) to
    serve the dashboard SPA for local viewing. The server runs in the
    background and serves all dashboard files (HTML, JS, CSS, JSON data).
    
    Args:
        port: HTTP port (default 8888)
        directory: Root directory to serve (default company/dashboards/spa)
        
    Returns:
        Dict with:
        - success: bool
        - url: str (HTTP URL to access dashboard)
        - port: int
        - directory: str
        - pid: int (process ID)
        - error: Optional[str]
        
    Example:
        >>> result = cortex_serve_dashboard(port=8888)
        >>> print(f"Dashboard: {result['url']}")
        >>> # Open in browser: http://localhost:8888/dashboard.html?repo=KSESSIONS
        
    Note:
        - Server runs in background (does not block)
        - Access via: http://localhost:{port}/dashboard.html?repo={REPO_NAME}
        - Stop via: Kill process using returned PID
        - Auto-detects MIME types (HTML, CSS, JS, JSON, PNG, etc.)
    """
    import subprocess
    import os
    
    try:
        directory_path = Path(directory)
        if not directory_path.exists():
            return {
                "success": False,
                "url": None,
                "port": port,
                "directory": directory,
                "pid": None,
                "error": f"Directory not found: {directory}",
            }
        
        # Start HTTP server in background
        cmd = f"python -m http.server {port}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(directory_path.absolute()),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        url = f"http://localhost:{port}"
        
        logger.info(f"Dashboard server started: {url} (PID: {process.pid})")
        
        return {
            "success": True,
            "url": url,
            "port": port,
            "directory": str(directory_path.absolute()),
            "pid": process.pid,
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"cortex_serve_dashboard failed: {e}", exc_info=True)
        return {
            "success": False,
            "url": None,
            "port": port,
            "directory": directory,
            "pid": None,
            "error": str(e),
        }


@mcp_tool(
    name="cortex_test_dashboard_e2e",
    description="Run Playwright E2E tests for dashboard SPA (browser validation)",
    parameters={
        "test_pattern": "string",
        "headed": "boolean",
    }
)
def cortex_test_dashboard_e2e(
    test_pattern: str = "tests/e2e/dashboard-browser.spec.js",
    headed: bool = False,
) -> Dict[str, Any]:
    """
    Run Playwright E2E tests for dashboard browser validation.
    
    This tool runs browser-based E2E tests using Playwright to validate:
    - Script loading (JSONDataAdapter, DualFormatDataLoader, ECharts, Mermaid)
    - Data fetching (dashboard-data.json)
    - UI rendering (tabs, charts, tables)
    - Navigation (tab switching, pagination)
    - No console errors
    
    Args:
        test_pattern: Test file pattern (default: dashboard-browser.spec.js)
        headed: Run in headed mode (visible browser, default: headless)
        
    Returns:
        Dict with:
        - success: bool
        - passed: int (number of passing tests)
        - failed: int (number of failing tests)
        - duration_seconds: float
        - output: str (test output)
        - error: Optional[str]
        
    Example:
        >>> result = cortex_test_dashboard_e2e()
        >>> print(f"Tests: {result['passed']} passed, {result['failed']} failed")
        
    Note:
        - Requires Playwright installed: npm install @playwright/test
        - Requires browsers: npx playwright install chromium
        - Auto-starts HTTP server on port 8888
        - Generates screenshots/videos on failure
    """
    import subprocess
    
    try:
        spa_dir = Path("company/dashboards/spa")
        if not spa_dir.exists():
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "duration_seconds": 0.0,
                "output": "",
                "error": f"Dashboard SPA directory not found: {spa_dir}",
            }
        
        # Build Playwright command
        cmd = ["npx", "playwright", "test"]
        if headed:
            cmd.append("--headed")
        if test_pattern:
            cmd.append(test_pattern)
        
        # Run tests
        import time
        start = time.time()
        
        result = subprocess.run(
            cmd,
            cwd=str(spa_dir.absolute()),
            capture_output=True,
            text=True,
        )
        
        duration = time.time() - start
        
        # Parse output for pass/fail counts
        output = result.stdout + result.stderr
        passed = output.count(" passed")
        failed = output.count(" failed")
        
        success = result.returncode == 0
        
        logger.info(
            f"Playwright tests: {passed} passed, {failed} failed "
            f"({duration:.2f}s)"
        )
        
        return {
            "success": success,
            "passed": passed,
            "failed": failed,
            "duration_seconds": round(duration, 2),
            "output": output,
            "error": None if success else f"Tests failed (exit code {result.returncode})",
        }
        
    except Exception as e:
        logger.error(f"cortex_test_dashboard_e2e failed: {e}", exc_info=True)
        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "duration_seconds": 0.0,
            "output": "",
            "error": str(e),
        }
