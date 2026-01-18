═══════════════════════════════════════════════════════════════════════════════
                          PHASE-REMEDIATION-01 EXECUTION CHECKLIST
                        Ready for Implementation - January 16, 2026
═══════════════════════════════════════════════════════════════════════════════

PRE-EXECUTION VALIDATION:
═════════════════════════════════════════════════════════════════════════════

Phase Information:
  ☐ Read cortex-master.yaml → phase_tracker.PHASE-REMEDIATION-01
  ☐ Verify locked: false ✓
  ☐ Verify requires: PHASE-16-ORCHESTRATOR-CONTINUATION ✓
  ☐ Verify PHASE-16 locked: true ✓

Governance Compliance:
  ☐ Load cortex-brain/tier0/governance/core-rules.yaml (29 immutable rules)
  ☐ Load cortex-brain/tier0/governance/phase-enforcement-map.yaml
  ☐ Load cortex-brain/tier0/governance/ac-validation-checklist.yaml
  ☐ Verify enforcement_mode: STRICT ✓

Git Repository:
  ☐ Verify branch: CORTEX6 ✓
  ☐ Verify working tree: CLEAN ✓
  ☐ Verify no uncommitted changes ✓
  ☐ Pull latest from remote (if applicable)

═════════════════════════════════════════════════════════════════════════════

PHASE CHECKPOINT:
═════════════════════════════════════════════════════════════════════════════

Before starting any AC implementation:

  ☐ Create checkpoint: git commit -m "checkpoint: before PHASE-REMEDIATION-01"
  ☐ Record commit hash: ___________________________
  ☐ Tag checkpoint: git tag -a PHASE-REMEDIATION-01-START -m "Phase start"

═════════════════════════════════════════════════════════════════════════════

AC-ID EXECUTION SEQUENCE (11 Total):
═════════════════════════════════════════════════════════════════════════════

ISSUE-001: AST Scanning Integration (6 ACs, 18 hours)
─────────────────────────────────────────────────────

AC-REM-001-01: ASTIntelligenceEngine integrated (3h)
  ☐ Read specification in cortex-master.yaml (PHASE-REMEDIATION-01 section)
  ☐ Create failing test: tests/unit/orchestrators/test_ast_integration.py
    Test: test_ast_scanning_enabled_on_comprehension()
  ☐ Implement integration in src/orchestrators/domain/interaction_orchestrator.py
  ☐ Verify test passes (GREEN)
  ☐ Run full orchestrator test suite (regression check)
  ☐ Verify audit trail created (AC_START, AC_EXECUTE, AC_COMPLETE)
  ☐ Commit: git commit -m "AC-REM-001-01: AST scanning enabled - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-001-02: CallGraphBuilder integration (3h)
  ☐ Create test: test_call_graph_built_for_comprehension()
  ☐ Implement CallGraphBuilder usage in comprehension phase
  ☐ Verify Call Graph traces 3+ layer transitions
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-001-02: CallGraph builder integrated - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-001-03: DependencyMapper creation (2h)
  ☐ Create test: test_dependency_map_generated()
  ☐ Implement DependencyMapper in src/core/analysis/
  ☐ Verify identifies 3+ levels of transitive dependencies
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-001-03: DependencyMapper created - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-001-04: PatternDetector integration (2h)
  ☐ Create test: test_pattern_detection_in_comprehension()
  ☐ Implement PatternDetector usage in comprehension phase
  ☐ Verify detects ≥1 patterns or reports 'none found'
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-001-04: PatternDetector integrated - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-001-05: Holistic context YAML generation (3h)
  ☐ Create test: test_comprehension_approval_gate()
  ☐ Implement YAML generation: {parsed_files, call_graphs, dependencies, patterns, impact_map}
  ☐ Verify YAML structure complete and valid
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-001-05: Comprehension approval YAML - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-001-06: Intent Router continuous execution (2h)
  ☐ Create test: test_intent_router_continuous_execution()
  ☐ Implement continuous execution check (LENS runs on EVERY request)
  ☐ Verify 4+ sequential requests show comprehension loop on each turn
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-001-06: Intent Router continuous - tests passing"
  ☐ Record commit hash: ___________________________


