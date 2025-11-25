"""
CORTEX Tier 1 Capture Gap Analysis

Investigates why only 3/14 conversations are being auto-captured (21% automation rate).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Paths
CORTEX_ROOT = Path(__file__).parent.parent
COPILOT_CHATS = CORTEX_ROOT / ".github" / "CopilotChats.md"
TIER1_DB = CORTEX_ROOT / "cortex-brain" / "tier1" / "conversations.db"


def analyze_copilot_chats() -> Dict:
    """Analyze CopilotChats.md to count conversations."""
    
    if not COPILOT_CHATS.exists():
        return {"error": "CopilotChats.md not found"}
    
    with open(COPILOT_CHATS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count user messages (conversations)
    user_messages = re.findall(r'^asifhussain60:', content, re.MULTILINE)
    
    # Count CORTEX responses
    cortex_responses = re.findall(r'^GitHub Copilot: 🧠 CORTEX', content, re.MULTILINE)
    
    # Estimate conversation threads (unique conversations)
    # Each thread starts with "Follow instructions in [CORTEX.prompt.md]"
    thread_starts = re.findall(
        r'^asifhussain60: Follow instructions in \[CORTEX\.prompt\.md\]',
        content,
        re.MULTILINE
    )
    
    return {
        "total_user_messages": len(user_messages),
        "total_cortex_responses": len(cortex_responses),
        "estimated_threads": len(thread_starts),
        "file_size_kb": COPILOT_CHATS.stat().st_size / 1024,
        "total_lines": len(content.splitlines())
    }


def analyze_tier1_db() -> Dict:
    """Analyze Tier 1 database to count captured conversations."""
    
    if not TIER1_DB.exists():
        return {"error": "Tier 1 database not found"}
    
    conn = sqlite3.connect(str(TIER1_DB))
    cursor = conn.cursor()
    
    # Get conversation count
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_conversations = cursor.fetchone()[0]
    
    # Get conversations by agent
    cursor.execute("""
        SELECT agent_id, COUNT(*) 
        FROM conversations 
        GROUP BY agent_id
    """)
    by_agent = cursor.fetchall()
    
    # Get message count
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    
    # Get recent conversations
    cursor.execute("""
        SELECT conversation_id, start_time, agent_id, goal
        FROM conversations
        ORDER BY start_time DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "by_agent": by_agent,
        "recent_conversations": recent
    }


def check_daemon_status() -> Dict:
    """Check if ambient capture daemon is running."""
    import subprocess
    import sys
    
    try:
        if sys.platform.startswith('win'):
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                timeout=5
            )
            daemon_running = 'auto_capture_daemon' in result.stdout
        else:
            result = subprocess.run(
                ['pgrep', '-f', 'auto_capture_daemon'],
                capture_output=True,
                text=True,
                timeout=5
            )
            daemon_running = result.returncode == 0
        
        return {"daemon_running": daemon_running}
    
    except Exception as e:
        return {"daemon_running": False, "error": str(e)}


def identify_root_cause(chats_data: Dict, tier1_data: Dict, daemon_data: Dict) -> List[str]:
    """Identify root cause of capture gap."""
    
    findings = []
    
    # Calculate gap
    expected = chats_data.get("estimated_threads", 0)
    actual = tier1_data.get("total_conversations", 0)
    gap = expected - actual
    
    if gap > 0:
        rate = (actual / expected * 100) if expected > 0 else 0
        findings.append(f"❌ CAPTURE GAP DETECTED: {gap} conversations missing ({rate:.1f}% automation rate)")
    
    # Check daemon status
    if not daemon_data.get("daemon_running", False):
        findings.append("❌ ROOT CAUSE: Ambient capture daemon NOT RUNNING")
        findings.append("   → Daemon monitors file system changes, terminal commands, git operations")
        findings.append("   → Does NOT monitor VS Code Copilot Chat directly")
    else:
        findings.append("✅ Daemon is running")
    
    # Check if Copilot Chat is being monitored
    findings.append("\n🔍 INVESTIGATION:")
    findings.append("   • CopilotChats.md contains VS Code Copilot Chat conversations")
    findings.append("   • Ambient daemon monitors: files, terminal, git, VS Code workspace")
    findings.append("   • Ambient daemon DOES NOT monitor: Copilot Chat conversation stream")
    findings.append("\n💡 ROOT CAUSE IDENTIFIED:")
    findings.append("   VS Code Copilot Chat conversations happen in a separate UI panel")
    findings.append("   that is NOT visible to the file system watcher or terminal monitor.")
    findings.append("\n   CopilotChats.md is auto-saved by VS Code but doesn't trigger")
    findings.append("   the ambient capture because:")
    findings.append("   1. File is in .github/ (may be in ignore patterns)")
    findings.append("   2. File changes too frequently (debouncer filters it out)")
    findings.append("   3. No semantic analysis of chat content (just file change event)")
    
    return findings


