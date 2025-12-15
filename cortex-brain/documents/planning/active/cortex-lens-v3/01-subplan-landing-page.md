# CORTEX Lens V3 - Sub-Plan 1: Landing Page/Home View

**Version:** 1.0  
**Date:** December 14, 2025  
**Author:** Asif Hussain  
**Status:** 🚀 IN PROGRESS  
**Parent Plan:** CORTEX-LENS-V3-MASTER-SUBPLAN.md  
**Template:** Console App (`src/cortex_lens/templates/console_app/`)

---

## 🎯 Scope Definition

### View Overview
**Landing Page/Home View** - First impression when dashboard loads

**Purpose:** Provide immediate high-level insights through KPI cards and health overview

**User Story:**
> As a developer opening a CORTEX Lens dashboard, I want to immediately see repository health and key metrics so I can quickly assess project status.

### Components to Build

1. **Dashboard Header** (Already exists in base template)
   - Repository name display
   - Scan timestamp
   - CORTEX branding
   - Theme toggle button (dark/light)

2. **Navigation Sidebar** (Already exists)
   - Tab list with icons
   - Active tab highlighting
   - Smooth transitions

3. **KPI Scorecard** (PRIMARY FOCUS)
   - 4-6 metric cards with glassmorphism styling
   - Large emoji icons (64px)
   - Metric value + label
   - Trend indicators (↑/↓)
   - Color coding by health (green/yellow/red)

4. **Health Radar Chart** (PRIMARY FOCUS)
   - 5-axis radar showing overall health
   - Axes: Code Quality, Test Coverage, Documentation, Security, Architecture
   - Interactive hover (show exact scores)
   - Color gradients (green → yellow → red)

5. **Quick Stats Grid** (SECONDARY)
   - File count, LOC, language distribution
   - Entry points count
   - Dependency count
   - Test count

### Data Requirements

**Input Data (from `analysisData` JSON):**
```javascript
{
  metadata: {
    repo_name: "CORTEX",
    scan_timestamp: "2025-12-14T08:30:00Z",
    total_files: 1247,
    total_loc: 45823,
    languages: {python: 65.2, javascript: 25.3, sql: 9.5}
  },
  health: {
    overall_score: 85,
    code_quality_score: 78,
    test_coverage_score: 71,
    documentation_score: 82,
    security_score: 90,
    architecture_score: 88
  },
  architecture: {
    entry_points: ["src/main.py", "scripts/cli.py"],
    layers: 4,
    commands: 12
  },
  dependencies: {
    total_count: 47,
    outdated_count: 3
  },
  testing: {
    total_tests: 327,
    passing_tests: 304,
    coverage_percentage: 69
  }
}
```

### Dependencies
- **Base Template:** `templates/base/cortex-unified.css` (glassmorphism)
- **JavaScript:** `templates/base/cortex-unified.js` (tab system)
- **Chart Library:** Chart.js (already included, for radar chart)
- **Component Library:** `templates/base/components/cortex-components.js` (KPIScorecard)

---

## 🧪 TDD Implementation Plan

### RED Phase: Write Failing Tests

#### Test 1: KPI Cards Rendering
```python
# tests/test_landing_page.py
def test_kpi_cards_rendered(dashboard_html):
    """Verify all KPI cards are present on landing page."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Should have 6 KPI cards
    kpi_cards = soup.find_all('div', class_='kpi-card')
    assert len(kpi_cards) == 6
    
    # Cards should have: icon, value, label, trend
    for card in kpi_cards:
        assert card.find('div', class_='kpi-icon')
        assert card.find('div', class_='kpi-value')
        assert card.find('div', class_='kpi-label')

def test_kpi_values_from_analysis_data(dashboard_html):
    """Verify KPI cards show correct data."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Overall health score should match
    health_card = soup.find('div', {'data-kpi': 'overall-health'})
    assert '85' in health_card.find('div', class_='kpi-value').text
    
    # Total files should match
    files_card = soup.find('div', {'data-kpi': 'total-files'})
    assert '1,247' in files_card.find('div', class_='kpi-value').text

def test_kpi_color_coding(dashboard_html):
    """Verify KPI cards have correct health color classes."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Score 85 should be 'excellent' (green)
    health_card = soup.find('div', {'data-kpi': 'overall-health'})
    assert 'kpi-excellent' in health_card['class']
    
    # Score 71 should be 'good' (yellow-green)
    coverage_card = soup.find('div', {'data-kpi': 'test-coverage'})
    assert 'kpi-good' in coverage_card['class']
```

