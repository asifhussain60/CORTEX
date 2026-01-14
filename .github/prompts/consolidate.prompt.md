# Intelligent Folder Consolidation Prompt

**Version:** 2.0  
**Status:** EXECUTABLE via GitHub Copilot Chat  
**Purpose:** Execute intelligent recursive folder consolidation with LLM-powered content refinement

---

## Overview

This prompt coordinates execution of the enhanced `consolidate.py` tool for intelligently consolidating all folders and subfolders into separate machine-readable files. Each folder becomes a single YAML/JSON file named after the folder, with all source files deleted.

**Key Innovation**: 
- Recursively consolidates ALL folders (root + subfolders)
- Each folder → one machine-readable file (named `foldername.yaml` or `foldername.json`)
- LLM-powered intelligent content extraction and refinement
- Automatic cleanup: deletes all source files and empty folders
- Nothing lost: all content preserved in consolidated files

## How to Use

### Basic Usage (Preview without cleanup)

```bash
python consolidate.py --folder SSOT/analysis --format yaml
```

Results in:
- `SSOT/analysis/analysis.yaml` - Consolidation of root folder files
- `SSOT/analysis/reqs/reqs.yaml` - Consolidation of reqs subfolder
- All original source files preserved

### Full Consolidation with Cleanup

```bash
python consolidate.py --folder SSOT/analysis --format yaml --cleanup
```

**WARNING**: This command:
- Creates `analysis.yaml` from root folder files
- Creates `reqs.yaml` from reqs subfolder files  
- **Deletes ALL source files** in both folders
- **Deletes empty folders** created after file cleanup
- Requires user confirmation before executing

## Parameters

### Required
- `--folder` (or `-f`): Root directory to consolidate (required)

### Optional
- `--format`: Output format `json` or `yaml` (default: `yaml`)
- `--cleanup` (or `-c`): Delete source files and empty folders after consolidation (requires confirmation)

## Tool Execution Details

### Tool Location
```
.github/prompts/tools/consolidate.py
```

### Command Syntax
```bash
cd D:\PROJECTS\CORTEX

# Preview consolidation (no cleanup)
python .github/prompts/tools/consolidate.py --folder SSOT/analysis --format yaml

# Full consolidation with source cleanup
python .github/prompts/tools/consolidate.py --folder SSOT/analysis --format yaml --cleanup
```

## How It Works

### Phase 1: Recursive Discovery
1. Identifies root folder and all subfolders
2. For each folder, collects all files (not subdirectories)
3. Skips hidden folders (starting with `.`)

### Phase 2: Intelligent Content Extraction
For each file, extracts:
- **Markdown** (`.md`): Headers with nesting levels, structure
- **Code** (`.py`, `.js`, `.ts`, `.java`, etc.): Classes, functions, imports
- **JSON/YAML**: Keys, validation, structure
- **Text**: Key terms, important concepts
- **Binary**: Base64 encoding with metadata

### Phase 3: Consolidation
Creates unified machine-readable file for each folder with:
- **Metadata**: Timestamp, folder name, file count, file types, errors
- **Files**: Complete content + extracted intelligence
- **Relationships**: Preserves which files came from which folder

### Phase 4: Cleanup (Optional)
When `--cleanup` flag is used:
1. **User confirmation** required (IRREVERSIBLE warning)
2. **Delete source files** from each folder
3. **Delete empty folders** (after files removed)
4. **Keep consolidation files** (`.yaml` or `.json`)

## Output Structure

### Folder Layout After Consolidation (with --cleanup)
```
SSOT/
└── analysis/
    ├── analysis.yaml          ← Root folder consolidation
    └── reqs/
        └── reqs.yaml          ← Reqs subfolder consolidation
```

All original source files deleted. Only `.yaml` files remain.

### File Structure Inside Consolidation File
```yaml
metadata:
  consolidation_timestamp: "2026-01-14T10:30:00"
  source_folder: "/path/to/folder"
  folder_name: "analysis"
  total_files: 15
  total_size_bytes: 124500
  file_type_summary:
    .md: 8
    .py: 4
    .txt: 3
  extraction_enabled: true
  errors: []

files:
  - filename: "README.md"
    size_bytes: 5000
    modified_time: "2026-01-14T09:00:00"
    extension: ".md"
    is_binary: false
    content: "# Content of file..."
    intelligence:
      structure: "markdown"
      key_sections:
        - level: 1
          text: "Main Title"
        - level: 2
          text: "Section"
      key_terms: ["CORTEX", "consolidation", "analysis"]
      
  - filename: "script.py"
    extension: ".py"
    is_binary: false
    content: "# Python code..."
    intelligence:
      structure: "code"
      language: "py"
      has_classes: true
      has_functions: true
      has_imports: true
```

## Use Cases

### Case 1: Preview Consolidation Structure
Before committing to cleanup, preview what will happen:
```bash
python consolidate.py --folder SSOT/analysis --format yaml
```
- Generates `analysis.yaml` and `reqs.yaml`
- All source files preserved
- Shows what consolidation will look like

### Case 2: Full Consolidation with Cleanup
Convert folder hierarchy into machine-readable files:
```bash
python consolidate.py --folder SSOT/analysis --format yaml --cleanup
```
- Creates consolidated files
- Deletes all source files
- Removes empty folders
- Result: Only `.yaml` files remain

### Case 3: JSON Format (for programmatic processing)
```bash
python consolidate.py --folder SSOT/analysis --format json --cleanup
```
- Same behavior as YAML
- Output format: `.json` instead of `.yaml`
- Better for programmatic parsing

