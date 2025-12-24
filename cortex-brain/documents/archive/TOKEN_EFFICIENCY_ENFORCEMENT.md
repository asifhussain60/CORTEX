# TOKEN_EFFICIENCY_ENFORCEMENT Evidence Template

**Rule ID:** TOKEN_EFFICIENCY_ENFORCEMENT  
**Category:** Token Management  
**Severity:** blocked

## Detection Context

Token budget violation detected in governance files!

**Operation:** '{operation}'  
**File:** '{file_path}'  
**Current size:** {current_tokens} tokens ({current_chars} characters)  
**Budget:** {max_tokens} tokens ({max_chars} characters)  
**Overage:** +{overage_tokens} tokens (+{overage_percent}%)

❌ **BLOCKED**: Governance file exceeds token budget

## Why Token Efficiency Matters

### The Problem (Current State)

- **Total baseline:** 98,000 tokens across 4 governance files
- **GitHub Copilot context window:** 200,000 tokens
- **CORTEX baseline consumption:** 49% of available context
- **Result:** Premature summarization every 3rd user statement
- **Impact:** Users see "summarizing conversation" interruption

### Token Budget Breakdown

| File | Current | Budget | Reduction Needed |
|------|---------|--------|------------------|
| CORTEX.prompt.md | 23K | 5K | 78.3% (18K) |
| brain-protection-rules.yaml | 60K | 8K | 86.7% (52K) |
| response-templates.yaml | 10K | 3K | 70.0% (7K) |
| copilot-instructions.md | 5K | 1K | 80.0% (4K) |
| **TOTAL** | **98K** | **17K** | **82.7% (81K)** |

### Your File Status

- **File:** {file_path}
- **Current:** {current_tokens} tokens
- **Budget:** {max_tokens} tokens
- **Status:** ❌ {overage_tokens} tokens over budget

## Optimization Techniques Available

### 1. Modularization (Phase 1 - 88.8% reduction)
- Extract detailed content to separate .md files
- Use #file: references in main governance files
- Example: Move "TDD Mastery Guide" to modules/tdd-mastery-guide.md
- Keep only summary + reference link in CORTEX.prompt.md

### 2. Template Compression (Phase 2 - 94.9% reduction)
- YAML anchor inheritance (&base_template)
- Shared components (header, footer, sections)
- Placeholder-based content (<operation>, <understanding>)
- Remove duplicate formatting instructions

### 3. Lazy Loading (Phase 3 - 96.9% reduction)
- Load SKULL rules only when triggered
- Index-based lookup (rule_id → file location)
- Cache in session memory
- Base load = index + metadata only

### 4. Reference Compression (Phase 4 - 98.0% reduction)
- Convert inline examples to reference pointers
- Store code samples in separate files
- Symbolic references (REF-001 → example.md)
- Load examples only when user requests details

## Immediate Actions

```bash
# 1. Validate current token usage
align governance-tokens validate

# 2. Analyze which content can be extracted
align governance-tokens analyze --file {file_path}

# 3. View optimization recommendations
align governance-tokens recommend

# 4. Apply automated fixes (if available)
align governance-tokens optimize --phase 1
```

## Manual Optimization (if automated unavailable)

### 1. Identify extraction candidates
- Long explanations (>500 chars)
- Code examples
- Detailed workflows
- Historical context
- Tutorial content

### 2. Create module file
```bash
# Create new module in .github/prompts/modules/
touch .github/prompts/modules/[feature]-guide.md
```

### 3. Move content to module
- Copy content from {file_path}
- Paste into module file
- Add module header (## Title, Purpose, Author)

### 4. Replace with reference
```markdown
# In {file_path}

## [Feature Name]
**Complete Guide:** #file:modules/[feature]-guide.md

[Brief 2-3 sentence summary only]
```

### 5. Validate reduction
```bash
align governance-tokens validate
# Should show: ✅ {file_path} within budget
```

## 4-Phase Optimization Strategy

### Phase 1: Modularization (Week 1)
- **Target:** 88.8% reduction (98K → 11K tokens)
- Extract 20+ detailed guides to modules/
- CORTEX.prompt.md: 23K → 5K tokens
- brain-protection-rules.yaml: 60K → 5K tokens
- response-templates.yaml: 10K → 1K tokens

### Phase 2: Template Compression (Week 2)
- **Target:** 94.9% reduction (98K → 5K tokens)
- YAML anchor inheritance
- Shared components (43% duplicate reduction)
- Placeholder-based injection

### Phase 3: Lazy Loading (Week 3)
- **Target:** 96.9% reduction (98K → 3K tokens)
- On-demand SKULL rule loading
- Index-based lookup system
- Session-level caching

### Phase 4: Reference Compression (Week 4)
- **Target:** 98.0% reduction (98K → 2K tokens)
- Symbolic references for examples
- Separate file storage
- Load on user request only

## Success Metrics

- ✅ Token budget compliance (17K max)
- ✅ No premature summarization (<10th statement)
- ✅ Context window utilization <10% (vs 49% current)
- ✅ Zero functionality loss (all features preserved)
- ✅ Deployment gate passes (Gate 16: Token Validation)

## Deployment Gate 16 (Token Validation)

This deployment gate automatically validates token efficiency:
- **Runs:** Pre-merge validation in CI/CD
- **Checks:** All 4 governance files
- **Fails:** If any file exceeds budget
- **Blocks:** Production deployment until resolved
- **Reports:** Overage details + optimization suggestions

## Testing

Token efficiency is validated by:
- `tests/tier0/test_token_efficiency_enforcement.py` (19 tests)
- Pre-commit hook: `.git/hooks/pre-commit-token-check`
- CI/CD Gate 16: Automated validation
- `align` CLI: Manual validation anytime

## Related Documentation

- TOKEN-OPTIMIZATION-HOLISTIC-PLAN.md - Complete 4-phase strategy
- .github/prompts/modules/token-efficiency-guide.md - Detailed implementation
- tests/tier0/test_token_efficiency_enforcement.py - Validation suite

## Need Help?

```bash
# Get optimization recommendations
align governance-tokens help

# Show current token usage breakdown
align governance-tokens status

# Dry-run optimization
align governance-tokens optimize --dry-run
```

## Related

**Rationale:** #file:documents/rationales/TOKEN_EFFICIENCY_ENFORCEMENT.md
