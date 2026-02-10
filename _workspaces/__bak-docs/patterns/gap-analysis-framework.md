# Gap Analysis Framework Pattern
**Extracted from:** chat01.md DIGEST (2026-02-04)  
**Reusability:** HIGH  
**Context:** Multi-dimensional gap identification for CORTEX enhancements

---

## Problem

When planning CORTEX enhancements, need a systematic framework to:
- Identify gaps comprehensively (not just surface issues)
- Link gaps to stakeholder impact (business value)
- Prioritize with evidence (not opinions)
- Generate actionable roadmaps (not vague recommendations)

---

## Solution

**5-Dimensional Gap Analysis Framework**

### 1. Current vs. Missing Analysis

| Dimension | Current State | Gap | Evidence |
|-----------|--------------|-----|----------|
| {Feature Area} | {What exists today} | {What's missing} | {Implementation Truth proof} |

**Example from chat01.md:**
```yaml
Dimension: Multi-Language AST Parsing
Current: Python-only deep analysis (ast.parse)
Gap: No AST parsing for C#, Java, TypeScript, JavaScript
Evidence:
  - cortex/lens/analyzers/ast_analyzer.py: Python-specific
  - No tree-sitter integration detected (grep search)
```

### 2. Stakeholder Impact Mapping

For EACH gap, document impact on ALL stakeholder personas:

| Persona | Current Pain | Gap Impact | Benefit When Fixed |
|---------|-------------|-----------|-------------------|
| Business Leaders | Cannot see system capabilities | ❌ No business narratives for non-Python | ✅ Full feature visibility |
| Product Owners | Cannot understand coverage | ❌ Use case extraction fails | ✅ Automated feature discovery |
| Software Engineers | Cannot navigate code | ❌ No class/method extraction | ✅ Architecture diagrams |
| Architects | Cannot visualize system | ❌ No polyglot analysis | ✅ Cross-stack architecture |

**Why This Works:**
- Connects technical gaps to business outcomes
- Builds consensus across roles
- Justifies investment (ROI clear)

### 3. Evidence-Based Priority Scoring

```yaml
Gap Scoring Matrix:
  
  Impact Score (1-5):
    5: Blocks 30%+ of users
    4: Degrades experience for key workflows
    3: Noticeable friction
    2: Nice-to-have
    1: Edge case
  
  Evidence Score (1-5):
    5: Multiple Implementation Truth proofs (grep, file scans, user reports)
    4: Strong code analysis + user feedback
    3: Code analysis only
    2: Anecdotal reports
    1: Hypothesis
  
  Feasibility Score (1-5):
    5: <2 weeks, low risk
    4: 2-4 weeks, dependencies manageable
    3: 1-2 months, moderate complexity
    2: 3-6 months, architectural changes
    1: >6 months, R&D required
  
  Priority = (Impact × Evidence) / Feasibility
```

**Example Calculation:**
```
Gap: Multi-Language AST Parsing
Impact: 5 (blocks 30% of repos)
Evidence: 5 (multiple grep proofs, chat transcript, dashboards)
Feasibility: 3 (4 weeks, tree-sitter integration)
Priority = (5 × 5) / 3 = 8.3 → P0
```

### 4. Phased Roadmap Generation

```yaml
Phase Template:
  
  Phase {N}: {Title}
    Duration: {X weeks}
    Dependencies: [{prior phases}]
    Deliverables:
      - {Concrete artifact 1}
      - {Concrete artifact 2}
    Tests:
      Unit: {count}
      Integration: {count}
      E2E: {count}
    Success Criteria:
      - {Measurable metric 1}
      - {Measurable metric 2}
    Risk Mitigation:
      - {Known risk} → {Mitigation strategy}
```

**Anti-Pattern:** Vague phases like "Improve X" without deliverables

**Best Practice:** Concrete deliverables with test counts

### 5. Comprehensive Risk Assessment

For EACH gap fix, document:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| {What could go wrong} | {H/M/L} | {H/M/L} | {Proactive prevention} |

**Example:**
```yaml
Risk: Tree-sitter performance on large repos
Likelihood: Medium (depends on repo size)
Impact: High (onboarding timeouts)
Mitigation:
  - Limit files per language (default 100)
  - Parallel parsing
  - Cache AST results
  - Incremental analysis
```

---

## Usage Pattern

### Step 1: Context Gathering (LENS)
```bash
# Use MCP tools to gather evidence
cortex_git_history(repo_path, hours=24)
cortex_lens_analyze(target="cortex/lens/analyzers/")
cortex_detect_duplicates(scope="full")
grep_search(query="ast.parse|tree-sitter|polyglot")
```

### Step 2: Gap Identification
```yaml
Gap {N}:
  Title: {Concise gap name}
  Current: {What exists today}
  Missing: {What's not there}
  Impact: {Business consequence}
  Evidence: [{proof 1}, {proof 2}]
  Stakeholders: {Affected personas}
```

### Step 3: Stakeholder Impact Matrix
```markdown
| Persona | Pain | Impact | Benefit |
```

### Step 4: Priority Scoring
```
Priority = (Impact × Evidence) / Feasibility
```

### Step 5: Phased Roadmap
```yaml
Phase 0: Foundation (1 week)
Phase 1: Core (4 weeks)
Phase 2: Integration (2 weeks)
...
```

### Step 6: Risk Mitigation
```yaml
Risk {N}: {description}
  Likelihood: {H/M/L}
  Impact: {H/M/L}
  Mitigation: [{strategy 1}, {strategy 2}]
```

---

## Metrics for Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Gap Coverage** | 100% (all identified) | # gaps with evidence / total mentioned |
| **Stakeholder Alignment** | 4+ personas | # stakeholders with documented impact |
| **Evidence Quality** | 80%+ scored 4-5 | # gaps with Implementation Truth proof |
| **Roadmap Clarity** | 100% phases have tests | # phases with test counts / total phases |
| **Risk Preparation** | 100% risks mitigated | # risks with mitigation / total risks |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Better Approach |
|--------------|---------|-----------------|
| **Opinion-Based Gaps** | "I think we need X" | Evidence-based (grep, user feedback) |
| **Single-Persona Analysis** | Misses cross-role value | All 4 personas (business, PM, eng, arch) |
| **Vague Roadmaps** | "Improve X" | Concrete deliverables + test counts |
| **No Risk Assessment** | Surprises in execution | Proactive mitigation planning |
| **Feasibility Ignored** | P0 everything | Realistic effort estimates (S/M/L) |

---

## Related Patterns

- [Enhancement Roadmap Template](enhancement-roadmap-template.md)
- [Stakeholder Impact Mapping](stakeholder-impact-mapping.md)
- [Evidence-Based Design](evidence-based-design.md)

---

## Example Application (chat01.md)

**Success Metrics:**
- ✅ 5 gaps identified (complete coverage)
- ✅ 4 stakeholder personas documented
- ✅ 100% gaps have Implementation Truth evidence
- ✅ 6-phase roadmap with 300 test estimates
- ✅ 3 risks with mitigation strategies

**Result:** Clear P0 recommendation (Multi-Language AST) with 16-week phased plan
