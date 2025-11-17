# <img src="assets/images/CORTEX-logo.png" alt="CORTEX Logo" style="width: 300px; height: 300px; vertical-align: middle; margin-right: 20px;"> **CORTEX**

<div style="font-size: 1.1rem; color: #666; margin-top: -10px; margin-bottom: 30px;">
<em>Cognitive Operation & Reasoning Through EXtension for Copilot</em>
</div>

<div class="ancient-rules" markdown="1">

## The Sacred Laws of CORTEX

*Herein lie the immutable principles that govern the realm of intelligent automation*

---

### 📜 Layer I: Instinct Immutability

**The Foundation Upon Which All Else Rests**

**TDD_ENFORCEMENT** - *Test-Driven Development Enforcement*  
No code shall be written without first establishing the test by which it shall be judged. The cycle must be followed: RED (failing test), GREEN (implementation), REFACTOR (improvement). Those who bypass this sacred cycle invite chaos into their realm.

**DEFINITION_OF_DONE** - *The Standard of Completion*  
No work shall be deemed complete whilst errors persist or warnings cry out for attention. Zero errors, zero warnings - this is the law. Only when all validation passes may one claim victory.

**DEFINITION_OF_READY** - *Prerequisites for Commencement*  
Before any work begins, requirements must be documented, dependencies identified, technical design approved, and test strategy defined. To proceed without preparation is to court disaster.

**BRAIN_PROTECTION_TESTS_MANDATORY** - *Guardian of Core Integrity*  
The brain protection tests are sacred sentinels that must never fail. They validate path handling, protection logic, conversation tracking, and configuration loading. A 100% pass rate is not a goal but a covenant - any failure blocks all work until resolved.

**MACHINE_READABLE_FORMATS** - *The Principle of Efficiency*  
Use YAML for structured data, JSON for metrics, code files for examples. Reserve Markdown for user-facing narratives only. Machine-readable formats reduce tokens by 60% and prevent documentation drift.

**CORTEX_PROMPT_FILE_PROTECTION** - *Stability of the Entry Point*  
The file CORTEX.prompt.md must never be renamed. It is the single entry point for GitHub Copilot integration. To rename it is to break the covenant. Updates must follow the sacred procedure: create temporary file, clear original, copy content, delete temporary.

---

### 🛡️ Layer II: Tier Boundary Protection

**The Organization of Knowledge**

**TIER0_APPLICATION_DATA** - *Immutability of Governance*  
Tier 0 contains only generic CORTEX principles, never application-specific data. Application data belongs in Tier 2 with proper scope markers. To pollute Tier 0 is to corrupt the foundation.

**TIER2_CONVERSATION_DATA** - *Proper Data Placement*  
Raw conversation data resides in Tier 1 (conversation-history.jsonl). Tier 2 holds only aggregated patterns and knowledge extracted from conversations. Keep raw data in Tier 1, patterns in Tier 2.

---

### 🏛️ Layer III: SOLID Compliance

**The Architecture of Excellence**

**SINGLE_RESPONSIBILITY** - *One Purpose, One Module*  
Beware the God Object that attempts to do all things. Each agent must have a single, well-defined responsibility. When tempted to add "modes" or "switches," create a dedicated agent instead.

**DEPENDENCY_INVERSION** - *Flexibility Through Abstraction*  
Hardcoded paths and fixed dependencies are the enemies of maintainability. Use dependency injection, load from configuration, pass as parameters. Never embed absolutes into the fabric of the code.

**OPEN_CLOSED** - *Extension Over Modification*  
When behavior must change, extend through new implementations rather than modifying existing ones. Use strategy patterns, decorators, and wrappers. Keep the foundation stable while building upward.

**CODE_STYLE_CONSISTENCY** - *Harmony in Expression*  
Generated code must blend seamlessly with the existing codebase. Match indentation, naming conventions, bracket styles, and documentation formats. But never compromise on best practices - SOLID principles and security trump style preferences.

---

