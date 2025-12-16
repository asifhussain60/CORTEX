================================================================================
CORTEX Batch Path Hardening Report
================================================================================
Mode: APPLIED
Timestamp: 2025-12-16 16:28:08

📊 Summary:
  Total files scanned: 2
  Files processed: 2
  Replacements made: 2
  Errors: 0
  Skipped: 0

🔧 Replacements:

  src\epmo\documentation\cli.py:
    Line 22:
      OLD: sys.path.insert(0, str(Path(__file__).parent.parent.parent.p...
      NEW: sys.path.insert(0, str(get_root_path().parent))...

  src\epmo\documentation\image_prompt_bridge.py:
    Line 19:
      OLD: sys.path.append(str(Path(__file__).parent.parent.parent / 'e...
      NEW: sys.path.append(str(get_root_path() / 'epm' / 'modules'))...

================================================================================