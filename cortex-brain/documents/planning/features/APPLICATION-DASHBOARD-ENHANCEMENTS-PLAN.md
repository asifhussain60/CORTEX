# 🧠 CORTEX Application Dashboard Enhancement Plan

**Version:** 1.0.0  
**Created:** December 2, 2025  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Purpose:** Enhance multi-tab Application Dashboard with UML modeling, domain entities, and universal project support

---

## 🎯 Executive Summary

This plan enhances the existing Application Dashboard (completed December 1, 2025) to support:
- **UML Class Diagrams** - Auto-generated from codebase structure
- **Domain Entity Modeling** - Detect and visualize business entities across languages
- **Universal Project Support** - API-only and database-only projects without UI
- **Enhanced Tab Structure** - Add Domain Model and Database Schema tabs
- **Multi-Language Entity Detection** - Python, C#, TypeScript, Java, ColdFusion

**Current State:**
- ✅ Multi-tab dashboard (Overview, Architecture, Health, Metrics, Reports)
- ✅ Clean Architecture (Domain entities, Use Cases, Infrastructure)
- ✅ UML generation exists (`render_uml_for_project`) - **ALREADY INTEGRATED**
- ✅ Works for UI-based projects (Blazor, React, ColdFusion)

**Target State:**
- ✅ UML class diagrams in Architecture tab
- ✅ Domain entity detection and visualization
- ✅ Database schema reverse-engineering
- ✅ API endpoint mapping (REST, GraphQL, gRPC)
- ✅ Support for backend-only and database-only projects

**Estimated Effort:** 42 hours (~1 week)

---

## 📋 Current Dashboard Architecture

### Existing Tab Structure
1. **Overview Tab** - Quick stats, system status, top issues
2. **Architecture Tab** - D3.js dependency graph, component relationships
3. **Health Tab** - Health scores, quality metrics
4. **Metrics Tab** - LOC, complexity, test coverage charts
5. **Reports Tab** - Detailed analysis reports

### Existing Domain Entities
```
src/dashboard/domain/
├── component.py       # Software component with health metrics
├── dependency.py      # Component dependency relationships
├── health_score.py    # Health calculation logic
├── issue.py          # Code issues (smells, security, bugs)
└── recommendation.py  # Actionable recommendations
```

### Existing UML Integration
- **Module:** `src/use_cases/render_uml_diagrams.py`
- **Function:** `render_uml_for_project(project_path, output_format='svg')`
- **Status:** ✅ **ALREADY WIRED** into `DashboardRenderer._generate_uml_diagram()`
- **Output:** SVG class diagrams with statistics

---

## 🏗️ Enhancement Architecture

### New Tab Structure (7 Tabs Total)
1. **Overview** - Existing (no changes)
2. **Architecture** - **ENHANCED** - Add UML class diagram section
3. **Domain Model** - **NEW** - Entity detection and relationships
4. **Database Schema** - **NEW** - Reverse-engineered schema visualization
5. **Health** - Existing (no changes)
6. **Metrics** - Existing (no changes)
7. **Reports** - Existing (no changes)

### New Domain Entities

```python
# src/dashboard/domain/domain_entity.py
@dataclass
class DomainEntity:
    """Business domain entity (Customer, Order, Product, etc.)"""
    name: str
    entity_type: EntityType  # MODEL, ENTITY, DTO, VALUE_OBJECT
    properties: List[EntityProperty]
    relationships: List[EntityRelationship]
    language: str
    file_path: str
    is_persistent: bool  # Has database backing?
    table_name: Optional[str]

# src/dashboard/domain/database_table.py
@dataclass
class DatabaseTable:
    """Database table schema"""
    name: str
    schema: str
    columns: List[DatabaseColumn]
    primary_keys: List[str]
    foreign_keys: List[ForeignKey]
    indexes: List[Index]

# src/dashboard/domain/api_endpoint.py
@dataclass
class ApiEndpoint:
    """REST/GraphQL/gRPC endpoint"""
    path: str
    method: str  # GET, POST, etc.
    handler_function: str
    parameters: List[Parameter]
    response_type: str
    authentication_required: bool
```

---

## 📊 Phase Breakdown

### Phase 1: UML Integration Enhancement (8 hours)
**Status:** Partially Complete (UML generation exists, needs UI integration)

**Objective:** Enhance Architecture tab with UML class diagram visualization

