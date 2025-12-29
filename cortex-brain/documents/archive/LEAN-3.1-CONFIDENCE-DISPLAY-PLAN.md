# CORTEX Lean 3.1: Confidence Display Enhancement Implementation Plan

**Date:** 2025-11-19  
**Feature:** Confidence Display Enhancement (Feature 2 of Lean 3.1)  
**Priority:** HIGH  
**Estimated Effort:** 2-3 days  
**Status:** In Progress

---

## Executive Summary

Implement confidence percentage display (0-100%) when CORTEX uses learned patterns from Tier 2 Knowledge Graph. Users will see pattern reliability scores in responses, helping them understand when CORTEX is applying learned knowledge vs. generating new responses.

**Key Benefits:**
- ✅ Transparency - Users know when CORTEX uses learned patterns
- ✅ Trust Building - Confidence scores indicate reliability
- ✅ Learning Feedback - Users see knowledge graph effectiveness
- ✅ Pattern Validation - Low confidence triggers review

---

## Current State Analysis

### Existing Confidence Infrastructure

**1. Pattern Learning Engine** (`src/tier1/pattern_learning_engine.py`)
- ✅ Already calculates confidence scores (0.0-1.0)
- ✅ Boosts confidence based on pattern usage
- ✅ Tracks pattern success rates
- ✅ Applies temporal pattern confidence

**2. Knowledge Graph** (`src/tier2/knowledge_graph.py`)
- ✅ Stores pattern confidence in database
- ✅ Indexes by confidence for fast queries
- ✅ Supports confidence decay over time
- ✅ Deletes patterns below 0.3 threshold

**3. Existing Scoring Factors:**
```python
# From pattern_learning_engine.py:
- base_confidence: Initial pattern match quality
- pattern_boost: Boost from file mention patterns
- window_confidence: Temporal pattern confidence
- usage_count: Pattern usage history
- success_rate: Pattern success history
```

**Gap:** Confidence is calculated internally but **never displayed to users**.

---

## Implementation Design

### Phase 1: Confidence Scoring Module (4-6 hours)

**File:** `src/cognitive/confidence_scorer.py`

**Purpose:** Centralized confidence calculation and formatting

