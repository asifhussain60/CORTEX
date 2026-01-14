# Session Summary Template

This directory stores structured session summaries for CORTEX development conversations.

## Purpose

Replace raw chat transcripts (which bloat workspace context) with structured decision records.

## Format

Each session summary is a YAML file: `{YYYY-MM-DD}-{topic-slug}.yaml`

## Template

```yaml
date: YYYY-MM-DD
topic: Brief description of the session focus
user_intent: What the user was trying to accomplish
orchestrator: Which orchestrator was used (or "Manual" if no orchestrator)
decision: Key decision made (if any)
rationale: Why this decision was made
ac_ids_referenced:
  - AC-XXX-NNN  # AC-ID with brief description
ac_ids_implemented:
  - AC-XXX-NNN  # AC-ID with brief description
next_steps:
  - Action item 1
  - Action item 2
blockers:
  - Blocker description (or "None")
artifacts_created:
  - file: path/to/file.ext
    purpose: What this file does
correlations:
  - epic: CORTEX-X.X
    phase: N
    context: Relevant context
```

## Benefits

✅ Searchable context for RAG retrieval  
✅ Audit trail of decisions  
✅ No chat transcript bloat (10-20 lines vs 4000+ lines)  
✅ Structured for knowledge graph ingestion  
✅ IDE-agnostic (not tied to GitHub Copilot)

## Example

See: `2026-01-14-database-alternatives.yaml`