#### Test 2: Health Radar Chart
```python
def test_health_radar_chart_exists(dashboard_html):
    """Verify health radar chart canvas is rendered."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Canvas for Chart.js
    canvas = soup.find('canvas', id='healthRadarChart')
    assert canvas is not None
    
def test_health_radar_data_injection(dashboard_html):
    """Verify radar chart gets correct health scores."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Check inline script with Chart.js initialization
    script = soup.find('script', string=re.compile('healthRadarChart'))
    assert 'Code Quality' in script.string
    assert '78' in script.string  # code_quality_score
    assert '71' in script.string  # test_coverage_score
    assert '82' in script.string  # documentation_score
```

#### Test 3: Glassmorphism Styling
```python
def test_glassmorphism_applied(dashboard_html):
    """Verify glassmorphism CSS classes are used."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    kpi_cards = soup.find_all('div', class_='kpi-card')
    for card in kpi_cards:
        # Should have glass-card class
        assert 'glass-card' in card.get('class', [])

def test_no_inline_styles(dashboard_html):
    """Verify no inline CSS (design system compliance)."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    # Check KPI cards don't have style attribute
    kpi_cards = soup.find_all('div', class_='kpi-card')
    for card in kpi_cards:
        assert card.get('style') is None or card.get('style') == ''
```

#### Test 4: Interactive Features
```python
def test_theme_toggle_button(dashboard_html):
    """Verify theme toggle button exists and functions."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    toggle_btn = soup.find('button', id='themeToggle')
    assert toggle_btn is not None
    assert 'onclick' in toggle_btn.attrs or 'data-action' in toggle_btn.attrs

def test_sidebar_navigation(dashboard_html):
    """Verify sidebar has all tab links."""
    soup = BeautifulSoup(dashboard_html, 'html.parser')
    
    sidebar = soup.find('nav', class_='sidebar')
    tab_links = sidebar.find_all('a', class_='tab-link')
    
    # Console app has 5 tabs
    assert len(tab_links) == 5
    
    # First tab should be active by default
    assert 'active' in tab_links[0].get('class', [])
```

### GREEN Phase: Implement Minimal Working View

