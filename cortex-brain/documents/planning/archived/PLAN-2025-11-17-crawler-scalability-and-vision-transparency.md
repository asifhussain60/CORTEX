# CORTEX Feature Planning: Crawler Scalability & Vision API Transparency

**Created:** 2025-11-17  
**Status:** Active Planning  
**Complexity:** High (Crawler), Medium (Vision API)  
**Estimated Effort:** 12-16 hours total  
**Priority:** High (Enterprise readiness)

---

## 📋 Planning Summary

**Two interconnected features:**

1. **Intelligent Crawler Strategy for Massive Codebases**
   - Problem: Current crawler may timeout on 1000K+ LOC repos or large databases
   - Solution: Size-aware adaptive strategy with sampling + chunking
   - Benefit: Enterprise-scale codebase support without timeout failures

2. **Vision API Transparency in Responses**
   - Problem: Users can't see when Vision API is active or what it extracted
   - Solution: Custom response format showing Vision API invocation + extraction results
   - Benefit: Trust, debugging, understanding of AI vision capabilities

---

## 🎯 Feature 1: Intelligent Crawler Strategy (Massive Codebase Support)

### Problem Statement

**Current Limitation:**
- Crawler assumes manageable codebase size
- No timeout prevention for 1000K+ LOC repos
- No adaptive strategy based on discovered size
- Risk: Crawler hangs or fails on enterprise monoliths

**Real-World Scenarios:**
- Oracle database with 50,000 stored procedures
- .NET monolith with 500 projects, 1M+ LOC
- Legacy codebase with decades of accumulated code
- Multi-repo workspace with interconnected dependencies

### Proposed Architecture

#### Phase 1: Size Detection & Strategy Selection (Pre-Crawl)

**What:** Fast size estimation before full crawl begins

**How:**
1. **Quick Scan (30 seconds max)**
   - Count files by extension (*.cs, *.sql, *.py)
   - Estimate LOC using file size heuristics (avg bytes/line)
   - Check database object counts (tables, views, procs)
   - Detect repo structure (monorepo vs multi-repo)

2. **Strategy Selection Decision Tree**
   ```
   Size Category:
   - SMALL (<50K LOC, <500 objects) → Full Analysis Strategy
   - MEDIUM (50K-250K LOC) → Chunked Analysis Strategy
   - LARGE (250K-1M LOC) → Sampling + Chunking Strategy
   - MASSIVE (1M+ LOC) → Intelligent Sampling Strategy
   ```

3. **User Notification**
   ```
   🔍 Detected codebase size: ~1.2M LOC (MASSIVE)
   📊 Strategy: Intelligent Sampling (5% coverage)
   ⏱️ Estimated time: 8-12 minutes
   ⚙️ Adjustable: Say "full crawl" for 100% (may take 2+ hours)
   ```

#### Phase 2: Adaptive Crawling Strategies

**Strategy A: SMALL - Full Analysis (Default for <50K LOC)**
- Analyze every file, every method, every relationship
- Build complete dependency graph
- Extract all patterns, anti-patterns, metrics
- Time: 2-5 minutes
- Accuracy: 100%

**Strategy B: MEDIUM - Chunked Analysis (50K-250K LOC)**
- Divide codebase into logical chunks (by namespace, project, module)
- Process chunks sequentially with progress tracking
- Pause between chunks (prevent timeout)
- Time: 5-15 minutes
- Accuracy: 100%

**Strategy C: LARGE - Sampling + Chunking (250K-1M LOC)**
- Sample 20% of files intelligently:
  - All entry points (Main, startup files)
  - All public APIs (controllers, services)
  - Representative files from each namespace
  - Recently modified files (git history)
- Process sampled files in chunks
- Extrapolate patterns from sample
- Time: 8-20 minutes
- Accuracy: 85-95% (high-confidence estimation)

**Strategy D: MASSIVE - Intelligent Sampling (1M+ LOC)**
- Sample 5% of files using stratified sampling:
  - Stratify by: file type, namespace, modification date, LOC
  - Ensure representative coverage across all modules
  - Prioritize: Core business logic, API boundaries, shared utilities
- Parallel processing (multi-threaded)
- Progressive refinement (user can request deeper dives)
- Time: 10-30 minutes
- Accuracy: 70-85% (statistical confidence)

#### Phase 3: Timeout Prevention Mechanisms

