# CX6 Acceptance Criteria Update - v15.0.0 Summary

**Date:** 2026-01-09  
**Version:** v15.0.0  
**Author:** CORTEX  
**Status:** MAJOR UPDATE - Holistic Alignment + Digest Utility

---

## 🎯 Executive Summary

**Major Features:**
1. ✅ **Holistic Plan Alignment System** - Continuous validation with complexity-based recreation
2. ✅ **Digest Utility** - Universal file-to-YAML converter with MCP exposure

**New AC Count:** 11 (AC-ALIGN-001 to AC-ALIGN-005, AC-DIGEST-001 to AC-DIGEST-006)  
**Total AC Count:** 411+ (was 400+)

---

## 📋 SECTION 21: Holistic Plan Alignment & Validation

### AC-ALIGN-001: Holistic Plan Review Triggers

**Purpose:** Automatic plan-to-requirements alignment validation on every gap-fix execution

**Key Features:**
- ✅ Triggered on EVERY gap-fix execution (Phase 11)
- ✅ Reviews: CX6-acceptance-criteria.yaml + CX6-requirements.yaml + cortex6-planner/ structure
- ✅ Detects: Missing AC coverage, obsolete tasks, structural violations
- ✅ Calculates complexity score (0-100) based on drift metrics

**Audit Evidence:**
- `cortex-brain/audit-logs/holistic-alignment-*.json`
- `cortex6/acceptance-criteria/alignment-complexity-{timestamp}.yaml`

---

### AC-ALIGN-002: Complexity-Based Plan Recreation

**Purpose:** Automatic plan deletion + recreation when drift becomes too severe

**Complexity Scoring Algorithm:**
```
complexity_score = (structural_violations × 10) 
                 + (coverage_gaps × 5) 
                 + (obsolete_tasks × 3)
```

**Thresholds & Actions:**

| Score | Threshold | Action |
|-------|-----------|--------|
| 0-20 | **LOW** | Minor alignment corrections only |
| 21-50 | **MEDIUM** | Major restructuring (reorder phases, inject gaps) |
| 51-75 | **HIGH** | Recreation recommended (user notified) |
| 76-100 | **CRITICAL** | 🔴 **AUTOMATIC deletion + recreation** |

**Metrics:**
- `plan_complexity_score` (0-100)
- `threshold_low: 20`
- `threshold_medium: 50`
- `threshold_high: 75`
- `threshold_critical: 76`

**Protection:**
- Score > 50: User notification before recreation
- Score ≥ 76: Automatic deletion + regeneration from AC
- Backup created before deletion: `archive/cortex6-planner-backup-{timestamp}/`

**Example Scenarios:**

**Scenario 1: LOW Complexity (Score: 15)**
```yaml
structural_violations: 1  # (README.md on root)
coverage_gaps: 1          # (1 missing AC)
obsolete_tasks: 0         # (no obsolete tasks)
score: (1×10) + (1×5) + (0×3) = 15
action: "Correct structure violations, inject 1 gap as task"
```

**Scenario 2: CRITICAL Complexity (Score: 85)**
```yaml
structural_violations: 5  # (5 00- prefix files, wrong root files)
coverage_gaps: 6          # (6 missing AC sections)
obsolete_tasks: 5         # (5 tasks no longer in AC)
score: (5×10) + (6×5) + (5×3) = 95
action: "DELETE cortex6-planner/ → REGENERATE from AC"
```

---

### AC-ALIGN-003: Prompt File Alignment Validation

**Purpose:** Keep `.github/prompts/*.prompt.md` synchronized with AC evolution

**Validation Checks:**
- ✅ Prompt instructions match current AC requirements
- ✅ Version metadata matches AC version
- ✅ No references to outdated AC IDs or removed features
- ✅ Auto-sync prompt sections from AC templates

**Drift Detection:**
- If drift > 30%: Flag for manual review (LLM regeneration risky)
- If drift < 30%: Auto-regenerate affected sections

**Audit Evidence:**
- `cortex6/acceptance-criteria/prompt-drift-{timestamp}.yaml`
- `cortex-brain/audit-logs/prompt-sync-*.json`

---

