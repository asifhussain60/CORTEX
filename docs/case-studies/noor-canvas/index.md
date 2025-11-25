# Noor Canvas

**Live Q&A Platform | Blazor Server | SignalR**

---

## 📋 Overview

Noor Canvas is a Blazor Server application providing real-time Q&A capabilities for live interactive sessions. The platform enables hosts to manage sessions, participants to submit questions, and real-time voting via SignalR.

**Technology Stack:**
- **Frontend:** Blazor Server (C#)
- **Backend:** ASP.NET Core 6.0+
- **Real-Time:** SignalR
- **Testing:** xUnit, Playwright
- **Deployment:** Continuous Deployment

---

## 🎯 CORTEX Engagements

Case study information about 🎯 cortex engagements. See related sections for complete context.

### [SignalR Architecture Refactoring](signalr-refactoring/index.md)
**Duration:** 3.5 days | **Type:** Refactoring | **Year:** 2025

Multi-phase refactoring transforming inline SignalR handlers into a service-oriented architecture with comprehensive test coverage. Included critical bug fix achieving 100% participant connection success.

**Highlights:**
- 🏗️ **Architecture:** Inline handlers → Service-oriented design
- ✅ **Testing:** 0% → 100% coverage (33 unit tests)
- 🔧 **Critical Fix:** 45-minute turnaround, 15 lines changed
- 📊 **Code Quality:** 1,520 lines duplication removed

[Read Full Case Study →](signalr-refactoring/index.md)

---

### [Canvas Components Refactoring](canvas-refactoring/index.md)
**Duration:** Week 1 Complete (Phase 1/3) | **Type:** Code Quality | **Year:** 2025

Systematic elimination of massive code duplication across three canvas components (HostControlPanel, SessionCanvas, TranscriptCanvas). Week 1 achieved 67% of total reduction goal through CSS extraction and component creation.

**Highlights:**
- 📉 **Duplication:** 2,360 lines eliminated (67% of 3,510 target)
- ⚡ **Efficiency:** 98.8% code reduction in refactored sections
- 🎨 **Architecture:** 3 new shared components created
- ✅ **Quality:** 100% visual parity maintained

[Read Full Case Study →](canvas-refactoring/index.md)

---

## 📈 Cumulative Impact

Across all Noor Canvas engagements:

<div class="metric-cards">
  <div class="metric-card">
    <div class="metric-value">3.5</div>
    <div class="metric-label">Days Total Engagement</div>
  </div>
  
  <div class="metric-card">
    <div class="metric-value">1,520</div>
    <div class="metric-label">Lines Duplication Removed</div>
  </div>
  
  <div class="metric-card">
    <div class="metric-value">100%</div>
    <div class="metric-label">Test Coverage Achieved</div>
  </div>
  
  <div class="metric-card">
    <div class="metric-value">100%</div>
    <div class="metric-label">Connection Success Rate</div>
  </div>
</div>

---

## 🏛️ Architecture Evolution

**Before CORTEX:**
```
HostControlPanel.razor (4,951 lines)
├── InitializeSignalRAsync() - 350+ lines inline handlers
├── Mixed UI logic + SignalR handling
└── Duplicated across 3 components

SessionCanvas.razor (4,056 lines)
├── HubConnectionBuilder - Inline configuration
├── 12+ inline event handlers
└── Duplicated SignalR patterns

TranscriptCanvas.razor (4,871 lines)
├── Duplicated SessionCanvas patterns
└── Type incompatibilities (nested classes)
```

**After CORTEX:**
```
HostControlPanel.razor (4,636 lines, -315)
└── IHostSignalREventHandler (service injection)

SessionCanvas.razor (3,740 lines, -316)
└── ISessionCanvasSignalRService (service injection)

TranscriptCanvas.razor (3,982 lines, -889)
└── Type adapter + ISessionCanvasSignalRService

Services/ (NEW, 637 lines)
├── IHostSignalREventHandler (5 methods, 287 lines)
├── ISessionCanvasSignalRService (8 methods, 336 lines)
└── HubConnectionFactory (absolute URL resolution)

Tests/ (NEW, 755 lines)
├── HostSignalREventHandlerTests (21 tests, 100% pass)
└── SessionCanvasSignalRServiceTests (12 tests, 100% pass)
```

---

## 🔍 Technology Breakdown

**Blazor Server Architecture:**
- Server-side rendering with SignalR circuits
- Real-time UI updates via SignalR
- Component-based architecture

**SignalR Hub Design:**
- Hub-based pub/sub messaging
- Host → Participant communication
- Real-time question submission and voting

**Testing Strategy:**
- TDD approach (tests before implementation)
- xUnit for unit testing
- Playwright for integration testing
- 100% coverage for critical paths

---

## 📚 Documentation

- [SignalR Refactoring Case Study](signalr-refactoring/index.md)
- [Methodology Deep Dive](signalr-refactoring/methodology.md)
- [Success Metrics](signalr-refactoring/metrics.md)
- [Technical Architecture](signalr-refactoring/technical.md)
- [Lessons Learned](signalr-refactoring/lessons.md)

---

**Application Type:** Web Application  
**Domain:** Live Q&A Platform  
**Status:** Production  
**CORTEX Version:** 3.2.0
