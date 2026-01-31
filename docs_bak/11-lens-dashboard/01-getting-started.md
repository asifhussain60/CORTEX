# LENS Dashboard - Getting Started

**Phase:** 14 - Visual Intelligence  
**Audience:** Developers, Team Leads, Project Managers

---

## 🚀 Installation

LENS Dashboard is included with CORTEX. No additional installation required.

### Prerequisites

- Python 3.9+
- Git (for git history analysis)
- CORTEX installed and configured

### Verify Installation

```bash
# Check CORTEX CLI
cortex --version

# Check dashboard command availability
cortex dashboard --help
```

---

## 📊 Your First Dashboard

### Step 1: Navigate to Repository

```bash
cd /path/to/your/repository
```

### Step 2: Generate Dashboard

```bash
# Generate dashboard for current directory
cortex dashboard generate .

# Or specify a path
cortex dashboard generate /path/to/repo
```

**Expected Output:**
```
🧠 CORTEX LENS Dashboard Generator
📁 Repository: /path/to/repo
🔍 Analyzing repository...
✅ Repository detection complete
✅ LENS analysis complete
✅ Generating visualizations...
✅ Rendering HTML templates...

📊 Dashboard generated successfully!
📂 Output: /path/to/repo/.cortex-lens/dashboard/
🌐 Open: file:///path/to/repo/.cortex-lens/dashboard/index.html

💡 Tip: Use 'cortex dashboard serve .' to start a local server
```

### Step 3: View Dashboard

**Option A: Open in Browser**
```bash
# macOS
open .cortex-lens/dashboard/index.html

# Linux
xdg-open .cortex-lens/dashboard/index.html

# Windows
start .cortex-lens/dashboard/index.html
```

**Option B: Use Built-in Server**
```bash
cortex dashboard serve . --port 8080
```

Then open: `http://localhost:8080`

---

## 🎨 Dashboard Tour

### Navigation

The dashboard consists of multiple tabs accessible via the top navigation bar:

```
┌─────────────────────────────────────────────────────┐
│ 🧠 CORTEX LENS    repo-name                         │
│ 🔒 Security  ⚡ Performance  ✓ Compliance           │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ [ Overview ] [ Dependencies ] [ Classes ]            │
│ [ Timeline ] [ Authors ]                            │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                                                      │
│              Tab Content Here                       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Tab Overview

1. **📋 Overview** - High-level repository summary
   - What the repository does (natural language)
   - Key features and capabilities
   - Technology stack
   - Architecture patterns

2. **🔗 Dependencies** - Module and function relationships
   - Interactive dependency graph
   - Circular dependency detection
   - Import analysis

3. **📐 Classes** - Object-oriented structure
   - UML class diagrams
   - Inheritance relationships
   - Method signatures

4. **⏱️ Timeline** - Git commit history
   - Temporal visualization
   - Commit categorization
   - Author activity

5. **👥 Authors** - Team collaboration
   - Author network graph
   - Contribution metrics
   - Collaboration patterns

### Multi-Dimensional Overlays

Toggle overlays using the header buttons:

- **🔒 Security** - Highlights security concerns
- **⚡ Performance** - Shows performance hotspots
- **✓ Compliance** - Displays compliance status

---

## 💻 CLI Usage

### Generate Command

```bash
# Basic generation
cortex dashboard generate <path>

# With custom output
cortex dashboard generate <path> --output /custom/path

# Verbose output
cortex dashboard generate <path> --verbose
```

**Arguments:**
- `<path>` - Repository path (default: current directory)

**Options:**
- `--output, -o` - Custom output directory
- `--verbose, -v` - Detailed logging

**Examples:**
```bash
# Current directory
cortex dashboard generate .

# Specific repository
cortex dashboard generate ~/projects/flask-app

# Custom output location
cortex dashboard generate . --output ~/dashboards/my-project

# Verbose mode
cortex dashboard generate . -v
```

### Serve Command

```bash
# Start local HTTP server
cortex dashboard serve <path>

