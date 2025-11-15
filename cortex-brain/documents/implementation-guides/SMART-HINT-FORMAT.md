# CORTEX Smart Hint Display Format

**Version:** 2.0 (Clean Format)  
**Purpose:** Visual template for displaying conversation capture suggestions  
**Status:** ✅ PRODUCTION

---

## 📐 Format Template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **CORTEX LEARNING OPPORTUNITY**

**This session has exceptional strategic value:**

✨ **Highlights:**
   • Multi-phase execution: Phase A + Phase B Milestone 1
   • Major efficiency win: 98% faster than estimated
   • Complete documentation: 4 comprehensive reports
   • Systematic planning: 10-step debugging roadmap
   • Quality: 70% implementation with clear continuation

📸 **Conversation Captured:**
   ✅ File created: `cortex-brain/conversation-vault/2025-11-13-path-1-execution-session.md`
   ✅ Ready to review and edit as needed
   ✅ Includes complete session analysis and learnings

📊 **Quality Score:** 31/10 (EXCEPTIONAL)

🎯 **Perfect example of:**
   • Incremental progress methodology
   • Strategic pause decisions
   • Systematic debugging approach
   • Documentation-first workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎨 Visual Design Principles

### 1. **Box Formatting**
- Use Unicode box drawing characters for borders
- Keep lines at 70 characters max for readability
- Clear visual separation from main content

### 2. **Emoji Usage**
- 💡 For "Learning Opportunity" header
- ✨ For highlights section
- 📸 For capture action
- 📊 For quality score
- 🎯 For use cases

### 3. **Content Structure**
- **Highlights:** Bullet points with key achievements
- **Conversation Captured:** File location and status
- **Quality Score:** Numerical + qualitative rating
- **Perfect example of:** Use cases for future reference

### 4. **Line Length**
- Max 70 characters per line
- Use bullet points for multi-item lists
- Break long descriptions into multiple bullets

---

## 📝 Usage Guidelines

### When to Show Smart Hint

**Show if:**
- Quality score ≥ GOOD (6+)
- Multi-phase planning present
- Challenge/Accept reasoning used
- Design decisions documented
- Strategic value for learning

**Don't Show if:**
- Simple Q&A exchanges
- Low quality score (<6)
- No strategic value
- User explicitly disabled hints

### Automatic File Creation

**Always:**
- Create file immediately in vault
- Use date-based naming: `YYYY-MM-DD-description.md`
- Include metadata at top (date, duration, quality score)
- Structure with clear sections
- Open file automatically for user review

**Never:**
- Just reference the file path
- Suggest manual creation
- Skip metadata
- Leave file empty

---

## 🔧 Implementation Example

### Before (Old Format - DON'T USE)
```
💡 **CORTEX LEARNING OPPORTUNITY**
This conversation has excellent strategic value: • Multi-phase planning: 4 phases • Challenge/Accept reasoning • Design decisions • File references: 3
📸 **Capture for future reference?** → Say: **"capture conversation"** → I'll save this discussion automatically → File will be created: cortex-brain/conversation-vault/2025-11-13-add-login-authentication.md → Review now or import to brain later
Quality Score: 12/10 (EXCELLENT)
```

### After (New Format - USE THIS)
```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **CORTEX LEARNING OPPORTUNITY**

**This conversation has excellent strategic value:**

✨ **Highlights:**
   • Multi-phase planning: 4 phases identified
   • Challenge/Accept reasoning throughout
   • Design decisions documented
   • File references: 3 components

📸 **Conversation Captured:**
   ✅ File created: `cortex-brain/conversation-vault/2025-11-13-add-login-authentication.md`
   ✅ Ready to review and edit as needed
   ✅ Includes complete implementation plan

📊 **Quality Score:** 12/10 (EXCELLENT)

🎯 **Perfect example of:**
   • Authentication implementation patterns
   • Security-first design approach
   • Systematic testing strategy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 Key Improvements

### 1. Readability
- ✅ Short lines (max 70 chars)
- ✅ Clear bullet points
- ✅ Visual hierarchy with sections
- ❌ No long run-on text

### 2. Actionability
- ✅ File already created
- ✅ Direct path shown
- ✅ Status indicators (✅)
- ❌ No manual steps needed

### 3. Visual Appeal
- ✅ Markdown formatting
- ✅ Box borders for separation
- ✅ Consistent emoji usage
- ❌ No dense text blocks

### 4. Information Density
- ✅ Key points highlighted
- ✅ Quality score prominent
- ✅ Use cases clear
- ❌ No unnecessary details

---

## 📦 Template Variables

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **CORTEX LEARNING OPPORTUNITY**

**This {session_type} has {quality_level} strategic value:**

✨ **Highlights:**
   {highlight_bullets}

📸 **Conversation Captured:**
   ✅ File created: `{file_path}`
   ✅ Ready to review and edit as needed
   ✅ {additional_context}

📊 **Quality Score:** {score}/10 ({quality_level})

🎯 **Perfect example of:**
   {use_case_bullets}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔄 Integration with CORTEX.prompt.md

Update the Smart Hint section in CORTEX.prompt.md:

```markdown
**Smart Hint (Optional - CORTEX 3.0):**
- ✅ AFTER Response section, BEFORE Next Steps
- ✅ Show ONLY if conversation quality ≥ GOOD threshold
- ✅ Use clean format with max 70 chars per line
- ✅ Create file immediately, don't just reference
- ✅ Use box borders for visual separation
- ❌ Don't interrupt flow - optional enhancement only
```

---

*Format optimized for VS Code Copilot Chat display*  
*Last Updated: 2025-11-13 | CORTEX 3.0 Smart Hints Enhancement*
