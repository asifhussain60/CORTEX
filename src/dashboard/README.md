# Universal Dashboard System

**Clean Architecture implementation for consolidated CORTEX and external application dashboards.**

## 🏗️ Architecture Overview

This dashboard system follows **Clean Architecture** principles with strict dependency management:

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                     │
│         (Flask Routes, Templates, HTTP)                 │
│  Depends on: Application, Infrastructure, Domain        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                    │
│    (JSON, SQLite, URL Resolution, File I/O)             │
│           Depends on: Domain only                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│         (Use Cases, DTOs, Business Workflows)           │
│           Depends on: Domain only                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                         │
│      (Entities, Repository Interfaces, Pure Logic)      │
│            Depends on: Nothing (Pure Python)            │
└─────────────────────────────────────────────────────────┘
```

### The Dependency Rule

**Source code dependencies must point inward ONLY.** Nothing in an inner circle can know about something in an outer circle.

✅ **Allowed**: Presentation → Infrastructure → Application → Domain  
❌ **Forbidden**: Domain → Application, Domain → Infrastructure, Application → Infrastructure

## 📂 Project Structure

```
src/dashboard/
├── domain/                     # Domain Layer (Pure Python)
│   ├── entities/
│   │   ├── dashboard_data.py   # Dashboard data entity
│   │   ├── application.py      # Application registry entity
│   │   └── tab_content.py      # Tab content entity
│   └── repositories/
│       ├── dashboard_repository.py    # Dashboard repo interface
│       └── application_repository.py  # App repo interface
│
├── application/                # Application Layer (Business Logic)
│   ├── use_cases/
│   │   ├── load_dashboard.py           # Load dashboard workflow
│   │   └── refresh_dashboard.py        # Refresh dashboard workflow
│   └── dtos/
│       ├── load_dashboard_dto.py       # Load request/response DTOs
│       └── refresh_dashboard_dto.py    # Refresh request/response DTOs
│
├── infrastructure/             # Infrastructure Layer (Adapters)
│   ├── repositories/
│   │   ├── json_dashboard_repository.py    # JSON file persistence
│   │   └── sqlite_app_repository.py        # SQLite app registry
│   └── url_resolver.py                     # Portable URL resolution
│
└── presentation/               # Presentation Layer (UI/API)
    └── app.py                              # Flask application factory

cortex-brain/dashboards/        # Dashboard data storage (JSON files)
tests/dashboard/                # Test suite (47+ tests)
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Flask (required for presentation layer)
pip install flask
```

### Running Tests

```bash
# Run all dashboard tests
pytest tests/dashboard/ -v

# Run specific layer tests
pytest tests/dashboard/domain/ -v           # Domain layer (22 tests)
pytest tests/dashboard/application/ -v     # Application layer (9 tests)
pytest tests/dashboard/infrastructure/ -v  # Infrastructure layer (26 tests)
pytest tests/dashboard/test_architecture.py -v  # Architecture enforcement (8 tests)

# Run with coverage
pytest tests/dashboard/ --cov=src/dashboard --cov-report=html
```

### Running the Dashboard

```python
from pathlib import Path
from src.dashboard.presentation.app import create_app

# Create Flask app
app = create_app(
    dashboard_base_path=Path("cortex-brain/dashboards"),
    app_registry_db_path=Path("cortex-brain/dashboards/apps.db")
)

# Run development server
app.run(host='0.0.0.0', port=5000, debug=True)
```

Access dashboards:
- **CORTEX Dashboard**: http://localhost:5000/
- **Specific App**: http://localhost:5000/{app_id}
- **Refresh API**: POST http://localhost:5000/refresh/{app_id}

## 🎯 Features

### Portable URLs
No hardcoded configuration needed. URLs adapt automatically:
- Development: `http://localhost:5000`
- Custom port: `http://localhost:8080`
- Production: `https://dashboard.example.com`

### Repository Pattern
Abstract interfaces in domain, concrete implementations in infrastructure:
```python
# Domain defines contract
class DashboardRepository(ABC):
    @abstractmethod
    def get_by_id(self, app_id: str) -> DashboardData:
        pass

# Infrastructure implements
class JsonDashboardRepository(DashboardRepository):
    def get_by_id(self, app_id: str) -> DashboardData:
        # JSON file loading implementation
```

