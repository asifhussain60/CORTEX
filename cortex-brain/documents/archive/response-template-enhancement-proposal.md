# Planning System - Response Template Enhancement Proposal

**Version:** 3.0.0  
**Author:** Asif Hussain  
**Date:** 2024-12-14  
**Status:** Proposed

---

## 🎯 Executive Summary

Enhance CORTEX response template system to support Planning System with:
- **Controlled verbosity** based on operation complexity
- **Visual ASCII progress bars** in all planning responses
- **Quick links** section with clickable file paths
- **Alphabet selection** (A, B, C) for autonomous continuation
- **Tiered response formats** matching operation tiers (1-4)

---

## 📊 Current State Analysis

### Existing Template Structure
```yaml
base_templates:
  - standard_5_part         # Default 5-section format
  - success_completion      # 🎉 CONGRATULATIONS format
  - tech_aware_response     # Cloud provider aligned
  - compact_format          # Minimal output

shared:
  - progress_bar            # Basic progress visualization
  - plan_file_link          # File path links
  - autonomous_execution    # Execution progress tracking
```

### Gaps Identified

1. **No Tiered Verbosity Control**
   - All responses use same detail level
   - No complexity-based scaling
   - Tier 1 operations get verbose output

2. **Inconsistent Progress Visualization**
   - Progress bars exist but not standardized
   - No unified placement (top vs bottom)
   - Missing from planning responses

3. **File Links Scattered**
   - Links embedded in response body
   - No dedicated "Quick Links" section
   - Non-clickable paths in some templates

4. **No Alphabet Selection Pattern**
   - Next steps use numbered lists
   - No standardized autonomous triggers
   - "A, B, C" selection not implemented

---

## 🏗️ Proposed Solution

### 1. Tiered Response Templates

Create 4 response templates matching operation tiers:

```yaml
base_templates:
  tier1_instant:           # <2s operations, minimal output
  tier2_lightweight:       # <10s operations, medium detail
  tier3_documented:        # Planning operations, full detail
  tier4_complex:           # Architecture changes, comprehensive
```

**Tier 1 (Instant) - Minimal Verbosity:**
```markdown
## 🧠 CORTEX {Operation}
**Author:** Asif Hussain

✅ {Brief confirmation}
{Single line result}
```

**Tier 2 (Lightweight) - Medium Verbosity:**
```markdown
## 🧠 CORTEX {Operation}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 What Was Done
{2-3 sentences}

### 📊 Result
{Key metrics or changes}
```

**Tier 3 (Documented) - Full 5-Part Format:**
```markdown
## 🧠 CORTEX {Operation}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{Standard 5-part format}

[... full format ...]

### 🔗 Quick Links
{Clickable file links}

### 📊 Progress
{Visual progress bar}

### 🔍 Next Steps
{Alphabet selection}
```

**Tier 4 (Complex) - Comprehensive Format:**
```markdown
# 🧠 CORTEX {Operation} - Phase {N}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{Detailed understanding}

### ⚡ Approach & Considerations
{Complexity analysis, dependencies, risks}

### 💬 Response
{Comprehensive response with subsections}

### 📊 Impact & Changes
{Detailed change log}

### 🔗 Quick Links
📋 **Main Plan:** [cortex-3.9-master.md](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/cortex-3.9-master.md)
📄 **Manifest:** [manifest.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/manifest.yaml)
🧠 **Brain Rules:** [brain-protection-rules.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml)

### 📊 Progress
┌─────────────────────────────────────────────────────────────────────────────┐
│ CORTEX Evolution v3.9 - Phase 03: Planning Orchestrator 3.0                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: [███████░░░░░░░░░░░░░░░░░░] 35% (6/17 phases)           │
│ Phase Progress:   [████████████░░░░░░░░░░░░░] 50% (3/6 hours)             │
│ Elapsed Time:     18.5 hours                                                │
└─────────────────────────────────────────────────────────────────────────────┘

### 🔍 Next Steps

**Choose Your Path:**

**A.** 🚀 **Continue Autonomously** - Complete remaining 4 tasks in this phase
   - Task 4: Integrate refactor cycle invocation
   - Task 5: Integrate vacuum cycle invocation
   - Task 6: Add version synchronization
   - Estimated: 2.5 hours remaining

**B.** ⏭️  **Next Phase Only** - Skip to Phase 04: ADO Orchestrator 3.0
   - Current phase saved (resume later)
   - Move to next phase
   
**C.** ⏸️  **Pause & Review** - Stop for user review
   - Current progress saved
   - Resume anytime: "Continue from Phase 03"

**To Proceed:** Type **A**, **B**, or **C** (or say "continue", "next phase", "pause")
```

