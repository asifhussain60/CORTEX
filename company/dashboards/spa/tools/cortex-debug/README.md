# CORTEX Debug Orchestrator

**Version:** 1.0.0  
**Purpose:** Automated debugging for SPA dashboard via console log tracing  
**Authority:** CORTEX Governance

---

## 🎯 Overview

The CORTEX Debug Orchestrator is a multi-phase debugging tool that:

1. **INJECT** — Floods all key JS files with uniquely marked console.logs
2. **CAPTURE** — Runs the dashboard and collects all debug output
3. **ANALYZE** — Traces logs to identify race conditions and integration breakages
4. **FIX-PLAN** — Generates a comprehensive fix plan with root cause analysis
5. **CLEANUP** — Removes ONLY CORTEX markers, leaving code production-ready

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORTEX Debug Orchestrator                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │  INJECT  │───▶│  CAPTURE │───▶│ ANALYZE  │───▶│ FIX-PLAN │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│        │                                                │       │
│        │              User Approves Fix                 │       │
│        │                     │                          ▼       │
│        │              ┌──────┴──────┐            ┌──────────┐  │
│        └──────────────│   CLEANUP   │◀───────────│  VERIFY  │  │
│                       └─────────────┘            └──────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Debug Marker Format

All injected logs use this unique format:

```javascript
// Format: [CORTEX_DEBUG_<SESSION>:<PHASE>:<FILE>:<LINE>] <message>
console.log('[CORTEX_DEBUG_abc123:INIT:app.js:97] Starting dashboard init');
console.log('[CORTEX_DEBUG_abc123:DATA:DualFormatDataLoader.js:45] Loading repo: KSESSIONS');
console.log('[CORTEX_DEBUG_abc123:RACE:TabManager.js:122] Tab switch before data ready');
```

**Session ID:** 8-char UUID (regenerated each debug run)  
**Phases:** INIT, DATA, DOM, RENDER, ASYNC, RACE, ERROR, COMPLETE

---

## 📊 Injection Points

| File | Injection Type | Purpose |
|------|----------------|---------|
| `app.js` | Function entry/exit | Track initialization flow |
| `DataBinder.js` | Data binding events | Track data flow |
| `DualFormatDataLoader.js` | Async operations | Detect race conditions |
| `JSONDataAdapter.js` | Data parsing | Validate data integrity |
| `TabManager.js` | Tab events | Track UI state changes |
| `ChartHost.js` | Chart rendering | Detect render timing issues |
| `Pagination.js` | Page events | Track pagination state |
| `SubTabs.js` | Sub-tab events | Track nested navigation |
| `UseCasesManager.js` | Use case rendering | Track complex renders |
| `Wizard.js` | Wizard steps | Track multi-step flows |

---

## 🧠 Analysis Patterns

The analyzer detects:

### Race Conditions
- Data accessed before load complete
- DOM manipulation before render
- Event handlers attached to missing elements

### Integration Breakages
- Script loading order issues
- Missing dependencies
- DOM container mismatches

### Timing Issues
- Async operations completing out of order
- Chart rendering before container visible
- Tab switching before content ready

---

## 🚀 Usage

```bash
# Full debugging cycle
node tools/cortex-debug/cortex-debug-orchestrator.js run

# Individual phases
node tools/cortex-debug/cortex-debug-orchestrator.js inject
node tools/cortex-debug/cortex-debug-orchestrator.js capture --url http://localhost:8888/dashboard.html?repo=KSESSIONS
node tools/cortex-debug/cortex-debug-orchestrator.js analyze
node tools/cortex-debug/cortex-debug-orchestrator.js cleanup

# After user confirms fix
node tools/cortex-debug/cortex-debug-orchestrator.js cleanup --confirm
```

---

## 📋 Output Files

| File | Purpose |
|------|---------|
| `.cortex-debug/session.json` | Current debug session metadata |
| `.cortex-debug/injection-map.json` | Map of all injected markers |
| `.cortex-debug/captured-logs.json` | Raw console output |
| `.cortex-debug/analysis-report.json` | Analyzed results |
| `.cortex-debug/fix-plan.md` | Human-readable fix plan |

---

## ⚠️ Safety

- **NEVER** commit debug-injected code
- **ALWAYS** run cleanup before production deployment
- Debug markers are designed to be easily grep-able: `CORTEX_DEBUG_`
- Cleanup validates no markers remain

---

*CORTEX Governance v7.1*
