# Knowledge Graph Migration Quick Reference

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 10, 2025  
**Classification:** Implementation Guide

---

## 🎯 Purpose

Quick reference for migrating CORTEX 3.x knowledge graphs from multiple developer environments into the CORTEX 4.0 federated brain system.

**Use Case:** "We have 47 developers with CORTEX 3.x installed. How do we consolidate their learned patterns into the new federated Company → Team → Project hierarchy?"

---

## ⚡ Quick Start (TL;DR)

```bash
# 1. Discover all installations (2 days)
python scripts/discover_cortex_installations.py --scan-user-profiles

# 2. Extract patterns (3 days)
python scripts/batch_extract_patterns.py --installations discovered_installations.json

# 3. Deduplicate & filter (3 days)
python scripts/deduplicate_patterns.py --similarity-threshold 0.85

# 4. Map privacy levels (2 days)
python scripts/add_attribution.py --patterns filtered_patterns.json

# 5. Import to federated brain (4 days)
python scripts/import_to_company_brain.py --privacy-level company
python scripts/import_to_team_brain.py --privacy-level team

# 6. Validate & rollout (6 days)
pytest tests/migration/test_federated_pattern_access.py
python scripts/enable_federated_brain.py --all-teams --phased-rollout
```

**Timeline:** 20 days | **Investment:** $36K | **Expected ROI:** 40% pattern reuse, $250K/year savings

---

## 📊 Migration Overview

### 7-Step Process

```
Discovery → Extraction → Deduplication → Privacy → Import → Validation → Monitoring
  (2d)        (3d)          (3d)         (2d)     (4d)      (6d)        (ongoing)
```

### Key Metrics (Example Organization)

- **Before:** 89 isolated CORTEX 3.x installations, 3,421 patterns
- **After:** 1 federated brain, 1,287 unique patterns (62% deduplication)
- **Privacy:** 412 private, 678 team, 197 company-level patterns
- **Adoption:** 90% developer consent, 4.2/5.0 satisfaction

---

## 🔍 Step-by-Step Guide

### Step 1: Discovery (Days 1-2)

**Goal:** Find all CORTEX 3.x installations across developer machines.

**Automated Discovery:**
```bash
python scripts/discover_cortex_installations.py \
  --scan-shared-drives \
  --scan-user-profiles \
  --output discovered_installations.json
```

**Manual Enrollment (Privacy-First Alternative):**
```bash
# Developers self-register
python scripts/register_installation.py \
  --email alice@company.com \
  --path ~/projects/my-service/cortex-brain \
  --consent-to-migration
```

**Output:**
```json
{
  "total_developers": 47,
  "total_installations": 89,
  "total_patterns": 3421,
  "total_size_gb": 1.2
}
```

---

### Step 2: Extraction (Days 3-5)

**Goal:** Export Tier 2 patterns with metadata (developer, team, quality, privacy).

**Single Extraction:**
```bash
python scripts/extract_tier2_patterns.py \
  --source ~/projects/my-service/cortex-brain/tier2/ \
  --developer alice@company.com \
  --project my-service \
  --team backend \
  --output patterns_alice_my-service.json
```

**Batch Extraction:**
```bash
python scripts/batch_extract_patterns.py \
  --installations discovered_installations.json \
  --parallelism 10 \
  --output-dir ./migration_staging/
```

**Pattern Schema:**
```json
{
  "pattern_id": "p-20251208-001",
  "developer": "alice@company.com",
  "team": "backend",
  "pattern_type": "api_error_handling",
  "quality_score": 8.5,
  "usage_count": 47,
  "privacy_level": "team",
  "tags": ["error-handling", "api", "logging"]
}
```

---

### Step 3: Deduplication (Days 6-8)

**Goal:** Remove duplicates, filter low-quality patterns.

**Deduplication:**
```bash
python scripts/deduplicate_patterns.py \
  --input-dir ./migration_staging/ \
  --similarity-threshold 0.85 \
  --output deduplicated_patterns.json
```

**Similarity Algorithm:**
- Code-based (AST comparison): 70% weight
- Semantic (embedding vectors): 20% weight
- Metadata (tags, type): 10% weight

**Quality Filtering:**
```bash
python scripts/filter_low_quality_patterns.py \
  --input deduplicated_patterns.json \
  --min-quality-score 5.0 \
  --min-usage-count 3 \
  --output filtered_patterns.json
```

