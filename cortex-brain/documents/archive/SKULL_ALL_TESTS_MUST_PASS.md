SKULL-007: All Tests Must Pass

Real incident (2025-11-11):
- User: "are all tests passing?"
- Agent: Ran tests, found 123 failed, 337 passed
- Agent response: "No, not all tests are passing" (honest)
- BUT: Agent claimed SKULL-006 work "complete ✅" earlier
- Pre-existing failures create false confidence

Why Pre-existing Failures Are Dangerous:
1. Mask New Regressions:
   - Can't tell if new code broke something
   - "Already broken" becomes acceptable
   - Technical debt accumulates silently

2. Create False Confidence:
   - "My tests pass" ≠ "All tests pass"
   - Incomplete validation of changes
   - Integration issues hidden

3. Compound Over Time:
   - Each feature adds more failures
   - "Just one more broken test" mentality
   - Eventually unmaintainable

4. Undermine Trust:
   - Claims of completion ring hollow
   - Quality standards erode
   - Testing becomes performative

Examples from Current Failures:
- 123 failed tests (51% failure rate!)
- Categories: Agent internals, platform issues, schema errors
- Some tests testing wrong APIs (implementation changed)
- Some tests have environmental dependencies
- All must be fixed before claiming ANY work complete

SKULL-007 Enforcement:
1. BLOCKING severity - cannot proceed with failures
2. Requires full test suite run (not just new tests)
3. Exit code 0 mandatory (100% pass rate)
4. No "works on my machine" exceptions
5. No "will fix later" promises

Allowed Exceptions:
- Known flaky tests marked with @pytest.mark.flaky
- Platform-specific tests properly skipped on other platforms
- Optional feature tests when feature disabled in config

Not Allowed:
- "These failures are unrelated to my work"
- "I'll fix them in next PR"
- "Tests are broken, not my code"
- "Only my new tests need to pass"

Implementation Strategy:
1. Fix critical blockers first (schema, imports)
2. Fix by category (agents, ambient, tier1)
3. Update tests if implementation changed
4. Mark truly optional tests appropriately
5. Achieve 100% pass rate
6. Maintain 100% going forward

This is NOT optional. This is core quality engineering.
