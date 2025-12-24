# Dashboard Developer Guide

**Tech Stack Enhancement Dashboard Suite - Developer Reference**  
**Version:** 1.0.0  
**Last Updated:** December 6, 2025  
**Author:** Asif Hussain

---

## Architecture Overview

### Technology Stack

- **Backend**: Python 3.9+, dataclasses, statistics, json
- **Frontend**: Vanilla JavaScript (ES6+), D3.js v7
- **Styling**: CSS3, Flexbox, Grid
- **Testing**: pytest, fixtures, integration tests

### Directory Structure

```
CORTEX/
├── src/dashboard/                    # Backend Python modules
│   ├── dependency_bloat_analyzer.py  # Statistical analysis
│   └── __init__.py
├── static/
│   ├── js/dashboard/                 # Frontend JavaScript
│   │   ├── dependency-bloat-analyzer.js
│   │   ├── framework-health-heatmap.js
│   │   └── migration-roadmap-generator.js
│   └── css/dashboard/                # Stylesheets
│       ├── dependency-bloat-analyzer.css
│       ├── framework-health-heatmap.css
│       └── migration-roadmap-generator.css
└── tests/
    ├── dashboard/                    # Unit tests (159 tests)
    └── integration/                  # Integration tests (17 tests)
```

---

## Backend API Reference

### DependencyBloatAnalyzer

**Location:** `src/dashboard/dependency_bloat_analyzer.py`

**Purpose:** Analyze package count distribution with statistical methods.

**Key Methods:**

```python
class DependencyBloatAnalyzer:
    def __init__(self, tech_stack_path: Optional[str] = None)
    def load_data(self, path: Optional[str] = None) -> Dict[str, Any]
    def extract_package_counts(self, data: Optional[Dict] = None) -> List[Tuple[str, int]]
    def calculate_statistics(self, counts: List[int]) -> Dict[str, float]
    def calculate_bloat_score(self, package_count: int, mean: float, std_dev: float) -> float
    def detect_outliers(self, counts: List[int], threshold: float) -> List[bool]
    def analyze(self, data: Optional[Dict] = None) -> BloatAnalysis
    def export_to_json(self, analysis: BloatAnalysis, output_path: str) -> None
```

**Example Usage:**

```python
from src.dashboard.dependency_bloat_analyzer import DependencyBloatAnalyzer

# Initialize with file path
analyzer = DependencyBloatAnalyzer("tech-stack.json")
analyzer.load_data()

# Or initialize with data dict
analyzer = DependencyBloatAnalyzer()
analysis = analyzer.analyze(tech_stack_data)

# Access results
print(f"Mean: {analysis.mean:.1f} packages")
print(f"Outliers: {len([s for s in analysis.solutions if s.is_outlier])}")

# Export to JSON
analyzer.export_to_json(analysis, "bloat-report.json")
```

**Data Structures:**

```python
@dataclass
class SolutionPackageStats:
    solution_name: str
    package_count: int
    bloat_score: float
    is_outlier: bool
    category: str  # 'critical', 'warning', 'normal'

@dataclass
class BloatAnalysis:
    solutions: List[SolutionPackageStats]
    mean: float
    median: float
    q1: float
    q3: float
    iqr: float
    outlier_threshold: float
    histogram_bins: List[Dict[str, Any]]
    box_plot_data: Dict[str, Any]
    recommendations: List[str]
```

---

## Frontend Component Reference

### DependencyBloatAnalyzer (JavaScript)

**Location:** `static/js/dashboard/dependency-bloat-analyzer.js`

**Purpose:** Render histogram, box plot, and recommendations.

**Initialization:**

```javascript
const analyzer = new DependencyBloatAnalyzer('container-id', techStackData);
```

**Key Methods:**

- `analyzeData()`: Process tech stack data
- `renderStatsSummary()`: Display mean/median/IQR/threshold cards
- `renderHistogram()`: D3.js histogram with 5 bins
- `renderBoxPlot()`: D3.js box plot with quartiles and outliers
- `renderSolutionsTable()`: Top 10 solutions by bloat score
- `renderRecommendations()`: Auto-generated recommendations

**D3.js Scales:**

```javascript
const xScale = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([0, innerWidth])
    .padding(0.2);

const yScale = d3.scaleLinear()
    .domain([0, maxValue * 1.1])
    .range([innerHeight, 0])
    .nice();
```

---

### FrameworkHealthHeatmap (JavaScript)

**Location:** `static/js/dashboard/framework-health-heatmap.js`

**Purpose:** 2D heatmap with weighted health scoring.

**Health Formula:**

```javascript
healthScore = (versionCurrency × 0.25) + (cveScore × 0.30) 
            + (eolStatus × 0.25) + (communityActivity × 0.20)
```

**Color Gradient:**

```javascript
const colorScale = d3.scaleLinear()
    .domain([0, 50, 70, 100])
    .range(['#E74C3C', '#F39C12', '#A8E6A1', '#27AE60']);
```

**Drill-Down Panel:**

```javascript
function showDrillDown(framework, focusFactor) {
    // Display detailed scores, recommendations, migration paths
    panel.select('.overall-score').text(framework.healthScore.toFixed(1));
    panel.select('.factor-breakdown').data(factors).enter()...;
}
```

---

### MigrationRoadmapGenerator (JavaScript)

**Location:** `static/js/dashboard/migration-roadmap-generator.js`

**Purpose:** Generate phased migration timelines.

**Priority Calculation:**

```javascript
priorityScore = (riskScore × 0.5) + (complexityFactor × 0.3) + (eolUrgency × 0.2)
```

**Phase Assignment:**