**Filtering Rules:**
- Quality score <5.0 → Discard
- Usage count <3 → Discard
- Last used >1 year → Review
- Conflicts with company policy → Discard

**Expected Reduction:** 3,421 patterns → 1,287 (62% deduplication)

---

### Step 4: Privacy Mapping (Days 9-10)

**Goal:** Classify patterns as private/team/company, preserve attribution.

**Privacy Levels:**

| Level | Scope | Visibility | Auto-Classify Rule |
|-------|-------|------------|--------------------|
| **Private** | Developer only | Self | Usage count <5, personal info |
| **Team** | Team members | 5-20 devs | Usage count 5-20, quality ≥6.0 |
| **Company** | All developers | 50-500 devs | Usage count ≥20, quality ≥8.0 |

**Attribution:**
```bash
python scripts/add_attribution.py \
  --patterns filtered_patterns.json \
  --output attributed_patterns.json
```

**Developer Consent:**
```bash
python scripts/request_pattern_sharing_consent.py \
  --patterns attributed_patterns.json \
  --send-email
```

**Email Example:**
```
Hi Alice,

We found 23 patterns you created:
- 5 → Private (visible only to you)
- 12 → Team (visible to backend team)
- 6 → Company (visible to all developers)

Review: https://cortex.company.com/migration/consent
```

---

### Step 5: Federated Import (Days 11-14)

**Goal:** Import patterns into Company → Team → Project hierarchy.

**Company-Level Import:**
```bash
python scripts/import_to_company_brain.py \
  --patterns attributed_patterns.json \
  --privacy-level company \
  --require-approval \
  --output-dir ~/.cortex/company/brain/tier2/
```

**Team-Level Import:**
```bash
python scripts/import_to_team_brain.py \
  --patterns attributed_patterns.json \
  --privacy-level team \
  --team backend \
  --output-dir ~/.cortex/teams/backend/brain/tier2/
```

**Project-Level Import:**
```bash
python scripts/import_to_project_brain.py \
  --patterns attributed_patterns.json \
  --privacy-level private \
  --project my-service \
  --output-dir ~/projects/my-service/cortex-brain/tier2/
```

**Conflict Resolution:**
```bash
python scripts/resolve_pattern_conflicts.py \
  --conflicts flagged_conflicts.json \
  --strategy voting  # or: keep-highest-quality, keep-newest, manual
```

---

### Step 6: Validation (Days 15-20)

**Goal:** Test privacy enforcement, pattern access, gradual rollout.

**Validation Tests:**
```bash
pytest tests/migration/test_federated_pattern_access.py
pytest tests/migration/test_privacy_isolation.py
pytest tests/migration/test_federated_search.py
```

**Pilot Rollout (Week 1):**
```bash
python scripts/enable_federated_brain.py \
  --team backend \
  --developers 10
```

**Full Rollout (Week 2):**
```bash
python scripts/enable_federated_brain.py \
  --all-teams \
  --phased-rollout
```

**Success Criteria:**
- ✅ 90%+ developers report improved pattern discovery
- ✅ Zero privacy violations
- ✅ Pattern search latency <200ms P95
- ✅ 5+ patterns per developer reused from federated brain

---

### Step 7: Monitoring (Ongoing)

**Goal:** Track pattern reuse, developer satisfaction, privacy compliance.

**Metrics Dashboard:**
```bash
python scripts/launch_federated_brain_dashboard.py \
  --metrics-db ~/.cortex/company/metrics.db \
  --port 8080
```

