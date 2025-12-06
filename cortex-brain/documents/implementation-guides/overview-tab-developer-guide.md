# Overview Tab Developer Guide

**Version:** 1.0  
**Last Updated:** 2025-12-06  
**Purpose:** Technical guide for extending and maintaining Overview tab components

---

## Architecture Overview

### Component Hierarchy

```
Overview Tab (Frontend)
├── overview-tab-v3.js (Main component, 580 lines)
├── overview-tab.css (Styles, 400 lines)
└── D3.js v7 (Charts library)

Backend Data Pipeline
├── OverviewCollector (Orchestrator)
│   ├── HealthDataCollector (Overall health metrics)
│   ├── ArchitectureCollector (Language composition)
│   └── CodeOrganizationCollector (File structure)
└── overview.json (Output, ~3KB)

Integration Layer
├── data-loader.js (Fetches overview.json)
└── app.js (Routes to Overview tab)
```

### Data Flow

```
1. Backend: OverviewCollector aggregates data → overview.json
2. Frontend: data-loader.js fetches → caches → passes to app.js
3. app.js: Routes to overview-tab-v3.js with data.overview
4. overview-tab-v3.js: Renders → D3.js charts → Updates DOM
```

---

## Backend Extension

### Adding New Metrics to overview.json

**File:** `src/dashboard/data/overview_collector.py`

**Step 1: Update schema**

Edit `overview.json` schema to include new field:

```json
{
  "key_metrics": {
    "existing_field": "...",
    "new_metric_name": 0  // Add your new metric
  }
}
```

**Step 2: Collect data**

Add collector method:

```python
class OverviewCollector:
    def _collect_new_metric(self, repo_path: Path) -> float:
        """
        Collect new metric from repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Calculated metric value
        """
        # Your collection logic here
        return calculated_value
```

**Step 3: Integrate into pipeline**

Add to `collect()` method:

```python
def collect(self, repo_path: Path) -> dict:
    # ... existing collection ...
    
    overview_data['key_metrics']['new_metric_name'] = self._collect_new_metric(repo_path)
    
    return overview_data
```

**Step 4: Add tests**

```python
def test_collect_new_metric(self):
    """Test new metric collection"""
    collector = OverviewCollector()
    result = collector._collect_new_metric(Path("/test/repo"))
    
    assert isinstance(result, float)
    assert result >= 0
```

**Step 5: Update integration tests**

Add to `tests/dashboard/test_overview_integration.py`:

```python
def test_new_metric_in_schema(self, mock_overview_data):
    """Verify new metric exists and is valid"""
    metrics = mock_overview_data.get('key_metrics')
    assert 'new_metric_name' in metrics, "new_metric_name missing"
    assert metrics['new_metric_name'] >= 0, "Invalid value"
```

---

## Frontend Extension

### Adding New Visual Component

**File:** `cortex-brain/dashboards/ui/components/overview-tab-v3.js`

**Example: Add "Deployment Frequency" metric**

**Step 1: Update renderOverview() function**

```javascript
function renderOverview(data) {
    // ... existing code ...
    
    // Add new metric card
    const deploymentFrequency = data.key_metrics.deployment_frequency || 0;
    
    html += `
        <div class="metric-card">
            <div class="metric-value">${deploymentFrequency}</div>
            <div class="metric-label">Deployments/Month</div>
            <div class="metric-trend ${getTrendClass(deploymentFrequency)}">
                ${formatTrendIndicator(data.trends.deployment_trend)}
            </div>
        </div>
    `;
    
    // ... rest of function ...
}
```

**Step 2: Add styles**

Edit `cortex-brain/dashboards/ui/styles/overview-tab.css`:

```css
.metric-card {
    /* Existing styles work, no changes needed */
}

/* Optional: Add deployment-specific styles */
.metric-card .deployment-indicator {
    color: #00d4aa;
    font-weight: 600;
}
```

**Step 3: Test rendering**

```javascript
// Manual test in browser console
const testData = {
    key_metrics: {
        deployment_frequency: 12
    },
    trends: {
        deployment_trend: "improving"
    }
};

renderOverview(testData);
// Verify metric card appears with value "12"
```

---

### Adding New D3.js Chart

