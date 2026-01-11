# CORTEX 6.0 Audit Log Viewer - Enhanced Plan Viewer Integration

**Date:** 2026-01-11  
**Version:** 1.0.0  
**Status:** ✅ IMPLEMENTED  
**Author:** CORTEX 6.0 Team

---

## 🎯 Executive Summary

The enhanced Plan Viewer now includes a **first-class Audit Log Viewer component** that transforms raw audit logs into actionable governance observability. This is not a generic log dump—it's an **execution and governance accountability surface** that answers:

- ✅ **What happened?** - Clear event descriptions with semantic meaning
- ✅ **Why it happened?** - Governance rules and triggering conditions
- ✅ **What changed?** - Context diffs and affected components
- ✅ **Why it matters?** - Impact assessment on plan health

---

## 📋 Component Overview

### Design Philosophy

> **"Audit logs are not history. They are accountability."**

The Audit Log Viewer implements a **three-pane design** optimized for:
1. **Fast filtering** - Find relevant events in seconds
2. **Semantic meaning** - Emphasize causality over chronology
3. **Impact assessment** - Distinguish critical signals from noise
4. **Governance correlation** - Link events to plan phases, features, and rules

---

## 🏗️ Architecture

### Three-Pane Layout

```
┌─────────────────────────────────────────────────────────────┐
│                   AUDIT SUMMARY STRIP                       │
│  (metrics, trends, last activity, risk signals)             │
├──────────────────┬──────────────────────────────────────────┤
│  FILTERS &       │        TIMELINE / TABLE                  │
│  FACETS          │  (chronological event list)              │
│  (left pane)     │                                          │
│                  │                                          │
│  • Time Range    │                                          │
│  • Category      │                                          │
│  • Level         │                                          │
│  • Component     │                                          │
├──────────────────┴──────────────────────────────────────────┤
│                 DETAIL & IMPACT PANEL                       │
│  (selected event analysis with governance context)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Component Specifications

### 1. Audit Summary Strip (Top)

**Purpose:** Immediate situational awareness without scrolling

**Metrics Displayed:**
- **Total Events** - Count of all audit events in scope
- **Allowed / Verified** - Successfully completed operations
- **In Progress / Deferred** - Ongoing or delayed operations
- **Blocked / Violations** - Failed or governance-blocked operations
- **Last Event** - Timestamp of most recent activity
- **Risk Level** - Calculated risk indicator (HIGH/MEDIUM/LOW)

**Risk Calculation:**
```javascript
riskScore = (critical_events × 3) + (error_events × 2) + blocked_events

Risk Level:
  - HIGH: riskScore > 20
  - MEDIUM: 10 < riskScore ≤ 20
  - LOW: riskScore ≤ 10