#### Step 1: Update Console App Index Template
```html
<!-- src/cortex_lens/templates/console_app/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ repo_name }} - CORTEX Lens</title>
    <link rel="stylesheet" href="../base/cortex-unified.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="dark-theme">
    <!-- Header -->
    <header class="dashboard-header glass-card">
        <div class="header-content">
            <h1>🔍 {{ repo_name }}</h1>
            <div class="header-meta">
                <span>📅 {{ scan_date }}</span>
                <button id="themeToggle" class="btn-theme-toggle" onclick="toggleTheme()">
                    🌙 Toggle Theme
                </button>
            </div>
        </div>
    </header>

    <div class="dashboard-layout">
        <!-- Sidebar -->
        <nav class="sidebar glass-card">
            <ul class="tab-list">
                <li><a href="#overview" class="tab-link active" data-tab="overview">
                    📊 Overview
                </a></li>
                <li><a href="#architecture" class="tab-link" data-tab="architecture">
                    🏗️ Architecture
                </a></li>
                <li><a href="#quality" class="tab-link" data-tab="quality">
                    ✨ Code Quality
                </a></li>
                <li><a href="#dependencies" class="tab-link" data-tab="dependencies">
                    📦 Dependencies
                </a></li>
                <li><a href="#testing" class="tab-link" data-tab="testing">
                    🧪 Testing
                </a></li>
            </ul>
        </nav>

        <!-- Main Content -->
        <main class="main-content">
            <!-- OVERVIEW TAB (Landing Page) -->
            <section id="overview" class="tab-content active">
                <h2 class="tab-title">📊 Repository Overview</h2>
                
                <!-- KPI Scorecard Grid -->
                <div class="kpi-grid">
                    <!-- Overall Health -->
                    <div class="kpi-card glass-card kpi-{{ overall_health_class }}" 
                         data-kpi="overall-health">
                        <div class="kpi-icon">💚</div>
                        <div class="kpi-value">{{ overall_score }}</div>
                        <div class="kpi-label">Overall Health</div>
                        <div class="kpi-trend">{{ overall_trend }}</div>
                    </div>

                    <!-- Total Files -->
                    <div class="kpi-card glass-card" data-kpi="total-files">
                        <div class="kpi-icon">📁</div>
                        <div class="kpi-value">{{ total_files }}</div>
                        <div class="kpi-label">Total Files</div>
                    </div>

                    <!-- Lines of Code -->
                    <div class="kpi-card glass-card" data-kpi="total-loc">
                        <div class="kpi-icon">📝</div>
                        <div class="kpi-value">{{ total_loc }}</div>
                        <div class="kpi-label">Lines of Code</div>
                    </div>

                    <!-- Test Coverage -->
                    <div class="kpi-card glass-card kpi-{{ coverage_class }}" 
                         data-kpi="test-coverage">
                        <div class="kpi-icon">🧪</div>
                        <div class="kpi-value">{{ coverage_percentage }}%</div>
                        <div class="kpi-label">Test Coverage</div>
                        <div class="kpi-trend">{{ coverage_trend }}</div>
                    </div>

                    <!-- Security Score -->
                    <div class="kpi-card glass-card kpi-{{ security_class }}" 
                         data-kpi="security-score">
                        <div class="kpi-icon">🔒</div>
                        <div class="kpi-value">{{ security_score }}</div>
                        <div class="kpi-label">Security Score</div>
                    </div>

                    <!-- Dependencies -->
                    <div class="kpi-card glass-card" data-kpi="dependencies">
                        <div class="kpi-icon">📦</div>
                        <div class="kpi-value">{{ dependency_count }}</div>
                        <div class="kpi-label">Dependencies</div>
                        <div class="kpi-sublabel">{{ outdated_count }} outdated</div>
                    </div>
                </div>

                <!-- Health Radar Chart -->
                <div class="chart-container glass-card">
                    <h3>🎯 Health Metrics</h3>
                    <canvas id="healthRadarChart" width="600" height="400"></canvas>
                </div>

                <!-- Quick Stats Grid -->
                <div class="stats-grid">
                    <div class="stat-item glass-card">
                        <div class="stat-icon">🐍</div>
                        <div class="stat-label">Primary Language</div>
                        <div class="stat-value">{{ primary_language }} ({{ primary_language_pct }}%)</div>
                    </div>
                    <div class="stat-item glass-card">
                        <div class="stat-icon">🚀</div>
                        <div class="stat-label">Entry Points</div>
                        <div class="stat-value">{{ entry_point_count }}</div>
                    </div>
                    <div class="stat-item glass-card">
                        <div class="stat-icon">✅</div>
                        <div class="stat-label">Tests Passing</div>
                        <div class="stat-value">{{ passing_tests }}/{{ total_tests }}</div>
                    </div>
                    <div class="stat-item glass-card">
                        <div class="stat-icon">🏗️</div>
                        <div class="stat-label">Architecture Layers</div>
                        <div class="stat-value">{{ layer_count }}</div>
                    </div>
                </div>
            </section>

            <!-- OTHER TABS (Placeholder for now) -->
            <section id="architecture" class="tab-content">
                <h2 class="tab-title">🏗️ Architecture</h2>
                <p>Architecture visualization coming soon...</p>
            </section>

            <section id="quality" class="tab-content">
                <h2 class="tab-title">✨ Code Quality</h2>
                <p>Code quality metrics coming soon...</p>
            </section>

            <section id="dependencies" class="tab-content">
                <h2 class="tab-title">📦 Dependencies</h2>
                <p>Dependency analysis coming soon...</p>
            </section>

            <section id="testing" class="tab-content">
                <h2 class="tab-title">🧪 Testing</h2>
                <p>Testing metrics coming soon...</p>
            </section>
        </main>
    </div>

    <!-- Data Injection -->
    <script>
        const analysisData = {{ analysis_data_json }};
    </script>

    <!-- Main JavaScript -->
    <script src="../base/cortex-unified.js"></script>
    <script>
        // Initialize Health Radar Chart
        const ctx = document.getElementById('healthRadarChart').getContext('2d');
        const healthRadarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Code Quality', 'Test Coverage', 'Documentation', 'Security', 'Architecture'],
                datasets: [{
                    label: 'Health Scores',
                    data: [
                        analysisData.health.code_quality_score,
                        analysisData.health.test_coverage_score,
                        analysisData.health.documentation_score,
                        analysisData.health.security_score,
                        analysisData.health.architecture_score
                    ],
                    backgroundColor: 'rgba(0, 212, 255, 0.2)',
                    borderColor: 'rgba(0, 212, 255, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(0, 212, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(0, 212, 255, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: '#888',
                            backdropColor: 'transparent'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: '#fff',
                            font: {
                                size: 14
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    </script>
</body>
</html>
```

