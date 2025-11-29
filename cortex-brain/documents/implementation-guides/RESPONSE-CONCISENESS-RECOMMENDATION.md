# CORTEX Response Conciseness - Recommendations

**Created:** 2025-11-09  
**Issue:** CORTEX responses are too verbose for practical use  
**Status:** 🎯 ACTIONABLE RECOMMENDATIONS  
**Priority:** HIGH (User Experience Impact)

---

## 🎯 Problem Analysis

### Current Verbosity Issues

**What's happening:**
1. ✅ **Status updates are comprehensive** - Great for progress tracking
2. ✅ **Technical details are accurate** - Great for understanding
3. ❌ **Responses are too long** - User can't efficiently parse information
4. ❌ **Too much context upfront** - Progressive disclosure missing
5. ❌ **Implementation details before action** - Gets in the way

**Example: Recent response was 1,100+ words when 100-200 would suffice**

---

## ✅ Recommended Solution: 3-Tier Response System

### Tier 1: Quick Response (Default) 🎯

**Length:** 50-150 words  
**Format:** Status + Key Info + Next Step  
**When:** All responses unless user requests detail

```markdown
✅ **Synced with CORTEX-2.0**

**Status:** Ready to continue implementation  
**Current Phase:** Phase 5.1 (26% complete)  
**Environment:** Python 3.9.6 venv ✓, 1,531 tests passing ✓

**Recent Update:** Universal Operations system (5/40 modules working)

**Your Track (Mac):** Phase 5.5 YAML Conversion (ready to start)

What would you like to work on?
```

**Why this works:**
- ✅ User sees status immediately
- ✅ Actionable information upfront
- ✅ Can ask for more details if needed

---

### Tier 2: Detailed Context (On Request) 📊

**Length:** 200-400 words  
**Format:** Structured sections with collapsible details  
**When:** User says "give me details", "show more", "explain"

```markdown
<details>
<summary>📊 Detailed Status (click to expand)</summary>

### What Was Updated
- 56 files changed
- Universal operations system implemented
- 5 end-to-end tests added

### Your Current Track
According to Machine-Specific Work Plan:
- **Mac:** Phase 5.5 YAML Conversion
- **Windows:** Phase 5.1 Integration Tests
- **Timeline:** Week 10 of 34 (63% complete)

### Key Files
- `src/operations/` - New universal system
- `cortex-operations.yaml` - Operation registry
- Design docs in `cortex-brain/cortex-2.0-design/`

</details>
```

---

### Tier 3: Deep Dive (Expert Mode) 🔍

**Length:** Full technical detail  
**Format:** Complete analysis with code snippets  
**When:** User says "show technical details", "deep dive", "explain architecture"

*This is what CORTEX currently does by default - move it to Tier 3 only*

---

## 🔧 Implementation Options

### Option 1: Configuration Flag (RECOMMENDED) ⭐

**Add to `cortex.config.json`:**

```json
{
  "response_settings": {
    "verbosity_level": "concise",  // Options: "concise" | "detailed" | "expert"
    "default_word_limit": 150,
    "show_metadata": false,  // Tier 2+ only
    "show_recommendations": true,
    "progressive_disclosure": true,
    "use_collapsible_sections": true
  }
}
```

**Implementation:**
1. Update `ResponseFormatter` to respect `verbosity_level`
2. Add word count tracking
3. Implement progressive disclosure (expand/collapse)
4. Add natural language toggle commands

**Effort:** 2-3 hours  
**Files:** 
- `src/entry_point/response_formatter.py` (enhance)
- `cortex.config.json` (add settings)
- Tests: `tests/entry_point/test_response_formatter.py` (extend)

---

### Option 2: Natural Language Commands (EASIEST) ⚡

**User can control verbosity on-the-fly:**

```
"Give me a quick summary"        → Tier 1 (50-150 words)
"Show me details"                → Tier 2 (200-400 words)
"Explain in depth"               → Tier 3 (full detail)
"Be concise" or "Be brief"       → Sets default to Tier 1
"Show everything"                → Sets default to Tier 3
```

**Implementation:**
1. Add intent detection for verbosity requests
2. Store preference in conversation context (Tier 1)
3. Apply to all subsequent responses
4. Allow per-response override

**Effort:** 1-2 hours  
**Files:**
- `src/cortex_agents/right_brain/intent_detector.py` (add patterns)
- `src/tier1/conversation_manager.py` (store preference)
- Entry point prompt (add verbosity instructions)

---

### Option 3: Smart Defaults by Intent (INTELLIGENT) 🧠

**Auto-adjust verbosity based on request type:**