### Dependency Injection
Use cases receive repositories via constructor:
```python
# Infrastructure creates repositories
dashboard_repo = JsonDashboardRepository(base_path="...")
app_repo = SqliteAppRepository(db_path="...")

# Inject into use cases
load_use_case = LoadDashboardUseCase(dashboard_repo)
refresh_use_case = RefreshDashboardUseCase(dashboard_repo)
```

## 📊 Adding New Applications

### 1. Register Application
```python
from src.dashboard.domain.entities.application import Application
from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
from datetime import datetime
from pathlib import Path

repo = SqliteAppRepository(db_path=Path("cortex-brain/dashboards/apps.db"))

app = Application(
    app_id="my-app",
    app_name="My Application",
    app_type="external",  # or "internal" or "user"
    data_path="/cortex-brain/dashboards/my-app",
    last_scan=datetime.now()
)

repo.save(app)
```

### 2. Create Dashboard Data
```python
from src.dashboard.domain.entities.dashboard_data import DashboardData
from src.dashboard.infrastructure.repositories.json_dashboard_repository import JsonDashboardRepository

repo = JsonDashboardRepository(base_path=Path("cortex-brain/dashboards"))

data = DashboardData(
    app_id="my-app",
    tabs={
        "overview": {
            "total_files": 50,
            "total_lines": 2500
        },
        "metrics": {
            "complexity": 2.8,
            "maintainability": 90
        }
    },
    metadata={
        "app_name": "My Application",
        "app_type": "external",
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat()
    }
)

repo.save(data)
```

### 3. Access Dashboard
Navigate to `http://localhost:5000/my-app`

## 🧪 Test Coverage

| Layer | Tests | Coverage | Status |
|-------|-------|----------|--------|
| Domain Entities | 12 | 100% | ✅ PASSING |
| Domain Repositories | 10 | 100% | ✅ PASSING |
| Application Use Cases | 9 | 100% | ✅ PASSING |
| Infrastructure JSON | 9 | 100% | ✅ PASSING |
| Infrastructure SQLite | 9 | 100% | ✅ PASSING |
| Infrastructure URL | 8 | 100% | ✅ PASSING |
| Architecture Enforcement | 8 | N/A | ✅ PASSING |
| **TOTAL** | **47+** | **100%** | **✅ ALL PASSING** |

## 🔒 Security Features

### Path Traversal Protection
```python
# ✅ ALLOWED
app_id = "my-app_v2"     # Alphanumeric, hyphens, underscores

# ❌ BLOCKED
app_id = "../etc/passwd"  # Path traversal attempt
app_id = "app/id"         # Slashes not allowed
app_id = "app:id"         # Special characters blocked
```

### Immutable Entities
All domain entities are frozen dataclasses preventing accidental mutations:
```python
@dataclass(frozen=True)
class DashboardData:
    app_id: str
    tabs: Dict[str, Any]
    metadata: Dict[str, Any]

# ❌ This raises FrozenInstanceError
data.app_id = "changed"
```

## 🎨 Clean Code Principles

### TDD (Test-Driven Development)
Every feature follows **RED → GREEN → REFACTOR**:
1. **RED**: Write failing test first
2. **GREEN**: Minimal implementation to pass
3. **REFACTOR**: Clean code while tests remain green

### SOLID Principles
- **S**ingle Responsibility: Each class has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interfaces can be swapped without breaking code
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

## 📝 API Reference

### LoadDashboardUseCase
```python
request = LoadDashboardRequest(app_id="cortex")
response = load_use_case.execute(request)

# Response fields:
# - app_id: str
# - app_name: str
# - data: DashboardData
```

### RefreshDashboardUseCase
```python
request = RefreshDashboardRequest(app_id="cortex", force=False)
response = refresh_use_case.execute(request)

# Response fields:
# - app_id: str
# - success: bool
# - message: str
# - refresh_time: datetime
```

### Flask Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Display CORTEX dashboard |
| GET | `/<app_id>` | Display specific app dashboard |
| POST | `/refresh/<app_id>` | Refresh dashboard data |
| POST | `/refresh/<app_id>?force=true` | Force refresh (ignore freshness) |

