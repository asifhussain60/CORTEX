---
scope: non-production-admin
agent_id: cortex-content-optimizer
status: active
layer: core
modes_served:
  - OPTIMIZE
capabilities:
  - multi_file_optimization
  - batch_content_compression
  - noise_removal
  - in_place_file_rewriting
  - syntax_validation
  - atomic_file_operations
mcp_tools:
  - cortex_optimize
priority: P1
token_cost_estimate: 1500
last_updated: "2026-03-06"
maintainer: "Asif Hussain"
---

# CORTEX Content Optimizer Agent

**Updated:** 2026-03-06  
**Purpose:** Multi-file content optimization — remove noise, compress intelligently, overwrite in-place.

---

## Role

Batch content optimization engine that processes arrays of heterogeneous files (HTML, Markdown, YAML, JSON, TXT, chat transcripts), removes noise while preserving signal, and overwrites files in-place with optimized content.

**Entry Point:** `ContentOptimizationOrchestrator` (`cortex/orchestrators/support/content_optimization_orchestrator.py`)
**MCP Tool:** `cortex_optimize`
**Phase:** 130

---

## Activation

Triggered by **OPTIMIZE** intent from `IntentRouter`.

**Trigger patterns:** "optimize", "/optimize", "compress files", "reduce files", "batch optimize", "remove noise", "minify"

**Usage:**

```
/optimize file_paths=["doc.md", "data.json", "config.yaml"]
optimize these files: doc.md, data.json, config.yaml
compress content in doc.md and data.json
batch optimize all files in .analysis/
```

---

## 5-Stage Pipeline

| Stage | Purpose | Method |
|-------|---------|--------|
| **1. Classify** | Detect content type for each file | Extension + MIME + content analysis |
| **2. Read** | Load all files into memory | Parallel batch I/O |
| **3. Optimize** | Per-type compression via LLM | Type-specific noise removal |
| **4. Validate** | Ensure syntax validity | YAML parse, JSON parse, HTML lint |
| **5. Write** | Overwrite files in-place | Atomic write (temp → rename) |

---

## Supported Content Types

| Type | Extensions | Optimization Strategy |
|------|------------|----------------------|
| **HTML** | `.html`, `.htm` | Remove comments, collapse whitespace, strip space around tags |
| **Markdown** | `.md`, `.markdown` | Remove filler phrases (Lorem ipsum, etc.), collapse blank lines |
| **YAML** | `.yaml`, `.yml` | Strip comments, remove excessive whitespace |
| **JSON** | `.json` | Minify (remove all whitespace, compact keys) |
| **Text** | `.txt` | Remove filler sentences, collapse blank lines |
| **Chat Transcript** | `.txt`, `.md` with chat markers | Delegate to `DistillationOrchestrator` (Phase 129) |

---

## Validation Gates

Before writing any file, the orchestrator validates syntax:

| Content Type | Validation | Action on Failure |
|--------------|------------|-------------------|
| **JSON** | `json.loads()` | Skip file, preserve original |
| **YAML** | `yaml.safe_load()` | Skip file, preserve original |
| **Others** | No strict syntax | Always valid |

**Guarantee:** No file is corrupted. If optimization breaks syntax, the original file remains unchanged.

---

## Atomic Write Strategy

Each file is written using a 2-step atomic operation:

1. Write optimized content to `{file}.tmp`
2. Rename `{file}.tmp` → `{file}` (atomic on POSIX)

**Rollback safety:** If the process crashes mid-write, the original file is intact. The `.tmp` file can be cleaned up.

---

## Workflow Template

**Location:** `cortex-registry/workflows/templates/lifecycle/content-optimization-workflow.yaml`

**Primitives used:**
- `primitives/execution/ac-marker-emit.yaml` — AC_START / AC_COMPLETE
- None (no governance gate required — non-code content)

---

## MCP Tool Interface

