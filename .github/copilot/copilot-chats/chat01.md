asifhussain60: update #file:cortex-epic-review.prompt.md  to 
Review .asif/AI-Learning/cortex6 folder to read the requirements (they should be converted to yaml) then review the live implementation against #file:source-of-truth epic and identify gaps 

GitHub Copilot: I'll update the epic review prompt to include reviewing the requirements in cortex6 and comparing against the live implementation to identify gaps. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-epic-review.prompt.md#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-epic-review.prompt.md#100-100), lines 100 to 250

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-epic-review.prompt.md#250-250), lines 250 to 400

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-epic-review.prompt.md#400-400), lines 400 to 663

Now I'll update the prompt to include reviewing the requirements from cortex6 folder and comparing against the live implementation: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Now let me add a new section to the executive summary template for requirements compliance: 

Using "Replace String in File"


```

```
Now let me add a section about analyzing the requirements folder structure: 

Using "Replace String in File"


```

```
Finally, let me update the references section to include the requirements folder: 

Using "Replace String in File"


```

```


Using "Replace String in File"


```

```
Perfect! Now let me create a summary of the changes:

## ✅ Updated Epic Review Prompt

I've successfully updated cortex-epic-review.prompt.md to include comprehensive requirements analysis and implementation comparison. Here's what was added:

### 🎯 Key Enhancements

**1. Requirements Discovery (Step 0 - NEW)**
- Scans cortex6 folder for all requirements
- Identifies non-YAML requirements (markdown, txt) that need conversion
- Defines expected YAML requirements structure

**2. Enhanced Context Loading (Step 1)**
- Added requirements YAML scanning
- Added live implementation scanning (`src/**/*.py`)
- Maps requirements to implementation files
- Includes orchestrator configs and system configs

**3. Requirements vs Implementation Comparison (Step 6)**
- **Missing Implementation Detection**: Requirements specified but not coded
- **Implementation Drift Detection**: Code doesn't match specification
- **Undocumented Implementation Detection**: Code exists without formal requirements
- Automatic gap categorization by severity

**4. New Gap Types**
- `MISSING_IMPLEMENTATION` (HIGH severity)
- `IMPLEMENTATION_DRIFT` (MEDIUM severity)  
- `UNDOCUMENTED_IMPLEMENTATION` (LOW severity)
- `MISSING_REQUIRED_IMPLEMENTATION` (CRITICAL severity)

**5. Enhanced Executive Summary**
- New "📐 REQUIREMENTS vs IMPLEMENTATION" section
- Specification compliance percentage
- Per-feature alignment scores with visual indicators
- Color-coded drift warnings

**6. Updated Execution Instructions**
- Explicit requirement loading step
- Implementation file scanning
- Specification compliance calculation
- Feature.yaml synchronization if drift detected

### 📊 New Report Section Example

The report now includes:
```
📐 REQUIREMENTS vs IMPLEMENTATION

Specification Compliance: 92%

Requirements Defined:     145
Implemented:             134 ████████████████░░░░ 92%
Missing:                  11 ███░░░░░░░░░░░░░░░░░  8%
Drifted from Spec:        5 █░░░░░░░░░░░░░░░░░░░  3%
Undocumented Code:        8 ██░░░░░░░░░░░░░░░░░░  5%
```

### ✨ Benefits

1. **Traceability**: Every requirement can be traced to implementation
2. **Quality Assurance**: Detects specification drift automatically
3. **Documentation**: Identifies undocumented code that needs specs
4. **Completeness**: Ensures all requirements are implemented
5. **YAML-First Compliance**: Encourages converting prose requirements to YAML

The epic review will now proactively identify gaps between what's specified and what's built, ensuring the CORTEX 6.0 build stays aligned with its requirements throughout development!

Made changes.

asifhussain60: Create a new plan to holistically remediate all these issues in .asif/AI-Learning/cortex6-fixes

GitHub Copilot: I'll create a comprehensive plan to holistically remediate all the issues identified in the epic review prompt. Let me first explore the current state and then create the plan. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.asif/AI-Learning)

Good, the `cortex6-fixes` folder already exists. Let me check its contents: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.asif/AI-Learning/cortex6-fixes)