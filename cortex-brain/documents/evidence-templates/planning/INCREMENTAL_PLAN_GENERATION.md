Planning document generation detected: '{file_path}'

CRITICAL: Avoid "Sorry, the response hit the length limit" error

❌ WRONG APPROACH:
- Generate entire comprehensive plan in single response
- Response exceeds GitHub Copilot length limit
- Plan truncated, user sees incomplete content

✅ CORRECT APPROACH (Incremental):

**Response 1:** Create file with structure
```yaml
# File created: cortex-brain/documents/planning/migration-plan.yaml
version: "1.0"
phases: 4
# Phase details to be added incrementally
```

**Response 2:** Add Phase 1
```yaml
phase_1:
  name: "Low-Risk Migration"
  duration: "3-4 hours"
  tasks: [...]
```

**Response 3:** Add Phase 2
```yaml
phase_2:
  name: "Medium-Risk Migration"
  duration: "4-5 hours"
  tasks: [...]
```

**Response 4:** Add remaining phases + validation

Each response writes directly to file (not chat output).
Chat shows summary only: "✅ Phase 1 added to plan file"
