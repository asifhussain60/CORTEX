================================================================================
CORTEX Batch Path Hardening Report
================================================================================
Mode: DRY RUN (preview only)
Timestamp: 2025-12-16 16:06:41

📊 Summary:
  Total files scanned: 3
  Files processed: 3
  Replacements made: 4
  Errors: 0
  Skipped: 0

🔧 Replacements:

  src\tier1\conversation_memory.py:
    Line 33:
      OLD: project_root = Path(__file__).parent.parent.parent...
      NEW:             project_root = get_root_path()...

  src\tier1\migrate_tier1.py:
    Line 322:
      OLD: default=Path(__file__).parent.parent.parent.parent /...
      NEW:         default=get_root_path().parent / ...
    Line 329:
      OLD: default=Path(__file__).parent.parent.parent.parent /...
      NEW:         default=get_root_path().parent / ...

  src\tier1\planning_doc_sync.py:
    Line 48:
      OLD: project_root = Path(__file__).parent.parent.parent...
      NEW:             project_root = get_root_path()...

================================================================================