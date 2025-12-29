# CORTEX Document Organization

**Purpose:** Mandatory folder structure for all CORTEX documents  
**Version:** 1.0  
**Status:** ✅ PRODUCTION

---

## 📁 CRITICAL: Document Organization Rules

**All informational documents MUST be created in organized folder structure within CORTEX brain.**

### ✅ ALWAYS USE
`/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/[category]/[filename].md`

### ❌ NEVER CREATE
Documents in repository root or unorganized locations

---

## 📂 Categories & Usage

| Category | Path | When to Use | Example |
|----------|------|-------------|---------|
| **Reports** | `/documents/reports/` | Implementation completion, status reports | `CORTEX-3.0-FINAL-REPORT.md` |
| **Analysis** | `/documents/analysis/` | Deep investigations, performance analysis | `ROUTER-PERFORMANCE-ANALYSIS.md` |
| **Summaries** | `/documents/summaries/` | Quick overviews, daily progress | `TIER3-IMPLEMENTATION-SUMMARY.md` |
| **Investigations** | `/documents/investigations/` | Research, architecture investigations | `AUTH-FEATURE-INVESTIGATION.md` |
| **Planning** | `/documents/planning/` | Roadmaps, implementation plans | `CORTEX-4.0-PLANNING.md` |
| **Conversations** | `/documents/conversation-captures/` | Strategic conversation captures | `CONVERSATION-CAPTURE-2025-11-14.md` |
| **Guides** | `/documents/implementation-guides/` | How-to guides, integration docs | `CORTEX-SETUP-GUIDE.md` |

---

## 📝 Examples of Proper Document Creation

```markdown
# Instead of this (WRONG):
/Users/asifhussain/PROJECTS/CORTEX/INVESTIGATION-ANALYSIS-REPORT.md

# Use this (CORRECT):
/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/analysis/INVESTIGATION-ANALYSIS-REPORT.md

# For conversation captures:
/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/conversation-captures/CONVERSATION-CAPTURE-2025-11-14-AUTHENTICATION.md

# For implementation reports:
/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/reports/CORTEX-3.0-IMPLEMENTATION-REPORT.md
```

---

## 📚 Reference Guide

**Complete organization structure:** See `cortex-brain/documents/README.md` for full naming conventions

---

## ⚠️ ENFORCEMENT

**Document organization is MANDATORY:**
- ALL informational documents MUST use proper categorization
- NEVER create .md files in repository root (except README.md, LICENSE, etc.)
- When referencing existing root documents, note they should be migrated
- Template documents should default to organized paths

**Violation Prevention:**
- Check file paths before creation
- Use absolute paths with proper categorization  
- Reference `cortex-brain/documents/README.md` for guidelines

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file
