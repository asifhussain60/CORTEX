# CORTEX User Repository Integration

**Purpose:** Lightweight integration instructions for adding CORTEX to existing user repositories without overwriting their copilot-instructions.md

---

## 🎯 Installation Guide

### If User Has NO `.github/copilot-instructions.md`

Simply copy CORTEX's copilot-instructions.md:

```powershell
Copy-Item ".github/copilot-instructions.md" "USER_REPO/.github/copilot-instructions.md"
```

### If User HAS `.github/copilot-instructions.md`

Add this lightweight reference to their **existing** file:

```markdown
---

## 🧠 CORTEX Integration

When user types `/CORTEX`, load `.github/prompts/CORTEX.prompt.md` for complete CORTEX instructions.

**CORTEX Features:** Planning, TDD, Architecture Intelligence, Code Review, Upgrade Management

**Quick Start:** Type `/CORTEX` or `help cortex` in GitHub Copilot Chat
```

This approach:
- ✅ Non-invasive (only 8 lines added)
- ✅ Preserves user's existing instructions
- ✅ Clearly separates CORTEX from user's project instructions
- ✅ Provides enough context for Copilot to find CORTEX.prompt.md

---

## 🔧 Installation Script

**For automated installation:**

```powershell
# Check if user has copilot-instructions.md
$userInstructionsPath = "USER_REPO/.github/copilot-instructions.md"

if (Test-Path $userInstructionsPath) {
    # Append CORTEX integration
    $cortexIntegration = @"

---

## 🧠 CORTEX Integration

When user types ``/CORTEX``, load ``.github/prompts/CORTEX.prompt.md`` for complete CORTEX instructions.

**CORTEX Features:** Planning, TDD, Architecture Intelligence, Code Review, Upgrade Management

**Quick Start:** Type ``/CORTEX`` or ``help cortex`` in GitHub Copilot Chat
"@
    
    Add-Content -Path $userInstructionsPath -Value $cortexIntegration
    Write-Host "✅ Added CORTEX integration to existing copilot-instructions.md"
} else {
    # Copy CORTEX's full instructions
    Copy-Item ".github/copilot-instructions.md" $userInstructionsPath
    Write-Host "✅ Created new copilot-instructions.md with CORTEX"
}
```

---

## 📋 Verification

After installation, test in GitHub Copilot Chat:

1. **Open new chat window**
2. **Type:** `/CORTEX`
3. **Expected:** Full CORTEX response with 5-part format
4. **If generic response:** Type `Follow instructions in CORTEX.prompt.md`

---

## 🔄 Upgrade Strategy

When CORTEX upgrades:
- **Full instructions (no user file):** Overwrite entire file ✅
- **Lightweight integration (user has file):** No changes needed ✅
- **User's instructions preserved:** Always ✅

---

**Author:** Asif Hussain  
**Version:** 3.7.0  
**License:** Source-Available (Use Allowed, No Contributions)
