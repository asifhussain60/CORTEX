# Quick Reference: File Consolidation Tool

## One-Liner Examples

```bash
# YAML in source folder (recommended for documentation)
python consolidate.py --folder SSOT/analysis --format yaml --output-in-source

# JSON in parent directory (default location)
python consolidate.py --folder scripts --format json

# Both formats in source
python consolidate.py --folder cortex-brain --format yaml --output-in-source
python consolidate.py --folder cortex-brain --format json --output-in-source
```

## In GitHub Copilot Chat

```
@consolidate --folder SSOT/analysis --format yaml --output-in-source
```

## Essential Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `--folder` | `SSOT/analysis` | **Required** - folder to scan |
| `--format` | `yaml` or `json` | Default: `json` |
| `--output-in-source` | *(flag)* | Write output to source folder, not parent |
| `--exclude` | `*.log,*.tmp,cache/**` | Skip patterns |
| `--include` | `*.py,*.md` | Only include patterns |

## Output Schema

```
{
  metadata: { timestamp, folder, file_count, size_bytes, errors }
  files: [ { path, extension, size, content, encoding } ]
  tree: { directory_structure }
}
```

## Files

- **Tool:** `consolidate.py` (15.7 KB)
- **Prompt:** `.github/prompt/consolidate.prompt.md` (5.8 KB)
- **Setup Guide:** `CONSOLIDATE-TOOL-SETUP.md`

## Status

✅ Tested and working  
✅ Supports JSON and YAML  
✅ Recursive scanning  
✅ Error resilient  

**Last Verified:** 2026-01-14
