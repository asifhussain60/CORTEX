#!/usr/bin/env python3
"""
CORTEX 6.0 - Audit Log Aggregator
Aggregates JSONL audit logs into a single JSON file for dashboard consumption
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

def aggregate_audit_logs(
    audit_logs_dir: Path,
    output_file: Path,
    days_back: int = 7,
    max_entries: int = 200
) -> Dict[str, Any]:
    """
    Aggregate audit logs from JSONL files into a single JSON file.
    
    Args:
        audit_logs_dir: Directory containing JSONL audit log files
        output_file: Path to write aggregated JSON file
        days_back: Number of days to look back for logs
        max_entries: Maximum number of entries to include
    
    Returns:
        Dictionary with aggregation statistics
    """
    all_entries = []
    files_processed = 0
    files_failed = 0
    
    # Get list of log files from last N days
    log_files = sorted(audit_logs_dir.glob("*.jsonl"), reverse=True)
    
    print(f"Found {len(log_files)} JSONL files in {audit_logs_dir}")
    
    # Process each file
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            all_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
            
            files_processed += 1
            
            # Stop if we have enough entries
            if len(all_entries) >= max_entries * 2:
                break
                
        except Exception as e:
            files_failed += 1
            print(f"  Failed to process {log_file.name}: {e}")
    
    # Sort by timestamp (most recent first)
    all_entries.sort(
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    # Keep only the most recent entries
    all_entries = all_entries[:max_entries]
    
    # Create aggregated data structure
    aggregated_data = {
        'generated_at': datetime.now().isoformat(),
        'total_entries': len(all_entries),
        'files_processed': files_processed,
        'files_failed': files_failed,
        'entries': all_entries
    }
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aggregated_data, f, indent=2)
    
    print(f"\n✅ Aggregated {len(all_entries)} audit entries")
    print(f"   Files processed: {files_processed}")
    print(f"   Files failed: {files_failed}")
    print(f"   Output: {output_file}")
    
    return aggregated_data


def main():
    """Main entry point"""
    # Paths
    workspace_root = Path(__file__).parent.parent
    audit_logs_dir = workspace_root / "cortex-brain" / "audit-logs"
    output_file = workspace_root / "templates" / "plan-viewer" / "audit-logs-aggregated.json"
    
    print("CORTEX 6.0 - Audit Log Aggregator")
    print("=" * 50)
    
    if not audit_logs_dir.exists():
        print(f"❌ Audit logs directory not found: {audit_logs_dir}")
        return 1
    
    # Aggregate logs
    result = aggregate_audit_logs(
        audit_logs_dir=audit_logs_dir,
        output_file=output_file,
        days_back=7,
        max_entries=200
    )
    
    print("\n" + "=" * 50)
    print("Aggregation complete!")
    print(f"Dashboard can now load: audit-logs-aggregated.json")
    
    return 0


if __name__ == "__main__":
    exit(main())