### 2. Standardized Quick Links Section

**Template Structure:**
```yaml
shared:
  quick_links:
    format: |
      ### 🔗 Quick Links
      
      {main_file_link}
      {key_files}
      
      💡 **Tip:** Click file names to open in VS Code editor
    
    main_file_link:
      format: "📋 **Main Plan:** [{filename}](file:///{absolute_path})"
    
    key_file_link:
      format: "📄 **{label}:** [{filename}](file:///{absolute_path})"
```

**Example Output:**
```markdown
### 🔗 Quick Links

📋 **Main Plan:** [cortex-3.9-master.md](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/cortex-3.9-master.md)
📄 **Manifest:** [manifest.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/manifest.yaml)
🧠 **Governance:** [brain-protection-rules.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml)
⚙️  **Config:** [cortex.config.json](file:///d:/PROJECTS/CORTEX/cortex.config.json)

💡 **Tip:** Click file names to open in VS Code editor
```

### 3. Visual ASCII Progress Bar (Standardized)

**Template Structure:**
```yaml
shared:
  progress_visualization:
    tier3_format: |
      ### 📊 Progress
      
      ┌─────────────────────────────────────────────────────────────────────────────┐
      │ {plan_name} - {phase_name}                                                  │
      ├─────────────────────────────────────────────────────────────────────────────┤
      │ Overall Progress: [{overall_bar}] {overall_pct}% ({phases_done}/{phases_total} phases) │
      │ Phase Progress:   [{phase_bar}] {phase_pct}% ({tasks_done}/{tasks_total} tasks)        │
      │ Elapsed Time:     {elapsed_time}                                            │
      │ Estimate:         {estimate_remaining}                                      │
      └─────────────────────────────────────────────────────────────────────────────┘
    
    tier4_format: |
      ### 📊 Progress
      
      ┌─────────────────────────────────────────────────────────────────────────────┐
      │ {plan_name} - {phase_name}                                                  │
      ├─────────────────────────────────────────────────────────────────────────────┤
      │ Overall Progress: [{overall_bar}] {overall_pct}% ({phases_done}/{phases_total} phases) │
      │ Phase Progress:   [{phase_bar}] {phase_pct}% ({tasks_done}/{tasks_total} tasks)        │
      │                                                                             │
      │ Time Tracking:                                                              │
      │   • Actual:      {actual_time} hours (development only)                    │
      │   • Elapsed:     {elapsed_time} hours (calendar time)                      │
      │   • Remaining:   {estimate_remaining}                                      │
      │   • Senior Dev:  {senior_dev_estimate} (baseline)                          │
      └─────────────────────────────────────────────────────────────────────────────┘

bars:
  characters:
    filled: "█"
    empty: "░"
    partial: "▒"
  
  length: 30  # Standard bar width
  
  calculation: |
    progress_ratio = completed / total
    filled_blocks = floor(progress_ratio * length)
    bar = (filled * filled_blocks) + (empty * (length - filled_blocks))
```

**Progress Bar Placement:**
- **Tier 1/2:** No progress bar (operations complete instantly)
- **Tier 3:** After Impact section, before Next Steps
- **Tier 4:** After Impact section, before Next Steps (enhanced format)

### 4. Alphabet Selection Pattern

