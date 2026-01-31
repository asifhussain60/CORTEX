# CORTEX DOCS ORCHESTRATOR GUIDE
**Version:** 1.0 | **Created:** 2026-01-31  
**Purpose:** HTML Generation for L2 Views

---

## 🎯 CortexDocsOrchestrator Overview

**Location:** `cortex/orchestrators/domain/cortex_docs_orchestrator.py`  
**Purpose:** Advisory + HTML generation for CORTEX documentation  
**Not MCP-Exposed:** Internal orchestrator for documentation workflow

---

## 🔧 Operations

### 1. Advisory Mode

#### `advise_section(section_name: str) -> Dict`
Get diagram and content recommendations for an L2 section.

```python
from cortex.orchestrators.domain.cortex_docs_orchestrator import CortexDocsOrchestrator

orchestrator = CortexDocsOrchestrator()

# Get recommendations for Token Optimization
advice = orchestrator.advise_section("token-optimization")

print(advice["diagrams"])  # Recommended D3.js + Mermaid diagrams
print(advice["content"])   # Content structure recommendations
print(advice["features"])  # Interactive features to implement
```

#### `advise_page(page_name: str) -> Dict`
Get recommendations for L3 detail page.

#### `compare_approaches(approaches: List[str]) -> Dict`
Compare D3.js vs SVG vs Mermaid for specific visualization.

```python
comparison = orchestrator.compare_approaches(["d3-sankey", "mermaid-flowchart", "svg-custom"])
print(comparison["recommendation"])  # Best approach
print(comparison["pros_cons"])       # Trade-offs
```

#### `list_sections() -> List[Dict]`
List all sections with status and effort estimates.

```python
sections = orchestrator.list_sections()
for section in sections:
    print(f"{section['name']} - {section['status']} - {section['effort_hours']}h")
```

---

### 2. Generation Mode

#### `generate_l2_page(section_name: str, yaml_spec: str) -> str`
Generate HTML for specific L2 section landing page.

```python
from pathlib import Path

# Read YAML specification
yaml_spec = Path("_workspaces/docker-plan/gitpages/L2/05-token-optimization.yaml").read_text()

# Generate HTML
html_content = orchestrator.generate_l2_page(
    section_name="token-optimization",
    yaml_spec=yaml_spec
)

# Save to file
output_path = Path("docs/token-optimization/index.html")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(html_content)
```

#### `generate_all(yaml_directory: str, output_directory: str) -> Dict`
Generate all documentation HTML files.

```python
results = orchestrator.generate_all(
    yaml_directory="_workspaces/docker-plan/gitpages/L2",
    output_directory="docs"
)

print(results["generated"])  # List of generated files
print(results["errors"])     # Any errors encountered
```

#### `validate(html_path: str) -> Dict`
Validate HTML5 structure and accessibility.

```python
validation = orchestrator.validate("docs/token-optimization/index.html")

print(validation["html5_valid"])       # Boolean
print(validation["wcag_aa_score"])     # 0-100
print(validation["issues"])            # List of issues to fix
```

---

## 📝 HTML Generation Workflow

### Step-by-Step Process

```python
from pathlib import Path
from cortex.orchestrators.domain.cortex_docs_orchestrator import CortexDocsOrchestrator

orchestrator = CortexDocsOrchestrator()

# 1. List all sections to generate
sections = orchestrator.list_sections()
print(f"Found {len(sections)} sections to generate")

# 2. For each section, generate HTML
yaml_dir = Path("_workspaces/docker-plan/gitpages/L2")
docs_dir = Path("docs")

for yaml_file in yaml_dir.glob("*.yaml"):
    if yaml_file.stem.startswith("00-"):
        continue  # Skip metadata files
    
    section_name = yaml_file.stem.replace("_", "-")
    yaml_spec = yaml_file.read_text()
    
    print(f"Generating {section_name}...")
    
    # Generate HTML
    html_content = orchestrator.generate_l2_page(
        section_name=section_name,
        yaml_spec=yaml_spec
    )
    
    # Determine output path
    if "security" in section_name:
        output_dir = docs_dir / "security" / section_name.split("-")[-1]
    elif "orchestrators" in section_name:
        output_dir = docs_dir / "orchestrators" / section_name.split("-")[-1]
    else:
        output_dir = docs_dir / section_name
    
    output_path = output_dir / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content)
    
    print(f"✅ Generated: {output_path}")
    
    # Validate
    validation = orchestrator.validate(str(output_path))
    if validation["html5_valid"]:
        print(f"✅ Validation passed (WCAG AA: {validation['wcag_aa_score']})")
    else:
        print(f"⚠️ Validation issues: {validation['issues']}")
```

---

## 🎨 HTML Template Structure

