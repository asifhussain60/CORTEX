# Baseline Metrics Report: 4 Target Repositories

**Date:** December 8, 2025  
**Purpose:** Establish baseline for comprehensive dashboard & code intelligence plan v3.9

---

## Executive Summary

This report captures baseline metrics for 4 legacy code repositories before implementing comprehensive code intelligence enhancements. Metrics will be used to measure improvement in documentation quality, executive summary specificity, and onboarding automation.

---

## Repository Metrics

### 1. TCBULK

**Location:** `C:\PROJECTS\TCBULK`

**File Counts:**
- C# Files (.cs): 243
- SQL Files (.sql): 107
- Config Files (.config): 1
- JSON Files (.json): 21
- XML Files (.xml): ~15 (estimated)

**Size Estimate:** ~8-12 MB  
**LOC Estimate:** 50,000-70,000 lines

**Primary Technologies:**
- Language: C#
- Database: SQL Server
- Framework: .NET Framework (likely 4.x)

**Documentation Status:** No README, no docs folder

**Business Domain Clues:**
- HQY.TCCARD namespace suggests Transaction Card system
- HQY.TCCARD.Database project indicates database-first architecture
- HQY.TCCARD.Reports suggests reporting module

---

### 2. V5.ColdFusion

**Location:** `C:\PROJECTS\V5.ColdFusion`

**File Counts:**
- ColdFusion Markup (.cfm): 2,694
- ColdFusion Components (.cfc): 79
- JavaScript (.js): 50
- CSS (.css): 51
- SQL (.sql): 8
- XML (.xml): ~20 (estimated)

**Size Estimate:** ~45-60 MB (largest repo)  
**LOC Estimate:** 450,000-600,000 lines

**Primary Technologies:**
- Language: ColdFusion (tag-based + CFScript)
- Database: Likely SQL Server or MySQL
- Frontend: JavaScript, CSS (minimal)

**Documentation Status:** Has Docs/ folder (outdated, needs verification)

**Business Domain Clues:**
- V5 prefix suggests Version 5 of larger system
- High .cfm count indicates web application with many pages
- Low .cfc count suggests procedural style (not OOP-heavy)
- Likely legacy employee benefits or HR system

**Notes:**
- Largest repository by file count (2,882 total files)
- Critical test case for ColdFusion parser development
- High priority for reverse engineering

---

### 3. V5.WebServices.PrevalidationWS

**Location:** `C:\PROJECTS\V5.WebServices.PrevalidationWS`

**File Counts:**
- C# Files (.cs): 48
- Config Files (.config): 36
- ASMX Web Services (.asmx): 2
- WSDL Files (.wsdl): ~5 (estimated)

**Size Estimate:** ~2-4 MB (smallest repo)  
**LOC Estimate:** 15,000-25,000 lines

**Primary Technologies:**
- Language: C#
- Framework: .NET Framework (ASMX web services)
- Protocol: SOAP

**Documentation Status:** No README, no docs folder

**Business Domain Clues:**
- PrevalidationWS suggests validation service
- ASMX indicates legacy SOAP web services (.NET 2.0-4.0 era)
- Part of V5 ecosystem (related to V5.ColdFusion)
- Likely pre-validation for employee benefits eligibility

**Notes:**
- Smallest repository
- SOAP/ASMX technology (deprecated, replaced by WCF/REST)
- Integration point between systems

---

### 4. V5.CommuterOpsWeb

**Location:** `C:\PROJECTS\V5.CommuterOpsWeb`

**File Counts:**
- C# Files (.cs): 237
- JavaScript (.js): 92
- ASPX Pages (.aspx): 57
- Razor Views (.cshtml): 41
- CSS Files (.css): 45
- Config Files (.config): ~10

**Size Estimate:** ~10-15 MB  
**LOC Estimate:** 70,000-100,000 lines

**Primary Technologies:**
- Language: C# (backend), JavaScript (frontend)
- Framework: ASP.NET Web Forms (.aspx) + ASP.NET MVC (.cshtml) - Hybrid!
- Frontend: JavaScript, CSS

**Documentation Status:** Has Docs/ folder (needs verification)

**Business Domain Clues:**
- CommuterOps suggests commuter operations/benefits
- Hybrid Web Forms + MVC indicates migration in progress
- Likely manages commuter parking, transit passes, vanpools
- Part of V5 ecosystem

**Notes:**
- Hybrid architecture (Web Forms legacy + MVC modern)
- Interesting case study for migration analysis
- Good candidate for onboarding automation demo

---

## Technology Stack Summary