#### Step 2: Update Dashboard Builder Variable Extraction
```python
# src/cortex_lens/generators/dashboard_builder.py (modify _extract_template_variables)

def _extract_template_variables(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract variables for template injection with enhanced KPI support."""
    
    metadata = analysis_data.get('metadata', {})
    health = analysis_data.get('health', {})
    architecture = analysis_data.get('architecture', {})
    dependencies = analysis_data.get('dependencies', {})
    testing = analysis_data.get('testing', {})
    
    # Helper functions
    def get_score_class(score):
        if score >= 80: return 'excellent'
        if score >= 60: return 'good'
        if score >= 40: return 'fair'
        return 'poor'
    
    def format_number(num):
        return f"{num:,}"
    
    # Extract all variables
    variables = {
        # Metadata
        'repo_name': metadata.get('repo_name', 'Unknown'),
        'scan_date': metadata.get('scan_timestamp', '').split('T')[0],
        'total_files': format_number(metadata.get('total_files', 0)),
        'total_loc': format_number(metadata.get('total_loc', 0)),
        
        # Health KPIs
        'overall_score': health.get('overall_score', 0),
        'overall_health_class': get_score_class(health.get('overall_score', 0)),
        'overall_trend': '↑' if health.get('overall_score', 0) > 75 else '↓',
        
        'coverage_percentage': testing.get('coverage_percentage', 0),
        'coverage_class': get_score_class(testing.get('coverage_percentage', 0)),
        'coverage_trend': '↑' if testing.get('coverage_percentage', 0) > 70 else '→',
        
        'security_score': health.get('security_score', 0),
        'security_class': get_score_class(health.get('security_score', 0)),
        
        # Dependencies
        'dependency_count': dependencies.get('total_count', 0),
        'outdated_count': dependencies.get('outdated_count', 0),
        
        # Architecture
        'entry_point_count': len(architecture.get('entry_points', [])),
        'layer_count': len(architecture.get('layers', [])),
        
        # Testing
        'total_tests': testing.get('total_tests', 0),
        'passing_tests': testing.get('passing_tests', 0),
        
        # Language
        'primary_language': list(metadata.get('languages', {}).keys())[0] if metadata.get('languages') else 'Python',
        'primary_language_pct': list(metadata.get('languages', {}).values())[0] if metadata.get('languages') else 100,
        
        # JSON for JavaScript
        'analysis_data_json': json.dumps(analysis_data, indent=2)
    }
    
    return variables
```