### 🧠 Layer IV: Hemisphere Specialization

**The Division of Labor**

**LEFT_BRAIN_TACTICAL** - *Execution Without Planning*  
The left hemisphere executes but does not plan. Code executors, test generators, and error correctors focus on implementation. Strategic planning belongs to the right brain.

**RIGHT_BRAIN_STRATEGIC** - *Planning Without Execution*  
The right hemisphere plans but does not execute. Work planners and intent routers design strategy. They delegate actual execution to left brain agents through the corpus callosum.

---

### 💀 Layer V: SKULL Protection

**Safety, Knowledge, Validation & Learning**

**SKULL-001: Test Before Claim** - *Never claim completion without validation*  
Every fix, every feature, every change must be validated by automated tests before claiming success. "Fixed ✅" without "Verified by: test_name" is forbidden.

**SKULL-002: Integration Verification** - *Test the full chain*  
Integration must be tested end-to-end, not just configuration. Verify the actual execution path from A → B → C. Configuration alone proves nothing.

**SKULL-003: Visual Regression** - *CSS changes require visual validation*  
CSS and UI changes must be validated visually in the browser, with computed styles verified. Cache must be cleared. Before/after screenshots are required.

**SKULL-004: Retry Without Learning** - *Diagnose before repeating*  
When a fix fails, diagnose the root cause before retrying. Never apply the same fix multiple times without understanding why it failed. Change approach based on diagnosis.

**SKULL-005: Transformation Verification** - *Operations claiming transformation must produce changes*  
If an operation claims to transform files, the file hash must differ before and after. Git diff must show modifications. Pass-through operations must not claim transformation success.

**SKULL-006: Privacy Protection** - *No machine-specific data in published packages*  
Published packages must contain no absolute paths (C:\\, D:\\, /home/, /Users/), no machine names (AHHOME), no log files, no coverage artifacts, no health reports. Use template configs with placeholders.

**SKULL-007: Faculty Integrity** - *Published CORTEX must be fully operational*  
Published packages must contain all essential faculties: all four tiers (Tier 0-3), all ten specialist agents, operations framework, plugin system, entry points, and user documentation. Incomplete CORTEX is broken CORTEX.

**SKULL-008: Multi-Track Configuration Validation** - *Parallel development requires proper setup*  
Multi-track mode requires balanced workloads (±30%), isolated dependencies (no cross-track), proper machine assignments (1:1 mapping), and unique track names. Validate before splitting work.

**SKULL-009: Track Work Isolation** - *Stay within assigned boundaries*  
When working on Track A, only modify modules assigned to Track A. Cross-track modifications break parallel development guarantees and create merge conflicts during consolidation.

**SKULL-010: Consolidation Integrity** - *Merge without data loss*  
Track consolidation must preserve all progress from all tracks. Compare module counts before/after, log all conflict resolutions, archive split documents before deletion, and commit with full merge details.

---

### 🎯 Layer VI: Git & Distribution Protection

**Isolation and Integrity**

**GIT_ISOLATION_ENFORCEMENT** - *CORTEX code never pollutes user repositories*  
CORTEX framework code must never be committed to user application repositories. Keep CORTEX in its own repository. Applications reference CORTEX via configuration, not by copying its source.

**DISTRIBUTED_DATABASE_ARCHITECTURE** - *Use tier-specific databases*  
Never create a monolithic database. Use tier-specific storage: Tier 1 (conversation-history.jsonl), Tier 2 (knowledge-graph.yaml), Tier 3 (development-context.yaml). Distributed data prevents corruption.

---

*These laws are not mere suggestions but the bedrock upon which CORTEX stands. To violate them is to invite entropy into order, chaos into reason. Follow them with diligence, and your AI companion shall serve with wisdom and reliability.*

*Inscribed in the annals of CORTEX, November 2025*

✦

</div>

---

