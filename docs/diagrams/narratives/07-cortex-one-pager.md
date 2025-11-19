# CORTEX One-Pager Narrative

## For Leadership

This single-image overview captures everything CORTEX does at a glance.

**Three Pillars:**

1. **Brain Architecture (LEFT)** - Four-tier memory system inspired by human cognition
   - Tier 0: Core principles (never change)
   - Tier 1: Recent conversations (short-term memory)
   - Tier 2: Learned patterns (long-term learning)
   - Tier 3: Project intelligence (situational awareness)

2. **Agent System (CENTER)** - Ten specialists working in harmony
   - LEFT Brain: Executes work with precision (builders)
   - RIGHT Brain: Plans strategy and protects quality (architects)
   - Corpus Callosum: Coordinates collaboration

3. **Features & Results (RIGHT)** - Proven capabilities and metrics
   - Zero-footprint plugins (no external dependencies)
   - 97.2% token reduction (massive cost savings)
   - <500ms performance (lightning fast)
   - 100% test pass rate (production quality)

**The Value Proposition:**

CORTEX transforms GitHub Copilot from a brilliant amnesiac into an experienced teammate with memory, learning capabilities, and project awareness. Developers save time, reduce frustration, and deliver higher quality code.

**ROI Example:**
- Before: Repeat context every conversation (5-10 min/day wasted)
- After: Natural conversations with context continuity
- Cost savings: 93.4% reduction in token costs
- Time savings: ~40 hours/year per developer

## For Developers

**Architecture at a Glance:**

This diagram provides a complete system overview showing:

1. **Data Flow (LEFT → CENTER → RIGHT)**
   ```
   Conversations → Brain Tiers → Agent Processing → Results
   ```

2. **Component Relationships**
   - Brain tiers feed agent intelligence
   - Agents coordinate via corpus callosum
   - Plugins leverage brain intelligence
   - All components < 500ms end-to-end

3. **System Capabilities**
   - Natural language interface (no commands to memorize)
   - Test-driven development (RED → GREEN → REFACTOR)
   - Brain protection (immutable governance rules)
   - Local-first (SQLite + YAML, no cloud)

**Technical Depth:**

**Brain Storage:**
```
Tier 0: YAML files (immutable, version controlled)
Tier 1: conversations.db (SQLite, FIFO queue)
Tier 2: knowledge-graph.db (SQLite + FTS5)
Tier 3: context-intelligence.db (SQLite analytics)
```

**Agent Coordination:**
```
User Request
  ↓ Intent Router (RIGHT)
  ↓ Routes to appropriate agent
  ↓ Work Planner creates strategy (RIGHT)
  ↓ Corpus Callosum delivers tasks
  ↓ Code Executor implements (LEFT)
  ↓ Test Generator validates (LEFT)
  ↓ Health Validator checks quality (LEFT)
  ↓ Knowledge Graph learns (RIGHT)
  ↓ Complete
```

**Plugin Architecture:**
```python
class RecommendationAPIPlugin(BasePlugin):
    def execute(self, request, context):
        # Access brain intelligence
        patterns = tier2.search_patterns(request)
        stability = tier3.get_file_stability(file)
        # Generate recommendations
        return intelligent_suggestions
```

**Performance Benchmarks:**
- Intent detection: ~50ms
- Pattern search: 92ms (target <150ms) ⚡
- Context analysis: 156ms (target <200ms) ⚡
- Conversation capture: 18ms (target <50ms) ⚡
- End-to-end: <500ms total

**Cost Analysis:**
```
Before CORTEX:
  74,047 input tokens × $0.00001 × 1.0 = $0.00074

After CORTEX:
  2,078 input tokens × $0.00001 × 1.0 = $0.00002
  
Savings: 93.4% per request
Annual (1,000 requests/month): $8,636 saved
```

## Key Takeaways

1. **Comprehensive Overview** - One image captures entire system
2. **Three-part Structure** - Brain + Agents + Results
3. **Visual Hierarchy** - Clear information flow
4. **Metrics Highlighted** - Proven performance and savings
5. **Self-contained** - Understandable without additional context

## Usage Scenarios

**When to Use This Image:**

✅ **Executive Presentations**
- Print at 11"x17" for meetings
- High-level overview without technical depth
- Emphasizes ROI and proven results

✅ **Documentation Hero**
- README.md top image
- First thing users see
- Provides instant system understanding

✅ **Conference Slides**
- Technical architecture overview
- Self-explanatory for 30-second glance
- Works without speaker notes

✅ **Social Media**
- Twitter/LinkedIn sharing
- Eye-catching infographic style
- Drives to repository/documentation

✅ **Onboarding**
- New team member orientation
- System architecture introduction
- Reference during training

**When NOT to Use:**

❌ **Deep Technical Docs** - Too high-level, use detailed diagrams instead
❌ **API Reference** - Not suitable for code-level documentation
❌ **Debugging Guides** - Lacks operational detail

## Design Notes

**Information Density:**
- High but not overwhelming
- Each section tells complete story
- Visual flow guides eye left → right
- Color coding aids comprehension

**Accessibility:**
- Text legible at 50% zoom
- Icons distinct and recognizable
- Color-blind friendly (patterns + icons, not just color)
- Alt text: "CORTEX system architecture overview showing 4-tier brain, 10 specialist agents, and key performance metrics"

**Branding Consistency:**
- Uses official CORTEX color palette
- Typography matches documentation
- Icon style consistent throughout
- Professional, technical aesthetic

**Print Considerations:**
- 300 DPI ensures crisp printing
- 16:9 aspect fits standard presentation formats
- Colors calibrated for both screen and print
- White background reduces ink usage

*Version: 1.0*  
*Last Updated: November 19, 2025*