## Safety Features

✅ **Disabled by default**: Cleanup requires explicit `--cleanup` flag  
✅ **User confirmation**: Warning shown before destructive operation  
✅ **Atomic operations**: Files only deleted after consolidation succeeds  
✅ **Error logging**: All failures tracked and reported  
✅ **Reversibility check**: Consolidation file must exist before cleanup  
✅ **Folder safety**: Only deletes empty folders created by file cleanup

## Key Features

✅ **Recursive**: Consolidates all folder levels independently  
✅ **Intelligent**: Extracts structure, headers, code patterns, key terms  
✅ **Safe**: Confirmation required, errors tracked, atomic operations  
✅ **Clean**: Deletes source files leaving only machine files  
✅ **Flexible**: Supports both YAML and JSON formats  
✅ **Complete**: No content lost - all text preserved + extracted intelligence  
✅ **Machine-Ready**: Structured format suitable for LLM processing  

## Intelligence Extraction Details

### Markdown Files
Extracts:
- Document headers and hierarchy (with levels 1-6)
- Structure and outline
- Key terms and concepts

### Code Files (Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby, PHP)
Detects:
- Language type
- Presence of classes and functions
- Import statements
- Code structure

### JSON/YAML Files
Validates:
- Format correctness
- Top-level keys
- Data structure

### All Text Files
Extracts:
- Quoted phrases
- Uppercase terms (likely constants/concepts)
- Key terminology (limited to 20 unique terms)

## Error Handling

- **Non-fatal errors**: Logged in `metadata.errors` array
- **Unreadable files**: Reported with file name and reason
- **Processing continues**: Consolidation succeeds even if some files fail
- **Encoding fallback**: Binary files stored as base64 if text reading fails

## Acceptance Criteria

✅ Each folder consolidated into single file named `foldername.yaml` or `foldername.json`  
✅ Recursive: All folder levels processed independently  
✅ Metadata: Consolidation timestamp, file counts, types, errors  
✅ Content: All file content preserved with full fidelity  
✅ Intelligence: Markdown structure, code patterns, key terms extracted  
✅ Cleanup: Source files and empty folders deleted when `--cleanup` used  
✅ Safety: User confirmation required for destructive operations  
✅ Idempotent: Can run multiple times with consistent results  

## Examples

### Example 1: SSOT/analysis Consolidation
```bash
cd D:\PROJECTS\CORTEX
python .github/prompts/tools/consolidate.py --folder SSOT/analysis --format yaml
```

Creates:
- `SSOT/analysis/analysis.yaml` (~200 KB with all root files)
- `SSOT/analysis/reqs/reqs.yaml` (~150 KB with all reqs files)

All files readable. No cleanup yet.

### Example 2: Full Pipeline with Cleanup
```bash
cd D:\PROJECTS\CORTEX
python .github/prompts/tools/consolidate.py --folder SSOT/analysis --format yaml --cleanup
```

Prompts:
```
⚠️  WARNING
All source files and empty folders will be DELETED
This operation is IRREVERSIBLE

Remaining files: Only consolidated machine files (*.yaml or *.json)
Continue? (yes/no): 
```

If user confirms with `yes`:
1. Creates `analysis.yaml` from root files
2. Creates `reqs.yaml` from reqs files
3. Deletes all source files in both folders
4. Deletes empty subfolders
5. Result: Only `.yaml` files remain

### Example 3: JSON Format
```bash
python consolidate.py --folder SSOT/analysis --format json --cleanup
```

Same as YAML but output is `.json` files instead of `.yaml`.

## Notes

- The tool is **idempotent**: Running it multiple times produces consistent results
- Already-consolidated files (`.yaml` or `.json`) are preserved during cleanup
- Large files are included in full (no truncation or compression)
- Binary files are stored as base64 (increases size ~33%)
- YAML is human-readable, suitable for documentation
- JSON is suitable for programmatic processing and API integration
- Cleanup is **IRREVERSIBLE** - always backup before using `--cleanup`

## Troubleshooting

### Q: I want to test cleanup without actually deleting
A: Run without `--cleanup` flag first to generate consolidation files. Review them, then run with `--cleanup`.

### Q: Can I undo a cleanup?
A: No, cleanup is destructive. The only recovery is from backups. Always backup before running with `--cleanup`.

### Q: What if consolidation fails?
A: Cleanup only runs if consolidation succeeds. Check error messages in consolidation file metadata.

### Q: How do I run it programmatically?
A: Use the Python API:
```python
from pathlib import Path
from consolidate import RecursiveConsolidator

consolidator = RecursiveConsolidator(
    Path("SSOT/analysis"),
    output_format="yaml",
    cleanup=False  # Set to True for cleanup
)
results = consolidator.consolidate_all()
consolidator.print_summary()
```

## Related Files

- **Tool**: `.github/prompts/tools/consolidate.py` (v2.0 with recursive consolidation and cleanup)
- **Prompt**: `.github/prompts/consolidate.prompt.md` (this file)

## Version History

**v2.0** (Current - Recursive Consolidation)
- ✅ Recursive folder consolidation
- ✅ Each folder → single machine file
- ✅ LLM-powered content refinement
- ✅ Safe source cleanup with confirmation
- ✅ Empty folder deletion
- ✅ Intelligence extraction (Markdown, code, data)

**v1.0** (Previous - Single Folder)
- Basic folder consolidation
- Output to parent directory
- Simple file discovery

---

**Status**: Ready for use  
**Date**: 2026-01-14  
**Test**: Run with `--folder SSOT/analysis --format yaml` to preview
