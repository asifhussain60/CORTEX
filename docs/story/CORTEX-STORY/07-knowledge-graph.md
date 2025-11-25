# Chapter 7: The Knowledge Graph

## The Day CORTEX Learned to Learn (Or: How YAML Became Sentient)

7 AM. Coffee cup #11. I was watching CORTEX work.

**Me:** "Use native array methods instead of lodash"  
**Executor:** *"Got it!"* ✅

**Next day:**  
**Me:** "Process this array"  
**Executor:** *[Suggests lodash again]*  
**Me:** 🤬

**The problem:** Tier 1 memory only holds 20 conversations. Yesterday's correction? GONE.

**I needed PERMANENT LEARNING.**

---

## The Napkin Strike Back (Napkin #3)

I grabbed another napkin (the barista was judging me at this point):

```
TIER 1 (Working Memory)
    ↓
[Learning Process]
    ↓
TIER 2 (Knowledge Graph)
    ↓
[Pattern Recognition]
    ↓
AGENT BEHAVIOR CHANGES
```

**The goal:** When I correct CORTEX 3 times, it should NEVER make that mistake again.

---

## The Knowledge Graph Structure (Or: How I Organized Wisdom)

I created `cortex-brain/knowledge-graph.yaml`:

```yaml
# TIER 2: KNOWLEDGE GRAPH
# Learned patterns, preferences, and wisdom

patterns:
  # Code Style Patterns
  pattern_native_array_methods:
    category: code_style
    rule: "Use native .map(), .filter(), .reduce() instead of lodash"
    confidence: 0.94
    learned_from:
      - conversation_abc123
      - conversation_def456
      - conversation_ghi789
    created: "2024-10-15"
    last_reinforced: "2024-11-10"
    times_applied: 47
    times_corrected: 0
    effectiveness: high
    
  pattern_jwt_authentication:
    category: architecture
    rule: "Use JWT with httpOnly cookies, not localStorage"
    confidence: 0.92
    learned_from:
      - conversation_xyz123
      - conversation_xyz456
    created: "2024-09-20"
    last_reinforced: "2024-11-09"
    times_applied: 12
    times_corrected: 1
    effectiveness: high
    notes: "One correction was due to CSRF edge case"

  # User Preferences
  preference_semicolons:
    category: user_preference
    rule: "Never use semicolons in JavaScript"
    confidence: 0.99
    learned_from:
      - conversation_pref001
      - conversation_pref002
      - conversation_pref003
      - conversation_pref004
    created: "2024-08-01"
    last_reinforced: "2024-11-10"
    times_applied: 234
    times_corrected: 0
    effectiveness: high
    notes: "User REALLY hates semicolons"

  # Anti-Patterns (Things to AVOID)
  antipattern_lodash_simple_arrays:
    category: antipattern
    rule: "Don't suggest lodash for simple array operations"
    confidence: 0.87
    learned_from:
      - conversation_anti001
      - conversation_anti002
      - conversation_anti003
    created: "2024-09-15"
    last_reinforced: "2024-11-08"
    times_corrected: 3
    effectiveness: medium
    notes: "User corrected 3 times, pattern learned"

  # Architectural Decisions
  architecture_microservices:
    category: architecture
    rule: "Project uses microservices, not monolith"
    confidence: 0.95
    learned_from:
      - conversation_arch001
    created: "2024-07-01"
    last_reinforced: "2024-11-10"
    times_applied: 89
    times_corrected: 0
    effectiveness: high
    context:
      services:
        - auth-service
        - user-service
        - payment-service
        - notification-service

  # Testing Patterns
  pattern_pytest_fixtures:
    category: testing
    rule: "Use pytest fixtures for test setup, not setUp() methods"
    confidence: 0.88
    learned_from:
      - conversation_test001
      - conversation_test002
    created: "2024-08-20"
    last_reinforced: "2024-11-05"
    times_applied: 34
    times_corrected: 1
    effectiveness: high

# Confidence Thresholds
confidence_levels:
  experimental: 0.0 - 0.5   # New pattern, not proven
  emerging: 0.5 - 0.7       # Seen a few times
  established: 0.7 - 0.9    # Consistently works
  proven: 0.9 - 1.0         # Never fails

# Learning Rules
learning_rules:
  promotion_threshold: 3     # Pattern needs 3 occurrences to be promoted from Tier 1
  deprecation_threshold: 5   # Pattern fails 5 times = remove from graph
  confidence_increase: 0.05  # Increase per successful application
  confidence_decrease: 0.10  # Decrease per failure/correction
```