#### Step 3: Add CSS for Landing Page Components
```css
/* src/cortex_lens/templates/base/cortex-unified.css (add to existing file) */

/* KPI Scorecard Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 48px;
}

.kpi-card {
    padding: 32px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.kpi-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
}

.kpi-icon {
    font-size: 64px;
    margin-bottom: 16px;
}

.kpi-value {
    font-size: 48px;
    font-weight: 700;
    color: #00d4ff;
    margin-bottom: 8px;
}

.kpi-label {
    font-size: 18px;
    font-weight: 600;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-trend {
    font-size: 24px;
    margin-top: 8px;
}

.kpi-sublabel {
    font-size: 14px;
    color: #888;
    margin-top: 4px;
}

/* Health Color Classes */
.kpi-excellent .kpi-value {
    color: #00ff88;
}

.kpi-good .kpi-value {
    color: #ffaa00;
}

.kpi-fair .kpi-value {
    color: #ff8800;
}

.kpi-poor .kpi-value {
    color: #ff4444;
}

/* Chart Container */
.chart-container {
    padding: 48px;
    margin-bottom: 48px;
}

.chart-container h3 {
    font-size: 32px;
    margin-bottom: 32px;
    text-align: center;
}

.chart-container canvas {
    max-width: 600px;
    margin: 0 auto;
    display: block;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
}

.stat-item {
    padding: 24px;
    text-align: center;
}

.stat-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.stat-label {
    font-size: 14px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #00d4ff;
}
```

### REFACTOR Phase: Design System Compliance

#### Refactoring Checklist
- [ ] Extract repeated CSS into reusable classes
- [ ] Ensure all glassmorphism values match design system specs
- [ ] Remove any inline styles
- [ ] Add CSS custom properties for theme colors
- [ ] Optimize chart rendering performance
- [ ] Add accessibility attributes (aria-labels, role)
- [ ] Validate responsive breakpoints (mobile, tablet, desktop)

---

## 📱 Mock Review Phase (Interactive Development)

### IMPORTANT: Live Server Workflow

**All development happens with live server running:**

1. **Start Server:** `.\cortex-lens-output\serve-landing.ps1`
2. **Browser Opens:** Automatic at http://localhost:8000
3. **Edit Files:** Modify HTML/CSS/JS in `cortex-lens-output\mock-landing\`
4. **See Changes:** Press F5 in browser
5. **Iterate:** Real-time feedback loop with user
6. **Stop Server:** Ctrl+C when done

### Generate Mock Dashboard

#### Step 1: Mock Data (Already Embedded)
```javascript
// Already in index.html - no separate file needed
const MOCK_LANDING_DATA = {
    "metadata": {
        "repo_name": "CORTEX",
        "scan_timestamp": "2025-12-14T08:30:00Z",
        "total_files": 1247,
        "total_loc": 45823,
        "languages": {"Python": 65.2, "JavaScript": 25.3, "SQL": 9.5}
    },
    "health": {
        "overall_score": 85,
        "code_quality_score": 78,
        "test_coverage_score": 71,
        "documentation_score": 82,
        "security_score": 90,
        "architecture_score": 88
    },
    "architecture": {
        "entry_points": ["src/main.py", "scripts/cli.py"],
        "layers": ["tier0", "tier1", "tier2", "tier3"],
        "commands": 12
    },
    "dependencies": {
        "total_count": 47,
        "outdated_count": 3
    },
    "testing": {
        "total_tests": 327,
        "passing_tests": 304,
        "coverage_percentage": 69
    }
}
```

#### Step 2: Files Created (✅ Complete)
```
cortex-lens-output/
├── serve-landing.ps1           # ✅ Live server script
└── mock-landing/
    ├── index.html              # ✅ Landing page HTML
    └── assets/
        ├── cortex-unified.css  # ✅ Admin dashboard styles
        └── cortex-unified.js   # ✅ Tab system + theme toggle
```

**Status:** All files created and ready for interactive development

#### Step 3: Start Live Development Server
```powershell
# Navigate to CORTEX root
cd D:\PROJECTS\CORTEX

