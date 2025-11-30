# SETUP-CORTEX.md Validation Section

**Purpose:** Add post-installation validation step to SETUP-CORTEX.md  
**Location:** After "🛠️ Installation" section (before "📚 Using CORTEX")

---

## New Section to Add

```markdown
### 5️⃣ Validate Installation

After initializing CORTEX, validate that everything is working correctly:

```bash
# Run installation validation
python -m src.orchestrators.setup_epm_orchestrator --validate

# Or via GitHub Copilot Chat:
/CORTEX validate installation
```

**Expected Output:**
```
🧠 CORTEX Installation Validation

Stage 1: Bootstrap Verification
  ✅ Entry Point
  ✅ Brain Structure
  ✅ Response Templates
  ✅ Orchestrators

Stage 2: Deployment Gate Validation (16 Gates)
  ✅ Gate  1: System Alignment (ERROR)
  ✅ Gate  2: TDD Integration (ERROR)
  ✅ Gate  3: Code Quality (ERROR)
  ✅ Gate  4: Test Coverage (ERROR)
  ✅ Gate  5: Documentation Complete (ERROR)
  ✅ Gate  6: Template Format (ERROR)
  ✅ Gate  7: Git Checkpoint System (ERROR)
  ✅ Gate  8: SWAGGER Entry Points (ERROR)
  ✅ Gate  9: Conversation Tracking (ERROR)
  ✅ Gate 10: Align Admin-Only (WARNING)
  ✅ Gate 11: Cleanup Data Preservation (ERROR)
  ✅ Gate 12: Deploy Manifest Valid (ERROR)
  ✅ Gate 13: TDD Mastery Integration (ERROR)
  ✅ Gate 14: User Feature Packaging (ERROR)
  ✅ Gate 15: Admin/User Separation (ERROR)
  ✅ Gate 16: Align EPM User-Only (WARNING)

📄 Validation report saved: cortex-brain/documents/reports/installation-validation-{timestamp}.md

✅ CORTEX is ready to use!
```

**If Validation Fails:**

```bash
# Auto-fix common issues
python -m src.orchestrators.setup_epm_orchestrator --validate --fix

# Example output with fixes:
🧠 CORTEX Installation Validation

Stage 1: Bootstrap Verification
  ❌ Response Templates
  ❌ Brain Structure

🔧 Attempting auto-remediation...
  ✅ Fixed: response-templates.yaml restored
  ✅ Fixed: Brain directories recreated

Re-validating after fixes...
  ✅ Response Templates
  ✅ Brain Structure

✅ CORTEX is ready to use (after auto-fixes)!
```

**View Detailed Report:**

```bash
# Check the validation report for detailed analysis
cat cortex-brain/documents/reports/installation-validation-{timestamp}.md
```

The report includes:
- Bootstrap verification results (entry point, brain, templates, orchestrators)
- 16-gate validation results with severity levels
- Specific error messages and recommendations
- Auto-remediation actions (if `--fix` was used)
- Next steps for manual fixes (if needed)

---

## 🔍 Understanding Gate Validation

CORTEX uses a **16-gate validation system** to ensure complete functional integrity:

**ERROR Gates (block deployment, warn on installation):**
1. **System Alignment** - Alignment reports present
2. **TDD Integration** - Tests run before deployment
3. **Code Quality** - No mock/stub patterns in production
4. **Test Coverage** - Minimum coverage thresholds met
5. **Documentation Complete** - All features documented
6. **Template Format** - Response templates properly formatted
7. **Git Checkpoint System** - Checkpoint orchestrator complete
8. **SWAGGER Entry Points** - Swagger features wired
9. **Conversation Tracking** - Tier 1/3 databases functional
11. **Cleanup Data Preservation** - Brain data preserved
12. **Deploy Manifest Valid** - Deployment manifest exists
13. **TDD Mastery Integration** - Git checkpoints in TDD workflow
14. **User Feature Packaging** - 5 key features included
15. **Admin/User Separation** - Admin tools excluded

**WARNING Gates (non-blocking):**
10. **Align Admin-Only** - Alignment triggers admin-only
16. **Align EPM User-Only** - Setup EPM user-facing only

**What Happens on Failure:**
- **Deployment:** ERROR gates block deployment, deployment aborted
- **Installation:** All gates run, report generated, user notified
- **Auto-fix:** Common issues (templates, brain structure) auto-remediated
- **Manual fix:** Complex issues (code changes) require manual intervention

---

## ⚠️ Common Validation Issues

### Issue: Missing Response Templates

**Symptom:**
```
❌ Response Templates
```

**Auto-fix:**
```bash
python -m src.orchestrators.setup_epm_orchestrator --validate --fix
```

**Manual fix:**
```bash
# Restore from backup
cp cortex-brain/response-templates.yaml.bak cortex-brain/response-templates.yaml
```

---

### Issue: Incomplete Brain Structure

**Symptom:**
```
❌ Brain Structure
Missing cortex-brain/tier1/
```

**Auto-fix:**
```bash
python -m src.orchestrators.setup_epm_orchestrator --validate --fix
```

**Manual fix:**
```bash
# Recreate directories
mkdir -p cortex-brain/tier1
mkdir -p cortex-brain/tier3
mkdir -p cortex-brain/documents/reports
```

---

### Issue: Gate Failures (Code-Level)

**Symptom:**
```
❌ Gate 13: TDD Mastery Integration
Documentation incomplete: tdd-mastery-guide.md missing checkpoint info
```

**Resolution:**
These require code/documentation changes and cannot be auto-fixed. Review the detailed report:
```bash
cat cortex-brain/documents/reports/installation-validation-{timestamp}.md
```

Follow recommendations in the **Recommendations** section.

---

## ✅ Validation Success Criteria

CORTEX is ready to use when:
- ✅ Bootstrap verification: 4/4 checks passed
- ✅ Gate validation: 14+ gates passed (ERROR gates must pass)
- ✅ Overall status: HEALTHY or WARNING
- ✅ Report shows: "CORTEX is ready to use!"

After successful validation, you can start working with CORTEX immediately!
```

---

## Integration Instructions

**File:** `scripts/temp/SETUP-CORTEX.md` (or template location)  
**Position:** After Step 4 (Initialize Brain), before "📚 Using CORTEX"  
**Replace:** Insert the entire "### 5️⃣ Validate Installation" section

**Note:** This section should be generated during deployment build process and included in SETUP-CORTEX.md automatically.