| Repository | Primary Language | Framework | Web Tech | LOC Estimate |
|------------|-----------------|-----------|----------|--------------|
| TCBULK | C# | .NET Framework | N/A | 50K-70K |
| V5.ColdFusion | ColdFusion | CF 9/2018 | CFM/CFC | 450K-600K |
| PrevalidationWS | C# | .NET ASMX | SOAP | 15K-25K |
| CommuterOpsWeb | C# | ASP.NET | Web Forms + MVC | 70K-100K |
| **TOTAL** | **Multi** | **Legacy** | **Mixed** | **585K-795K** |

---

## Analysis Challenges Identified

### 1. ColdFusion Parser Priority
- V5.ColdFusion has 2,694 .cfm files and 79 .cfc files
- NO existing ColdFusion parser in CORTEX
- Must handle both tag-based markup and CFScript syntax
- Represents 60%+ of total codebase LOC

### 2. Multi-Framework Complexity
- CommuterOpsWeb uses BOTH Web Forms (.aspx) AND MVC (.cshtml)
- Requires analysis of two different ASP.NET paradigms
- Migration state needs to be captured in documentation

### 3. Documentation Gaps
- Only 2 of 4 repos have Docs/ folders (ColdFusion, CommuterOpsWeb)
- Existing docs likely outdated (V5 suggests 5+ years old)
- TCBULK and PrevalidationWS have ZERO documentation

### 4. Legacy Technology Stack
- ASMX web services (deprecated since 2010)
- ColdFusion (niche language, shrinking community)
- Web Forms (legacy ASP.NET, not recommended for new projects)
- All indicate 10-15 year old codebase

### 5. Business Domain Inference
- CommuterOps, PrevalidationWS, TCCARD all suggest employee benefits domain
- Likely interconnected systems (V5 prefix common across 3 repos)
- Reverse engineering must identify cross-system integrations

---

## Baseline Metrics for Success Measurement

### Current State (Before Enhancement)

**Executive Summary Quality:**
- Current Score: 3/10 (generic template with file counts)
- Business Domain Identification: 0/4 repos
- Specific Capabilities Listed: 0/4 repos
- Feature Evolution Insights: 0/4 repos

**Onboarding Time:**
- Estimated Manual Setup: 4-8 hours per developer
- Automated Steps: 0%
- Environment Validation: Manual only
- Tool Recommendations: None

**Documentation Coverage:**
- Repositories with Docs: 2/4 (50%)
- Docs Verified Current: 0/4 (assumed outdated)
- Auto-Generated Docs: 0/4
- Instructional Manuals: 0/4

**Data Quality:**
- False Positive Rate: ~30% (languages, versions)
- Independent Validation: Exists but limited
- Cross-Tab Reconciliation: 3 rules only (R8/R9/R10)
- Validation Coverage: ~40% of dashboard tabs

### Target State (Post-Enhancement)

**Executive Summary Quality:**
- Target Score: 8/10
- Business Domain Identification: 4/4 repos (100%)
- Specific Capabilities: 5-8 per repo
- Feature Evolution: Present for repos with git history

**Onboarding Time:**
- Target Manual Setup: <30 minutes
- Automated Steps: 90%+
- Environment Validation: 15+ automated checks
- Tool Recommendations: 3-5 per category

**Documentation Coverage:**
- Auto-Generated Docs: 4/4 (100%)
- Docs Verified Current: 4/4 (generated from code)
- Instructional Manuals: 4/4
- Formats: Markdown + HTML + JSON

**Data Quality:**
- False Positive Rate: <5%
- Independent Validation: 7 new rules (R1-R7)
- Cross-Tab Reconciliation: 15 rules total (R8-R15)
- Validation Coverage: 100% of dashboard tabs

---

## Next Steps

1. ✅ **Baseline Metrics Captured** (COMPLETE)
2. ✅ **ColdFusion Test Environment Set Up** (COMPLETE - 20 sample files extracted)
3. ⏳ **Phase 1 Task 1.1: ColdFusion Parser TDD** (Ready to start)
4. ⏳ **User Interviews** (Schedule with 3 developers, 3 executives)
5. ⏳ **Plan Approval** (Review comprehensive plan, adjust priorities)

**ColdFusion Test Files:**
- Location: `tests/fixtures/coldfusion/`
- Sample Count: 20 files (10 .cfm + 10 .cfc)
- Ready for RED phase test development

---

**Report Generated:** December 8, 2025  
**Next Update:** After Phase 1 completion (ColdFusion parser + AST extractors)