**Template Structure:**
```yaml
shared:
  alphabet_selection:
    format: |
      ### 🔍 Next Steps
      
      **Choose Your Path:**
      
      {option_a}
      
      {option_b}
      
      {option_c}
      
      **To Proceed:** Type **A**, **B**, or **C** (or say "{trigger_words}")
    
    option_a:
      format: |
        **A.** 🚀 **{label}** - {description}
           {details}
           {estimate}
    
    option_b:
      format: |
        **B.** ⏭️  **{label}** - {description}
           {details}
    
    option_c:
      format: |
        **C.** ⏸️  **{label}** - {description}
           {details}
    
    trigger_words:
      option_a: ["continue", "go", "proceed", "A"]
      option_b: ["next phase", "skip", "B"]
      option_c: ["pause", "stop", "review", "C"]
```

**Standard Options:**

**Option A - Continue Autonomously:**
- Label: "Continue Autonomously"
- Description: Complete all remaining tasks in current phase/plan
- Details: List of remaining tasks with estimates
- Trigger: "continue", "go", "proceed", "A"

**Option B - Next Phase Only:**
- Label: "Next Phase Only"
- Description: Skip to next phase, save current progress
- Details: Next phase name and overview
- Trigger: "next phase", "skip", "B"

**Option C - Pause & Review:**
- Label: "Pause & Review"
- Description: Stop for user review, save progress
- Details: Resume instructions
- Trigger: "pause", "stop", "review", "C"

### 5. Response Template YAML Updates

**New Template Sections:**
```yaml
# Planning System Templates
templates:
  planning_phase_progress:
    name: Planning Phase Progress
    tier: 4
    triggers:
      - phase_complete
      - phase_progress
    
    base_template: tier4_complex
    
    sections:
      understanding: "{phase_name} completed with {tasks_completed} tasks finished"
      challenge: "{challenge_description}"
      response: "{phase_summary}"
      impact: "{files_changed_list}"
      quick_links: true
      progress_bar: true
      alphabet_selection: true
    
    quick_links:
      main_file: "{plan_file_path}"
      key_files:
        - label: "Manifest"
          path: "{manifest_path}"
        - label: "Current Phase"
          path: "{current_phase_path}"
        - label: "Governance"
          path: "{governance_path}"
    
    progress_bar:
      overall:
        current: "{phases_completed}"
        total: "{phases_total}"
      phase:
        current: "{tasks_completed}"
        total: "{tasks_total}"
      time:
        actual: "{actual_hours}"
        elapsed: "{elapsed_hours}"
        remaining: "{estimate_remaining}"
    
    alphabet_selection:
      option_a:
        label: "Continue Autonomously"
        description: "Complete remaining {remaining_tasks} tasks"
        details: "{task_list}"
        estimate: "{time_estimate}"
      option_b:
        label: "Next Phase Only"
        description: "Move to Phase {next_phase_number}: {next_phase_name}"
        details: "Current progress saved"
      option_c:
        label: "Pause & Review"
        description: "Stop for user review"
        details: "Resume: 'Continue from Phase {current_phase_number}'"
  
  planning_tier1_instant:
    name: Planning Tier 1 Instant
    tier: 1
    triggers:
      - quick_operation
      - instant_command
    
    base_template: tier1_instant
    
    format: |
      ## 🧠 CORTEX {operation}
      **Author:** Asif Hussain
      
      ✅ {confirmation_message}
      {result_one_liner}
  
  planning_tier2_lightweight:
    name: Planning Tier 2 Lightweight
    tier: 2
    triggers:
      - lightweight_operation
      - single_file_change
    
    base_template: tier2_lightweight
    
    format: |
      ## 🧠 CORTEX {operation}
      **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
      
      ---
      
      ### 🎯 What Was Done
      {summary_2_3_sentences}
      
      ### 📊 Result
      {key_changes_or_metrics}
      
      ### 🔍 Next Steps
      {simple_next_action}
  
  planning_tier3_documented:
    name: Planning Tier 3 Documented
    tier: 3
    triggers:
      - feature_planning
      - documented_operation
    
    base_template: tier3_documented
    
    sections:
      understanding: true
      challenge: true
      response: true
      impact: true
      quick_links: true
      progress_bar: true
      next_steps: true
```