# Start live server (opens browser automatically)
.\cortex-lens-output\serve-landing.ps1

# Server will:
# - Serve on http://localhost:8000
# - Open browser automatically
# - Allow F5 refresh to see changes
# - Keep running in PowerShell window

# KEEP THIS WINDOW OPEN FOR LIVE DEVELOPMENT
```

**Interactive Development Workflow:**
1. Server starts → Browser opens automatically
2. Edit files in `cortex-lens-output\mock-landing\`
3. Press F5 in browser to see changes
4. Iterate with user feedback
5. Ctrl+C to stop server when done

### User Review Checklist

#### Visual Design
- [ ] **Glassmorphism:** Cards have semi-transparent background with blur?
- [ ] **Typography:** Large headings (32-48px), readable body (18px)?
- [ ] **Icons:** Emoji icons are 64px and visually impactful?
- [ ] **Spacing:** Generous padding (32px cards, 24px gaps)?
- [ ] **Colors:** Primary cyan (#00d4ff) used consistently?

#### KPI Cards
- [ ] **Layout:** 6 cards in responsive grid?
- [ ] **Content:** Icon, value, label all visible?
- [ ] **Color Coding:** Health scores show correct colors (green/yellow/red)?
- [ ] **Hover Effect:** Cards lift on hover with smooth animation?
- [ ] **Trends:** Trend indicators (↑/↓) make sense?

#### Health Radar Chart
- [ ] **Rendering:** Chart displays without errors?
- [ ] **Data:** 5 axes showing correct scores?
- [ ] **Colors:** Cyan theme matching design system?
- [ ] **Interactivity:** Hover shows tooltips with exact values?
- [ ] **Labels:** Axis labels readable and positioned correctly?

#### Navigation
- [ ] **Sidebar:** All 5 tabs listed?
- [ ] **Active State:** First tab (Overview) highlighted?
- [ ] **Click:** Tab switching works smoothly?
- [ ] **Theme Toggle:** Dark/light mode switches correctly?

#### Performance
- [ ] **Load Time:** Dashboard loads in <5 seconds?
- [ ] **Rendering:** No visible layout shifts during load?
- [ ] **Smooth:** Animations and transitions feel fluid (60fps)?

### Feedback Capture Form

**Reviewer:** [User Name]  
**Date:** [Review Date]  
**Dashboard Version:** Sub-Plan 1 - Landing Page v1.0

**What Works Well:**
```
[List positive aspects]
```

**Issues Found:**
```
Issue 1: [Description]
  - Severity: [Critical/Major/Minor]
  - Screenshot: [Attach if applicable]
  - Suggested Fix: [How to resolve]

Issue 2: ...
```

**Improvement Suggestions:**
```
[List enhancements]
```

**Approval Decision:**
- [ ] ✅ APPROVED - Proceed to next sub-plan
- [ ] 🔄 REVISE - Need changes (list in issues)
- [ ] ❌ REJECT - Major redesign required

---

## 🔗 Integration Steps

### Once User Approves

#### Step 1: Run Full Test Suite
```bash
# Unit tests for landing page
pytest tests/test_landing_page.py -v

# Integration tests (Selenium)
pytest tests/test_dashboard_rendering.py::TestAssetLoading -v
pytest tests/test_dashboard_rendering.py::TestStylingRendering -v

# Overall test suite
pytest tests/test_dashboard_rendering.py -v --html=test-report.html
```

**Expected Results:**
- ✅ All unit tests passing (8/8)
- ✅ Selenium tests passing (21/22, 1 xfail expected)
- ✅ No console errors in browser
- ✅ Load time <5 seconds

#### Step 2: Git Checkpoint
```bash
git add src/cortex_lens/templates/console_app/index.html
git add src/cortex_lens/templates/base/cortex-unified.css
git add src/cortex_lens/generators/dashboard_builder.py
git add tests/test_landing_page.py

git commit -m "feat(lens): Sub-Plan 1 - Landing Page/Home View complete

