# CORTEX Documentation Organizer

**Version:** 1.0.0  
**Type:** PowerShell Script  
**Category:** Operations  
**Platform:** Windows (PowerShell 5.1+)

---

## 🎯 Purpose

Analyzes and organizes the `docs/` folder structure by:
1. **Identifying misplaced files** at root level that should be in subfolders
2. **Building a complete link graph** to track all file references
3. **Detecting orphaned files** not linked anywhere in the navigation
4. **Moving files** to appropriate locations
5. **Updating all link references** to maintain site integrity
6. **Archiving or deleting** orphaned content

---

## 🚀 Quick Start

### Preview Changes (Dry Run - Safe)

```powershell
.\cortex-toolkit\docs-organizer.ps1
```

or

```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $true
```

### Execute Cleanup

```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false
```

### Execute with Confirmation

```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false -Force
```

### Delete Orphans Instead of Archiving

```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false -DeleteOrphans
```

---

## 📋 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-DryRun` | Switch | `$true` | Preview changes without modifying files |
| `-DeleteOrphans` | Switch | `$false` | Delete orphaned files instead of archiving |
| `-Force` | Switch | `$false` | Skip confirmation prompts |

---

## 🏗️ What It Does

### 1. Root-Level File Analysis

**Goal:** Keep root level clean with only essential infrastructure files.

**Whitelisted Root Files:**
- `index.html` - Main landing page
- `faq.html` - FAQ page (linked from index)
- `sitemap.html` - Site map (linked from index)
- `search-index.json` - Search index
- `404.md` - GitHub Pages 404
- `README.md` - Repository README
- `DEPLOYMENT.md` - Deployment guide
- `QUICK-LAUNCH.md` - Quick launch guide
- `.nojekyll`, `.deployment-trigger`, `.trigger` - Infrastructure

**Files to Move:**
- `dashboard-diagnostic.html` → `lens/diagnostics/`
- `test-tabs.html` → `prototypes/`
- `testing-planning-orchestrator.md` → `development/testing/`
- `visual-differentiation-demo.html` → `prototypes/`

### 2. Link Graph Building

**How it works:**
1. Scans all HTML files recursively
2. Extracts all `href=""` and `src=""` references
3. Resolves relative paths (`../`, `./`)
4. Builds reverse link map (what links TO each file)
5. Identifies orphaned files (no incoming links)

**Example:**
```
index.html
  ├── links to → architecture/index.html
  ├── links to → knowledge/index.html
  └── links to → story/viewer.html

architecture/index.html
  ├── links to → brain-tiers.html
  └── links to → skull-protection.html

ORPHAN: prototypes/old-design.html (no links to this file)
```

### 3. Orphan Detection & Categorization

**Categories:**
- **Story Chapters** - `story/Chapter-NN/index.html` (may need navigation)
- **Old/Backup Files** - `*-old.html`, `index-old.html` (safe to delete)
- **Prototypes** - Experimental UI components
- **Duplicates** - Content duplicated in `technical/` folders
- **Other** - Miscellaneous unlinked content

### 4. Link Reference Updates

**Before:**
```html
<a href="dashboard-diagnostic.html">Diagnostic Tool</a>
```

**After:**
```html
<a href="lens/diagnostics/dashboard-diagnostic.html">Diagnostic Tool</a>
```

All parent and child HTML files are scanned and updated automatically.

---

## 📊 Output

### Console Display

```
🧠 CORTEX Documentation Organizer v1.0.0
⚙️ Mode: DRY RUN (preview only)

🔍 Building link graph...
✅ Link graph built: 199 files, 39 orphaned

📂 Analyzing root-level files...
  ✅ Keep at root: 8
  📦 Move to subfolders: 4
  ⚠️  Review needed: 0

🔧 Executing cleanup...
  📦 Moving: dashboard-diagnostic.html → lens/diagnostics/
  📦 Moving: test-tabs.html → prototypes/
  📦 Moving: testing-planning-orchestrator.md → development/testing/
  📦 Moving: visual-differentiation-demo.html → prototypes/

🔗 Updating links in HTML files...
  ✅ Updated links in 1 files

📊 Report saved: cortex-brain/documents/reports/docs-cleanup-20260103.json

✅ Cleanup Complete!

Summary:
  📦 Files moved: 4
  🔗 Files with updated links: 1
  📁 Files archived: 0
  🗑️  Files deleted: 0

⚠️  Orphaned Files Found (39):
  📂 Story Chapters: 13
  📂 Old/Backup Files: 6
  📂 Prototypes: 3
  📂 Duplicates: 2
  📂 Other: 15

  💡 Tip: Run with -DeleteOrphans to remove old files, or review report at:
     cortex-brain/documents/reports/docs-cleanup-20260103.json

⚠️  DRY RUN MODE - No changes were made
Run with -DryRun $false to execute
```

### JSON Report

Saved to: `cortex-brain/documents/reports/docs-cleanup-YYYYMMDD.json`

