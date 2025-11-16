# Memory Flow Narrative

## For Leadership

This diagram shows CORTEX's "learning cycle" - how everyday conversations become long-term knowledge.

**Stage 1:** You have a conversation with Copilot  
**Stage 2:** CORTEX captures it (working memory)  
**Stage 3:** Extracts key information (what, why, how)  
**Stage 4:** Stores patterns (learning)  
**Stage 5:** Analyzes project health (intelligence)

**Real-World Analogy:** Like taking notes in a meeting (Stage 2), highlighting key points (Stage 3), filing them in a knowledge base (Stage 4), and updating project dashboards (Stage 5).

## For Developers

**Architecture Pattern:** ETL pipeline with progressive enrichment

**Pipeline Stages:**

1. **Capture (Tier 1)**
   - Raw conversation stored in SQLite
   - FIFO queue (oldest deleted at 21st conversation)
   - <30ms write latency

2. **Extraction (Processing Layer)**
   - Entity detection (files, classes, methods)
   - Intent classification (PLAN, EXECUTE, TEST, etc.)
   - Context enrichment (git branch, active files)

3. **Pattern Storage (Tier 2)**
   - Similar conversations clustered
   - Workflow templates extracted
   - File relationships updated
   - ~100ms processing time

4. **Analytics Update (Tier 3)**
   - File stability recalculated
   - Session productivity tracked
   - Git metrics refreshed
   - ~200ms analysis time

**Data Transformations:**

```
Raw conversation:
  "Add authentication to dashboard"

Entities extracted:
  {
    "action": "add",
    "feature": "authentication",
    "location": "dashboard",
    "files": {"["}"Dashboard.tsx", "AuthService.ts"{"]"}
  }

Intent detected:
  EXECUTE (confidence: 0.92)

Pattern matched:
  "feature_implementation" (similarity: 0.85)

Context updated:
  Dashboard.tsx churn_rate: 0.28 (warning threshold exceeded)
```

## Key Takeaways

1. **Automatic learning** - No manual knowledge capture
2. **Progressive enrichment** - More intelligence at each stage
3. **Fast processing** - <500ms total pipeline
4. **Quality improves over time** - More conversations = better patterns
5. **Privacy-preserving** - All local (no cloud)

## Usage Scenarios

**Scenario 1: First Week Using CORTEX**
- Tier 1: 5 conversations captured
- Tier 2: Basic patterns forming
- Tier 3: Analyzing git history only

**Scenario 2: After 3 Months**
- Tier 1: 20 conversations (FIFO limit)
- Tier 2: 150 patterns learned
- Tier 3: Productivity insights available
- CORTEX suggests proven workflows
- Warns about risky files proactively

*Version: 1.0*  
*Last Updated: November 16, 2025*
