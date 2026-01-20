# Quick Start Guide

**Last Updated:** 2026-01-20  
**Audience:** Developers  
**Prerequisites:** [Installation](0-installation.md)  
**Time Required:** 15 minutes

## Overview

This quick start guide walks you through your first interaction with CORTEX, demonstrating key capabilities including orchestrator execution, domain knowledge queries, and governance validation.

## Step 1: Verify Installation

Ensure CORTEX is properly installed:

```bash
# Activate virtual environment
source .venv/bin/activate

# Check system health
python -m cortex.cli system health
```

Expected output:
```
CORTEX System Health
────────────────────
✅ Governance DB: connected (5040 entries)
✅ Domain Brain: operational
✅ MCP Server: ready
✅ Orchestrator Registry: 15 orchestrators
Overall: HEALTHY ✅
```

## Step 2: List Available Orchestrators

Discover what orchestrators are available:

```bash
python -m cortex.cli orchestrator list
```

Output:
```
┌─────────────────────────┬───────────┬─────────┬────────────────────────────────┐
│ Name                    │ Domain    │ Status  │ Description                    │
├─────────────────────────┼───────────┼─────────┼────────────────────────────────┤
│ onboarding              │ planning  │ active  │ User onboarding workflow       │
│ complexity_assessment   │ analysis  │ active  │ Assess operation complexity    │
│ gap_detection           │ analysis  │ active  │ Detect implementation gaps     │
│ bkio                    │ integrat. │ active  │ Business knowledge ingestion   │
│ challenge_integration   │ planning  │ active  │ Challenge workflow integration │
└─────────────────────────┴───────────┴─────────┴────────────────────────────────┘
```

## Step 3: Execute Your First Orchestrator

Run the complexity assessment orchestrator:

```bash
python -m cortex.cli orchestrator execute complexity_assessment \
  --context '{"operation": "add_new_feature", "files_affected": 3}'
```

Output:
```
Executing orchestrator: complexity_assessment
─────────────────────────────────────────────

Context:
  Operation: add_new_feature
  Files Affected: 3

Assessment Result:
  Complexity Score: 0.28 (SIMPLE)
  Approval: AUTO-APPROVED
  
Factors:
  • LENS Confidence: 0.85 (high)
  • Dependency Depth: 2 (low)
  • Operation Scope: local

Recommendation: Proceed with implementation.

Audit Trail:
  AC-ID: AC-COMPLEX-001
  Duration: 1.2s
  Status: ✅ COMPLETE
```

## Step 4: Query Domain Knowledge

Query the Domain Brain for governance rules:

```bash
python -m cortex.cli knowledge query \
  --domain governance \
  --keywords "TDD,testing" \
  --max-results 3
```

Output:
```
Knowledge Query Results
───────────────────────

Found 3 results in 45ms:

1. CORE-008 (Rule)
   Domain: governance
   Content: TDD methodology required - tests must be written before implementation
   Severity: CRITICAL

2. CORE-011 (Rule)
   Domain: governance
   Content: Type hints mandatory on all function signatures
   Severity: HIGH

3. Test Coverage (Standard)
   Domain: governance
   Content: Minimum 85% code coverage required for locked phases
   Severity: MEDIUM
```

## Step 5: Validate Governance Compliance

Check a file against governance rules:

```bash
python -m cortex.cli governance validate src/mcp/server_sdk.py
```

Output:
```
Governance Validation: src/mcp/server_sdk.py
────────────────────────────────────────────

✅ CORE-008 (TDD): Test file exists
✅ CORE-011 (Type Hints): All functions typed
✅ CORE-012 (Docstrings): Google-style docstrings present
✅ CORE-013 (Exceptions): No bare except clauses
✅ CORE-028 (Naming): File name within 25 chars

Summary: 5 passed, 0 warnings, 0 failed
Status: COMPLIANT ✅
```

## Step 6: Check Audit Trail

View recent audit entries:

```bash
python -m cortex.cli governance audit --start-date 2026-01-20 --verify-chain
```

Output:
```
Audit Trail Query
─────────────────

Hash Chain: ✅ VERIFIED (unbroken)

Recent Entries (last 24h):
┌─────────┬──────────────────┬─────────────┬──────────────────────┐
│ ID      │ AC-ID            │ Operation   │ Timestamp            │
├─────────┼──────────────────┼─────────────┼──────────────────────┤
│ 7834    │ AC-COMPLEX-001   │ AC_COMPLETE │ 2026-01-20T10:05:01Z │
│ 7833    │ AC-COMPLEX-001   │ AC_EXECUTE  │ 2026-01-20T10:05:00Z │
│ 7832    │ AC-COMPLEX-001   │ AC_START    │ 2026-01-20T10:05:00Z │
└─────────┴──────────────────┴─────────────┴──────────────────────┘

Total entries: 5040
Chain integrity: VERIFIED ✅
```

## Step 7: Start MCP Server (Optional)

If you want to use CORTEX with Claude Desktop or VS Code:

```bash
# Start MCP server
python -m src.mcp
```

The server runs on stdio, ready for MCP client connections.

## What You've Learned

In this quick start, you've:

| Step | Capability | Component |
|------|------------|-----------|
| 1 | System health monitoring | CLI |
| 2 | Orchestrator discovery | Orchestrator Registry |
| 3 | Orchestrator execution | Complexity Assessment |
| 4 | Knowledge queries | Domain Brain |
| 5 | Governance validation | Governance Framework |
| 6 | Audit trail verification | Audit Logger |
| 7 | MCP server operation | MCP Protocol |

## Key Concepts Introduced

### Orchestrators
Business process automation units that execute domain-specific logic with built-in governance and resilience.

### Domain Brain
Centralized knowledge management system that stores and retrieves business rules, domain facts, and relationships.

### Governance Framework
Multi-tier rule system (Tier 0-3) that enforces compliance, security, and quality standards.

### Audit Trail
Tamper-evident logging system with hash chain integrity for full traceability.

### Complexity Assessment
Intelligent evaluation of operation complexity to determine approval requirements.

## Next Steps

Now that you've completed the quick start:

1. **[First Orchestrator](2-first-orchestrator.md)** - Build a custom orchestrator
2. **[System Overview](../02-architecture/1-system-overview.md)** - Understand the full architecture
3. **[MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md)** - Integrate with AI clients
4. **[Domain Brain](../02-architecture/4-domain-brain.md)** - Learn knowledge management

## Troubleshooting

### Orchestrator Not Found

```
Error: Orchestrator 'unknown' not found
```

**Solution:** Use `cortex orchestrator list` to see available orchestrators.

### Knowledge Query Returns Empty

```
Found 0 results
```

**Solution:** Check domain spelling and try broader keywords.

### Governance Validation Fails

```
❌ CORE-008 (TDD): No test file found
```

**Solution:** Create a test file in `tests/` matching the source file pattern.

## Related Documentation

- [First Orchestrator](2-first-orchestrator.md) - Create custom orchestrator
- [CLI Reference](../03-api-reference/cli/0-guide.md) - Full CLI documentation
- [Troubleshooting](../04-guides/operations/4-troubleshooting.md) - Common issues
