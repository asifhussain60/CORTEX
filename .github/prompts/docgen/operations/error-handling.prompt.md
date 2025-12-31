# ⚠️ Error Handling & Recovery

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Define exit codes and recovery procedures

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Stale diagrams found (warning) |
| 2 | Invalid arguments |
| 3 | Project root not found |
| 4 | Permission denied |
| 5 | Git not available (non-fatal) |

---

## Recovery Procedures

### Corrupted Manifest

```bash
# Restore from backup
cp cortex-brain/documents/docgen-manifest.json.bak.* cortex-brain/documents/docgen-manifest.json

# Or regenerate from scratch
python3 cortex-toolkit/documentation/docgen_discovery.py --force
```

### Failed Mid-Execution

```bash
# Check for temp files
ls -la cortex-brain/documents/*.tmp

# Remove stale temps
rm -f cortex-brain/documents/*.tmp
```

### Missing Governance File

```bash
# Regenerate from index.html
python cortex-toolkit/documentation/governance_validator.py --index docs/index.html

# If index.html also missing → HALT with error
```

---

## Security Considerations

| Risk | Mitigation |
|------|------------|
| Path traversal | All paths validated to stay within project root |
| Subprocess injection | Git commands use list args, not shell strings |
| Manifest tampering | Checksums included in manifests |
| Concurrent access | Atomic file writes prevent corruption |

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Could not analyze X: syntax error` | Invalid Python file | Fix syntax or add to `.docgenignore` |
| `Git not available` | Git not installed | Install Git or run with `--no-git` |
| `Permission denied` | File permissions | Check write access to `cortex-brain/documents/` |
| `Manifest checksum mismatch` | File corrupted | Regenerate manifest |
| `Index.html not found` | Wrong path | Verify docs/index.html exists |
| `Unauthorized page` | Not in governance | Use approval protocol |