```python
"""
CORTEX Confidence Scoring Module

Calculates and formats confidence scores for pattern usage display.
Converts internal confidence (0.0-1.0) to user-friendly percentages.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class ConfidenceLevel(Enum):
    """Confidence level categories for user display"""
    VERY_HIGH = "Very High"  # 90-100%
    HIGH = "High"            # 75-89%
    MEDIUM = "Medium"        # 50-74%
    LOW = "Low"              # 30-49%
    VERY_LOW = "Very Low"    # <30%


@dataclass
class ConfidenceScore:
    """Confidence score with metadata for display"""
    percentage: int  # 0-100
    level: ConfidenceLevel
    pattern_count: int  # Number of patterns used
    usage_history: int  # Total usage count
    last_used: Optional[datetime]
    factors: Dict[str, float]  # Contributing factors
    
    def format_display(self) -> str:
        """Format confidence for user display"""
        emoji = self._get_emoji()
        return f"{emoji} Confidence: {self.percentage}% ({self.level.value})"
    
    def format_detailed(self) -> str:
        """Format detailed confidence explanation"""
        display = self.format_display()
        details = f"Based on {self.pattern_count} similar patterns"
        if self.usage_history > 0:
            details += f" ({self.usage_history} successful uses)"
        return f"{display} - {details}"
    
    def _get_emoji(self) -> str:
        """Get emoji for confidence level"""
        emoji_map = {
            ConfidenceLevel.VERY_HIGH: "🟢",
            ConfidenceLevel.HIGH: "🟢", 
            ConfidenceLevel.MEDIUM: "🟡",
            ConfidenceLevel.LOW: "🟠",
            ConfidenceLevel.VERY_LOW: "🔴"
        }
        return emoji_map.get(self.level, "⚪")


class ConfidenceScorer:
    """
    Calculate confidence scores from pattern data
    
    Factors considered:
    - Pattern match quality (40%)
    - Usage history (30%)
    - Success rate (20%)
    - Recency (10%)
    """
    
    # Weights for confidence calculation
    WEIGHT_MATCH_QUALITY = 0.40
    WEIGHT_USAGE_HISTORY = 0.30
    WEIGHT_SUCCESS_RATE = 0.20
    WEIGHT_RECENCY = 0.10
    
    def calculate_confidence(
        self,
        base_confidence: float,
        usage_count: int = 0,
        success_rate: float = 0.0,
        last_used: Optional[datetime] = None,
        pattern_count: int = 1
    ) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score
        
        Args:
            base_confidence: Pattern match quality (0.0-1.0)
            usage_count: Number of times pattern used successfully
            success_rate: Success rate of pattern (0.0-1.0)
            last_used: When pattern was last used
            pattern_count: Number of patterns contributing
            
        Returns:
            ConfidenceScore with percentage and metadata
        """
        factors = {}
        
        # Factor 1: Match Quality (40%)
        match_score = base_confidence
        factors['match_quality'] = match_score
        
        # Factor 2: Usage History (30%)
        # More usage = higher confidence (logarithmic scale)
        import math
        usage_score = min(1.0, math.log10(usage_count + 1) / 2.0) if usage_count > 0 else 0.0
        factors['usage_history'] = usage_score
        
        # Factor 3: Success Rate (20%)
        factors['success_rate'] = success_rate
        
        # Factor 4: Recency (10%)
        recency_score = self._calculate_recency_score(last_used)
        factors['recency'] = recency_score
        
        # Weighted sum
        weighted_confidence = (
            match_score * self.WEIGHT_MATCH_QUALITY +
            usage_score * self.WEIGHT_USAGE_HISTORY +
            success_rate * self.WEIGHT_SUCCESS_RATE +
            recency_score * self.WEIGHT_RECENCY
        )
        
        # Convert to percentage (0-100)
        percentage = int(weighted_confidence * 100)
        
        # Determine confidence level
        level = self._determine_level(percentage)
        
        return ConfidenceScore(
            percentage=percentage,
            level=level,
            pattern_count=pattern_count,
            usage_history=usage_count,
            last_used=last_used,
            factors=factors
        )
    
    def _calculate_recency_score(self, last_used: Optional[datetime]) -> float:
        """Calculate recency score (1.0 = recent, 0.0 = old)"""
        if not last_used:
            return 0.5  # Neutral score if no data
        
        age_days = (datetime.now() - last_used).days
        
        if age_days <= 7:
            return 1.0  # Very recent
        elif age_days <= 30:
            return 0.8  # Recent
        elif age_days <= 90:
            return 0.6  # Moderately old
        elif age_days <= 180:
            return 0.4  # Old
        else:
            return 0.2  # Very old
    
    def _determine_level(self, percentage: int) -> ConfidenceLevel:
        """Determine confidence level from percentage"""
        if percentage >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif percentage >= 75:
            return ConfidenceLevel.HIGH
        elif percentage >= 50:
            return ConfidenceLevel.MEDIUM
        elif percentage >= 30:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
```

**Test Coverage:** `tests/cognitive/test_confidence_scorer.py`
- Test all confidence levels (0-100%)
- Test edge cases (no usage history, very old patterns)
- Test factor weighting accuracy
- Test display formatting

---

### Phase 2: Response Template Integration (2-3 hours)

**File:** `cortex-brain/response-templates.yaml`

**New Template Section:**

```yaml
# Confidence Display Template (When patterns are used)
confidence_display:
  name: "confidence_display"
  trigger: []  # Auto-injected by system, not user-triggered
  response_type: "structured"
  content: |
    🧠 **CORTEX {{operation_type}}**
    Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
    
    {{confidence_indicator}}
    
    🎯 **My Understanding Of Your Request:**
       {{understanding}}
    
    ⚠️ **Challenge:** {{challenge_type}}
       {{challenge_explanation}}
    
    💬 **Response:**
    
    {{response_content}}
    
    📝 **Your Request:** {{request_echo}}
    
    🔍 **Next Steps:**
       {{next_steps}}
  
  placeholders:
    - operation_type
    - confidence_indicator  # NEW: Shows pattern confidence
    - understanding
    - challenge_type
    - challenge_explanation
    - response_content
    - request_echo
    - next_steps
```

**Confidence Indicator Template:**

```yaml
confidence_indicator_template:
  # High confidence (75-100%)
  high_confidence: |
    🎯 **Pattern Match Confidence:** {{confidence_display}}
    
    I'm applying learned patterns from {{pattern_count}} similar conversations.
    {{detailed_explanation}}
  
  # Medium confidence (50-74%)
  medium_confidence: |
    🟡 **Pattern Match Confidence:** {{confidence_display}}
    
    I found {{pattern_count}} related patterns, but applying them with moderate confidence.
    {{detailed_explanation}}
  
  # Low confidence (<50%)
  low_confidence: |
    🟠 **Pattern Match Confidence:** {{confidence_display}}
    
    Limited pattern history available. Response based on {{pattern_count}} patterns.
    {{detailed_explanation}}
  
  # No patterns (new territory)
  no_patterns: |
    ℹ️ **New Territory:** No learned patterns available for this request.
    
    Generating fresh response using CORTEX capabilities.
```