**Tasks:**
1. **Add UML Section to Architecture Tab** (2h)
   - Split Architecture tab into two panels: "Dependency Graph" + "UML Class Diagram"
   - Add toggle buttons to switch between views
   - Implement SVG rendering for UML diagrams

2. **Enhance UML Generation** (4h)
   - Add filtering by namespace/package
   - Add zoom/pan controls for large diagrams
   - Color-code by entity type (models, DTOs, services)
   - Add relationship type labels (inheritance, composition, aggregation)

3. **UML Statistics Dashboard** (2h)
   - Class count by type (concrete, abstract, interface)
   - Inheritance depth analysis
   - Coupling metrics (dependencies per class)
   - Display in Architecture tab sidebar

**Deliverables:**
- ✅ Updated `architecture_tab.html` with UML panel
- ✅ Enhanced `render_uml_diagrams.py` with filtering
- ✅ CSS styling for UML visualization
- ✅ Tests for UML integration

**Dependencies:** None (existing functionality)

---

### Phase 2: Domain Entity Detection (14 hours)
**Status:** Not Started

**Objective:** Auto-detect business entities across multiple languages and visualize relationships

**Tasks:**
1. **Multi-Language Entity Detector** (6h)
   - Python: Detect `@dataclass`, SQLAlchemy models, Pydantic models
   - C#: Detect classes with `[Entity]`, POCO classes, EF Core entities
   - TypeScript: Detect `interface`, `type`, class with properties
   - Java: Detect classes with `@Entity`, POJOs
   - ColdFusion: Detect `component` with persistent properties

2. **Entity Relationship Analyzer** (4h)
   - Detect one-to-many, many-to-many relationships
   - Identify foreign key properties
   - Build entity relationship graph
   - Calculate entity complexity scores

3. **Domain Model Tab UI** (4h)
   - D3.js entity relationship diagram
   - Entity list with properties
   - Relationship matrix visualization
   - Filter by module/namespace

**Deliverables:**
- ✅ `src/crawlers/analyzers/entity_detector.py`
- ✅ `src/dashboard/domain/domain_entity.py`
- ✅ `src/dashboard/use_cases/analyze_domain_model.py`
- ✅ `templates/domain_model_tab.html`
- ✅ Tests for entity detection (20 tests minimum)

**Dependencies:** Phase 1 (UML patterns reusable)

---

### Phase 3: Database Schema Reverse Engineering (10 hours)
**Status:** Not Started

**Objective:** Detect database connections and reverse-engineer schema for visualization

**Tasks:**
1. **Database Connection Detector** (3h)
   - Scan for connection strings (SQLite, PostgreSQL, MySQL, SQL Server, MongoDB)
   - Parse ORM configurations (SQLAlchemy, EF Core, Hibernate, Mongoose)
   - Extract database type and schema name

2. **Schema Inspector** (4h)
   - Connect to database and introspect schema
   - Extract tables, columns, data types, constraints
   - Map foreign keys and indexes
   - Generate schema metadata

3. **Database Schema Tab UI** (3h)
   - Mermaid.js ER diagram
   - Table list with column details
   - Foreign key relationship visualization
   - Data dictionary export

**Deliverables:**
- ✅ `src/dashboard/infrastructure/database_inspector.py`
- ✅ `src/dashboard/domain/database_table.py`
- ✅ `src/dashboard/use_cases/analyze_database_schema.py`
- ✅ `templates/database_schema_tab.html`
- ✅ Tests for schema inspection (15 tests minimum)

**Dependencies:** None (standalone feature)

**Security Considerations:**
- ⚠️ Read-only database connections
- ⚠️ No credential storage (use environment variables)
- ⚠️ Timeout protection for large schemas

---

### Phase 4: API Endpoint Mapping (6 hours)
**Status:** Not Started

**Objective:** Detect API endpoints for backend-only projects

**Tasks:**
1. **Endpoint Detector** (3h)
   - REST: Flask routes, FastAPI endpoints, ASP.NET Core controllers, Express.js routes
   - GraphQL: Schema files, resolvers
   - gRPC: Proto files, service definitions

2. **API Documentation Generator** (2h)
   - Extract endpoint path, method, parameters
   - Generate OpenAPI/Swagger-compatible schema
   - Map handlers to code files

3. **API Visualization** (1h)
   - Add API section to Overview tab
   - Display endpoint count by method
   - Link endpoints to implementation files

