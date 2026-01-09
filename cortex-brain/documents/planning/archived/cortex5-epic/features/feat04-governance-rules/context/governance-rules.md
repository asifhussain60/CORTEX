# Feature: Governance Rules (SKULL System)

**Feature ID:** F002 | **Category:** Architecture Integrity | **Priority:** 🔥 HIGH | **Status:** Partial

## �� Purpose
Enforce 61+ governance rules preventing architectural drift, ensuring code quality, and protecting brain integrity.

## 📋 Key Rules
1. **TDD_ENFORCEMENT** - Tests must fail before implementation
2. **HOLISTIC_DISCOVERY** - Search before create
3. **GIT_ISOLATION** - CORTEX code never commits to user repos
4. **PLANNING_ISOLATION** - Plans create structure ONLY, never implement
5. **PLAN_FILE_ORGANIZATION** - Files in subfolders (not root)
6. **HAND_OFF_PROTOCOL** - Autonomous orchestrators execute independently
7. **SCRIPT_ORGANIZATION_ENFORCEMENT** - ⚡ NEW (Phase 1.5)

## ✅ Acceptance Criteria
- [ ] All 61 rules documented
- [ ] Automated validation pipeline
- [ ] Pre-commit hooks
- [x] SCRIPT_ORGANIZATION_ENFORCEMENT added (lines 188-233)

## 🔗 Dependencies
**Requires:** F001 (Planning System)  
**Required By:** F003 (Toolkit), F004 (Testing)

## 📍 Location
`cortex-brain/brain-protection-rules.yaml`

---
**Status:** Rule #7 added, enforcement pending Phase 7