**Usage Example in Response:**

```markdown
🧠 **CORTEX Feature Implementation**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🟢 **Pattern Match Confidence: 87% (High)** - Based on 12 similar patterns (34 successful uses)

🎯 **My Understanding Of Your Request:**
   You want to add authentication to the dashboard
   
[rest of response...]
```

---

### Phase 3: Integration with Tier 2 Knowledge Graph (3-4 hours)

**File:** `src/tier2/knowledge_graph.py` (Enhancement)

**Add Confidence Metadata to Search Results:**

```python
def search_patterns(
    self,
    query: str,
    min_confidence: float = 0.5,
    limit: int = 10,
    include_confidence_metadata: bool = False  # NEW parameter
) -> List[Dict]:
    """
    Search patterns with optional confidence metadata
    
    Returns:
        If include_confidence_metadata=True:
        [
            {
                "pattern_id": "...",
                "title": "...",
                "confidence": 0.85,
                "usage_count": 12,
                "success_rate": 0.92,
                "last_used": datetime(...),
                "pattern_count": 5  # How many patterns matched
            },
            ...
        ]
    """
    # Existing search logic...
    
    if include_confidence_metadata:
        # Enhance results with metadata for confidence display
        for result in results:
            result['pattern_count'] = len(results)
            result['success_rate'] = self._calculate_success_rate(result['pattern_id'])
    
    return results
```

---

### Phase 4: Response Generation Integration (2-3 hours)

**File:** `src/agents/intent_router.py` or response generator

**Inject Confidence Display:**

```python
from src.cognitive.confidence_scorer import ConfidenceScorer, ConfidenceScore

class ResponseGenerator:
    """Generate responses with confidence display"""
    
    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()
    
    def generate_response_with_confidence(
        self,
        user_request: str,
        operation_type: str,
        pattern_results: List[Dict]
    ) -> str:
        """
        Generate response with confidence indicator
        
        Args:
            user_request: User's request text
            operation_type: Type of operation (planning, execution, etc.)
            pattern_results: Matching patterns from knowledge graph
        
        Returns:
            Formatted response with confidence display
        """
        if not pattern_results:
            # No patterns - use "no_patterns" template
            return self._generate_without_patterns(user_request, operation_type)
        
        # Calculate confidence from best pattern match
        best_pattern = pattern_results[0]
        
        confidence = self.confidence_scorer.calculate_confidence(
            base_confidence=best_pattern.get('confidence', 0.5),
            usage_count=best_pattern.get('usage_count', 0),
            success_rate=best_pattern.get('success_rate', 0.0),
            last_used=best_pattern.get('last_used'),
            pattern_count=len(pattern_results)
        )
        
        # Select template based on confidence level
        confidence_indicator = self._format_confidence_indicator(confidence)
        
        # Generate response with confidence display
        return self._render_template(
            operation_type=operation_type,
            confidence_indicator=confidence_indicator,
            user_request=user_request,
            pattern_data=best_pattern
        )
```

---

## Implementation Timeline

### Day 1 (4-6 hours)
- ☐ Create `src/cognitive/confidence_scorer.py`
- ☐ Implement `ConfidenceScore` dataclass
- ☐ Implement `ConfidenceScorer` class
- ☐ Write unit tests (`tests/cognitive/test_confidence_scorer.py`)
- ☐ Validate all confidence levels work correctly

### Day 2 (5-7 hours)
- ☐ Add confidence templates to `response-templates.yaml`
- ☐ Enhance `knowledge_graph.py` search with metadata
- ☐ Create response generator integration
- ☐ Test confidence display in responses
- ☐ Validate template rendering

### Day 3 (3-4 hours)
- ☐ Integration testing with Tier 2 Knowledge Graph
- ☐ Test edge cases (no patterns, low confidence, high confidence)
- ☐ Update CORTEX.prompt.md documentation
- ☐ Create user-facing examples
- ☐ Validation checkpoint

---

## Success Criteria

### Functional Requirements
- ✅ Confidence percentage displays when patterns are used
- ✅ Confidence level (High/Medium/Low) shows correctly
- ✅ Pattern count and usage history visible
- ✅ Different templates for different confidence levels
- ✅ No display when no patterns available

