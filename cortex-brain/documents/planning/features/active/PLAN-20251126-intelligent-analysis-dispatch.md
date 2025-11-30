# Intelligent Analysis Dispatch System - Implementation Plan

**Created:** 2025-11-26  
**Status:** Planning  
**Priority:** High  
**Estimated Duration:** 3 weeks  
**Dependencies:** Documentation Format Enforcement (APPROVED-20251126)

---

## 🎯 Overview

Automatically detect analysis intent (analyze/review/understand/explain) and intelligently dispatch crawlers to generate comprehensive multi-format documentation without user micromanagement.

**Vision:** User says "analyze PayrollManager code" → CORTEX produces visual diagrams, markdown documentation, metrics, and exports automatically.

---

## 📋 Definition of Ready (DoR)

### Requirements Documentation
- [x] Analysis intent detection keywords identified
- [x] Three-tier intelligence system defined (Scope/Format/Depth)
- [x] Format selection logic documented
- [x] Override mechanisms specified
- [x] Performance requirements established

### Dependencies
- [x] Documentation Format Enforcement plan approved
- [x] Interactive dashboard generator (will be built in parallel)
- [x] Existing crawler infrastructure available
- [x] Pattern matching algorithms defined

### Technical Design
- [x] Intent detection architecture designed
- [x] Scope detection algorithms specified
- [x] Format intelligence rules defined
- [x] Dispatch orchestration workflow documented

### Test Strategy
- [x] Intent detection test cases defined
- [x] Format selection validation tests planned
- [x] End-to-end analysis workflows tested
- [x] Performance benchmarks established

### Acceptance Criteria
- [ ] "analyze X" triggers automatic multi-format documentation
- [ ] Scope detection accuracy >90% (file/feature/architecture)
- [ ] Format selection appropriate for context
- [ ] Standard analysis completes in <15 seconds
- [ ] Deep analysis completes in <60 seconds
- [ ] User override options functional

### Security Review (OWASP)
**Feature Type:** Automatic Code Analysis + Documentation Generation

**A01 - Broken Access Control:**
- [x] Repository access validation before analysis
- [x] No unauthorized file access during crawling
- [x] Respect .gitignore and sensitive file patterns

**A03 - Injection:**
- [x] Sanitize file paths before crawler execution
- [x] Safe code parsing (AST-based, not eval)
- [x] Output escaping for generated documentation

**A05 - Security Misconfiguration:**
- [x] Default to safe analysis depth (standard, not deep)
- [x] Rate limiting on crawler execution
- [x] Resource limits (memory, CPU, time)

**A08 - Software and Data Integrity Failures:**
- [x] Validate analysis results before document generation
- [x] Checksum verification for generated files
- [x] Rollback on analysis failures

---

## 🏗️ Phase Breakdown

### ☐ Phase 1: Intent Detection & Scope Analysis (Week 1, Days 1-2)

**Duration:** 2 days (16 hours)

**Tasks:**

1. **Create Intent Detection Engine** (5 hours)
   - Module: `src/cortex_agents/strategic/intent_analyzer_agent.py`
   - Features:
     - Keyword detection: analyze, review, understand, explain, investigate
     - Context extraction: what to analyze (file, feature, architecture)
     - Depth modifier detection: quick, brief, deep, comprehensive
     - Override detection: "as markdown", "visual only", "no diagrams"
   - Tests: `tests/cortex_agents/strategic/test_intent_analyzer_agent.py`
   - **Output:** Intent detection with 90%+ accuracy

2. **Create Scope Detection Logic** (4 hours)
   - Module: `src/analysis/scope_detector.py`
   - Features:
     - File-level detection: Specific file paths/names mentioned
     - Feature-level detection: Pattern matching (auth*, payment*, user*)
     - Architecture-level detection: "application", "codebase", "system"
     - Complexity estimation: Component count, dependency depth
   - Tests: `tests/analysis/test_scope_detector.py`
   - **Output:** Accurate scope classification

3. **Create Format Intelligence Rules** (4 hours)
   - Configuration: `cortex-brain/documents/standards/format-intelligence-rules.yaml`
   - Rules:
     - Visual triggers: complexity_score, component_count, journey_detected
     - Markdown triggers: simple_code, api_docs, summary_only
     - Hybrid triggers: feature_analysis, review_request
     - Override handling: user-specified format preferences
   - **Output:** Format selection rule engine

4. **Create Depth Control System** (3 hours)
   - Module: `src/analysis/depth_controller.py`
   - Features:
     - Quick mode: 2-5s, markdown + simple diagram
     - Standard mode: 10-15s, markdown + Mermaid + metrics (default)
     - Deep mode: 30-60s, full dashboard + all formats + exports
     - Auto-escalation: Bump depth if complexity high
   - Tests: `tests/analysis/test_depth_controller.py`
   - **Output:** Depth control logic

**Acceptance Criteria:**
- ✅ Intent detection accuracy >90% on test cases
- ✅ Scope classification correct for file/feature/architecture
- ✅ Format rules validated with 20+ scenarios
- ✅ Depth control respects time limits

---

### ☐ Phase 2: Analysis Dispatch Orchestrator (Week 1, Days 3-5)

**Duration:** 3 days (24 hours)

**Tasks:**

1. **Create Analysis Dispatch Orchestrator** (8 hours)
   - Module: `src/orchestrators/analysis_dispatch_orchestrator.py`
   - Workflow:
     1. Receive user request
     2. Detect intent (analyze/review/understand)
     3. Determine scope (file/feature/architecture)
     4. Select formats (visual/markdown/hybrid)
     5. Choose depth (quick/standard/deep)
     6. Dispatch crawlers
     7. Generate documentation
     8. Save outputs
   - Tests: `tests/orchestrators/test_analysis_dispatch_orchestrator.py`
   - **Output:** Central orchestration logic

2. **Integrate Crawler System** (6 hours)
   - Module: `src/analysis/crawler_dispatcher.py`
   - Features:
     - File crawler: Parse single file, extract methods/classes
     - Feature crawler: Scan pattern-matched files, build feature map
     - Architecture crawler: Full repo scan, component graph
     - Dependency analyzer: Build call graphs, import trees
   - Tests: `tests/analysis/test_crawler_dispatcher.py`
   - **Output:** Unified crawler interface

3. **Create Documentation Generator Adapter** (5 hours)
   - Module: `src/analysis/documentation_adapter.py`
   - Features:
     - Markdown generator: Code summaries, API docs
     - Mermaid generator: Flow diagrams, class diagrams
     - D3.js generator: Interactive dashboards (uses existing template)
     - Export generator: PDF/PNG/PPTX outputs
   - Tests: `tests/analysis/test_documentation_adapter.py`
   - **Output:** Multi-format generation

4. **Add Progress Tracking** (3 hours)
   - Module: `src/analysis/progress_tracker.py`
   - Features:
     - Real-time status updates
     - Estimated completion time
     - Stage indicators: Analyzing → Generating → Exporting
     - Error handling with partial results
   - **Output:** User-visible progress

5. **Create Output Manager** (2 hours)
   - Module: `src/analysis/output_manager.py`
   - Features:
     - Organize outputs in structured directories
     - Generate index.md with links to all formats
     - Create "View Analysis" shortcuts
     - Handle output cleanup/versioning
   - **Output:** Organized documentation structure

**Acceptance Criteria:**
- ✅ Orchestrator handles all three scope levels
- ✅ Crawlers execute without errors
- ✅ Documentation generated in all requested formats
- ✅ Progress visible to user
- ✅ Outputs organized and accessible

---

### ☐ Phase 3: Format Intelligence Implementation (Week 2, Days 1-3)

**Duration:** 3 days (24 hours)

**Tasks:**

1. **Implement Visual Format Generator** (8 hours)
   - Module: `src/analysis/formatters/visual_formatter.py`
   - Outputs:
     - D3.js interactive dashboard (for architecture/feature)
     - Mermaid flowcharts (for sequences, flows)
     - Mermaid class diagrams (for OOP analysis)
     - Mermaid state diagrams (for state machines)
     - Component graphs (for dependencies)
   - Tests: `tests/analysis/formatters/test_visual_formatter.py`
   - **Output:** Comprehensive visual documentation

2. **Implement Markdown Format Generator** (6 hours)
   - Module: `src/analysis/formatters/markdown_formatter.py`
   - Outputs:
     - Executive summary (3-5 sentences)
     - Component breakdown (classes, methods, responsibilities)
     - API documentation (public interfaces)
     - Code metrics (complexity, LOC, test coverage)
     - Recommendations (refactoring, improvements)
   - Tests: `tests/analysis/formatters/test_markdown_formatter.py`
   - **Output:** Professional markdown documentation

3. **Implement Hybrid Format Generator** (5 hours)
   - Module: `src/analysis/formatters/hybrid_formatter.py`
   - Outputs:
     - Markdown with embedded Mermaid diagrams
     - HTML with interactive sections + markdown content
     - Tabbed interface (Overview/Code/Diagrams/Metrics)
   - Tests: `tests/analysis/formatters/test_hybrid_formatter.py`
   - **Output:** Best-of-both-worlds documentation

4. **Implement Export Format Generator** (5 hours)
   - Module: `src/analysis/formatters/export_formatter.py`
   - Outputs:
     - PDF export (using markdown-pdf or similar)
     - PNG export (screenshot dashboards)
     - PPTX export (presentation slides)
     - JSON export (machine-readable analysis)
   - Tests: `tests/analysis/formatters/test_export_formatter.py`
   - **Output:** Shareable documentation formats

**Acceptance Criteria:**
- ✅ Visual formats render correctly
- ✅ Markdown formats comprehensive and readable
- ✅ Hybrid formats combine best of both
- ✅ Export formats functional and professional

---

### ☐ Phase 4: Intelligence Rules & Override System (Week 2, Days 4-5)

**Duration:** 2 days (16 hours)

**Tasks:**

1. **Implement Format Selection Engine** (5 hours)
   - Module: `src/analysis/format_selector.py`
   - Logic:
     - Calculate complexity score (dependencies, LOC, cyclomatic)
     - Count components (files, classes, methods)
     - Detect patterns (user journeys, state machines)
     - Apply rules from format-intelligence-rules.yaml
     - Select appropriate formats
   - Tests: `tests/analysis/test_format_selector.py`
   - **Output:** Intelligent format selection

2. **Implement Override System** (4 hours)
   - Module: `src/analysis/override_handler.py`
   - Features:
     - Parse override keywords: "as markdown", "visual only", "no exports"
     - Validate override requests (prevent conflicts)
     - Apply user preferences from config
     - Log override decisions for learning
   - Tests: `tests/analysis/test_override_handler.py`
   - **Output:** User control over automation

3. **Create Format Intelligence Configuration** (4 hours)
   - File: `cortex-brain/documents/standards/format-intelligence-rules.yaml`
   - Rules:
     - Complexity thresholds for visual formats
     - File count thresholds for architecture analysis
     - Pattern detection rules (auth, payment, etc.)
     - Default format preferences by scope
   - **Output:** Configurable intelligence rules

4. **Add Learning System (Basic)** (3 hours)
   - Module: `src/analysis/format_learner.py`
   - Features:
     - Track user overrides (what they prefer)
     - Store preferences in Tier 3 (per-repo)
     - Adjust defaults based on patterns
     - Provide "forget preferences" option
   - Tests: `tests/analysis/test_format_learner.py`
   - **Output:** Adaptive format selection

**Acceptance Criteria:**
- ✅ Format selection matches complexity appropriately
- ✅ User overrides respected
- ✅ Configuration rules editable
- ✅ Learning system improves over time

---

### ☐ Phase 5: Integration & Entry Point Updates (Week 3, Days 1-2)

**Duration:** 2 days (16 hours)

**Tasks:**

1. **Update Intent Router** (4 hours)
   - Module: `src/cortex_agents/intent_router.py`
   - Changes:
     - Add analysis intent detection (analyze/review/understand)
     - Route to AnalysisDispatchOrchestrator
     - Pass context (file paths, user request, overrides)
   - Tests: Update existing intent router tests
   - **Output:** Automatic routing to analysis

2. **Create Analysis Agent** (5 hours)
   - Module: `src/cortex_agents/tactical/analysis_agent.py`
   - Features:
     - Implements BaseAgent interface
     - can_handle: Detects analysis intent
     - execute: Calls AnalysisDispatchOrchestrator
     - Returns: AgentResponse with document links
   - Tests: `tests/cortex_agents/tactical/test_analysis_agent.py`
   - **Output:** Analysis agent integrated

