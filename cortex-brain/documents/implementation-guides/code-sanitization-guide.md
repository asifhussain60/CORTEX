# Code Sanitization Tool - Implementation Guide

**Version:** 1.0.0  
**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**  
**Created:** December 16, 2025

---

## Overview

The **Code Sanitization Tool** transforms domain-specific codebases into generic, shareable versions while preserving full functionality, architecture patterns, and learning value. Use this to safely share sample applications, case studies, and learning materials without exposing proprietary company information.

### Key Features

✅ **5-Phase Workflow:** Analyze → Mapping → Transform → Validate → Report  
✅ **Multi-Language Support:** C#, Python, TypeScript, JavaScript  
✅ **AST-Aware Transformations:** Preserves code structure and semantics  
✅ **Build Validation:** Ensures sanitized code builds and tests pass  
✅ **Audit Trail:** Complete transformation mapping and rollback capability  
✅ **Dry-Run Preview:** See changes before applying  

---

## Quick Start

### Copilot Chat (Recommended)

```
sanitize C:\Projects\MyApp
```

Interactive workflow with user approval gates.

### Command Line

```bash
# Basic sanitization
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp

# Dry-run preview
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp --dry-run

# Custom output directory
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp -o C:\Projects\Generic-App

# Auto-approve with custom mappings
python scripts/cli_wrappers/sanitize_wrapper.py C:\Projects\MyApp --auto-approve --mapping-file mappings.json
```

---

## Workflow Phases

### Phase 1: Discovery & Analysis

**What it does:**
- Scans codebase structure
- Identifies domain-specific terminology
- Detects sensitive data (connection strings, API keys, emails)
- Extracts namespaces and dependencies

**Output:**
- File inventory (by language and type)
- Domain terminology report with frequency
- Sensitive data locations
- Namespace catalog

### Phase 2: Transformation Mapping

**What it does:**
- Generates domain→generic mappings using manifest rules
- Detects naming conflicts
- Resolves conflicts with disambiguators
- Creates preview for user review

**Output:**
- Comprehensive transformation mappings
- Conflict resolution report
- Side-by-side preview

**User Interaction:**
- ✅ Approval required before transformation
- ⚙️ Can modify mappings via custom mapping file

### Phase 3: Execute Transformation

**What it does:**
- Creates backup of source codebase
- Applies transformations across all files
- Renames files and directories
- Updates configuration files
- Transforms documentation

**Output:**
- Sanitized codebase in output directory
- Transformation log with statistics
- Backup location for rollback

**Safety:**
- ✅ Original codebase never modified
- ✅ Backup retained for 30 days
- ✅ Rollback on validation failure

### Phase 4: Build & Test Validation

**What it does:**
- Detects build system (.NET, Python, Node.js)
- Executes build
- Runs test suite
- Compares test results with original

**Output:**
- Build success/failure
- Test pass/fail counts
- Validation report

**Quality Gates:**
- ✅ Build must succeed
- ✅ Test pass rate >= original
- ✅ No broken references

**Rollback:**
- Automatic rollback if validation fails

### Phase 5: Generate Audit Report

**What it does:**
- Documents complete transformation
- Generates mapping reference (JSON)
- Archives all artifacts
- Provides traceability

**Output:**
- Audit report (Markdown)
- Mapping reference (JSON for reverse transformation)
- Validation metrics

---

## Configuration

### Manifest: `cortex-brain/orchestrator-manifests/code-sanitization-manifest.yaml`

#### Terminology Categories

```yaml
terminology_categories:
  domain_specific:
    - reimbursement
    - funding
    - HSA
    - FSA
  
  compliance_specific:
    - HIPAA
    - PHI
    - SOC2
  
  infrastructure_specific:
    - company_name
    - internal_urls
```

#### Generic Replacements

```yaml
generic_replacements:
  domain:
    reimbursement: payment
    funding: payment
    HSA: account_type_a
  
  compliance:
    HIPAA: GDPR
    PHI: PII
    SOC2: "ISO 27001"
```

### Custom Mapping File

Create `mappings.json` to override default mappings:

```json
{
  "MyCompany": "GenericCorp",
  "ProprietarySystem": "ExternalSystem",
  "InternalAPI": "ThirdPartyAPI"
}
```

Usage:
```bash
python scripts/cli_wrappers/sanitize_wrapper.py MyApp --mapping-file mappings.json
```

---

## Supported Languages

| Language | Extensions | Transformation Strategy |
|----------|-----------|------------------------|
| C# | `.cs` | AST-aware (Roslyn) |
| Python | `.py` | AST-aware (ast) |
| TypeScript | `.ts`, `.tsx` | AST-aware (typescript) |
| JavaScript | `.js` | AST-aware |
| Markdown | `.md` | Regex with code block preservation |
| JSON/YAML | `.json`, `.yaml`, `.yml` | Structure-aware |
| OpenAPI | `.openapi.yaml` | OpenAPI-aware schema update |

---

## Examples

### Example 1: Healthcare App → Generic Payment System

**Original:**
```csharp
namespace RA.FundingInvoices.Core
{
    public class FundingInvoice
    {
        // HIPAA audit field
        public string MemberSSN { get; set; }
    }
}
```

