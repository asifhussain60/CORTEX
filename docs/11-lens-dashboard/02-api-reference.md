# LENS Dashboard - API Reference

**Phase:** 14 - Visual Intelligence  
**Version:** 1.0.0

---

## 🌐 REST API Endpoints

### Base URL

```
http://localhost:8000/api/lens/dashboard
```

### Authentication

Currently, no authentication required. Future versions will support API keys.

---

## 📡 Endpoints

### 1. Generate Dashboard

Generate a new dashboard for a repository.

**Endpoint:** `POST /api/lens/dashboard/generate`

**Request Body:**
```json
{
  "repo_path": "/path/to/repository",
  "output_path": "/optional/custom/path"  // Optional
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "output_path": "/path/to/repository/.cortex-lens/dashboard",
  "tabs": [
    {
      "id": "overview",
      "name": "Overview",
      "template": "repository_overview_tab.html"
    },
    {
      "id": "dependencies",
      "name": "Dependencies",
      "template": "dependency_graph_tab.html"
    },
    {
      "id": "classes",
      "name": "Classes",
      "template": "class_diagram_tab.html"
    },
    {
      "id": "timeline",
      "name": "Timeline",
      "template": "git_timeline_tab.html"
    },
    {
      "id": "authors",
      "name": "Authors",
      "template": "author_network_tab.html"
    }
  ],
  "repository_type": "external",  // or "cortex"
  "timestamp": "2026-01-29T10:30:00Z"
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid path
{
  "detail": "Repository path does not exist"
}

// 422 Unprocessable Entity - Validation error
{
  "detail": [
    {
      "loc": ["body", "repo_path"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}

// 500 Internal Server Error
{
  "detail": "Dashboard generation failed: <error message>"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/lens/dashboard/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/alice/projects/flask-app"
  }'
```

---

### 2. List Dashboards

Get a list of all generated dashboards.

**Endpoint:** `GET /api/lens/dashboard/list`

**Response (200 OK):**
```json
{
  "dashboards": [
    {
      "name": "flask-app",
      "path": "/Users/alice/projects/flask-app/.cortex-lens/dashboard",
      "size_mb": 1.2,
      "generated_at": "2026-01-29T10:30:00Z",
      "tabs_count": 5
    },
    {
      "name": "CORTEX",
      "path": "/Users/alice/projects/CORTEX/reports/lens-dashboard",
      "size_mb": 2.5,
      "generated_at": "2026-01-28T15:20:00Z",
      "tabs_count": 8
    }
  ],
  "total": 2
}
```

**Example:**
```bash
curl http://localhost:8000/api/lens/dashboard/list
```

---

### 3. Get Dashboard Metadata

Get metadata for a specific dashboard.

**Endpoint:** `GET /api/lens/dashboard/{repo_name}/metadata`

**Path Parameters:**
- `repo_name` - Repository name (basename of repo path)

**Response (200 OK):**
```json
{
  "name": "flask-app",
  "path": "/Users/alice/projects/flask-app/.cortex-lens/dashboard",
  "generated_at": "2026-01-29T10:30:00Z",
  "repository_type": "external",
  "tabs": [
    {
      "id": "overview",
      "name": "Overview",
      "data_files": ["static/data/overview.json"]
    },
    {
      "id": "dependencies",
      "name": "Dependencies",
      "data_files": [
        "static/data/call_graph.json",
        "static/data/import_graph.json"
      ]
    }
  ],
  "stats": {
    "total_files": 120,
    "total_lines": 8500,
    "total_commits": 450,
    "total_authors": 3
  }
}
```

**Error Responses:**
```json
// 404 Not Found
{
  "detail": "Dashboard not found: flask-app"
}
```

**Example:**
```bash
curl http://localhost:8000/api/lens/dashboard/flask-app/metadata
```

---

### 4. Serve Dashboard File

Serve a specific file from a dashboard.

**Endpoint:** `GET /api/lens/dashboard/{path:path}`