| Intent Type | Default Verbosity | Rationale |
|-------------|-------------------|-----------|
| STATUS, RESUME | Tier 1 (concise) | User wants quick overview |
| PLAN | Tier 2 (detailed) | User needs structured plan |
| EXECUTE | Tier 1 (concise) | User wants results, not process |
| EXPLAIN, LEARN | Tier 3 (expert) | User explicitly wants detail |
| DEBUG, VALIDATE | Tier 2 (detailed) | User needs diagnostic info |

**Implementation:**
1. Map intents to default verbosity levels
2. Override with user preference if set
3. Add "more" / "less" commands to adjust

**Effort:** 3-4 hours  
**Files:**
- `src/cortex_agents/right_brain/intent_detector.py` (mapping)
- `src/entry_point/response_formatter.py` (smart formatting)
- Design doc: Add verbosity rules to intent system

---

## 🎯 Recommended Approach (Hybrid)

**Combine all 3 for best UX:**

### Phase 1: Quick Win (1-2 hours) ✅
1. **Add natural language commands** (Option 2)
   - "be concise" / "show details" / "explain fully"
2. **Update entry point prompt** with verbosity guidance
3. **Set default to Tier 1** (50-150 words)

### Phase 2: Smart Defaults (2-3 hours) 📊
4. **Implement intent-based verbosity** (Option 3)
5. **Add word count tracking** to ResponseFormatter
6. **Store user preference** in Tier 1 conversation context

### Phase 3: Configuration (1-2 hours) ⚙️
7. **Add config settings** (Option 1)
8. **Add progressive disclosure** (collapsible sections)
9. **Comprehensive testing** for all verbosity levels

**Total Effort:** 4-7 hours  
**User Impact:** IMMEDIATE (Phase 1), ENHANCED (Phase 2-3)

---

## 📝 Specific Code Changes

### 1. Update Entry Point Prompt

**File:** `.github/prompts/CORTEX.prompt.md` or copilot-instructions

**Add this section after "How to Use CORTEX":**

```markdown
---

## 💬 Response Style & Verbosity

**Default:** CORTEX provides concise, actionable responses (50-150 words)

**You control detail level:**
- **Quick Summary** (default): Status + key info + next step
- **Show Details**: Structured breakdown with context (200-400 words)  
- **Explain Fully**: Complete technical detail with code

**Natural language commands:**
- "Be concise" or "Keep it brief" → Short responses
- "Show me details" or "Give me more context" → Medium detail
- "Explain in depth" or "Show everything" → Full detail
- "More" → Expand last response
- "Less" → Summarize last response

**Your preference persists** across the conversation until changed.

---
```

---

### 2. Enhance ResponseFormatter

**File:** `src/entry_point/response_formatter.py`

**Add verbosity parameter:**

```python
class ResponseFormatter:
    """Formats agent responses with configurable verbosity."""
    
    def __init__(self, default_verbosity: str = "concise"):
        """
        Initialize formatter.
        
        Args:
            default_verbosity: "concise" | "detailed" | "expert"
        """
        self.default_verbosity = default_verbosity
        self.word_limits = {
            "concise": 150,
            "detailed": 400,
            "expert": None  # No limit
        }
    
    def format(
        self,
        response: AgentResponse,
        verbosity: Optional[str] = None,
        include_metadata: bool = None,
        include_recommendations: bool = None,
        format_type: str = "text"
    ) -> str:
        """
        Format response with verbosity control.
        
        Args:
            response: AgentResponse to format
            verbosity: Override default verbosity level
            include_metadata: Auto-determined if None based on verbosity
            include_recommendations: Auto-determined if None
            format_type: "text" | "json" | "markdown"
        """
        verbosity = verbosity or self.default_verbosity
        
        # Auto-adjust metadata/recommendations based on verbosity
        if include_metadata is None:
            include_metadata = verbosity in ["detailed", "expert"]
        
        if include_recommendations is None:
            include_recommendations = verbosity in ["concise", "detailed"]
        
        # Format based on type
        if format_type == "json":
            formatted = self._format_json(response)
        elif format_type == "markdown":
            formatted = self._format_markdown(
                response, verbosity, include_metadata, include_recommendations
            )
        else:
            formatted = self._format_text(
                response, verbosity, include_metadata, include_recommendations
            )
        
        # Apply word limit for concise/detailed
        word_limit = self.word_limits.get(verbosity)
        if word_limit:
            formatted = self._truncate_to_limit(formatted, word_limit)
        
        return formatted
    
    def _format_text_concise(self, response: AgentResponse) -> str:
        """Format concise text (50-150 words)."""
        lines = []
        
        # Status (always)
        symbol = "✓" if response.success else "✗"
        status = "SUCCESS" if response.success else "FAILURE"
        lines.append(f"{symbol} **{status}**")
        
        # Message (truncated if long)
        if response.message:
            msg = response.message
            if len(msg.split()) > 50:
                msg = " ".join(msg.split()[:50]) + "..."
            lines.append(f"\n{msg}")
        
        # Key result (summary only)
        if response.result:
            if isinstance(response.result, dict):
                key_info = self._extract_key_info(response.result)
                if key_info:
                    lines.append(f"\n**Key Info:** {key_info}")
            else:
                lines.append(f"\n**Result:** {str(response.result)[:100]}")
        
        # Top recommendation only
        if response.next_actions and len(response.next_actions) > 0:
            lines.append(f"\n**Next:** {response.next_actions[0]}")
        
        # Expansion hint
        lines.append(f"\n_Say 'show details' for more info_")
        
        return "\n".join(lines)
    
    def _extract_key_info(self, result: Dict) -> str:
        """Extract most important info from result dict."""
        # Prioritize: status, count, files, errors
        for key in ["status", "count", "files_changed", "errors", "summary"]:
            if key in result:
                val = result[key]
                if isinstance(val, list):
                    return f"{len(val)} {key}"
                return f"{key}: {val}"
        
        # Fallback: first item
        if result:
            key, val = next(iter(result.items()))
            if isinstance(val, list):
                return f"{len(val)} {key}"
            return f"{key}: {val}"
        
        return ""
    
    def _truncate_to_limit(self, text: str, word_limit: int) -> str:
        """Truncate text to word limit preserving structure."""
        words = text.split()
        if len(words) <= word_limit:
            return text
        
        # Truncate and add expansion hint
        truncated = " ".join(words[:word_limit])
        return f"{truncated}...\n\n_Response truncated. Say 'show more' for full details_"
```