**Example: Add "Complexity Distribution" histogram**

**Step 1: Create chart function**

```javascript
function renderComplexityDistribution(data, containerId) {
    const complexityData = data.complexity_distribution; // [1, 5, 12, 8, 2]
    const bins = ["0-5", "6-10", "11-20", "21-50", "50+"];
    
    // Set dimensions
    const margin = {top: 20, right: 20, bottom: 40, left: 50};
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // X scale
    const x = d3.scaleBand()
        .domain(bins)
        .range([0, width])
        .padding(0.1);
    
    // Y scale
    const y = d3.scaleLinear()
        .domain([0, d3.max(complexityData)])
        .range([height, 0]);
    
    // Draw bars
    svg.selectAll(".bar")
        .data(complexityData)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", (d, i) => x(bins[i]))
        .attr("width", x.bandwidth())
        .attr("y", d => y(d))
        .attr("height", d => height - y(d))
        .attr("fill", "#4a90e2");
    
    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(y).ticks(5));
    
    // Add labels
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", height + 35)
        .attr("text-anchor", "middle")
        .text("Complexity Range");
    
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -35)
        .attr("text-anchor", "middle")
        .text("File Count");
}
```

**Step 2: Call from renderOverview()**

```javascript
function renderOverview(data) {
    // ... existing code ...
    
    html += `
        <div class="chart-container">
            <h3>Complexity Distribution</h3>
            <div id="complexity-chart"></div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Render after DOM update
    setTimeout(() => {
        renderComplexityDistribution(data, 'complexity-chart');
    }, 100);
}
```

**Step 3: Add responsive handling**

```javascript
function renderComplexityDistribution(data, containerId) {
    const container = document.getElementById(containerId);
    const containerWidth = container.offsetWidth;
    
    // Responsive width
    const width = Math.min(containerWidth, 400) - margin.left - margin.right;
    
    // ... rest of chart code ...
}

// Add resize listener
window.addEventListener('resize', debounce(() => {
    // Re-render chart on resize
    d3.select("#complexity-chart").selectAll("*").remove();
    renderComplexityDistribution(window.currentData, 'complexity-chart');
}, 250));
```

---

## Styling Guidelines

### CSS Architecture

**File:** `cortex-brain/dashboards/ui/styles/overview-tab.css`

**Structure:**
```css
/* 1. Health Score Hero (lines 1-120) */
.health-score-hero { }

/* 2. Key Metrics Cards (lines 121-240) */
.key-metrics-grid { }

/* 3. Health Categories (lines 241-320) */
.health-categories { }

/* 4. Composition Chart (lines 321-380) */
.composition-chart { }

/* 5. Responsive Breakpoints (lines 381-400) */
@media (max-width: 1024px) { }
```

### Adding New Styles

**Best practices:**
1. **Namespace:** Prefix with `.overview-tab-`
2. **Modular:** Keep component styles together
3. **Responsive:** Add mobile breakpoints
4. **Consistent:** Use existing color scheme

**Example:**

```css
/* New component: Deployment History Timeline */
.overview-tab-deployment-timeline {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--card-bg);
    border-radius: 12px;
}

.deployment-timeline-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    border-left: 3px solid var(--primary-color);
}

.deployment-timestamp {
    font-size: 0.875rem;
    color: var(--text-secondary);
    min-width: 120px;
}