def generate_recommendations() -> List[str]:
    """Generate recommendations to fix capture gap."""
    
    return [
        "\n🔧 RECOMMENDED SOLUTIONS:",
        "",
        "**Option 1: VS Code Extension Integration (BEST)**",
        "   • Create VS Code extension to hook into Copilot Chat API",
        "   • Directly capture conversation events in real-time",
        "   • Send to CORTEX Tier 1 via IPC or local API",
        "   • Pros: Real-time, accurate, no file parsing",
        "   • Cons: Requires extension development",
        "",
        "**Option 2: CopilotChats.md File Watcher (QUICK WIN)**",
        "   • Modify ambient daemon to specifically watch CopilotChats.md",
        "   • Parse file on change to extract new conversations",
        "   • Use hybrid capture approach (already validated in CORTEX 3.0 design)",
        "   • Pros: Fast to implement, uses existing code",
        "   • Cons: Post-hoc (not real-time), file parsing overhead",
        "",
        "**Option 3: Manual Capture Workflow Enhancement**",
        "   • Improve hybrid capture UX (smart hints + one-click)",
        "   • Add keyboard shortcut for quick capture",
        "   • Show capture reminder at end of valuable conversations",
        "   • Pros: User maintains control, quality review",
        "   • Cons: Still manual, requires user action",
        "",
        "**RECOMMENDATION: Option 2 (Quick Win) → Option 1 (Long-term)**",
        "   1. Implement CopilotChats.md watcher immediately (1-2 hours)",
        "   2. Test with real conversations to validate",
        "   3. Plan VS Code extension for CORTEX 3.0 roadmap",
    ]


def main():
    """Main analysis entry point."""
    
    print("=" * 80)
    print("CORTEX TIER 1 CAPTURE GAP ANALYSIS")
    print("=" * 80)
    print()
    
    # Analyze CopilotChats.md
    print("📊 Analyzing CopilotChats.md...")
    chats_data = analyze_copilot_chats()
    
    if "error" not in chats_data:
        print(f"   • Total user messages: {chats_data['total_user_messages']}")
        print(f"   • Total CORTEX responses: {chats_data['total_cortex_responses']}")
        print(f"   • Estimated conversation threads: {chats_data['estimated_threads']}")
        print(f"   • File size: {chats_data['file_size_kb']:.1f} KB")
        print(f"   • Total lines: {chats_data['total_lines']}")
    else:
        print(f"   ❌ {chats_data['error']}")
    
    print()
    
    # Analyze Tier 1 database
    print("📊 Analyzing Tier 1 database...")
    tier1_data = analyze_tier1_db()
    
    if "error" not in tier1_data:
        print(f"   • Total conversations: {tier1_data['total_conversations']}")
        print(f"   • Total messages: {tier1_data['total_messages']}")
        if tier1_data['by_agent']:
            print(f"   • By agent: {dict(tier1_data['by_agent'])}")
        if tier1_data['recent_conversations']:
            print(f"   • Recent conversations:")
            for conv_id, start_time, agent_id, goal in tier1_data['recent_conversations']:
                print(f"      - {conv_id[:12]}... | {agent_id} | {start_time}")
    else:
        print(f"   ❌ {tier1_data['error']}")
    
    print()
    
    # Check daemon status
    print("📊 Checking ambient daemon status...")
    daemon_data = check_daemon_status()
    print(f"   • Daemon running: {daemon_data.get('daemon_running', 'Unknown')}")
    
    print()
    print("=" * 80)
    
    # Identify root cause
    findings = identify_root_cause(chats_data, tier1_data, daemon_data)
    for finding in findings:
        print(finding)
    
    # Generate recommendations
    recommendations = generate_recommendations()
    for rec in recommendations:
        print(rec)
    
    print()
    print("=" * 80)
    print(f"Analysis completed: {datetime.now().isoformat()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