---

### 3. Add Intent Detection for Verbosity

**File:** `src/cortex_agents/right_brain/intent_detector.py`

**Add verbosity intent patterns:**

```python
# In IntentDetector class

VERBOSITY_PATTERNS = {
    "set_concise": [
        r"\b(be |make it |keep it )?(concise|brief|short|quick)\b",
        r"\btl;?dr\b",
        r"\bsummarize\b",
        r"\bless detail",
    ],
    "set_detailed": [
        r"\b(show|give me|need) (more |some )?(details?|context|info)\b",
        r"\bexplain (more|further)\b",
        r"\bmedium detail",
    ],
    "set_expert": [
        r"\b(explain|show) (fully|completely|in depth|everything)\b",
        r"\bfull (detail|analysis|breakdown)\b",
        r"\btechnical details?\b",
        r"\bexpert mode\b",
    ],
    "expand_last": [
        r"^\s*more\s*$",
        r"^\s*expand\s*$",
        r"^\s*show more\s*$",
    ],
    "compress_last": [
        r"^\s*less\s*$",
        r"^\s*summarize\s*$",
        r"^\s*tldr\s*$",
    ],
}

def detect_verbosity_request(self, request: str) -> Optional[str]:
    """
    Detect verbosity change request.
    
    Returns:
        "set_concise" | "set_detailed" | "set_expert" | 
        "expand_last" | "compress_last" | None
    """
    request_lower = request.lower()
    
    for intent, patterns in self.VERBOSITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, request_lower):
                return intent
    
    return None
```

---

### 4. Store User Preference in Tier 1

**File:** `src/tier1/conversation_manager.py`

**Add preference tracking:**

```python
def set_user_preference(
    self,
    conversation_id: str,
    preference_key: str,
    preference_value: Any
) -> bool:
    """
    Store user preference for conversation.
    
    Args:
        conversation_id: Conversation identifier
        preference_key: Preference name (e.g., "verbosity_level")
        preference_value: Preference value
    
    Returns:
        True if stored successfully
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store in JSON metadata
        cursor.execute("""
            UPDATE conversations
            SET metadata = json_set(
                COALESCE(metadata, '{}'),
                '$.preferences.' || ?,
                json(?)
            )
            WHERE conversation_id = ?
        """, (preference_key, json.dumps(preference_value), conversation_id))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.error(f"Failed to store preference: {e}")
        return False

def get_user_preference(
    self,
    conversation_id: str,
    preference_key: str,
    default: Any = None
) -> Any:
    """
    Retrieve user preference for conversation.
    
    Returns:
        Preference value or default if not set
    """
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT json_extract(metadata, '$.preferences.' || ?)
            FROM conversations
            WHERE conversation_id = ?
        """, (preference_key, conversation_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return json.loads(result[0])
        
        return default
    
    except Exception as e:
        logger.error(f"Failed to retrieve preference: {e}")
        return default
```

