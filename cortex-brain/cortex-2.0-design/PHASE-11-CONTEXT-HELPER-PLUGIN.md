# CORTEX 2.0 - Phase 11: Context Helper Plugin

**Created:** 2025-11-12  
**Status:** 🟡 DESIGN COMPLETE - Implementation Pending  
**Type:** Developer Utility Plugin  
**Priority:** MEDIUM  
**Dependencies:** Response Templates (Phase 5), Plugin System (Phase 1)

---

## 📋 Executive Summary

**Purpose:** Enable developers to quickly get CORTEX and application context through natural "Tell me how/what/why" requests in VS Code Copilot Chat.

**Key Insight:** This is NOT a documentation generator - it's a **developer utility** that delivers instant, contextual explanations and diagram prompts directly in Chat without creating files.

**Approach:** Leverage existing Response Templates system (Phase 5) + optional dynamic data plugin for real-time metrics.

**Footprint:** Zero new dependencies (uses Python `string.Template` built-in).

---

## 🎯 Problem Statement

### Current Pain Points

**Developers want:**
1. "Explain token optimization in simple terms" → Get answer in Chat immediately
2. "Show me how SKULL protection works" → Formatted explanation ready to share
3. "Create Gemini prompt for entry point diagram" → Copy/paste ready prompt
4. "What's my current module count?" → Real-time implementation stats

**Current reality:**
- Must navigate multiple markdown files
- Must read through verbose documentation
- Must manually create diagram prompts
- No quick way to get contextual help in Chat

### User Persona

**Primary User:** Developer working in VS Code, using GitHub Copilot Chat for CORTEX development

**Typical Workflow:**
```
1. Developer working on feature
2. Needs quick context: "How does token optimization work?"
3. CORTEX returns formatted markdown in Chat
4. Developer reads explanation inline, continues working
5. Total time: <10 seconds vs minutes of doc navigation
```

---

## 🏗️ Architecture Design

### Option A: Response Templates Only (Recommended - Phase 11.1)

**Implementation:** Add templates to existing `response-templates.yaml`