### User Experience
- ✅ Confidence display is concise (1-2 lines)
- ✅ Emoji indicators clear and intuitive
- ✅ Explanation helps users understand reliability
- ✅ Doesn't clutter response unnecessarily

### Technical Requirements
- ✅ Confidence calculation uses 4 factors (match, usage, success, recency)
- ✅ Integration with existing Tier 2 Knowledge Graph
- ✅ Unit test coverage ≥ 90%
- ✅ Performance overhead < 50ms per response

---

## Testing Strategy

### Unit Tests
```python
# tests/cognitive/test_confidence_scorer.py

def test_confidence_very_high():
    """Should show 90-100% for highly reliable patterns"""
    scorer = ConfidenceScorer()
    score = scorer.calculate_confidence(
        base_confidence=0.95,
        usage_count=50,
        success_rate=0.98,
        last_used=datetime.now()
    )
    assert score.percentage >= 90
    assert score.level == ConfidenceLevel.VERY_HIGH

def test_confidence_with_no_usage():
    """Should show lower confidence for unused patterns"""
    scorer = ConfidenceScorer()
    score = scorer.calculate_confidence(
        base_confidence=0.80,
        usage_count=0,
        success_rate=0.0,
        last_used=None
    )
    assert score.percentage < 75  # Can't be HIGH without usage

def test_confidence_display_formatting():
    """Should format confidence display correctly"""
    score = ConfidenceScore(
        percentage=87,
        level=ConfidenceLevel.HIGH,
        pattern_count=12,
        usage_history=34,
        last_used=datetime.now(),
        factors={}
    )
    display = score.format_detailed()
    assert "87%" in display
    assert "High" in display
    assert "12 similar patterns" in display
    assert "34 successful uses" in display
```

### Integration Tests
```python
# tests/integration/test_confidence_display.py

def test_confidence_display_in_response():
    """Should inject confidence display into response"""
    # Simulate pattern search
    patterns = knowledge_graph.search_patterns(
        query="authentication feature",
        include_confidence_metadata=True
    )
    
    # Generate response
    response = generator.generate_response_with_confidence(
        user_request="add authentication",
        operation_type="Feature Implementation",
        pattern_results=patterns
    )
    
    # Verify confidence display present
    assert "Confidence:" in response
    assert "%" in response
    assert "Based on" in response

def test_no_confidence_display_without_patterns():
    """Should show 'New Territory' when no patterns"""
    response = generator.generate_response_with_confidence(
        user_request="build quantum computer interface",
        operation_type="Feature Implementation",
        pattern_results=[]
    )
    
    assert "New Territory" in response
    assert "No learned patterns" in response
```

---

## Edge Cases

### Case 1: No Patterns Available
**Scenario:** User requests something CORTEX has never seen  
**Expected:** Display "New Territory" message, no confidence percentage  
**Template:** `no_patterns` template variant

### Case 2: Very Low Confidence (<30%)
**Scenario:** Patterns exist but are unreliable (old, low usage)  
**Expected:** Display red indicator (🔴), warn user about low confidence  
**Action:** Consider regenerating response without patterns

### Case 3: Multiple Patterns with Different Confidences
**Scenario:** 10 patterns found with confidences ranging 40-90%  
**Expected:** Use highest confidence pattern, mention pattern count  
**Display:** "Based on 10 patterns (best match: 90%)"

### Case 4: Pattern Confidence Decay
**Scenario:** Pattern hasn't been used in 6 months  
**Expected:** Recency factor lowers confidence, display reflects age  
**Display:** "Based on older patterns (last used 6 months ago)"

---

## Documentation Updates

### CORTEX.prompt.md Additions

```markdown
## 🎯 Confidence Display (NEW in Lean 3.1)

**What It Is:**
CORTEX now shows confidence percentages when using learned patterns from the Knowledge Graph. This helps you understand when CORTEX is applying proven patterns vs. generating new responses.

**How It Appears:**

```markdown
🟢 **Pattern Match Confidence: 87% (High)** - Based on 12 similar patterns (34 successful uses)
```

**Confidence Levels:**
- 🟢 **90-100% (Very High):** Well-established pattern, many successful uses
- 🟢 **75-89% (High):** Reliable pattern with good usage history
- 🟡 **50-74% (Medium):** Pattern exists but moderate confidence
- 🟠 **30-49% (Low):** Limited pattern data, lower reliability
- 🔴 **<30% (Very Low):** Unreliable pattern, consider fresh approach
- ℹ️ **New Territory:** No patterns available, fresh response

**When You See It:**
- Feature planning (using past planning patterns)
- Code implementation (using similar code patterns)
- Architecture decisions (using design patterns)
- Bug fixes (using similar error resolutions)

**When You DON'T See It:**
- Simple questions (no patterns needed)
- First-time requests (no history)
- Administrative commands (direct execution)
```