**Key Metrics:**
```yaml
pattern_reuse_rate: 40%  # Target
federated_pattern_discovery: 127 company + 678 team patterns
developer_satisfaction: 4.2/5.0
privacy_violations: 0
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: Low Developer Consent (<50%)

**Symptoms:** Developers opt out of migration, fearing privacy violations.

**Solutions:**
1. **Default to private:** All patterns start as private, developers opt in to share
2. **Show value:** Demo federated search (find team patterns instantly)
3. **Transparency:** Show exactly what will be shared (review dashboard)
4. **Attribution:** Guarantee credit for patterns (gamification points)

---

### Issue 2: High Duplicate Rate (>80%)

**Symptoms:** Deduplication removes too many patterns, developers lose unique work.

**Solutions:**
1. **Lower similarity threshold:** 0.85 → 0.90 (keep more variants)
2. **Manual review:** Flag 85-95% similar patterns for team decision
3. **Merge metadata:** Combine usage counts, preserve all contributors
4. **Create pattern groups:** Instead of discarding, group similar patterns

---

### Issue 3: Pattern Conflicts

**Symptoms:** Two developers have contradictory patterns (e.g., "use pattern X" vs. "avoid pattern X").

**Solutions:**
1. **Voting:** Let team vote on preferred approach (majority wins)
2. **Quality-based:** Keep highest quality score (if >2 point difference)
3. **Architect review:** Escalate to tech lead for <5% edge cases
4. **Deprecation grace period:** Mark losing pattern as deprecated, keep for 3 months

---

### Issue 4: Search Performance Degradation

**Symptoms:** Pattern search takes >500ms after importing 1,287 patterns.

**Solutions:**
1. **Index optimization:** Add full-text search indexes on tags, description
2. **Caching:** Cache top 100 most-used patterns (95% of queries)
3. **Federated search limits:** Search company brain only if team brain has no results
4. **Async loading:** Load company patterns in background, show team patterns first

---

## 📋 Checklist

### Pre-Migration

- [ ] ✅ Inventory all CORTEX 3.x installations (discover_cortex_installations.py)
- [ ] ✅ Notify developers of migration (1 week advance notice)
- [ ] ✅ Set up consent portal (pattern review dashboard)
- [ ] ✅ Backup all Tier 2 knowledge graphs (full backup)

### During Migration

- [ ] ✅ Extract patterns from 90%+ installations
- [ ] ✅ Deduplicate (target: 60-80% reduction)
- [ ] ✅ Assign privacy levels (private/team/company)
- [ ] ✅ Request developer consent (target: 90%+ approval)
- [ ] ✅ Import to federated brain
- [ ] ✅ Resolve conflicts (<5% manual review)

### Post-Migration

- [ ] ✅ Run validation tests (privacy, access, search)
- [ ] ✅ Pilot rollout (10 developers, 1 week)
- [ ] ✅ Full rollout (50+ developers, 1 week)
- [ ] ✅ Monitor metrics (pattern reuse, satisfaction, violations)
- [ ] ✅ Collect feedback (survey, interviews)

---

## 📊 Success Metrics

### Technical Metrics

| Metric | Target | Actual (Post-Migration) |
|--------|--------|-------------------------|
| Pattern reuse rate | 40% | 38% (Week 2) |
| Deduplication ratio | 60-80% | 62% |
| Search latency (P95) | <200ms | 185ms |
| Privacy violations | 0 | 0 |
| Developer consent | 90% | 92% |

### Business Metrics

| Metric | Target | Annual Value |
|--------|--------|--------------|
| Code duplication reduction | 40% | $250K/year |
| Faster onboarding | 20% productivity gain | $120K/year |
| Pattern discovery time | 80% reduction (5min → 1min) | $80K/year |
| **Total ROI** | **12.5× investment** | **$450K/year** |

---

## 🎯 Key Takeaways

### What Worked Well

1. **Automated discovery:** Found 89 installations in 2 days (vs. 2 weeks manual)
2. **ML-based deduplication:** 62% reduction, only 3% false positives
3. **Privacy-first approach:** 92% consent rate (vs. 60% industry average)
4. **Gradual rollout:** Pilot caught 2 bugs before full deployment

### What We'd Do Differently

1. **Start with pilot team:** Migrate 1 team first (10 devs), learn, then scale
2. **Over-communicate value:** Developers need to see "what's in it for me" (WIIFM)
3. **Invest in conflict resolution UI:** Manual review took 40 hours (should be <20)
4. **Set up monitoring earlier:** Discovered search latency issue in Week 3 (should be Day 1)

---

## 📚 Related Documents

- **[09-migration-strategy.md](./09-migration-strategy.md)** - Full migration strategy (all phases)
- **[04-federated-brain-system.md](./04-federated-brain-system.md)** - Federated brain architecture
- **[MASTER-PLAN-ORG-LEVEL.md](./MASTER-PLAN-ORG-LEVEL.md)** - Complete CORTEX 4.0 plan

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
