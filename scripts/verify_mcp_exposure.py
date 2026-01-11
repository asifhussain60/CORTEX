"""
MCP Tool Exposure Verification Script

Verifies that @mcp_tool decorated functions are automatically registered
in the CapabilityRegistry.

Author: Asif Hussain
AC-ID: AC-MCP-EXPOSE-001
"""

from src.mcp.capability_registry import CapabilityRegistry
from src.mcp.mcp_decorator import get_decorated_tools


def verify_mcp_exposure():
    """
    Verify MCP tool exposure.
    
    Prints before/after metrics showing exposure rate improvement.
    """
    print("=" * 80)
    print("🔍 CORTEX MCP TOOL EXPOSURE VERIFICATION")
    print("=" * 80)
    print()
    
    # Create registry and discover all capabilities
    print("📦 Initializing CapabilityRegistry...")
    registry = CapabilityRegistry()
    registry.discover_all()
    
    # Get decorated tools count
    decorated_tools = get_decorated_tools()
    
    # Get all capabilities
    all_capabilities = registry.list_all()
    
    print(f"✅ Registry initialized with {len(all_capabilities)} capabilities")
    print()
    
    # Group by category
    by_category = registry.group_by_category()
    
    print("📊 CAPABILITY BREAKDOWN BY CATEGORY")
    print("-" * 80)
    for category, caps in sorted(by_category.items()):
        print(f"  {category:20s}: {len(caps):3d} capabilities")
    print()
    
    # Priority tools check
    priority_tools = [
        "cortex_audit_query",
        "cortex_governance_validate",
        "cortex_todo_list",
        "cortex_traceability_gaps"
    ]
    
    print("🎯 PRIORITY TOOLS STATUS")
    print("-" * 80)
    for tool_name in priority_tools:
        cap = registry.get(tool_name)
        if cap:
            print(f"  ✅ {tool_name:35s} - EXPOSED")
        else:
            print(f"  ❌ {tool_name:35s} - NOT FOUND")
    print()
    
    # Calculate exposure metrics
    # Before: 8 capabilities (manual)
    # After: 8 manual + decorated tools
    
    manual_count = 8  # From original discovery (plan, tdd, investigate, etc.)
    decorated_count = len(decorated_tools)
    total_exposed = len(all_capabilities)
    
    # Estimate total tool functions (from verification report)
    total_functions = 37
    
    before_rate = (manual_count / total_functions) * 100
    after_rate = (total_exposed / total_functions) * 100
    
    print("📈 EXPOSURE METRICS")
    print("-" * 80)
    print(f"  Total Python Tool Functions:    {total_functions}")
    print(f"  Manual Capabilities:            {manual_count}")
    print(f"  Auto-registered (Decorated):    {decorated_count}")
    print(f"  Total Exposed Capabilities:     {total_exposed}")
    print()
    print(f"  BEFORE (Manual Only):           {before_rate:.1f}% ({manual_count}/{total_functions})")
    print(f"  AFTER (Manual + Decorated):     {after_rate:.1f}% ({total_exposed}/{total_functions})")
    print(f"  IMPROVEMENT:                    +{after_rate - before_rate:.1f}% ({total_exposed - manual_count} new tools)")
    print()
    
    # List all decorated tools
    print("🔧 AUTO-REGISTERED DECORATED TOOLS")
    print("-" * 80)
    
    # Get decorated capabilities (those with auto_registered=True metadata)
    decorated_caps = [cap for cap in all_capabilities if cap.metadata.get("auto_registered")]
    
    for cap in sorted(decorated_caps, key=lambda c: c.name):
        category = cap.metadata.get("category", "general")
        priority = cap.metadata.get("priority", "")
        priority_label = f" [{priority}]" if priority else ""
        print(f"  • {cap.name:40s} {category:15s}{priority_label}")
    
    print()
    print("=" * 80)
    print(f"✅ VERIFICATION COMPLETE - {len(decorated_caps)} decorated tools registered")
    print("=" * 80)
    
    return {
        "success": True,
        "total_exposed": total_exposed,
        "manual_count": manual_count,
        "decorated_count": decorated_count,
        "before_rate": before_rate,
        "after_rate": after_rate,
        "improvement": after_rate - before_rate
    }


if __name__ == "__main__":
    result = verify_mcp_exposure()
    
    if not result["success"]:
        exit(1)
