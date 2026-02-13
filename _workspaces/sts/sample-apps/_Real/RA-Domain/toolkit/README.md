# RA Domain Analysis Toolkit

**Version:** 1.0  
**Created:** December 11, 2025  
**Purpose:** Deep domain analysis for Product.Example repository

---

## 🎯 Quick Start

### Prerequisites
```powershell
# Python 3.8+ with dependencies
pip install tree-sitter tree-sitter-c-sharp pyyaml

# Repository access
Test-Path "C:\PROJECTS\Product.Example"  # Should return True
```

### Quick Scan (30 seconds)
```powershell
# Structural analysis only
.\scripts\01_quick_scan.ps1 -RepoPath "C:\PROJECTS\Product.Example"
```

### Full Analysis (17.58 hours - batched execution)
```powershell
# Execute all 20 batches
python scripts\06_master_orchestrator.py --repo-path "C:\PROJECTS\Product.Example" --execute-all
```

### Specific Analysis
```powershell
# Test coverage only (Batch 11)
python scripts\06_master_orchestrator.py --batch 11

# Regulatory compliance only
python scripts\04_regulatory_validator.py --validators irs,hipaa,pci-dss

# Business logic extraction
python scripts\03_business_logic_extractor.py --focus-service ExampleDomainService
```

---

## 📁 Toolkit Structure

```
toolkit/
├── README.md                           # This file
├── ARCHITECTURE.md                     # System architecture documentation
│
├── config/                             # Configuration files
│   ├── analysis-config.yaml            # Main analysis configuration
│   ├── regulatory-rules.json           # RegulatoryAgency/PrivacyRegulation/PaymentSecurity rules
│   └── batch-definitions.yaml          # 20-batch execution plan
│
├── scripts/                            # Executable scripts
│   ├── 01_quick_scan.ps1               # PowerShell quick scan
│   ├── 02_test_coverage_analyzer.py    # Test coverage analysis
│   ├── 03_business_logic_extractor.py  # Business rule extraction
│   ├── 04_regulatory_validator.py      # Compliance validation
│   ├── 05_report_generator.ps1         # Markdown report generation
│   └── 06_master_orchestrator.py       # Master execution coordinator
│
├── src/                                # Python source code
│   ├── collectors/                     # Data collectors
│   │   ├── base_collector.py           # Base class
│   │   ├── entity_collector.py         # Entity extraction
│   │   ├── dto_collector.py            # DTO extraction
│   │   ├── service_collector.py        # Service extraction
│   │   ├── test_collector.py           # Test analysis
│   │   └── regulatory_collector.py     # Compliance checks
│   │
│   ├── orchestrators/                  # Workflow orchestrators
│   │   ├── ra_domain_orchestrator.py   # Master orchestrator
│   │   ├── batch_executor.py           # Batch workflow manager
│   │   └── progress_tracker.py         # Progress monitoring
│   │
│   ├── parsers/                        # AST parsers
│   │   ├── csharp_parser.py            # Tree-sitter C# parser
│   │   ├── entity_parser.py            # Entity-specific parsing
│   │   └── service_parser.py           # Service method parsing
│   │
│   └── validators/                     # Regulatory validators
│       ├── irs_validator.py            # RegulatoryAgency compliance
│       ├── hipaa_validator.py          # PrivacyRegulation audit
│       └── pci_dss_validator.py        # PaymentSecurity checks
│
└── tests/                              # Unit tests
    ├── test_collectors.py
    ├── test_parsers.py
    └── test_validators.py
```

---

## 🚀 Features

### 1. AST-Based Code Analysis
- **Entity Extraction:** 30 domain entities with properties, relationships, compliance flags
- **DTO Analysis:** 44 data transfer objects
- **Service Decomposition:** 19 domain services, 1,113 methods
- **Interface Discovery:** 18 contracts

### 2. Test Coverage Analysis
- **Test-to-Code Mapping:** Links test methods to production code
- **Coverage by Layer:** Domain (80%+), Service (75%+), Job (70%+)
- **Gap Identification:** Untested critical paths, missing test scenarios
- **Scenario Generation:** 40+ regulatory test cases (RegulatoryAgency/PrivacyRegulation/PaymentSecurity)

### 3. Regulatory Compliance Validation
- **RegulatoryAgency Tax Code:** FlexAccount/HealthSavings contribution limits, rollover rules, grace period
- **PrivacyRegulation Security:** PHI audit trails, access controls, MFA enforcement
- **PaymentSecurity:** CVV prohibition, PAN encryption, card masking

### 4. Business Logic Extraction
- **Decision Trees:** Plan-type-specific rules (FlexAccount/HealthSavings/HealthReimbursement/DependentCare)
- **Workflow Definitions:** 7 core business workflows
- **Simplified Explanations:** Rollover logic, claims processing, balance management