### AC-ALIGN-004: Plan Structure Validation

**Purpose:** Enforce AC-ORC-PLAN-002 on every holistic review

**Validation Checks:**
| Check | Rule |
|-------|------|
| **Root Files** | EXACTLY 3: continuation-prompt.md, thoughts.txt, plan-viewer.html |
| **Prefixes** | NO 00-, 01-, etc. prefixes allowed |
| **Formats** | All artifacts (except 3 root files) MUST be .yaml or .json |
| **Folders** | 5 required: analysis/, artifacts/, context/, reports/, tracking/ |

**Auto-Remediation:**
- Violations found → Trigger structure migration automatically
- Backup to `archive/` before remediation
- Apply corrections per AC-ORC-PLAN-002

**SKULL Rules Enforced:**
- `PLAN_FILE_ORGANIZATION`
- `NO_00_PREFIX_FILES`
- `YAML_JSON_ONLY`

---

### AC-ALIGN-005: Multiple Alignment Triggers

**Purpose:** Ensure alignment validation runs at strategic checkpoints

**Trigger Points:**

| Trigger | When | Frequency |
|---------|------|-----------|
| **Gap-Fix** | Every gap-fix Phase 11 holistic sync | Per execution |
| **Manual** | `/CORTEX align cortex6` command | On demand |
| **Pre-Flight** | Before `/CORTEX continue cortex6` | Per execution |
| **Scheduled** | Daily if plan modified in last 24h | Daily (conditional) |
| **Git Hook** | When CX6-acceptance-criteria.yaml modified | On AC commit |

**Cache Optimization:**
- Results cached for 1 hour
- Skip validation if already done within cache window
- Cache invalidated on AC file changes

---

## 📦 SECTION 22: Digest Utility - File Format Conversion

### AC-DIGEST-001: Universal File-to-YAML Conversion

**Purpose:** Convert any file format to structured YAML for CORTEX knowledge ingestion

**Supported Formats:**

| Format | Extension | Extraction Features |
|--------|-----------|---------------------|
| **Markdown** | `.md` | Headings, lists, tables, code blocks, metadata |
| **Text** | `.txt` | Line-by-line with section detection |
| **JSON** | `.json` | Direct structure mapping |
| **CSV** | `.csv` | Tabular data with headers |
| **HTML** | `.html` | Semantic structure (headings, sections, links) |
| **PDF** | `.pdf` | Text extraction with page metadata |
| **DOCX** | `.docx` | Paragraphs, tables, styles |

**Conversion Process:**
1. **Parse:** Extract structured data from source format
2. **Transform:** Map to YAML structure with schema
3. **Validate:** Check against `digest-output.schema.json`
4. **Metadata:** Add filename, format, creation date, author
5. **Chunk:** Split large files into sections with cross-references

**Example Input (Markdown):**
```markdown
# API Specification

## Authentication
- OAuth2
- JWT tokens

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/users | List users |
```

**Example Output (YAML):**
```yaml
metadata:
  source_file: "api-spec.md"
  format: "markdown"
  created_at: "2026-01-09T10:30:00Z"
  author: "Asif Hussain"

content:
  title: "API Specification"
  sections:
    - name: "Authentication"
      items:
        - "OAuth2"
        - "JWT tokens"
    - name: "Endpoints"
      type: "table"
      rows:
        - method: "GET"
          path: "/api/users"
          description: "List users"
```

---

### AC-DIGEST-002: Auto-Classification & Governance-Compliant Storage

**Purpose:** Intelligent file placement following CORTEX brain tier organization

**Classification Rules:**

| Content Type | Detected By | Storage Location |
|--------------|-------------|------------------|
| **Plans** | Keywords: "Phase", "Task", "Epic" | `documents/planning/` |
| **Docs** | Markdown with sections, no code | `documents/` |
| **Code** | Code blocks, function definitions | `artifacts/` |
| **Knowledge** | API specs, architecture docs | `tier2/domain-knowledge/` |
| **Requirements** | "MUST", "SHALL", "AC-*" patterns | `tier0/requirements/` |
| **Best Practices** | "Best practice", "Pattern", "Anti-pattern" | `tier0/best-practices/` |

