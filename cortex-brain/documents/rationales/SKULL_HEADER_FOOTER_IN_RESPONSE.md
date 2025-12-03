SKULL-007: Faculty Integrity Check

Real incident (2025-11-12):
- Exclusion-based publish script too aggressive
- Excluded 97.9% of files (good for privacy!)
- BUT also excluded essential faculties:
  ❌ All 10 specialist agents missing
  ❌ Tier 1 conversation_tracker.py missing
  ❌ Entry points (CORTEX.prompt.md) missing
  ❌ Plugin system missing
- Published CORTEX was incomplete and non-functional

Impact:
- Users copy broken CORTEX to their application
- CORTEX cannot coordinate work (no agents)
- CORTEX cannot remember (no Tier 1)
- Copilot cannot find CORTEX (no entry points)
- Result: Complete failure, wasted user time

SKULL-007 prevents this by:
1. Comprehensive test that verifies ALL faculties present
2. Blocking publish if any faculty missing
3. Listing exact files required for each faculty
4. Testing BEFORE deployment (not discovery by users)

The Brilliant Fix:
Instead of exclusion-based publish (exclude dev files),
switch to INCLUSION-based publish (include ONLY essentials):

Benefits:
- Simpler logic (copy what's needed vs exclude what's not)
- Guaranteed completeness (explicit list of essentials)
- No accidental omissions (inclusion list is exhaustive)
- Better maintainability (clear intent)

Implementation:
- Create test_publish_faculties.py with test_cortex_fully_operational()
- Test checks: Tier 0-3, Agents, Operations, Plugins, Entry Points, Docs
- Publish script copies ONLY essential directories
- Test runs BEFORE declaring publish complete

Result:
- Package size: 393 files, 3.8 MB (perfect!)
- All faculties present: ✅
- No privacy leaks: ✅  
- CORTEX fully operational: ✅
