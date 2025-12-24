# Code Sanitization - Quick Reference

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION

---

## Quick Commands

```bash
# Copilot Chat (Recommended)
sanitize C:\Projects\MyApp
sanitize codebase dry-run

# CLI
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp --dry-run
```

---

## What It Does

Transforms company-specific codebases into generic, shareable versions:

✅ Replaces domain terminology (e.g., "Reimbursement" → "Payment")  
✅ Removes proprietary data (company names, URLs, credentials)  
✅ Updates namespaces (e.g., "RA.FundingInvoices" → "PaymentProcessor")  
✅ Validates build + tests pass after transformation  
✅ Generates audit trail with rollback capability  

---

## 5-Phase Workflow

1. **Analyze** - Scan codebase, identify domain terms
2. **Mapping** - Generate transformations, preview changes
3. **Transform** - Apply changes, create timestamped backup
4. **Validate** - Build and test sanitized code
5. **Report** - Generate audit documentation, delete backup on success

**Backup Policy:** Created before transformation, automatically deleted after successful validation. Preserved if errors occur.

---

## Common Use Cases

### Healthcare → Generic
```
RA.FundingInvoices → PaymentProcessor
HIPAA → GDPR
Member → Customer
HSA/FSA → AccountType
```

### Finance → Generic
```
Transaction.Banking → Transaction.Payment
Proprietary algorithms → Standard algorithms
Internal API names → Generic API names
```

### Any Domain → Generic
```
Company-specific terms → Generic equivalents
Internal URLs → example.com
Department names → Generic roles
```

---

## Options

| Option | Purpose |
|--------|---------|
| `--dry-run` | Preview without applying |
| `--output <path>` | Custom output directory |
| `--auto-approve` | Skip user prompts |
| `--mapping-file <path>` | Custom mappings (JSON) |
| `--verbose` | Detailed logging |

---

## Custom Mappings

Create `mappings.json`:

```json
{
  "MyCompany": "GenericCorp",
  "ProprietaryAPI": "ThirdPartyAPI",
  "InternalSystem": "ExternalSystem"
}
```

Use:
```bash
python scripts/cli_wrappers/sanitize_wrapper.py MyApp --mapping-file mappings.json
```

---

## Validation

**Quality Gates:**
- ✅ Build succeeds
- ✅ Test pass rate >= original
- ✅ No broken references
- ✅ No proprietary data leaked

**Auto-Rollback:** If validation fails, backup restored automatically

---

## Output

```
MyApp-sanitized/          # Sanitized codebase
MyApp_backup_timestamp/   # Original backup (30-day retention)
sanitization-audit-report.md      # Complete audit trail
sanitization-mapping-reference.json  # Reversible transformations
```

---

## Integration

```bash
# After creating sample app
onboard MyApp
sanitize MyApp

# Before uploading to GitHub
sanitize MyLearningProject
git add MyLearningProject-sanitized
```

---

## Files

| File | Purpose |
|------|---------|
| `code-sanitization-manifest.yaml` | Configuration |
| `sanitization_orchestrator.py` | 5-phase workflow |
| `code-sanitization-guide.md` | Full documentation |
| `sanitize_wrapper.py` | CLI interface |

---

## Example Workflow

```bash
# 1. Preview changes
sanitize C:\Projects\HealthcareApp --dry-run

# 2. Review mapping preview
# (Copilot shows domain→generic mappings)

# 3. Apply transformation
sanitize C:\Projects\HealthcareApp

# 4. Review sanitized code
cd HealthcareApp-sanitized
dotnet build
dotnet test

# 5. Upload safely
git init
git add .
git commit -m "Generic learning sample"
git push
```

---

**Full Guide:** `cortex-brain/documents/implementation-guides/code-sanitization-guide.md`

**Support:** `help sanitize` in Copilot Chat