---

## 📋 Implementation Plan

### Phase 1: Template Structure (2 hours)
1. Create tier1_instant, tier2_lightweight base templates
2. Enhance tier3_documented, tier4_complex templates
3. Add shared.quick_links section
4. Add shared.progress_visualization section
5. Add shared.alphabet_selection section

### Phase 2: Progress Bar Standardization (1 hour)
1. Define bar characters (█, ░, ▒)
2. Implement bar calculation logic
3. Create tier3_format and tier4_format variants
4. Test with various progress percentages

### Phase 3: Quick Links Integration (1 hour)
1. Add file path resolution logic
2. Implement clickable link format (file:///)
3. Create main_file_link and key_file_link templates
4. Add to all Tier 3+ templates

### Phase 4: Alphabet Selection Pattern (1.5 hours)
1. Define option_a, option_b, option_c formats
2. Implement trigger word mapping
3. Add to planning templates
4. Create autonomous continuation logic

### Phase 5: Integration & Testing (1.5 hours)
1. Update Planning Orchestrator 3.0 to use new templates
2. Test all 4 tier levels
3. Validate progress bar rendering
4. Test alphabet selection triggers
5. Validate file link clicking

**Total Estimate:** 7 hours

---

## 🎯 Success Criteria

### Verbosity Control
- ✅ Tier 1 operations: <5 lines output
- ✅ Tier 2 operations: <15 lines output
- ✅ Tier 3 operations: Full 5-part format with enhancements
- ✅ Tier 4 operations: Comprehensive format with all sections

### Visual Progress
- ✅ ASCII progress bars in all Tier 3+ responses
- ✅ Consistent placement (after Impact, before Next Steps)
- ✅ Dual progress tracking (overall + phase)
- ✅ Time metrics visible (actual, elapsed, remaining)

### Quick Links
- ✅ Dedicated section in all Tier 3+ responses
- ✅ Main plan file always first
- ✅ Key files (≤4) with meaningful labels
- ✅ Clickable file:/// paths in VS Code

### Alphabet Selection
- ✅ Standard A/B/C format in all planning responses
- ✅ Clear descriptions for each option
- ✅ Task details and estimates in Option A
- ✅ Trigger word alternatives documented

---

## 🔄 Backward Compatibility

### Existing Templates
- ✅ All existing templates remain functional
- ✅ New templates extend, not replace
- ✅ Gradual migration path (no breaking changes)

### Operation Routing
- ✅ Tier detection via complexity_analyzer.py
- ✅ Template selection automatic based on tier
- ✅ Override mechanism for special cases

---

## 📖 Usage Examples

### Example 1: Tier 1 Instant Response
**Input:** `healthcheck`
**Output:**
```markdown
## 🧠 CORTEX Healthcheck
**Author:** Asif Hussain

✅ System healthy - All components operational
Brain: ✅ | Orchestrators: 8/8 | Agents: 2/2
```

### Example 2: Tier 3 Documented Response
**Input:** `plan new feature`
**Output:**
```markdown
## 🧠 CORTEX Feature Planning
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
Created incremental plan for "new feature" with 5 phases...

[... full 5-part format ...]

### 🔗 Quick Links
📋 **Main Plan:** [feature-plan.md](file:///...)
📄 **Manifest:** [manifest.yaml](file:///...)

### 📊 Progress
┌─────────────────────────────────────────────────────────────────┐
│ Feature Planning - Phase 1 of 5                                │
├─────────────────────────────────────────────────────────────────┤
│ Overall Progress: [██████░░░░░░░░░░░░] 20% (1/5 phases)       │
└─────────────────────────────────────────────────────────────────┘

### 🔍 Next Steps

**Choose Your Path:**

**A.** 🚀 **Continue Autonomously** - Complete all 5 phases
   - Phase 2: Implementation
   - Phase 3: Testing
   - Phase 4: Documentation
   - Phase 5: Integration
   Estimated: 18 hours

**B.** ⏭️  **Next Phase Only** - Execute Phase 2: Implementation
   - Current plan saved

**C.** ⏸️  **Pause & Review** - Stop for review
   - Resume: "Continue feature planning"

**To Proceed:** Type **A**, **B**, or **C** (or say "continue", "next phase", "pause")
```

### Example 3: Tier 4 Complex Response
**Input:** Phase 03 completion in cortex-evolution-v3.9
**Output:**
```markdown
# 🧠 CORTEX Evolution v3.9 - Phase 03 Complete
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
Phase 03: Planning Orchestrator 3.0 completed with tiered execution, automatic cycles, and version synchronization.

[... comprehensive details ...]

### 🔗 Quick Links
📋 **Main Plan:** [cortex-3.9-master.md](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/cortex-3.9-master.md)
📄 **Manifest:** [manifest.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/manifest.yaml)
📝 **Phase 03:** [phase-03-planning.md](file:///d:/PROJECTS/CORTEX/cortex-brain/documents/planning/cortex-evolution-v3.9/phase-03-planning.md)
🧠 **Governance:** [brain-protection-rules.yaml](file:///d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml)

### 📊 Progress
┌─────────────────────────────────────────────────────────────────────────────┐
│ CORTEX Evolution v3.9 - Phase 03: Planning Orchestrator 3.0                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: [████░░░░░░░░░░░░░░░░░░░░░░] 18% (3/17 phases)          │
│ Phase Progress:   [████████████████████████████] 100% (6/6 hours)          │
│                                                                             │
│ Time Tracking:                                                              │
│   • Actual:      6.0 hours (development only)                              │
│   • Elapsed:     12.5 hours (calendar time)                                │
│   • Remaining:   46-64 hours (14 phases)                                   │
│   • Senior Dev:  52-70 hours (baseline)                                    │
└─────────────────────────────────────────────────────────────────────────────┘

### 🔍 Next Steps

**Choose Your Path:**

**A.** 🚀 **Continue Autonomously** - Complete remaining 14 phases
   - Phase 04: ADO Orchestrator 3.0 (3h)
   - Phase 05: TDD Orchestrator 3.0 (4h)
   - Phase 06: Maintenance Orchestrator 3.0 (3h)
   - ... (11 more phases)
   Estimated: 46 hours remaining

**B.** ⏭️  **Next Phase Only** - Execute Phase 04: ADO Orchestrator 3.0
   - Apply Planning System patterns to ADO operations
   - Estimated: 3 hours

**C.** ⏸️  **Pause & Review** - Stop for user review
   - Current progress saved (3/17 phases complete)
   - Resume: "Continue from Phase 04"

**To Proceed:** Type **A**, **B**, or **C** (or say "continue", "next phase", "pause")
```

---

## 📊 Benefits Summary

### User Experience
- **Faster comprehension:** Tiered verbosity matches operation complexity
- **Clear progress:** Visual bars show exactly where you are
- **Easy navigation:** One-click file access
- **Autonomous control:** A/B/C selection empowers user choice

### Developer Experience
- **Consistent patterns:** Standard template structure
- **Easy maintenance:** Centralized template definitions
- **Flexible integration:** Tier-based automatic routing
- **Clear documentation:** Examples for each tier

### System Benefits
- **Token efficiency:** Tier 1/2 use minimal tokens
- **User engagement:** Progress visualization maintains context
- **Reduced friction:** Quick links eliminate path hunting
- **Autonomous capability:** Alphabet selection enables full automation

---

## 🔍 Next Steps

1. **Review Proposal:** Validate approach with user requirements
2. **Approve Template Structure:** Confirm tier definitions and formats
3. **Implement Phase 1:** Create base template structure (2h)
4. **Test Integration:** Validate with Planning Orchestrator 3.0
5. **Roll Out Gradually:** Start with Tier 3/4, add Tier 1/2 later
