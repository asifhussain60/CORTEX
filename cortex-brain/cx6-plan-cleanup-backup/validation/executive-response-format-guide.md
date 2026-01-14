# Executive Response Format - Quick Reference

**Version:** 1.0 | **Date:** 2026-01-11  
**Purpose:** Quick reference for GitHub Copilot responses

---

## Template (Copy This)

```markdown
## Executive Summary
[3-5 sentence paragraph: what was done, impact, next action]

## Outcomes
• [Quantified result with numbers]
• [Specific artifact created with path]
• [Status change or completion metric]
• [Max 5 bullets total]

## Risks
• [Explicit assumption made]
• [Conflict requiring manual review]
• [Max 3 bullets, OPTIONAL section]

## Decisions
• [Rule applied to resolve ambiguity]
• [Precedence used (e.g., Tier 0 > Tier 1)]
• [Max 3 bullets, OPTIONAL section]

## Next Steps
• [Actionable command: `python3 -m src.main "command"`]
• [File reference: see `path/to/file.ext`]
• [Max 3 bullets total]
```

---

## Rules

### DO ✅
- Start with 3-5 sentence executive summary paragraph
- Use bullet points for ALL lists
- Quantify outcomes (X files, Y AC-IDs, Z% complete)
- Include file paths in code format: `path/to/file.ext`
- Use progress bars for multi-step operations: `[████░░░░░░] 40%`
- Reference continuation files instead of duplicating content

### DON'T ❌
- Include code blocks (unless user says "show me the code")
- Write narrative paragraphs (use bullets)
- Describe step-by-step procedures (state outcomes)
- Nest sections deeper than 2 levels
- Exceed word limits (500 default, tier-based)

---

## Word Limits by Tier

| Tier | Max Words | Use Case |
|------|-----------|----------|
| INSTANT | 50 | Factual queries, status checks |
| FOCUSED | 200 | Single concept, quick updates |
| STRUCTURED | 400 | Multi-faceted operations |
| COMPREHENSIVE | 500 | Complex operations, full analysis |

**Override:** User can request `--max-words N`

---

## Section Limits

| Section | Max Items | Required? |
|---------|-----------|-----------|
| Executive Summary | 1 paragraph (3-5 sentences) | YES |
| Outcomes | 5 bullets | YES |
| Risks | 3 bullets | OPTIONAL |
| Decisions | 3 bullets | OPTIONAL |
| Next Steps | 3 bullets | YES |

---

## Examples

### ❌ WRONG (Verbose)

```
I have analyzed your request and will now proceed with the implementation. 
First, I'll examine the current codebase structure to understand the 
existing architecture. Then I'll create a detailed plan outlining each 
step required. After that, I'll begin implementing the feature by...

Step 1: Examine Directory Structure
- Look at src/ folder
- Check for existing implementations
- Identify dependencies

Step 2: Create Plan
- Define phases
- Assign AC-IDs
- Estimate time

[Continues for 200+ lines]
```

### ✅ RIGHT (Executive)

```
## Executive Summary
Analyzed 47 Python files and created implementation plan with 3 phases. 
Phase 1 infrastructure ready to start. 5 AC-IDs defined, all tests passing.

## Outcomes
• Analyzed 47 files across 8 modules
• Created plan: `cortex-brain/cx6-plan/feature-x-plan.yaml`
• Defined 5 AC-IDs (AC-FEAT-001 to AC-FEAT-005)
• All prerequisite tests passing (12/12)

## Next Steps
• Start Phase 1: `tdd implement AC-FEAT-001`
• Review plan: see `cortex-brain/cx6-plan/feature-x-plan.yaml`
```

**Word Count:** WRONG = 250+ | RIGHT = 85 ✅

---

## Code Block Rules

### ❌ Don't Include Code by Default

```
Here's the implementation:

\`\`\`python
def authenticate_user(username: str, password: str) -> bool:
    # Validate credentials
    user = db.get_user(username)
    if not user:
        return False
    return verify_password(password, user.password_hash)
\`\`\`
```

### ✅ Reference Implementation Location

```
## Outcomes
• Implemented authentication: `src/auth/authenticator.py`
• Created 5 tests: `tests/auth/test_authenticator.py`
• All tests passing (5/5)

## Next Steps
• Review code: see `src/auth/authenticator.py`
```

### ✅ Only Show Code When Explicitly Requested

**User:** "show me the authentication code"

**Response:** [Include code block only when user explicitly requests it]

---

## Progress Bar Format

**Standard:** 10-character width

```
`[████░░░░░░]` **40%** 🔄 In Progress
`[██████████]` **100%** ✅ Complete
`[██░░░░░░░░]` **20%** ⏳ Pending
```

**Table Format:**

```markdown
| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | `[████████░░]` 80% | 🔄 In Progress |
| Phase 2 | `[██░░░░░░░░]` 20% | ⏳ Pending |
```

---

## Continuation Prompts

**Always include at end of response:**

```markdown
📋 **Resume Work:** `continue {operation} {context}` *(see `{reference_file}`)*
```

**Examples:**

```
📋 **Resume Work:** `continue plan phase-1` *(see `cortex-brain/tier1/tracking/progress-tracker.json`)*

📋 **Resume Work:** `tdd continue user-auth` *(see `tests/auth/test_authenticator.py`)*

📋 **Resume Work:** `continue investigation auth-failure` *(see `cortex-brain/documents/investigations/auth-failure/00-investigation-report.md`)*
```

---

## Enforcement Checklist

Before sending response, verify:

- [ ] Executive summary paragraph exists (3-5 sentences)
- [ ] All lists use bullet points (•)
- [ ] Outcomes quantified (X files, Y AC-IDs, Z%)
- [ ] File paths in code format (`path/to/file`)
- [ ] No code blocks (unless explicitly requested)
- [ ] Word count ≤ tier limit
- [ ] Max sections: 5 for COMPREHENSIVE
- [ ] Continuation prompt included
- [ ] Next steps are actionable commands

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| "I will analyze..." | "Analyzed X files..." |
| "First, then, after..." | Use outcome bullets |
| Code blocks everywhere | Reference file paths only |
| 10+ bullet points | Max 5 per section |
| Nested subsections | Max 2 levels deep |
| Generic next steps | Specific commands with paths |
| No quantification | Add numbers (X files, Y%, Z AC-IDs) |

---

## Quick Comparison

| Aspect | Verbose Mode | Executive Mode |
|--------|-------------|----------------|
| **Length** | 200-500 lines | 10-30 lines |
| **Format** | Narrative paragraphs | Bullet points |
| **Code** | Shown inline | Referenced by path |
| **Steps** | Procedural description | Outcome declaration |
| **Sections** | 8+ nested | 5 flat |
| **Words** | 1000+ | 500 max |
| **Next Steps** | Generic suggestions | Specific commands |

---

## Configuration Reference

**Source Files:**
- `cortex-brain/response-templates-v4.yaml` (v4.2.0)
- `.github/prompts/CORTEX.prompt.md` (v6.4.0)

**Implementation:**
- GitHub Copilot enforces via prompt instructions
- Python TemplateRenderer (future implementation)
- Orchestrator manifests (reference executive_summary config)

**Override Syntax:**
```bash
python3 -m src.main "{request}" --max-words 1000
python3 -m src.main "{request}" --show-code
```

---

**Last Updated:** 2026-01-11  
**Next Review:** After 10 interactions to measure effectiveness
