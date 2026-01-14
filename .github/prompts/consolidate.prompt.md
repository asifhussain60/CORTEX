# File Consolidation Prompt

**Version:** 1.0  
**Status:** EXECUTABLE via GitHub Copilot Chat  
**Purpose:** Execute folder consolidation using the canonical `consolidate.py` CLI tool

---

## Overview

This prompt coordinates execution of the `consolidate.py` tool for consolidating folder contents into structured machine-readable formats (JSON/YAML). The tool is the single source of truth for all consolidation operations.

## How to Use in GitHub Copilot Chat

### Basic Usage

```
@consolidate --folder <path> --format json
@consolidate --folder <path> --format yaml --output-in-source
@consolidate --folder <path> --format json --output-in-source
```

### Examples

**Consolidate SSOT/analysis with YAML in source folder:**
```
@consolidate --folder SSOT/analysis --format yaml --output-in-source
```

**Consolidate with JSON (default):**
```
@consolidate --folder scripts --format json
```

**Consolidate with custom excludes:**
```
@consolidate --folder cortex-brain --exclude "*.log,*.tmp,cache/**" --format yaml
```

## Parameters

- `--folder` (required): Root directory to scan and consolidate
- `--format` (optional): Output format `json` or `yaml` (default: `json`)
- `--output-in-source` (optional): Write output to source folder instead of parent directory
- `--exclude` (optional): Comma-separated glob patterns to skip
- `--include` (optional): Comma-separated glob patterns to include exclusively

## Tool Execution Details

### Tool Location
```
.github/prompts/tools/consolidate.py
```

### Command Syntax
```bash
cd D:\PROJECTS\CORTEX
python .github/prompts/tools/consolidate.py --folder <path> [--format json|yaml] [--output-in-source] [--exclude PATTERNS] [--include PATTERNS]
```

### What the Tool Does

#### Validation Phase
- Verify folder exists and is accessible
- Validate output format is supported
- Check write permissions for output destination

#### Discovery Phase
- Walk directory tree recursively
- Apply include/exclude patterns to file paths
- Collect metadata: file path, size, extension, modification time

#### Read Phase
- Read all text files with UTF-8 encoding
- Fall back to base64 encoding for binary files
- Track read success/failure with error context

#### Consolidation Phase
- Structure data with metadata wrapper
- Preserve file hierarchy relationships
- Generate summary statistics

#### Output Phase
- Serialize to specified format (JSON or YAML)
- Write to designated location (source folder with `--output-in-source`, parent directory by default)
- Validate output integrity

## Output Schema

### Structure
```json
{
  "metadata": {
    "consolidation_timestamp": "ISO-8601",
    "source_folder": "path",
    "total_files": number,
    "total_size_bytes": number,
    "file_type_summary": { "extension": count },
    "errors": [ { "file": "path", "error_type": "string", "message": "string" } ]
  },
  "files": [
    {
      "path": "relative/path/file.ext",
      "extension": ".ext",
      "size_bytes": number,
      "modified_time": "ISO-8601",
      "is_binary": boolean,
      "content": "string or base64",
      "encoding": "utf8 or base64"
    }
  ],
  "tree": {
    "directory_structure": { ... }
  }
}
```

## Error Handling

- Non-fatal errors are logged in the `errors` array in metadata
- Unreadable files are reported with reason (permissions, encoding, size)
- Processing continues even if individual files fail to read
- Summary of all failures included in final output

## Key Features

✅ **Parameterized** - Works with any folder path  
✅ **Format Flexible** - Outputs JSON or YAML  
✅ **Location Flexible** - Output to source or parent directory  
✅ **Recursive** - Scans entire directory tree  
✅ **Error Resilient** - Continues on file read failures  
✅ **Metadata Rich** - Captures file details, timestamps, encodings  
✅ **Binary Safe** - Handles text and binary files with base64 fallback  

## Integration Examples

### Manual Execution
```bash
cd D:\PROJECTS\CORTEX
python .github/prompts/tools/consolidate.py --folder SSOT/analysis --format yaml --output-in-source
```

### In Python Scripts
```python
from pathlib import Path
import sys
sys.path.insert(0, "D:\\PROJECTS\\CORTEX\\.github\\prompts\\tools")
from consolidate import FileConsolidator

consolidator = FileConsolidator(
    folder_path="SSOT/analysis",
    output_format="yaml",
    output_in_source=True
)
success, output_file = consolidator.run()
```

### In Automation/CI
```yaml
- name: Consolidate folder
  run: |
    cd ${{ github.workspace }}
    python .github/prompts/tools/consolidate.py \
      --folder ${{ inputs.folder }} \
      --format ${{ inputs.format }} \
      --output-in-source
```

## Acceptance Criteria

✅ Single YAML file in source folder (with `--format yaml --output-in-source`)  
✅ Recursive scanning of all nested directories  
✅ Metadata wrapper with consolidation timestamp, file counts, type summary  
✅ File hierarchy preservation in `tree` section  
✅ Proper error reporting for unreadable files  
✅ Support for custom exclude/include patterns  
✅ Support for both JSON and YAML output formats  

## Notes

- The tool is idempotent - running it multiple times produces consistent results
- Default excludes prevent inclusion of cache, venv, node_modules, .git, and log files
- Large files are included in full (no truncation)
- File ownership and permissions are not preserved in consolidated output (metadata only)
- YAML output is human-readable and suitable for documentation
- JSON output is suitable for programmatic processing

## Default Exclude Patterns

```
**/.git/**
**/__pycache__/**
**/*.pyc
**/node_modules/**
**/.venv/**
**/*.log
```

These are automatically applied unless overridden with `--exclude`

## Related Files

- **Tool:** `.github/prompts/tools/consolidate.py`
- **Setup Guide:** `.github/prompts/tools/CONSOLIDATE-TOOL-SETUP.md`
- **Quick Reference:** `.github/prompts/tools/CONSOLIDATE-QUICK-REF.md`
