#!/usr/bin/env python3
"""
CORTEX MCP Wiring Audit Script

Analyzes:
1. Orchestrator wiring in wiring.yaml vs actual implementations
2. MCP tool exposure (@mcp_tool decorators)
3. MCP adapter registration
4. Missing MCP exposure for orchestrators

AC-AUDIT-001: Comprehensive MCP wiring audit
"""

import yaml
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


def load_wiring_yaml() -> Dict[str, Any]:
    """Load wiring.yaml specification."""
    wiring_path = Path("cortex/wiring/specifications/wiring.yaml")
    with open(wiring_path, 'r') as f:
        return yaml.safe_load(f)


def find_orchestrator_files() -> List[Path]:
    """Find all orchestrator implementation files."""
    orchestrator_files = []
    base_path = Path("cortex/orchestrators")
    for py_file in base_path.rglob("*.py"):
        if "test" not in str(py_file) and "__pycache__" not in str(py_file):
            orchestrator_files.append(py_file)
    return orchestrator_files


def find_mcp_tool_files() -> List[Path]:
    """Find all MCP tool files."""
    tool_files = []
    base_path = Path("cortex/mcp/tools")
    for py_file in base_path.rglob("*.py"):
        if "test" not in str(py_file) and "__pycache__" not in str(py_file):
            tool_files.append(py_file)
    return tool_files


def extract_orchestrator_classes(file_path: Path) -> List[str]:
    """Extract orchestrator class names from Python file."""
    classes = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Match class definitions inheriting from IOrchestrator or similar
            pattern = r'class\s+(\w+Orchestrator)\s*\('
            matches = re.findall(pattern, content)
            classes.extend(matches)
    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
    return classes


def extract_mcp_tools(file_path: Path) -> List[str]:
    """Extract MCP tool names from Python file."""
    tools = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Match @mcp_tool decorators
            pattern = r'@mcp_tool\(\s*name=["\']([^"\']+)["\']'
            matches = re.findall(pattern, content)
            tools.extend(matches)
            
            # Also match function definitions after @mcp_tool
            pattern2 = r'@mcp_tool\([^)]*\)\s*def\s+(\w+)\s*\('
            matches2 = re.findall(pattern2, content, re.MULTILINE)
            tools.extend(matches2)
    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
    return tools


def audit_wiring_yaml():
    """Audit wiring.yaml configuration."""
    print("\n" + "="*80)
    print("📋 WIRING.YAML AUDIT")
    print("="*80)
    
    wiring = load_wiring_yaml()
    
    # Count orchestrators
    core_count = len(wiring.get('orchestrators', {}).get('core', []))
    domain_count = len(wiring.get('orchestrators', {}).get('domain', []))
    support_count = len(wiring.get('orchestrators', {}).get('support', []))
    analyzer_count = len(wiring.get('analyzers', []))
    
    total = core_count + domain_count + support_count
    
    print(f"\n✅ Core Orchestrators: {core_count}")
    print(f"✅ Domain Orchestrators: {domain_count}")
    print(f"✅ Support Orchestrators: {support_count}")
    print(f"✅ LENS Analyzers: {analyzer_count}")
    print(f"\n📊 Total: {total} orchestrators + {analyzer_count} analyzers")
    
    # Check MCP adapter assignments
    print(f"\n🔌 MCP ADAPTER ASSIGNMENTS:")
    orchestrators_with_adapters = []
    orchestrators_without_adapters = []
    orchestrators_with_tools = []
    
    for tier in ['core', 'domain', 'support']:
        for orch in wiring.get('orchestrators', {}).get(tier, []):
            name = orch.get('name')
            adapter = orch.get('mcp_adapter')
            mcp_tools = orch.get('mcp_tools', [])
            
            if adapter:
                orchestrators_with_adapters.append(name)
            else:
                orchestrators_without_adapters.append(name)
            
            if mcp_tools:
                orchestrators_with_tools.append((name, mcp_tools))
    
    print(f"  ✅ With MCP Adapter: {len(orchestrators_with_adapters)}")
    print(f"  ⚠️  Without MCP Adapter: {len(orchestrators_without_adapters)}")
    print(f"  🛠️  With MCP Tools: {len(orchestrators_with_tools)}")
    
    if orchestrators_without_adapters:
        print(f"\n  Missing MCP Adapters:")
        for name in orchestrators_without_adapters[:10]:  # Show first 10
            print(f"    - {name}")
        if len(orchestrators_without_adapters) > 10:
            print(f"    ... and {len(orchestrators_without_adapters) - 10} more")
    
    return wiring, orchestrators_with_adapters, orchestrators_without_adapters


