# CORTEX Knowledge Graph Import System - User Guide

## Overview

The CORTEX Knowledge Graph Import System allows you to capture strategic conversations and import them as reusable patterns. These patterns enable CORTEX to recognize similar scenarios in future work and suggest proven approaches.

## Quick Start

### 1. Import a Conversation
```bash
python scripts/import_conversation.py cortex-brain/documents/conversation-captures/your-capture.md
```

### 2. Verify the Import
```bash
python scripts/verify_import.py
```

### 3. Search for Patterns
```bash
# List all patterns
python scripts/search_patterns.py --list

# Search by tag
python scripts/search_patterns.py --tag test_driven_development

# Search by keyword
python scripts/search_patterns.py --search validation
```

### 4. View Pattern Details
```bash
python scripts/show_pattern.py <pattern_id>
```

## Available Scripts

### `import_conversation.py`
**Purpose:** Import conversation captures into knowledge graph

**Usage:**
```bash
python scripts/import_conversation.py <path-to-markdown-file>
```

**Example:**
```bash
python scripts/import_conversation.py cortex-brain/documents/conversation-captures/2025-11-18-capability-driven-validation-implementation.md
```

**Output:**
- Pattern ID
- Quality score
- Key patterns count
- Lessons learned count
- Files involved count
- Tags for searchability
- Storage location confirmation

**What It Does:**
1. Reads conversation capture markdown file
2. Extracts patterns, lessons, metrics
3. Checks for duplicates
4. Appends to knowledge-graph.yaml
5. Enables pattern recognition

---

### `verify_import.py`
**Purpose:** Verify a pattern was successfully imported

**Usage:**
```bash
python scripts/verify_import.py [pattern_id]
```

**Default:** Verifies most recent import (`capability_driven_validation_2025_11_18`)

**Output:**
- ✅ Success/failure status
- Total patterns in knowledge graph
- Pattern metadata (ID, title, status, namespace, quality)
- Content summary (key patterns, lessons, files, tags)

---

### `search_patterns.py`
**Purpose:** Search knowledge graph by tags or keywords

**Usage:**
```bash
# List all patterns
python scripts/search_patterns.py --list

# Search by exact tag match
python scripts/search_patterns.py --tag <tag-name>

# Search by keyword in title
python scripts/search_patterns.py --search <search-term>
```

**Examples:**
```bash
# Show all patterns
python scripts/search_patterns.py --list

# Find TDD patterns
python scripts/search_patterns.py --tag test_driven_development

# Find validation patterns
python scripts/search_patterns.py --search validation
```

**Output:**
- Number of matching patterns
- Pattern titles
- Pattern IDs
- Status
- Quality scores
- Key tags
- Pattern counts (key patterns, lessons)

**Available Tags:**
- `validation`
- `test_driven_development`
- `configuration_driven`
- `iterative_debugging`
- `documentation_coverage`
- `yaml_driven`
- `production_ready`

---

### `show_pattern.py`
**Purpose:** Display comprehensive pattern details

**Usage:**
```bash
python scripts/show_pattern.py <pattern_id>
```

**Example:**
```bash
python scripts/show_pattern.py capability_driven_validation_2025_11_18
```

**Output:**
- **Metadata:** ID, date, status, namespace, quality, source, import timestamp
- **Key Patterns:** Name, description, evidence, confidence scores
- **Lessons Learned:** Lesson name, context, impact
- **Implementation Metrics:** Code changes, test coverage, quality stats
- **Files Involved:** List of related files
- **Reusable Artifacts:** Methods/functions that can be reused
- **Tags:** Searchable keywords

---

## Workflow Examples

### Example 1: Import and Verify
```bash
# Import conversation
python scripts/import_conversation.py cortex-brain/documents/conversation-captures/my-capture.md

# Verify import succeeded
python scripts/verify_import.py

# View full details
python scripts/show_pattern.py my_pattern_id_2025_11_18
```

### Example 2: Search for TDD Patterns
```bash
# Find all TDD patterns
python scripts/search_patterns.py --tag test_driven_development

# Get details of specific pattern
python scripts/show_pattern.py capability_driven_validation_2025_11_18
```

### Example 3: Review All Patterns
```bash
# List all patterns in knowledge graph
python scripts/search_patterns.py --list

# Pick a pattern and view details
python scripts/show_pattern.py <pattern_id_from_list>
```

---

## Pattern Structure

### Conversation Capture Format
Create markdown files in `cortex-brain/documents/conversation-captures/` with:

```markdown
# Title

## Implementation Journey
- Requirements
- Design decisions
- Implementation details
- Debugging cycles
- Test results

## Key Patterns
1. Pattern name - Description
2. Pattern name - Description

## Lessons Learned
1. Lesson - Why it matters
2. Lesson - Why it matters

## Metrics
- Code changes
- Test results
- Performance
```

### Knowledge Graph Entry
The import script creates structured YAML entries:

```yaml
patterns:
  - pattern_id: unique_identifier_YYYY_MM_DD
    title: Human-readable title
    date: YYYY-MM-DD
    quality_score: 1-14
    status: production_ready
    namespace: cortex.domain.subdomain
    key_patterns:
      - name: Pattern name
        description: What it does
        evidence: Proof it works
        confidence: 0.0-1.0
    lessons_learned:
      - lesson: What was learned
        impact: Why it matters
    implementation_metrics:
      code: {changes}
      tests: {coverage}
      quality: {results}
    files_involved: [paths]
    reusable_artifacts: [methods]
    tags: [keywords]
    source_file: Original capture path
    imported_at: ISO timestamp
```

---

## Current Knowledge Graph

### Pattern: capability_driven_validation_2025_11_18
**Quality:** 14/10 (exceptional)  
**Status:** production_ready  
**Namespace:** cortex.validation.documentation  

**Tags:**
- validation
- test_driven_development
- configuration_driven
- iterative_debugging
- documentation_coverage
- yaml_driven
- production_ready

**Key Patterns (5):**
1. Test-Driven Development (0.95 confidence)
2. Iterative Debugging (0.95 confidence)
3. Configuration-Driven Design (0.92 confidence)
4. Comprehensive Gap Reporting (0.90 confidence)
5. Flexible File Matching (0.90 confidence)

**Lessons (4):**
1. Filter Early in Pipeline
2. Parameter Names Matter
3. Test Harness Reveals Truth
4. Comprehensive Tests Pay Off

**Reusable Artifacts (4):**
- `validate_documentation_coverage()` method
- `_generate_expected_docs_from_capabilities()` helper
- `_scan_existing_documentation()` helper
- `_document_exists()` flexible matcher

---

## Tips for Success

### Creating Good Conversation Captures
1. **Document the Journey:** Include the full implementation story, not just the result
2. **Capture Decisions:** Explain why you chose specific approaches
3. **Record Bugs:** Document bugs found and how they were fixed
4. **Show Evidence:** Include concrete metrics (test results, performance, code size)
5. **Extract Lessons:** Explicitly state what was learned and why it matters
6. **Tag Appropriately:** Add relevant tags for future searchability

### Writing Effective Patterns
1. **Be Specific:** "Test-Driven Development" not just "TDD"
2. **Show Confidence:** High confidence (0.90+) for proven patterns
3. **Provide Evidence:** Real numbers, test results, actual outcomes
4. **Make It Reusable:** Document methods/functions that can be copied

### Choosing Quality Scores
- **1-5:** Experimental, learning phase
- **6-8:** Good implementation, some issues
- **9-10:** Excellent, production-ready
- **11-14:** Exceptional, strategic value (rare)

### Tagging Strategy
Use tags that describe:
- **Methodology:** test_driven_development, iterative_debugging
- **Domain:** validation, configuration, documentation
- **Technology:** yaml_driven, python_based, database
- **Status:** production_ready, experimental, refactored

---

## Troubleshooting

### Import Fails with "File not found"
**Solution:** Check file path is correct and file exists
```bash
ls cortex-brain/documents/conversation-captures/your-file.md
```

### Import Succeeds but Verification Fails
**Solution:** Check pattern_id matches in both scripts
```bash
# Look for pattern_id in import output
# Use that exact ID with verify script
python scripts/verify_import.py pattern_id_from_output
```

### Search Returns No Results
**Solution:** 
1. Check knowledge graph has patterns: `python scripts/search_patterns.py --list`
2. Verify tag spelling is exact (case-sensitive)
3. Try broader search: `python scripts/search_patterns.py --search <keyword>`

### Pattern Display Shows Errors
**Solution:** Check YAML syntax in knowledge-graph.yaml
```bash
python -c "import yaml; yaml.safe_load(open('cortex-brain/tier2/knowledge-graph.yaml'))"
```

---

## Next Steps

1. **Import More Conversations:** Build your knowledge graph with strategic captures
2. **Query Before Starting:** Search patterns before tackling similar work
3. **Update Confidence:** Boost confidence scores when patterns prove useful
4. **Add New Tags:** Expand tagging vocabulary as patterns grow
5. **Create Templates:** Use successful patterns as templates for new work

---

## Technical Details

### Files
- **Knowledge Graph:** `cortex-brain/tier2/knowledge-graph.yaml`
- **Captures:** `cortex-brain/documents/conversation-captures/`
- **Scripts:** `scripts/import_conversation.py`, `verify_import.py`, `search_patterns.py`, `show_pattern.py`

### Performance
- Import: ~1 second per conversation
- Search: <100ms
- Display: <50ms
- Knowledge graph grows linearly with pattern count

### Dependencies
- Python 3.7+
- PyYAML module
- Standard library (pathlib, datetime, sys)

---

**Last Updated:** 2025-11-18  
**Version:** 1.0  
**Status:** Production-ready