**Path Parameters:**
- `path` - Relative path to file within dashboard directory

**Response:**
- `200 OK` - File content with appropriate MIME type
- `404 Not Found` - File not found

**Examples:**
```bash
# Get main HTML
curl http://localhost:8000/api/lens/dashboard/flask-app/index.html

# Get JSON data
curl http://localhost:8000/api/lens/dashboard/flask-app/static/data/timeline.json

# Get JavaScript
curl http://localhost:8000/api/lens/dashboard/flask-app/static/vendor/alpine-3.13.3.min.js
```

---

### 5. Health Check

Check API health status.

**Endpoint:** `GET /api/lens/dashboard/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-29T10:30:00Z",
  "components": {
    "orchestrator": "available",
    "renderers": "available",
    "templates": "available"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/lens/dashboard/health
```

---

## 🐍 Python Client

### LENSVisualizationOrchestrator

Main orchestrator for dashboard generation.

```python
from pathlib import Path
from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
    DashboardData,
)

class LENSVisualizationOrchestrator:
    """
    Main coordinator for LENS-powered dashboard generation.
    
    Attributes:
        repo_path: Path to repository root
        git_analyzer: GitHistoryAnalyzer instance
        ast_analyzer: ASTAnalyzer instance
        comment_extractor: CommentExtractor instance
    """
    
    def __init__(self, repo_path: Path) -> None:
        """
        Initialize orchestrator.
        
        Args:
            repo_path: Path to repository root
        """
        ...
    
    def generate_dashboard(
        self, 
        output_path: Optional[Path] = None
    ) -> DashboardData:
        """
        Generate complete dashboard.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            DashboardData with generated content
        """
        ...
    
    def get_dashboard_tabs(self) -> List[DashboardTab]:
        """
        Get applicable tabs for repository.
        
        Returns:
            List of DashboardTab objects
        """
        ...
```

**Example:**
```python
# Basic usage
orchestrator = LENSVisualizationOrchestrator(
    repo_path=Path("/path/to/repo")
)
result = orchestrator.generate_dashboard()

# Custom output
result = orchestrator.generate_dashboard(
    output_path=Path("/custom/output")
)

# Access data
print(result.output_path)
print(result.tabs)
print(result.repository_overview)
```

---

### DashboardData

Dataclass containing dashboard output.

```python
@dataclass
class DashboardData:
    """Complete dashboard data for all tabs."""
    
    output_path: Path
    tabs: List[DashboardTab]
    repository_overview: Dict[str, Any] = field(default_factory=dict)
    dependency_graph: Dict[str, Any] = field(default_factory=dict)
    class_diagrams: Dict[str, Any] = field(default_factory=dict)
    temporal_analysis: Dict[str, Any] = field(default_factory=dict)
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    brain_architecture: Dict[str, Any] = field(default_factory=dict)
    governance_heatmap: Dict[str, Any] = field(default_factory=dict)
    orchestrator_constellation: Dict[str, Any] = field(default_factory=dict)
```

---

### Repository Detector

Detect repository type and features.

```python
from pathlib import Path
from cortex.visualization.repository_detector import (
    is_cortex_repository,
    RepositoryDetector,
)

def is_cortex_repository(repo_path: Path) -> bool:
    """
    Check if repository is CORTEX.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        True if CORTEX repository, False otherwise
    """
    ...

class RepositoryDetector:
    """Detect repository type and features."""
    
    @staticmethod
    def detect(repo_path: Path) -> Dict[str, Any]:
        """
        Detect repository characteristics.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dictionary with detection results:
                - is_cortex: bool
                - project_type: str (flask, django, generic, etc.)
                - features: Dict[str, bool]
        """
        ...
```

**Example:**
```python
from pathlib import Path
from cortex.visualization.repository_detector import (
    is_cortex_repository,
    RepositoryDetector,
)

repo_path = Path("/path/to/repo")

# Simple check
if is_cortex_repository(repo_path):
    print("CORTEX repository detected!")

# Detailed detection
detector = RepositoryDetector()
info = detector.detect(repo_path)
print(f"Project type: {info['project_type']}")
print(f"Features: {info['features']}")
```