---

## The Learning Pipeline (How Patterns are Born)

### Step 1: Observation (Learner Agent Watches)

Every interaction is monitored:

```python
# Learner Agent observes:
user_message = "Use native .map() instead of lodash"
assistant_action = "Suggested lodash.map()"
correction = True

learner.record_interaction({
    'type': 'correction',
    'category': 'code_style',
    'from': 'lodash.map()',
    'to': 'native .map()',
    'timestamp': '2024-11-10T07:15:00Z'
})
```

### Step 2: Pattern Detection (Are We Seeing a Trend?)

Learner checks Tier 1 (last 20 conversations):

```python
similar_corrections = [
    {'date': '2024-11-08', 'type': 'lodash -> native'},
    {'date': '2024-11-09', 'type': 'lodash -> native'},
    {'date': '2024-11-10', 'type': 'lodash -> native'}
]

if len(similar_corrections) >= 3:
    # Pattern detected! Promote to Tier 2
    learner.promote_to_knowledge_graph()
```

### Step 3: Knowledge Graph Update (Pattern Promotion)

```yaml
# knowledge-graph.yaml gets new entry:
pattern_native_array_methods:
  category: code_style
  rule: "Use native .map(), .filter(), .reduce() instead of lodash"
  confidence: 0.65  # Start with moderate confidence
  learned_from:
    - conversation_abc123
    - conversation_def456
    - conversation_ghi789
  created: "2024-11-10"
  last_reinforced: "2024-11-10"
  times_applied: 0  # Not applied yet
  times_corrected: 0
  effectiveness: unknown
```

### Step 4: Pattern Application (Agents Use Knowledge)

Next time Executor writes array code:

```python
# Executor checks Tier 2 knowledge graph
pattern = knowledge_graph.get_pattern('array_operations')

if pattern and pattern.confidence > 0.5:
    # Use native methods (pattern confidence: 0.65)
    code = "items.map(item => item.id)"
else:
    # Low confidence, use default approach
    code = "_.map(items, item => item.id)"
```

### Step 5: Feedback Loop (Did It Work?)

If user doesn't correct:
```python
# Success! Increase confidence
pattern.confidence += 0.05  # Now 0.70
pattern.times_applied += 1
pattern.effectiveness = 'high'
```

If user corrects:
```python
# Oops! Decrease confidence
pattern.confidence -= 0.10  # Now 0.55
pattern.times_corrected += 1
pattern.effectiveness = 'medium'
```

---

## The Bayesian Learning Model (Math! In a Story!)

I used Bayesian updating for confidence scores:

**Initial confidence:** 0.65 (moderate)

**After 5 successful applications:**
```
0.65 + (0.05 × 5) = 0.90 (proven pattern!)
```

**After 1 correction:**
```
0.90 - (0.10 × 1) = 0.80 (still strong)
```

**After 5 corrections:**
```
0.80 - (0.10 × 5) = 0.30 (pattern deprecated)
```

**If confidence < 0.5:** Pattern is removed from knowledge graph.

**Why Bayesian?**
- Self-correcting (bad patterns fade away)
- Confidence grows with success
- Resilient to occasional failures
- Matches human learning (we forget bad habits over time)

---

## The Cross-Machine Sync Problem (Plot Twist!)

**Scenario:** You work on 3 machines.

**Desktop:** Learns "use JWT"  
**MacBook:** Learns "use native array methods"  
**Work Laptop:** Learns "prefer TypeScript strict mode"

**Problem:** Each machine has DIFFERENT knowledge graphs!

**Solution:** Git + Merge Algorithm

```bash
# knowledge-graph.yaml is tracked in Git
git add cortex-brain/knowledge-graph.yaml
git commit -m "CORTEX learned: use native array methods"
git push

# On another machine
git pull

# CORTEX merges knowledge graphs intelligently
```

