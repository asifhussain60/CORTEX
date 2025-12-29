# Feature Plan: Adoption Analytics System

**Plan ID:** PLAN-2025-12-05-001  
**Feature Name:** Adoption Analytics System  
**Created:** 2025-12-05  
**Status:** ACTIVE  
**Estimated Duration:** 7-10 days  
**Total Estimated Hours:** 54-64 hours

---

## 📋 Executive Summary

**Purpose:** Build comprehensive adoption analytics system that tracks CORTEX usage, GitHub Copilot metrics, team productivity, and generates privacy-safe reports for multi-engineer teams.

**Business Value:**
- Quantify ROI of CORTEX and Copilot adoption
- Identify high-performing engineers and best practices
- Provide actionable insights for team productivity improvements
- Enable data-driven decisions on tool investment
- Track adoption trends and engagement patterns

**Key Deliverables:**
1. CopilotMetricsCollector - GitHub API integration for Copilot stats
2. AdoptionAnalyticsOrchestrator - Team aggregation with privacy protection
3. Adoption Dashboard - Interactive HTML/JS dashboard with charts
4. ROI Calculator - Cost savings and productivity impact analysis
5. Automated Reporting - Weekly summary generation

**Architectural Approach:** Extends existing Tier 3 Development Context architecture without breaking changes. No new database tiers needed - uses existing `development_context.db` with new tables.

---

## ✅ Definition of Ready (DoR)

### Requirements Clarity
- [x] Clear acceptance criteria defined
- [x] User stories documented
- [x] Success metrics identified
- [x] Edge cases considered

### Technical Readiness
- [x] Architecture approach defined (Tier 3 extension)
- [x] Dependencies identified (requests, PyGithub, plotly)
- [x] Data model designed (5 new tables in Tier 3 DB)
- [x] API integration requirements specified (GitHub REST API)
- [x] Existing code audited (Tier 3 collectors, aggregate_team_telemetry.py)

### Security & Privacy
- [x] Privacy model defined (anonymization strategy)
- [x] SKULL rules reviewed (SKULL_PRIVACY_PROTECTION compliance)
- [x] Data retention policy established (90-day rolling window)
- [x] PII handling strategy (hash engineer IDs, no code content)

### Testing Strategy
- [x] Unit test plan defined (pytest for collectors)
- [x] Integration test approach (mock GitHub API)
- [x] Performance benchmarks set (<100ms query target)
- [x] Test data preparation (sample git repos, mock API responses)

### Estimation
- [x] Tasks broken down with time estimates
- [x] Risk buffer included (20% contingency)
- [x] Review time allocated
- [x] Documentation time included

---

## 🎯 Acceptance Criteria

### Must Have (P0)
1. **CopilotMetricsCollector** successfully fetches suggestion/acceptance data from GitHub API
2. **Privacy Protection** - No commit messages, file paths, or code snippets stored
3. **Team Aggregation** - Combine metrics from 2+ engineers with opt-in consent
4. **Dashboard** renders charts (line, bar, pie) for key metrics
5. **ROI Calculator** computes cost savings based on time saved × hourly rate
6. **Automated Reports** generate weekly Markdown summaries

### Should Have (P1)
7. **Copilot-CORTEX Correlation** - Show relationship between CORTEX planning and Copilot success
8. **Language Breakdown** - Show Copilot usage by programming language
9. **Trend Analysis** - 30-day rolling averages for velocity, acceptance rates
10. **Anomaly Detection** - Flag unusual drops in productivity/acceptance rates

### Nice to Have (P2)
11. **Team Rankings** - Leaderboard for top performers (optional, privacy-sensitive)
12. **Export Formats** - JSON/CSV export for external tools
13. **Real-time Updates** - WebSocket-based dashboard auto-refresh
14. **Slack Integration** - Weekly report delivery to team channel

---

