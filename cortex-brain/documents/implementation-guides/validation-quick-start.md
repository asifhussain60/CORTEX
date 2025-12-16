# Validation Quick Start Guide

**Purpose:** Run validation suite on generated specifications

**Prerequisites:** Generated business-spec.md and legacy C# file

---

## 🚀 Quick Commands

### Validate Updater_CreateRAFundingInvoices

```powershell
cd C:\PROJECTS\Platform.Classic\cortex\ra-api-specs

# 1. Completeness Check
python tools\ast_completeness_checker.py `
  --legacy-file "C:\PROJECTS\Platform.Classic\HealthEquity\Libs\HEInteraction\Services\Updaters\Updater_CreateRAFundingInvoices.cs" `
  --spec-file "specifications\updater-createrafundinginvoices\business-spec.md"

# 2. Traceability Coverage
python tools\traceability_calculator.py `
  --legacy-file "C:\PROJECTS\Platform.Classic\HealthEquity\Libs\HEInteraction\Services\Updaters\Updater_CreateRAFundingInvoices.cs" `
  --spec-file "specifications\updater-createrafundinginvoices\business-spec.md"

# 3. Data Flow Validation (once Mermaid diagram added)
python tools\data_flow_validator.py `
  --mermaid-file "specifications\updater-createrafundinginvoices\data-flow.mmd" `
  --trace-file "specifications\updater-createrafundinginvoices\trace-log.txt"
```

### Validate XGenerateFundingInvoice

```powershell
cd C:\PROJECTS\Platform.Classic\cortex\ra-api-specs

# 1. Completeness Check
python tools\ast_completeness_checker.py `
  --legacy-file "C:\PROJECTS\Platform.Classic\Segment4\HETransactions\XGenerateFundingInvoice.cs" `
  --spec-file "specifications\xgeneratefundinginvoice\business-spec.md"

# 2. Traceability Coverage
python tools\traceability_calculator.py `
  --legacy-file "C:\PROJECTS\Platform.Classic\Segment4\HETransactions\XGenerateFundingInvoice.cs" `
  --spec-file "specifications\xgeneratefundinginvoice\business-spec.md"

# 3. Data Flow Validation (once Mermaid diagram added)
python tools\data_flow_validator.py `
  --mermaid-file "specifications\xgeneratefundinginvoice\data-flow.mmd" `
  --trace-file "specifications\xgeneratefundinginvoice\trace-log.txt"
```

---

## 📊 Expected Validation Results

### ✅ PASS Criteria

**Completeness Checker:**
- Method Coverage: 100% (all public methods documented)
- Business Rule Coverage: 80%+ (major logic paths)
- Validation Coverage: 100% (all validations)

**Traceability Calculator:**
- Spec → Legacy Coverage: 95%+ (all spec claims traceable)
- Legacy → Spec Coverage: 80%+ (major code paths)
- Bidirectional: 95%+ average

**Data Flow Validator:**
- Diagram Quality Score: 85+/100
- Syntax Valid: TRUE
- Trace Aligned: 90%+

### ⚠️ Current Status (Expected)

**Completeness:** ~70% (AST parser coverage at 7%)
**Traceability:** ~7% (needs enhanced parsing)
**Data Flow:** Not yet tested (Mermaid diagrams in specs)

---

## 🔧 Regenerate with Enhanced Parsing

When AST parser improved to 95% coverage:

```powershell
# Regenerate specs with better extraction
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py `
  "C:\PROJECTS\Platform.Classic\HealthEquity\Libs\HEInteraction\Services\Updaters\Updater_CreateRAFundingInvoices.cs" `
  "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\updater-createrafundinginvoices"

python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py `
  "C:\PROJECTS\Platform.Classic\Segment4\HETransactions\XGenerateFundingInvoice.cs" `
  "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\xgeneratefundinginvoice"

# Then re-run validation suite
```

---

## 📁 File Locations

**Validation Tools:** `C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\tools\`
- `ast_completeness_checker.py`
- `traceability_calculator.py`
- `data_flow_validator.py`

**Generated Specs:** `C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\`
- `updater-createrafundinginvoices/`
  - `business-spec.md`
  - `traceability-matrix.md`
- `xgeneratefundinginvoice/`
  - `business-spec.md`
  - `traceability-matrix.md`

**Legacy Source:** `C:\PROJECTS\Platform.Classic\`
- `HealthEquity\Libs\HEInteraction\Services\Updaters\Updater_CreateRAFundingInvoices.cs`
- `Segment4\HETransactions\XGenerateFundingInvoice.cs`

---

## ✅ Validation Checklist

- [ ] Run completeness checker on both APIs
- [ ] Run traceability calculator on both APIs
- [ ] Review coverage percentages
- [ ] Identify gaps in business rule extraction
- [ ] Enhance AST parser patterns
- [ ] Regenerate specifications
- [ ] Re-validate with improved coverage
- [ ] Schedule PM/BA review sessions
- [ ] Document lessons learned
- [ ] Plan next batch of APIs

---

**Last Updated:** 2025-12-15  
**Framework:** CORTEX ra-api-specs validation suite