```json
{
  "Timestamp": "2026-01-03T...",
  "DryRun": true,
  "DocsRoot": "d:\\PROJECTS\\CORTEX\\docs",
  "RootAnalysis": {
    "Keep": ["index.html", "faq.html", ...],
    "Move": [
      {
        "File": "dashboard-diagnostic.html",
        "Target": "lens/diagnostics/",
        "Linked": false
      }
    ]
  },
  "LinkGraph": {
    "TotalFiles": 199,
    "LinkedFiles": 160,
    "OrphanedFiles": 39
  },
  "OrphanedFiles": [
    "story/Chapter-01/index.html",
    "architecture/index-old.html",
    ...
  ],
  "Actions": {
    "FilesToMove": [...],
    "LinksToUpdate": [...],
    "FilesToArchive": [...],
    "FilesToDelete": [...]
  }
}
```

---

## 🔄 Workflow

### Typical Usage

1. **Initial Analysis (DRY RUN)**
   ```powershell
   .\cortex-toolkit\docs-organizer.ps1
   ```
   Review console output and JSON report.

2. **Review Orphaned Files**
   - Check `OrphanedFiles` in report
   - Decide: Archive, Delete, or Add Navigation
   - Update `$MoveMap` or `$DeletePatterns` if needed

3. **Execute Cleanup**
   ```powershell
   .\cortex-toolkit\docs-organizer.ps1 -DryRun $false
   ```

4. **Verify Changes**
   - Test navigation on local server
   - Verify links work correctly
   - Check archived files if needed

5. **Commit Changes**
   ```powershell
   git add docs/
   git commit -m "docs: reorganize structure and clean orphaned files"
   ```

---

## 🎛️ Customization

### Add Files to Root Whitelist

Edit `$RootWhitelist` array:

```powershell
$RootWhitelist = @(
    'index.html',
    'faq.html',
    'sitemap.html',
    'your-new-file.html'  # Add here
)
```

### Configure File Moves

Edit `$MoveMap` hashtable:

```powershell
$MoveMap = @{
    'dashboard-diagnostic.html' = 'lens/diagnostics/'
    'my-prototype.html' = 'prototypes/'  # Add here
}
```

### Auto-Delete Patterns

Edit `$DeletePatterns` array:

```powershell
$DeletePatterns = @(
    '*-old.html',
    '*-backup.html',
    '*-test.html',
    '*.tmp',
    '*-draft.html'  # Add here
)
```

---

## 🛡️ Safety Features

1. **Dry Run Default** - Always previews first
2. **Archiving** - Orphaned files moved to `docs/archives/cleanup-TIMESTAMP/`
3. **JSON Report** - Complete audit trail of all actions
4. **Confirmation Prompts** - Unless `-Force` is used
5. **Path Validation** - Checks existence before moving
6. **Link Resolution** - Handles `../`, `./`, absolute paths correctly

---

## 🔧 Troubleshooting

### "Link graph shows too many orphans"

**Cause:** Links may use query strings, anchors, or JavaScript navigation.

**Solution:** Review the report manually. Some "orphans" may be intentional (prototypes, tests).

### "Links not updating correctly"

**Cause:** Complex relative path resolution or dynamic links.

**Solution:** Check the `LinksToUpdate` in the JSON report. May need manual verification.

### "Script fails on special characters"

**Cause:** File names with spaces, Unicode, or special chars.

**Solution:** Rename files to use hyphens instead of spaces, avoid special characters.

---

## 📚 Integration

### Run as Part of Maintenance

```powershell
# Include in maintenance pipeline
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false -Force
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
pwsh -Command ".\cortex-toolkit\docs-organizer.ps1 -DryRun | Select-String 'orphaned'"
```

### CI/CD Validation

```yaml
# .github/workflows/docs-check.yml
- name: Check docs organization
  run: |
    pwsh -Command ".\cortex-toolkit\docs-organizer.ps1 -DryRun"
```

---

## 📈 Metrics Tracked

- Total HTML files scanned
- Root-level files analyzed
- Files moved to subfolders
- Links updated
- Files archived
- Files deleted
- Orphaned files by category

---

## 🎯 Future Enhancements

- [ ] Markdown file support (`.md`)
- [ ] JavaScript link extraction (dynamic navigation)
- [ ] Sitemap.xml generation
- [ ] Broken link detection (404s)
- [ ] Image reference validation
- [ ] CSS/JS asset cleanup
- [ ] Auto-generate navigation menus

---

## 📖 Related Tools

- **cortex-deploy** - Deployment to publish directory
- **cortex-health** - System health checks (includes docs validation)
- **cortex-cleanup** - General cleanup operations

---

## 📝 Version History

### v1.0.0 (2026-01-03)
- ✅ Initial release
- ✅ Root file analysis
- ✅ Link graph building
- ✅ Orphan detection
- ✅ File moving with link updates
- ✅ Archive/delete options
- ✅ JSON report generation
- ✅ Categorized orphan display

---

**Author:** CORTEX Toolkit Manager  
**License:** MIT  
**Support:** https://github.com/asifhussain60/CORTEX/issues