**LLM-Powered Classification:**
- Content analysis with GPT-4 (when heuristics uncertain)
- Confidence score: High (>80%) = auto-store, Low (<80%) = prompt user

**Governance Compliance:**
- Follows `brain-protection-rules.yaml` placement rules
- Respects tier organization (tier0 = governance, tier1 = working memory, tier2 = knowledge, tier3 = dev context)
- Creates subfolders if missing
- Collision detection: File exists → append timestamp or prompt user

**Example:**
```bash
# Digest API spec (no target specified)
python -m src.utilities.digest api-spec.md

# Auto-classified as "Knowledge" → stored at:
# tier2/domain-knowledge/api-specs/api-spec.yaml
```

---

### AC-DIGEST-003: MCP Tool Exposure

**Purpose:** Make digest utility accessible via Model Context Protocol

**MCP Tool Registration:**
```python
# Tool Name
cortex_digest

# Parameters
{
  "file_path": str,           # REQUIRED - Path to file to convert
  "target_location": str,     # OPTIONAL - Override auto-classification
  "format": str               # OPTIONAL - Override auto-detect
}

# Return Value
{
  "success": bool,
  "yaml_path": str,           # Path to generated YAML
  "classification": str,      # Detected category
  "metadata": {
    "original_format": str,
    "size_bytes": int,
    "conversion_time_ms": int
  }
}
```

**Invocation Examples:**

**Via MCP:**
```python
result = mcp.invoke('cortex_digest', {
    'file_path': '/path/to/api-spec.md'
})
# Returns: {'success': True, 'yaml_path': 'tier2/.../api-spec.yaml', ...}
```

**Via CLI:**
```bash
python -m src.utilities.digest /path/to/api-spec.md
```

**Error Handling:**
- Unsupported format → Graceful fallback (store as text blob in YAML)
- File not found → Clear error message with suggestions
- Permission denied → Log audit event, return error

---

### AC-DIGEST-004: Batch Processing & Recursion

**Purpose:** Convert entire directories efficiently

**Batch Mode Features:**

```bash
# Convert entire directory recursively
python -m src.utilities.digest /path/to/docs/ --recursive

# Filter by pattern
python -m src.utilities.digest /path/to/docs/ --recursive \
    --include "*.md" --exclude "*-backup.md"

# Progress reporting (ASCII for accessibility)
Converting: [████████░░] 80% (40/50 files)
- api-spec.md → tier2/domain-knowledge/api-specs/api-spec.yaml ✅
- auth-flow.md → tier2/domain-knowledge/auth/auth-flow.yaml ✅
- old-backup.md → Skipped (excluded) ⏭️
```

**Error Recovery:**
- Continue on individual file errors
- Log failures to `digest-errors.log`
- Summary report with success/failure counts

**Summary Report:**
```yaml
digest_summary:
  generated_at: "2026-01-09T10:30:00Z"
  source_directory: "/path/to/docs/"
  total_files: 50
  successful: 45
  failed: 5
  skipped: 0
  conversion_time_seconds: 12.5
  
  failed_files:
    - file: "corrupted.pdf"
      error: "PDF extraction failed: Invalid format"
    - file: "locked.docx"
      error: "Permission denied"
```

---

### AC-DIGEST-005: YAML Output Schema Validation

**Purpose:** Ensure all converted YAML files follow consistent schema

**Schema Validation:**
- Validate against `cortex-brain/schemas/digest-output.schema.json`
- Required fields: `metadata` (source_file, format, created_at), `content` (structured data)
- Validation failure → Reject, log error with details
- Auto-generate minimal schema if content type unknown

