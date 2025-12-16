================================================================================
CORTEX Batch Path Hardening Report
================================================================================
Mode: APPLIED
Timestamp: 2025-12-16 16:32:22

📊 Summary:
  Total files scanned: 2
  Files processed: 2
  Replacements made: 3
  Errors: 0
  Skipped: 0

🔧 Replacements:

  src\context\context_resolver.py:
    Line 129:
      OLD: cortex_from_module = Path(__file__).parent.parent.parent  # ...
      NEW:         cortex_from_module = get_root_path()  # src/context ...
    Line 158:
      OLD: cortex_root = Path(__file__).parent.parent.parent...
      NEW:             cortex_root = get_root_path()...

  src\context\examples\sample_operation.py:
    Line 13:
      OLD: sys.path.insert(0, str(Path(__file__).parent.parent.parent))...
      NEW: sys.path.insert(0, str(get_root_path()))...

================================================================================