3. **Update Response Templates** (3 hours)
   - File: `cortex-brain/response-templates.yaml`
   - Templates:
     - analysis_started: Progress notification
     - analysis_complete: Links to generated docs
     - analysis_error: Error handling with suggestions
   - **Output:** User-friendly responses

4. **Update CORTEX.prompt.md** (2 hours)
   - File: `.github/prompts/CORTEX.prompt.md`
   - Sections:
     - Add "Intelligent Analysis" section
     - Document natural language commands
     - Explain scope/format/depth detection
     - Provide examples
   - **Output:** Documentation updated

5. **Update System Alignment** (2 hours)
   - Module: `src/operations/modules/admin/system_alignment_orchestrator.py`
   - Changes:
     - Add analysis agent to discovered agents
     - Include analysis orchestrator in scoring
     - Validate format intelligence integration
   - **Output:** Alignment includes new system

**Acceptance Criteria:**
- ✅ Natural language analysis commands work
- ✅ Intent router detects and routes correctly
- ✅ Response templates provide clear feedback
- ✅ Documentation updated
- ✅ System alignment includes new components

---

### ☐ Phase 6: Testing & Validation (Week 3, Days 3-4)

**Duration:** 2 days (16 hours)

**Test Scenarios:**

1. **File-Level Analysis Tests** (4 hours)
   - "analyze PayrollManager.cs"
   - "review src/utils/helper.py"
   - "understand this file" (with active editor)
   - **Expected:** File analysis + method diagrams + markdown
   - **Performance:** <10 seconds

2. **Feature-Level Analysis Tests** (4 hours)
   - "analyze authentication system"
   - "review payment processing"
   - "understand user management"
   - **Expected:** Feature map + flow diagrams + comprehensive docs
   - **Performance:** <15 seconds

3. **Architecture-Level Analysis Tests** (4 hours)
   - "analyze the application"
   - "review entire codebase"
   - "understand system architecture"
   - **Expected:** Full dashboard + component graph + all exports
   - **Performance:** <60 seconds

4. **Override Tests** (2 hours)
   - "analyze X as markdown only"
   - "quick analyze Y"
   - "deep review Z with exports"
   - **Expected:** User preferences respected

5. **Error Handling Tests** (2 hours)
   - Invalid file paths
   - Empty repositories
   - Unsupported file types
   - Timeout scenarios

**Acceptance Criteria:**
- ✅ 100% test pass rate
- ✅ Performance targets met for all depth levels
- ✅ Error handling graceful
- ✅ Generated documentation validates against schemas

---

### ☐ Phase 7: Documentation & Deployment (Week 3, Day 5)

**Duration:** 1 day (8 hours)

**Tasks:**

1. **Create User Guide** (3 hours)
   - File: `cortex-brain/documents/guides/INTELLIGENT-ANALYSIS-GUIDE.md`
   - Sections:
     - How to use analysis commands
     - Scope detection examples
     - Format selection logic
     - Override options
     - Troubleshooting
   - **Output:** Comprehensive user guide

2. **Create Configuration Guide** (2 hours)
   - File: `cortex-brain/documents/guides/ANALYSIS-CONFIGURATION-GUIDE.md`
   - Sections:
     - format-intelligence-rules.yaml documentation
     - Customizing complexity thresholds
     - Adding new pattern matchers
     - Adjusting performance settings
   - **Output:** Admin configuration guide

3. **Update Module Documentation** (2 hours)
   - Update all relevant module README files
   - Add examples to docstrings
   - Document public APIs
   - **Output:** Complete code documentation

4. **Deploy to Production** (1 hour)
   - Run full validation suite
   - Execute deployment pipeline
   - Verify analysis commands work
   - Update VERSION to 3.4.0
   - Tag release
   - **Output:** Production deployment

**Acceptance Criteria:**
- ✅ User guide complete with examples
- ✅ Configuration guide clear
- ✅ All modules documented
- ✅ Deployment successful

---

## 🎯 Definition of Done (DoD)

