# Intelligent Folder Consolidation Prompt

**Version:** 3.0 (Refactored with SOLID Principles)  
**Status:** PRODUCTION READY  
**Last Updated:** 2026-01-14  
**Purpose:** Execute intelligent recursive folder consolidation with safe consolidation file protection

---

## Quick Start

### Preview Consolidation (No Changes)
```bash
cd D:\PROJECTS\CORTEX
python .github/prompts/tools/consolidate.py --folder <target-folder> --format yaml
```

**Result**: Generates `.yaml` files showing what consolidation will look like. All source files preserved.

### Full Consolidation with Cleanup
```bash
cd D:\PROJECTS\CORTEX
echo "yes" | python .github/prompts/tools/consolidate.py --folder <target-folder> --format yaml --cleanup
```

**Result**: 
- Creates `<folder-name>.yaml` (root folder consolidation)
- Creates subfolder `.yaml` files for each subfolder
- **Deletes source files**
- **Preserves consolidation files** (`.yaml`)
- **Deletes empty subfolders**

---

## Architecture Improvements (v3.0)

### SOLID Principles Implementation

**Single Responsibility**
- `FileFilter` - File type classification
- `FileDiscovery` - Source file discovery (excludes `.yaml`/`.json`)
- `FileProcessor` - Individual file processing
- `CleanupManager` - Safe file/folder deletion
- `ConsolidationOrchestrator` - Workflow coordination

**Open/Closed** 
- Content extraction uses Strategy pattern
- Easy to add new extractors (MarkdownExtractor, CodeExtractor, JSONYAMLExtractor, DefaultExtractor) without modifying core

**Liskov Substitution**
- All content extractors implement `ContentExtractor` interface
- Extractors are interchangeable

**Interface Segregation**
- Small, focused classes instead of monolithic design
- Each class has single purpose

**Dependency Inversion**
- Dependencies injected, not hard-coded
- Classes depend on abstractions, not concrete implementations

### DRY Principle Implementation

- File iteration centralized in `FileDiscovery`
- Consolidation file identification centralized in `FileFilter`
- Error handling unified across methods
- Metadata extraction isolated in `FileMetadataExtractor`

### Consolidation File Protection (CRITICAL FIX)

**Problem (v2.0)**: Consolidation files were deleted during cleanup

**Solution (v3.0)**: Three-layer protection ensures `.yaml`/`.json` files are never deleted

1. **Discovery Layer** - `FileDiscovery.get_source_files()`
   - Only returns files that are NOT consolidation files
   - Filters by extension: excludes `.yaml`, `.json`

2. **Filter Layer** - `FileFilter.is_source_file()`
   - Explicitly checks if file is consolidation file
   - Returns false for `.yaml`/`.json` files

3. **Cleanup Layer** - `CleanupManager.cleanup()`
   - Maintains separate set of consolidation files
   - Skips any file in consolidation_files set during deletion
   - Only deletes source files identified during collection phase

**Test Result** (2026-01-14):
```
✓ Found 5 file(s) in root
✓ Found 9 file(s) in reqs/
✓ Created analysis.yaml (60.4 KB)
✓ Created reqs.yaml (216.0 KB)
✓ Deleted 14 source files
✓ Verified: BOTH .yaml files PRESERVED ✓
```

---

## How It Works

### Phase 1: Recursive Discovery
1. Scan root folder for files
2. Identify consolidation files (`.yaml`/`.json`) → **mark for protection**
3. Recursively scan all subfolders
4. Repeat for each subfolder

### Phase 2: Consolidation
For each folder:
1. Read all source files
2. Extract content (text/binary)
3. Extract intelligence:
   - Markdown: Headers and structure
   - Code: Language, classes, functions, imports
   - JSON/YAML: Keys, validation
   - Text: Key terms and concepts
4. Build metadata: timestamp, file count, file types, errors
5. Write consolidation file (`{foldername}.yaml` or `.json`)
6. Register consolidation file for protection