```javascript
function assignPhases(tasks, maxHoursPerPhase = 160) {
    // Resolve dependencies (.NET 8 before C# 12)
    // Handle large tasks (>160h get dedicated phase)
    // Distribute tasks evenly across phases
}
```

**Timeline Rendering:**

```javascript
const xScale = d3.scaleLinear()
    .domain([0, totalWeeks])
    .range([0, innerWidth]);

const bars = g.selectAll('.phase-bar')
    .data(phases)
    .enter().append('rect')
    .attr('x', d => xScale(d.startWeek))
    .attr('width', d => xScale(d.durationWeeks));
```

---

## Adding New Dashboard Components

### Step 1: Create Backend Module

```python
# src/dashboard/my_analyzer.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MyAnalysisResult:
    metric1: float
    metric2: int
    items: List[str]

class MyAnalyzer:
    def __init__(self, tech_stack_path: str = None):
        self.data = None
    
    def load_data(self, path: str = None) -> Dict[str, Any]:
        # Load and parse JSON
        pass
    
    def analyze(self, data: Dict = None) -> MyAnalysisResult:
        # Perform analysis
        pass
```

### Step 2: Create Frontend Component

```javascript
// static/js/dashboard/my-analyzer.js
class MyAnalyzer {
    constructor(containerId, techStackData) {
        this.container = d3.select(`#${containerId}`);
        this.data = techStackData;
        this.init();
    }
    
    init() {
        this.container.html('');
        this.analyzeData();
        this.render();
    }
    
    analyzeData() {
        // Process data
    }
    
    render() {
        // D3.js visualization
    }
}
```

### Step 3: Create Stylesheet

```css
/* static/css/dashboard/my-analyzer.css */
.my-analyzer {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
    padding: 20px;
}

.my-analyzer-header {
    font-size: 28px;
    margin-bottom: 20px;
}

/* Responsive */
@media (max-width: 768px) {
    .my-analyzer {
        padding: 10px;
    }
}
```

### Step 4: Create Tests

```python
# tests/dashboard/test_my_analyzer.py
import pytest
from src.dashboard.my_analyzer import MyAnalyzer

@pytest.fixture
def sample_data():
    return {"solutions": [...]}

class TestMyAnalyzer:
    def test_analysis_basic(self, sample_data):
        analyzer = MyAnalyzer()
        result = analyzer.analyze(sample_data)
        assert result.metric1 > 0
```

### Step 5: Run Tests

```bash
pytest tests/dashboard/test_my_analyzer.py -v
```

---

## Testing Guidelines

### Unit Tests (per component)

- **Coverage Target**: 90%+
- **Test Classes**: Group by functionality
- **Fixtures**: Reusable test data
- **Edge Cases**: Empty data, single item, large datasets

**Example:**

```python
class TestHistogramBinning:
    def test_bin_assignment(self): ...
    def test_empty_bins(self): ...
    def test_single_solution(self): ...
```

### Integration Tests

- **End-to-end workflows**
- **Cross-component consistency**
- **Performance benchmarks**
- **Error handling**

**Run All Tests:**

```bash
pytest tests/ -v --cov=src/dashboard
```

---

## Performance Optimization

### Backend

1. **Use dataclasses** for structured data (faster than dicts)
2. **Cache calculations** when analyzing multiple times
3. **Stream large files** instead of loading into memory
4. **Profile with cProfile** to identify bottlenecks

### Frontend

1. **Debounce user input** (300ms delay for filters)
2. **Virtual scrolling** for tables >1000 rows
3. **Lazy load visualizations** (IntersectionObserver)
4. **Throttle animations** (60fps cap)
5. **Use requestAnimationFrame** for smooth updates

### D3.js Optimization

```javascript
// BAD: Recreate SVG on every update
container.html('');
container.append('svg')...

// GOOD: Update existing elements
const svg = container.selectAll('svg').data([data]);
svg.enter().append('svg').merge(svg).attr('width', width)...
```

---

## Deployment

### Production Build

```bash
# Minify JavaScript
npx terser static/js/dashboard/*.js -o dist/dashboard.min.js

# Minify CSS
npx csso static/css/dashboard/*.css -o dist/dashboard.min.css

# Optimize images
npx imagemin static/images/* --out-dir=dist/images
```

### CDN Configuration

```html
<link rel="stylesheet" href="https://cdn.example.com/dashboard.min.css">
<script src="https://cdn.example.com/dashboard.min.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ static/ ./
CMD ["python", "-m", "http.server", "8080"]
```

---

## Troubleshooting Development Issues

### Issue: Tests Failing Locally

```bash
# Clear pytest cache
rm -rf .pytest_cache __pycache__

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run with verbose output
pytest tests/dashboard/ -vv
```

### Issue: D3.js Not Rendering

1. Check browser console for errors
2. Verify D3.js version (v7 required)
3. Ensure container element exists before init
4. Check data format matches expected structure

### Issue: Linting Errors

```bash
# Python (flake8)
flake8 src/dashboard/ --max-line-length=120

# JavaScript (ESLint)
eslint static/js/dashboard/ --fix
```

---

## API Versioning

**Current Version**: 1.0.0 (Semantic Versioning)

- **Major**: Breaking changes to API or data format
- **Minor**: New features, backward-compatible
- **Patch**: Bug fixes, no new features

**Deprecation Policy**: 6 months notice before removing features

---

## Contributing

1. Fork repository
2. Create feature branch (`feature/my-feature`)
3. Write tests (maintain 90%+ coverage)
4. Run linters and tests
5. Submit pull request with description

---

**Developer Support:**  
Contact: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX
