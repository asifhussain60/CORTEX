# Dashboard MVC Integration Guide

**Authority:** Phase 32 - Glassmorphism Dashboard Generator Fix  
**Version:** 1.0  
**Updated:** 2026-02-06  
**Status:** ACTIVE

---

## Overview

The CORTEX dashboard follows a client-side MVC (Model-View-Controller) architecture, enabling rich interactive experiences while maintaining file:// protocol compatibility and no external fetch dependencies.

**Key Benefits:**
- ✅ Clear separation of concerns (Model, View, Controller)
- ✅ Data-driven updates without page reload
- ✅ Deferred rendering for performance optimization
- ✅ Works offline (file:// protocol compatible)
- ✅ Single HTML file deployment (all assets included)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ Dashboard HTML (repos/<slug>/index.html)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ MODEL: window.dashboardData (Embedded JSON)       │  │
│  │ ├─ repo_slug, display_name, health_score         │  │
│  │ ├─ overview_metrics, architecture, use_cases     │  │
│  │ └─ vulnerabilities, testing, recommendations     │  │
│  └───────────────────────────────────────────────────┘  │
│           ↓ (Data binding)                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ VIEW: HTML + CSS (Glassmorphism theme)           │  │
│  │ ├─ Dashboard header (logo + stats)               │  │
│  │ ├─ Tab navigation (.tab-button)                  │  │
│  │ ├─ Content panels (.tab-panel)                   │  │
│  │ └─ Chart containers (ChartHost)                  │  │
│  └───────────────────────────────────────────────────┘  │
│           ↓ (Event delegation)                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ CONTROLLER: JavaScript event handlers            │  │
│  │ ├─ Tab switching (click → show panel)            │  │
│  │ ├─ Chart initialization (ChartHost.render)       │  │
│  │ ├─ Data filtering (UseCasesManager)              │  │
│  │ └─ Navigation (links → state change)             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Model: Data Representation

**Location:** `window.dashboardData` (embedded in `<script>` tag)

**Structure:**
```javascript
window.dashboardData = {
  // Core identifiers
  repo_slug: "ksessions",
  display_name: "KSESSIONS",
  owner: "Enterprise IT",
  primary_language: "Python",
  
  // Summary metrics
  health_score: 92,        // 0-100
  risk_score: 8,           // 0-100
  loc: 145829,             // Lines of code
  files: 2847,             // Total files
  services_count: 12,      // Microservices/modules
  coverage_pct: 87.3,      // Test coverage %
  
  // Metadata
  last_analyzed_at: "2026-02-06T10:30:00Z",
  version: "8.0",
  tags: ["enterprise", "auth", "production"],
  
  // Tab data (populated on demand)
  overview_metrics: {
    functions: 1245,
    classes: 287,
    critical_issues: 0,
    major_issues: 2,
    minor_issues: 14,
  },
  
  architecture: [
    {
      name: "API Layer",
      module_count: 8,
      loc: 24500,
      complexity: 2.3,
      dependencies: ["auth", "database"],
    },
    // ... more layers
  ],
  
  dependencies: [
    {
      name: "fastapi",
      version: "0.109.2",
      latest_version: "0.109.2",
      is_outdated: false,
      has_vulnerabilities: false,
    },
    // ... more deps
  ],
  
  quality: [
    {
      name: "Cyclomatic Complexity",
      value: 2.8,
      threshold: 5.0,
      status: "ok",
    },
    // ... more metrics
  ],
  
  vulnerabilities: [
    {
      id: "CWE-89",
      title: "SQL Injection Risk",
      description: "...",
      severity: "high",
      cwe_id: "CWE-89",
      file_path: "app/db.py",
      line_number: 145,
      recommendation: "Use parameterized queries",
    },
    // ... more findings
  ],
  
  testing: {
    coverage_pct: 87.3,
    unit_tests: 391,
    integration_tests: 45,
    e2e_tests: 12,
    risky_files: ["app/auth.py"],
    uncovered_files: ["app/migrations/"],
  },
  
  use_cases: [
    {
      id: "UC-001",
      title: "Multi-tenant session isolation",
      summary: "KSESSIONS provides secure session isolation for multi-tenant deployments",
      persona: "production_owner",
      category: "reliability",
      severity: "high",
      tags: ["session", "auth", "isolation"],
      signals: ["zero_security_incidents", "87.3% coverage"],
      actions: ["Review session cache strategy"],
      related_tabs: ["overview", "security"],
    },
    // ... more use cases
  ],
  
  recommendations: [
    {
      id: "REC-001",
      title: "Upgrade outdated dependencies",
      description: "3 dependencies have critical security updates available",
      priority: "p0",
      category: "security",
      effort: "low",
      impact: "high",
    },
    // ... more recommendations
  ],
};
```

**Data Types:**
- `Enum` values converted to strings: `"production_owner"` instead of `UseCasePersona.PRODUCTION_OWNER`
- `datetime` converted to ISO 8601: `"2026-02-06T10:30:00Z"`
- Nested dataclasses become objects: `overview_metrics: {...}`

**Size Considerations:**
- Typical: 10-20 KB (gzip-compressible)
- Embedded directly in HTML (no fetch)
- Parsed once on page load

---

## View: Presentation Layer

### Header Component

```html
<div class="dashboard-header">
  <div class="logo-container">
    <img src="../../assets/images/CORTEX-logo-200.png" alt="CORTEX">
  </div>
  <div class="header-content">
    <h1 class="title">KSESSIONS</h1>
    <p class="tagline">Enterprise session management system</p>
    
    <div class="header-stats">
      <div class="header-stat">
        <div class="value">92</div>
        <div class="label">Health</div>
      </div>
      <div class="header-stat">
        <div class="value">87.3%</div>
        <div class="label">Coverage</div>
      </div>
      <div class="header-stat">
        <div class="value">2847</div>
        <div class="label">Files</div>
      </div>
    </div>
  </div>
</div>
```

**CSS Styling:**
```css
.dashboard-header {
  background: var(--glass-bg, rgba(26, 31, 58, 0.7));
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--glass-border);
}

.logo-container img {
  animation: logoGlow 3s ease-in-out infinite alternate;
}

.title {
  font-size: 2.5rem;
  color: var(--accent-primary, #00d4ff);
  text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
}
```

### Tab Navigation

```html
<div class="tab-navigation">
  <button class="tab-button active" data-tab="overview">
    📊 Overview
  </button>
  <button class="tab-button" data-tab="architecture">
    🏗️ Architecture
  </button>
  <button class="tab-button" data-tab="dependencies">
    📦 Dependencies
  </button>
  <button class="tab-button" data-tab="security">
    🔒 Security
  </button>
  <button class="tab-button" data-tab="testing">
    🧪 Testing
  </button>
  <button class="tab-button" data-tab="use-cases">
    💡 Use Cases
  </button>
  <button class="tab-button" data-tab="recommendations">
    ⚡ Recommendations
  </button>
</div>
```

### Content Panels

```html
<div class="content-panels">
  <div id="overview" class="tab-panel active">
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-value">145829</div>
        <div class="metric-label">Lines of Code</div>
      </div>
      <!-- More metric cards -->
    </div>
  </div>
  
  <div id="architecture" class="tab-panel">
    <!-- Architecture visualization -->
    <div class="chart-host" data-chart="architecture"></div>
  </div>
  
  <!-- More panels -->
</div>
```

### Chart Containers

```html
<!-- Deferred rendering: chart only loads when tab visible -->
<div class="chart-host" 
     data-chart="vulnerabilities"
     data-chart-type="severity-breakdown">
  <div class="chart-placeholder">
    <p>📊 Loading visualization...</p>
  </div>
</div>
```

---

## Controller: Interaction Logic

### Tab Navigation Handler

```javascript
document.querySelectorAll('.tab-button').forEach(button => {
  button.addEventListener('click', (e) => {
    const tabName = e.target.closest('.tab-button').dataset.tab;
    
    // Update active states
    document.querySelectorAll('.tab-button').forEach(b => {
      b.classList.toggle('active', b.dataset.tab === tabName);
    });
    
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === tabName);
    });
    
    // Trigger chart rendering if needed
    if (!document.getElementById(tabName).dataset.rendered) {
      renderCharts(tabName);
      document.getElementById(tabName).dataset.rendered = true;
    }
  });
});
```

### Chart Initialization (ChartHost)

```javascript
class ChartHost {
  constructor(container, data, options = {}) {
    this.container = container;
    this.data = data;
    this.options = options;
    this.chart = null;
    this.isVisible = false;
  }
  
  // Lazy-load chart only when visible
  render() {
    if (!this.isVisible || this.chart) return;
    
    // Initialize ECharts instance
    this.chart = echarts.init(this.container);
    this.chart.setOption(this.options);
    this.isVisible = true;
  }
}

// Render on tab click
function renderCharts(tabName) {
  const container = document.getElementById(tabName);
  const hosts = container.querySelectorAll('[data-chart]');
  
  hosts.forEach(hostEl => {
    const chartName = hostEl.dataset.chart;
    const chartType = hostEl.dataset.chartType;
    const data = window.dashboardData[chartName];
    
    const host = new ChartHost(hostEl, data);
    host.render();
  });
}
```

### Use Cases Manager

```javascript
class UseCasesManager {
  constructor(containerId, useCases) {
    this.container = document.querySelector(containerId);
    this.useCases = useCases;
    this.filteredCases = useCases;
    this.init();
  }
  
  init() {
    // Add filter controls
    this.addFilterUI();
    
    // Render initial list
    this.render();
    
    // Initialize search (Fuse.js)
    this.fuse = new Fuse(this.useCases, {
      keys: ['title', 'summary', 'tags'],
      threshold: 0.3,
    });
  }
  
  filterByPersona(persona) {
    this.filteredCases = this.useCases.filter(
      uc => uc.persona === persona
    );
    this.render();
  }
  
  search(query) {
    const results = this.fuse.search(query);
    this.filteredCases = results.map(r => r.item);
    this.render();
  }
  
  render() {
    const html = this.filteredCases.map(uc => `
      <div class="use-case-card severity-${uc.severity}">
        <h3>${uc.title}</h3>
        <p>${uc.summary}</p>
        <div class="uc-meta">
          <span class="persona">${uc.persona}</span>
          <span class="category">${uc.category}</span>
        </div>
      </div>
    `).join('');
    
    this.container.innerHTML = html;
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  const useCases = window.dashboardData?.use_cases || [];
  window.useCasesManager = new UseCasesManager(
    '#use-cases-container',
    useCases
  );
});
```

### Deferred Rendering Strategy

```javascript
// Only render charts when their tab becomes visible
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const chart = new ChartHost(entry.target, data);
      chart.render();
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll('[data-chart]').forEach(host => {
  observer.observe(host);
});
```

---

## Data Flow Example

**Scenario:** User clicks "Architecture" tab

```
1. User Action
   └─ Click <button data-tab="architecture">
   
2. Controller Event Handler
   ├─ Detect click event
   ├─ Get tab name from data-tab
   └─ Update UI state (add .active class)
   
3. Visibility Change
   └─ Show #architecture panel
   
4. Deferred Rendering Trigger
   ├─ Check if charts already rendered
   └─ If not: Call renderCharts('architecture')
   
5. Chart Initialization
   ├─ Find [data-chart] elements in panel
   ├─ Extract data from window.dashboardData.architecture
   ├─ Create ChartHost instances
   └─ Call chart.render()
   
6. ECharts Rendering
   ├─ Initialize echarts.init(container)
   ├─ Apply chart options
   ├─ Display visualization
   └─ User sees interactive chart
```

---

## Testing the MVC Integration

### Pilot Test Files

**tests/dashboard/test_mvc_integration.html** (650 LOC)
- Tests Model: Data injection, JSON validation
- Tests View: CSS rendering, layout correctness
- Tests Controller: Event handling, state management
- Tests Integration: Full data flow

**tests/dashboard/test_deferred_renderer.html** (503 LOC)
- Tests ChartHost visibility guards
- Tests lazy-loading behavior
- Tests performance metrics
- Tests file:// compatibility

### Running Pilot Tests

```bash
# Open test in browser (file:// mode)
open tests/dashboard/test_mvc_integration.html

# Or via HTTP server
cd CORTEX && python3 -m http.server 8000
# Then visit: http://localhost:8000/tests/dashboard/test_mvc_integration.html

# Check browser console for:
# ✅ Model tests pass
# ✅ View tests pass
# ✅ Controller tests pass
# ✅ Integration tests pass
```

### Automated Tests

```bash
# Run pytest for generator tests
pytest tests/visualization/spa/test_suite_generator.py::TestGPTSpecAcceptanceCriteria::test_glassmorphism_css_present -v

# Should pass:
# ✅ Glassmorphism CSS files present
# ✅ Color specifications correct
# ✅ Asset paths relative
# ✅ No fetch() calls
```

---

## Common Patterns

### Adding a New Tab

1. **Add button to navigation:**
   ```html
   <button class="tab-button" data-tab="new-tab">
     📈 New Tab
   </button>
   ```

2. **Add panel to content:**
   ```html
   <div id="new-tab" class="tab-panel">
     <!-- Tab content -->
     <div class="chart-host" data-chart="new_data"></div>
   </div>
   ```

3. **Add data to model:**
   ```javascript
   window.dashboardData.new_data = [/* data array */];
   ```

4. **Chart auto-renders on tab click** (no code needed!)

### Adding a New Filter

```javascript
// In UseCasesManager
filterByCategory(category) {
  this.filteredCases = this.useCases.filter(
    uc => uc.category === category
  );
  this.render();
}

// In UI
<select id="category-filter">
  <option value="">All Categories</option>
  <option value="reliability">Reliability</option>
  <option value="security">Security</option>
</select>

// Event handler
document.getElementById('category-filter').addEventListener('change', (e) => {
  window.useCasesManager.filterByCategory(e.target.value);
});
```

### Updating Data Dynamically

```javascript
// Update a metric
window.dashboardData.health_score = 95;

// Re-render affected view
document.querySelector('[data-metric="health"]').textContent = 95;

// Or re-initialize charts if data structure changed
renderCharts('overview');
```

---

## Performance Considerations

1. **Deferred Rendering** — Only render visible charts
2. **Lazy Loading** — Use `IntersectionObserver` for off-screen elements
3. **Data Embedding** — No network requests (file:// compatible)
4. **CSS Classes** — Minimize reflows with CSS transitions
5. **Search Indexing** — Fuse.js indexes data once on init

**Expected Performance:**
- Page load: < 500ms
- Tab switch: < 100ms
- Chart render: < 300ms
- Search: < 50ms

---

## Troubleshooting MVC Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Data not displaying | Model not loaded | Check `window.dashboardData` exists |
| Charts empty | ChartHost not rendering | Check container visibility, call `render()` |
| Tab click broken | Event handler missing | Verify `.tab-button` event listeners attached |
| Styles wrong | CSS not loaded | Check `glass-*.css` file paths |
| Search not working | Fuse.js not loaded | Verify vendor libs loaded, init UseCasesManager |

---

## References

- **Phase 32:** Glassmorphism Dashboard Generator Fix
- **Template:** company/dashboards/templates/repo-dashboard-glass-v1.html
- **Generator:** cortex/visualization/spa/suite_generator.py
- **Pilot Tests:** tests/dashboard/test_mvc_integration.html (650 LOC)
- **Deferred Rendering:** tests/dashboard/test_deferred_renderer.html (503 LOC)