.deployment-status {
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

.deployment-status.success {
    background: rgba(0, 212, 170, 0.15);
    color: #00d4aa;
}

.deployment-status.failed {
    background: rgba(255, 75, 75, 0.15);
    color: #ff4b4b;
}

/* Responsive: Stack on mobile */
@media (max-width: 768px) {
    .deployment-timeline-item {
        flex-direction: column;
        align-items: flex-start;
    }
}
```

---

## Performance Optimization

### Chart Rendering Performance

**Problem:** D3.js charts slow with large datasets (>1000 points)

**Solutions:**

**1. Data Sampling**
```javascript
function sampleData(data, maxPoints = 100) {
    if (data.length <= maxPoints) return data;
    
    const step = Math.ceil(data.length / maxPoints);
    return data.filter((_, i) => i % step === 0);
}

// Use in chart rendering
const sampledData = sampleData(rawData, 100);
renderChart(sampledData);
```

**2. Virtualization (for large lists)**
```javascript
function renderVirtualizedList(items, visibleCount = 20) {
    const scrollContainer = document.getElementById('scrollable-list');
    const visibleStart = Math.floor(scrollContainer.scrollTop / itemHeight);
    const visibleEnd = visibleStart + visibleCount;
    
    const visibleItems = items.slice(visibleStart, visibleEnd);
    // Render only visible items
}
```

**3. Debounced Resize**
```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

window.addEventListener('resize', debounce(() => {
    reRenderCharts();
}, 250));
```

---

## Testing

### Unit Tests

**Backend tests:** `tests/dashboard/test_overview_collector.py`

```python
def test_overview_collector_aggregation():
    """Test OverviewCollector aggregates data correctly"""
    collector = OverviewCollector()
    data = collector.collect(Path("/test/repo"))
    
    assert 'overall_health' in data
    assert 'key_metrics' in data
    assert data['overall_health']['score'] >= 0
```

### Integration Tests

**Schema validation:** `tests/dashboard/test_overview_integration.py`

```python
def test_new_field_in_schema(mock_overview_data, overview_schema):
    """Verify new field matches schema"""
    validate(instance=mock_overview_data, schema=overview_schema)
```

### Frontend Tests (Manual)

**Browser console tests:**

```javascript
// Test data loading
console.log('Testing data load...');
fetch('/data/mock/overview.json')
    .then(r => r.json())
    .then(data => {
        console.log('Data loaded:', data);
        console.assert(data.overall_health.score >= 0, 'Invalid health score');
        console.assert(Array.isArray(data.composition.languages), 'Languages not array');
    });

// Test chart rendering
console.log('Testing chart render...');
const testData = { /* ... */ };
renderOverview(testData);
console.assert(document.querySelector('.health-score-hero'), 'Hero not rendered');
console.assert(document.querySelector('#composition-chart svg'), 'Chart not rendered');
```

---

## Debugging

### Common Issues

**Issue 1: Chart not rendering**

**Symptoms:** Empty div, no SVG

**Debug steps:**
```javascript
// 1. Check data exists
console.log('Data:', window.currentData);

// 2. Check container exists
console.log('Container:', document.getElementById('chart-container'));

// 3. Check D3 loaded
console.log('D3 version:', d3.version);

// 4. Check for JS errors
// Open browser DevTools → Console tab
```

**Solution:** Ensure `setTimeout()` delay allows DOM update before D3 renders.

---

**Issue 2: Schema mismatch error**

**Symptoms:** "Cannot read property 'languages' of undefined"

**Debug steps:**
```javascript
// 1. Log data structure
console.log(JSON.stringify(data, null, 2));

// 2. Check expected vs actual
console.log('Expected:', { languages: [...] });
console.log('Actual:', data.composition);

// 3. Add fallbacks
const languages = data.composition?.languages || [];
```

**Solution:** Always use optional chaining (`?.`) and defaults (`|| []`).

---

**Issue 3: Performance lag**

**Symptoms:** UI freezes when rendering large datasets

**Debug steps:**
```javascript
// 1. Profile rendering
console.time('render');
renderOverview(data);
console.timeEnd('render'); // Should be <300ms

// 2. Check data size
console.log('Data size:', JSON.stringify(data).length, 'bytes');
console.log('Languages count:', data.composition.languages.length);

// 3. Enable browser profiler
// DevTools → Performance tab → Record
```

**Solution:** Implement data sampling or pagination for large datasets.

---

## Deployment Checklist

Before deploying Overview tab changes:

- [ ] **Backend tests pass:** `pytest tests/dashboard/test_overview_integration.py`
- [ ] **Schema validation:** All required fields present in overview.json
- [ ] **Performance:** Rendering <300ms (test with large dataset)
- [ ] **Responsive:** Test on mobile (375px), tablet (768px), desktop (1920px)
- [ ] **Browser compatibility:** Test Chrome, Firefox, Safari, Edge
- [ ] **Accessibility:** Keyboard navigation works, screen reader friendly
- [ ] **Documentation:** Update user guide if UI changed
- [ ] **Git commit:** Clean commit with descriptive message
- [ ] **Dashboard restart:** Kill existing server, restart on port 8082
- [ ] **Visual QA:** Compare before/after screenshots

---

## Migration Guide

### Upgrading from Overview v2 to v3

**Breaking changes:**
1. `composition` changed from flat object to nested structure
2. `critical_issues` field names changed (`title` → `severity`, `description` → `message`)

**Migration steps:**

**1. Update backend collector**

```python
# Old (v2)
composition = {
    "Python": 75.2,
    "JavaScript": 15.8
}

# New (v3)
composition = {
    "languages": [
        {"name": "Python", "percentage": 75.2, "loc": 34340},
        {"name": "JavaScript", "percentage": 15.8, "loc": 7219}
    ]
}
```

**2. Update frontend rendering**

```javascript
// Old (v2)
Object.entries(composition).map(([lang, pct]) => ...)

// New (v3)
composition.languages.map(lang => lang.percentage)
```

**3. Run tests to verify**

```bash
pytest tests/dashboard/test_overview_integration.py
```

---

## Contribution Guidelines

### Code Style

**JavaScript:**
- ES6+ syntax (const/let, arrow functions, template literals)
- 4-space indentation
- Single quotes for strings
- Descriptive variable names (`healthScore` not `hs`)

**Python:**
- PEP 8 compliant
- Type hints for all functions
- Docstrings (Google style)
- 4-space indentation

### Git Workflow

**Branch naming:**
- `feature/overview-tab-metric-xyz`
- `fix/overview-chart-rendering`
- `docs/overview-user-guide-update`

**Commit messages:**
- Prefix: `feat`, `fix`, `test`, `docs`, `refactor`
- Format: `feat(dashboard): add deployment frequency metric`
- Body: Explain why, not what (code shows what)

**Pull Request:**
- Title: Clear description of change
- Description: Link to issue, screenshots, testing notes
- Reviewers: Tag dashboard team
- CI: All tests must pass

---

## API Reference

### OverviewCollector

**File:** `src/dashboard/data/overview_collector.py`

```python
class OverviewCollector:
    """
    Aggregates overview data from multiple collectors.
    
    Attributes:
        health_collector: HealthDataCollector instance
        architecture_collector: ArchitectureCollector instance
        code_org_collector: CodeOrganizationCollector instance
    """
    
    def collect(self, repo_path: Path) -> dict:
        """
        Collect overview data for repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            dict: Overview data matching overview.json schema
            
        Raises:
            FileNotFoundError: If repo_path doesn't exist
            ValueError: If data collection fails
        """
```

### renderOverview()

**File:** `cortex-brain/dashboards/ui/components/overview-tab-v3.js`

```javascript
/**
 * Render Overview tab UI
 * 
 * @param {Object} data - Overview data from overview.json
 * @param {Object} data.overall_health - Overall health object
 * @param {number} data.overall_health.score - Health score 0-100
 * @param {string} data.overall_health.status - Status (healthy|warning|critical)
 * @param {Object} data.key_metrics - Key metrics object
 * @param {number} data.key_metrics.total_files - Total file count
 * @param {Array} data.health_categories - Health category array
 * @param {Array} data.critical_issues - Critical issue array
 * @param {Object} data.composition - Composition object
 * @param {Array} data.composition.languages - Language array
 * 
 * @returns {void}
 */
function renderOverview(data) { ... }
```

---

## Resources

**Related files:**
- Backend: `src/dashboard/data/overview_collector.py`
- Frontend: `cortex-brain/dashboards/ui/components/overview-tab-v3.js`
- Styles: `cortex-brain/dashboards/ui/styles/overview-tab.css`
- Tests: `tests/dashboard/test_overview_integration.py`
- Schema: `overview.json` (in data directories)

**External documentation:**
- [D3.js API Reference](https://d3js.org/api)
- [JSON Schema](https://json-schema.org/)
- [pytest Documentation](https://docs.pytest.org/)

**Support:**
- GitHub Issues: github.com/asifhussain60/CORTEX/issues
- Developer Slack: #cortex-dashboard channel

---

**Last updated:** 2025-12-06 | **Version:** 1.0 | **Maintainer:** CORTEX Team