**Deliverables:**
- ✅ `src/crawlers/analyzers/api_detector.py`
- ✅ `src/dashboard/domain/api_endpoint.py`
- ✅ API endpoint section in Overview tab
- ✅ Tests for API detection (12 tests minimum)

**Dependencies:** Phase 2 (entity detection patterns)

---

### Phase 5: Universal Project Support (4 hours)
**Status:** Not Started

**Objective:** Ensure dashboard works for API-only and database-only projects

**Tasks:**
1. **Project Type Detection** (1h)
   - Classify as: UI (frontend), API (backend), Database, Full-Stack, Library
   - Adjust tab visibility based on project type
   - Provide appropriate recommendations

2. **Conditional Tab Rendering** (2h)
   - Show Domain Model tab if entities detected
   - Show Database Schema tab if database connection found
   - Hide Health tab if no tests found
   - Show API-specific metrics for backend projects

3. **Non-UI Project Templates** (1h)
   - Add CLI project detection
   - Add background service detection (workers, queues)
   - Add data pipeline detection (ETL, streaming)

**Deliverables:**
- ✅ `src/dashboard/use_cases/detect_project_type.py`
- ✅ Conditional tab rendering logic
- ✅ Project type badge in Overview tab
- ✅ Tests for project type detection (10 tests minimum)

**Dependencies:** Phases 2, 3, 4 (all detection systems)

---

## 🧪 Testing Strategy

### Test Distribution by Phase

| Phase | Unit Tests | Integration Tests | Total |
|-------|-----------|------------------|-------|
| Phase 1: UML Enhancement | 8 | 4 | 12 |
| Phase 2: Entity Detection | 15 | 5 | 20 |
| Phase 3: Database Schema | 12 | 3 | 15 |
| Phase 4: API Mapping | 10 | 2 | 12 |
| Phase 5: Universal Support | 8 | 2 | 10 |
| **Total** | **53** | **16** | **69** |

### Test Requirements (TDD Workflow)

**RED → GREEN → REFACTOR for every deliverable:**

1. **Phase 1 Tests**
   - UML SVG rendering test
   - UML filtering test (by namespace)
   - UML statistics calculation test
   - Architecture tab integration test

2. **Phase 2 Tests**
   - Python entity detection (dataclass, SQLAlchemy, Pydantic)
   - C# entity detection (EF Core, POCO)
   - TypeScript entity detection (interface, class)
   - Relationship detection test
   - Entity graph building test

3. **Phase 3 Tests**
   - Connection string parsing test
   - SQLite schema inspection test
   - PostgreSQL schema inspection test
   - Foreign key detection test
   - ER diagram generation test

4. **Phase 4 Tests**
   - Flask route detection test
   - FastAPI endpoint detection test
   - GraphQL schema parsing test
   - OpenAPI schema generation test

5. **Phase 5 Tests**
   - Project type classification test
   - Conditional tab rendering test
   - API-only project dashboard test
   - Database-only project dashboard test

---

## 📐 Technical Design

### UML Diagram Architecture

```python
# Existing: src/use_cases/render_uml_diagrams.py
def render_uml_for_project(
    project_path: str,
    output_format: str = 'svg',
    filter_namespace: Optional[str] = None,  # NEW
    max_classes: int = 50  # NEW - prevent massive diagrams
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate UML class diagram for project.
    
    Returns:
        - SVG content (or PNG/PDF)
        - Statistics (class count, relationships, depth)
    """
    pass
```

### Entity Detection Pipeline

```python
# NEW: src/crawlers/analyzers/entity_detector.py
class EntityDetector:
    """Detect business domain entities across languages"""
    
    def __init__(self):
        self.language_detectors = {
            'python': PythonEntityDetector(),
            'csharp': CSharpEntityDetector(),
            'typescript': TypeScriptEntityDetector(),
            'java': JavaEntityDetector(),
            'coldfusion': ColdFusionEntityDetector()
        }
    
    def detect_entities(self, project_path: str) -> List[DomainEntity]:
        """Scan project and return all detected entities"""
        pass
    
    def analyze_relationships(self, entities: List[DomainEntity]) -> List[EntityRelationship]:
        """Build relationship graph between entities"""
        pass
```

### Database Schema Inspector

