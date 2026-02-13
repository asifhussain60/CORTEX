# CLI Command Reference

**Last Updated:** 2026-01-20  
**Audience:** Developers, Operators  
**Prerequisites:** [Local Development Setup](../../04-guides/deployment/1-local-development.md)

## Overview

CORTEX provides a command-line interface for orchestrator execution, governance validation, and system management. The CLI integrates with the governance framework and maintains full audit trail compliance.

## Installation

The CLI is available after CORTEX installation:

```bash
# Verify installation
cortex --version

# Or run via Python module
python -m cortex.cli --version
```

## Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | Path to config file | `cortex-config.yaml` |
| `--verbose, -v` | Enable verbose output | `false` |
| `--debug` | Enable debug logging | `false` |
| `--quiet, -q` | Suppress non-essential output | `false` |
| `--json` | Output in JSON format | `false` |
| `--help, -h` | Show help message | - |

## Commands

### Orchestrator Commands

#### Execute Orchestrator

```bash
cortex orchestrator execute <name> [OPTIONS]
```

Execute a named orchestrator.

**Options:**
- `--context JSON` - Execution context as JSON
- `--context-file PATH` - Load context from file
- `--timeout SECONDS` - Execution timeout (default: 300)
- `--async` - Run asynchronously, return execution ID

**Examples:**
```bash
# Execute with inline context
cortex orchestrator execute planning --context '{"intent": "create_feature"}'

# Execute with context file
cortex orchestrator execute planning --context-file context.json

# Execute asynchronously
cortex orchestrator execute analysis --async
```

#### List Orchestrators

```bash
cortex orchestrator list [OPTIONS]
```

List available orchestrators.

**Options:**
- `--domain DOMAIN` - Filter by domain
- `--status STATUS` - Filter by status (active, inactive)
- `--format FORMAT` - Output format (table, json, yaml)

**Example:**
```bash
# List all orchestrators
cortex orchestrator list

# List planning domain orchestrators
cortex orchestrator list --domain planning

# Output as JSON
cortex orchestrator list --json
```

**Output:**
```
┌─────────────────────────┬───────────┬─────────┬────────────────────────────────┐
│ Name                    │ Domain    │ Status  │ Description                    │
├─────────────────────────┼───────────┼─────────┼────────────────────────────────┤
│ onboarding              │ planning  │ active  │ User onboarding workflow       │
│ complexity_assessment   │ analysis  │ active  │ Assess operation complexity    │
│ gap_detection           │ analysis  │ active  │ Detect implementation gaps     │
│ bkio                    │ integrat. │ active  │ Business knowledge ingestion   │
└─────────────────────────┴───────────┴─────────┴────────────────────────────────┘
```

#### Get Orchestrator Info

```bash
cortex orchestrator info <name>
```

Get detailed information about an orchestrator.

**Example:**
```bash
cortex orchestrator info planning
```

**Output:**
```
Orchestrator: planning
Domain: planning
Status: active
Description: Workflow coordination and planning

Health:
  Circuit Breaker: closed
  Last Execution: 2026-01-20T10:00:00Z
  Success Rate: 98%

Metrics:
  Total Executions: 1,250
  Avg Duration: 3.2s
  Error Rate: 2%

Configuration:
  Timeout: 300s
  Max Retries: 3
  Complexity Gate: enabled
```

### Knowledge Commands

#### Query Knowledge

```bash
cortex knowledge query [OPTIONS]
```

Query the Domain Brain.

**Options:**
- `--domain DOMAIN` - Domain to query (repeatable)
- `--keywords WORDS` - Search keywords (comma-separated)
- `--type TYPE` - Entity type filter
- `--max-results N` - Maximum results (default: 10)

**Examples:**
```bash
# Query financial domain
cortex knowledge query --domain financial --keywords transaction,audit

# Query multiple domains
cortex knowledge query --domain financial --domain compliance --max-results 5

# Query specific entity type
cortex knowledge query --type rule --keywords governance
```

#### Ingest Knowledge

```bash
cortex knowledge ingest <file> [OPTIONS]
```

Ingest knowledge from a file.

**Options:**
- `--format FORMAT` - File format (yaml, json, markdown, csv)
- `--domain DOMAIN` - Target domain
- `--validate-only` - Validate without ingesting

**Examples:**
```bash
# Ingest YAML file
cortex knowledge ingest rules.yaml --format yaml --domain compliance

# Validate only
cortex knowledge ingest rules.yaml --validate-only
```

### Governance Commands

#### Validate

```bash
cortex governance validate <target> [OPTIONS]
```

Validate against governance rules.

**Options:**
- `--rules RULES` - Specific rules to check (comma-separated)
- `--strict` - Fail on warnings
- `--report PATH` - Save report to file

**Examples:**
```bash
# Validate a file
cortex governance validate src/orchestrators/planning.py

# Validate with specific rules
cortex governance validate . --rules CORE-008,CORE-011,CORE-012

# Generate report
cortex governance validate . --report governance-report.md
```

