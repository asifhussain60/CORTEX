# 🧱 Orchestrator Composable Template System

**Priority:** MEDIUM-HIGH (25) | **Estimated Effort:** 4-6 hrs | **Category:** Enhancement

---

## 🎯 Objective

Implement a LEGO-style composable template system where all orchestrators can combine specific and generic template blocks while using standardized progress bar format.

---

## 📋 Execution Steps

### Step 1: Verify Existing Template Structure
Read current templates and understand structure:
```powershell
# Check for existing composable/block patterns
Select-String -Path "cortex-brain\response-templates-v4.yaml" -Pattern "composable|block" | Select-Object -First 20

# Check which manifests already have response_templates
Get-ChildItem "cortex-brain\manifests\orchestrators\*-manifest.yaml" | ForEach-Object {
  $hasTemplates = Select-String -Path $_.FullName -Pattern "response_templates:" -Quiet
  [PSCustomObject]@{
    File = $_.Name
    HasResponseTemplates = $hasTemplates
  }
} | Format-Table -AutoSize
```

**Expected Output:** List of manifests showing which already have `response_templates` sections.

### Step 2: Add Composable Blocks Section to response-templates-v4.yaml
Edit `cortex-brain/response-templates-v4.yaml`:
- Add new section after existing templates (approximately line 850+)
- Insert the `composable_blocks` schema definition:

```yaml
# ============================================================================
# COMPOSABLE BLOCKS SYSTEM
# ============================================================================

composable_blocks:
  version: "1.0"
  
  # Standardized Progress Tracker (MANDATORY for all orchestrators)
  progress_tracker_standard:
    description: "Standardized visual progress tracker"
    format: |
      ### 📊 {{operation_name}} STATUS
      
      **Overall Progress:** `{{overall_bar}}` **{{overall_percentage}}%** {{status_emoji}} {{status_text}}
      
      | Phase | Progress | Status |
      |-------|----------|--------|
      {{#each phases}}
      | Phase {{phase_num}} - {{phase_name}} | `{{phase_bar}}` | {{phase_percentage}}% {{phase_icon}} {{phase_status}} |
      {{/each}}
    
    config:
      bar_width: 10
      filled_char: "█"
      empty_char: "░"
      icons:
        complete: "✅"
        in_progress: "🔄"
        pending: "⏳"
        failed: "❌"
        skipped: "⏸️"

  # Generic blocks (shared across all orchestrators)
  generic_blocks:
    understanding:
      emoji: "🎯"
      title: "Understanding & Scope"
    approach:
      emoji: "⚡"
      title: "Approach & Considerations"
    response:
      emoji: "💬"
      title: "Response"
    changes:
      emoji: "📊"
      title: "Impact & Changes"
    next_steps:
      emoji: "🔍"
      title: "Next Steps"
    validation_status:
      emoji: "✅"
      title: "Validation Status"
```

Verify: `grep -A 5 "composable_blocks:" cortex-brain/response-templates-v4.yaml`

### Step 3: Add response_templates to Planning Manifest
Edit `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`:
- Locate end of file (before closing)
- Add `response_templates` section:

```yaml
response_templates:
  plan_creation:
    blocks:
      - cortex_header
      - understanding
      - progress_tracker_standard
      - dor_dod_status
      - deliverables_matrix
      - next_steps
  plan_execution:
    blocks:
      - cortex_header
      - progress_tracker_standard
      - changes
      - next_steps
```

Verify: `grep -A 10 "response_templates:" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

### Step 4: Add response_templates to TDD Manifest
Edit `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`:
- Add at end of file:

```yaml
response_templates:
  test_run:
    blocks:
      - cortex_header
      - understanding
      - tdd_cycle_status
      - test_results_summary
      - next_steps
  refactor:
    blocks:
      - cortex_header
      - progress_tracker_standard
      - changes
      - validation_status
```

Verify: `grep -A 8 "response_templates:" cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`

### Step 5: Add response_templates to Debug Manifest
Edit `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`:
- Add at end:

```yaml
response_templates:
  investigation:
    blocks:
      - cortex_header
      - understanding
      - bug_hypothesis
      - approach
      - next_steps
  resolution:
    blocks:
      - cortex_header
      - changes
      - validation_status
      - next_steps