# Custom port
cortex dashboard serve <path> --port 3000

# Custom host
cortex dashboard serve <path> --host 0.0.0.0
```

**Arguments:**
- `<path>` - Repository path (default: current directory)

**Options:**
- `--port, -p` - Server port (default: 8000)
- `--host, -h` - Server host (default: 127.0.0.1)

**Examples:**
```bash
# Default server (localhost:8000)
cortex dashboard serve .

# Custom port
cortex dashboard serve . --port 3000

# Allow network access
cortex dashboard serve . --host 0.0.0.0 --port 8080
```

### List Command

```bash
# List all generated dashboards
cortex dashboard list
```

**Output:**
```
📊 Generated Dashboards:

1. my-project
   Path: /Users/alice/projects/my-project/.cortex-lens/dashboard
   Generated: 2026-01-29 10:30:00

2. flask-app
   Path: /Users/alice/projects/flask-app/.cortex-lens/dashboard
   Generated: 2026-01-28 15:45:00

Total: 2 dashboards
```

---

## 🌐 REST API Usage

### Start API Server

```bash
# Using uvicorn directly
uvicorn cortex.visualization.api.dashboard_routes:app --reload

# Or via Python
python -m uvicorn cortex.visualization.api.dashboard_routes:app --port 8000
```

### API Endpoints

#### Generate Dashboard

```bash
curl -X POST http://localhost:8000/api/lens/dashboard/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "output_path": "/optional/output/path"
  }'