- Implemented KPI scorecard with 6 metric cards
- Added health radar chart (Chart.js, 5 axes)
- Enhanced glassmorphism styling (admin dashboard aesthetic)
- Created quick stats grid with 4 items
- Added responsive layout (mobile/tablet/desktop)
- Tests: 8/8 unit tests passing, 21/22 Selenium passing

User Approval: ✅ [User Name] - [Date]
Next: Sub-Plan 2 - Executive Brief Tab"
```

#### Step 3: Update Progress Tracker
```bash
# Update CORTEX-LENS-V3-MASTER-SUBPLAN.md progress table
# Change Sub-Plan 1 status to ✅ Complete
# Add completion date
# Update overall progress bar
```

#### Step 4: Create Next Sub-Plan File
```bash
# Generate Sub-Plan 2 document
# Copy template structure
# Define Executive Brief tab scope
```

---

## 📝 Lessons Learned

### What Worked Well
```
[To be filled after implementation]

Example:
- Chart.js integration was straightforward
- KPI card grid layout responsive by default
- Glassmorphism styling applied cleanly
```

### What Could Improve
```
[To be filled after implementation]

Example:
- KPI color coding logic needed refinement
- Radar chart labels overlapped at small screen sizes
- Theme toggle button positioning unclear
```

### Insights for Next Sub-Plan
```
[To be filled after implementation]

Example:
- Need to pre-load narrative data for Executive Brief tab
- Consider lazy-loading charts for performance
- Standardize card hover effects across all tabs
```

---

## 🎯 Success Criteria

### Mandatory (Must Pass)
- ✅ All 8 unit tests passing
- ✅ Selenium tests passing (21/22 minimum)
- ✅ No inline styles (design system compliance)
- ✅ Load time <5 seconds
- ✅ User approval obtained

### Optional (Nice to Have)
- ⭐ KPI cards show trend over time (not just current)
- ⭐ Health radar chart interactive (click axis → drill-down)
- ⭐ Quick stats grid sortable/filterable
- ⭐ Export landing page as PNG image

### Blocker Issues (Would Fail Approval)
- ❌ KPI cards not rendering
- ❌ Chart.js throws errors
- ❌ Glassmorphism not applied
- ❌ Layout broken on mobile
- ❌ Data not injected correctly

---

## 🔗 Related Files

- **Template:** `src/cortex_lens/templates/console_app/index.html`
- **Styles:** `src/cortex_lens/templates/base/cortex-unified.css`
- **JavaScript:** `src/cortex_lens/templates/base/cortex-unified.js`
- **Builder:** `src/cortex_lens/generators/dashboard_builder.py`
- **Mock Implementation:** `cortex-lens-output/mock-landing/`
- **Test Suite:** `cortex-lens-output/mock-landing/tests/landing-page.test.js` ✅ CREATED
- **Test Runner:** `cortex-lens-output/mock-landing/tests/test-runner.html` ✅ CREATED
- **Mock Data:** Embedded in `index.html` (analysisData object)

---

## 🧪 Test Harness (MANDATORY TDD)

### Test Suite Coverage

**File:** `cortex-lens-output/mock-landing/tests/landing-page.test.js`

**Test Suites (5 categories, 30+ assertions):**

1. **HTML Structure Tests**
   - ✅ Header element exists
   - ✅ Logo-sidebar container exists and is fixed position
   - ✅ CORTEX logo exists with 150px width
   - ✅ Sidebar navigation exists
   - ✅ Tab list has no bullets (list-style: none)
   - ✅ 5 navigation tabs exist
   - ✅ Main content area exists
   - ✅ Main content has 280px left margin
   - ✅ KPI grid exists
   - ✅ 6 KPI cards exist
   - ✅ Health chart canvas exists

2. **Layout Behavior Tests**
   - ✅ Sidebar spans full viewport height (calc(100vh - 80px))
   - ✅ Main content is scrollable (height > viewport)
   - ✅ Sidebar remains fixed during scroll
   - ✅ No dashboard-layout wrapper exists (grid conflict removed)

3. **CSS Styling Tests**
   - ✅ Glass cards have backdrop-filter blur
   - ✅ Logo has drop-shadow effect
   - ✅ KPI cards have min-height >= 200px
   - ✅ Theme toggle button exists
   - ✅ Valid theme applied (dark or light)

4. **Responsiveness Tests**
   - ✅ KPI grid uses CSS Grid display
   - ✅ Tab links use flexbox
   - ✅ Responsive media queries defined

5. **JavaScript Functionality Tests**
   - ✅ toggleTheme function exists
   - ✅ Tab switching updates active class
   - ✅ One tab content is active at a time
   - ✅ analysisData object exists
   - ✅ analysisData has health and metadata properties
   - ✅ Health score is defined
   - ✅ Chart.js library is loaded

### Running Tests

**Open in Browser:**
```bash
# Navigate to test runner
cd cortex-lens-output/mock-landing/tests
# Open test-runner.html in browser
```

**Expected Output:**
```
📋 Testing HTML Structure...
✅ Header element exists
✅ Logo-sidebar container exists
✅ Logo-sidebar container is position: fixed
✅ CORTEX logo exists
✅ Logo width is 150px
✅ Sidebar navigation exists
✅ Tab list has no bullets
✅ 5 navigation tabs exist
✅ Main content area exists
✅ Main content has 280px left margin
✅ KPI grid exists
✅ 6 KPI cards exist
✅ Health chart canvas exists

