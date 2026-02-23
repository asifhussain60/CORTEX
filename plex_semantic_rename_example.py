"""
Plex Semantic Rename — Usage Example

Demonstrates the new LLM-powered semantic renaming workflow for G:\FLICKS\Wicked.

This script showcases:
1. LLM semantic understanding ("Chad Alva does Jojo Kiss" → "Chad Does Jojo")
2. Duplicate detection and collision prevention
3. SQLite snapshot + rollback capability
4. Hybrid LLM/rule-based routing

**Two Modes:**
- **IN_CONTEXT (VS Code):** Uses current GitHub Copilot conversation (no API key needed)
- **STANDALONE (CLI):** Uses OpenAI/Anthropic API (requires API key)

Requirements for Standalone Mode:
    pip install openai  # or anthropic
    Set OPENAI_API_KEY environment variable

VS Code Mode (Recommended):
    Just run in Copilot Chat - it will prompt you inline for rename proposals
"""

import os
from cortex.mcp.tools.video_library_tool import cortex_plex_semantic_rename


def main_in_context():
    """
    Run semantic rename in VS Code with GitHub Copilot (IN_CONTEXT mode).
    
    This mode uses the current conversation context - no API keys needed!
    """
    print("=" * 80)
    print("PLEX SEMANTIC RENAME — IN_CONTEXT MODE (VS Code Copilot)")
    print("=" * 80)
    print()
    print("🤖 Using current GitHub Copilot conversation (no API key required)")
    print()
    
    # STEP 1: Preview with in-context LLM
    print("STEP 1: PREVIEW (DRY RUN)")
    print("-" * 80)
    
    result = cortex_plex_semantic_rename(
        root_path="G:\\FLICKS\\Wicked",
        use_llm=True,
        llm_provider="in_context",  # 🎯 Use VS Code Copilot conversation
        llm_api_key=None,  # Not needed for in-context mode
        min_confidence=0.85,
        enable_duplicate_detection=True,
        enable_snapshots=True,
        dry_run=True,
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📁 Total files: {result['total_files']}")
    print(f"📝 Rename proposals: {result['proposals_count']}")
    print(f"🤖 Mode: IN_CONTEXT (GitHub Copilot)")
    print(f"⏱️  Duration: {result['duration_seconds']}s")
    print()
    
    if result['errors']:
        print("❌ ERRORS:")
        for err in result['errors']:
            print(f"  - {err}")
        print()
    
    print("Workflow Steps:")
    for step in result['steps']:
        icon = "✅" if step['status'] == "success" else "❌"
        print(f"  {icon} {step['name']}: {step['status']} ({step['duration_ms']}ms)")
    print()
    
    # STEP 2: Apply changes
    user_input = input("Apply rename proposals? (yes/no): ")
    
    if user_input.lower() != "yes":
        print("❌ Cancelled by user.")
        return
    
    result_apply = cortex_plex_semantic_rename(
        root_path="G:\\FLICKS\\Wicked",
        use_llm=True,
        llm_provider="in_context",
        llm_api_key=None,
        min_confidence=0.85,
        enable_duplicate_detection=True,
        enable_snapshots=True,
        dry_run=False,  # APPLY CHANGES
    )
    
    print(f"✅ Success: {result_apply['success']}")
    print(f"📝 Files renamed: {result_apply['files_renamed']}")
    print(f"📸 Snapshot ID: {result_apply['snapshot_id']} (for rollback)")
    print()
    
    # STEP 3: Rollback instructions
    if result_apply['snapshot_id']:
        print("🔄 ROLLBACK INSTRUCTIONS:")
        print(f"   If you need to undo changes, run:")
        print(f"   >>> from cortex.tools.media.restore_manager import RestoreManager")
        print(f"   >>> from pathlib import Path")
        print(f"   >>> manager = RestoreManager(Path('.cortex-runtime/backups/plex-snapshots.db'))")
        print(f"   >>> manager.rollback(snapshot_id={result_apply['snapshot_id']})")
        print()


def main_standalone():
    """
    Run semantic rename with external API (STANDALONE mode).
    
    Requires OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set. Falling back to rule-based renaming.")
    
    print("=" * 80)
    print("PLEX SEMANTIC RENAME — STANDALONE MODE (External API)")
    print("=" * 80)
    print()
    
    result = cortex_plex_semantic_rename(
        root_path="G:\\FLICKS\\Wicked",
        use_llm=True if api_key else False,
        llm_provider="openai",  # or "anthropic"
        llm_api_key=api_key,
        min_confidence=0.85,
        enable_duplicate_detection=True,
        enable_snapshots=True,
        dry_run=True,
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📁 Total files: {result['total_files']}")
    print(f"📝 Rename proposals: {result['proposals_count']}")
    print(f"🤖 LLM used: {result['llm_used']}")
    print()


if __name__ == "__main__":
    # Detect environment
    if "VSCODE_PID" in os.environ or "TERM_PROGRAM" in os.environ:
        print("🎯 Detected VS Code environment — using IN_CONTEXT mode")
        main_in_context()
    else:
        print("🎯 Detected standalone environment — using EXTERNAL API mode")
        main_standalone()