```

### Step 6: Add response_templates to Remaining Manifests
Repeat for these files in `cortex-brain/manifests/orchestrators/`:
- `cortex-lens-v3-manifest.yaml`
- `refinement-orchestrator-manifest.yaml`
- `code-sanitization-manifest.yaml`
- `technical-documentation-orchestrator-manifest.yaml`

Each should have appropriate `response_templates` section matching their operations.

### Step 7: Update Progress Bar Templates
Edit `cortex-brain\response-templates-v4.yaml` to align existing templates:
- Locate `autonomous_execution_progress` (around line 715)
- Update table headers to: `Phase | Progress | Status`
- Ensure bar width is 10 characters (10 blocks total: filled █ + empty ░)
- Use standardized icons: ✅ (complete), 🔄 (in-progress), ⏳ (pending), ❌ (failed), ⏸️ (skipped)

Verify:
```powershell
# Find the autonomous_execution_progress template
$content = Get-Content "cortex-brain\response-templates-v4.yaml" -Raw
$templateStart = $content.IndexOf("autonomous_execution_progress:")
if ($templateStart -ge 0) {
  $section = $content.Substring($templateStart, 500)
  Write-Host "Template found at position $templateStart"
  $section | Select-String -Pattern "Phase|Progress|Status"
} else {
  Write-Host "❌ Template not found"
}

# Check for standardized icons
Select-String -Path "cortex-brain\response-templates-v4.yaml" -Pattern "✅|🔄|⏳|❌|⏸️" | Select-Object -First 10
```

**Expected Output:** Confirmation that table headers and icons are present in template.

### Step 8: Validate All Changes
```powershell
# Check YAML syntax (requires PyYAML installed)
try {
  python -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates-v4.yaml')); print('✅ Valid YAML')"
} catch {
  Write-Host "❌ YAML validation failed: $_" -ForegroundColor Red
  exit 1
}

# Verify all manifests have response_templates
$manifests = Get-ChildItem "cortex-brain\manifests\orchestrators\*-manifest.yaml"
$results = @()
foreach ($file in $manifests) {
  $hasTemplates = Select-String -Path $file.FullName -Pattern "response_templates:" -Quiet
  $status = if ($hasTemplates) { "✅" } else { "❌ (missing)" }
  $results += [PSCustomObject]@{
    File = $file.Name
    HasResponseTemplates = $status
  }
}
$results | Format-Table -AutoSize

# Count manifests with response_templates
$count = ($results | Where-Object { $_.HasResponseTemplates -eq "✅" }).Count
Write-Host "`nTotal manifests with response_templates: $count / $($manifests.Count)" -ForegroundColor $(if ($count -eq 8) { 'Green' } else { 'Yellow' })
```

**Expected Output:** 
- "✅ Valid YAML" confirmation
- Table showing all 8 manifests with ✅ status
- "Total manifests with response_templates: 8 / 8" in green

---

## ✅ Success Criteria
- [ ] `composable_blocks` section exists in `response-templates-v4.yaml`
  Verify: `grep "composable_blocks:" cortex-brain/response-templates-v4.yaml` returns match
- [ ] All 8 orchestrator manifests have `response_templates` section
  Verify: `grep -l "response_templates:" cortex-brain/manifests/orchestrators/*-manifest.yaml | wc -l` returns `8`
- [ ] Progress bars use standardized 10-character width
  Verify: Progress bars show 10 chars (e.g., `██████████` or `████████░░`)
- [ ] All progress bars use standardized icons: ✅ 🔄 ⏳ ❌ ⏸️
  Verify: `grep -E "✅|🔄|⏳|❌|⏸️" cortex-brain/response-templates-v4.yaml`
- [ ] YAML files are valid (no syntax errors)
  Verify: Python yaml.safe_load succeeds on all files
- [ ] Existing templates continue to work (no breaking changes)
  Verify: Run CORTEX with simple command and confirm response renders

---

## 📁 Files to Modify

| File | Change |
|------|--------|
| `cortex-brain/response-templates-v4.yaml` | Add `composable_blocks` section, align progress bars |
| `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/technical-documentation-orchestrator-manifest.yaml` | Add `response_templates` |

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```powershell
Remove-Item "d:\PROJECTS\CORTEX\.asif\backlog\25-orchestrator-composable-templates.md" -Force
```