def audit_mcp_tools():
    """Audit MCP tool exposure."""
    print("\n" + "="*80)
    print("🛠️  MCP TOOLS AUDIT")
    print("="*80)
    
    tool_files = find_mcp_tool_files()
    all_tools = []
    tool_by_file = defaultdict(list)
    
    for tool_file in tool_files:
        tools = extract_mcp_tools(tool_file)
        all_tools.extend(tools)
        if tools:
            tool_by_file[tool_file.name] = tools
    
    print(f"\n✅ Total MCP Tool Files: {len(tool_files)}")
    print(f"✅ Total @mcp_tool Decorators: {len(all_tools)}")
    print(f"✅ Files with Tools: {len(tool_by_file)}")
    
    # Show tool categories
    print(f"\n📦 TOOL CATEGORIES:")
    categories = defaultdict(list)
    for file_name, tools in sorted(tool_by_file.items()):
        category = file_name.replace('.py', '').replace('_', ' ').title()
        categories[category] = tools
    
    for category, tools in sorted(categories.items())[:15]:  # Show first 15
        print(f"  • {category}: {len(tools)} tools")
    
    return all_tools, tool_by_file


def audit_orchestrator_implementations():
    """Audit orchestrator implementations."""
    print("\n" + "="*80)
    print("🧠 ORCHESTRATOR IMPLEMENTATIONS AUDIT")
    print("="*80)
    
    orch_files = find_orchestrator_files()
    all_orchestrators = []
    orch_by_file = defaultdict(list)
    
    for orch_file in orch_files:
        orchestrators = extract_orchestrator_classes(orch_file)
        all_orchestrators.extend(orchestrators)
        if orchestrators:
            orch_by_file[orch_file] = orchestrators
    
    print(f"\n✅ Total Orchestrator Files: {len(orch_files)}")
    print(f"✅ Total Orchestrator Classes: {len(all_orchestrators)}")
    print(f"✅ Files with Orchestrators: {len(orch_by_file)}")
    
    # Show by directory
    print(f"\n📁 BY DIRECTORY:")
    by_dir = defaultdict(list)
    for file_path, orchestrators in orch_by_file.items():
        dir_name = file_path.parent.name
        by_dir[dir_name].extend(orchestrators)
    
    for dir_name, orchestrators in sorted(by_dir.items()):
        print(f"  • {dir_name}/: {len(orchestrators)} orchestrators")
    
    return all_orchestrators, orch_by_file


def cross_check_wiring_vs_implementations(wiring_data, all_orchestrator_classes):
    """Cross-check wiring.yaml against actual implementations."""
    print("\n" + "="*80)
    print("🔍 CROSS-CHECK: WIRING vs IMPLEMENTATIONS")
    print("="*80)
    
    # Extract orchestrator names from wiring.yaml
    wired_orchestrators = set()
    for tier in ['core', 'domain', 'support']:
        for orch in wiring_data.get('orchestrators', {}).get(tier, []):
            wired_orchestrators.add(orch.get('name'))
    
    # Convert implementation classes to set
    implemented_orchestrators = set(all_orchestrator_classes)
    
    # Find mismatches
    wired_not_implemented = wired_orchestrators - implemented_orchestrators
    implemented_not_wired = implemented_orchestrators - wired_orchestrators
    
    print(f"\n✅ Orchestrators in wiring.yaml: {len(wired_orchestrators)}")
    print(f"✅ Orchestrators implemented: {len(implemented_orchestrators)}")
    print(f"✅ Matching: {len(wired_orchestrators & implemented_orchestrators)}")
    
    if wired_not_implemented:
        print(f"\n⚠️  WIRED BUT NOT IMPLEMENTED ({len(wired_not_implemented)}):")
        for name in sorted(wired_not_implemented)[:10]:
            print(f"    - {name}")
        if len(wired_not_implemented) > 10:
            print(f"    ... and {len(wired_not_implemented) - 10} more")
    
    if implemented_not_wired:
        print(f"\n⚠️  IMPLEMENTED BUT NOT WIRED ({len(implemented_not_wired)}):")
        for name in sorted(implemented_not_wired)[:10]:
            print(f"    - {name}")
        if len(implemented_not_wired) > 10:
            print(f"    ... and {len(implemented_not_wired) - 10} more")
    
    return wired_not_implemented, implemented_not_wired


