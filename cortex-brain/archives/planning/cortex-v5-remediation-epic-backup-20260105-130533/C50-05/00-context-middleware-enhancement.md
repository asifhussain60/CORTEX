# C50-05: Context Middleware Enhancement

**Plan ID:** C50-05  
**Epic:** C50 CORTEX v5 Gap Remediation  
**Status:** 🔄 IN PROGRESS  
**Duration:** 2-3 days (24 hours)  
**Dependencies:** C50-00C (Test Coverage Sprint) ✅

---

## 🎯 Objective

Enhance the existing `CrossSessionContextMiddleware` with deeper Vision API integration, file relationship analysis, and semantic search to provide richer context for orchestrators.

**Current State:**
- ✅ Basic continuation detection (`continue`, `resume`, `next phase`)
- ✅ Session manager integration (orchestrator sessions)
- ✅ Project tracker integration (active planning projects)
- ✅ Token-efficient metadata injection (<200 tokens)

**Gap Analysis:**
- ❌ Vision API context not automatically injected from middleware
- ❌ File relationships not analyzed for context enrichment
- ❌ Semantic search not integrated for relevant code discovery
- ❌ No priority-based context source ranking

---

## 📋 Phases

### Phase 1: Vision API Integration (6h)

**Goal:** Automatically inject Vision API analysis results into context when images are present

**Tasks:**
1. Integrate with existing `VisionContextMiddleware` and `ImageContextMiddleware`
2. Add vision context detection to `enrich_context()` method
3. Inject vision analysis metadata (<100 tokens) when images detected
4. Add vision context priority (Priority 1: highest importance)

**Deliverables:**
- Enhanced `enrich_context()` with vision detection
- Vision metadata injection logic
- 5 unit tests for vision integration

**Acceptance Criteria:**
- ✅ Vision context detected from image attachments
- ✅ Vision metadata injected (<100 tokens)
- ✅ No duplicate vision analysis (cache-aware)
- ✅ All tests passing

---

### Phase 2: File Relationship Analysis (8h)

**Goal:** Add file relationship context to help orchestrators understand code dependencies

**Tasks:**
1. Integrate with `file-relationships.yaml` knowledge graph
2. Add `analyze_file_relationships()` method
3. Inject related files metadata when specific files mentioned
4. Add relationship context priority (Priority 3)

**Deliverables:**
- File relationship analyzer
- Related files metadata injection
- 6 unit tests for relationship analysis

**Acceptance Criteria:**
- ✅ File relationships loaded from knowledge graph
- ✅ Related files detected from user input
- ✅ Dependency context injected (<150 tokens)
- ✅ All tests passing

---

### Phase 3: Semantic Search Integration (8h)

**Goal:** Use semantic search to find relevant code context automatically

**Tasks:**
1. Integrate with existing semantic search infrastructure
2. Add `semantic_context_search()` method
3. Inject relevant code snippets when technical terms detected
4. Add semantic context priority (Priority 4)

**Deliverables:**
- Semantic search integration
- Context-aware code discovery
- 5 unit tests for semantic search

**Acceptance Criteria:**
- ✅ Semantic search triggered on technical queries
- ✅ Relevant code snippets injected (<200 tokens)
- ✅ Token budget respected (total <500 tokens)
- ✅ All tests passing

---

### Phase 4: Priority-Based Context Ranking (2h)

**Goal:** Implement priority system to manage token budget across context sources

**Tasks:**
1. Add priority ranking system (1=highest, 4=lowest)
2. Implement token budget management (<500 tokens total)
3. Add context trimming when budget exceeded
4. Update documentation

**Priority Order:**
1. **Vision Context** (Priority 1): Image analysis when images present (~100 tokens)
2. **Session Context** (Priority 2): Recent orchestrator/project sessions (~100 tokens)
3. **File Relationships** (Priority 3): Related files when specific files mentioned (~150 tokens)
4. **Semantic Search** (Priority 4): Relevant code when technical terms detected (~150 tokens)

**Budget Management:**
- Total budget: 500 tokens
- If exceeded: Trim Priority 4, then Priority 3, preserve Priority 1-2

**Deliverables:**
- Priority ranking implementation
- Token budget manager
- Context trimming logic
- 4 unit tests for priority system
- Updated documentation

**Acceptance Criteria:**
- ✅ Priority system implemented
- ✅ Token budget enforced
- ✅ Context trimmed when needed
- ✅ Documentation updated
- ✅ All tests passing

---

## 🎯 Definition of Done

- ✅ Vision API integration complete
- ✅ File relationship analysis implemented
- ✅ Semantic search integrated
- ✅ Priority-based ranking operational
- ✅ 20 unit tests (100% passing)
- ✅ Token budget system working (<500 tokens)
- ✅ Documentation updated
- ✅ Integration tests passing
- ✅ No regression in existing middleware functionality

---

## 📊 Success Metrics

- **Token Efficiency:** Context injection ≤500 tokens (vs manual context gathering)
- **Coverage:** 20+ tests, 85%+ coverage
- **Performance:** Context enrichment <100ms
- **Integration:** Works with all 9 orchestrators

---

## 🔗 References

- Existing: `src/orchestrators/context_middleware.py` (288 lines)
- Vision: `src/operations/utilities/vision_context_middleware.py`
- Vision: `src/operations/utilities/image_context_middleware.py`
- Files: `cortex-brain/file-relationships.yaml`
- Epic: `00-cortex-v5-remediation.md`
- Manifest: `c50-epic-manifest.yaml`

---

**Author:** Asif Hussain  
**Created:** 2026-01-04  
**Last Updated:** 2026-01-04