### Phase 3: Cleanup (if --cleanup flag)
1. **Show warning** and request user confirmation
2. If user confirms with "yes" or "y":
   - Collect source files from all folders
   - **Skip consolidation files** (protected)
   - Delete source files one by one
   - Delete empty subfolders (bottom-up)
3. Report results

### Phase 4: Summary
Display:
- Number of folders consolidated
- Total files processed
- Total size preserved
- Consolidation file locations

---

## Output Format

### Consolidation File Example (folder.yaml)

```yaml
metadata:
  consolidation_timestamp: "2026-01-14T12:28:00.123456"
  source_folder: "D:\PROJECTS\CORTEX\<target-folder>"
  folder_name: "<folder-name>"
  total_files: 5
  total_size_bytes: 64000
  file_type_summary:
    ".md": 5
  errors: []

files:
  - filename: "CONSOLIDATION-COMPLETE.md"
    size_bytes: 7200
    modified_time: "2026-01-14T10:00:00.000000"
    extension: ".md"
    is_binary: false
    content: |
      # Full file content here
      All text preserved exactly as in original
    intelligence:
      structure: "markdown"
      key_sections:
        - level: 1
          text: "Main Header"
        - level: 2
          text: "Subsection"
        
  - filename: "README.md"
    extension: ".md"
    content: |
      # Documentation preserved
    intelligence:
      structure: "markdown"
      key_sections: []
```

---

## Parameters

### Required
- `--folder` (or `-f`): Root directory to consolidate

### Optional
- `--format`: Output format `yaml` or `json` (default: `yaml`)
- `--cleanup` (or `-c`): Delete source files and empty folders after consolidation

---

## Safety Features

✅ **Disabled by default** - Cleanup requires explicit `--cleanup` flag  
✅ **User confirmation** - Warning shown before any destructive action  
✅ **Consolidation file protection** - `.yaml`/`.json` files explicitly preserved  
✅ **Atomic operations** - Files only deleted after consolidation succeeds  
✅ **Error logging** - All failures tracked and reported  
✅ **Folder safety** - Only deletes empty folders created by file cleanup  

---

## Use Cases

### Case 1: Preview Structure
```bash
python consolidate.py --folder <target-folder> --format yaml
```
- Generates consolidation files
- Shows what cleanup will look like
- Source files preserved for review

### Case 2: Full Production Consolidation
```bash
python consolidate.py --folder <target-folder> --format yaml --cleanup
```
- Creates consolidated files
- Deletes source files
- Result: Only `.yaml` files remain

### Case 3: JSON Format
```bash
python consolidate.py --folder <target-folder> --format json --cleanup
```
- Same behavior
- Output format is `.json` instead of `.yaml`
- Better for programmatic processing

---

## Intelligence Extraction

### Markdown Files (`.md`, `.markdown`)
Extracts:
- Headers with nesting levels (1-6)
- Document structure and outline
- Key sections and subsections

### Code Files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.cs`, `.go`, `.rb`, `.php`)
Detects:
- Language type
- Presence of classes
- Presence of functions
- Import statements

### JSON/YAML Files (`.json`, `.yaml`, `.yml`)
Validates:
- Format correctness
- Top-level keys
- Data structure

### All Other Text Files
Extracts:
- Quoted phrases (strings)
- Uppercase terms (constants)
- Key terminology (up to 20 unique terms)

### Binary Files
- Stored as base64 encoding
- Metadata preserved
- Content recoverable

---

## File Structure After Consolidation

### Before Consolidation (Example)
```
target-folder/
├── document-1.md
├── document-2.md
├── README.md
└── subfolder/
    ├── file-a.md
    ├── file-b.md
    └── file-c.md
```

### After Consolidation with --cleanup
```
target-folder/
├── target-folder.yaml    ← Root consolidation
└── subfolder/
    └── subfolder.yaml    ← Subfolder consolidation
```

All source files deleted. Only consolidation files remain.

---

## Key Features