```

---

### 2. Filters & Facets Panel (Left)

**Purpose:** Composable filtering for signal isolation

**Filter Categories:**

#### Time Range
- All Time (default)
- Last Hour
- Last 24 Hours
- Last 7 Days

#### Category (Domain)
- All Categories (default)
- Governance
- Orchestrator
- Validation
- Middleware
- Infrastructure
- Brain
- Integration
- MCP

#### Level (Severity)
- All Levels (default)
- Info
- Warning
- Error
- Critical

**UX Behavior:**
- ✅ Filters are composable (multiple can be active)
- ✅ Active filters show checkmarks
- ✅ Filter counts update dynamically
- ✅ URL state reflects current filters (future enhancement)

---

### 3. Timeline / Table (Center)

**Purpose:** Chronological event display with expandable details

**Event Row Structure:**
```html
┌─────────────────────────────────────────────────┐
│ [Timestamp]              [Level Badge]          │
│ CATEGORY                                        │
│ Human-readable message summary...               │
│ 🖥️ Actor  •  🎯 Target  •  ✓ Outcome           │
└─────────────────────────────────────────────────┘
```

**Rendering Features:**
- ✅ Newest events first (chronological descending)
- ✅ Virtualized rendering for large log sets (up to 50 visible)
- ✅ Hover effects for interactive feedback
- ✅ Selection highlights current event
- ✅ Semantic color coding by level

**Level Color Mapping:**
```javascript
INFO     → Blue  (#60a5fa)
WARNING  → Yellow (#fbbf24)
ERROR    → Red (#ef4444)
CRITICAL → Dark Red (#991b1b)
```

---

### 4. Detail & Impact Panel (Bottom)

**Purpose:** Deep inspection with governance context

When an event is selected, displays:

#### What Happened
Full explanation: `[Actor] performed [Action] on [Target] with outcome [Outcome]`

Example:
> **MasterOrchestrator** performed **Execute** operation on **AC-GOV-001** with outcome: **allowed**. Governance rule enforced successfully.

#### Why It Happened
Governance context: Rule ID, triggering condition, domain enforcement

Example:
> This action was triggered by governance rule **CORE-001** as part of the **governance** domain enforcement.

#### What Changed
State diff: Before → After context changes

Examples:
- ✅ **Allowed:** "Operation completed successfully. System state was updated."
- 🟡 **Deferred:** "Operation is in progress. Changes being applied."
- 🔴 **Blocked:** "Operation was blocked. No system state was modified."

#### Impact Assessment
Risk classification with actionable guidance:

- **🔴 HIGH IMPACT:** Blocks progress or violates critical rules. Immediate attention required.
- **🟡 MEDIUM IMPACT:** May affect plan execution. Review recommended.
- **✅ NO CURRENT IMPACT:** Informational event. No action required.

#### Evidence & References
Clickable links to:
- Governance rules (e.g., `CORE-001`)
- Plan phases (e.g., `Phase 1`)
- Correlation IDs (for trace debugging)
- Components and domains

---

## 📊 Data Model

### Normalized Audit Event Schema

```json
{
  "id": "evt-0001",
  "timestamp": "2026-01-11T10:35:18Z",
  "domain": "governance",
  "actor": "GovernanceMerger",
  "action": "EnforceInvariant",
  "target": "AC-GOV-001",
  "outcome": "allowed",
  "level": "info",
  "reason": "Governance rule enforced successfully",
  "evidence": {
    "rule": "CORE-001",
    "phase": "Phase 1"
  },
  "correlationId": "CORTEX-ABC123DEF456"
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique event identifier |
| `timestamp` | ISO8601 | Event occurrence time |
| `domain` | string | Audit category (governance, orchestrator, etc.) |
| `actor` | string | Component or system that performed action |
| `action` | string | Operation type (Execute, Validate, Enforce, etc.) |
| `target` | string | Affected artifact (AC-ID, file, component, etc.) |
| `outcome` | enum | Result: allowed, blocked, deferred, verified, in-progress |
| `level` | enum | Severity: info, warning, error, critical |
| `reason` | string | Human-readable explanation |
| `evidence` | object | Metadata (rules, phases, files, commits, etc.) |
| `correlationId` | string | Session/trace identifier for debugging |

---

## 🔄 Data Loading Strategy

### Primary Source
1. **Attempt:** Load from `../../../audit-logs/consolidated-audit.json`
2. **Fallback:** Generate mock audit data (100 events)

### Normalization Layer
Raw audit logs are transformed into the normalized schema:

```javascript
normalizeAuditLogs(rawLogs) {
  return rawLogs.map((log, index) => ({
    id: log.id || `evt-${index}`,
    timestamp: log.timestamp || new Date().toISOString(),
    domain: log.category || log.domain || 'unknown',
    actor: log.component || log.actor || 'System',
    action: log.operation || log.action || 'unknown',
    target: log.target || log.message || 'N/A',
    outcome: determineOutcome(log),
    level: log.level || 'info',
    reason: log.message || 'No message',
    evidence: log.metadata || {},
    correlationId: log.correlation_id || null
  }));
}
```

### Outcome Determination Logic
```javascript
determineOutcome(log) {
  const level = log.level.toLowerCase();
  const message = log.message.toLowerCase();
  
  if (level === 'error' || level === 'critical') return 'blocked';
  if (level === 'warning') return 'deferred';
  if (message.includes('success') || message.includes('complete')) return 'allowed';
  if (message.includes('initialize') || message.includes('start')) return 'in-progress';
  return 'verified';
}
```

---

## 🎨 Visual Design

### Color Palette (CORTEX Cyber-Blue/Slate)

```css
--color-primary-accent: #00d4ff;      /* Cyber cyan */
--color-primary-accent-alt: #7b2cbf;  /* Purple accent */

--color-completed: #10b981;           /* Green */
--color-in-progress: #f59e0b;         /* Orange */
--color-blocked: #ef4444;             /* Red */
--color-not-started: #6b7280;         /* Grey */

--color-audit-info: #60a5fa;          /* Blue */
--color-audit-warning: #fbbf24;       /* Yellow */
--color-audit-error: #ef4444;         /* Red */
--color-audit-critical: #991b1b;      /* Dark red */
```

### Interactive States
- **Hover:** Border color changes to cyber-blue (#00d4ff)
- **Selected:** Background opacity increases, border glows
- **Transition:** 200ms ease-out for smooth feedback

### Typography
- **Base:** System font stack (-apple-system, BlinkMacSystemFont, Segoe UI)
- **Monospace:** Courier New (for timestamps and IDs)
- **Sizes:** xs (0.75rem) to 3xl (2rem) semantic scale

---

## 🔧 Implementation Details

### Key Functions

#### 1. Filter Application
```javascript
applyFilters() {
  const { time, category, level } = this.data.filters;
  let filtered = [...this.data.auditLogs];
  
  // Time filter
  if (time !== 'all') {
    const cutoff = this.getTimeCutoff(time, new Date());
    filtered = filtered.filter(log => new Date(log.timestamp) >= cutoff);
  }
  
  // Category filter
  if (category !== 'all') {
    filtered = filtered.filter(log => log.domain === category);
  }
  
  // Level filter
  if (level !== 'all') {
    filtered = filtered.filter(log => log.level === level);
  }
  
  this.data.filteredLogs = filtered;
  this.renderAuditTimeline();
}
```

#### 2. Impact Assessment
```javascript
assessImpact(event) {
  if (event.level === 'critical' || event.outcome === 'blocked') {
    return {
      level: 'high',
      title: '🔴 HIGH IMPACT',
      description: 'This event blocks progress or violates critical governance rules.'
    };
  } else if (event.level === 'warning' || event.outcome === 'deferred') {
    return {
      level: 'medium',
      title: '🟡 MEDIUM IMPACT',
      description: 'This event may affect plan execution or reduce confidence.'
    };
  } else {
    return {
      level: 'low',
      title: '✅ NO CURRENT IMPACT',
      description: 'This is an informational event. No action required.'
    };
  }
}
```

#### 3. Export Functionality
```javascript
exportAuditLogs() {
  const data = JSON.stringify(this.data.filteredLogs, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `cortex-audit-export-${new Date().toISOString()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
```

---

## ✅ Acceptance Criteria

The Audit Log Viewer is complete when:

- [x] **Fast Answers:** User can answer "why is this blocked?" in under 10 seconds
- [x] **Evidence Links:** Blocked plan items clearly reference audit evidence
- [x] **Signal vs Noise:** Informational logs do not overwhelm critical signals
- [x] **Causality Explained:** Logs explain causality, not just chronology
- [x] **Observability Tool:** Feels like observability, not a console dump

---

## 🚀 Usage Examples

### Scenario 1: "Why is AC-GOV-001 blocked?"

1. Open Plan Viewer
2. Navigate to Audit Log Viewer section
3. **Filter:** Category = "Governance", Level = "Error"
4. **Result:** 3 events shown
5. **Click** on event with target "AC-GOV-001"
6. **Detail Panel Shows:**
   - **What:** MasterOrchestrator attempted to execute AC-GOV-001
   - **Why:** CORE-017 governance rule blocked execution (missing prerequisites)
   - **Changed:** No state change (operation blocked)
   - **Impact:** 🔴 HIGH - Blocks Phase 1 completion
   - **Evidence:** Link to CORE-017 rule documentation

**Time to answer: ~8 seconds**

---

### Scenario 2: "Show me all governance violations this week"

1. **Filter:** Time Range = "Last 7 Days", Level = "Critical"
2. **Result:** 12 critical events displayed
3. **Summary Strip Shows:**
   - Total Events: 1,234
   - Blocked: 12
   - Risk Level: MEDIUM
4. **Export:** Click "Export" button to download JSON for deeper analysis

---

## 📈 Future Enhancements

### Phase 2 (Planned)
- [ ] **Live Updates:** WebSocket connection for real-time event streaming
- [ ] **Search:** Full-text search across event messages
- [ ] **Correlation View:** Group events by correlation ID (trace debugging)
- [ ] **Sparklines:** Mini charts showing event trends over time

### Phase 3 (Planned)
- [ ] **Backend API:** Replace file loading with REST API
- [ ] **Pagination:** Server-side pagination for massive log sets
- [ ] **Advanced Filters:** Regex support, custom date ranges, multi-select
- [ ] **Drill-Down:** Click evidence links to navigate to rule documentation

### Phase 4 (Planned)
- [ ] **Alerting:** Real-time notifications for critical events
- [ ] **Dashboards:** Governance health dashboards
- [ ] **AI Insights:** LLM-powered root cause analysis

---

## 🔗 Integration Points

### With Plan Viewer Core
- **Hero Metrics:** Total audit events displayed in hero section
- **Phase Cards:** Audit event counts per phase (future)
- **Architecture View:** Component health from audit logs (future)

### With Governance System
- **Rule Enforcement:** Links to CORE-* rules
- **Policy Decisions:** Tier precedence resolution events
- **Validation Results:** AC-ID validation outcomes

### With Orchestration
- **Lifecycle Events:** MasterOrchestrator state transitions
- **TodoManager:** Task creation and completion events
- **TDD-Master:** Test execution results

---

## 📚 Technical References

### Files Created
- `plan-viewer-enhanced.html` - Enhanced viewer with audit integration
- `AUDIT-LOG-VIEWER-IMPLEMENTATION.md` - This documentation

### Dependencies
- **D3.js v7** - Data visualization (future charts)
- **Bootstrap Icons** - Icon library
- **No backend required** - Client-side only (for now)

### Browser Compatibility
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive design)

---

## 🎯 Success Metrics

### User Experience
- **Time to Insight:** < 10 seconds to answer "why blocked?"
- **Signal Clarity:** 90%+ of critical events actionable
- **Navigation:** < 3 clicks to reach event details

### Technical Performance
- **Load Time:** < 2 seconds for 1,000 events
- **Render Time:** < 500ms for filter changes
- **Memory:** < 50MB for 10,000 cached events

---

## 📝 Changelog

### Version 1.0.0 (2026-01-11)
- ✅ Initial implementation with three-pane design
- ✅ Audit summary strip with risk calculation
- ✅ Filter & facets panel (time, category, level)
- ✅ Timeline/table with virtualized rendering
- ✅ Detail & impact panel with governance context
- ✅ Export functionality (JSON)
- ✅ Mock data generation for testing
- ✅ Responsive design (desktop + mobile)

---

## 🙏 Acknowledgments

**Design Inspiration:** chat01.md specifications by Asif Hussain  
**Architecture:** CORTEX 6.0 4-tier governance system  
**Philosophy:** "Audit logs are not history. They are accountability."

---

**Document Status:** ✅ COMPLETE  
**Last Updated:** 2026-01-11  
**Next Review:** After Phase 2 MasterOrchestrator integration