**Schema Example:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["metadata", "content"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["source_file", "format", "created_at"],
      "properties": {
        "source_file": {"type": "string"},
        "format": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "author": {"type": "string"}
      }
    },
    "content": {
      "type": "object",
      "description": "Structured content (format-specific)"
    }
  }
}
```

---

### AC-DIGEST-006: Implementation Requirements

**Files to Create:**

| File | Purpose |
|------|---------|
| `src/utilities/digest.py` | Core conversion logic |
| `src/utilities/converters/markdown.py` | Markdown converter |
| `src/utilities/converters/text.py` | Text converter |
| `src/utilities/converters/json_conv.py` | JSON converter |
| `src/utilities/converters/csv.py` | CSV converter |
| `src/utilities/converters/html.py` | HTML converter |
| `src/utilities/converters/pdf.py` | PDF converter |
| `src/utilities/converters/docx.py` | DOCX converter |
| `src/mcp/digest_tool.py` | MCP tool wrapper |
| `cortex-brain/schemas/digest-output.schema.json` | Output schema |
| `src/utilities/README.md` | Usage documentation |

**Test Coverage:**
- Unit tests: 95%+ coverage for all conversion functions
- Integration tests: End-to-end MCP invocation
- Test files: `tests/utilities/test_digest_*.py`

---

## 📊 Impact Summary

### New Capabilities

| Capability | Benefit |
|------------|---------|
| **Holistic Alignment** | Prevents plan drift, ensures AC compliance |
| **Complexity-Based Recreation** | Automatic cleanup when plans become too stale |
| **Prompt Sync** | Keeps orchestrator prompts aligned with AC evolution |
| **Digest Utility** | Universal knowledge ingestion from any format |
| **Batch Conversion** | Efficient processing of documentation sets |

### Governance Enhancements

| Enhancement | Rule |
|-------------|------|
| **Continuous Validation** | Plans validated on gap-fix, pre-flight, schedule, git hook |
| **Auto-Remediation** | Structure violations fixed automatically |
| **Tier Compliance** | Digest respects brain tier organization |
| **SKULL Enforcement** | PLAN_FILE_ORGANIZATION, NO_00_PREFIX, YAML_JSON_ONLY |

---

## 🚀 Next Steps

### Phase 1: Implement Holistic Alignment (AC-ALIGN-001 to AC-ALIGN-005)
**Estimated Effort:** 12-16 hours

1. Implement `src/orchestrators/alignment/holistic_alignment_orchestrator.py`
2. Add complexity scoring algorithm
3. Implement plan recreation logic (threshold detection)
4. Add prompt file sync mechanism
5. Create alignment validation triggers
6. Add tests: `tests/orchestrators/test_holistic_alignment.py`

### Phase 2: Implement Digest Utility (AC-DIGEST-001 to AC-DIGEST-006)
**Estimated Effort:** 16-20 hours

1. Implement `src/utilities/digest.py` (core)
2. Implement format-specific converters (7 formats)
3. Add LLM-powered classification
4. Implement MCP tool wrapper
5. Add batch processing support
6. Create schema validation
7. Add tests: `tests/utilities/test_digest_*.py`

### Phase 3: Integration Testing
**Estimated Effort:** 4-6 hours

1. Test gap-fix → holistic alignment integration
2. Test digest via MCP invocation
3. Test batch conversion workflows
4. Test complexity-based recreation triggers

---

## 📁 File Locations

| Artifact | Location |
|----------|----------|
| **AC Source** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-acceptance-criteria.yaml` |
| **Alignment Reports** | `cortex6/acceptance-criteria/alignment-complexity-{timestamp}.yaml` |
| **Digest Schema** | `cortex-brain/schemas/digest-output.schema.json` |
| **Audit Logs** | `cortex-brain/audit-logs/holistic-alignment-*.json` |
| **Digest Summaries** | `cortex-brain/documents/utilities/digest-summary-{timestamp}.yaml` |

---

## ✅ Validation

**AC Count:**
- **Previous:** 400+ AC
- **Added:** 11 AC (AC-ALIGN-001 to AC-ALIGN-005, AC-DIGEST-001 to AC-DIGEST-006)
- **Current:** 411+ AC

**Version:**
- **Previous:** v14.4.0
- **Current:** v15.0.0

**Priority Breakdown:**
- **P0_CRITICAL:** AC-ALIGN-001, AC-ALIGN-002, AC-ALIGN-004
- **P1_HIGH:** AC-ALIGN-003, AC-ALIGN-005, AC-DIGEST-001, AC-DIGEST-002, AC-DIGEST-003, AC-DIGEST-006
- **P2_MEDIUM:** AC-DIGEST-004, AC-DIGEST-005

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