---

### Renderers

#### D3GitTimelineRenderer

```python
from cortex.visualization.renderers.d3_git_timeline_renderer import (
    D3GitTimelineRenderer,
)

renderer = D3GitTimelineRenderer()

commits = [
    {
        "hash": "abc123",
        "author": "Alice",
        "date": "2026-01-29T10:00:00",
        "message": "feat: Add feature",
        "files_changed": 5,
        "insertions": 100,
        "deletions": 20,
    }
]

timeline_data = renderer.render_timeline(commits)
# Returns: {"days": [...], "stats": {...}}
```

#### D3AuthorNetworkRenderer

```python
from cortex.visualization.renderers.d3_author_network_renderer import (
    D3AuthorNetworkRenderer,
)

renderer = D3AuthorNetworkRenderer()

commits = [
    {
        "hash": "abc123",
        "author": "Alice",
        "date": "2026-01-29T10:00:00",
        "files_changed": ["src/main.py", "src/utils.py"],
    }
]

network_data = renderer.render_network(commits)
# Returns: {"nodes": [...], "links": [...]}
```

#### MermaidClassDiagramGenerator

```python
from cortex.visualization.renderers.mermaid_class_diagram_generator import (
    MermaidClassDiagramGenerator,
)

generator = MermaidClassDiagramGenerator()

classes = [
    {
        "name": "MyClass",
        "methods": [{"name": "method1", "visibility": "public"}],
        "attributes": [{"name": "attr1", "visibility": "private"}],
        "bases": []
    }
]

diagram = generator.generate_diagram(classes)
# Returns: "classDiagram\n    class MyClass..."
```

---

## 🔧 Configuration Objects

### OutputConfiguration

```python
@dataclass
class OutputConfiguration:
    """Dashboard output configuration."""
    
    repo_path: Path
    output_path: Path
    gitignore_entry: Optional[str]
```

### DashboardTab

```python
@dataclass
class DashboardTab:
    """Dashboard tab configuration."""
    
    id: str
    name: str
    template: str
    applicability: str  # "universal" or "cortex_only"
```

---

## 📊 Data Formats

### Timeline JSON

```json
{
  "days": [
    {
      "date": "2026-01-29",
      "commits": [
        {
          "hash": "abc123",
          "author": "Alice",
          "time": "10:30:00",
          "message": "feat: Add feature",
          "category": "feature",
          "impact": 120,
          "files_changed": 5
        }
      ]
    }
  ],
  "stats": {
    "total_commits": 450,
    "total_authors": 3,
    "date_range": {
      "start": "2025-01-01",
      "end": "2026-01-29"
    }
  }
}
```

### Author Network JSON

```json
{
  "nodes": [
    {
      "id": "alice",
      "name": "Alice",
      "commits": 150,
      "size": 20
    }
  ],
  "links": [
    {
      "source": "alice",
      "target": "bob",
      "value": 10,
      "shared_files": ["src/main.py"]
    }
  ]
}
```

---

## 🚀 Performance

### Response Times

| Endpoint | Avg Time | Max Time |
|----------|----------|----------|
| `/generate` | 5-30s | 60s |
| `/list` | <100ms | 500ms |
| `/metadata` | <50ms | 200ms |
| `/health` | <10ms | 50ms |

### Rate Limiting

Currently, no rate limiting. Future versions will implement:
- 10 requests per minute for `/generate`
- 100 requests per minute for other endpoints

---

## 🔐 CORS Configuration

Default CORS settings:
- **Allowed Origins:** `["*"]` (all origins)
- **Allowed Methods:** `["GET", "POST", "OPTIONS"]`
- **Allowed Headers:** `["*"]`

Production deployments should restrict origins.

---

**Next:** [CLI Reference](./03-cli-reference.md)