---

## 🧪 Testing Strategy

### Test Cases to Add

**File:** `tests/entry_point/test_response_formatter_verbosity.py` (new)

```python
"""Test response formatter verbosity levels."""

import pytest
from src.entry_point.response_formatter import ResponseFormatter
from src.cortex_agents.base_agent import AgentResponse


class TestVerbosityLevels:
    """Test different verbosity levels."""
    
    def test_concise_under_word_limit(self):
        """Test concise format stays under 150 words."""
        formatter = ResponseFormatter(default_verbosity="concise")
        response = AgentResponse(
            success=True,
            result={"files": ["a.py", "b.py"] * 50},  # Lots of data
            message="Very long message " * 100,  # Long message
        )
        
        output = formatter.format(response)
        word_count = len(output.split())
        
        assert word_count <= 150, f"Expected ≤150 words, got {word_count}"
        assert "show details" in output.lower()  # Expansion hint
    
    def test_detailed_shows_more(self):
        """Test detailed format includes metadata."""
        formatter = ResponseFormatter(default_verbosity="detailed")
        response = AgentResponse(
            success=True,
            result={"status": "complete"},
            metadata={"task": "test"}
        )
        
        output = formatter.format(response)
        assert "Metadata:" in output or "task:" in output
    
    def test_expert_no_limit(self):
        """Test expert format has no word limit."""
        formatter = ResponseFormatter(default_verbosity="expert")
        response = AgentResponse(
            success=True,
            message="Word " * 1000,  # Very long
        )
        
        output = formatter.format(response)
        word_count = len(output.split())
        
        assert word_count > 150, "Expert mode should not truncate"


class TestVerbosityOverride:
    """Test verbosity can be overridden per call."""
    
    def test_override_default(self):
        """Test per-call verbosity override."""
        formatter = ResponseFormatter(default_verbosity="concise")
        response = AgentResponse(success=True, message="Test")
        
        concise = formatter.format(response, verbosity="concise")
        expert = formatter.format(response, verbosity="expert")
        
        assert len(expert.split()) >= len(concise.split())
```

---

## 📊 Expected Improvements

### Before (Current State)
- ❌ Average response: 800-1,200 words
- ❌ Takes 1-2 minutes to parse
- ❌ Critical info buried in details
- ❌ Can't quickly scan for action items

### After (With Recommendations)
- ✅ Default response: 50-150 words (Tier 1)
- ✅ Takes 10-15 seconds to parse
- ✅ Critical info upfront
- ✅ Can expand if needed
- ✅ User controls detail level

### User Experience Improvement
- **Reading time:** 1-2 min → 10-15 sec (85% reduction)
- **Time to action:** Immediate vs delayed
- **Cognitive load:** LOW (scan) vs HIGH (parse)
- **Flexibility:** User-controlled progressive disclosure

---

## 🎯 Next Steps

### Immediate (Do First)
1. ✅ **Review this document** with stakeholder
2. **Decide on approach** (recommend: Hybrid Phase 1-3)
3. **Create feature branch:** `feature/concise-responses`
4. **Implement Phase 1** (1-2 hours)
5. **Test with real queries**

### Short Term (This Week)
6. **Implement Phase 2** (2-3 hours)
7. **Add comprehensive tests**
8. **Update documentation**
9. **Deploy to production**

### Medium Term (Optional Enhancement)
10. **Add collapsible sections** for Markdown responses
11. **Track user verbosity preferences** analytics
12. **A/B test** default verbosity levels
13. **Add visual indicators** (🎯 concise, 📊 detailed, 🔍 expert)

---

## 📖 Related Documentation

**Design docs:**
- `cortex-brain/cortex-2.0-design/29-response-template-system.md` - Original design (needs update)

**Implementation files:**
- `src/entry_point/response_formatter.py` - Core formatting logic
- `src/cortex_agents/right_brain/intent_detector.py` - Intent detection
- `tests/entry_point/test_response_formatter.py` - Existing tests

**Configuration:**
- `cortex.config.json` - Add response_settings section

---

## ✅ Decision Required

**Question for user:** Which approach do you prefer?

1. **Quick Win** (1-2 hours): Natural language commands only
2. **Smart Defaults** (3-4 hours): Intent-based verbosity
3. **Full System** (4-7 hours): All three phases (recommended)
4. **Custom**: Tell me what you want

**Next action:** Await your decision, then implement chosen approach.

---

*This document provides actionable recommendations to address CORTEX verbosity issues while maintaining flexibility for users who need detailed responses.*
