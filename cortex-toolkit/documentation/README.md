# CORTEX Toolkit - Documentation Tools

Documentation generation and maintenance utilities.

## Tools

### docs-generate (`cortex-docs-gen`)

**Purpose:** Generate documentation from source code.

**File:** `generate_docs_from_code.py`

**Usage:**
```bash
python cortex-toolkit/documentation/generate_docs_from_code.py
```

**Features:**
- Extract docstrings
- Generate API documentation
- Create markdown files
- Update existing docs

---

### prompts-regenerate (`cortex-prompts-regen`)

**Purpose:** Regenerate AI prompt files for GitHub Copilot.

**File:** `regenerate_prompts.py`

**Usage:**
```bash
python cortex-toolkit/documentation/regenerate_prompts.py
```

**Requires:** Admin privileges

**Features:**
- Update `.github/prompts/CORTEX.prompt.md`
- Sync with `cortex-operations.yaml`
- Update response templates
- Maintain prompt versioning

---

### quick-reference (`cortex-qr`)

**Purpose:** Generate quick reference documentation.

**File:** `generate_quick_reference.py`

**Usage:**
```bash
python cortex-toolkit/documentation/generate_quick_reference.py
```

**Features:**
- Command quick reference
- Tool catalog generation
- Usage examples
- Category summaries

---

## Output Locations

- API Docs: `docs/api/`
- Quick Reference: `cortex-brain/QUICK-REFERENCE.md`
- Prompts: `.github/prompts/`
- Module Guides: `cortex-brain/modules/`

## Workflow

1. **Generate from Code:**
   ```bash
   python cortex-toolkit/documentation/generate_docs_from_code.py
   ```

2. **Update Quick Reference:**
   ```bash
   python cortex-toolkit/documentation/generate_quick_reference.py
   ```

3. **Regenerate Prompts:**
   ```bash
   python cortex-toolkit/documentation/regenerate_prompts.py
   ```

## Best Practices

- Run doc generation after major code changes
- Regenerate prompts after operation updates
- Keep quick reference in sync with manifest
- Version control all generated docs
