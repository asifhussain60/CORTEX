================================================================================
CORTEX Batch Path Hardening Report
================================================================================
Mode: APPLIED
Timestamp: 2025-12-16 16:32:03

📊 Summary:
  Total files scanned: 1
  Files processed: 1
  Replacements made: 1
  Errors: 0
  Skipped: 0

🔧 Replacements:

  src\policy\policy_test_generator.py:
    Line 145:
      OLD: sys.path.insert(0, str(Path(__file__).parent.parent.parent))...
      NEW: sys.path.insert(0, str(get_root_path()))...

================================================================================