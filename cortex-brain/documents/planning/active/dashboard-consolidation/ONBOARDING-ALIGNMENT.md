# Dashboard & Onboarding Alignment Plan
**Version:** 1.0  
**Date:** December 6, 2025  
**Author:** Asif Hussain  
**Status:** 🚀 Implementation Complete + Strategic Roadmap

---

## 🎯 Executive Summary

This plan defines the cohesive architecture for CORTEX's admin dashboard and application onboarding systems, establishing a unified data collection, storage, and visualization framework that scales across multiple repositories.

**Completed:** All core infrastructure reorganization and data collection  
**Next Phase:** Enhanced integrations and advanced features

---

## 📊 Current State (Completed)

### ✅ Infrastructure Reorganization

**New Folder Structure:**
```
cortex-brain/dashboards/
├── data/                           # NEW: Centralized data hub
│   ├── repos/                      # Repository-specific data
│   │   ├── v5-webservices-prevalidationws/
│   │   ├── tcbulk/
│   │   ├── v5-coldfusion/
│   │   ├── cortex/
│   │   ├── noor-canvas/
│   │   ├── kashkole/
│   │   ├── ksessions/
│   │   └── alist/
│   ├── mock/                       # Mock data for testing
│   ├── schema/                     # JSON schemas & validators
│   └── templates/                  # Data templates
├── ui/                             # Dashboard UI components
│   ├── index.html                  # Main dashboard
│   ├── data-loader.js              # Updated data loader
│   ├── components/                 # UI components
│   └── styles/                     # Stylesheets
└── README.md                       # Documentation
```

### ✅ Code Updates Completed

1. **Data Loader (`ui/data-loader.js`)**
   - Updated all source paths to use `/data/repos/` and `/data/mock/`
   - Added new repositories: tcbulk, v5-coldfusion

2. **Admin Dashboard Launcher (`src/operations/modules/admin_dashboard_launcher_module.py`)**
   - Updated `_discover_repositories()` to scan `data/repos/` directory
   - Maintains backward compatibility with existing features

3. **Dashboard Collector (`src/orchestrators/dashboard_collector.py`)**
   - Updated output path to `cortex-brain/dashboards/data/repos/{repo-name}/`
   - All new collections automatically use organized structure

4. **Schema Validator (`data/schema/schema-validator.py`)**
   - Updated schema path reference to `data/schema/health-data-schema.json`

5. **Test Suite**
   - Updated 7 test files to reference new `data/repos/` paths
   - All tests now use consistent path structure

### ✅ Data Collection Completed

**Repositories Analyzed:**
- ✅ v5-webservices-prevalidationws (existing data migrated)
- ✅ TCBULK (newly collected - 1.3 seconds)
- ✅ V5.ColdFusion (newly collected - 6.3 seconds)

**Data Files per Repository:**
- `health-data.json` - Overall health metrics
- `tech-stack.json` - Technology stack analysis
- `security.json` - Security analysis
- `architecture.json` - Architecture patterns
- `code-organization.json` - Code structure metrics
- `team-metrics.json` - Team activity data
- `vendors.json` - Dependencies and packages
- `metadata.json` - Collection metadata

---

