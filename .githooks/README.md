# CORTEX Git Hooks

This directory contains git hooks for enforcing CORTEX governance and architecture standards.

## Installation

**Automatic (Recommended):**
```bash
git config core.hooksPath .githooks
```

**Manual:**
```bash
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Hooks

### pre-commit
**Purpose:** MCP-FIRST architecture enforcement

**Checks:**
- ✅ Python files don't bypass MCP with direct file operations
- ✅ Instruction files contain MCP PRE-FLIGHT checks
- ✅ IMPLEMENT/FIX/REFACTOR intents use `cortex_process_request`
- ✅ ANALYZE/AUDIT intents use `cortex_lens_analyze`

**Violations Block Commit:** Yes (can bypass with `--no-verify`, not recommended)

## Enforcement Levels

| Level | Action | Bypass |
|-------|--------|--------|
| **P0 Critical** | Block commit | `--no-verify` (discouraged) |
| **P1 High** | Warn but allow | N/A |
| **P2 Medium** | Log only | N/A |

## Testing Hooks

```bash
# Test pre-commit hook
.githooks/pre-commit

# Expected output if compliant:
# ✅ MCP-FIRST compliance validated
```

## Cross-Machine Enforcement

This hook enforces standards **on all machines** that clone the repository:

1. Clone repository
2. Run: `git config core.hooksPath .githooks`
3. Hook active on that machine

**Team Setup:** Add to onboarding docs or use git config templates.

## Related

- [MCP-FIRST Architecture](.github/copilot-instructions.md#mcp-first-enforcement)
- [CORTEX Prompt](.github/prompts/CORTEX.prompt.md)
- [Governance Rules](cortex/governance/)