---

## Risks & Mitigations

### Risk 1: Performance Overhead
**Risk:** Confidence calculation adds latency  
**Mitigation:** Cache confidence scores, calculate asynchronously  
**Target:** < 50ms overhead

### Risk 2: User Confusion
**Risk:** Users don't understand confidence percentages  
**Mitigation:** Clear explanations, emoji indicators, detailed help  
**Validation:** User testing feedback

### Risk 3: Low Confidence Overload
**Risk:** Too many low-confidence warnings  
**Mitigation:** Only show confidence when patterns actually used  
**Threshold:** Don't display for admin/simple commands

---

## Next Steps After Completion

1. **Collect User Feedback:** Monitor how users respond to confidence display
2. **Tune Thresholds:** Adjust confidence level thresholds based on feedback
3. **Enhance Factors:** Add more sophisticated factors (context similarity, semantic match)
4. **Extend to Agents:** Show per-agent confidence (Work Planner confidence vs Code Executor confidence)
5. **Learning Loop:** Use confidence feedback to improve Knowledge Graph

---

## Appendix: Examples

### Example 1: High Confidence Planning

```markdown
🧠 **CORTEX Feature Planning**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🟢 **Pattern Match Confidence: 92% (Very High)** - Based on 18 similar planning sessions (67 successful uses)

I'm applying the interactive planning workflow that has worked well for similar features.

🎯 **My Understanding Of Your Request:**
   You want to plan a user authentication feature for the dashboard

⚠️ **Challenge:** ✓ **Accept**
   This follows our established planning pattern for security-critical features.

💬 **Response:**
I'll guide you through our proven 4-phase planning process, which has successfully
planned 18 similar authentication features. We'll cover requirements, security review,
implementation strategy, and testing approach.

📝 **Your Request:** Plan user authentication feature

🔍 **Next Steps:**
   ☐ Phase 1: Requirements & Security Baseline
   ☐ Phase 2: Architecture Design
   ☐ Phase 3: Implementation Strategy
   ☐ Phase 4: Testing & Validation
   
   Ready to start Phase 1?
```

### Example 2: Medium Confidence Implementation

```markdown
🧠 **CORTEX Code Implementation**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🟡 **Pattern Match Confidence: 68% (Medium)** - Based on 5 related patterns

I found some similar implementations, but adapting with moderate confidence.

🎯 **My Understanding Of Your Request:**
   You want to add email validation to the registration form

⚠️ **Challenge:** ✓ **Accept**
   Standard validation pattern, though your specific framework combination is less common.

💬 **Response:**
I'll implement email validation using patterns from similar forms. The approach
combines client-side validation (immediate feedback) with server-side validation
(security). Let me know if you want to review the pattern before implementing.

📝 **Your Request:** Add email validation to registration

🔍 **Next Steps:**
   1. Review validation pattern (recommended for medium confidence)
   2. Implement client-side validation
   3. Add server-side validation
   4. Write validation tests
```

### Example 3: No Patterns (New Territory)

```markdown
🧠 **CORTEX Feature Implementation**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

ℹ️ **New Territory:** No learned patterns available for this request.

Generating fresh response using CORTEX capabilities.

🎯 **My Understanding Of Your Request:**
   You want to integrate a quantum computing simulator into the dashboard

⚠️ **Challenge:** ⚡ **Challenge**
   This is new territory for CORTEX. No previous quantum integration patterns exist.
   I recommend interactive planning to build a new pattern together.

💬 **Response:**
Since this is uncharted territory, let's take a careful approach. I'll help you
research quantum computing integration options, evaluate frameworks, and design
a proof-of-concept. This will create a new pattern for future quantum features.

📝 **Your Request:** Integrate quantum computing simulator

🔍 **Next Steps:**
   1. Research quantum computing frameworks (Qiskit, Cirq, Q#)
   2. Create integration feasibility analysis
   3. Design proof-of-concept architecture
   4. Plan iterative implementation
```

---

**Status:** Ready for Implementation  
**Approved By:** [Pending]  
**Start Date:** [To be determined]

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