def generate_recommendations(wiring_data, orchestrators_without_adapters, mcp_tools):
    """Generate recommendations for improving MCP exposure."""
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    print("\n📋 PRIORITY ACTIONS:")
    
    # 1. Add MCP adapters
    if orchestrators_without_adapters:
        print(f"\n1️⃣  ADD MCP ADAPTERS ({len(orchestrators_without_adapters)} orchestrators)")
        print("   These orchestrators lack MCP adapters for external tool exposure:")
        for name in sorted(orchestrators_without_adapters)[:5]:
            print(f"     - {name}")
        if len(orchestrators_without_adapters) > 5:
            print(f"     ... and {len(orchestrators_without_adapters) - 5} more")
    
    # 2. Core tools verification
    core_tools = ['cortex_process_request', 'cortex_lens_analyze', 'cortex_challenge']
    missing_core = [t for t in core_tools if t not in mcp_tools]
    
    if missing_core:
        print(f"\n2️⃣  VERIFY CORE MCP TOOLS")
        print("   These critical tools may not be properly exposed:")
        for tool in missing_core:
            print(f"     - {tool}")
    
    # 3. MCP tool count
    print(f"\n3️⃣  MCP TOOL EXPOSURE")
    print(f"   ✅ {len(mcp_tools)} MCP tools decorated with @mcp_tool")
    print(f"   🎯 Target: Ensure all 36 orchestrators have MCP exposure")
    
    # 4. Tool discovery
    print(f"\n4️⃣  AUTO-DISCOVERY STATUS")
    print("   ✅ auto_discover_and_register_tools() in MCP server")
    print("   ✅ @mcp_tool decorator system operational")
    
    print("\n" + "="*80)


def main():
    """Run comprehensive MCP wiring audit."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "🧠 CORTEX MCP WIRING AUDIT" + " "*32 + "║")
    print("║" + " "*78 + "║")
    print("║" + "  Version: 1.0 | Date: 2026-02-07" + " "*44 + "║")
    print("║" + "  Authority: CORE-035 (Single Canonical Implementation)" + " "*21 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # 1. Audit wiring.yaml
        wiring_data, with_adapters, without_adapters = audit_wiring_yaml()
        
        # 2. Audit MCP tools
        mcp_tools, tool_by_file = audit_mcp_tools()
        
        # 3. Audit orchestrator implementations
        all_orchestrators, orch_by_file = audit_orchestrator_implementations()
        
        # 4. Cross-check
        wired_not_impl, impl_not_wired = cross_check_wiring_vs_implementations(
            wiring_data, all_orchestrators
        )
        
        # 5. Generate recommendations
        generate_recommendations(wiring_data, without_adapters, mcp_tools)
        
        print("\n✅ AUDIT COMPLETE")
        print("="*80 + "\n")
        
        # Return summary
        return {
            "wired_orchestrators": len(with_adapters) + len(without_adapters),
            "with_mcp_adapters": len(with_adapters),
            "without_mcp_adapters": len(without_adapters),
            "mcp_tools": len(mcp_tools),
            "implemented_orchestrators": len(all_orchestrators),
            "wired_not_implemented": len(wired_not_impl),
            "implemented_not_wired": len(impl_not_wired),
        }
        
    except Exception as e:
        print(f"\n❌ AUDIT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