```python
# NEW: src/dashboard/infrastructure/database_inspector.py
class DatabaseInspector:
    """Reverse-engineer database schema"""
    
    def __init__(self):
        self.adapters = {
            'sqlite': SQLiteInspector(),
            'postgresql': PostgreSQLInspector(),
            'mysql': MySQLInspector(),
            'sqlserver': SQLServerInspector(),
            'mongodb': MongoDBInspector()
        }
    
    def detect_connections(self, project_path: str) -> List[DatabaseConnection]:
        """Find database connection strings in config files"""
        pass
    
    def inspect_schema(self, connection: DatabaseConnection) -> List[DatabaseTable]:
        """Connect and extract schema metadata"""
        pass
```

### API Endpoint Detector

```python
# NEW: src/crawlers/analyzers/api_detector.py
class ApiEndpointDetector:
    """Detect REST/GraphQL/gRPC endpoints"""
    
    def __init__(self):
        self.framework_detectors = {
            'flask': FlaskRouteDetector(),
            'fastapi': FastAPIEndpointDetector(),
            'aspnet': AspNetCoreControllerDetector(),
            'express': ExpressRouteDetector(),
            'graphql': GraphQLSchemaDetector(),
            'grpc': GrpcServiceDetector()
        }
    
    def detect_endpoints(self, project_path: str) -> List[ApiEndpoint]:
        """Scan for API endpoint definitions"""
        pass
```

---

## 🎨 UI/UX Enhancements

### Architecture Tab Layout (Enhanced)

```
+---------------------------------------+
| Architecture Tab                       |
+---------------------------------------+
| [Dependency Graph] [UML Class Diagram] |  ← Toggle buttons
+---------------------------------------+
| Left Panel:          | Right Panel:   |
| - View Controls      | - SVG Diagram  |
| - Filters            | - Zoom/Pan     |
| - Statistics         | - Search       |
+---------------------------------------+
```

### Domain Model Tab Layout (New)

```
+---------------------------------------+
| Domain Model Tab                       |
+---------------------------------------+
| Entity Statistics:                     |
| - 24 Entities | 15 Relationships      |
+---------------------------------------+
| D3.js ER Diagram (Interactive)        |
|                                       |
| [Customer] → [Order] → [Product]     |
|     ↓                                 |
| [Address]                             |
+---------------------------------------+
| Entity Details Sidebar:               |
| - Properties                          |
| - Relationships                       |
| - Database Table                      |
+---------------------------------------+
```

### Database Schema Tab Layout (New)

```
+---------------------------------------+
| Database Schema Tab                    |
+---------------------------------------+
| Connected to: PostgreSQL (myapp_db)   |
+---------------------------------------+
| Mermaid.js ER Diagram                 |
|                                       |
| Tables: 18 | Views: 3 | Indexes: 42  |
+---------------------------------------+
| Table List:                           |
| - customers (12 columns)             |
| - orders (8 columns)                 |
| - products (15 columns)              |
+---------------------------------------+
```

---

## 🔄 Integration with Existing Systems

### Brain Tier Integration

**Tier 1 (Working Memory):**
- Store recent entity detections
- Cache database schema metadata
- Track API endpoint changes

**Tier 2 (Knowledge Graph):**
- Learn entity naming patterns
- Store relationship templates
- Build domain vocabulary

**Tier 3 (Development Context):**
- Track entity complexity trends
- Monitor database schema changes
- Identify entity hotspots (most modified)

### CORTEX Operations Integration

**Planning System:**
- Use entity model for feature planning
- Suggest affected entities for changes
- Validate database migration plans

**TDD Workflow:**
- Generate entity-based test fixtures
- Suggest test cases for entity relationships
- Validate entity integrity constraints

**Response Templates:**
- Add "show domain model" command
- Add "analyze database schema" command
- Add "list api endpoints" command

---

## 🚀 Deployment Strategy

### Rollout Phases

**Week 1: Phase 1 (UML Enhancement)**
- Deploy enhanced Architecture tab
- No breaking changes (additive only)
- Backward compatible with existing dashboards

**Week 2: Phases 2-3 (Domain + Database)**
- Deploy Domain Model tab (conditional rendering)
- Deploy Database Schema tab (conditional rendering)
- Add project type detection

**Week 3: Phases 4-5 (API + Universal Support)**
- Deploy API endpoint mapping
- Enable universal project support
- Full regression testing

### Rollback Plan
- Each phase is independently deployable
- New tabs are additive (no changes to existing tabs)
- Feature flags for Domain Model and Database Schema tabs

---

## 📝 Success Criteria

### Phase 1: UML Enhancement
- ✅ UML diagram renders in Architecture tab
- ✅ Class filtering by namespace works
- ✅ Statistics display correctly
- ✅ 12/12 tests passing