**Output:**
```
Governance Validation Results
─────────────────────────────

✅ CORE-008 (TDD): PASS - Test coverage verified
✅ CORE-011 (Type Hints): PASS - All functions typed
✅ CORE-012 (Docstrings): PASS - Documentation present
⚠️  CORE-028 (Naming): WARN - File name 28 chars (limit: 25)

Summary: 3 passed, 1 warning, 0 failed
```

#### Audit Trail

```bash
cortex governance audit [OPTIONS]
```

Query the audit trail.

**Options:**
- `--ac-id AC_ID` - Filter by AC-ID
- `--start-date DATE` - Start date (YYYY-MM-DD)
- `--end-date DATE` - End date (YYYY-MM-DD)
- `--operation OP` - Filter by operation
- `--verify-chain` - Verify hash chain integrity

**Examples:**
```bash
# Query recent audit entries
cortex governance audit --start-date 2026-01-20

# Query specific AC-ID
cortex governance audit --ac-id AC-PLAN-001

# Verify hash chain
cortex governance audit --verify-chain
```

**Output:**
```
Audit Trail Query Results
────────────────────────

Hash Chain: ✅ VERIFIED (unbroken)

┌─────────┬──────────────┬─────────────┬────────────────────────┐
│ ID      │ AC-ID        │ Operation   │ Timestamp              │
├─────────┼──────────────┼─────────────┼────────────────────────┤
│ 7831    │ AC-PLAN-001  │ AC_COMPLETE │ 2026-01-20T10:00:05Z   │
│ 7830    │ AC-PLAN-001  │ AC_EXECUTE  │ 2026-01-20T10:00:02Z   │
│ 7829    │ AC-PLAN-001  │ AC_START    │ 2026-01-20T10:00:00Z   │
└─────────┴──────────────┴─────────────┴────────────────────────┘

Showing 3 of 5040 entries
```

### Phase Commands

#### Phase Status

```bash
cortex phase status [PHASE_NAME]
```

Show phase status.

**Examples:**
```bash
# Show all phases
cortex phase status

# Show specific phase
cortex phase status PHASE-22-MCP-PROTOCOL-COMPLIANCE
```

**Output:**
```
Phase Status Summary
────────────────────

PHASE-22-MCP-PROTOCOL-COMPLIANCE
  Status: ✅ COMPLETED
  Locked: ✅ Yes
  ACs: 8/8 (100%)
  Tests: All passing

PHASE-23-COMPLEXITY-AWARE-CONFIRMATION
  Status: ✅ COMPLETED
  Locked: ✅ Yes
  ACs: 4/4 (100%)
  Tests: All passing

Summary: 25 phases completed, 25 locked, 100% completion
```

#### Phase Readiness

```bash
cortex phase readiness <PHASE_NAME>
```

Check phase readiness for locking.

**Output:**
```
Phase Readiness Check: PHASE-25-GOVERNANCE-COMPOSITION
──────────────────────────────────────────────────────

✅ Governance: All CORE rules satisfied
✅ Audit Trail: 62 entries, hash chain valid
✅ Tests: 183/183 passing (100%)
✅ Documentation: Updated

READY TO LOCK ✅

To lock phase:
  cortex phase lock PHASE-25-GOVERNANCE-COMPOSITION
```

### Configuration Commands

#### Show Configuration

```bash
cortex config show [OPTIONS]
```

Show current configuration.

**Options:**
- `--section SECTION` - Show specific section
- `--defaults` - Include default values

**Example:**
```bash
cortex config show --section complexity_gate
```

#### Set Configuration

```bash
cortex config set <key> <value>
```

Update configuration value.

**Example:**
```bash
cortex config set complexity_gate.thresholds.trivial 0.10
```

### System Commands

#### Health Check

```bash
cortex system health
```

Check system health.

**Output:**
```
CORTEX System Health
────────────────────

Components:
  ✅ Governance DB: connected (5040 entries)
  ✅ Domain Brain: operational
  ✅ MCP Server: ready
  ✅ Orchestrator Registry: 15 orchestrators

Services:
  ✅ REST API: listening on :8000
  ✅ Audit Logger: active
  ✅ Hash Chain: unbroken

Overall: HEALTHY ✅
```

#### Version

```bash
cortex system version
```

Show version information.

**Output:**
```
CORTEX v1.0.0
  Protocol: MCP 2024-11-05
  Python: 3.11.5
  Platform: darwin-arm64
  Config: cortex-config.yaml
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORTEX_CONFIG` | Config file path | `cortex-config.yaml` |
| `CORTEX_LOG_LEVEL` | Log level | `INFO` |
| `CORTEX_API_KEY` | API key for remote operations | - |
| `CORTEX_DB_PATH` | Governance DB path | `cortex_brain/state/governance.db` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Governance violation |
| 4 | Execution timeout |
| 5 | Connection error |

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(cortex completion bash)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(cortex completion zsh)"
```

### Fish

```fish
# Add to ~/.config/fish/config.fish
cortex completion fish | source
```

## Related Documentation

- [REST API](../rest-api/0-guide.md) - HTTP API
- [MCP Protocol](../mcp-protocol/0-specification.md) - AI-native protocol
- [Local Development](../../04-guides/deployment/1-local-development.md) - Setup guide
- [Troubleshooting](../../04-guides/operations/4-troubleshooting.md) - Common issues
