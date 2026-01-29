#!/usr/bin/env python3
"""
Phase 8.2: Update EventRegistry and DomainPluginRegistry Imports
"""

from pathlib import Path

updates = {
    "EventRegistry": {
        "from": "from cortex.brain.core.orchestrator.terminal_events import",
        "to": "from cortex.core.orchestrator.terminal_events import",
        "files": [
            "tests/unit/core/orchestrator/test_master_orchestrator.py",
        ]
    },
    "DomainPluginRegistry": {
        "from": "from cortex.brain.domain_orchestrators.business.plugins import",
        "to": "from cortex.domain_orchestrators.business.plugins import",
        "files": [
            "cortex/domain_orchestrators/business/__init__.py",
            "tests/unit/domain_orchestrators/test_domain_plugins_context.py",
        ]
    }
}

repo_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
updated = 0
failed = []

print("=" * 80)
print("PHASE 8.2: Updating EventRegistry & DomainPluginRegistry Imports")
print("=" * 80)
print()

for registry_name, config in updates.items():
    print(f"\n📦 {registry_name}")
    print("-" * 40)
    
    for file_path in config["files"]:
        full_path = repo_root / file_path
        
        if not full_path.exists():
            print(f"  ❌ NOT FOUND: {file_path}")
            failed.append(file_path)
            continue
        
        try:
            content = full_path.read_text()
            original = content
            
            # Replace import statement
            content = content.replace(config["from"], config["to"])
            
            if content != original:
                full_path.write_text(content)
                print(f"  ✅ UPDATED: {file_path}")
                updated += 1
            else:
                print(f"  ⚠️  NO CHANGES: {file_path}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {file_path} - {e}")
            failed.append(file_path)

print()
print("=" * 80)
print(f"RESULTS: {updated}/3 files updated")
if failed:
    print(f"FAILED: {len(failed)} files")
else:
    print("✅ ALL FILES UPDATED SUCCESSFULLY")
print("=" * 80)
