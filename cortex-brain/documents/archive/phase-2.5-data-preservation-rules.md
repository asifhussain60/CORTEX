# Phase 2.5: Data Preservation Rules 🛡️ - CRITICAL FIELDS

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 30, 2025  
**Purpose:** Ensure critical user data is NEVER lost during maintenance file regeneration

---

## ⚠️ MANDATORY: Preserve User Data During File Regeneration

**Philosophy:** "Regenerate structure, preserve data" - Templates and format can change, but user content is sacred.

---

## Protected Fields in Plan Files (YAML/Markdown)

**When regenerating plan files (`00-master-plan.md`, `*.yaml`), MUST preserve:**

| Field | Location | Why Protected | Example |
|-------|----------|---------------|---------|
| **copilot_instructions** | YAML plans | GitHub Copilot runtime config | `response_template`, `progress_updates`, `tdd_enforcement` |
| **metadata.notes** | All plans | User annotations | Implementation notes, decisions |
| **metadata.tags** | All plans | User categorization | `["critical", "security", "auth"]` |
| **threat_analysis** | Security plans | ThreatModeler output | STRIDE categories, mitigations |
| **custom_format** | copilot_instructions | User-defined templates | Custom response formats |
| **session_metadata** | Plan state | Execution history | Checkpoints, rollback points |

---

## Extraction Pattern (Before Regeneration)

**MANDATORY: Extract user data BEFORE any file regeneration:**

```bash
# Example: Regenerating a plan file
PLAN_FILE="cortex-brain/documents/planning/active/feature-xyz/00-master-plan.md"

# Step 1: Extract protected fields
if [ -f "$PLAN_FILE" ]; then
  echo "🛡️  Extracting protected fields from $PLAN_FILE..."
  
  # Extract copilot_instructions (YAML front matter)
  COPILOT_INSTRUCTIONS=$(yq eval '.copilot_instructions' "$PLAN_FILE" 2>/dev/null || echo "{}")
  
  # Extract metadata.notes
  USER_NOTES=$(yq eval '.metadata.notes' "$PLAN_FILE" 2>/dev/null || echo "")
  
  # Extract metadata.tags
  USER_TAGS=$(yq eval '.metadata.tags' "$PLAN_FILE" 2>/dev/null || echo "[]")
  
  # Extract threat_analysis
  THREAT_ANALYSIS=$(yq eval '.threat_analysis' "$PLAN_FILE" 2>/dev/null || echo "{}")
  
  # Save to temp file
  cat > /tmp/preserved_data.json << EOF
{
  "copilot_instructions": $COPILOT_INSTRUCTIONS,
  "metadata_notes": "$USER_NOTES",
  "metadata_tags": $USER_TAGS,
  "threat_analysis": $THREAT_ANALYSIS
}
EOF
  
  echo "  ✅ Protected fields extracted to /tmp/preserved_data.json"
fi

# Step 2: Regenerate file (template/structure changes)
echo "🔄 Regenerating $PLAN_FILE with new template..."
# ... regeneration logic ...

# Step 3: Re-inject protected fields
if [ -f /tmp/preserved_data.json ]; then
  echo "🛡️  Re-injecting protected fields..."
  
  # Merge preserved data back into regenerated file
  yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
    "$PLAN_FILE" /tmp/preserved_data.json > /tmp/merged_plan.yaml
  
  mv /tmp/merged_plan.yaml "$PLAN_FILE"
  
  echo "  ✅ Protected fields restored"
  rm /tmp/preserved_data.json
fi
```

---

## Protected Fields in Response Templates

**When regenerating `response-templates-v4.yaml`, MUST preserve:**

| Section | Fields | Why Protected |
|---------|--------|---------------|
| **named_templates** | All user-defined templates | Custom progress bars, specialized formats |
| **named_templates.autonomous_execution_progress** | Template structure | Planning orchestrator runtime dependency |
| **named_templates.*.format** | Handlebars templates | User customizations, progress bar layouts |

**Extraction Example:**

```bash
TEMPLATE_FILE="cortex-brain/response-templates-v4.yaml"

# Extract named_templates section before regeneration
if [ -f "$TEMPLATE_FILE" ]; then
  echo "🛡️  Preserving named_templates from $TEMPLATE_FILE..."
  yq eval '.named_templates' "$TEMPLATE_FILE" > /tmp/preserved_named_templates.yaml
  
  # After regeneration, merge back
  echo "🔄 Merging preserved templates into regenerated file..."
  yq eval-all '.named_templates = select(fileIndex == 1)' \
    "$TEMPLATE_FILE" /tmp/preserved_named_templates.yaml > /tmp/merged_templates.yaml
  
  mv /tmp/merged_templates.yaml "$TEMPLATE_FILE"
  echo "  ✅ named_templates restored"
fi
```

---

## Verification After Regeneration

**MANDATORY checks after ANY file regeneration:**