ISSUE-003: Response Verbosity & Header Injection (3 ACs, 7 hours)
─────────────────────────────────────────────────────────────────

AC-REM-003-01: Copilot verbosity enforcement (2h)
  ☐ Create test: test_copilot_verbosity_enforcement()
  ☐ Update .github/copilot-instruction.md system prompt
  ☐ Add enforcements: <500 words, no 'Let me' phrases, direct communication
  ☐ Verify 10 sample responses average <500 words
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-003-01: Copilot verbosity enforced - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-003-02: Chat header injection wrapper (4h)
  ☐ Create test: test_chat_header_injection_wrapper()
  ☐ Implement ChatResponseFormatter class in src/
  ☐ Verify all responses include headers (operation, orchestrator, phase, author)
  ☐ Verify JSON responses remain parseable
  ☐ Verify test passes (16+ unit tests)
  ☐ Commit: git commit -m "AC-REM-003-02: Chat header wrapper - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-003-03: Copyright notice in responses (1h)
  ☐ Create test: test_copyright_in_chat_responses()
  ☐ Implement copyright footer: "Copyright © 2025-2026 Asif Hussain"
  ☐ Verify appears in all responses
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-003-03: Copyright notices - tests passing"
  ☐ Record commit hash: ___________________________


ISSUE-004: Code Quality - Bare Except & Hardcoded Paths (2 ACs, 6 hours)
─────────────────────────────────────────────────────────────────────────

AC-REM-004-01: Replace bare except clauses (3h)
  ☐ Create test: test_no_bare_except_clauses()
  ☐ Find all bare except: grep -rn "except:" src/
  ☐ Replace each with specific exception types
  ☐ Run CORE-013 compliance check
  ☐ Verify grep returns 0 matches
  ☐ Verify test passes
  ☐ Commit: git commit -m "AC-REM-004-01: Bare except replaced - tests passing"
  ☐ Record commit hash: ___________________________

AC-REM-004-02: Replace hardcoded paths (3h)
  ☐ Create test: test_no_hardcoded_paths()
  ☐ Find all /Users paths: grep -rn "/Users/" tests/
  ☐ Replace each with Path(__file__).parent patterns
  ☐ Run CORE-028 compliance check (pre-commit hook)
  ☐ Verify grep returns 0 matches
  ☐ Verify test passes (reference: PHASE-12 fix 54fe9ad91)
  ☐ Commit: git commit -m "AC-REM-004-02: Hardcoded paths removed - tests passing"
  ☐ Record commit hash: ___________________________


═════════════════════════════════════════════════════════════════════════════

PHASE COMPLETION VERIFICATION:
═════════════════════════════════════════════════════════════════════════════

After all 11 ACs complete:

Test Verification:
  ☐ Run: pytest tests/unit/orchestrators/ -v
  ☐ Run: pytest tests/integration/ -v
  ☐ Verify: All tests PASSING
  ☐ Verify: Coverage >95% for modified classes
  ☐ Record test results: ___________________________

Audit Trail Verification:
  ☐ Query: SELECT ac_id, COUNT(*) FROM audit_log WHERE ac_id LIKE 'AC-REM%'
  ☐ Verify: 11 AC-IDs present
  ☐ Verify: Each AC-ID has ≥3 entries (START, EXECUTE, COMPLETE)
  ☐ Verify: Minimum 33 entries total
  ☐ Verify: Hash chain integrity (no gaps)
  ☐ Record audit entry count: ___________________________

Governance Compliance:
  ☐ Verify: CORE-008 satisfied (TDD pattern followed)
  ☐ Verify: CORE-011 satisfied (Type hints mandatory)
  ☐ Verify: CORE-012 satisfied (Docstrings present)
  ☐ Verify: CORE-013 satisfied (No bare except)
  ☐ Verify: CORE-026 satisfied (Checkpoints created)
  ☐ Verify: CORE-027 satisfied (Audit trail complete)
  ☐ Verify: CORE-028 satisfied (Kebab-case naming)

