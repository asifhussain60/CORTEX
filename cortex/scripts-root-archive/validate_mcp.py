#!/usr/bin/env python3
"""
CORTEX MCP Server Validation Script

Validates that the MCP server and all dependencies are properly installed
and functional.

Usage:
    python scripts/validate_mcp.py
"""

import sys
import importlib
from typing import List, Tuple


def check_module(module_name: str, display_name: str = None) -> Tuple[bool, str]:
    """Check if a module can be imported."""
    if display_name is None:
        display_name = module_name
    
    try:
        importlib.import_module(module_name)
        return True, f"✓ {display_name}"
    except ImportError as e:
        return False, f"✗ {display_name}: {e}"


def main() -> int:
    """Main validation function."""
    print("=" * 70)
    print("CORTEX MCP Server Validation")
    print("=" * 70)
    print()
    
    # Core dependencies
    print("Core Dependencies:")
    print("-" * 70)
    
    checks: List[Tuple[str, str]] = [
        ("yaml", "PyYAML"),
        ("pydantic", "Pydantic"),
        ("click", "Click"),
        ("dotenv", "python-dotenv"),
        ("psutil", "psutil"),
        ("dependency_injector", "dependency-injector"),
        ("prometheus_client", "prometheus-client"),
    ]
    
    core_results = [check_module(mod, name) for mod, name in checks]
    for success, msg in core_results:
        print(msg)
    
    # Web framework
    print("\nWeb Framework:")
    print("-" * 70)
    
    web_checks = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("httpx", "HTTPX"),
        ("requests", "Requests"),
    ]
    
    web_results = [check_module(mod, name) for mod, name in web_checks]
    for success, msg in web_results:
        print(msg)
    
    # Testing framework
    print("\nTesting Framework:")
    print("-" * 70)
    
    test_checks = [
        ("pytest", "pytest"),
        ("pytest_cov", "pytest-cov"),
        ("pytest_asyncio", "pytest-asyncio"),
        ("pytest_timeout", "pytest-timeout"),
        ("pytest_mock", "pytest-mock"),
        ("xdist", "pytest-xdist"),
    ]
    
    test_results = [check_module(mod, name) for mod, name in test_checks]
    for success, msg in test_results:
        print(msg)
    
    # Code quality
    print("\nCode Quality Tools:")
    print("-" * 70)
    
    quality_checks = [
        ("black", "black"),
        ("isort", "isort"),
        ("mypy", "mypy"),
        ("pylint", "pylint"),
        ("flake8", "flake8"),
    ]
    
    quality_results = [check_module(mod, name) for mod, name in quality_checks]
    for success, msg in quality_results:
        print(msg)
    
    # CORTEX MCP modules
    print("\nCORTEX MCP Modules:")
    print("-" * 70)
    
    cortex_checks = [
        ("cortex.mcp", "cortex.mcp"),
        ("cortex.mcp.server", "cortex.mcp.server"),
        ("cortex.mcp.protocol", "cortex.mcp.protocol"),
        ("cortex.mcp.registry", "cortex.mcp.registry"),
        ("cortex.mcp.tool_discovery", "cortex.mcp.tool_discovery"),
    ]
    
    cortex_results = [check_module(mod, name) for mod, name in cortex_checks]
    for success, msg in cortex_results:
        print(msg)
    
    # Test MCP server functionality
    print("\nMCP Server Functional Tests:")
    print("-" * 70)
    
    try:
        from cortex.mcp import MCPServer
        server = MCPServer()
        tools = server.list_tools()
        print(f"✓ MCP Server created successfully")
        print(f"✓ {len(tools)} tools registered")
        
        # Test tool execution
        response = server.call_tool("sample_tool", {"input": "test"}, "validation-1")
        print(f"✓ Tool execution successful")
        
    except Exception as e:
        print(f"✗ MCP Server test failed: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 70)
    all_results = core_results + web_results + test_results + quality_results + cortex_results
    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)
    failed = total - passed
    
    print(f"Validation Summary: {passed}/{total} checks passed")
    
    if failed > 0:
        print(f"WARNING: {failed} checks failed")
        print("\nMCP Server is partially functional but some dependencies are missing.")
        return 1
    else:
        print("\n✓ All validation checks passed!")
        print("✓ MCP Server is fully operational")
        return 0


if __name__ == "__main__":
    sys.exit(main())