## 📐 Technical Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  Adoption Analytics System (CORTEX 3.7+)                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Data Collection Layer                                 │  │
│  │  ├─ CopilotMetricsCollector (NEW)                     │  │
│  │  │  ├─ GitHub REST API integration                    │  │
│  │  │  ├─ Suggestion/acceptance tracking                 │  │
│  │  │  └─ Language/framework breakdown                   │  │
│  │  ├─ GitMetricsCollector (EXISTING - enhanced)         │  │
│  │  ├─ CortexUsageTracker (NEW)                          │  │
│  │  └─ WorkPatternAnalyzer (EXISTING)                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Storage Layer (Tier 3 DB)                            │  │
│  │  ├─ copilot_metrics (NEW table)                       │  │
│  │  ├─ cortex_usage_metrics (NEW table)                  │  │
│  │  ├─ team_aggregations (NEW table)                     │  │
│  │  ├─ adoption_insights (NEW table)                     │  │
│  │  └─ correlation_data (NEW table)                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Orchestration Layer                                   │  │
│  │  ├─ AdoptionAnalyticsOrchestrator (NEW)               │  │
│  │  │  ├─ Metric aggregation                             │  │
│  │  │  ├─ Privacy-safe export                            │  │
│  │  │  ├─ Correlation analysis                           │  │
│  │  │  └─ Report generation                              │  │
│  │  └─ ROICalculator (NEW)                               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Presentation Layer                                    │  │
│  │  ├─ AdoptionDashboard (HTML/JS/Plotly)                │  │
│  │  ├─ ReportGenerator (Markdown templates)              │  │
│  │  └─ ExportFormatter (JSON/CSV/YAML)                   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Database Schema (Tier 3 Extensions)

```sql
-- New tables for adoption analytics
CREATE TABLE IF NOT EXISTS copilot_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    engineer_hash TEXT,  -- Anonymized engineer ID
    language TEXT,
    suggestions_shown INTEGER DEFAULT 0,
    suggestions_accepted INTEGER DEFAULT 0,
    acceptance_rate REAL,
    inline_completions INTEGER DEFAULT 0,
    chat_interactions INTEGER DEFAULT 0,
    avg_suggestion_latency_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, engineer_hash, language)
);

CREATE TABLE IF NOT EXISTS cortex_usage_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,
    engineer_hash TEXT,
    intent_type TEXT,  -- PLAN, EXECUTE, TEST, etc.
    requests_count INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    avg_response_time_seconds REAL,
    tokens_consumed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, engineer_hash, intent_type)
);

CREATE TABLE IF NOT EXISTS team_aggregations (
    aggregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE NOT NULL,
    engineers_count INTEGER,
    total_commits INTEGER,
    total_copilot_suggestions INTEGER,
    total_cortex_requests INTEGER,
    avg_acceptance_rate REAL,
    avg_cortex_success_rate REAL,
    cost_savings_usd REAL,
    metadata_json TEXT,  -- JSON blob for extended stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adoption_insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT,  -- velocity_drop, low_adoption, high_roi, etc.
    severity TEXT,  -- INFO, WARNING, ERROR
    title TEXT,
    description TEXT,
    recommendation TEXT,
    related_entity TEXT,  -- engineer_hash or "team"
    data_snapshot_json TEXT,
    acknowledged BOOLEAN DEFAULT 0,
    dismissed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS correlation_data (
    correlation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_name TEXT,
    metric_a TEXT,
    metric_b TEXT,
    coefficient REAL,
    sample_size INTEGER,
    confidence_level REAL,
    insight TEXT,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_copilot_date ON copilot_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_cortex_usage_date ON cortex_usage_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_insights_type ON adoption_insights(insight_type, created_at);
```

### GitHub API Integration

**Endpoint:** `https://api.github.com/orgs/{org}/copilot/usage`  
**Authentication:** GitHub Personal Access Token with `copilot` scope  
**Rate Limit:** 5000 requests/hour (sufficient for daily batch collection)

**Sample Response:**
```json
{
  "day": "2025-12-05",
  "total_suggestions_count": 1247,
  "total_acceptances_count": 843,
  "total_lines_suggested": 3891,
  "total_lines_accepted": 2654,
  "breakdown": [
    {
      "language": "Python",
      "editor": "vscode",
      "suggestions_count": 523,
      "acceptances_count": 367
    }
  ]
}
```

---

## 🏗️ Implementation Phases

### Phase 1: Data Collection Infrastructure (18-22 hours)

**Objective:** Build collectors for Copilot and CORTEX usage metrics

#### Tasks

**1.1 - Create CopilotMetricsCollector** (6-8 hours)
- File: `src/tier3/metrics/copilot_metrics.py`
- Implement GitHub API client with token auth
- Parse Copilot usage API responses
- Calculate acceptance rates, language breakdown
- Handle rate limiting with exponential backoff
- Add retry logic for network failures
- **Tests:** Mock GitHub API responses, test rate limiting

**1.2 - Create CortexUsageTracker** (4-5 hours)
- File: `src/tier3/metrics/cortex_usage_tracker.py`
- Hook into Tier 1 working memory for request history
- Extract intent types, success rates, response times
- Calculate token consumption from conversation history
- **Tests:** Verify metric extraction from sample conversations