**Sanitized:**
```csharp
namespace PaymentProcessor.Core
{
    public class PaymentInvoice
    {
        // GDPR audit field
        public string CustomerID { get; set; }
    }
}
```

### Example 2: Configuration Files

**Original:**
```json
{
  "ConnectionStrings": {
    "Database": "Server=internal-db.mycompany.com;..."
  }
}
```

**Sanitized:**
```json
{
  "ConnectionStrings": {
    "Database": "Server=localhost;..."
  }
}
```

---

## Best Practices

### Before Sanitization

1. ✅ **Test Original Codebase**
   - Ensure all tests pass before sanitization
   - Document baseline test pass rate

2. ✅ **Review Sensitive Data**
   - Check for hardcoded credentials
   - Review connection strings
   - Audit comments for proprietary info

3. ✅ **Create Git Checkpoint**
   - Commit all changes
   - Tag as pre-sanitization checkpoint

### During Sanitization

1. ✅ **Use Dry-Run First**
   - Preview all transformations
   - Review mapping conflicts
   - Verify terminology replacements

2. ✅ **Review Mapping Preview**
   - Check for unintended replacements
   - Verify compound terms handled correctly
   - Ensure no loss of meaning

3. ✅ **Validate Custom Mappings**
   - Test custom mapping file syntax
   - Verify no circular mappings

### After Sanitization

1. ✅ **Review Sanitized Code**
   - Spot-check critical files
   - Verify no proprietary terms leaked
   - Check documentation accuracy

2. ✅ **Run Full Test Suite**
   - Should match original pass rate
   - Investigate any new failures

3. ✅ **Archive Artifacts**
   - Save audit report
   - Preserve mapping reference
   - Store backup securely

---

## Troubleshooting

### Build Failures

**Problem:** Sanitized code doesn't build

**Solutions:**
1. Check transformation log for partial replacements
2. Review namespace mappings for missing dependencies
3. Verify configuration files transformed correctly
4. Use `--dry-run` to preview before applying

### Test Failures

**Problem:** Tests pass before but fail after sanitization

**Solutions:**
1. Check test files for hardcoded domain terms
2. Review test data fixtures for transformation
3. Verify mock data updated consistently
4. Compare test output before/after

### Missing Transformations

**Problem:** Some domain terms not replaced

**Solutions:**
1. Add terms to manifest's `terminology_categories`
2. Use custom mapping file for edge cases
3. Check file exclusions (bin/, obj/, etc.)
4. Verify file extensions supported

### Naming Conflicts

**Problem:** Multiple terms map to same generic term

**Solutions:**
1. Review conflict resolution report
2. Add disambiguators in custom mapping file
3. Update manifest's `generic_replacements`

---

## API Reference

### SanitizationOrchestrator

```python
from src.operations.modules.orchestration.sanitization_orchestrator import SanitizationOrchestrator

orchestrator = SanitizationOrchestrator()

results = orchestrator.execute_sanitization(
    source_directory="C:\\Projects\\MyApp",
    output_directory="C:\\Projects\\Generic-App",  # Optional
    mapping_overrides={"CompanyName": "GenericCorp"},  # Optional
    dry_run=False,  # True for preview
    auto_approve=False  # True to skip prompts
)

# Results structure
{
    "status": "success" | "failed" | "cancelled",
    "start_time": "ISO timestamp",
    "end_time": "ISO timestamp",
    "is_complete": True,
    "phases": {
        "analyze": {...},
        "mapping": {...},
        "transform": {...},
        "validate": {...},
        "report": {...}
    }
}
```

---

## Integration with CORTEX

### As Part of Application Onboarding

```
# After creating sample app, sanitize it
onboard MyApp
sanitize MyApp --auto-approve
```

### With Planning System 2.0

```
# Plan a feature, sanitize the implementation
plan authentication feature
sanitize src/features/authentication
```

### With Documentation Generation

```
# Generate docs, then sanitize
generate docs for MyApp
sanitize MyApp/docs
```

---

## Security Considerations

### Data Protection

- ✅ Never sanitizes test data containing real PII/PHI
- ✅ Verifies no sensitive data in comments/strings
- ✅ Masks connection strings and credentials
- ✅ Preserves data protection compliance requirements

### Auditability

- ✅ Maintains complete transformation log
- ✅ Generates reversible mapping file
- ✅ Documents all automated decisions
- ✅ Provides rollback capability

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-16 | Initial release with 5-phase workflow |

---

## Related Documentation

- **Manifest:** `cortex-brain/orchestrator-manifests/code-sanitization-manifest.yaml`
- **Orchestrator:** `src/operations/modules/orchestration/sanitization_orchestrator.py`
- **CLI Wrapper:** `scripts/cli_wrappers/sanitize_wrapper.py`
- **Operations:** `cortex-operations.yaml` (sanitize operation)

---

## Support

**Issues:** File in CORTEX GitHub repository  
**Questions:** Use Copilot Chat: `help sanitize`

---

*Implementation Guide for CORTEX Code Sanitization Tool*  
*Author: Asif Hussain | Copyright © 2025 Asif Hussain. All rights reserved.*