**Pros:**
- ✅ Zero new dependencies
- ✅ Instant response (<50ms)
- ✅ Already working infrastructure
- ✅ Static content (doesn't change often)
- ✅ No new code needed

**Cons:**
- ⚠️ Cannot show real-time data (e.g., current module count)
- ⚠️ Must update YAML when metrics change

**Use Cases:**
- Explain technical concepts (token optimization, SKULL, agents)
- Generate diagram prompts for Gemini
- Provide layman explanations
- Show architectural overviews

**Example Template:**

```yaml
# cortex-brain/response-templates.yaml

templates:
  # Developer Utility: Token Optimization Explanation
  explain_token_optimization:
    triggers:
      - "explain token optimization"
      - "how does token optimization work"
      - "token reduction details"
      - "tell me about token optimization"
    
    response_type: narrative
    context_needed: false
    verbosity: detailed
    
    content: |
      # 🎯 Token Optimization - Technical Explanation
      
      **Problem:** CORTEX 1.0 loaded 74,047 tokens (8,701 lines) on every request
      - Cost: $2.22 per request (GPT-4 pricing)
      - Time: 2-3 seconds to parse
      - Waste: 95% content irrelevant to request
      
      **Solution:** 4-tier optimization strategy
      
      ## 1. Modular Architecture (97% reduction)
      **Before:** Single 8,701-line monolithic file
      **After:** 8 focused modules (200-400 lines each)
      **How:** Load only needed modules via Intent Routing
      - User: "refresh story" → Load story.md only (400 lines)
      - User: "setup environment" → Load setup-guide.md only (600 lines)
      
      ## 2. ML Context Compression (TF-IDF)
      **Algorithm:** scikit-learn TfidfVectorizer
      **Process:** 
      1. Chunk documentation into semantic units
      2. Score each chunk by relevance to user query
      3. Keep top N chunks (configurable: 5-15)
      4. Discard irrelevant context (50-80% reduction)
      
      ## 3. Cache Management (50k token limit)
      **Before:** Unlimited context accumulation
      **After:** Rolling 50k token window
      **How:** 
      - Track cumulative tokens per session
      - When > 50k: Drop oldest 20% of context
      - Preserves recent + high-relevance chunks
      
      ## 4. Smart Context Selection (Intent-based)
      **Zero-context scenarios:**
      - "what's 2+2?" → No CORTEX context needed
      - "explain Python syntax" → No CORTEX context needed
      **Selective loading:**
      - "Add auth" → Load executor + tester agents only
      - "Fix bug" → Load health validator + pattern matcher only
      
      ## Results (Measured)
      - **Tokens:** 74,047 → 2,078 avg (97.2% reduction)
      - **Cost:** $2.22 → $0.06 per request (97% savings)
      - **Time:** 2-3s → 80ms (97% faster)
      - **Annual Savings:** $25,920 (1000 requests/month)
      
      ## Implementation Files
      - `src/tier2/ml_context_optimizer.py` (TF-IDF compression)
      - `src/tier1/cache_manager.py` (Token limit enforcement)
      - `src/cortex_agents/intent_router.py` (Smart context selection)
      - `prompts/shared/*.md` (Modular documentation)
      
      ## Validation
      - Test suite: `tests/tier2/test_ml_context_optimizer.py`
      - Benchmarks: `prompts/validation/PHASE-3-VALIDATION-REPORT.md`
      - Token tracking: Real-time via Copilot API
      
      ---
      *Source: CORTEX 2.0 Phase 3 Validation Report*
      *© 2024-2025 Asif Hussain │ CORTEX Developer Utility*
  
  # Developer Utility: Generate Gemini Diagram Prompt
  diagram_token_optimization:
    triggers:
      - "create token optimization diagram"
      - "diagram for token optimization"
      - "gemini prompt token optimization"
    
    response_type: copyable_prompt
    context_needed: false
    verbosity: concise
    
    content: |
      # 🎨 Token Optimization Diagram - Gemini Prompt
      
      **Copy this entire block to Gemini Image Generator:**
      
      ```
      Create a professional technical diagram with three sections (Before/Engine/After):
      
      LEFT SECTION (Before - Red theme):
      - Large file icon labeled "monolithic.md"
      - Text: "74,047 tokens"
      - Text: "$2.22 per request"
      - Text: "8,701 lines"
      - Text: "2-3 seconds load time"
      
      CENTER SECTION (Optimization Engine - Purple theme):
      - Hexagon shape labeled "OPTIMIZATION ENGINE"
      - 4 internal components:
        1. "Modular Architecture" (folder icon, 8 modules)
        2. "ML Compression" (brain icon, TF-IDF algorithm)
        3. "Cache Management" (gauge icon, 50k limit)
        4. "Smart Selection" (target icon, Intent Routing)
      - Arrows flowing from left to right through engine
      
      RIGHT SECTION (After - Green theme):
      - Multiple small file icons (8 modules)
      - Text: "2,078 tokens (avg)"
      - Text: "$0.06 per request"
      - Text: "200-400 lines each"
      - Text: "80ms load time"
      
      BOTTOM BANNER (Blue theme):
      - "RESULTS" in large text
      - "97.2% Reduction │ $25,920/year Saved │ 97% Faster"
      
      STYLE:
      - Professional AWS architecture diagram aesthetic
      - Clean modern lines, no gradients
      - Color coding: Red (before), Purple (engine), Green (after), Blue (results)
      - Icons: Flat design, 2D style
      - Resolution: 1920x1080px
      - Font: Clean sans-serif (Helvetica/Roboto style)
      ```
      
      ---
      
      ## Human-Readable Description
      
      This diagram shows CORTEX 2.0's token optimization journey. The left side 
      depicts the bloated monolithic file (74K tokens, expensive, slow). The center 
      shows the 4-part optimization engine transforming the architecture. The right 
      side shows the lean modular result (2K tokens, 97% cheaper, 97% faster).
      
      The bottom results banner emphasizes the massive efficiency gains achieved.
      
      **Use Case:** Stakeholder presentations, architecture reviews, blog posts
      **Generated:** 2025-11-12 via CORTEX Context Helper
      
      ---
      *© 2024-2025 Asif Hussain │ CORTEX Developer Utility*
```

---

### Option B: Dynamic Context Plugin (Phase 11.2 - Optional Extension)

**Implementation:** Lightweight plugin for real-time data injection

**When to use:**
- User requests current module count: "How many modules are implemented?"
- User wants test status: "What's my current test coverage?"
- User asks about their app: "Explain my application architecture"

**Pros:**
- ✅ Real-time data (current module count, test stats)
- ✅ User application analysis (reads their code)
- ✅ Personalized context

**Cons:**
- ⚠️ 200 lines of new code
- ⚠️ Requires plugin maintenance

**File Structure:**

```
src/plugins/context_helper_plugin/
├── __init__.py
├── context_helper_plugin.py (main plugin - 200 lines)
├── templates/
│   ├── explanations/
│   │   ├── token_optimization.template.md
│   │   ├── skull_protection.template.md
│   │   └── agent_system.template.md
│   └── diagrams/
│       ├── architecture.template.md
│       └── token_optimization.template.md
└── context_gatherers/
    ├── cortex_metrics.py (gather current module count, tests)
    └── user_code_analyzer.py (analyze user's application)
```

**Example Plugin:**

```python
# src/plugins/context_helper_plugin/context_helper_plugin.py

from src.plugins.base_plugin import BasePlugin, PluginMetadata
from string import Template
from pathlib import Path
from typing import Dict, Any

class ContextHelperPlugin(BasePlugin):
    """Developer utility for 'Tell me how/what/why' requests."""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="context_helper",
            name="Context Helper Plugin",
            version="1.0.0",
            category=PluginCategory.UTILITY,
            priority=PluginPriority.MEDIUM,
            description="Quick context delivery for developers",
            author="Asif Hussain",
            dependencies=[],
            hooks=[],
            config_schema={}
        )
    
    def register_commands(self):
        return [
            CommandMetadata(
                command="explain",
                natural_language_equivalent="explain X / tell me about X",
                plugin_id=self.metadata.plugin_id,
                description="Explain CORTEX concepts",
                category=CommandCategory.UTILITY
            ),
            CommandMetadata(
                command="diagram",
                natural_language_equivalent="create diagram for X",
                plugin_id=self.metadata.plugin_id,
                description="Generate Gemini diagram prompts",
                category=CommandCategory.UTILITY
            )
        ]
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context.get('request', '').lower()
        
        if 'token optimization' in request:
            if 'diagram' in request:
                return self._diagram_token_optimization()
            else:
                return self._explain_token_optimization()
        
        elif 'skull' in request:
            return self._explain_skull_protection()
        
        elif 'module count' in request or 'how many modules' in request:
            return self._current_module_count()
        
        return {"success": False, "message": "Unknown context request"}
    
    def _explain_token_optimization(self) -> Dict[str, Any]:
        """Return explanation with real-time metrics."""
        
        # Gather current metrics (dynamic!)
        total_modules = self._count_modules()
        implemented_modules = self._count_implemented_modules()
        test_count = self._count_tests()
        
        template_path = Path(__file__).parent / "templates/explanations/token_optimization.template.md"
        template = Template(template_path.read_text())
        
        content = template.substitute(
            total_modules=total_modules,
            implemented_modules=implemented_modules,
            implementation_percent=round((implemented_modules / total_modules) * 100, 1),
            test_count=test_count,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return {
            "success": True,
            "output_type": "markdown",
            "content": content
        }
    
    def _diagram_token_optimization(self) -> Dict[str, Any]:
        """Generate Gemini prompt for token optimization diagram."""
        
        template_path = Path(__file__).parent / "templates/diagrams/token_optimization.template.md"
        template = Template(template_path.read_text())
        
        content = template.substitute(
            # Static content - could inject dynamic metrics if desired
        )
        
        return {
            "success": True,
            "output_type": "markdown",
            "content": content
        }
    
    def _current_module_count(self) -> Dict[str, Any]:
        """Real-time module implementation status."""
        
        total = self._count_modules()
        implemented = self._count_implemented_modules()
        percent = round((implemented / total) * 100, 1)
        
        return {
            "success": True,
            "output_type": "markdown",
            "content": f"""
# 📊 CORTEX Module Status (Live)

**Total Modules Defined:** {total}
**Modules Implemented:** {implemented}
**Completion:** {percent}%

**Breakdown by Operation:**
{self._module_breakdown_table()}

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Real-time data from CORTEX implementation*
"""
        }
    
    def _count_modules(self) -> int:
        """Count modules defined in cortex-operations.yaml."""
        # Implementation details...
        pass
    
    def _count_implemented_modules(self) -> int:
        """Count Python module files in src/operations/modules/."""
        # Implementation details...
        pass
```

---

## 🎯 Use Cases & Examples

### Use Case 1: Quick Concept Explanation

**User:** "explain token optimization"

**CORTEX Response:**
```markdown
# 🎯 Token Optimization - Technical Explanation

[Full formatted explanation appears in Chat]

**Problem:** 74,047 tokens loaded every request...
**Solution:** 4-tier optimization...
[... complete explanation ...]

---
*© 2024-2025 Asif Hussain │ CORTEX Developer Utility*
```

**User Action:** Reads in Chat, continues working

---

### Use Case 2: Diagram Prompt Generation

**User:** "create diagram for token optimization"

**CORTEX Response:**
```markdown
# 🎨 Token Optimization Diagram - Gemini Prompt

**Copy this entire block to Gemini Image Generator:**

```
Create professional technical diagram with three sections...
[... complete Gemini prompt ...]
```

## Human-Readable Description

This diagram shows CORTEX 2.0's token optimization...
[... explanation ...]
```

**User Action:** 
1. Copies Gemini prompt from Chat
2. Opens Gemini Image Generator
3. Pastes prompt
4. Generates diagram

---

### Use Case 3: Real-Time Metrics (Plugin Only)

**User:** "how many modules are implemented?"

**CORTEX Response:**
```markdown
# 📊 CORTEX Module Status (Live)

**Total Modules Defined:** 54
**Modules Implemented:** 24
**Completion:** 44.4%

**Breakdown by Operation:**
| Operation | Implemented | Total | Progress |
|-----------|-------------|-------|----------|
| Setup | 11 | 11 | 100% |
| Story Refresh | 6 | 6 | 100% |
| Cleanup | 6 | 6 | 100% |
| Documentation | 1 | 6 | 17% |
| Brain Protection | 0 | 6 | 0% |
| Test Execution | 0 | 5 | 0% |

**Last Updated:** 2025-11-12 14:32:45

---
*Real-time data from CORTEX implementation*
```

---

## 📊 Integration with Existing Systems

### Reusable Components

**1. GenerateImagePromptsModule (Already Exists)**

**Current:** Hardcoded strings in `generate_image_prompts_module.py`

**Refactor Opportunity:**
```python
# BEFORE (current - hardcoded)
def _generate_prompts_content(self) -> str:
    return """
    ### Diagram 1: Architecture
    Create a technical system architecture diagram showing...
    """

# AFTER (with Context Helper Plugin)
from src.plugins.context_helper_plugin import ContextHelperPlugin

def _generate_prompts_content(self) -> str:
    plugin = ContextHelperPlugin()
    
    diagrams = [
        plugin.execute({"request": "diagram token optimization"}),
        plugin.execute({"request": "diagram skull protection"}),
        plugin.execute({"request": "diagram entry point architecture"}),
    ]
    
    return "\n\n---\n\n".join([d['content'] for d in diagrams])
```

**Benefit:** Maintain prompts in templates, not hardcoded strings

---

**2. DocGenerator Workflow (Already Exists)**

**Current:** Individual generator methods in `doc_generator.py`

**Refactor Opportunity:**
```python
# BEFORE (current)
def _generate_overview(self, user_request: str) -> str:
    return f"This feature implements: {user_request}"

# AFTER (with Context Helper Plugin)
def _generate_overview(self, user_request: str) -> str:
    plugin = ContextHelperPlugin()
    result = plugin.execute({
        "request": f"explain feature {user_request}",
        "explanation_type": "feature_overview"
    })
    return result['content']
```

**Benefit:** Consistent formatting across all documentation

---

**3. Response Templates (Already Working)**

**Integration:** Context Helper templates live in `response-templates.yaml`

**No code changes needed** - just add templates!

```yaml
# cortex-brain/response-templates.yaml

templates:
  # Add Context Helper templates here
  explain_token_optimization:
    triggers: ["explain token optimization", "token optimization details"]
    response_type: narrative
    content: |
      [Explanation content]
```

---

## 🔧 Implementation Plan

### Phase 11.1: Response Templates (1 hour)

**Goal:** Enable static explanations and diagram prompts

**Tasks:**
1. Add 10 response templates to `response-templates.yaml`:
   - `explain_token_optimization`
   - `explain_skull_protection`
   - `explain_agent_system`
   - `explain_entry_point_modularization`
   - `diagram_token_optimization`
   - `diagram_skull_protection`
   - `diagram_entry_point_architecture`
   - `explain_layman_token_optimization`
   - `explain_technical_token_optimization`
   - `quickstart_cortex`

2. Test templates via Copilot Chat:
   ```
   "explain token optimization"
   "create diagram for token optimization"
   "explain SKULL protection"
   ```

3. Update entry point (`CORTEX.prompt.md`) with Context Helper examples

**Deliverables:**
- 10 new response templates (YAML additions)
- Updated entry point documentation
- Zero new dependencies

**Estimated Effort:** 1 hour

---

### Phase 11.2: Dynamic Context Plugin (Optional - 2-3 hours)

**Goal:** Enable real-time metrics and user application analysis

**Tasks:**
1. Create `src/plugins/context_helper_plugin/` directory structure
2. Implement `ContextHelperPlugin` class (200 lines)
3. Create 5 template files (explanations + diagrams)
4. Implement context gatherers:
   - `cortex_metrics.py` (module count, test stats)
   - `user_code_analyzer.py` (analyze user's code)
5. Register plugin with command registry
6. Add tests (`test_context_helper_plugin.py`)

**Deliverables:**
- 1 new plugin (200 lines)
- 5 template files
- 2 context gatherer utilities
- Test suite (20+ tests)
- Zero new dependencies

**Estimated Effort:** 2-3 hours

---

### Phase 11.3: Integration with Existing Systems (1 hour)

**Goal:** Refactor existing hardcoded prompts to use templates

**Tasks:**
1. Refactor `GenerateImagePromptsModule` to use Context Helper
2. Refactor `DocGenerator` workflow to use Context Helper
3. Update tests
4. Verify end-to-end functionality

**Deliverables:**
- 2 refactored modules
- Updated tests
- Cleaner, more maintainable code

**Estimated Effort:** 1 hour

---

## 📈 Success Metrics

### Phase 11.1 (Response Templates)

**Goal:** Enable instant context delivery for common requests

**Metrics:**
- ✅ 10 response templates added
- ✅ Templates load in <50ms
- ✅ Developer can get explanation without navigating docs
- ✅ Gemini prompts copy/paste ready

---

### Phase 11.2 (Dynamic Plugin - Optional)

**Goal:** Real-time CORTEX metrics and user app analysis

**Metrics:**
- ✅ Plugin loads in <200ms
- ✅ Current module count accurate (live data)
- ✅ User application analysis working
- ✅ 20+ tests passing

---

### Phase 11.3 (Integration)

**Goal:** Existing systems use Context Helper templates

**Metrics:**
- ✅ `GenerateImagePromptsModule` refactored
- ✅ `DocGenerator` refactored
- ✅ No hardcoded prompts remain
- ✅ All tests still passing

---

## 🎯 Acceptance Criteria

### Phase 11.1 (Minimum Viable Product)

- [ ] User can say "explain token optimization" → Get formatted answer in Chat
- [ ] User can say "create diagram for token optimization" → Get Gemini prompt
- [ ] User can say "explain SKULL protection" → Get detailed explanation
- [ ] All explanations include copyright footer
- [ ] Response time < 100ms (template loading)
- [ ] Zero new dependencies added

---

### Phase 11.2 (Dynamic Extension)

- [ ] User can say "how many modules are implemented?" → Get live count
- [ ] User can say "what's my test coverage?" → Get current stats
- [ ] Plugin loads in < 200ms
- [ ] Test suite passes (20+ tests)
- [ ] Zero new dependencies added

---

## 🚀 Next Steps

**Immediate (Phase 11.1):**
1. Review and approve this design document
2. Add 10 response templates to `response-templates.yaml`
3. Test in Copilot Chat
4. Update status documents

**Future (Phase 11.2 - Optional):**
1. Decide if real-time data is needed
2. Implement Dynamic Context Plugin
3. Integrate with existing systems

**Timeline:**
- Phase 11.1: 1 hour (response templates)
- Phase 11.2: 2-3 hours (dynamic plugin, if needed)
- Phase 11.3: 1 hour (integration, if Phase 11.2 done)

**Total Effort:** 1 hour (minimum) to 5 hours (complete with dynamic data)

---

## 📚 Related Documents

- `cortex-brain/response-templates.yaml` (existing infrastructure)
- `src/operations/modules/generate_image_prompts_module.py` (integration target)
- `src/workflows/stages/doc_generator.py` (integration target)
- `src/plugins/base_plugin.py` (plugin foundation)
- `.github/prompts/CORTEX.prompt.md` (entry point)

---

**Status:** 🟡 DESIGN COMPLETE - Awaiting approval for Phase 11.1 implementation

**Recommendation:** Start with Phase 11.1 (response templates only) - 1 hour effort, zero dependencies, immediate value for developers.

---

*© 2024-2025 Asif Hussain │ CORTEX 2.0 Phase 11 Design Document*
