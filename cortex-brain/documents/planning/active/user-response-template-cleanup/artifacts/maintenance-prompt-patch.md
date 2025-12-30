# Maintenance Prompt Patch - Response Template Integrity

**Purpose:** Add Rule 8 and Phase 11 to `cortex-maintenance.prompt.md`  
**Created:** 2025-12-30  
**Plan:** user-response-template-cleanup

---

## Patch Location

Insert after **Rule 7: Autonomous Execution Enforcement** (approximately line 290)

---

## New Content to Add

### Rule 8: Response Template Integrity (NEW - December 30, 2025)

**ALL response template references MUST resolve to existing files.**

**Validation Checks:**
1. Every `inherits_from` reference points to existing file
2. Every `template:` in routing rules points to defined template
3. No orphaned template definitions
4. Schema versions are consistent (v4.0)
5. Introduction templates exist for all audiences (professional, leadership, product, engineering)

**❌ FORBIDDEN:**
- `inherits_from: core/base-templates/5-part-standard.yaml` (file doesn't exist)
- Template references to undefined templates
- Duplicate routing/component files across locations
- Schema version mismatch (must be v4.0)

**✅ REQUIRED:**
- Single source of truth: `response-templates-v4.yaml`
- All routing in: `response-templates/response-routing-rules.yaml`
- Introduction templates in: `response-templates/operations/introduction/`
- Validated on every maintenance run

**Auto-Repair Actions:**
- Remove orphaned `inherits_from` references
- Delete duplicate files in `cortex-brain/` root
- Generate missing introduction templates from artifacts
- Update schema versions to v4.0

**Reference Files:**
- `cortex-brain/response-templates-v4.yaml` (master definitions)
- `cortex-brain/response-templates/response-routing-rules.yaml` (intent routing)
- `cortex-brain/documents/planning/active/user-response-template-cleanup/artifacts/introduction-templates.yaml` (template source)

---

## Phase 11: Response Template Validation

**Add to 10-Phase Pipeline (making it 11-Phase):**

```markdown
### Phase 11: Response Template Validation 📋

**Purpose:** Ensure all response templates are properly wired and functional.

**Scan Operations:**
```bash
echo "📋 Phase 11: Validating response templates..."

# 1. Check for orphaned inherits_from references
echo "  Scanning for orphaned inherits_from..."
grep -r "inherits_from:" cortex-brain/response-templates/ | while read line; do
  FILE=$(echo "$line" | cut -d: -f3- | tr -d ' ')
  if [ ! -f "cortex-brain/response-templates/$FILE" ]; then
    echo "    ⚠️  Orphaned: $FILE"
  fi
done

# 2. Check for duplicate files
echo "  Checking for duplicates..."
for FILE in response-routing-rules.yaml response-profile-variants.yaml response-base-components.yaml; do
  if [ -f "cortex-brain/$FILE" ] && [ -f "cortex-brain/response-templates/$FILE" ]; then
    echo "    ⚠️  Duplicate: $FILE"
  fi
done

# 3. Verify introduction templates exist
echo "  Verifying introduction templates..."
for TEMPLATE in introduction_professional introduction_leadership introduction_product introduction_engineering; do
  if ! grep -q "$TEMPLATE:" cortex-brain/response-templates-v4.yaml cortex-brain/response-templates/operations/introduction/introduction.yaml 2>/dev/null; then
    echo "    ⚠️  Missing: $TEMPLATE"
  fi
done

# 4. Check schema version consistency
echo "  Checking schema versions..."
grep -r "schema_version:" cortex-brain/response-templates/*.yaml | grep -v "4.0" && echo "    ⚠️  Version mismatch found"

echo "✅ Phase 11 complete"
```

**Auto-Repair Actions:**

| Issue | Action |
|-------|--------|
| Orphaned `inherits_from` | Remove the line |
| Duplicate files in root | Delete root version, keep response-templates/ version |
| Missing introduction template | Copy from artifacts/introduction-templates.yaml |
| Schema version mismatch | Update to 4.0 |

**Success Criteria:**
- Zero orphaned references
- Zero duplicate files
- All 4 introduction templates exist
- All schemas at v4.0
```

---

## Pipeline Update

Update the pipeline table to include Phase 11:

```markdown
| Phase | Focus Area | Diagnose | Auto-Repair | Verify |
|-------|-----------|----------|-------------|--------|
| **1** | 🔍 DISCOVERY | Scan system | Generate action report | Issues cataloged |
| **2** | 🗑️ CLEANUP | Find backups | Delete waste | Zero bloat |
| **3** | 🔧 SCAFFOLDING | Check generators | Create missing | Test works |
| **4** | 🔌 WIRING | Detect unwired | Auto-wire | 100% coverage |
| **5** | 🧪 TESTING | Run tests | Fix bugs | 100% pass |
| **6** | 📚 KNOWLEDGE | Scan library | Sync YAML↔MD | Accessible |
| **7** | 🗂️ ORGANIZATION | Check structure | Archive/consolidate | Clean |
| **8** | 🔀 ROUTING | Validate router | Fix paths | Functional |
| **9** | 📝 PROMPTS | Measure bloat | Regenerate | <200 lines |
| **10** | ✅ VERIFICATION | Run diagnostics | Fix critical | ≥95% health |
| **11** | 📋 TEMPLATES | Validate templates | Fix references | 100% wired |
```

---

## Execution Order Update

Add to Phase Execution Order:

```
Phase 11: TEMPLATES (Response Integrity)
  ├─ Scan for orphaned inherits_from references
  ├─ Delete duplicate routing/component files
  ├─ Verify introduction templates exist
  ├─ Check schema version consistency
  └─ Auto-repair all issues
```

---

## Final Verification

After applying this patch, run:

```bash
# Verify Rule 8 is in maintenance prompt
grep -c "Rule 8: Response Template Integrity" .github/prompts/cortex-maintenance.prompt.md
# Expected: 1

# Verify Phase 11 is in pipeline
grep -c "Phase 11" .github/prompts/cortex-maintenance.prompt.md
# Expected: Multiple matches
```
