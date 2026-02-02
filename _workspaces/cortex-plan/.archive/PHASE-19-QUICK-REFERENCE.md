# PHASE-19: LENS Unified Intelligence - Quick Reference

**Version:** 1.0 | **Created:** 2026-02-02  
**Status:** 📋 PLANNED - Ready for Implementation  
**Duration:** 4 weeks (80 hours estimated)

---

## 🎯 ONE-SENTENCE SUMMARY

Transform LENS into a multi-faceted intelligence system that executes ALL capabilities (AST, Git, Config, Pattern, Vendor, Database) in a single scan while building domain knowledge incrementally (snowball effect).

---

## ⚡ CRITICAL GAPS (Must Fix)

1. **`_update_company_domains()` NOT IMPLEMENTED** - Called at line 230 of repository_onboarding_orchestrator.py but method doesn't exist
2. **DomainKnowledgeMerger MISSING** - Core snowball accumulator not created
3. **VendorDetector MISSING** - Vendor intelligence not operational
4. **DatabaseCrawlerPlugin MISSING** - Database schema extraction not available
5. **PatternDiscoveryOrchestrator MISSING** - 3-tier pattern system not implemented
6. **ExternalResearchOrchestrator MISSING** - Secure external lookups not available

---

## 🏗️ ARCHITECTURE SUMMARY

### 3-Tier Pattern Discovery System

```
TIER 1: KNOWN (99% confidence)
  - Hardcoded patterns (Repository, Factory, etc.)
  - Vendors (LaunchDarkly, Stripe, Auth0)
  - File: cortex/knowledge/patterns/known_patterns.yaml

TIER 2: LEARNED (70-95% confidence)
  - Company-specific patterns
  - Promoted from Tier 3 after manual review
  - File: company/domains/learned-patterns.yaml

TIER 3: CANDIDATE (<70% confidence)
  - First-time detections
  - Requires human review
  - File: company/domains/candidate-patterns.yaml
```

### Vendor Detection

- **Sources:** SDK imports, config files, environment variables
- **Supported:** LaunchDarkly, Stripe, Auth0, Twilio, SendGrid, DataDog, New Relic
- **Output:** company/domains/{repo}/vendors.yaml

### Database Crawling

- **Plugins:** SQL Server (P0), PostgreSQL (P0), Oracle (P1), MySQL (P2), MongoDB (P2)
- **Fallback:** Schema inference from ORM models (60-75% confidence)
- **Security:** Read-only connections, user consent required
- **Output:** company/domains/{repo}/database-schema.yaml

### External Research (Secure)

- **Allowlist:** PyPI, NPM, NuGet, GitHub only
- **Enforcement:** SSL pinning, 5s timeout, 10 req/min rate limit
- **Cache:** 7-day TTL, content-hash verification
- **Security:** No repo code sent to external APIs

### Snowball Effect

