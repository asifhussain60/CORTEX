# PowerShell Script Best Practices - Learned from Experience

**Source:** Multi-threaded crawler debugging (2025-11-04)  
**Confidence:** 0.95+ (battle-tested)  
**Purpose:** Prevent common PowerShell scripting issues

---

## 🚨 Critical Issues & Solutions

### 1. Regex Quote Escaping ⚠️ HIGH IMPACT

**Problem:** Backtick escaping for quotes in regex patterns fails to parse

**❌ WRONG - Causes Parse Errors:**
```powershell
# These ALL fail to parse:
$match = [regex]::Match($text, "[`'\""](.*)[ `'\"\"']")
$match = [regex]::Match($text, '[`"'](.*)[`"'']')
$match = [regex]::Matches($text, "\.locator\([`'\""]([^`'\""]+ )[`'\"\"]\)")
```

**✅ CORRECT - Use Hex Escape Sequences:**
```powershell
# Single quote: \x27
# Double quote: \x22
$match = [regex]::Match($text, '[\x27\x22](.*)[ \x27\x22]')
$match = [regex]::Matches($text, "\.locator\([\x27\x22]([^\x27\x22]+)[\x27\x22]\)")
```

**Why:** PowerShell parser gets confused with backtick+quote combinations. Hex codes are unambiguous.

**Frequency:** Affected 5 regex patterns in crawler scripts  
**Confidence:** 0.95

---

### 2. Path Handling for KDS Location ⚠️ HIGH IMPACT

**Problem:** Hardcoded `\KDS\` prefix causes path doubling when workspace IS KDS

**❌ WRONG - Path Doubling:**
```powershell
# When $WorkspaceRoot = "D:\PROJECTS\KDS"
$brainDir = "$WorkspaceRoot\KDS\kds-brain"
# Results in: D:\PROJECTS\KDS\KDS\kds-brain  ❌
```

**✅ CORRECT - Detect KDS Location:**
```powershell
# Normalize and detect
$normalizedRoot = $WorkspaceRoot.TrimEnd('\')
if ($normalizedRoot -match '\\KDS$') {
    # Workspace IS KDS
    $brainDir = "$normalizedRoot\kds-brain"
} else {
    # KDS is inside workspace
    $brainDir = "$normalizedRoot\KDS\kds-brain"
}
```

**Why:** KDS can be standalone repo or embedded in larger workspace

**Frequency:** Affected 6 crawler scripts  
**Confidence:** 0.98

---

### 3. Start-Job Parameter Passing ⚠️ MEDIUM IMPACT

**Problem:** `Start-Job -FilePath` fails with complex parameter passing

**❌ WRONG - FilePath Issues:**
```powershell
$job = Start-Job -FilePath $scriptPath -ArgumentList $WorkspaceRoot
# Error: Missing ')' in method call (confusing error message)
```

**✅ CORRECT - Use ScriptBlock:**
```powershell
$job = Start-Job -ScriptBlock {
    param($ScriptPath, $WorkspaceRoot)
    & $ScriptPath -WorkspaceRoot $WorkspaceRoot
} -ArgumentList $scriptPath, $WorkspaceRoot
```

**Why:** `-ScriptBlock` provides more reliable parameter passing for parallel jobs

**Frequency:** 1 occurrence (orchestrator.ps1)  
**Confidence:** 0.90

---

### 4. PowerShell Module Dependencies ⚠️ HIGH IMPACT

**Problem:** Missing modules cause cryptic errors at runtime

**❌ WRONG - Assume Module Exists:**
```powershell
# This fails if powershell-yaml not installed
$yaml = ConvertFrom-Yaml -Yaml $content
# Error: The term 'ConvertFrom-Yaml' is not recognized...
```

**✅ CORRECT - Check and Install:**
```powershell
# Check if module available
if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
    Write-Warning "powershell-yaml module required"
    Write-Host "Install with: Install-Module -Name powershell-yaml -Scope CurrentUser"
    exit 1
}

Import-Module powershell-yaml -ErrorAction Stop
$yaml = ConvertFrom-Yaml -Yaml $content
```

**Required Modules for KDS:**
- `powershell-yaml` - For YAML operations (ConvertFrom-Yaml, ConvertTo-Yaml)

**Frequency:** 1 occurrence (feed-brain.ps1)  
**Confidence:** 1.0

---

## 🎯 Workflow Best Practices

### Debugging PowerShell Scripts in Jobs

**Pattern:** Test individually before using in Start-Job

**Steps:**
1. **Run script directly** with test parameters
   ```powershell
   .\script.ps1 -Param "test-value"
   ```

2. **Fix syntax errors** (especially regex patterns)
   - Check for backtick escaping issues
   - Validate regex patterns parse correctly

3. **Test various inputs**
   - Empty/minimal data
   - Large datasets
   - Edge cases (special characters, paths with spaces)

4. **Only then integrate with Start-Job**
   ```powershell
   $job = Start-Job -ScriptBlock { ... }
   ```

**Benefit:** Saves 30+ minutes debugging cryptic job errors  
**Confidence:** 0.95

---

## 📋 Pre-Flight Checklist for PowerShell Scripts

Before creating/modifying PowerShell scripts, verify:

### Regex Patterns
- [ ] No backtick escaping for quotes (use `\x27` and `\x22`)
- [ ] Patterns tested in PowerShell directly
- [ ] Special characters properly escaped

### Path Handling
- [ ] No hardcoded `\KDS\` prefix without detection
- [ ] Path normalization (.TrimEnd('\\'))
- [ ] Works for both standalone KDS and embedded scenarios

### Job Orchestration
- [ ] Using `-ScriptBlock` instead of `-FilePath` for complex params
- [ ] Parameters passed correctly via `-ArgumentList`
- [ ] Error handling for job failures

### Dependencies
- [ ] Required modules documented
- [ ] Module availability checked before use
- [ ] Clear error messages if module missing

### Testing
- [ ] Script tested directly (not just in jobs)
- [ ] Edge cases covered (empty data, large data, special chars)
- [ ] Error messages are helpful (not cryptic)

---

## 🧠 Integration with Code Executor

**When generating PowerShell scripts, Code Executor should:**

1. **Check knowledge graph** for `validation_insights.powershell_*` patterns
2. **Apply corrections** automatically (hex escaping, path detection)
3. **Include module checks** for known dependencies
4. **Use proven workflows** (test individually before jobs)
5. **Add comments** referencing these best practices

**Example:**
```powershell
# Using hex escape sequences for quotes (see PowerShell Best Practices)
# \x27 = single quote, \x22 = double quote
$matches = [regex]::Matches($Content, "\.locator\([\x27\x22]([^\x27\x22]+)[\x27\x22]\)")
```

---

## 📊 Impact Metrics

| Issue | Frequency | Time Lost | Confidence | Impact |
|-------|-----------|-----------|------------|--------|
| Regex escaping | 5 scripts | ~45 min | 0.95 | HIGH |
| Path doubling | 6 scripts | ~30 min | 0.98 | HIGH |
| Start-Job params | 1 script | ~15 min | 0.90 | MEDIUM |
| Missing modules | 1 script | ~10 min | 1.0 | HIGH |
| **TOTAL** | **13 fixes** | **~100 min** | **0.95 avg** | **HIGH** |

**Time Saved by Learning:** Future PowerShell scripts will avoid these issues automatically

---

## 🔄 Continuous Learning

**This knowledge should be updated when:**
- New PowerShell issues encountered
- Better solutions discovered
- Patterns validated across multiple scripts
- Community best practices emerge

**Maintenance:**
- Review quarterly
- Update confidence scores based on usage
- Add new patterns as they emerge
- Remove obsolete patterns (if better solutions found)

---

**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** 2026-02-04  
**Source:** Multi-threaded crawler debugging session