📐 Testing Layout Behavior...
✅ Sidebar spans full viewport height
✅ Main content is scrollable (height > viewport)
✅ Sidebar remains fixed during scroll
✅ No dashboard-layout wrapper exists

🎨 Testing CSS Styling...
✅ Glass cards exist in DOM
✅ Glass cards have backdrop-filter blur
✅ Logo has drop-shadow effect
✅ KPI cards have min-height >= 200px
✅ Theme toggle button exists
✅ Valid theme is applied

📱 Testing Responsiveness...
✅ KPI grid uses CSS Grid
✅ Tab links use flexbox
✅ Responsive media queries defined

⚙️ Testing JavaScript Functionality...
✅ toggleTheme function exists
✅ Tab switching updates active class
✅ One tab content is active
✅ analysisData object exists
✅ analysisData has health and metadata properties
✅ Health score is defined in analysisData
✅ Chart.js library is loaded

==================================================
📊 TEST RESULTS SUMMARY
==================================================
Total Tests: 30+
✅ Passed: 30+
❌ Failed: 0
Pass Rate: 100.0%
```

### Test Maintenance

**When to Update Tests:**
1. Layout changes (sidebar width, spacing, positioning)
2. New components added (KPI cards, charts, sections)
3. CSS changes (colors, effects, responsiveness)
4. JavaScript changes (functions, event handlers, animations)
5. Bug fixes (add regression test for each bug)

**Test Failure Protocol:**
1. ❌ Test fails → Stop development
2. 🔍 Investigate root cause
3. 🔧 Fix code OR update test (if requirements changed)
4. ✅ Verify all tests pass
5. 📝 Document change in lessons learned

---

## 🚀 Next Action

**Current Status:** ✅ COMPLETE - Test harness created  
**Estimated Time:** ~~4-6 hours~~ **COMPLETED**  
**Assigned To:** Asif Hussain

**Implementation Status:**
1. ✅ Write failing tests (RED phase) - Complete
2. ✅ Implement landing page HTML - Complete
3. ✅ Add CSS for KPI/chart/stats - Complete  
4. ✅ Fix layout structure (remove grid conflict) - Complete
5. ✅ Generate mock dashboard - Complete
6. ✅ Create test harness - Complete
7. ⏳ User review cycle - IN PROGRESS
8. ⏳ Integration and git checkpoint - PENDING

**Remaining Work:**
- User approval of design
- Git checkpoint with test suite
- Update progress in master sub-plan

---

**Last Updated:** December 14, 2025  
**Sub-Plan Status:** ✅ IMPLEMENTED + TESTED  
**User Approval:** ⏳ AWAITING REVIEW