```

**Response:**
```json
{
  "status": "success",
  "output_path": "/path/to/repo/.cortex-lens/dashboard",
  "tabs": [
    {"id": "overview", "name": "Overview"},
    {"id": "dependencies", "name": "Dependencies"},
    {"id": "classes", "name": "Classes"},
    {"id": "timeline", "name": "Timeline"},
    {"id": "authors", "name": "Authors"}
  ],
  "timestamp": "2026-01-29T10:30:00Z"
}
```

#### List Dashboards

```bash
curl http://localhost:8000/api/lens/dashboard/list
```

**Response:**
```json
{
  "dashboards": [
    {
      "name": "my-project",
      "path": "/path/to/my-project/.cortex-lens/dashboard",
      "generated_at": "2026-01-29T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### Get Dashboard Metadata

```bash
curl http://localhost:8000/api/lens/dashboard/my-project/metadata
```

#### Serve Dashboard Files

```bash
curl http://localhost:8000/api/lens/dashboard/my-project/index.html
```

#### Health Check

```bash
curl http://localhost:8000/api/lens/dashboard/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T10:30:00Z",
  "version": "1.0.0"
}
```

---

## 🐍 Python API Usage

### Basic Usage

```python
from pathlib import Path
from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
)

# Initialize orchestrator
orchestrator = LENSVisualizationOrchestrator(
    repo_path=Path("/path/to/repo")
)

# Generate dashboard
result = orchestrator.generate_dashboard()

# Access results
print(f"Output: {result.output_path}")
print(f"Tabs: {[tab.name for tab in result.tabs]}")
```

### Custom Output Path

```python
from pathlib import Path
from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
)

orchestrator = LENSVisualizationOrchestrator(
    repo_path=Path("/path/to/repo")
)

# Custom output location
result = orchestrator.generate_dashboard(
    output_path=Path("/custom/output/path")
)
```

### Access Dashboard Data

```python
# Generate dashboard
result = orchestrator.generate_dashboard()

# Access data for each tab
print("Repository Overview:")
print(result.repository_overview)

print("Dependency Graph:")
print(result.dependency_graph)

print("Class Diagrams:")
print(result.class_diagrams)

print("Temporal Analysis:")
print(result.temporal_analysis)

print("Impact Analysis:")
print(result.impact_analysis)
```

### Repository Detection

```python
from pathlib import Path
from cortex.visualization.repository_detector import is_cortex_repository

repo_path = Path("/path/to/repo")

if is_cortex_repository(repo_path):
    print("This is a CORTEX repository!")
    # Access CORTEX-specific features
else:
    print("External repository detected")
    # Use universal features only
```

---

## 📂 Output Structure

### Directory Layout

```
repo-root/
├── .cortex-lens/              # Dashboard output (auto-created)
│   └── dashboard/
│       ├── index.html         # Main dashboard page
│       ├── static/
│       │   ├── vendor/        # Bundled JS/CSS libraries
│       │   │   ├── alpine-3.13.3.min.js
│       │   │   ├── d3-7.8.5.min.js
│       │   │   ├── mermaid-10.6.1.min.js
│       │   │   └── tailwind-3.4.0.min.css
│       │   └── data/          # Generated JSON data
│       │       ├── timeline.json
│       │       ├── authors.json
│       │       ├── dependencies.json
│       │       └── classes.json
│       └── tabs/              # Tab-specific assets
└── .gitignore                 # Auto-updated with .cortex-lens/
```

### Generated Files

| File | Purpose | Size |
|------|---------|------|
| `index.html` | Main dashboard | ~20KB |
| `static/vendor/*.js` | JavaScript libraries | ~1.1MB |
| `static/vendor/*.css` | CSS frameworks | ~100KB |
| `static/data/*.json` | Visualization data | Varies |

---

## 🔧 Configuration

### Custom Tab Selection

Currently, tabs are auto-detected based on repository type (CORTEX vs external). Future versions will support custom configuration.

### Output Location Override

```bash
# Environment variable
export CORTEX_DASHBOARD_OUTPUT=/custom/path
cortex dashboard generate .

# Or via CLI flag
cortex dashboard generate . --output /custom/path
```

---

## 🐛 Troubleshooting

### Dashboard Not Generating

**Problem:** Command hangs or fails silently

**Solutions:**
1. Check Git repository exists: `git status`
2. Verify Python version: `python --version` (3.9+ required)
3. Run with verbose flag: `cortex dashboard generate . --verbose`

### Empty Visualizations

**Problem:** Dashboard loads but visualizations are empty

**Solutions:**
1. Ensure repository has commit history: `git log`
2. Check for Python files: `find . -name "*.py"`
3. Verify output data files exist in `static/data/`

### Port Already in Use

**Problem:** `cortex dashboard serve` fails with "Address already in use"

**Solutions:**
```bash
# Use different port
cortex dashboard serve . --port 3000

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Permission Denied

**Problem:** Cannot write to output directory

**Solutions:**
```bash
# Check permissions
ls -la .cortex-lens/

# Fix permissions
chmod 755 .cortex-lens/
chmod -R 644 .cortex-lens/dashboard/*
```

---

## 💡 Tips & Best Practices

### Performance

- **Large Repositories:** First generation may take 30-60s
- **Incremental Updates:** Re-generation is faster (uses cache)
- **Serve Mode:** Use for development, not production

### Security

- **Local Only:** Dashboard is not intended for public hosting
- **Sensitive Data:** Review before sharing dashboard exports
- **Git-Ignored:** `.cortex-lens/` is auto-added to `.gitignore`

### Workflow Integration

```bash
# Generate dashboard after major commits
git commit -m "feat: Add new feature"
cortex dashboard generate .

# Review before code review
cortex dashboard serve . &
open http://localhost:8000

# Share with team (export)
tar -czf dashboard.tar.gz .cortex-lens/dashboard/
```

---

## 📚 Next Steps

- **[API Reference](./02-api-reference.md)** - Complete API documentation
- **[CLI Reference](./03-cli-reference.md)** - All CLI commands
- **[Renderer Guide](./04-renderer-guide.md)** - Custom visualizations
- **[Examples](./07-examples.md)** - Real-world use cases

---

**Need Help?** See **[FAQ](./08-faq.md)** or **[Troubleshooting Guide](./09-troubleshooting.md)**
