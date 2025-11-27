# Token Usage Audit - Track 2 Phase B2
**Date:** 2025-11-16  
**Phase:** Phase B2 Task B2.1 - Token Bloat Audit  
**Current Score:** Token Usage 0/100 (55 issues identified)  
**Target Score:** Token Usage 80/100  

## Top Token Offenders

### Prompts Directory (Top 20)
| File | Size (KB) | Est. Tokens | Priority | Category |
|------|-----------|-------------|----------|----------|
| refresh-docs.md | 47.80 | 12,236 | HIGH | User prompt |
| intent-router.md | 31.42 | 8,044 | HIGH | Internal |
| technical-reference.md | 31.24 | 7,997 | MEDIUM | Shared doc |
| agents-guide.md | 26.42 | 6,764 | MEDIUM | Shared doc |
| brain-crawler.md | 25.86 | 6,621 | HIGH | Internal |
| configuration-reference.md | 24.89 | 6,372 | MEDIUM | Shared doc |
| work-planner.md | 23.64 | 6,051 | HIGH | Internal |
| commit-handler.md | 22.75 | 5,824 | MEDIUM | Internal |
| PHASE-3-TEST-RESULTS-ANALYSIS.md | 22.66 | 5,801 | LOW | Archive candidate |
| story.md | 21.66 | 5,544 | MEDIUM | Shared doc |
| code-executor.md | 21.59 | 5,528 | HIGH | Internal |
| brain-query.md | 20.11 | 5,149 | HIGH | Internal |
| mandatory-post-task.md | 19.45 | 4,980 | MEDIUM | Shared |
| test-generator.md | 19.21 | 4,918 | MEDIUM | Internal |
| brain-updater.md | 19.12 | 4,894 | HIGH | Internal |
| brain-amnesia.md | 19.04 | 4,875 | HIGH | Internal |
| tracking-guide.md | 18.32 | 4,691 | LOW | Shared doc |
| publish.md | 17.76 | 4,547 | MEDIUM | Shared |
| execution-tracer.md | 17.65 | 4,519 | MEDIUM | Shared |
| setup-guide.md | 17.06 | 4,368 | LOW | Shared doc |

**Prompts Total (Top 20):** ~120,000 tokens

### Cortex-Brain Directory (Top 20)
| File | Size (KB) | Est. Tokens | Priority | Category |
|------|-----------|-------------|----------|----------|
| the-awakening-of-cortex.md (archive) | 72.60 | 18,586 | LOW | Already archived |
| CORTEX-STORYTELLING-CONTEXT.md | 48.24 | 12,349 | LOW | Simulation |
| CORTEX-2.0-CAPABILITY-ANALYSIS.md (archive) | 46.11 | 11,803 | LOW | Already archived |
| STORY-REFRESH-REDESIGN-IMPLEMENTATION-PLAN.md | 39.26 | 10,051 | MEDIUM | Planning doc |
| 2025-11-13-path-1-execution-session.md (vault) | 38.99 | 9,982 | LOW | Conversation |
| 2025-11-13-path-1-execution-session.md (captures) | 38.33 | 9,813 | LOW | Conversation |
| PHASE-5.1-TEST-DESIGN.md | 35.71 | 9,142 | MEDIUM | Planning doc |
| CORTEX-3.0-DIAGRAM-CATALOG.md | 35.71 | 9,142 | MEDIUM | Planning doc |
| REQUEST-VALIDATOR-CODE-EXAMPLES.md (archive) | 35.65 | 9,127 | LOW | Already archived |
| REQUEST-VALIDATOR-VISUAL-ARCHITECTURE.md | 28.57 | 7,314 | MEDIUM | Planning doc |

**Cortex-Brain Total (Top 20):** ~106,000 tokens

## Optimization Strategy

### Phase B2.2: High-Impact Refactoring (20 hours)

#### Immediate Actions (High ROI)
1. **Archive Validation Files** (2 hours)
   - Move `PHASE-3-TEST-RESULTS-ANALYSIS.md` to archives
   - These are reference-only, rarely loaded
   - Estimated savings: ~6,000 tokens

2. **Split Large User Prompts** (6 hours)
   - `refresh-docs.md` (12K tokens) → Modular refresh system
   - Convert to operation-based loading (lazy load sections)
   - Estimated savings: ~8,000 tokens

3. **Modularize Internal Agent Prompts** (8 hours)
   - `intent-router.md` (8K tokens) → Intent patterns YAML + minimal MD
   - `work-planner.md` (6K tokens) → Planning templates YAML
   - `brain-crawler.md` (6.6K tokens) → Crawler config YAML
   - `code-executor.md` (5.5K tokens) → Execution patterns YAML
   - Estimated savings: ~15,000 tokens

4. **Convert Shared Docs to YAML Schemas** (4 hours)
   - `agents-guide.md` (6.7K) → `agent-specs.yaml`
   - `configuration-reference.md` (6.4K) → `config-specs.yaml`
   - Estimated savings: ~8,000 tokens (60% reduction)

**Total Estimated Savings:** ~37,000 tokens (from top offenders)

### Phase B2.3: Lazy Loading System (6 hours)

#### Implementation
- Section-based markdown loading (load only `## Section` headers needed)
- YAML reference system for documentation
- On-demand prompt assembly

#### Target Files for Lazy Loading
- All "reference" and "guide" documentation
- Technical specifications
- Large planning documents

**Expected Impact:** 50% reduction in typical conversation token load

### Phase B2.4: Validation (2 hours)

#### Success Criteria
- Token score: 0/100 → 80/100 (+80 points)
- Overall optimizer score: 75/100 → 90/100 (+15 points, reach target)
- All functionality preserved
- Zero test failures

## Timeline
- **B2.1 Audit:** 1 hour (COMPLETE)
- **B2.2 Refactoring:** 20 hours (4 days) - NEXT
- **B2.3 Lazy Loading:** 6 hours (1 day)
- **B2.4 Validation:** 2 hours (0.5 days)

**Total:** 29 hours over 5.5 days

## Next Step
Begin Phase B2.2 with highest-impact optimization: Archive validation files and split refresh-docs.md
