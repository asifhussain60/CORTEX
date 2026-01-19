# PaymentProcessor API Specifications - Platform.Classic

**Purpose:** Generated specifications for legacy PaymentProcessor APIs  
**Generator:** CORTEX Lens v3.0  
**Date:** December 15, 2025

---

## 📁 Specifications

This folder contains **generated outputs** from CORTEX Lens for PaymentProcessor API modernization.

**Generator Location:** `C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py` (v3.0)

---

### Available Specifications

#### 1. updater-createpaymenttransactioninvoices
- **business-spec.md** - PM/BA specification with user stories
- **openapi.yaml** - OpenAPI 3.0 specification (YAML)
- **openapi.json** - OpenAPI 3.0 specification (JSON)
- **traceability-matrix.md** - Legacy→Modern line mapping
- **diagrams/** - Separate Mermaid diagram files
  - flowchart.mmd - Business logic flow
  - sequence.mmd - Component interactions
  - dependency.mmd - Class relationships

#### 2. xgeneratetransactioninvoice
- **business-spec.md** - PM/BA specification with user stories
- **openapi.yaml** - OpenAPI 3.0 specification (YAML)
- **openapi.json** - OpenAPI 3.0 specification (JSON)
- **traceability-matrix.md** - Legacy→Modern line mapping
- **diagrams/** - Separate Mermaid diagram files
  - flowchart.mmd - Business logic flow
  - sequence.mmd - Component interactions
  - dependency.mmd - Class relationships

#### 3. xupdatetransactionbatch
- **business-spec.md** - PM/BA specification with user stories
- **openapi.yaml** - OpenAPI 3.0 specification (YAML)
- **openapi.json** - OpenAPI 3.0 specification (JSON)
- **traceability-matrix.md** - Legacy→Modern line mapping
- **diagrams/** - Separate Mermaid diagram files
  - flowchart.mmd - Business logic flow
  - sequence.mmd - Component interactions

---

## 🚀 Generating New Specifications

```bash
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py \
  "<legacy_file.cs>" \
  "<output_directory>"
```

**Example:**
```bash
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py \
  "C:\PROJECTS\Platform.Classic\Segment4\PaymentTransactions\XGenerateTransactionInvoice.cs" \
  "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\xgeneratetransactioninvoice"
```

**Generated Files:**
- `business-spec.md` - Business specification with diagram links
- `diagrams/` - Separate Mermaid diagram files (.mmd)
  - `flowchart.mmd` - Business logic flow and decision points
  - `sequence.mmd` - Component interactions and message flow
  - `dependency.mmd` - Class relationships (if ≥2 dependencies)
- `openapi.yaml` - OpenAPI 3.0 (YAML)
- `openapi.json` - OpenAPI 3.0 (JSON)
- `traceability-matrix.md` - Traceability matrix

**Diagram Rendering:**
- **VS Code:** Install [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension
- **Online:** Copy .mmd content to [mermaid.live](https://mermaid.live)
- **CLI:** Use `mmdc` command to generate PNG/SVG from .mmd files

---

## 📚 Documentation

**CORTEX Lens Documentation:**
- Quick Reference: `C:\PROJECTS\CORTEX\cortex_brain\documents\CORTEX-LENS-QUICK-REF.md`
- OpenAPI Guide: `C:\PROJECTS\CORTEX\cortex_brain\documents\implementation-guides\openapi-generation-guide.md`
- Usage Guide: `C:\PROJECTS\CORTEX\cortex_brain\documents\implementation-guides\cortex-lens-usage-guide.md`

**Validators:**
- AST Completeness: `C:\PROJECTS\CORTEX\src\operations\modules\validators\ast_completeness_checker.py`
- Data Flow: `C:\PROJECTS\CORTEX\src\operations\modules\validators\data_flow_validator.py`
- Traceability: `C:\PROJECTS\CORTEX\src\operations\modules\validators\traceability_calculator.py`

---

## ✅ What's Included

**Each Specification Contains:**
- Executive Summary (30-second overview)
- User Stories ("As a... I want to... So that...")
- Business Rules (extracted from IF/ELSE logic)
- Validation Rules (extracted from throw statements)
- Database Operations (queries and updates)
- Mermaid Diagrams (flowchart, sequence, dependency)
- OpenAPI 3.0 Specification (YAML + JSON)
- Traceability Matrix (line-by-line mapping)

---

## 🎯 Purpose

**Problem:** Large number of legacy APIs without documented requirements

**Solution:** Generate specifications from legacy code for PM/BA validation before modernization

**Workflow:**
1. Run CORTEX Lens generator on legacy code
2. Review generated specification with PM/BA teams
3. Validate business logic and rules
4. Use OpenAPI spec for modern implementation
5. Cross-check legacy vs modern behavior

---

**Generator Version:** 3.0.0  
**Status:** Production Ready  
**Last Updated:** December 15, 2025