## 🐛 Troubleshooting

### Tests Fail with "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask
```

### Dashboard Not Found (404)
Ensure dashboard JSON file exists:
```bash
ls cortex-brain/dashboards/{app_id}.json
```

### Architecture Tests Fail
Check for forbidden imports:
```bash
pytest tests/dashboard/test_architecture.py -v
```

## 📚 Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

## 🤝 Contributing

This project follows strict Clean Architecture. Before contributing:

1. **Read Architecture Guidelines**: Understand the dependency rule
2. **Write Tests First**: RED → GREEN → REFACTOR cycle
3. **Verify Architecture**: Run `pytest tests/dashboard/test_architecture.py`
4. **100% Coverage**: All new code must have tests

## 📄 License

Source-Available (Use Allowed, No Contributions) - See LICENSE file

## ✨ Author

**Asif Hussain**  
GitHub: [github.com/asifhussain60/CORTEX](https://github.com/asifhussain60/CORTEX)

---

**Built with Clean Architecture • TDD Mastery • SOLID Principles**

---

## 🎨 Phase 2: UI Templates & Styling (COMPLETE)

### Template System

**Base Template** (`templates/base.html`):
- HTML5 structure with responsive viewport
- Header with navigation
- Footer with attribution  
- CSS and JavaScript asset links
- Content block for child templates

**Dashboard Template** (`templates/dashboard_clean.html`):
- Extends base.html
- Dashboard header with app name and metadata
- Tab navigation with data-tab attributes
- Tab panels with unique IDs
- Metrics grid with card layout
- Automatic HTML escaping (XSS protection)

### CSS Customization (`static/css/style.css`)

**CSS Variables for Theming:**
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #1abc9c;
    --spacing-md: 1rem;
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

**Key CSS Classes:**
- `.dashboard-container` - Main wrapper
- `.tabs-nav` - Tab button container
- `.tab-button` / `.tab-button.active` - Tab buttons with active state
- `.metrics-grid` - CSS Grid for metric cards (auto-fill, minmax(250px, 1fr))
- `.metric-card` - Individual metric with hover effect
- `.metric-label` / `.metric-value` - Metric display

**Responsive Breakpoints:**
- Mobile: < 768px (single column, stacked tabs)
- Tablet: 768px+ (2-3 columns)
- Desktop: 1024px+ (3-4 columns)
- Large: 1440px+ (max width 1600px)

### JavaScript API (`static/js/dashboard.js`)

**Tab Switching:**
```javascript
// Automatic on button click with data-tab="tab-name"
// Manual: switchTab('overview')
```

**Refresh Dashboard:**
```javascript
// Call from HTML: onclick="refreshDashboard(); return false;"
// AJAX POST to /refresh/<app_id>
// Reloads page on success
```

**URL Hash Support:**
```javascript
// Direct links: http://localhost:5000/cortex#metrics
// Browser back/forward buttons work
// Hash changes trigger tab switches
```

**Utility Functions:**
```javascript
formatNumber(1234567)  // "1,234,567"
formatBytes(1048576)   // "1 MB"
```

### Customization Examples

**1. Change Color Scheme:**
```css
/* Edit style.css :root section */
:root {
    --primary-color: #1e3a8a;      /* Dark blue */
    --secondary-color: #3b82f6;    /* Bright blue */
    --accent-color: #10b981;       /* Green */
}
```

**2. Adjust Metric Card Size:**
```css
.metrics-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Larger cards */
    gap: var(--spacing-xl); /* More spacing */
}
```

**3. Add Custom Tab:**
```html
<!-- In dashboard_clean.html -->
<button class="tab-button" data-tab="custom">Custom Tab</button>

<div class="tab-panel" id="tab-custom">
    <h3>Custom Content</h3>
    <!-- Your content here -->
</div>
```

---

## 📊 Test Coverage

**Total Tests:** 104 (100% passing)

### Breakdown by Layer:
- Domain Layer: 22 tests
- Application Layer: 9 tests  
- Infrastructure Layer: 26 tests
- Presentation Layer: 39 tests
  - Templates: 8 tests
  - CSS: 8 tests
  - JavaScript: 7 tests
  - Integration: 11 tests
  - Routes: 5 tests
- Architecture: 8 tests

### Test Execution:
```bash
# All tests
pytest tests/dashboard/ -v

