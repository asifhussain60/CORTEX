# TRACK:EVAL EXECUTION CARD
**One-page reference | 2026-01-22 | Ready to execute**

---

## THE REQUEST (Copy-Paste)

```
python /Users/asifhussain/PROJECTS/CORTEX/scripts/execute-track-eval-silent.py
```

---

## WHAT YOU GET

| Metric | Value |
|--------|-------|
| **Time** | 10-15 min |
| **Phases** | 8 (1 blocking) |
| **Output** | stderr: summary, stdout: JSON |
| **Result** | eval-results.json |
| **Exit Code** | 0=pass, 1=fail |

---

## PHASES EXECUTED

1. ✓ Test collection verification
2. ⚠ PHASE-E implementation quality (BLOCKS IF <90%)
3. ✓ Import migration audit
4. ✓ Governance compliance
5. ✓ Roadmap cleanup
6. ✓ Git checkpoint verification
7. ✓ Docstring compliance
8. ✓ Coverage baseline

---

## IF IT FAILS

**PHASE-AUDIT-002 blocks?** → Needs 7-14 days remediation  
See: `docs/EVAL-TRACK-REMEDIATION-PLAN-20260122.md`

**Other phase warns?** → Non-blocking, proceed if needed

---

## AFTER COMPLETION

```bash
# Check results
jq '.phases[] | "\(.phase): \(.status)"' eval-results.json

# If all pass: commit
git add eval-results.json
git commit -m "EVAL-TRACK: 8/8 phases passed"

# Proceed to Knowledge Graph track
```

---

## EFFICIENCY TIPS

- **Silent + JSON:** Both outputs at once (stderr + stdout)
- **No duplicate output:** Phase results logged, not repeated
- **Programmatic:** JSON format for downstream processing
- **Fail-fast:** Stops on blocking phase if fails

---

**Ready? Run it now.**