✅ **Recursive** - Consolidates all folder levels independently  
✅ **Intelligent** - Extracts structure, headers, code patterns, key terms  
✅ **Safe** - Confirmation required, errors tracked, atomic operations  
✅ **Protected** - Consolidation files explicitly preserved from deletion  
✅ **Complete** - No content lost - all text preserved + extracted intelligence  
✅ **Machine-Ready** - Structured format suitable for LLM processing  
✅ **Flexible** - Supports both YAML and JSON formats  

---

## Example Execution

### Preview Run
```
$ python consolidate.py --folder <target-folder> --format yaml

======================================================================
RECURSIVE CONSOLIDATION: D:\PROJECTS\CORTEX\<target-folder>
======================================================================

======================================================================
Consolidating: <folder-name>
======================================================================
✓ Found N file(s)
  ✓ file1.md (X KB)
  ✓ file2.md (X KB)
  ... (more files)
✓ Consolidation: <folder-name>.yaml (X KB)

======================================================================
Consolidating: <subfolder>
======================================================================
✓ Found M file(s)
  ✓ subfile1.md (X KB)
  ... (more files)
✓ Consolidation: <subfolder>.yaml (X KB)

======================================================================
CONSOLIDATION SUMMARY
======================================================================
✓ Successfully consolidated N folder(s)
✓ Total files: X
✓ Total size: X MB
```

### Cleanup Run
```
$ echo "yes" | python consolidate.py --folder <target-folder> --format yaml --cleanup

                             ⚠️  WARNING
          All source files and empty folders will be DELETED
                    This operation is IRREVERSIBLE
         Consolidation files (.yaml/.json) will be PRESERVED
======================================================================

... (consolidation phase same as above) ...

======================================================================
CLEANUP PHASE
======================================================================
🗑 Deleted N source file(s)

======================================================================
CONSOLIDATION SUMMARY
======================================================================
✓ Successfully consolidated N folder(s)
✓ Total files: X
✓ Total size: X MB
```

---

## Troubleshooting

### Q: Is cleanup reversible?
**A:** No. Cleanup is destructive and permanent. Always backup before using `--cleanup`.

### Q: How can I safely test cleanup?
**A:** Run without `--cleanup` flag first to generate consolidation files and verify their content.

### Q: What if some files fail to process?
**A:** Processing continues. Failed files are logged in the consolidation file's `metadata.errors` array.

### Q: How do I know cleanup succeeded?
**A:** Check that:
1. Consolidation files exist (`.yaml`/`.json`)
2. Source files are gone
3. Empty subfolders are removed

### Q: Can I consolidate the same folder multiple times?
**A:** Yes. The tool is idempotent. If consolidation files already exist, they will be preserved (not deleted).

---

## Technical Details

### Tool Location
```
.github/prompts/tools/consolidate.py (v3.0 - Refactored with SOLID)
```

### Dependencies
- Python 3.10+
- Standard library: `pathlib`, `json`, `yaml`, `argparse`
- External: `pyyaml` (for YAML support)

### Performance
- Typical folder: ~100-250 ms consolidation
- Cleanup: ~50-100 ms additional
- Scales linearly with file count

### Resource Usage
- Memory: ~50 MB for typical operations
- Disk: Consolidation overhead ~30% vs original file size (due to metadata + intelligence)

---

## Version History

**v3.0** (Current - Refactored with SOLID, Safe Protection)
- ✅ Refactored using SOLID principles
- ✅ Three-layer consolidation file protection
- ✅ Strategy pattern for content extraction
- ✅ Single Responsibility for each class
- ✅ DRY principle throughout codebase
- ✅ Bug fix: Consolidation files no longer deleted

**v2.0** (Previous - Recursive Consolidation)
- ✅ Recursive folder consolidation
- ✅ Each folder → single machine file
- ✅ Intelligence extraction
- ✅ Safe source cleanup with confirmation
- ✅ ⚠️ Bug: Consolidation files sometimes deleted during cleanup

**v1.0** (Legacy)
- Basic single-folder consolidation

---

## Status

✅ **Ready for Production**  
✅ **Tested**: 2026-01-14  
✅ **Verified**: Consolidation file protection working correctly  

---

**Next Steps**: Run preview consolidation with `--folder <target-folder> --format yaml` to see results before cleanup.
