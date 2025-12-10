# Intelligent Regeneration System - Implementation Guide

**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**  
**Version:** 1.0.0 | **Created:** December 10, 2025

---

## 🎯 Overview

The Intelligent Regeneration System enables incremental document/image/diagram regeneration by tracking content hashes. Only regenerates files when source content or dependencies actually change, providing 90%+ time savings on repeat runs.

## 🏗️ Architecture

### Components

1. **RegenerationTracker** (`src/operations/utilities/regeneration_tracker.py`)
   - SHA256 content hashing
   - Dependency tracking
   - Manifest persistence
   - Statistics collection

2. **Regeneration Manifest** (`cortex-brain/metadata/regeneration-manifest.yaml`)
   - Tracks source and output hashes
   - Records dependencies
   - Stores statistics
   - Survives git operations

3. **CLI Integration** (`scripts/cli_wrappers/regenerate_prompts_wrapper.py`)
   - `--incremental` flag (default)
   - `--force` flag (full regeneration)
   - `--dry-run` flag (preview)

### Data Flow

```
User Command
    ↓
CLI Wrapper
    ↓
RegenerationTracker.should_regenerate()
    ├─→ Check manifest for tracked data
    ├─→ Compute current source hash
    ├─→ Compare with tracked hash
    └─→ Return (regenerate: bool, reason: str)
    ↓
If regenerate == False: Skip file
If regenerate == True: Regenerate file
    ↓
RegenerationTracker.mark_regenerated()
    ├─→ Compute new hashes
    ├─→ Update manifest
    └─→ Record statistics
    ↓
RegenerationTracker.finalize()
    ├─→ Calculate time saved
    ├─→ Save manifest
    └─→ Return summary
```

## 📋 Usage

### Basic Usage

```python
from src.operations.utilities.regeneration_tracker import RegenerationTracker

tracker = RegenerationTracker()

# Check if file needs regeneration
should_regen, reason = tracker.should_regenerate(
    output_file=".github/copilot-instructions.md",
    source_dependencies=[
        "cortex-brain/response-templates.yaml",
        "cortex-brain/brain-protection-rules.yaml",
        "scripts/regenerate_cortex_prompts.py"
    ]
)

if should_regen:
    print(f"Regenerating: {reason}")
    regenerate_file()
    
    # Mark as regenerated
    tracker.mark_regenerated(
        output_file=".github/copilot-instructions.md",
        source_dependencies=[
            "cortex-brain/response-templates.yaml",
            "cortex-brain/brain-protection-rules.yaml",
            "scripts/regenerate_cortex_prompts.py"
        ]
    )
else:
    print(f"Skipping: {reason}")

# Finalize and get stats
stats = tracker.finalize()
print(f"Time saved: {stats['time_saved']:.1f}s")
```

### CLI Usage

```bash
# Default: Incremental regeneration
python scripts/cli_wrappers/regenerate_prompts_wrapper.py

# Explicit incremental
python scripts/cli_wrappers/regenerate_prompts_wrapper.py --incremental

# Force full regeneration
python scripts/cli_wrappers/regenerate_prompts_wrapper.py --force

# Preview changes
python scripts/cli_wrappers/regenerate_prompts_wrapper.py --dry-run

# Copilot Chat
"regenerate prompts"
"regenerate prompts force"
```

## 🔍 How It Works

### Change Detection Logic

1. **First Run:**
   - Manifest empty
   - All files marked for regeneration
   - Hashes computed and stored

2. **Subsequent Runs:**
   - Load manifest
   - For each file:
     - Compute current source hash
     - Compare with stored source hash
     - If different → regenerate
     - If same → skip

3. **Force Mode:**
   - Clear manifest
   - Regenerate all files
   - Recompute all hashes

### Hash Computation

```python
def compute_file_hash(file_path):
    """SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def compute_combined_hash(file_paths):
    """Combined hash of multiple files."""
    combined = "".join([compute_file_hash(p) for p in file_paths])
    return hashlib.sha256(combined.encode()).hexdigest()
```

### Dependency Tracking

Files can declare dependencies that affect regeneration:

```python
files_to_check = [
    {
        'output': '.github/copilot-instructions.md',
        'dependencies': [
            'cortex-brain/response-templates.yaml',  # Data source
            'cortex-brain/brain-protection-rules.yaml',  # Data source
            'scripts/regenerate_cortex_prompts.py'  # Generator script
        ]
    }
]
```

If ANY dependency changes, file is regenerated.

## 📊 Manifest Schema

```yaml
version: "1.0.0"
last_updated: "2025-12-10T10:30:00Z"

documents:
  ".github/copilot-instructions.md":
    source_hash: "abc123..."         # SHA256 of source templates/data
    generated_hash: "def456..."      # SHA256 of generated file
    last_regenerated: "2025-12-10T10:30:00Z"
    dependencies:
      - "cortex-brain/response-templates.yaml"
      - "cortex-brain/brain-protection-rules.yaml"

images:
  "docs/story/illustrations/00-basement.png":
    prompt_hash: "ghi789..."
    image_hash: "jkl012..."
    generation_params:
      model: "dall-e-3"
      size: "1024x1024"
    last_regenerated: "2025-12-10T10:35:00Z"

diagrams:
  "docs/architecture/system-overview.mmd":
    source_hash: "mno345..."
    generated_hash: "pqr678..."
    last_regenerated: "2025-12-10T10:40:00Z"

statistics:
  total_regenerations: 42
  last_full_regeneration: "2025-12-01T08:00:00Z"
  last_incremental_regeneration: "2025-12-10T10:30:00Z"
  files_skipped_last_run: 8
  time_saved_seconds: 240.0
```