**Tool:** `cortex_optimize`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_paths` | `array` | ✅ | Array of absolute file paths to optimize |
| `orchestrator_context` | `string` | ⚪ | Optional governance routing context |

**Returns:**

```json
{
  "success": true,
  "files_processed": 5,
  "files_written": 5,
  "total_bytes_saved": 12847,
  "file_results": [
    {
      "file_path": "/path/to/doc.md",
      "content_type": "markdown",
      "original_size": 5420,
      "optimized_size": 3102,
      "compression_ratio": 42.8,
      "success": true,
      "error": null
    }
  ]
}
```

---

## Example Usage

### Single File

```
optimize doc.md
```

### Multiple Files

```
optimize files: doc.md, data.json, config.yaml
```

### Array Syntax (MCP direct)

```python
from cortex.mcp.tools.cortex_optimize_tool import CortexOptimize

tool = CortexOptimize()
result = tool.execute({
    "file_paths": [
        "/workspace/doc.md",
        "/workspace/data.json",
        "/workspace/config.yaml",
    ]
})

print(f"Saved {result.data['total_bytes_saved']} bytes")
```

---

## Governance

**Rules enforced:**
- CORE-002: No .md/.txt report files — all output inline
- CORE-035: Single canonical implementation (no duplicate optimizers)
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs

**No CORE-008 (TDD) enforcement:** OPTIMIZE mode does not touch code, so test-first is not required.

**No holistic validation gate:** OPTIMIZE mode is non-invasive (content files only, not source code).

---

## Relationship to DISTILL Mode

| Mode | Purpose | Input | Output |
|------|---------|-------|--------|
| **DISTILL** (Phase 129) | Compress **chat transcripts** into executable prompts | Single conversation string | Distilled prompt (goals, decisions, constraints) |
| **OPTIMIZE** (Phase 130) | Compress **file arrays** of mixed content | Array of file paths | Overwritten files in-place |

**Integration:** When OPTIMIZE encounters a file classified as `ContentType.CHAT_TRANSCRIPT`, it delegates to `DistillationOrchestrator` for specialized chat compression.

---

## Error Handling

| Error | Behavior |
|-------|----------|
| **Empty file_paths array** | Return `success=False`, `error_message="Empty file_paths array — nothing to optimize."` |
| **File not found** | Skip file, log in `file_results`, continue with others |
| **Read permission denied** | Skip file, log in `file_results`, continue with others |
| **Syntax validation failure** | Skip file, preserve original, log error |
| **Write permission denied** | Skip file, preserve original, log error |
| **All files failed** | Return `success=False` with aggregate error count |

**Fail-safe guarantee:** No partial writes. Each file is either fully optimized or unchanged.

---

## Testing Strategy

**Golden test suite:** `tests/golden/test_content_optimization_golden.py`

**Coverage:**
- 15 golden tests across all 6 content types
- Multi-file batch scenarios (mixed types)
- Validation gate enforcement (broken YAML/JSON)
- Error handling (missing files, read errors, write errors)
- Atomic write verification (no partial states)

**Test execution:**

```bash
make test-smoke  # includes golden tests
python3 scripts/run_tests.py file tests/golden/test_content_optimization_golden.py
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Throughput** | ~50-100 files/second (parallel I/O) |
| **Compression ratio** | 20-60% size reduction (content-dependent) |
| **Memory usage** | Linear with file count (batch reads) |
| **Latency** | ~100-200ms per file (LLM optimization) |

**Optimization:** For large file arrays (>100 files), consider batching into chunks to limit memory usage.

---

## Future Enhancements

| Enhancement | Priority | Phase |
|-------------|----------|-------|
| **Parallel LLM optimization** | P2 | Future |
| **Diff preview before write** | P2 | Future |
| **Rollback command** | P3 | Future |
| **Content-type plugins** | P3 | Future |

---

*Agent specification current as of March 2026 · Phase 130 implementation*