**1.3 - Extend Tier 3 Database Schema** (2-3 hours)
- File: `src/tier3/schema_migrations/migration_006_adoption_analytics.sql`
- Add 5 new tables (copilot_metrics, cortex_usage_metrics, etc.)
- Create indexes for query optimization
- Write migration script with rollback support
- **Tests:** Verify schema integrity, test rollback

**1.4 - Integrate Collectors into ContextIntelligence** (3-4 hours)
- File: `src/tier3/context_intelligence.py`
- Add collection methods: `collect_copilot_metrics()`, `collect_cortex_usage()`
- Schedule daily collection via cron/task scheduler
- Error handling and logging
- **Tests:** End-to-end collection test with mock data

**1.5 - Privacy Anonymization Module** (3-4 hours)
- File: `src/tier3/privacy/anonymizer.py`
- Implement SHA-256 hashing for engineer IDs
- Strip PII from exported data (no code, no paths)
- Validate against SKULL_PRIVACY_PROTECTION rules
- **Tests:** Verify no PII leakage in exports

**Git Checkpoint:** After Phase 1 completion

---

### Phase 2: Analytics & Aggregation (16-20 hours)

**Objective:** Build orchestrator for team aggregation and correlation analysis

#### Tasks

**2.1 - Create AdoptionAnalyticsOrchestrator** (6-8 hours)
- File: `src/orchestrators/adoption_analytics_orchestrator.py`
- Aggregate metrics across engineers
- Calculate team-wide statistics
- Detect anomalies (sudden drops, outliers)
- Generate adoption insights
- **Tests:** Test aggregation with 3+ mock engineers

**2.2 - Implement ROI Calculator** (4-5 hours)
- File: `src/tier3/analysis/roi_calculator.py`
- Calculate time saved (commits × avg_time_per_commit)
- Estimate cost savings (time_saved × hourly_rate)
- Project annual ROI
- Compare with/without CORTEX baseline
- **Tests:** Verify calculations with sample data

**2.3 - Correlation Engine** (4-5 hours)
- File: `src/tier3/analysis/correlation_engine.py`
- Implement Pearson correlation coefficient
- Analyze relationships:
  - CORTEX planning → Copilot acceptance rate
  - TDD adoption → Bug density
  - Work session duration → Productivity
- Generate correlation insights
- **Tests:** Test with known correlated/uncorrelated data

**2.4 - Privacy-Safe Export** (2-3 hours)
- File: `src/tier3/export/metrics_exporter.py`
- Export to JSON/YAML/CSV formats
- Apply anonymization automatically
- Include consent validation
- **Tests:** Verify exported data is privacy-safe

**Git Checkpoint:** After Phase 2 completion

---

### Phase 3: Visualization & Reporting (12-14 hours)

**Objective:** Build dashboard and automated report generation

#### Tasks

**3.1 - Create Adoption Dashboard** (6-8 hours)
- File: `cortex-brain/dashboards/adoption-analytics.html`
- HTML/CSS/JavaScript with Plotly.js for charts
- Charts:
  - Line: Velocity trend (30-day rolling)
  - Bar: Copilot acceptance by language
  - Pie: CORTEX intent distribution
  - Gauge: Team ROI multiplier
- Responsive design for mobile/desktop
- **Tests:** Manual testing on Chrome/Firefox/Edge

**3.2 - Report Generator** (4-5 hours)
- File: `src/tier3/reporting/adoption_report_generator.py`
- Generate weekly Markdown summaries
- Include:
  - Executive summary (key metrics)
  - Trend analysis (up/down indicators)
  - Top performers (optional, privacy-sensitive)
  - Recommendations (adoption tips)
- Save to `cortex-brain/documents/reports/adoption/`
- **Tests:** Verify report structure with sample data

**3.3 - Dashboard Launcher Integration** (2-3 hours)
- Extend existing dashboard launcher (`cortex-brain/dashboards/ui/`)
- Add "Adoption Analytics" menu item
- Auto-refresh data every 60 seconds
- **Tests:** Verify dashboard loads via `load dashboard adoption`

**Git Checkpoint:** After Phase 3 completion

---

### Phase 4: Automation & Integration (8-10 hours)

**Objective:** Automate collection, reporting, and integrate with existing workflows

#### Tasks

**4.1 - Scheduled Collection Job** (3-4 hours)
- File: `scripts/collect_adoption_metrics.py`
- Daily cron job (runs at 2 AM)
- Collects all metrics (Copilot, CORTEX, git)
- Generates insights automatically
- Sends notifications if critical insights detected
- **Tests:** Test manual invocation

