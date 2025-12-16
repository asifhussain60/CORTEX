================================================================================
CORTEX Batch Path Hardening Report
================================================================================
Mode: APPLIED
Timestamp: 2025-12-16 16:31:55

📊 Summary:
  Total files scanned: 1
  Files processed: 1
  Replacements made: 1
  Errors: 0
  Skipped: 0

🔧 Replacements:

  src\migrations\run_all_migrations.py:
    Line 52:
      OLD: default=Path(__file__).parent.parent.parent.parent / 'cortex...
      NEW:         default=get_root_path().parent / 'cortex-brain'...

================================================================================