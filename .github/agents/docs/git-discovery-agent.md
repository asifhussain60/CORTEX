# Git Discovery Agent

**Agent ID:** `git-discovery-agent`  
**Updated:** 2026-03-02  
**Layer:** docs  
**Status:** active  
**Responsibility:** Inspect Git history, classify changes, detect architectural shifts  
**Inputs:** Git repository, last execution timestamp  
**Outputs:** Classified change manifest (JSON-compatible structure)

---

## 🎯 Single Responsibility

Analyze Git history since the last documented execution and produce a structured change manifest classifying every relevant file change by documentation impact category.

This agent does NOT modify any files. It produces a change manifest consumed by downstream agents.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Repository path** | Workspace root | ✅ |
| **Last execution timestamp** | `.cortex-runtime/doc-orchestrator-state.json` | ✅ (falls back to 7 days if missing) |
| **Scope filter** | User-provided or default `[cortex/, cortex-registry/, cortex-docs/, .github/, tests/]` | Optional |

---

## 📤 Outputs

A **change manifest** with the following structure:

```yaml
discovery:
  timestamp: "2026-03-02T10:30:00Z"
  since: "2026-02-23T10:30:00Z"
  commit_range: "abc1234..def5678"
  total_commits: 47
  total_files_changed: 123

  categories:
    architectural_shifts:
      - type: "new_orchestrator"
        path: "cortex/orchestrators/core/new_orchestrator.py"
        commit: "abc1234"
        summary: "Added FooOrchestrator for bar intent routing"
      - type: "dissolved_package"
        path: "cortex_old/"
        commit: "def5678"
        summary: "Dissolved cortex_old package — migrated to cortex/"

    new_capabilities:
      - type: "new_mcp_tool"
        path: "cortex/mcp/tools/cortex_foo.py"
        summary: "New MCP tool for foo operations"

    deprecated_features:
      - type: "removed_module"
        path: "cortex/old_module.py"
        summary: "Module sunset — functionality merged into cortex/new_module.py"

    behavioral_changes:
      - type: "governance_rule_change"
        path: "cortex-registry/core/rules.yaml"
        summary: "CORE-070 added — new pre-commit validation"

    documentation_changes:
      - type: "content_update"
        path: "cortex-docs/.content/05-orchestration.md"
        summary: "Updated orchestrator count"

    test_changes:
      - type: "new_test_file"
        path: "tests/orchestrators/test_foo.py"
        summary: "Tests for FooOrchestrator"
```

---

## 🔍 Detection Rules

### File Classification Matrix

| Path Pattern | Category | Sub-type |
|-------------|----------|----------|
| `cortex/orchestrators/**/*.py` (new) | `architectural_shifts` | `new_orchestrator` |
| `cortex/orchestrators/**/*.py` (deleted) | `deprecated_features` | `removed_orchestrator` |
| `cortex/orchestrators/**/*.py` (renamed) | `architectural_shifts` | `orchestrator_moved` |
| `cortex/mcp/tools/**/*.py` (new) | `new_capabilities` | `new_mcp_tool` |
| `cortex/mcp/mcp_registry.py` (modified) | `new_capabilities` | `tool_registration_change` |
| `cortex-registry/core/**/*.yaml` (modified) | `behavioral_changes` | `governance_rule_change` |
| `cortex-registry/workflows/**/*.yaml` (new) | `new_capabilities` | `new_workflow_template` |
| `cortex/models/canonical_enums.py` (modified) | `behavioral_changes` | `intent_type_change` |
| `cortex/intelligence/**/*.py` (modified) | `behavioral_changes` | `intelligence_change` |
| `cortex-docs/**` (any) | `documentation_changes` | varies |
| `.github/prompts/**` (any) | `documentation_changes` | `prompt_change` |
| `.github/agents/**` (any) | `documentation_changes` | `agent_change` |
| `tests/**` (any) | `test_changes` | varies |

### Architectural Shift Detection

An **architectural shift** is detected when any of the following occur:
1. **Orchestrator count changes** — new files added or removed in `cortex/orchestrators/`
2. **Package dissolution** — a top-level package directory is deleted
3. **Tier restructuring** — files moved between `core/`, `domain/`, `support/` tiers
4. **Intelligence facade change** — modifications to `cortex/intelligence/facade.py`
5. **Entry point change** — modifications to `cortex/orchestrators/core/master_orchestrator.py`

### Capability Detection

A **new capability** is detected when:
1. New MCP tool file appears in `cortex/mcp/tools/`
2. New registration in `cortex/mcp/mcp_registry.py`
3. New intent type in `cortex/models/canonical_enums.py`
4. New workflow template in `cortex-registry/workflows/templates/`
5. New debug strategy in `cortex/orchestrators/support/debugging/`

---

## ⚙️ Execution

### Git Commands Used

```bash
# Get commits since last execution
git log --since="{timestamp}" --format="%H %s" --name-status

# Get file-level changes
git diff --name-status {last_commit}..HEAD

# Detect renames
git diff --name-status -M {last_commit}..HEAD

# Count per-directory changes
git diff --stat {last_commit}..HEAD -- cortex/
```

### Deterministic Behavior

This agent is **deterministic** — given the same Git state and timestamp, it always produces the same change manifest. No LLM inference is used for classification; all classification is rule-based per the File Classification Matrix above.

---

## 🔗 Downstream Consumers

| Consumer | What It Uses |
|----------|-------------|
| `drift-detection-agent` | `architectural_shifts` + `new_capabilities` + `deprecated_features` |
| `doc-sync-agent` | Full manifest — determines which `.content/` files need updating |
| `diagram-regeneration-agent` | `architectural_shifts` — triggers diagram rebuild |
| `narrative-continuity-agent` | `new_capabilities` — source material for story evolution |
| `release-notes-agent` | Full manifest — structured changelog generation |
| `coverage-audit-agent` | Full manifest — validates nothing slipped through undocumented |

---

## 🛡️ Safety

- **Read-only** — this agent never modifies files
- **Idempotent** — safe to run multiple times
- **Bounded** — respects scope filter to avoid scanning irrelevant paths
- **Timestamped** — every manifest includes generation timestamp for audit trail