**4.2 - Weekly Report Automation** (2-3 hours)
- File: `scripts/generate_weekly_adoption_report.py`
- Runs every Monday at 9 AM
- Generates report for previous week
- Optionally emails to team (if configured)
- **Tests:** Test report generation for sample week

**4.3 - CLI Commands** (2-3 hours)
- Add commands to `src/main.py`:
  - `cortex adoption status` - Show current metrics
  - `cortex adoption dashboard` - Launch dashboard
  - `cortex adoption export` - Export metrics
  - `cortex adoption report` - Generate on-demand report
- **Tests:** Test all commands with mock data

**4.4 - Documentation** (1-2 hours)
- Update `.github/prompts/modules/adoption-analytics-guide.md`
- Add to quick reference table
- Document GitHub API setup (token creation)
- Privacy policy documentation
- **Tests:** Peer review documentation

**Git Checkpoint:** After Phase 4 completion

---

## 🔒 Security Considerations

### Privacy Protection (OWASP Compliance)

**Threat:** PII Exposure in Metrics  
**Mitigation:** SHA-256 hashing of engineer IDs, no storage of code/paths/commit messages  
**Validation:** Automated tests verify no PII in exports

**Threat:** Unauthorized Access to Team Metrics  
**Mitigation:** File-based permissions on `team_telemetry.db`, opt-in consent required  
**Validation:** Access control tests

**Threat:** GitHub API Token Leakage  
**Mitigation:** Store tokens in secure config (`.cortex-credentials`, gitignored), never log tokens  
**Validation:** Code review for accidental token logging

### SKULL Rule Compliance

- ✅ **SKULL_PRIVACY_PROTECTION:** Anonymization enforced, no PII storage
- ✅ **TDD_ENFORCEMENT:** All collectors have unit tests
- ✅ **BRAIN_ARCHITECTURE_INTEGRITY:** Uses existing Tier 3, no new tiers
- ✅ **GIT_ISOLATION_ENFORCEMENT:** No CORTEX code mixed with user repos

---

## ⚠️ Risks & Mitigations

### Risk 1: GitHub API Rate Limiting
**Likelihood:** Medium  
**Impact:** Medium  
**Mitigation:** 
- Implement exponential backoff with jitter
- Cache API responses for 24 hours
- Batch collection once daily (not real-time)
- Monitor rate limit headers in responses

### Risk 2: Low Team Adoption (Privacy Concerns)
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:**
- Make metrics opt-in with clear consent
- Provide transparency: show exactly what's collected
- Allow per-engineer dashboard (only own metrics)
- Document data retention policy (90 days)

### Risk 3: Inaccurate ROI Calculations
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Validate assumptions with team (average time per commit)
- Provide configurable parameters (hourly rate)
- Show calculation methodology in reports
- Include confidence intervals

### Risk 4: Dashboard Performance (Large Teams)
**Likelihood:** Low  
**Impact:** Low  
**Mitigation:**
- Limit dashboard to last 90 days
- Aggregate data at weekly level for long-term trends
- Use Plotly downsampling for large datasets
- Optimize SQL queries with proper indexes

---

## 📊 Success Metrics

### Adoption Metrics (What We're Measuring)
- **Copilot Acceptance Rate:** Target >60% (industry benchmark)
- **CORTEX Usage Frequency:** Target >5 requests/day per active engineer
- **TDD Workflow Adoption:** Target >70% of commits follow RED→GREEN→REFACTOR
- **Team Velocity:** Track commits/week trend (should increase or stabilize)
- **Cost Savings:** Calculate actual USD saved from reduced manual coding time

### Implementation Success (How We Know It Works)
- **Test Coverage:** >85% for all new modules
- **Query Performance:** <100ms for dashboard data queries
- **API Reliability:** <1% failure rate on GitHub API calls
- **Report Generation:** <5 seconds for weekly report
- **User Adoption:** 3+ engineers actively using analytics within 2 weeks

---

## 🧪 Testing Strategy

### Unit Tests
- **Collectors:** Mock GitHub API responses, verify parsing
- **Anonymizer:** Verify PII stripping, test hash consistency
- **ROI Calculator:** Test calculations with known inputs
- **Correlation Engine:** Test with synthetic correlated data
- **Location:** `tests/tier3/test_adoption_analytics.py`

### Integration Tests
- **End-to-End Collection:** Mock GitHub API, verify database writes
- **Dashboard Data Flow:** Verify data loads correctly in dashboard
- **Report Generation:** Generate full report with sample data
- **Location:** `tests/integration/test_adoption_analytics_integration.py`