```bash
# For plan files
echo "🔍 Verifying preserved fields in regenerated plan..."

# Check copilot_instructions exists
COPILOT_CHECK=$(yq eval 'has("copilot_instructions")' "$PLAN_FILE")
if [ "$COPILOT_CHECK" = "true" ]; then
  echo "  ✅ copilot_instructions preserved"
else
  echo "  ❌ ERROR: copilot_instructions LOST during regeneration!"
  exit 1
fi

# Check response_template is set
RESPONSE_TEMPLATE=$(yq eval '.copilot_instructions.response_template' "$PLAN_FILE" 2>/dev/null)
if [ -n "$RESPONSE_TEMPLATE" ]; then
  echo "  ✅ response_template preserved: $RESPONSE_TEMPLATE"
else
  echo "  ⚠️  WARNING: response_template missing (using default)"
fi

# For response templates
echo "🔍 Verifying named_templates in response-templates-v4.yaml..."

NAMED_TEMPLATES_COUNT=$(yq eval '.named_templates | length' "$TEMPLATE_FILE")
if [ "$NAMED_TEMPLATES_COUNT" -gt 0 ]; then
  echo "  ✅ named_templates preserved: $NAMED_TEMPLATES_COUNT templates"
else
  echo "  ❌ ERROR: named_templates LOST during regeneration!"
  exit 1
fi
```

---

## Preservation Commit Pattern

**When committing regenerated files, commit message MUST include preservation confirmation:**

```bash
git add "$PLAN_FILE" "$TEMPLATE_FILE"

git commit -m "refactor: regenerate plan/template structure

**Files Regenerated:**
- $PLAN_FILE (new template format)
- $TEMPLATE_FILE (updated schema)

**Protected Fields Preserved:**
✅ copilot_instructions (response_template, progress_updates, tdd_enforcement)
✅ metadata.notes (user annotations)
✅ named_templates (autonomous_execution_progress, interactive_planning_progress)
✅ threat_analysis (STRIDE categories, mitigations)

**Verification:**
- copilot_instructions: $(yq eval '.copilot_instructions.response_template' "$PLAN_FILE")
- named_templates count: $(yq eval '.named_templates | length' "$TEMPLATE_FILE")

Generated by: Phase 2.5 - Data Preservation"
```

---

## Success Criteria

**✅ Phase 2.5 is complete when:**

| Check | Command | Expected |
|-------|---------|----------|
| copilot_instructions in plans | `find cortex-brain/documents/planning/active -name "*.yaml" -exec yq eval 'has("copilot_instructions")' {} \; \| grep -c true` | ≥1 |
| response_template set | `find cortex-brain/documents/planning/active -name "*.yaml" -exec yq eval '.copilot_instructions.response_template' {} \; \| grep -c "autonomous_execution_progress"` | ≥1 |
| named_templates exist | `yq eval '.named_templates \| length' cortex-brain/response-templates-v4.yaml` | ≥1 |
| Preservation commits | `git log --oneline \| grep -c "Protected Fields Preserved"` | ≥1 |

---

## Integration with Maintenance Prompt

**This guide should be referenced in `.github/prompts/cortex-maintenance.prompt.md` Phase 2.5:**

```markdown
## Phase 2.5: Data Preservation Rules 🛡️

**Reference:** `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md`

**Critical fields that MUST be preserved during file regeneration:**
- `copilot_instructions` in plan files
- `named_templates` in response-templates-v4.yaml
- `metadata.notes` and `metadata.tags` in plans
- `threat_analysis` in security plans

**Before regenerating ANY file:**
1. Extract protected fields using `yq eval`
2. Perform regeneration
3. Re-inject protected fields
4. Verify with mandatory checks
5. Commit with preservation confirmation
```

---

## Example: Full Regeneration with Preservation

```bash
#!/bin/bash
# Example: Safely regenerate a plan file

PLAN_FILE="cortex-brain/documents/planning/active/user-response-template-cleanup/00-master-plan.md"

echo "🔄 Starting safe regeneration of $PLAN_FILE..."

# Phase 1: Extract
yq eval '.copilot_instructions' "$PLAN_FILE" > /tmp/copilot_instructions.yaml
yq eval '.metadata.notes' "$PLAN_FILE" > /tmp/metadata_notes.txt
yq eval '.threat_analysis' "$PLAN_FILE" > /tmp/threat_analysis.yaml

# Phase 2: Regenerate (your logic here)
echo "Regenerating with new template..."
# ... template regeneration code ...

# Phase 3: Restore
yq eval -i '.copilot_instructions = load("/tmp/copilot_instructions.yaml")' "$PLAN_FILE"
yq eval -i '.metadata.notes = load("/tmp/metadata_notes.txt")' "$PLAN_FILE"
yq eval -i '.threat_analysis = load("/tmp/threat_analysis.yaml")' "$PLAN_FILE"

# Phase 4: Verify
if yq eval 'has("copilot_instructions")' "$PLAN_FILE" | grep -q "true"; then
  echo "✅ Preservation successful!"
else
  echo "❌ CRITICAL: Data loss detected!"
  exit 1
fi

# Phase 5: Commit
git add "$PLAN_FILE"
git commit -m "refactor: regenerate $PLAN_FILE with preserved copilot_instructions"
```

---

**End of Phase 2.5 Data Preservation Rules**