### 5. Dashboard Integration
- **Auto-Registration:** Discovered repos added to dashboard selector
- **Real-Time Progress:** Batch completion tracking
- **Visualization:** Charts, heatmaps, compliance status

---

## 📊 Output Structure

All analysis results saved to:
```
cortex_brain/dashboards/data/repos/Product.Example/
├── dashboard.json                      # Master dashboard data
├── ast-outputs/                        # AST scan results
├── test-coverage/                      # Coverage reports
├── regulatory/                         # Compliance findings
├── business-logic/                     # Extracted rules
└── reports/                            # Executive summaries
```

---

## 🔧 Configuration

### Main Configuration: `config/analysis-config.yaml`

```yaml
repository:
  path: "C:/PROJECTS/Product.Example"
  name: "Product.Example"

batches:
  enabled: [1, 2, 2.5, 3.1, 3.2, 3.3, 7, 11, 13, 20]

regulatory:
  irs_limits:
    fsa_annual_max: 3200
    fsa_carryover_max: 640
    hsa_individual_max: 4150

test_coverage:
  minimum_threshold: 80
```

Edit this file to customize analysis behavior.

---

## 📈 Batch Execution Plan

| Batch | Duration | Description | Output |
|-------|----------|-------------|--------|
| 1 | 30 min | Repository metrics | `structural-analysis.json` |
| 2 | 90 min | Business domain map | `business-domain-map.json` |
| 2.5 | 60 min | Regulatory intelligence | `regulatory-baseline.json` |
| 3.1-3.3 | 90 min | Entity extraction | `entities-batch-{1-3}.json` |
| 11 | 60 min | Test coverage | `coverage-report.json` |
| 13 | 90 min | Business logic | `business-rules.json` |
| 20 | 60 min | Dashboard integration | `dashboard.json` |

**Total:** 20 batches, 20.58 hours

---

## 🎯 Common Use Cases

### Use Case 1: Quick Health Check
```powershell
# 30-second scan
.\scripts\01_quick_scan.ps1 -RepoPath "C:\PROJECTS\Product.Example"

# Review: ast-outputs/structural-analysis.json
```

### Use Case 2: Compliance Audit
```powershell
# Run all regulatory validators
python scripts\04_regulatory_validator.py --validators all

# Review: regulatory/p0-issues-tracking.json
```

### Use Case 3: Test Gap Analysis
```powershell
# Analyze test coverage
python scripts\02_test_coverage_analyzer.py

# Review: test-coverage/untested-critical-paths.json
```

### Use Case 4: Business Logic Documentation
```powershell
# Extract business rules
python scripts\03_business_logic_extractor.py --output-format markdown

# Review: business-logic/rollover-rules-simplified.md
```

### Use Case 5: Full Domain Analysis
```powershell
# Execute all 20 batches (run overnight)
python scripts\06_master_orchestrator.py --execute-all --email-on-completion

# Review: reports/executive-summary.md
```

---

## 🔍 Troubleshooting

### Issue: "Repository not found"
```powershell
# Verify path
Test-Path "C:\PROJECTS\Product.Example"

# Update config
# Edit config/analysis-config.yaml → repository.path
```

### Issue: "AST parsing failed"
```powershell
# Install tree-sitter
pip install tree-sitter tree-sitter-c-sharp

# Verify installation
python -c "from tree_sitter import Language; print('OK')"
```

### Issue: "Permission denied"
```powershell
# Run as administrator
Start-Process powershell -Verb RunAs

# Or adjust execution policy
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## 📚 Documentation

- **Architecture:** `ARCHITECTURE.md` - System design and component diagrams
- **Batch Plan:** `../test-plan-v2-batched.md` - Complete 20-batch execution plan
- **Executive Summary:** `../documents/EXECUTIVE-SUMMARY-BATCHES-1-7.md` - Current progress
- **Regulatory Rules:** `config/regulatory-rules.json` - RegulatoryAgency/PrivacyRegulation/PaymentSecurity requirements

---

## 🤝 Integration with CORTEX Dashboard

### View Analysis Results in Dashboard

```powershell
# Launch admin dashboard
python -m src.orchestrators.dashboard_launcher --source "Product.Example"

# Access: http://localhost:8080/ui/index.html
```

**Dashboard Features:**
- Repository selector dropdown
- Progress tracker (3/20 batches complete)
- AST output visualization
- Compliance status indicators
- Business logic charts

---

## 📝 Next Steps

1. **Run Quick Scan:** `.\scripts\01_quick_scan.ps1`
2. **Review Batch Plan:** See `../test-plan-v2-batched.md`
3. **Execute Priority Batches:** Batches 1, 2, 2.5, 11, 13 (high ROI)
4. **Review Compliance:** `regulatory/p0-issues-tracking.json`
5. **Plan Remediation:** Address P0 issues first

---

**Author:** Asif Hussain  
**License:** © 2025 Asif Hussain. All rights reserved.  
**Support:** See ARCHITECTURE.md for design details
