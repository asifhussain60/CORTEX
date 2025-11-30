# 📚 Onboarding Dashboard - User Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** November 30, 2025

---

## 🎯 Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Dashboard Features](#dashboard-features)
4. [Tab-by-Tab Guide](#tab-by-tab-guide)
5. [Export Options](#export-options)
6. [Performance Features](#performance-features)
7. [Accessibility](#accessibility)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## 📖 Introduction

The CORTEX Onboarding Dashboard is a comprehensive visualization tool that provides security, architecture, and testing insights for your projects. It features:

- **5 Interactive Tabs:** Security, Architecture, Integration, Testing, UML Diagrams
- **Real-time Metrics:** Live project statistics and health indicators
- **Professional UI:** WCAG 2.1 AA compliant, mobile-responsive design
- **Export Capabilities:** PowerPoint presentations for stakeholders
- **Performance Optimized:** Caching, lazy loading, and efficient rendering

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install dependencies
pip install -r requirements.txt

# Optional: Install PPTX export support
pip install python-pptx
```

### Generate Your First Dashboard

```python
from src.dashboard.use_cases.generate_dashboard import generate_dashboard

# Generate dashboard for your project
dashboard_html = generate_dashboard(
    project_path="/path/to/your/project",
    output_path="dashboard.html"
)

print(f"Dashboard created: {dashboard_html}")
```

### View in Browser

```bash
# Open the generated HTML file
open dashboard.html  # macOS
xdg-open dashboard.html  # Linux
start dashboard.html  # Windows
```

---

## ✨ Dashboard Features

### Security Tab 🔒

**Purpose:** Validate OWASP security compliance and input/output handling

**Features:**
- **Input Validation Status:** Shows validation coverage for user inputs
- **Output Encoding:** XSS prevention with HTML entity encoding
- **OWASP Compliance:** Detailed checklist with pass/fail indicators
- **Security Metrics:** Vulnerability counts and remediation status

**Example Insights:**
- ✅ All user inputs validated
- ⚠️ 2 endpoints missing output encoding
- ❌ SQL injection vulnerability detected in `user_service.py`

---

### Architecture Tab 🏗️

**Purpose:** Visualize clean architecture layers and UML class diagrams

**Features:**
- **Layer Overview:** Domain, Data, Use Cases, Presentation layers
- **Dependency Graph:** Shows relationships between modules
- **UML Class Diagrams:** Auto-generated from Python source code
- **Component Health:** Color-coded health indicators (🟢🟡🔴)

**Sub-tabs:**
1. **Overview:** High-level architecture summary
2. **Layers:** Detailed layer breakdown
3. **UML Diagrams:** Interactive class diagrams (zoom, pan, search)

**Example Insights:**
- 🏗️ 4 layers identified: Domain, Data, Use Cases, Presentation
- ✅ No circular dependencies detected
- 📊 15 domain entities, 8 repositories, 12 use cases

---

### Integration Tab 🔌

**Purpose:** Monitor API integrations and external service connections

**Features:**
- **Active Integrations:** List of connected services
- **Health Checks:** Real-time status monitoring
- **Error Logs:** Recent integration failures
- **Performance Metrics:** Response times and success rates

**Example Insights:**
- ✅ Database: Healthy (5ms avg response)
- ⚠️ Payment Gateway: Slow (350ms avg response)
- ❌ Email Service: Down (last success 2h ago)

---

### Testing Tab ✅

**Purpose:** Test coverage analysis and quality metrics

**Features:**
- **Test Summary:** Total tests, passing/failing counts
- **Coverage Report:** Line, branch, and function coverage
- **Test Types:** Unit, integration, end-to-end breakdown
- **Recent Failures:** Details on failing tests with stack traces

**Example Insights:**
- ✅ 149/149 tests passing (100%)
- 📊 92% line coverage (target: 80%)
- ⏱️ Average test duration: 1.2s

---

### UML Diagrams Tab 📊

**Purpose:** Visualize code structure with auto-generated UML diagrams

**Features:**
- **Class Diagrams:** Methods, attributes, inheritance
- **Interactive Controls:** Zoom in/out, pan, search classes
- **Export:** Download as SVG or PNG
- **Lazy Loading:** Fast rendering for large codebases

**Controls:**
- **Zoom In/Out:** `+` and `-` buttons or mouse wheel
- **Pan:** Click and drag
- **Search:** Find specific classes by name
- **Export:** Download SVG (vector) or PNG (raster)

**Example Insights:**
- 📦 45 classes visualized
- 🔗 23 inheritance relationships
- 📊 avg 6.4 methods per class

---

## 💾 Export Options

### PowerPoint Export

Export dashboard as a professional PowerPoint presentation:

```python
from src.dashboard.use_cases.export_pptx import export_dashboard_to_pptx

# Export to PPTX
pptx_path = export_dashboard_to_pptx(
    dashboard_data=your_dashboard_data,
    output_path="dashboard_report.pptx"
)

print(f"Presentation created: {pptx_path}")
```

**Slides Included:**
1. Title slide with project metadata
2. Overview metrics
3. Security foundation
4. Architecture layers
5. Integration status
6. Test coverage
7. Summary and key achievements

**Customization:**

```python
from src.dashboard.use_cases.export_pptx import PPTXExportConfig

config = PPTXExportConfig(
    title="My Project Dashboard",
    subtitle="Q4 2025 Security Review",
    author="Your Name",
    primary_color=(0, 102, 204),  # RGB
    include_charts=True,
    include_tables=True
)

export_dashboard_to_pptx(dashboard_data, config=config)
```

---

## ⚡ Performance Features

### Caching

**Server-Side Caching:**
- 24-hour TTL (Time To Live)
- Automatic cache invalidation on data changes
- LRU eviction for memory management
- 80-95% cache hit rate expected

**Client-Side Caching:**
- 30-minute browser cache
- 50MB cache limit
- LocalStorage persistence
- Automatic cleanup

**Performance Impact:**
- Before: 5-8s per dashboard load
- After: <1s cached loads (85% faster)

### Lazy Loading

**UML Diagrams:**
- Loaded only when tab is visible
- Intersection Observer for smooth experience
- Progressive rendering (60 FPS)

**Charts:**
- D3.js optimization with batch rendering
- Virtualized tables for large datasets

---

## ♿ Accessibility

The dashboard meets **WCAG 2.1 AA** standards:

### Keyboard Navigation

- **Tab:** Navigate between interactive elements
- **Enter/Space:** Activate buttons and tabs
- **Arrow Keys:** Navigate between tabs
- **Escape:** Close modals and tooltips
- **Home/End:** Jump to first/last tab

### Screen Reader Support

- **ARIA Labels:** All interactive elements labeled
- **Live Regions:** Dynamic updates announced
- **Skip Links:** Jump to main content
- **Semantic HTML:** Proper heading hierarchy

### Visual Accessibility

- **Color Contrast:** 4.5:1 minimum (normal text), 3:1 (large text)
- **Focus Indicators:** 3px outline with 2px offset
- **Keyboard Navigation Mode:** Visible only during keyboard use
- **Reduced Motion:** Respects `prefers-reduced-motion` setting

### Touch Accessibility

- **Minimum Touch Targets:** 44×44px (Apple HIG standard)
- **Touch Feedback:** Visual ripple effect on tap
- **No Hover-Dependent Features:** All features accessible via touch

---

## 🛠️ Troubleshooting

### Dashboard Not Loading

**Symptoms:** Blank page or error message

**Solutions:**
1. Check browser console for errors (F12)
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Clear browser cache and reload (Ctrl+Shift+R)
4. Check file permissions on output directory

### UML Diagrams Not Rendering

**Symptoms:** Empty UML tab or broken image

**Solutions:**
1. Verify Graphviz installed: `dot -V`
2. Install Graphviz: `brew install graphviz` (macOS) or `apt install graphviz` (Linux)
3. Check Python path includes Graphviz binaries
4. Verify source code is valid Python (no syntax errors)

### PPTX Export Failing

**Symptoms:** `ImportError: No module named 'pptx'`

**Solutions:**
1. Install python-pptx: `pip install python-pptx`
2. Verify installation: `python -c "import pptx; print(pptx.__version__)"`
3. Check write permissions on output directory

### Slow Performance

**Symptoms:** Dashboard takes >5 seconds to load

**Solutions:**
1. Enable caching (should be automatic)
2. Reduce max table rows in config
3. Limit UML diagram size (exclude large modules)
4. Clear old cache files: `rm -rf .cache/dashboard/*`

### Cache Not Working

**Symptoms:** Dashboard regenerates on every load

**Solutions:**
1. Check cache directory exists and is writable
2. Verify TTL not set to 0 in config
3. Clear corrupted cache: `rm -rf .cache/dashboard/*`
4. Check system time is correct (affects TTL calculation)

---

## 📚 API Reference

### Generate Dashboard

```python
def generate_dashboard(
    project_path: str,
    output_path: str = "dashboard.html",
    include_uml: bool = True,
    include_tests: bool = True,
    cache_enabled: bool = True
) -> str:
    """
    Generate complete onboarding dashboard
    
    Args:
        project_path: Path to project root directory
        output_path: Where to save generated HTML
        include_uml: Generate UML diagrams (requires Graphviz)
        include_tests: Run and include test results
        cache_enabled: Use cached data if available
        
    Returns:
        Path to generated HTML file
        
    Raises:
        FileNotFoundError: If project_path doesn't exist
        PermissionError: If output_path not writable
    """
```

### Export to PPTX

```python
def export_dashboard_to_pptx(
    dashboard_data: Dict[str, Any],
    output_path: Optional[Path] = None,
    config: Optional[PPTXExportConfig] = None
) -> Path:
    """
    Export dashboard to PowerPoint presentation
    
    Args:
        dashboard_data: Dashboard data dictionary
        output_path: Custom output path (default: auto-generated)
        config: Export configuration
        
    Returns:
        Path to created PPTX file
        
    Raises:
        ImportError: If python-pptx not installed
        ValueError: If dashboard_data invalid
    """
```

### Configuration

```python
@dataclass
class DashboardConfig:
    """Dashboard generation configuration"""
    
    # Performance
    cache_ttl_hours: int = 24
    max_table_rows: int = 100
    lazy_load_uml: bool = True
    
    # Features
    enable_accessibility: bool = True
    enable_responsive: bool = True
    enable_export: bool = True
    
    # Styling
    primary_color: str = "#0066cc"
    success_color: str = "#28a745"
    warning_color: str = "#ffc107"
    danger_color: str = "#dc3545"
```

---

## 🔗 Additional Resources

- **GitHub Repository:** https://github.com/asifhussain60/CORTEX
- **Issue Tracker:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** `cortex-brain/documents/implementation-guides/`
- **Examples:** `examples/dashboard_demos/`

---

## 📝 License

Source-Available License  
**Use Allowed, No Contributions**

Copyright (c) 2025 Asif Hussain

---

**Questions or Issues?**

Create an issue on GitHub or contact the maintainer through the repository.