## 🏗️ Architecture Design

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Repository Analysis                        │
│  (TCBULK, V5.ColdFusion, PreValidationWS, etc.)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Dashboard Data Collector (Orchestrator)             │
│  • Tech Stack Analyzer                                       │
│  • Architecture Scanner                                      │
│  • Security Analyzer                                         │
│  • Code Organization Metrics                                 │
│  • Team Activity Tracker                                     │
│  • Vendor Dependency Scanner                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│     cortex-brain/dashboards/data/repos/{repo-name}/         │
│  • Structured JSON data files                               │
│  • Validated against schemas                                │
│  • Versioned metadata                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Dashboard UI (index.html)                       │
│  • Repository dropdown selector                             │
│  • Real-time data loading                                   │
│  • Interactive visualizations                               │
│  • Multi-tab interface (Executive, Tech, Security, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### Component Integration Map

```
Application Onboarding
        │
        ├─→ Dashboard Collector ──→ data/repos/{repo-name}/
        │                                  │
        ├─→ Crawlers ──────────────→ discovery-reports/
        │                                  │
        └─→ Documentation Gen ─────→ documents/
                                          │
                                          ▼
                              Admin Dashboard Launcher
                                          │
                                          ▼
                              Dashboard UI (Browser)
```

---

## 🔄 Integration Points

### 1. Application Onboarding → Dashboard Data

**Current State:** Separate workflows  
**Future Enhancement:** Auto-trigger data collection during onboarding

```python
# Proposed integration in application_onboarding_steps.py
class GenerateDashboardDataStep(OnboardingStep):
    """Generate dashboard data as part of onboarding"""
    
    def execute(self, context: Dict[str, Any]) -> StepResult:
        project_root = context.get('project_root')
        
        # Run dashboard collector
        collector = DashboardDataCollector(project_root)
        results = collector.collect_all()
        collector.save_results(results)
        
        return StepResult(
            success=True,
            data={"dashboard_url": f"...?source={repo_slug}"}
        )
```

### 2. Dashboard UI ↔ Backend Services

**Current:** Static JSON file loading  
**Future:** Real-time data streaming

- WebSocket support for live updates
- Server-side data aggregation
- Multi-repo comparison views

### 3. Data Schema Evolution

**Current:** Fixed JSON structure  
**Future:** Versioned schemas with migration support

```yaml
# Schema versioning strategy
data_version: "2.0"
backward_compatible: true
migration_path: "1.0 -> 2.0"
breaking_changes: []
```

---

## 🎯 Phase 2: Enhanced Integration (Future)

### Priority 1: Auto-Collection During Onboarding

**Goal:** Automatically generate dashboard data when onboarding new applications

**Implementation:**
1. Add `GenerateDashboardDataStep` to onboarding workflow
2. Integrate with EPM step registry
3. Display dashboard link in onboarding completion message

**Estimated Effort:** 2-3 hours  
**Dependencies:** None  
**Impact:** High - streamlines onboarding experience

### Priority 2: Real-Time Data Refresh

**Goal:** Enable dashboard to refresh data without manual collection

**Implementation:**
1. Add file system watchers for data changes
2. Implement WebSocket server for push updates
3. Add "Refresh" button to UI with progress indicator

**Estimated Effort:** 4-6 hours  
**Dependencies:** WebSocket infrastructure  
**Impact:** Medium - improves user experience

### Priority 3: Multi-Repository Comparison

**Goal:** Compare metrics across multiple repositories in single view

**Implementation:**
1. Create comparison data aggregator
2. Build comparison UI components
3. Add filtering and grouping capabilities

**Estimated Effort:** 6-8 hours  
**Dependencies:** Aggregation service  
**Impact:** High - enables cross-project insights

### Priority 4: Advanced Analytics

**Goal:** Historical trending and predictive analytics

**Implementation:**
1. Store historical snapshots (time-series data)
2. Build trending visualizations
3. Implement anomaly detection

**Estimated Effort:** 8-12 hours  
**Dependencies:** Time-series storage  
**Impact:** High - provides strategic insights

---

## 📁 Folder Structure Optimization

### Current Strengths

✅ **Separation of Concerns**
- Data separated from UI
- Schema validation isolated
- Mock data for testing

✅ **Scalability**
- Easy to add new repositories
- Template-based data structure
- Version-controlled schemas

✅ **Maintainability**
- Clear organization
- Discoverable paths
- Consistent naming

### Recommended Enhancements

#### 1. Add Archive Directory

```
data/
├── repos/          # Active repository data
├── archives/       # Historical snapshots
│   └── {repo-name}/
│       └── {timestamp}/
├── mock/
├── schema/
└── templates/
```

**Purpose:** Preserve historical data for trending analysis

#### 2. Add Cache Layer

```
data/
├── repos/
├── cache/          # Computed aggregations
│   ├── summary.json        # All repos summary
│   ├── comparisons.json    # Cross-repo comparisons
│   └── trends.json         # Time-series trends
├── mock/
├── schema/
└── templates/
```

**Purpose:** Improve dashboard load performance

#### 3. Add Exports Directory

```
dashboards/
├── data/
├── ui/
├── exports/        # Generated reports
│   ├── pdf/
│   ├── csv/
│   └── html/
└── README.md
```

**Purpose:** Support report generation and sharing

---

## 🔐 Security & Access Control

### Current State
- Admin-only features protected by `_is_admin_repo()` checks
- Data access via file system (no authentication)
- UI served from local HTTP server

### Future Enhancements

1. **Role-Based Access Control (RBAC)**
   - Admin: Full access to all repositories
   - Developer: Access to assigned repositories only
   - Viewer: Read-only access

2. **Data Encryption**
   - Encrypt sensitive security data at rest
   - Secure data transmission via HTTPS

3. **Audit Logging**
   - Track dashboard access
   - Log data collection activities
   - Monitor data exports

---

## 🧪 Testing Strategy

### Current Coverage
- ✅ 7 test files updated for new paths
- ✅ Unit tests for data collectors
- ✅ Integration tests for dashboard components

### Recommended Additions

1. **End-to-End Tests**
   - Full onboarding → dashboard workflow
   - Multi-repository scenarios
   - UI interaction tests

2. **Performance Tests**
   - Large repository handling
   - Concurrent data collection
   - UI responsiveness with big datasets

3. **Schema Validation Tests**
   - Test all data files against schemas
   - Version migration testing
   - Backward compatibility verification

---

## 📈 Metrics & Success Criteria

### Phase 1 (Completed) ✅
- [x] Organized folder structure created
- [x] All code updated to use new paths
- [x] Data collected for 3 target repositories
- [x] Test suite updated and passing
- [x] Zero breaking changes to existing functionality

### Phase 2 (Future)
- [ ] Auto-collection during onboarding: 95% success rate
- [ ] Dashboard load time: < 2 seconds for any repository
- [ ] Data freshness: < 5 minutes for real-time updates
- [ ] User satisfaction: 4.5+/5.0 rating
- [ ] Code coverage: > 85% for dashboard components

---

## 🛠️ Implementation Checklist

### Completed ✅
- [x] Create `cortex-brain/dashboards/data/` structure
- [x] Move existing data to `data/repos/`
- [x] Update `data-loader.js` paths
- [x] Update admin dashboard launcher
- [x] Update dashboard collector
- [x] Update schema validator paths
- [x] Update test suite (7 files)
- [x] Collect data for TCBULK
- [x] Collect data for V5.ColdFusion
- [x] Verify all data integrity
- [x] Create collection script with progress feedback
- [x] Create comprehensive alignment plan

### Phase 2 (Prioritized)
- [ ] Add `GenerateDashboardDataStep` to onboarding
- [ ] Implement real-time refresh mechanism
- [ ] Build multi-repository comparison view
- [ ] Add historical archiving
- [ ] Create cache layer for aggregations
- [ ] Implement export functionality
- [ ] Add RBAC framework
- [ ] Create end-to-end tests
- [ ] Build performance monitoring
- [ ] Document all APIs and integrations

---

## 📚 Documentation

### Updated Files
1. `ui/data-loader.js` - Data source paths
2. `src/operations/modules/admin_dashboard_launcher_module.py` - Repository discovery
3. `src/orchestrators/dashboard_collector.py` - Output directory
4. `data/schema/schema-validator.py` - Schema path
5. 7 test files - Path references
6. `scripts/collect_dashboard_data_with_progress.py` - NEW collection script

### New Documentation Needed
- [ ] Admin dashboard user guide
- [ ] Data collection API documentation
- [ ] Schema evolution guide
- [ ] Integration developer guide
- [ ] Troubleshooting guide

---

## 🚀 Quick Start Commands

### Collect Dashboard Data
```bash
# Single repository
python -m src.orchestrators.dashboard_collector --path "C:\PROJECTS\MyRepo"

# Multiple repositories with progress
python scripts\collect_dashboard_data_with_progress.py
```

### Launch Dashboard
```bash
# Admin dashboard (multi-repo selector)
python -m src.orchestrators.admin_dashboard_launcher

# Standard dashboard (specific repo)
python -m src.orchestrators.dashboard_launcher --source "tcbulk"
```

### Run Tests
```bash
# Dashboard component tests
pytest tests/dashboard/ -v

# Data collector tests
pytest tests/unit/test_data_collectors_* -v
```

---

## 🎓 Lessons Learned

### What Worked Well
1. **Progressive Enhancement:** Made changes incrementally with validation
2. **Clear Separation:** Data vs UI vs logic separation improved maintainability
3. **Progress Feedback:** User-facing progress updates prevented confusion
4. **Backward Compatibility:** No breaking changes during reorganization

### Challenges Overcome
1. **Path Updates:** Multiple files needed coordination - used multi_replace tool
2. **Test Coverage:** Ensuring all tests updated - used grep search to find all
3. **Data Migration:** Moving existing data without loss - careful validation

### Best Practices Established
1. Always use centralized data directory (`data/repos/`)
2. Include metadata in all collected data
3. Validate data against schemas before saving
4. Provide progress feedback for long-running operations
5. Keep UI and data layers decoupled

---

## 📞 Support & Contacts

**Questions about this plan:** Reference this document in chat  
**Implementation issues:** Check test suite first, then review logs  
**New repository onboarding:** Use `collect_dashboard_data_with_progress.py`

---

**Document Version:** 1.0  
**Last Updated:** December 6, 2025  
**Next Review:** Upon Phase 2 implementation start  
**Maintained By:** CORTEX Development Team