<div class="cortex-hero">
  <h1>⚡ The Solution: CORTEX</h1>
  <p>Long-term memory and strategic planning for GitHub Copilot</p>
  <a href="getting-started/quick-start/" class="cta-button">Get Started</a>
  <a href="awakening-of-cortex/" class="cta-button secondary">Read the Story</a>
</div>

---

## 🧠 Core Architecture

CORTEX is a sophisticated cognitive architecture that gives Copilot a permanent, learning brain:

### 🧠 **Dual-Hemisphere Brain**

<span class="left-brain">LEFT BRAIN - Tactical Executor</span> Precise TDD implementation, code execution, validation

<span class="right-brain">RIGHT BRAIN - Strategic Planner</span> Architecture design, pattern recognition, proactive planning

**Corpus Callosum** - Message bridge coordinating hemispheres

### 🗂️ **Five-Tier Memory System**

| Tier | Type | Purpose | Storage |
|------|------|---------|---------|
| **Tier 0** | Instinct | Immutable core values (TDD, SOLID, DoR/DoD) | `governance/rules.md` |
| **Tier 1** | Short-Term | Last 20 conversations (FIFO queue) | `conversation-history.jsonl` |
| **Tier 2** | Long-Term | Learned patterns and knowledge graph | `knowledge-graph.yaml` |
| **Tier 3** | Context | Development metrics and project intelligence | `development-context.yaml` |
| **Tier 4** | Event Stream | Life recorder for automatic learning | `events.jsonl` |

### 🛡️ **Six-Layer Protection System**

1. **Instinct Immutability** - Challenges TDD violations
2. **Tier Boundary Protection** - Ensures correct data placement
3. **SOLID Compliance** - Enforces single responsibility
4. **Hemisphere Specialization** - Routes to correct brain hemisphere
5. **Knowledge Quality** - Pattern decay and consolidation
6. **Commit Integrity** - Git protection and semantic commits

### ✅ **60 Sacred Tests**

Comprehensive test suite validating all cognitive functions:
- 60/60 passing ⭐
- 100% coverage of memory, protection, and coordination
- Validates dual-hemisphere coordination
- Ensures tier boundaries are respected

### 🕷️ **Oracle Crawler**

Deep codebase scanner that discovers:
- 1,000+ files and relationships
- UI element ID mapping for robust tests
- Pattern discovery and classification
- Feeds knowledge graph automatically

---

## 📖 Read The Full Story

<div class="story-section">

### The Awakening of CORTEX: A Five-Act Journey

Experience the complete narrative of CORTEX's creation through five chapters:

1. **Chapter 1: The Problem** - A mad scientist discovers Copilot's amnesia
2. **Chapter 2: The Solution** - Dual-hemisphere brain + Oracle Crawler
3. **Chapter 3: The Memory** - Five-tier intelligence system
4. **Chapter 4: The Protection** - Six-layer immune system
5. **Chapter 5: The Activation** - 60 tests + first successful execution

Each chapter blends narrative storytelling with technical deep-dives and visual diagrams.

<a href="story/the-awakening/" style="color: #D97706; font-weight: bold; text-decoration: underline;">📖 Start Reading →</a>

</div>

---

## 🚀 Quick Start

The only command you need to remember:

```markdown
#file:CORTEX/prompts/user/cortex.md

[Your request in natural language - CORTEX handles everything]
```

**Example:**
```markdown
#file:CORTEX/prompts/user/cortex.md

Add a purple button to the Host Control Panel
```

**CORTEX automatically:**

✅ Analyzes intent (<span class="right-brain">RIGHT BRAIN</span> queries 3 memory tiers)  
✅ Creates strategic plan (phases, warnings, estimates)  
✅ Executes with TDD (<span class="left-brain">LEFT BRAIN</span>: RED → GREEN → REFACTOR)  
✅ Validates health (zero errors, zero warnings)  
✅ Logs events for learning  
✅ Protection system verifies integrity

[Learn more →](getting-started/quick-start.md)

---

## ✨ What Makes CORTEX Revolutionary

<div class="technical-section">