### Code Quality
- [x] All analysis components implemented
- [x] 100% test pass rate
- [x] 80%+ test coverage on new code
- [x] Code reviewed and approved

### Functionality
- [x] "analyze X" triggers automatic analysis
- [x] Scope detection >90% accuracy
- [x] Format intelligence works correctly
- [x] Override system functional
- [x] Performance targets met

### Documentation
- [x] User guide complete
- [x] Configuration guide complete
- [x] CORTEX.prompt.md updated
- [x] Module documentation complete

### Integration
- [x] Intent router integration complete
- [x] Analysis agent registered
- [x] System alignment includes new components
- [x] Response templates updated

### Deployment
- [x] All tests passing
- [x] Manual testing completed
- [x] Performance validated
- [x] Deployed to production
- [x] Version tagged (v3.4.0)

---

## 🚨 Risk Analysis

### High Risk

1. **Performance Degradation on Large Codebases**
   - Impact: High (>60s for deep analysis)
   - Mitigation: Progressive analysis, caching, parallel processing
   - Contingency: Add "analyze in background" option

2. **Incorrect Scope Detection**
   - Impact: High (analyzes wrong things)
   - Mitigation: Extensive testing, user confirmation for ambiguous requests
   - Contingency: Add "did you mean?" suggestions

### Medium Risk

3. **Format Selection Mismatches**
   - Impact: Medium (generates wrong format)
   - Mitigation: Conservative defaults, user overrides
   - Contingency: Allow format regeneration

4. **Crawler Errors on Complex Code**
   - Impact: Medium (incomplete analysis)
   - Mitigation: Robust error handling, partial results
   - Contingency: Fallback to simpler analysis

### Low Risk

5. **User Confusion on Automatic Behavior**
   - Impact: Low (users surprised by automation)
   - Mitigation: Clear documentation, progress indicators
   - Contingency: Add "explain what you're doing" mode

---

## 📊 Success Metrics

### Quantitative
- **Intent Detection Accuracy:** >90%
- **Scope Detection Accuracy:** >90%
- **Format Selection Accuracy:** >85% (user satisfaction)
- **Performance:**
  - Quick: <5s
  - Standard: <15s
  - Deep: <60s
- **Test Coverage:** >80%

### Qualitative
- **User Experience:** "Just works" without micromanagement
- **Documentation Quality:** Professional, comprehensive
- **Differentiation:** Clear advantage over manual documentation
- **Adaptability:** System learns from user preferences

---

## 🔄 Rollback Plan

**If deployment fails:**

1. **Immediate Rollback** (5 minutes)
   - Revert intent router changes
   - Disable analysis agent registration
   - Restore previous version

2. **Root Cause Analysis** (1 hour)
   - Identify failing component
   - Review logs and errors
   - Document failure conditions

3. **Fix and Redeploy** (varies)
   - Apply targeted fix
   - Run regression tests
   - Gradual rollout with monitoring

---

## 📦 Deliverables Summary

### Core Modules
- `src/cortex_agents/strategic/intent_analyzer_agent.py`
- `src/orchestrators/analysis_dispatch_orchestrator.py`
- `src/analysis/scope_detector.py`
- `src/analysis/depth_controller.py`
- `src/analysis/format_selector.py`
- `src/analysis/crawler_dispatcher.py`
- `src/analysis/documentation_adapter.py`
- `src/cortex_agents/tactical/analysis_agent.py`

### Formatters
- `src/analysis/formatters/visual_formatter.py`
- `src/analysis/formatters/markdown_formatter.py`
- `src/analysis/formatters/hybrid_formatter.py`
- `src/analysis/formatters/export_formatter.py`

### Configuration
- `cortex-brain/documents/standards/format-intelligence-rules.yaml`

### Documentation
- `cortex-brain/documents/guides/INTELLIGENT-ANALYSIS-GUIDE.md`
- `cortex-brain/documents/guides/ANALYSIS-CONFIGURATION-GUIDE.md`
- Updated `.github/prompts/CORTEX.prompt.md`

### Tests
- 12+ test files covering all components

---

**Plan Created:** 2025-11-26  
**Estimated Completion:** 3 weeks (80 hours)  
**Author:** Asif Hussain  
**Status:** Awaiting Approval