Cleanup Protocol (REQUIRED):
  ☐ Delete any temporary .md files in root
  ☐ Delete any temporary AC reports in root
  ☐ Move any summary docs to .github/roadmap/reports/
  ☐ Verify root contains ONLY: README.md, pytest.ini, requirements.txt
  ☐ Verify no uncommitted changes
  ☐ Create final checkpoint: git commit -m "PHASE-REMEDIATION-01: cleanup done"

Phase Completion:
  ☐ Update cortex-master.yaml:
     - phase_tracker.PHASE-REMEDIATION-01.status = "COMPLETED"
     - phase_tracker.PHASE-REMEDIATION-01.locked = true
     - phase_tracker.PHASE-REMEDIATION-01.completed_ac_ids = 11
     - phase_tracker.PHASE-REMEDIATION-01.audit_verification.verified = true
     - phase_tracker.PHASE-REMEDIATION-01.audit_verification.entry_count = N (actual count)
  ☐ Create phase completion commit:
     git commit -m "PHASE-REMEDIATION-01: COMPLETED - all 11 ACs verified"
  ☐ Tag completion: git tag -a PHASE-REMEDIATION-01-COMPLETE -m "Phase complete"

═════════════════════════════════════════════════════════════════════════════

PHASE READINESS SUMMARY:
═════════════════════════════════════════════════════════════════════════════

Ready for Implementation: ✅ YES
  • All prerequisites satisfied
  • Governance enforced
  • No blockers identified
  • 11 ACs fully specified
  • Test requirements clear

Starting Point: AC-REM-001-01 (AST Scanning Integration)
Estimated Completion: 4 days (32 hours)
Next Phase After: PHASE-REMEDIATION-02 (Per-Turn Governance Enforcement)

═════════════════════════════════════════════════════════════════════════════

QUICK REFERENCE: GOVERNANCE RULES TO FOLLOW
═════════════════════════════════════════════════════════════════════════════

CORE-008: Tests MUST exist BEFORE implementation (RED → GREEN)
  Pattern: Write test first, implement to pass, refactor

CORE-011: ALL functions MUST have type hints
  Example: def parse_file(self, path: str) -> ParseResult:

CORE-012: ALL public APIs MUST have docstrings (Google style)
  Format: """Brief description.
          
          Args:
              param: Description
          
          Returns:
              Description
          """

CORE-013: NO bare except, NO generic Exception
  Wrong: except:
  Wrong: except Exception:
  Right: except FileNotFoundError: / except KeyError:

CORE-026: Git checkpoint BEFORE every major action
  Pattern: git commit -m "checkpoint: before AC-<ID>"

CORE-027: AC_START, AC_EXECUTE, AC_COMPLETE audit entries
  Logged automatically when AC status changes

CORE-028: Kebab-case, ≤25 chars total
  Example: test_ast_scanning.py (19 chars) ✓
  Example: test_very_long_orchestrator_integration_system.py (51 chars) ✗

═════════════════════════════════════════════════════════════════════════════

EMERGENCY ROLLBACK:
═════════════════════════════════════════════════════════════════════════════

If issues arise during execution:

  1. Identify last good commit: git log --oneline -10
  2. Soft reset (keep changes): git reset --soft <commit-hash>
  3. Hard reset (discard): git reset --hard <commit-hash>
  4. Restore from stash: git stash pop
  5. Tag for reference: git tag -a <phase-name>-rollback

═════════════════════════════════════════════════════════════════════════════

SIGN-OFF:
═════════════════════════════════════════════════════════════════════════════

Execution Checklist Status: ✅ COMPLETE & READY
Date Prepared: January 16, 2026
Prepared By: GitHub Copilot (CORTEX Builder)
Governance Mode: STRICT (no overrides)
Next Action: Start AC-REM-001-01 implementation

═════════════════════════════════════════════════════════════════════════════