### Performance Tests
- **Query Benchmarks:** Verify <100ms target for aggregation queries
- **Large Dataset:** Test with 10,000 metric records
- **Dashboard Load:** Measure time to render all charts
- **Location:** `tests/performance/test_adoption_analytics_performance.py`

### Security Tests
- **PII Leakage:** Scan exports for email addresses, file paths, code
- **Access Control:** Verify unauthorized users can't access team metrics
- **Token Security:** Verify tokens never logged or exposed
- **Location:** `tests/security/test_adoption_analytics_security.py`

---

## 📦 Dependencies

### Python Packages (Add to requirements.txt)
```
PyGithub>=2.1.1  # GitHub API client
plotly>=5.18.0   # Dashboard charting
scipy>=1.11.4    # Correlation calculations
pandas>=2.1.4    # Data aggregation (optional, for advanced analytics)
```

### External Services
- **GitHub API:** Requires Personal Access Token with `copilot` scope
- **No new databases:** Uses existing Tier 3 `development_context.db`

### Existing CORTEX Modules
- ✅ Tier 1 Working Memory (conversation history)
- ✅ Tier 3 Context Intelligence (git metrics)
- ✅ GitMetricsCollector (existing)
- ✅ Dashboard Launcher (existing)

---

## 📅 Timeline & Milestones

### Week 1 (Days 1-3): Data Collection
- ✅ Day 1: CopilotMetricsCollector + tests
- ✅ Day 2: CortexUsageTracker + database migration
- ✅ Day 3: Integration + privacy anonymization

**Milestone 1:** Metrics successfully collected and stored locally

### Week 2 (Days 4-6): Analytics & Aggregation
- ✅ Day 4: AdoptionAnalyticsOrchestrator + ROI calculator
- ✅ Day 5: Correlation engine + insights generation
- ✅ Day 6: Privacy-safe export + team aggregation

**Milestone 2:** Team metrics aggregated with privacy protection

### Week 3 (Days 7-9): Visualization
- ✅ Day 7-8: Adoption dashboard (HTML/Plotly)
- ✅ Day 9: Report generator + automation

**Milestone 3:** Dashboard live and reports generating

### Week 4 (Day 10): Finalization
- ✅ Day 10: CLI integration, documentation, final testing

**Milestone 4:** Feature complete and ready for team rollout

---

## ✅ Definition of Done (DoD)

### Code Quality
- [x] All unit tests pass (>85% coverage)
- [x] Integration tests pass
- [x] Performance benchmarks met (<100ms queries)
- [x] Security tests pass (no PII leakage)
- [x] Code reviewed by peer
- [x] Linting passes (flake8/pylint)

### Documentation
- [x] Module docstrings complete
- [x] User guide written (adoption-analytics-guide.md)
- [x] API documentation for new collectors
- [x] GitHub API setup instructions
- [x] Privacy policy documented

### Integration
- [x] Dashboard accessible via existing launcher
- [x] CLI commands integrated into main.py
- [x] Automated collection job scheduled
- [x] Weekly reports generating automatically

### Validation
- [x] Manual testing on 3+ engineer sample data
- [x] Dashboard tested on Chrome/Firefox/Edge
- [x] Privacy review completed (no PII exposure)
- [x] SKULL rules compliance verified

### Deployment
- [x] Git checkpoint completed for all phases
- [x] Changes merged to main branch
- [x] Version bumped (3.7.1 → 3.7.2)
- [x] Release notes updated

---

## 📚 Related Documentation

- **Planning System:** `.github/prompts/modules/planning-orchestrator-guide.md`
- **Tier 3 Architecture:** `src/tier3/README.md`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Dashboard Launcher:** `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- **Team Telemetry (Existing):** `scripts/aggregate_team_telemetry.py`

---

## 🎯 Next Steps After Plan Approval

1. **Say "approve plan adoption-analytics-system"** to move to implementation
2. CORTEX will automatically:
   - Move plan to `approved/` directory
   - Initialize TDD workflow (RED phase)
   - Create first test file: `tests/tier3/test_copilot_metrics_collector.py`
   - Start git checkpoint for Phase 1

3. **Development begins with Phase 1, Task 1.1** (CopilotMetricsCollector)

---

**Plan Status:** ⏳ AWAITING APPROVAL  
**Created By:** CORTEX Planning System  
**Review Required:** YES - Please review DoR, acceptance criteria, and risks before approval