## 🚀 Extending the System

### Adding New File Types

1. **Update Manifest Schema:**
   ```yaml
   # cortex-brain/metadata/regeneration-manifest.yaml
   new_category:
     # Files of new type
   ```

2. **Use Tracker API:**
   ```python
   should_regen, reason = tracker.should_regenerate(
       output_file="path/to/output.ext",
       source_dependencies=["source1.yaml", "source2.py"],
       category="new_category"  # Specify category
   )
   
   if should_regen:
       regenerate_new_type()
       tracker.mark_regenerated(
           output_file="path/to/output.ext",
           source_dependencies=["source1.yaml", "source2.py"],
           category="new_category",
           additional_metadata={"custom_key": "value"}
       )
   ```

### Adding to Other Regeneration Scripts

1. **Import Tracker:**
   ```python
   from src.operations.utilities.regeneration_tracker import RegenerationTracker
   ```

2. **Initialize:**
   ```python
   tracker = RegenerationTracker()
   ```

3. **Check Before Regenerating:**
   ```python
   for file in files_to_process:
       should_regen, reason = tracker.should_regenerate(
           file['output'],
           file['dependencies'],
           category='diagrams'
       )
       
       if should_regen:
           regenerate(file)
           tracker.mark_regenerated(
               file['output'],
               file['dependencies'],
               category='diagrams'
           )
   ```

4. **Finalize:**
   ```python
   stats = tracker.finalize()
   print(f"Processed: {stats['files_processed']}, Skipped: {stats['files_skipped']}")
   ```

## 📈 Performance Metrics

### Expected Performance

| Metric | First Run | Subsequent (No Changes) | Subsequent (1 Change) |
|--------|-----------|-------------------------|----------------------|
| Files Processed | 10 | 0 | 1 |
| Files Skipped | 0 | 10 | 9 |
| Time | 20s | 0.5s | 2.5s |
| Time Saved | 0s | 19.5s | 17.5s |

### Real-World Savings

- **Prompt Regeneration:** 2 files, 4-6 seconds per file
  - Without tracking: 10s every run
  - With tracking: 0.5s if no changes (90% savings)

- **Diagram Regeneration:** 20 diagrams, 5 seconds per diagram
  - Without tracking: 100s every run
  - With tracking: 5s if 1 changed (95% savings)

## 🔧 Troubleshooting

### Manifest Corruption

If manifest becomes corrupted:

```bash
# Force regeneration to rebuild manifest
python scripts/cli_wrappers/regenerate_prompts_wrapper.py --force
```

Or manually delete:
```bash
rm cortex-brain/metadata/regeneration-manifest.yaml
```

### False Positives (Unnecessary Regeneration)

Caused by:
- Manual file edits (changes `generated_hash`)
- Git operations changing timestamps
- Line ending differences

Solution: Use `--dry-run` to preview changes before regenerating.

### False Negatives (Missed Changes)

Caused by:
- Missing dependencies in tracking config
- External file changes not tracked

Solution: Add all source dependencies to `dependencies` list.

## 🎯 Best Practices

1. **Declare All Dependencies:**
   - Include templates, configs, generator scripts
   - Include data sources (YAML, JSON)
   - Don't include CORTEX core files unless they affect output

2. **Use Appropriate Categories:**
   - `documents`: Markdown, text files
   - `images`: PNG, JPG, SVG
   - `diagrams`: Mermaid, PlantUML, D2

3. **Run Incremental by Default:**
   - Use `--force` only when needed
   - Use `--dry-run` to preview changes

4. **Monitor Statistics:**
   - Check time saved in output
   - Review `files_skipped` to ensure tracking works

5. **Test After Changes:**
   - Run once with `--force` to establish baseline
   - Run again to verify skipping works
   - Modify dependency and verify regeneration triggers

## 🔍 Example Output

### Incremental Run (No Changes)

```
⚡ Incremental mode: Only regenerating changed files
  ⏭️  Skipping: .github/copilot-instructions.md
    Reason: No changes detected
  ⏭️  Skipping: .github/prompts/CORTEX.prompt.md
    Reason: No changes detected

No files need regeneration - all up to date!

📊 Regeneration Statistics:
  Files regenerated: 0
  Files skipped: 2
  Time saved: ~4.0 seconds
```

### Incremental Run (1 Change)

```
⚡ Incremental mode: Only regenerating changed files
  ✓ Will regenerate: .github/copilot-instructions.md
    Reason: Source dependencies changed
  ⏭️  Skipping: .github/prompts/CORTEX.prompt.md
    Reason: No changes detected

📝 Regenerating 1 file(s)...
[... regeneration output ...]

📊 Regeneration Statistics:
  Files regenerated: 1
  Files skipped: 1
  Time saved: ~2.0 seconds
```

### Force Run

```
🔥 Force mode: Regenerating all files

📝 Regenerating 2 file(s)...
[... regeneration output ...]

📊 Regeneration Statistics:
  Files regenerated: 2
  Files skipped: 0
  Time saved: ~0.0 seconds
```

## 📚 Related Documentation

- **Regeneration Tracker API:** `src/operations/utilities/regeneration_tracker.py`
- **Manifest Schema:** `cortex-brain/metadata/regeneration-manifest.yaml`
- **CLI Wrapper:** `scripts/cli_wrappers/regenerate_prompts_wrapper.py`
- **Operations Config:** `cortex-operations.yaml` (regenerate_prompts)

---

**Questions?** Refer to inline documentation in `regeneration_tracker.py` or run with `--help`.
