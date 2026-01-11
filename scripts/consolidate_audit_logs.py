#!/usr/bin/env python3
"""
Consolidate Audit Logs Script
Merges all JSONL audit log files into a single consolidated JSON file
for consumption by the plan-viewer audit log viewer.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def consolidate_audit_logs():
    """Consolidate all JSONL audit logs into a single JSON file."""
    
    # Paths
    workspace_root = Path(__file__).parent.parent
    audit_logs_dir = workspace_root / "cortex-brain" / "audit-logs"
    output_file = audit_logs_dir / "consolidated-audit.json"
    
    print(f"📂 Scanning audit logs directory: {audit_logs_dir}")
    
    # Collect all JSONL files
    jsonl_files = sorted(audit_logs_dir.glob("*.jsonl"))
    
    if not jsonl_files:
        print("⚠️  No JSONL files found")
        return
    
    print(f"📋 Found {len(jsonl_files)} JSONL files")
    
    # Collect all log entries
    all_logs = []
    
    for jsonl_file in jsonl_files:
        print(f"   Reading: {jsonl_file.name}")
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        log_entry = json.loads(line)
                        all_logs.append(log_entry)
                    except json.JSONDecodeError as e:
                        print(f"      ⚠️  Skipping invalid JSON at line {line_num}: {e}")
                        continue
        
        except Exception as e:
            print(f"      ❌ Error reading {jsonl_file.name}: {e}")
            continue
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Write consolidated file
    print(f"\n💾 Writing consolidated file with {len(all_logs)} entries...")
    
    consolidated_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_entries": len(all_logs),
            "source_files": [f.name for f in jsonl_files],
            "format_version": "1.0"
        },
        "logs": all_logs
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2)
    
    # File size
    file_size = output_file.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Consolidated {len(all_logs)} audit log entries")
    print(f"📄 Output: {output_file}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"\n🌐 Reload plan-viewer.html to see real audit data!")

if __name__ == "__main__":
    consolidate_audit_logs()