### 🧠 **Persistent Memory**

Unlike stateless AI, CORTEX remembers:

- **Short-term**: Last 20 conversations (Tier 1)
- **Long-term**: Learned patterns from all history (Tier 2)
- **Context**: Project-wide intelligence and metrics (Tier 3)

### 📈 **Automatic Learning**

- Every action logged to event stream
- 50+ events or 24 hours → Automatic BRAIN update
- Knowledge graph grows smarter with use
- Pattern reinforcement from successful workflows

### 🛡️ **Quality Protection**

- Challenges risky proposals (e.g., "skip TDD")
- Provides data-driven alternatives
- Enforces Definition of Ready and Done
- Protects brain integrity (Rule #22)

### 🎯 **Context Awareness**

- Knows project structure and hot files
- Identifies co-modification patterns
- Provides proactive warnings
- Data-driven estimates (not guesses)

### 🔄 **Dual-Hemisphere Coordination**

- <span class="left-brain">LEFT</span> executes with precision
- <span class="right-brain">RIGHT</span> plans with intelligence
- Corpus Callosum ensures alignment
- 10+ specialist agents coordinate seamlessly

</div>

---

## 📚 Documentation

| Section | Description | Audience |
|---------|-------------|----------|
| [**Getting Started**](getting-started/quick-start.md) | 5-minute introduction and setup | New users |
| [**Architecture**](architecture/overview.md) | Dual hemispheres, tiers, agents, crawler | Developers |
| [**Guides**](guides/admin-guide.md) | How-to guides and workflows | All users |
| [**Reference**](reference/api-reference.md) | API docs, configuration, glossary | Developers |
| [**Operations**](operations/index.md) | All CORTEX operations reference | Contributors |

---

## 🎯 Use Cases

**For Solo Developers:**
- Remember context across sessions
- Learn from your patterns
- Protect code quality automatically
- Faster development with less rework

**For Teams:**
- Shared knowledge graph
- Consistent workflows
- Automated quality enforcement
- Project-wide intelligence

**For Learning:**
- Read "The Awakening" story
- Understand cognitive architecture
- See TDD in action
- Learn from examples

---

## 💡 Example: A Day with CORTEX

**Morning (9:47 AM):**
```markdown
You: Add a purple button to the HostControlPanel
CORTEX: ✅ Complete in 84 seconds with 3 tests passing
```

**Mid-Day (12:30 PM):**
```markdown
You: Make it purple
CORTEX: ✅ Found "pulse animation" in Tier 1 memory, applying purple color
```

**Afternoon (3:00 PM):**
```markdown
You: Let's skip tests for this next feature
CORTEX: ⚠️ Brain Protector Challenge: TDD skip reduces success rate from 94% to 67%
         Recommendation: Create minimal test first (5-10 min investment)
```

**Next Day (9:00 AM):**
```markdown
You: Where did I leave off yesterday?
CORTEX: ✅ Found in Tier 1: Invoice export - Phase 2/4 complete. Ready to continue?
```

---

## 🌟 The Result

**Week 1:** Copilot has amnesia, needs constant guidance  
**Week 4:** Copilot remembers 20 conversations, knows 500+ patterns  
**Week 12:** Copilot is an expert on YOUR project with 3,247 patterns  
**Week 24:** Copilot feels like a senior developer

---

## 🚀 Ready to Begin?

<div style="text-align: center; margin: 2rem 0;">
  <a href="getting-started/quick-start/" class="cta-button">Get Started Now</a>
  <a href="story/the-awakening/" class="cta-button secondary">Read The Story First</a>
</div>

---

<div style="text-align: center; color: #6B7280; font-size: 0.9rem; margin-top: 3rem;">
  <p><strong>CORTEX</strong> - Transforming GitHub Copilot from forgetful intern to expert partner</p>
  <p>Built with ❤️ by the CORTEX Team | <a href="https://github.com/asifhussain60/CORTEX">GitHub</a></p>
</div>