**Mechanism 1: Time Budgets**
```python
BUDGET_LIMITS = {
    "SMALL": 300,      # 5 minutes max
    "MEDIUM": 900,     # 15 minutes max
    "LARGE": 1200,     # 20 minutes max
    "MASSIVE": 1800    # 30 minutes max
}
```

**Mechanism 2: Graceful Degradation**
- If approaching time budget (80% consumed):
  - Skip less critical analysis (code comments, formatting)
  - Reduce sampling depth
  - Prioritize high-value targets (core business logic)
- If time budget exceeded:
  - Save partial results
  - Mark as "incomplete" with percentage coverage
  - Offer resume option: "Resume crawl from 60% complete?"

**Mechanism 3: Progressive Disclosure**
- Real-time progress updates every 30 seconds:
  ```
  🔄 Crawling progress: 35% complete (1,200/3,500 files)
  📂 Current: src/services/authentication/
  ⏱️ Elapsed: 4m 32s | Remaining: ~8m
  ```

**Mechanism 4: Interruptible Checkpoints**
- Save state every 100 files processed
- User can interrupt: "pause crawl" or Ctrl+C
- Resume later: "resume crawl [session-id]"
- Checkpoint data: `cortex-brain/crawler-temp/checkpoint-[session-id].json`

#### Phase 4: Size-Aware Result Presentation

**For SMALL/MEDIUM (Full Analysis):**
```markdown
✅ Crawl Complete (100% coverage)

📊 Results:
   - Files analyzed: 1,234
   - Dependencies: 567 tracked
   - Patterns identified: 23
   - Architecture: Layered (3-tier)
   - Health score: 87/100

🔍 Deep Dive:
   - View dependency graph (Mermaid)
   - Explore file relationships
   - Check code quality metrics
```

**For LARGE/MASSIVE (Sampled Analysis):**
```markdown
✅ Crawl Complete (15% statistical sample)

📊 Results (95% confidence):
   - Estimated total LOC: ~1.2M
   - Sampled files: 4,521 / 30,000
   - Patterns identified: 18 (high-confidence)
   - Architecture: Modular monolith (estimated)
   - Health score: 72/100 (±8 margin)

⚠️ Sampling Strategy:
   - Stratified by namespace (12 strata)
   - Core modules: 100% coverage
   - Peripheral modules: 5% sample
   - Confidence intervals calculated

🔍 Options:
   1. Accept sample (recommended for planning)
   2. Deep dive into specific namespace (full analysis)
   3. Increase sample to 25% (~45 min)
   4. Schedule full crawl overnight (2-4 hours)
```

### Implementation Phases

#### Phase 1: Size Detection Engine (2 hours)
**Deliverables:**
- `src/crawler/size_detector.py` - Fast size estimation
- Heuristics for LOC estimation from file sizes
- Database object counting (SQL queries)
- Strategy selection logic

**Tests:**
- Unit: Size detection accuracy (±10% acceptable)
- Integration: Strategy selection for known repos
- Performance: Detection completes in <30 seconds

---

#### Phase 2: Adaptive Strategy Implementation (4 hours)
**Deliverables:**
- `src/crawler/strategies/` - Four strategy classes
  - `full_analysis_strategy.py`
  - `chunked_analysis_strategy.py`
  - `sampling_strategy.py`
  - `intelligent_sampling_strategy.py`
- Sampling algorithms (stratified, random, prioritized)
- Chunking logic (by namespace, project, etc.)

**Tests:**
- Unit: Each strategy processes test fixtures correctly
- Integration: Strategy switching based on size
- Performance: Sampling reduces time by 80-95%

---

#### Phase 3: Timeout Prevention (3 hours)
**Deliverables:**
- Time budget enforcement
- Graceful degradation logic
- Progress tracking (real-time updates)
- Checkpoint/resume system

**Tests:**
- Unit: Time budget triggers correctly
- Integration: Checkpoint save/restore works
- Performance: Overhead <5% for checkpointing

---

#### Phase 4: Result Presentation (1.5 hours)
**Deliverables:**
- Size-aware result formatting
- Confidence interval calculations
- Sampling strategy explanations
- Deep dive options (namespace focus)

**Tests:**
- Unit: Confidence intervals accurate
- Integration: Results match strategy used
- UX: Clear explanations, actionable options

---

#### Phase 5: Integration & Testing (2 hours)
**Deliverables:**
- End-to-end tests (SMALL → MASSIVE repos)
- Performance benchmarking
- Documentation updates

**Tests:**
- Integration: Full workflow (detection → strategy → results)
- Performance: No timeouts on 2M LOC test repo
- Regression: Existing crawls still work

---

### Acceptance Criteria (DoD)

**Functional:**
- ✅ Crawler detects codebase size in <30 seconds
- ✅ Selects appropriate strategy automatically
- ✅ MASSIVE repos (1M+ LOC) complete in <30 minutes
- ✅ No timeouts on 2M LOC test repository
- ✅ Sampling accuracy ≥70% for MASSIVE, ≥85% for LARGE
- ✅ User can interrupt/resume crawl at any checkpoint
- ✅ Progress updates every 30 seconds during crawl
- ✅ Results include confidence intervals for sampled analysis

**Quality:**
- ✅ Unit tests: ≥80% coverage
- ✅ Integration tests: All strategies tested end-to-end
- ✅ Performance tests: Benchmarks for 100K, 500K, 1M, 2M LOC
- ✅ Documentation: User guide + technical reference updated

**User Experience:**
- ✅ Clear size detection notification before crawl starts
- ✅ Real-time progress with time estimates
- ✅ Transparent sampling strategy explanation
- ✅ Options to adjust depth/coverage after results

---

### Risks & Mitigation

**Risk 1: Sampling accuracy too low for planning decisions**
- Mitigation: Allow users to request 25% or 50% samples
- Mitigation: Provide confidence intervals with all estimates
- Mitigation: "Deep dive" option for critical namespaces

**Risk 2: Stratified sampling misses critical code**
- Mitigation: Always include entry points, public APIs, core modules at 100%
- Mitigation: Git history analysis to find recently modified files
- Mitigation: User can specify "must-include" paths