CortexDocsOrchestrator generates HTML following this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{section_title} | CORTEX</title>
    <link href="../assets/css/main.css" rel="stylesheet"/>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
    <!-- Hero Section with 300x300 CORTEX Logo -->
    <section class="hero-section">
        <img src="../assets/images/CORTEX-logo-512.png" width="300" height="300"/>
        <h1>{section_title}</h1>
        <p>{tagline}</p>
        <div class="stats-pills">
            <!-- Stats from YAML -->
        </div>
    </section>
    
    <!-- D3.js Visualizations -->
    <section class="visualization-section">
        <div id="d3-viz-1"></div>
        <div id="d3-viz-2"></div>
        <div id="d3-viz-3"></div>
    </section>
    
    <!-- Mermaid Diagrams -->
    <section class="diagram-section">
        <div class="mermaid">
            <!-- Mermaid diagram from .mmd file -->
        </div>
    </section>
    
    <!-- Content Sections -->
    <section class="content-section">
        <!-- Content from YAML -->
    </section>
    
    <!-- CTA Section -->
    <section class="cta-section">
        <!-- Call to action -->
    </section>
    
    <!-- D3.js Initialization Scripts -->
    <script>
        // Load data and render D3.js visualizations
    </script>
</body>
</html>
```

---

## 🔗 Integration with docs/index.html

After generating all HTML files, update `docs/index.html`:

```python
from pathlib import Path

index_path = Path("docs/index.html")
index_content = index_path.read_text()

# Find the section where L1 tiles are defined
# Insert new tiles for each generated view

new_tiles = """
<!-- NEW: Token Optimization -->
<div class="glass-card-clickable level1-tile" onclick="window.location.href='token-optimization/index.html'">
    <div class="card-icon"><i class="fas fa-coins"></i></div>
    <h3>Token Optimization</h3>
    <p>70% cost reduction through intelligent context management</p>
</div>

<!-- NEW: Toolkit Manager -->
<div class="glass-card-clickable level1-tile" onclick="window.location.href='toolkit-manager/index.html'">
    <div class="card-icon"><i class="fas fa-toolbox"></i></div>
    <h3>Toolkit Manager</h3>
    <p>15+ MCP tools with dependency tracking</p>
</div>

<!-- ... repeat for all 16 views ... -->
"""

# Insert new tiles before closing </section> tag
# (Manual editing recommended for precise placement)
```

---

## 🧪 Testing

### Local Testing

```bash
# Start local server
cd docs
python3 -m http.server 8080

# Open in browser
open http://localhost:8080/token-optimization/index.html
```

### Validation

```python
from cortex.orchestrators.domain.cortex_docs_orchestrator import CortexDocsOrchestrator

orchestrator = CortexDocsOrchestrator()

# Validate single file
result = orchestrator.validate("docs/token-optimization/index.html")
print(f"HTML5 Valid: {result['html5_valid']}")
print(f"WCAG AA Score: {result['wcag_aa_score']}")

# Validate all generated files
from pathlib import Path

for html_file in Path("docs").rglob("index.html"):
    if "_tests" in str(html_file):
        continue
    
    result = orchestrator.validate(str(html_file))
    status = "✅" if result["html5_valid"] else "❌"
    print(f"{status} {html_file.parent.name} - WCAG: {result['wcag_aa_score']}")
```

---

## 📦 Deployment

### GitHub Pages Deployment

```bash
# After generating all HTML files
cd /Users/asifhussain/PROJECTS/CORTEX

# Commit changes
git add docs/
git commit -m "feat: Add 16 L2 views with D3.js visualizations"

# Push to GitHub (triggers auto-deploy)
git push origin CORTEX

# GitHub Pages will deploy to:
# https://asifhussain60.github.io/CORTEX/token-optimization/index.html
```

---

## 🔍 Troubleshooting

### Issue: D3.js visualization not rendering

**Solution:**
1. Check browser console for errors
2. Verify data file path is correct
3. Ensure D3.js script loads before visualization script

### Issue: Mermaid diagram not displaying

**Solution:**
1. Verify Mermaid CDN script is loaded
2. Check diagram syntax in `.mmd` file
3. Ensure `mermaid.initialize()` is called

### Issue: Responsive design broken on mobile

**Solution:**
1. Check viewport meta tag
2. Verify CSS media queries
3. Test with Chrome DevTools mobile emulator

---

## 📊 Generation Metrics

Track generation progress:

```python
import time
from pathlib import Path

start_time = time.time()
generated_count = 0
error_count = 0

yaml_dir = Path("_workspaces/docker-plan/gitpages/L2")

for yaml_file in yaml_dir.glob("*.yaml"):
    if yaml_file.stem.startswith("00-"):
        continue
    
    try:
        # Generate HTML
        # ... (generation code) ...
        generated_count += 1
        print(f"✅ Generated {generated_count}")
    except Exception as e:
        error_count += 1
        print(f"❌ Error: {yaml_file.stem} - {e}")

elapsed_time = time.time() - start_time
print(f"\n📊 Generation Complete:")
print(f"   Generated: {generated_count}")
print(f"   Errors: {error_count}")
print(f"   Time: {elapsed_time:.2f}s")
print(f"   Avg: {elapsed_time/generated_count:.2f}s per file")
```

---

## ✅ Quick Start Checklist

- [ ] Import CortexDocsOrchestrator
- [ ] Read YAML specification
- [ ] Generate HTML for one view (test)
- [ ] Validate generated HTML
- [ ] Test locally with http.server
- [ ] Verify D3.js visualizations render
- [ ] Verify Mermaid diagrams display
- [ ] Test responsive design
- [ ] Generate all remaining views
- [ ] Update docs/index.html navigation
- [ ] Commit and push to GitHub
- [ ] Verify GitHub Pages deployment

---

*CortexDocsOrchestrator Guide | Version 1.0 | Internal Use Only*
