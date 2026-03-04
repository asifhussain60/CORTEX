---
scope: non-production-admin
---
# Release Notes Agent

**Agent ID:** `release-notes-agent`  
**Updated:** 2026-03-02  
**Layer:** docs  
**Status:** active  
**Responsibility:** Generate structured changelogs and release notes from Git diffs  
**Inputs:** Change manifest from `git-discovery-agent`, phase completion records  
**Outputs:** Release notes in conventional changelog format

---

## 🎯 Single Responsibility

Transform raw Git change data into human-readable, structured release notes. Produce changelogs that are useful for developers, product owners, and business stakeholders — with different detail levels for each audience.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Change manifest** | `git-discovery-agent` output | ✅ |
| **Phase records** | `cortex-registry/planning/phases/completed/` | ✅ |
| **Git tags** | `git tag --list` | Optional |
| **Previous release notes** | `cortex-docs/_archive/release-notes/` or inline history | Optional |

---

## 📤 Outputs

| Output | Format | Audience |
|--------|--------|----------|
| **Full changelog** | Conventional Commits format | Developers |
| **Summary changelog** | Grouped by category | Product Owners |
| **Executive summary** | 3-sentence highlight | Business Leaders |

---

## 📋 Changelog Format

### Full Changelog (Developer)

```markdown
# Changelog — CORTEX {version}
**Date:** {ISO 8601 date}  
**Phase:** {phase_id} — {phase_title}  
**Commits:** {commit_range}

## 🚀 Features
- **{scope}:** {description} ({commit_hash})
- **{scope}:** {description} ({commit_hash})

## 🐛 Bug Fixes
- **{scope}:** {description} ({commit_hash})

## ♻️ Refactoring
- **{scope}:** {description} ({commit_hash})

## 📚 Documentation
- **{scope}:** {description} ({commit_hash})

## 🧪 Tests
- **{scope}:** {description} ({commit_hash})

## ⚠️ Breaking Changes
- **{scope}:** {description} — Migration: {migration_steps}

## 📊 Metrics
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Orchestrator files | {old} | {new} | +{delta} |
| MCP tools registered | {old} | {new} | +{delta} |
| Test count | {old} | {new} | +{delta} |
| Governance rules | {old} | {new} | +{delta} |
```

### Summary Changelog (Product Owner)

```markdown
# Release Summary — CORTEX {version}
**Date:** {date} | **Phase:** {phase_title}

## What's New
- {user-facing description of feature 1}
- {user-facing description of feature 2}

## What's Fixed
- {user-facing description of fix 1}

## What's Changed
- {user-facing description of refactor 1}

## Impact
- {capability_count} capabilities added
- {fix_count} issues resolved
- {test_delta} new tests added
```

### Executive Summary (Business Leader)

```markdown
**CORTEX {version}** — {one-line summary of the most impactful change}.
{Count} new capabilities added, {count} issues resolved.
System now has {total_orchestrators} orchestrators, {total_mcp_tools} tools,
and {total_tests} tests ensuring production stability.
```

---

## 🔄 Generation Rules

### Commit Classification

Commits are classified using Conventional Commits prefixes:

| Prefix | Category | Icon |
|--------|----------|------|
| `feat:` | Features | 🚀 |
| `fix:` | Bug Fixes | 🐛 |
| `refactor:` | Refactoring | ♻️ |
| `docs:` | Documentation | 📚 |
| `test:` | Tests | 🧪 |
| `perf:` | Performance | ⚡ |
| `chore:` | Maintenance | 🔧 |
| `ci:` | CI/CD | 🏗️ |
| `style:` | Style | 🎨 |

### Scope Extraction

Scopes are extracted from commit messages:

```
feat(mcp): Add new cortex_foo tool
     ^^^^
     scope = "mcp"

fix(orchestrators): Fix routing for IMPLEMENT intent
    ^^^^^^^^^^^^^^^
    scope = "orchestrators"
```

If no scope is specified, infer from the changed file paths.

### Breaking Change Detection

A change is **breaking** if:
1. Commit message contains `BREAKING CHANGE:` footer
2. Commit message prefix includes `!` (e.g., `feat!:`)
3. A public API signature changed (detected via diff analysis)
4. A governance rule was added that restricts previously allowed behavior

### Version Tagging

Release notes are identified by the phase they document:

```
Phase 107 → identifier "Phase 107"
Phase 108 → identifier "Phase 108"
```

Do not use semver tags or release numbers. Phase identifiers are the canonical release reference.

---

## 📊 Metrics Capture

Every release note includes a metrics delta:

```
1. Count orchestrator files: find cortex/orchestrators -name "*.py" | wc -l
2. Count MCP tools: grep -c "register" cortex/mcp/mcp_registry.py
3. Count governance rules: find cortex-registry/core -name "*.yaml" | wc -l
4. Count tests: python3 -m pytest --collect-only -q 2>/dev/null | tail -1
5. Count intent types: grep IntentType canonical_enums.py | wc -l

Compare current vs previous release to calculate deltas.
```

---

## 🔄 Automation Integration

### Trigger Points

| Trigger | Action |
|---------|--------|
| Phase marked COMPLETE | Generate full changelog for the phase |
| Git tag created | Generate release notes for the tagged version |
| `/doc-release` command | Generate changelog for current state vs last release |
| Documentation certification passes | Append certification badge to latest release notes |

### Phase Completion Integration

When a phase is marked complete in `cortex-registry/planning/phases/completed/`:

1. Read the phase's dedicated YAML file for acceptance criteria
2. Read the change manifest for commits in the phase's date range
3. Generate all three changelog formats
4. Include the phase's acceptance criteria as verification checklist
5. Report inline (CORE-002)

---

## ⚙️ Deterministic Behavior

Release note generation is deterministic:
- Same Git history → same changelog
- Commit classification is rule-based (prefix matching)
- Metrics are computed from live file system counts
- No LLM inference used for classification

---

## 🔗 Downstream Consumers

| Consumer | What It Uses |
|----------|-------------|
| `coverage-audit-agent` | Verifies every phase has release notes |
| `doc-sync-agent` | Uses release notes to update `.content/` changelog sections |
| `narrative-continuity-agent` | Uses phase completions as story material |

---

## 🛡️ Safety

- **Read-only on source** — only generates new output; never modifies source files
- **Append-only history** — never overwrites previous release notes
- **Conventional format** — follows industry-standard changelog conventions
- **Auditable** — every generated note includes commit range and timestamp
