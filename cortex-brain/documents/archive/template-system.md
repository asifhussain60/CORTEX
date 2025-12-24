# CORTEX Template System

**Purpose:** Template-based responses for instant help and status queries  
**Version:** 1.0  
**Status:** ✅ PRODUCTION

---

## ⚡ RESPONSE TEMPLATES (No Python Execution Needed!)

**When user says "help" or similar:**
1. Load #file:../../../cortex-brain/response-templates.yaml
2. Find matching trigger
3. Return pre-formatted response
4. **NO Python execution needed!**

---

## 🎯 CRITICAL: Template Trigger Detection

**BEFORE responding to ANY user request:**

1. **Check for template triggers** in #file:../../../cortex-brain/response-templates.yaml
2. **Planning Detection (PRIORITY)** - Check if user wants to plan:
   - Triggers: "plan", "let's plan", "plan a feature", "plan this", "help me plan", "planning", "feature planning", "i want to plan"
   - If matched: Load #file:../../../prompts/shared/help_plan_feature.md and activate interactive planning workflow
   - Context detection: "let's plan ADO feature" = planning + ADO context (no separate triggers needed)
3. **If no trigger match**: Proceed with natural language response using MANDATORY RESPONSE FORMAT

---

## 📋 Common Template Triggers

| Trigger | Response Template | Load From |
|---------|-------------------|-----------|
| `help`, `/help` | Quick command table | response-templates.yaml |
| `help detailed` | Categorized commands | response-templates.yaml |
| `status` | Implementation status | response-templates.yaml |
| `plan [feature]` | Interactive planning | help_plan_feature.md |
| `quick start` | First-time user guide | response-templates.yaml |

---

## 🧠 Contextual Intelligence

**CORTEX automatically adapts based on work context:**

| Work Type | Response Focus | Agents Activated | Template Style |
|-----------|---------------|------------------|----------------|
| **Feature Implementation** | Code + tests | Executor, Tester, Validator | Technical detail |
| **Debugging/Issues** | Root cause analysis | Health Validator, Pattern Matcher | Diagnostic focus |
| **Testing/Validation** | Coverage + edge cases | Tester, Validator | Validation-centric |
| **Architecture/Design** | System impact | Architect, Work Planner | Strategic overview |
| **Documentation** | Clarity + examples | Documenter | User-friendly |
| **General Questions** | Concise answers | Intent Detector | Minimal detail |

**How it works:**
- Tier 2 Knowledge Graph learns from past interactions
- Pattern Matcher detects work context automatically
- Response templates adapt (but you can override anytime)

**User control:** Say "be more [concise/detailed/technical]" to adjust

---

## 📁 Template Integration Examples

### Example 1: Planning Workflow

```
User: "let's plan authentication"
→ MATCH: planning_triggers
→ ACTION: Create planning file, load help_plan_feature.md
→ RESPONSE: Interactive planning workflow in dedicated .md file

User: "let's plan ADO feature" + [screenshot]
→ MATCH: planning_triggers + vision API integration
→ ACTION: Analyze screenshot, create pre-populated ADO form
→ RESPONSE: "✅ Vision API extracted ADO-12345. Review template"
```

### Example 2: Help Request

```
User: "help"
→ MATCH: help_triggers
→ ACTION: Load response-templates.yaml, return help_table
→ RESPONSE: Pre-formatted command table
```

### Example 3: Natural Language (No Match)

```
User: "add a button"
→ NO MATCH: No triggers
→ ACTION: Natural language response
→ RESPONSE: Execute code implementation directly
```

---

**Why this matters:** Planning workflows require structured interaction with persistent artifacts (files). Without trigger detection, CORTEX skips planning templates and executes directly. Vision API integration extracts requirements from screenshots automatically. File-based planning creates persistent artifacts (not ephemeral chat).

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file