- **Load:** Existing company/domains/{repo}/*.yaml
- **Analyze:** Run all LENS analyzers
- **Merge:** Increment existing with new (confidence-based winner)
- **Persist:** Save enhanced YAMLs
- **Report:** Delta (what changed)

---

## 📋 IMPLEMENTATION SCHEDULE

### Week 1: Foundation (P0-A)
- [ ] Implement `_update_company_domains()` (8 tests)
- [ ] Create DomainKnowledgeMerger (15 tests)
- [ ] Create VendorDetector (20 tests)
- [ ] Create vendors.yaml schema
- [ ] Integrate into LENSOrchestrator

**Deliverable:** Snowball effect working, vendor detection operational

### Week 2: Database Intelligence (P0-B)
- [ ] Create DatabaseCrawlerPlugin interface (8 tests)
- [ ] Implement SQLServerCrawlerPlugin (18 tests)
- [ ] Implement PostgreSQLCrawlerPlugin (16 tests)
- [ ] Create SchemaInferenceEngine (12 tests)
- [ ] Create database-schema.yaml schema

**Deliverable:** Database schema extraction for SQL Server + PostgreSQL

### Week 3: Pattern Discovery + External Research (P1)
- [ ] Create PatternDiscoveryOrchestrator (25 tests)
- [ ] Create known_patterns.yaml (100+ patterns)
- [ ] Create ExternalResearchOrchestrator (15 tests)
- [ ] Implement allowlist enforcement + caching (12 tests)
- [ ] Create LaunchDarklyAnalyzer (10 tests)

**Deliverable:** 3-Tier pattern discovery + external research operational

### Week 4: MCP Exposure + Integration (P1)
- [ ] Expose 5 new MCP tools (20 tests)
- [ ] Update cortex-architect.prompt.md audit checks
- [ ] Update wiring.yaml
- [ ] Integration testing (8 tests)
- [ ] Documentation (4 docs)

**Deliverable:** Full LENS unified intelligence operational + documented

---

## 🔧 NEW MCP TOOLS

1. **`cortex_lens_discover_patterns`** - Scan for unknown patterns
2. **`cortex_lens_research_vendor`** - Look up vendor metadata
3. **`cortex_lens_promote_pattern`** - Promote Tier 3 → Tier 2
4. **`cortex_lens_get_learned_patterns`** - Retrieve company patterns
5. **`cortex_lens_dismiss_candidate`** - Mark as false positive

---

## 📁 NEW FILES TO CREATE

### Orchestrators
- `cortex/orchestrators/domain/domain_knowledge_merger.py` (~300 LOC)
- `cortex/orchestrators/support/pattern_discovery_orchestrator.py` (~400 LOC)
- `cortex/orchestrators/support/external_research_orchestrator.py` (~300 LOC)

### Analyzers
- `cortex/lens/analyzers/vendor_detector.py` (~400 LOC)
- `cortex/lens/analyzers/launchdarkly_analyzer.py` (~250 LOC)

### Plugins
- `cortex/lens/plugins/database_crawler_plugin.py` (~150 LOC, interface)
- `cortex/lens/plugins/database/sqlserver_crawler.py` (~500 LOC)
- `cortex/lens/plugins/database/postgresql_crawler.py` (~450 LOC)

### Engines
- `cortex/lens/engines/schema_inference_engine.py` (~300 LOC)

### Infrastructure
- `cortex/infrastructure/external_api_client.py` (~200 LOC)

### YAML Templates
- `company/domains/TEMPLATE-vendors.yaml`
- `company/domains/TEMPLATE-database-schema.yaml`
- `company/domains/TEMPLATE-learned-patterns.yaml`
- `cortex/knowledge/patterns/known_patterns.yaml`

### Tests
- 160+ unit tests
- 8 integration tests

---

## ✅ SUCCESS CRITERIA

- [ ] LENS unified scan executes all analyzers in single call
- [ ] Snowball effect operational (2nd scan enhances 1st scan data)
- [ ] Vendor detection works for LaunchDarkly, Stripe, Auth0
- [ ] Database crawling works for SQL Server + PostgreSQL
- [ ] 3-Tier pattern discovery operational
- [ ] External research secured via allowlist
- [ ] All 160+ unit tests passing
- [ ] All 8 integration tests passing
- [ ] MCP tools exposed and functional
- [ ] Documentation complete (4 docs)

---

## 🛡️ SECURITY ENFORCEMENT

- ✅ Allowlist-only domains (no arbitrary URLs)
- ✅ SSL certificate pinning
- ✅ Rate limiting (10 req/min per domain)
- ✅ Circuit breaker (3 failures → 10-min cooldown)
- ✅ Content-hash verification for cache
- ✅ NO repo code sent to external APIs
- ✅ Read-only database connections only
- ✅ User consent gates for DB queries
- ✅ Secrets redacted in all outputs

---

## 📊 TEST COUNTS

| Component | Unit Tests | File |
|-----------|-----------|------|
| DomainKnowledgeMerger | 15 | test_domain_knowledge_merger.py |
| VendorDetector | 20 | test_vendor_detector.py |
| DatabaseCrawlerPlugin | 46 | test_*_crawler.py (4 files) |
| PatternDiscoveryOrchestrator | 25 | test_pattern_discovery.py |
| ExternalResearchOrchestrator | 15 | test_external_research.py |
| External API Client | 12 | test_external_api_client.py |
| LaunchDarklyAnalyzer | 10 | test_launchdarkly_analyzer.py |
| Repository Onboarding | 8 | test_repository_onboarding.py |
| MCP Tools | 20 | test_lens_tools.py |
| **Integration Tests** | **8** | **test_lens_unified_scan.py** |
| **TOTAL** | **171** | |

---

## 🚨 RISKS & MITIGATION

| Risk | Mitigation |
|------|------------|
| Database connection failures | Graceful fallback to ORM schema inference |
| External API rate limits | Circuit breaker + 7-day cache |
| False positives in patterns | 3-Tier system with manual review |
| Encrypted connection strings | Detect type, prompt for alternatives |
| LENS scan too slow | Parallelize analyzers, cache intermediate results |

---

## 📖 DOCUMENTATION TO CREATE

1. `docs/11-mcp-tools/lens-unified-intelligence.md`
2. `docs/08-reference/pattern-discovery.md`
3. `docs/08-reference/vendor-detection.md`
4. `docs/08-reference/database-crawling.md`

---

## 🔗 RELATED PHASES

- **Phase 15:** Static Repository Visualization (provides dashboard foundation)
- **Phase 18:** Enterprise Dashboard System (will display LENS unified output)
- **Phase 10:** LENS Remote Intelligence (remote git analysis baseline)

---

## 🎯 NEXT STEPS

1. **Read:** [PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml](./PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml) for full specification
2. **Start:** Week 1 (DomainKnowledgeMerger + VendorDetector)
3. **Test-First:** Write tests BEFORE implementation (TDD compliance)
4. **Iterate:** Weekly deliverables with continuous validation

---

**For Questions:** Reference chat02.txt (source of architectural decisions)  
**For Context:** Review PHASE-15 and PHASE-18 YAMLs for dashboard integration