# Specific layer
pytest tests/dashboard/presentation/ -v

# With coverage
pytest tests/dashboard/ --cov=src/dashboard --cov-report=html
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All 104 tests passing
- [ ] No architecture violations (8 architecture tests)
- [ ] CSS minified for production
- [ ] JavaScript linted and tested
- [ ] Templates tested with real data
- [ ] Security: HTML escaping enabled (Jinja2 auto-escape)
- [ ] Security: No inline JavaScript in templates
- [ ] Security: CSP headers configured (if needed)

### Production Settings
```python
app = create_app(
    dashboard_base_path=Path("/var/www/dashboards"),
    app_registry_db_path=Path("/var/www/data/apps.db")
)

app.config['TESTING'] = False
app.config['DEBUG'] = False
app.config['ENV'] = 'production'
```

### Performance Optimization
- Enable Flask caching for static assets
- Minify CSS and JavaScript (optional, already small)
- Use CDN for static assets (optional)
- Enable gzip compression

---

## 📖 API Reference

### Flask Routes

**GET /**
- Returns: CORTEX dashboard HTML
- Template: dashboard_clean.html
- Data: loads from `cortex.json`

**GET /<app_id>**
- Returns: Application dashboard HTML
- Template: dashboard_clean.html
- Data: loads from `<app_id>.json`
- Error: 404 if dashboard not found

**POST /refresh/<app_id>**
- Returns: JSON response
- Body: `{ "app_id": "...", "success": true, "message": "...", "refresh_time": "..." }`
- Query Params: `?force=true` (optional)
- Error: 500 with JSON error response

### Repository Interface

```python
# Load dashboard
data = dashboard_repository.get_by_id("cortex")

# Save dashboard
dashboard_repository.save(dashboard_data)

# Check existence
exists = dashboard_repository.exists("cortex")
```

### Use Case Execution

```python
# Load dashboard use case
request = LoadDashboardRequest(app_id="cortex")
response = load_dashboard_use_case.execute(request)

# Access response
print(response.app_id)
print(response.app_name)
print(response.data.tabs)
```

---

## 🔧 Troubleshooting

### Dashboard Not Found (404)
- Check JSON file exists: `data/dashboards/<app_id>.json`
- Verify app_id format (alphanumeric, hyphens, underscores only)
- Check file permissions (readable by Flask process)

### Tabs Not Switching
- Verify dashboard.js is loaded (check browser console)
- Ensure tab buttons have `data-tab` attributes
- Ensure tab panels have `id="tab-<name>"` format
- Check browser JavaScript console for errors

### Styling Issues
- Verify style.css is loaded (check Network tab)
- Clear browser cache (CSS may be cached)
- Check for CSS variable support (modern browsers only)
- Inspect element to verify classes are applied

### Refresh Not Working
- Check network request in browser DevTools
- Verify `/refresh/<app_id>` endpoint exists
- Check Flask logs for errors
- Ensure AJAX response is valid JSON

---

## 🎓 Learning Resources

### Clean Architecture
- **Book:** "Clean Architecture" by Robert C. Martin
- **Pattern:** Dependency Inversion Principle (DIP)
- **Benefits:** Testability, maintainability, flexibility

### TDD Mastery
- **Cycle:** RED (failing test) → GREEN (minimal code) → REFACTOR (clean code)
- **Benefits:** Confidence, documentation, design feedback
- **Practice:** Write test first, make it fail, make it pass, refactor

### Flask Best Practices
- Application factory pattern (create_app)
- Dependency injection (repositories)
- Template inheritance (base → child)
- Blueprint organization (for larger apps)

---

**Version History:**
- v2.0 (Phase 2): UI Templates, CSS, JavaScript, Integration Tests (104 tests)
- v1.0 (Phase 1): Clean Architecture Foundation (70 tests)

**Maintainer:** Asif Hussain  
**License:** Source-Available (Use Allowed, No Contributions)