**Merge Algorithm:**
```python
def merge_knowledge_graphs(local, remote):
    """Merge two knowledge graphs intelligently."""
    merged = {}
    
    for pattern_id in set(local.keys()) | set(remote.keys()):
        local_pattern = local.get(pattern_id)
        remote_pattern = remote.get(pattern_id)
        
        if local_pattern and remote_pattern:
            # Both have this pattern - merge with higher confidence
            if local_pattern.confidence > remote_pattern.confidence:
                merged[pattern_id] = local_pattern
            else:
                merged[pattern_id] = remote_pattern
                
            # Combine learned_from sources
            merged[pattern_id].learned_from = list(set(
                local_pattern.learned_from + 
                remote_pattern.learned_from
            ))
            
        elif local_pattern:
            merged[pattern_id] = local_pattern
        else:
            merged[pattern_id] = remote_pattern
    
    return merged
```

**Result:** All machines share accumulated wisdom! 🎉

---

## The Real-World Impact: Before & After

### Before Knowledge Graph (Tier 1 Only):

**Conversation 1:**  
**Me:** "Use JWT"  
**CORTEX:** *"Got it!"*

**Conversation 25 (Tier 1 limit = 20):**  
**Me:** "Add authentication"  
**CORTEX:** *"Should we use sessions or JWT?"*  
**Me:** *"WE DISCUSSED THIS!"*

### After Knowledge Graph (Tier 2):

**Conversation 1:**  
**Me:** "Use JWT"  
**CORTEX:** *"Got it!"*  
**Learner:** *[Records pattern]*

**Conversation 3:**  
**Me:** "Use JWT" (again)  
**Learner:** *[Pattern detected! Promoting to Tier 2 with 0.65 confidence]*

**Conversation 25:**  
**Me:** "Add authentication"  
**CORTEX:** *[Checks Tier 2: JWT pattern confidence = 0.92]*  
**CORTEX:** *"Implementing JWT authentication with httpOnly cookies..."*  
**Me:** 😭 (happy tears)

---

## The Pattern Categories (Organized Wisdom)

I organized patterns into 7 categories:

### 1. **Code Style**
- Indentation preferences
- Naming conventions
- Language-specific idioms

### 2. **Architecture**
- System design decisions
- Microservices vs monolith
- Database choices

### 3. **User Preferences**
- Editor preferences (tabs vs spaces)
- Language preferences (TypeScript vs JavaScript)
- Framework choices (React vs Vue)

### 4. **Testing Patterns**
- Test framework (pytest, jest)
- Test structure (fixtures, mocks)
- Coverage requirements

### 5. **Anti-Patterns**
- Things that FAILED
- Approaches to AVOID
- Common mistakes

### 6. **Security**
- Authentication patterns
- Authorization rules
- Encryption requirements

### 7. **Performance**
- Optimization techniques
- Caching strategies
- Database indexing

---

## The "AHA!" Moment: It Learns My Style

After 2 months of using CORTEX with knowledge graph:

**Me:** "Add a button"  
**CORTEX:**
- Uses my preferred purple (#7B2CBF) ✅
- Applies 8px border-radius (my preference) ✅
- Implements with React hooks (not classes) ✅
- Writes tests with jest (not mocha) ✅
- Uses TypeScript strict mode ✅

**I didn't specify ANY of that.** CORTEX learned it from 2 months of interactions.

**It learned my coding style like a human would.**

---

## The Statistics (Token Optimization Part 2)

**Tier 1 only (20 conversations):** 2,000 tokens average  
**Tier 2 knowledge graph (500 patterns):** 1,200 tokens when loaded  

**But:** Knowledge graph is SELECTIVE. Only loads relevant patterns.

**Example:**
- User asks about "authentication"
- Load patterns matching category: architecture, security
- **Tokens used:** 300 (not 1,200)

**Token reduction:** 75% by selective loading

---

## What's Next?

We have memory (Tier 1) and learning (Tier 2). But how do we protect all this?

What if CORTEX learns a BAD pattern? What if it breaks its own brain? What if it suggests something dangerous?

That's where **SKULL Protection Layer** (Tier 0) comes in.

---

*Current CORTEX Status: 14 operations, 97 modules, 37 live (38% conscious). Knowledge graph: 500+ patterns accumulated. Learning rate: Bayesian. Next: Self-protection...*

**[← Back to Chapter 6](06-corpus-callosum.md) | [Continue to Chapter 8: The Protection Layer →](08-protection-layer.md)**