### Phase 2: Domain Entity Detection
- ✅ Entities detected in Python, C#, TypeScript projects
- ✅ Relationship graph builds correctly
- ✅ Domain Model tab renders entity diagram
- ✅ 20/20 tests passing

### Phase 3: Database Schema
- ✅ Database connections detected automatically
- ✅ Schema extracted for SQLite, PostgreSQL, MySQL
- ✅ ER diagram renders in Database Schema tab
- ✅ 15/15 tests passing

### Phase 4: API Endpoint Mapping
- ✅ REST endpoints detected (Flask, FastAPI, ASP.NET)
- ✅ GraphQL schema parsed
- ✅ API section shows in Overview tab
- ✅ 12/12 tests passing

### Phase 5: Universal Project Support
- ✅ Dashboard works for API-only projects
- ✅ Dashboard works for database-only projects
- ✅ Tabs conditionally render based on project type
- ✅ 10/10 tests passing

### Overall Success
- ✅ **69/69 tests passing** (100% coverage)
- ✅ No regression in existing functionality
- ✅ Performance < 10 seconds for projects with 500 files
- ✅ Documentation updated with new features

---

## ❓ Questions Answered

### Will this dashboard work for API projects without UI?
**Yes.** Phase 5 adds project type detection. For API-only projects:
- Overview tab shows API endpoint statistics
- Domain Model tab shows entity relationships
- Database Schema tab shows backend database
- Health tab evaluates API code quality
- Architecture tab shows service dependencies

### Will this work for database-only projects (stored procedures, views)?
**Yes.** Phase 3 adds database schema inspection:
- Database Schema tab shows tables, views, stored procedures
- Overview tab shows database object counts
- Architecture tab shows table dependency graph
- Metrics tab shows database complexity metrics

### Can it handle microservices with multiple databases?
**Yes.** Phase 3 detects multiple connection strings:
- Each database gets a separate schema visualization
- Database Schema tab has dropdown to select database
- Cross-database relationships detected via foreign keys

### What languages are supported for entity detection?
- ✅ Python (dataclass, SQLAlchemy, Pydantic)
- ✅ C# (EF Core, POCO classes)
- ✅ TypeScript (interface, class)
- ✅ Java (POJO, JPA entities)
- ✅ ColdFusion (persistent components)

### How does this integrate with existing CORTEX brain?
- Tier 1 caches entity and schema data (fast retrieval)
- Tier 2 learns entity naming patterns (suggests entity names)
- Tier 3 tracks entity complexity trends (identifies hot spots)

---

## 📅 Timeline

| Phase | Duration | Dependencies | Start Date |
|-------|----------|--------------|------------|
| Phase 1: UML Enhancement | 8h | None | Week 1 Day 1 |
| Phase 2: Domain Entity Detection | 14h | Phase 1 | Week 1 Day 2 |
| Phase 3: Database Schema | 10h | None | Week 2 Day 1 |
| Phase 4: API Mapping | 6h | Phase 2 | Week 2 Day 3 |
| Phase 5: Universal Support | 4h | Phases 2-4 | Week 2 Day 4 |
| **Total** | **42h** | - | **~1 week** |

---

## 🔗 Related Documents

- **Current Dashboard Implementation:** `src/dashboard/` (Clean Architecture)
- **UML Generation Module:** `src/use_cases/render_uml_diagrams.py`
- **Dashboard Renderer:** `src/dashboard/presentation/dashboard_renderer.py`
- **Dashboard Template:** `src/dashboard/presentation/templates/dashboard.html`
- **Application Health Orchestrator:** `src/orchestrators/application_health_orchestrator.py`
- **Consolidated Plan:** `cortex-brain/documents/planning/features/CONSOLIDATED-PLAN-SUMMARY.md`

---

## 🎯 Next Steps

1. **Approve Plan** - Review and approve enhancement plan
2. **Phase 1 Kickoff** - Start UML integration enhancement (8 hours)
3. **Entity Detection** - Implement multi-language entity detection (14 hours)
4. **Database Schema** - Add database reverse-engineering (10 hours)
5. **API Mapping** - Implement API endpoint detection (6 hours)
6. **Universal Support** - Enable API-only and database-only projects (4 hours)

**Commands:**
- `approve plan APPLICATION-DASHBOARD-ENHANCEMENTS-PLAN`
- `start phase 1 uml enhancement`
- `run tests for dashboard enhancements`

---

**End of Plan** 🧠