**Risk 3: Checkpoint system adds overhead**
- Mitigation: Checkpoint every 100 files (not every file)
- Mitigation: Async checkpoint writes (don't block crawling)
- Mitigation: Measure overhead in performance tests (<5% acceptable)

**Risk 4: Multi-threading introduces race conditions**
- Mitigation: Thread-safe data structures for result aggregation
- Mitigation: Lock-free algorithms where possible
- Mitigation: Comprehensive concurrency tests

---

## 🎯 Feature 2: Vision API Transparency

### Problem Statement

**Current Limitation:**
- Users attach screenshots but don't see Vision API working
- No indication of what was extracted from image
- Debugging vision failures is impossible
- Trust issue: "Did CORTEX actually analyze my image?"

**User Confusion:**
```
User: [attaches login mockup] "plan authentication"
CORTEX: "I'll create a plan for authentication..."
User: 🤔 "Did you look at my screenshot?"
```

### Proposed Solution

#### Custom Response Format for Vision API

**When image/screenshot attached:**

```markdown
🧠 **CORTEX Interactive Planning** 🖼️ **[Vision API Active]**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

📸 **Vision Analysis:**
   Analyzing attached image: `login-mockup.png` (1920x1080, 245 KB)
   
   🔍 **Extracted Elements:**
   • Text Fields: Email Input, Password Input
   • Buttons: "Sign In" (primary), "Forgot Password?" (link)
   • Labels: "Email Address", "Password", "Remember Me" (checkbox)
   • Branding: Company logo (top-left), tagline
   • Layout: Centered card, 400px width, white background
   • Colors: Primary Blue (#4A90E2), Dark Gray (#333)
   
   🎯 **Inferred Requirements:**
   1. User authentication with email/password
   2. "Remember me" session persistence
   3. Password reset flow required
   4. Responsive design (mobile-friendly)
   5. Branding integration needed

🎯 **My Understanding Of Your Request:** 
   You want to plan an authentication feature based on the UI mockup provided (login screen with email/password fields)

⚠️ **Challenge:** ✓ **Accept**
   The mockup is clear and provides concrete UI requirements. I'll create a plan that matches this design.

💬 **Response:**
   I've extracted 8 UI elements from your mockup and identified 5 core requirements. Creating a planning file with pre-populated acceptance criteria based on visual analysis...

📝 **Your Request:** Plan authentication feature using provided UI mockup

🔍 Next Steps:
   ☐ Phase 1: Review Vision-Generated Acceptance Criteria
   ☐ Phase 2: Technical Architecture (backend + frontend)
   ☐ Phase 3: Implementation Plan (tasks per phase)
   
   Planning file created at: `cortex-brain/documents/planning/features/active/PLAN-authentication-vision-2025-11-17.md`
```

### Implementation Details

#### Phase 1: Vision API Response Headers (1 hour)

**Deliverables:**
- Response template variant: `response-templates.yaml` → `vision_api_active` template
- Vision extraction summary formatter
- Image metadata display (filename, dimensions, size)

**Structure:**
```python
class VisionResponseFormatter:
    def format_response_with_vision(
        self,
        image_path: str,
        extracted_elements: Dict[str, List[str]],
        inferred_requirements: List[str],
        confidence_scores: Dict[str, float]
    ) -> str:
        """
        Generate custom response format showing Vision API results
        
        Returns markdown with:
        - Image metadata
        - Extracted elements (categorized)
        - Inferred requirements
        - Confidence indicators
        """
```

**Example Categories for Extraction:**
- UI Elements: buttons, inputs, labels, checkboxes, dropdowns
- Text Content: headings, body text, error messages, tooltips
- Layout: positioning, spacing, alignment, grouping
- Colors: primary, secondary, accent, backgrounds
- Branding: logos, icons, typography
- Technical: form structure, validation hints, API endpoints (if visible in code screenshots)

---

#### Phase 2: Confidence Indicators (45 minutes)

**What:** Show confidence scores for vision extraction

**Why:** Vision API may misinterpret elements - transparency builds trust

**Format:**
```markdown
🔍 **Extracted Elements:**
   ✅ Text Fields: Email Input (95%), Password Input (98%)
   ⚠️ Buttons: "Sign In" (78% - low contrast, verify text)
   ✅ Checkbox: "Remember Me" (92%)
   ❓ Logo: Company branding (42% - unclear, manual verification needed)
```

**Thresholds:**
- ✅ High confidence: ≥85%
- ⚠️ Medium confidence: 70-84%
- ❓ Low confidence: <70% (flag for manual verification)

---

#### Phase 3: Vision Debugging Mode (1 hour)

**What:** Optional detailed view showing Vision API internals

**Trigger:** User says "vision debug" or sets `CORTEX_VISION_DEBUG=true`

**Output:**
```markdown
🐛 **Vision API Debug Info:**

🔌 API Used: GitHub Copilot Vision API v2.1
⏱️ Processing Time: 2.3 seconds
🖼️ Image Preprocessing: Resized 1920x1080 → 800x450 (API limit)

📊 Raw Extraction Results:
   - OCR Text: 47 text regions detected
   - Object Detection: 12 UI elements classified
   - Layout Analysis: 3 containers identified
   - Color Palette: 8 distinct colors extracted

🧠 Classification Confidence:
   - Button: 0.78 (threshold: 0.70, PASS)
   - Input Field: 0.95 (threshold: 0.85, PASS)
   - Logo: 0.42 (threshold: 0.60, FAIL - flagged)

⚠️ Warnings:
   - Low contrast detected (button text)
   - Ambiguous element (logo vs decorative image)
   - Recommend manual verification for flagged items
```

---

#### Phase 4: Vision Failure Handling (45 minutes)

**What:** Graceful degradation when Vision API fails

**Scenarios:**
1. **API Unavailable:** Fall back to filename-based heuristics
2. **Image Format Unsupported:** Notify user, proceed without vision
3. **Extraction Confidence Too Low:** Show what was extracted, ask for manual input
4. **API Rate Limit Hit:** Queue request, notify user of delay

**Example:**
```markdown
⚠️ **Vision API Notice:**
   
   Vision API is currently unavailable (GitHub service degraded).
   
   📋 Fallback Mode:
   - Detected image: `login-screen.png`
   - Inferred from filename: Login functionality
   - Proceeding with standard planning workflow
   
   💡 Tip: You can manually describe the screenshot:
   "The mockup shows email/password fields with a blue sign-in button"
```

---

### Implementation Phases

#### Phase 1: Response Template Updates (1 hour)
**Deliverables:**
- `vision_api_active` template variant
- Image metadata formatter
- Extracted elements display logic

**Tests:**
- Template renders correctly with vision data
- Confidence indicators show properly
- Graceful handling of missing vision data

---

#### Phase 2: Vision Extraction Formatter (1.5 hours)
**Deliverables:**
- `src/vision/extraction_formatter.py`
- Categorization logic (UI elements, text, layout, colors)
- Confidence score integration

**Tests:**
- All element types formatted correctly
- Confidence thresholds applied
- Categorization accurate (button vs link, etc.)

---

#### Phase 3: Debug Mode Implementation (1 hour)
**Deliverables:**
- Debug flag detection
- Detailed vision logging
- API metadata collection

**Tests:**
- Debug mode toggles correctly
- No performance impact when disabled
- Sensitive data not exposed in debug logs

---

#### Phase 4: Failure Handling (1 hour)
**Deliverables:**
- Fallback strategies for each failure scenario
- User notifications
- Graceful degradation logic

**Tests:**
- All failure scenarios handled
- No crashes when Vision API unavailable
- User receives clear explanations

---

#### Phase 5: Integration Testing (1 hour)
**Deliverables:**
- End-to-end tests with real images
- Performance benchmarks
- Documentation updates

**Tests:**
- Vision + Planning workflow works end-to-end
- Response format displays correctly in GitHub Copilot Chat
- No regressions in non-vision workflows

---

### Acceptance Criteria (DoD)

**Functional:**
- ✅ Vision API invocation visible in response header
- ✅ Extracted elements displayed with categories
- ✅ Confidence scores shown for all extractions
- ✅ Low-confidence items flagged for manual verification
- ✅ Debug mode available for troubleshooting
- ✅ Graceful fallback when Vision API unavailable

**Quality:**
- ✅ Unit tests: ≥80% coverage
- ✅ Integration tests: Vision + Planning workflow
- ✅ Manual testing: 5 different screenshot types
- ✅ Documentation: User guide updated

**User Experience:**
- ✅ Clear indication Vision API is active
- ✅ Transparent about what was extracted
- ✅ Confidence in results (or lack thereof)
- ✅ Debugging possible when extraction fails

---

### Risks & Mitigation

**Risk 1: Vision API response too verbose (clutters chat)**
- Mitigation: Collapsible sections for extracted elements
- Mitigation: Summary view by default, "show details" option
- Mitigation: User setting: `vision_detail_level: minimal|standard|verbose`

**Risk 2: Low confidence extractions mislead users**
- Mitigation: Always show confidence scores
- Mitigation: Flag items <70% for manual review
- Mitigation: Explain why confidence is low (contrast, blur, ambiguity)

**Risk 3: Vision API adds latency to planning workflow**
- Mitigation: Async vision processing (show planning UI immediately)
- Mitigation: Pre-populate plan while vision processes in background
- Mitigation: Update plan with vision results when ready (live)

---

## 🔗 Integration Between Features

**Synergy:** Crawler + Vision API

**Use Case:** Screenshot of database schema diagram
1. User: [attaches ER diagram] "crawl this database"
2. Vision API: Extracts table names, relationships, key fields
3. Crawler: Uses vision-extracted schema as crawl target hints
4. Result: Focused crawl on specific tables (not blind exploration)

**Benefit:** Vision guides crawler to high-value targets in massive schemas

---

## 📊 Overall Timeline

| Phase | Feature | Duration | Dependencies |
|-------|---------|----------|--------------|
| **Week 1** | | | |
| Phase 1.1 | Size Detection Engine | 2h | None |
| Phase 1.2 | Vision Response Templates | 1h | None |
| Phase 1.3 | Vision Extraction Formatter | 1.5h | Phase 1.2 |
| **Week 2** | | | |
| Phase 2.1 | Adaptive Strategies (all 4) | 4h | Phase 1.1 |
| Phase 2.2 | Vision Confidence Indicators | 45m | Phase 1.3 |
| Phase 2.3 | Vision Debug Mode | 1h | Phase 1.3 |
| **Week 3** | | | |
| Phase 3.1 | Timeout Prevention | 3h | Phase 2.1 |
| Phase 3.2 | Vision Failure Handling | 1h | Phase 2.2 |
| Phase 3.3 | Result Presentation | 1.5h | Phase 3.1 |
| **Week 4** | | | |
| Phase 4.1 | Crawler Integration Testing | 2h | Phase 3.3 |
| Phase 4.2 | Vision Integration Testing | 1h | Phase 3.2 |
| Phase 4.3 | Documentation | 1h | All |

**Total Estimated Effort:** 15.75 hours (~2 work weeks)

---

## ✅ Definition of Ready (DoR)

**Before starting implementation:**

- [ ] Planning file reviewed and approved
- [ ] Test repository prepared (100K, 500K, 1M, 2M LOC variants)
- [ ] Vision API access confirmed (GitHub Copilot)
- [ ] Sample images collected (UI mockups, diagrams, error screenshots)
- [ ] Performance benchmarks baseline established
- [ ] Integration points identified (crawler → knowledge graph, vision → planning)
- [ ] Fallback strategies defined for all failure scenarios

---

## ✅ Definition of Done (DoD)

**For completion:**

**Crawler:**
- [ ] All 4 strategies implemented and tested
- [ ] Size detection accurate (±10% margin)
- [ ] No timeouts on 2M LOC test repo
- [ ] Sampling accuracy meets thresholds (70% MASSIVE, 85% LARGE)
- [ ] Checkpoint/resume system works
- [ ] Progress updates display correctly
- [ ] Result presentation includes confidence intervals
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests pass (all size categories)
- [ ] Performance benchmarks documented

**Vision API:**
- [ ] Custom response format displays in GitHub Copilot Chat
- [ ] All extraction categories implemented
- [ ] Confidence indicators accurate
- [ ] Debug mode functional
- [ ] Failure handling tested (API down, rate limit, unsupported format)
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests pass (vision → planning workflow)
- [ ] Manual testing completed (5+ screenshot types)

**Documentation:**
- [ ] User guide updated (both features)
- [ ] Technical reference updated (API docs)
- [ ] Example screenshots with expected outputs
- [ ] Troubleshooting section (vision failures, crawler timeouts)

**Deployment:**
- [ ] No regressions in existing workflows
- [ ] Feature flags available (can disable if issues arise)
- [ ] Monitoring in place (crawler performance, vision API success rate)

---

## 🎯 Success Metrics

**Crawler:**
- Time to complete 1M LOC repo: <30 minutes (target)
- Sampling accuracy: ≥70% for MASSIVE, ≥85% for LARGE
- Timeout rate: <1% (across all size categories)
- User satisfaction: ≥4.0/5.0 (feedback survey)

**Vision API:**
- Extraction accuracy: ≥85% (compared to manual analysis)
- User awareness: 100% (users always see Vision API notice)
- Confidence calibration: Low-confidence flags are genuinely ambiguous (validated manually)
- User trust: ≥4.5/5.0 (feedback survey)

---

## 📝 Notes & Decisions

**Decision 1: Why stratified sampling for MASSIVE repos?**
- Rationale: Random sampling may miss entire modules/namespaces
- Stratification ensures representative coverage across all layers
- Trade-off: Slightly more complex algorithm, but much better accuracy

**Decision 2: Why show confidence scores in Vision API responses?**
- Rationale: Vision AI is not 100% accurate, transparency builds trust
- Users can manually verify low-confidence extractions
- Debugging vision issues is easier with confidence data

**Decision 3: Why separate strategies instead of one adaptive algorithm?**
- Rationale: Different size categories have fundamentally different needs
- Small repos: Full analysis is feasible and valuable
- Massive repos: Sampling is mandatory, full analysis impractical
- Cleaner code separation vs complex conditional logic

**Decision 4: Why file-based planning for this session?**
- Rationale: Complex multi-feature plan, needs persistence
- Chat-only would lose details when window closes
- File allows iterative refinement and approval workflow
- Directly integrates with CORTEX development pipeline

---

## 🔄 Next Actions

**Immediate:**
1. Review this planning file
2. Approve or request changes
3. Prioritize: Crawler first (higher risk) or Vision API first (faster win)?

**After Approval:**
1. Create test repositories (100K, 500K, 1M, 2M LOC)
2. Collect sample images (UI mockups, diagrams, error screenshots)
3. Set up feature branches: `feature/crawler-scalability`, `feature/vision-transparency`
4. Begin Phase 1 implementation

**Checkpoints:**
- End of Week 1: Size detection + Vision templates working
- End of Week 2: All strategies implemented, confidence indicators ready
- End of Week 3: Timeout prevention complete, failure handling tested
- End of Week 4: Full integration, documentation, ready for release

---

**Status:** ACTIVE PLANNING - Awaiting approval  
**Next Update:** After user review and feedback  
**File Location:** `cortex-brain/documents/planning/features/active/PLAN-2025-11-17-crawler-scalability-and-vision-transparency.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file
