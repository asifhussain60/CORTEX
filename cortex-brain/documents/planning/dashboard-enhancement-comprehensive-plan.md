# Dashboard Enhancement Comprehensive Plan

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 5, 2025  
**Version:** 1.0.0  
**Status:** PLANNING

---

## Executive Summary

This plan outlines comprehensive enhancements to CORTEX's dashboard data collectors and schema to support **universal project analysis** across diverse technology stacks, architectures, and scales. The current system, designed for smaller API projects, will be redesigned to handle:

- **Large-scale web applications** (10K+ files, 500K+ LOC)
- **Multi-language ecosystems** (C#, ColdFusion, TypeScript, Python, SQL, etc.)
- **Complex architectures** (N-Tier MVC, SOA, Microservices, Monoliths)
- **Multiple database platforms** (SQL Azure, Oracle, SQL Server, PostgreSQL)
- **Full-stack applications** (Frontend + Backend + Database + Infrastructure)

### Analysis Results

**Repositories Analyzed:**

| Repository | Type | Scale | Key Technologies |
|------------|------|-------|------------------|
| **luum-fresh** | Multi-app MVC Suite | ~4,835 C# files, 4,822 SQL files | C# MVC, .NET Core, SQL Azure, Web API, Background Jobs, SFTP, Azure Functions |
| **V5.ColdFusion** | Enterprise App Suite | ~2,694 CFM files, 1,442 Python files | ColdFusion, Oracle, Python scripts, Email workflows |
| **TCBULK** | Full-Stack Angular | ~377 Python, 243 C#, 172 TS files | Angular 12+, .NET Core API, SQL Server, SSRS Reports |
| **V5.PrevalidationWS** (baseline) | SOAP Web Service | ~50 files | C# SOAP, Oracle, Web API |

---

## 🎯 Current State Analysis

### Existing Dashboard Collectors

**Location:** `src/dashboard/data/`

| Collector | Focus | Limitations |
|-----------|-------|-------------|
| `tech_stack_collector.py` | Detect languages, frameworks, libraries | Only supports `package.json`, `requirements.txt`, `.csproj`, `packages.config` |
| `architecture_collector.py` | Analyze tiers, components, endpoints | Limited .NET support, no ColdFusion/Angular detection |
| `code_org_collector.py` | Complexity, hotspots, duplications | Python/C# only, struggles with 4K+ files |
| `security_collector.py` | Security issues, vulnerabilities | Basic pattern matching, no OWASP Top 10 mapping |
| `team_metrics_collector.py` | Git activity, contributors | Works well, needs scale optimization |
| `vendor_detector.py` | External dependencies | Limited to NuGet/npm/pip |

### Current Schema Structure

**File:** `cortex-brain/dashboards/schema/health-data-schema.json`

**Strengths:**
- ✅ Standardized metadata structure
- ✅ Health scoring system
- ✅ Code metrics foundation
- ✅ Testing metrics support

**Gaps:**
- ❌ No frontend/backend separation for full-stack apps
- ❌ No database schema analysis (tables, procedures, views)
- ❌ No API endpoint documentation (REST, SOAP, GraphQL)
- ❌ No microservice dependency mapping
- ❌ No infrastructure-as-code detection (Azure, AWS, Terraform)
- ❌ No multi-language complexity scoring
- ❌ No business domain model extraction

---

## 🚀 Enhancement Goals

### Primary Objectives

1. **Universal Language Support**
   - C#, TypeScript, JavaScript, Python, ColdFusion, SQL, HTML/CSS, Java, Go, Rust
   - Framework detection: MVC, Angular, React, Vue, Blazor, Spring, Django, Express

2. **Comprehensive Architecture Analysis**
   - Full-stack layer detection (UI → API → Business → Data → Infrastructure)
   - Microservices topology mapping
   - Database schema visualization (ERD generation)
   - API contract extraction (Swagger, WSDL, GraphQL schemas)

3. **Scalability for Large Codebases**
   - Handle 10K+ files without timeout
   - Parallel processing with worker pools
   - Incremental/cached analysis
   - Selective deep-scan mode

4. **Enhanced Metrics**
   - Business domain complexity (entities, workflows, rules)
   - Cross-layer coupling analysis
   - Performance hotspots (N+1 queries, inefficient algorithms)
   - Security posture scoring (OWASP Top 10 compliance)

5. **Multi-Database Platform Support**
   - SQL Azure, Oracle, SQL Server, PostgreSQL, MySQL
   - NoSQL: MongoDB, Redis, CosmosDB
   - Schema diff tracking, migration history

---

## 📐 Proposed Architecture

### 1. Universal Data Schema v2.0

**File:** `cortex-brain/dashboards/schema/universal-dashboard-schema-v2.json`

#### Schema Structure

```json
{
  "schema_version": "2.0.0",
  "metadata": {
    "project_name": "string",
    "project_type": "web_app|api|microservices|database|library|monolith",
    "primary_languages": ["C#", "TypeScript", "SQL"],
    "repository_url": "string",
    "branch": "string",
    "scan_timestamp": "ISO8601",
    "scan_duration_seconds": 0,
    "total_files_scanned": 0
  },
  
  "architecture": {
    "type": "n-tier|microservices|monolith|soa|serverless",
    "layers": [
      {
        "name": "Presentation|Business|Data|Infrastructure",
        "path": "relative/path",
        "technology": "Angular|MVC|Web API|Entity Framework",
        "file_count": 0,
        "loc": 0,
        "dependencies": ["layer_name"]
      }
    ],
    "components": [
      {
        "name": "ComponentName",
        "type": "module|service|controller|repository|view",
        "path": "path/to/component",
        "dependencies": ["component_name"],
        "complexity_score": 0,
        "change_frequency": 0
      }
    ],
    "microservices": [
      {
        "name": "ServiceName",
        "type": "rest_api|grpc|event_driven",
        "endpoints": 0,
        "dependencies": ["service_name"],
        "database": "db_name"
      }
    ]
  },
  
  "frontend": {
    "framework": "Angular|React|Vue|MVC Razor|Blazor",
    "version": "string",
    "components_count": 0,
    "routes_count": 0,
    "state_management": "NgRx|Redux|Vuex|None",
    "ui_library": "Material|Bootstrap|Tailwind",
    "bundle_size_kb": 0,
    "dependencies": [
      {
        "name": "string",
        "version": "string",
        "type": "production|dev"
      }
    ],
    "pages": [
      {
        "route": "/path",
        "component": "ComponentName",
        "complexity": 0,
        "api_calls": ["endpoint"]
      }
    ]
  },
  
  "backend": {
    "framework": ".NET Core|Express|Django|Spring|ColdFusion",
    "version": "string",
    "api_type": "REST|SOAP|GraphQL|gRPC",
    "endpoints": [
      {
        "path": "/api/resource",
        "method": "GET|POST|PUT|DELETE",
        "controller": "ControllerName",
        "authentication": "JWT|OAuth|None",
        "complexity": 0,
        "dependencies": ["service_name"]
      }
    ],
    "services": [
      {
        "name": "ServiceName",
        "type": "business_logic|data_access|integration",
        "methods_count": 0,
        "dependencies": ["service_name"]
      }
    ],
    "middleware": ["Authentication", "Logging", "CORS"],
    "background_jobs": [
      {
        "name": "JobName",
        "schedule": "cron_expression",
        "purpose": "description"
      }
    ]
  },
  
  "database": {
    "platform": "SQL Azure|Oracle|SQL Server|PostgreSQL|MySQL|MongoDB",
    "version": "string",
    "schema": {
      "tables": [
        {
          "name": "TableName",
          "columns_count": 0,
          "rows_estimate": 0,
          "indexes": 0,
          "foreign_keys": 0,
          "triggers": 0
        }
      ],
      "views": [
        {
          "name": "ViewName",
          "complexity": 0,
          "dependencies": ["table_name"]
        }
      ],
      "stored_procedures": [
        {
          "name": "ProcedureName",
          "parameters_count": 0,
          "loc": 0,
          "complexity": 0
        }
      ],
      "functions": [
        {
          "name": "FunctionName",
          "type": "scalar|table_valued",
          "complexity": 0
        }
      ],
      "user_defined_types": []
    },
    "orm": "Entity Framework|Hibernate|Dapper|None",
    "migrations": {
      "count": 0,
      "pending": 0
    }
  },
  
  "infrastructure": {
    "cloud_provider": "Azure|AWS|GCP|On-Premise",
    "deployment_type": "App Service|Kubernetes|VM|Serverless",
    "ci_cd": "Azure DevOps|GitHub Actions|Jenkins|GitLab CI",
    "iac_tool": "ARM Templates|Terraform|CloudFormation|None",
    "monitoring": ["Application Insights", "CloudWatch", "Datadog"],
    "configuration": {
      "files": ["appsettings.json", "web.config"],
      "secrets_management": "Key Vault|Secrets Manager|Environment Variables"
    }
  },
  
  "code_metrics": {
    "languages": {
      "C#": {
        "files": 0,
        "loc": 0,
        "classes": 0,
        "methods": 0,
        "avg_complexity": 0
      },
      "TypeScript": {
        "files": 0,
        "loc": 0,
        "components": 0,
        "services": 0
      },
      "SQL": {
        "files": 0,
        "loc": 0,
        "tables": 0,
        "procedures": 0,
        "views": 0
      }
    },
    "complexity": {
      "cyclomatic_avg": 0,
      "cognitive_avg": 0,
      "halstead_difficulty": 0,
      "maintainability_index": 0
    },
    "quality": {
      "code_smells": 0,
      "technical_debt_hours": 0,
      "duplication_pct": 0,
      "comment_ratio": 0
    },
    "hotspots": [
      {
        "file": "path/to/file",
        "complexity": 0,
        "change_frequency": 0,
        "last_modified": "ISO8601",
        "risk_score": 0
      }
    ]
  },
  
  "security": {
    "overall_score": 0,
    "vulnerabilities": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 0
    },
    "owasp_top_10": [
      {
        "category": "A01:2021 - Broken Access Control",
        "risk_level": "high|medium|low",
        "instances": 0,
        "files": ["path/to/file"]
      }
    ],
    "dependency_vulnerabilities": [
      {
        "package": "package_name",
        "version": "version",
        "severity": "critical|high|medium|low",
        "cve": "CVE-2023-XXXXX"
      }
    ],
    "secrets_exposed": 0,
    "ssl_tls_issues": 0
  },
  
  "testing": {
    "unit_tests": {
      "count": 0,
      "coverage_pct": 0,
      "pass_rate": 0
    },
    "integration_tests": {
      "count": 0,
      "coverage_pct": 0
    },
    "e2e_tests": {
      "count": 0,
      "framework": "Protractor|Cypress|Playwright"
    },
    "test_quality": {
      "assertion_density": 0,
      "test_smells": 0
    }
  },
  
  "business_domain": {
    "entities": [
      {
        "name": "EntityName",
        "type": "aggregate|entity|value_object",
        "properties_count": 0,
        "relationships": ["entity_name"]
      }
    ],
    "workflows": [
      {
        "name": "WorkflowName",
        "steps": 0,
        "complexity": 0
      }
    ],
    "business_rules": 0
  },
  
  "documentation": {
    "readme_present": true,
    "api_documentation": "Swagger|Postman|None",
    "architecture_diagrams": 0,
    "inline_comments_pct": 0,
    "documentation_score": 0
  },
  
  "health": {
    "overall_score": 0,
    "trend": "improving|stable|degrading",
    "status": "healthy|warning|critical",
    "last_deployment": "ISO8601",
    "incidents_30d": 0
  }
}
```

---

### 2. Collector Architecture Redesign

#### Hierarchical Collector System

```
┌─────────────────────────────────────────┐
│   ParallelCollectorOrchestrator        │
│   (Main Coordinator)                    │
└────────────────┬────────────────────────┘
                 │
      ┌──────────┴──────────────────────────────────────┐
      │                                                  │
┌─────▼──────────────┐                    ┌─────────────▼───────┐
│ UniversalCollector │                    │  CachedCollector    │
│ (Language Agnostic)│                    │  (Incremental Mode) │
└─────┬──────────────┘                    └─────────────────────┘
      │
      ├───► ArchitectureAnalyzer (Detects layers, components)
      ├───► FrontendAnalyzer (Angular, React, Vue, MVC Razor)
      ├───► BackendAnalyzer (API, Services, Controllers)
      ├───► DatabaseAnalyzer (Schema extraction, migrations)
      ├───► InfrastructureAnalyzer (Cloud, CI/CD, IaC)
      ├───► SecurityAnalyzer (OWASP, CVE, secrets)
      ├───► MetricsAnalyzer (Complexity, quality, hotspots)
      ├───► TestingAnalyzer (Coverage, test quality)
      └───► BusinessDomainAnalyzer (Entities, workflows)
```

#### Language-Specific Parsers

```
┌──────────────────────────────────────────────┐
│           Language Parser Factory            │
└────────────────┬─────────────────────────────┘
                 │
      ┌──────────┴──────────────────────────────┐
      │                                          │
┌─────▼──────────┐   ┌──────────┐   ┌──────────▼───────┐
│ CSharpParser   │   │  TSParser│   │ ColdFusionParser │
│ (AST Analysis) │   │ (Angular)│   │ (CFM/CFC)        │
└────────────────┘   └──────────┘   └──────────────────┘
      │
      ├───► Extract Classes, Methods, Properties
      ├───► Calculate Complexity (Cyclomatic, Cognitive)
      ├───► Detect Patterns (MVC, DI, Repository)
      ├───► Extract API Endpoints (Attributes)
      └───► Identify Dependencies (Using statements)
```

---

### 3. Performance Optimization Strategy

#### Problem: Current collectors timeout on 4K+ files

**Solutions:**

1. **Parallel Worker Pools**
   ```python
   class ScalableCollectorOrchestrator:
       def __init__(self, max_workers=None):
           self.max_workers = max_workers or (os.cpu_count() * 2)
           self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
       
       def collect_parallel(self, files):
           chunks = self._chunk_files(files, chunk_size=100)
           futures = [
               self.executor.submit(self._process_chunk, chunk)
               for chunk in chunks
           ]
           return [f.result() for f in as_completed(futures)]
   ```

2. **File Streaming (Not Loading All Content)**
   ```python
   def analyze_file_streaming(file_path):
       """Read file in chunks, analyze incrementally"""
       with open(file_path, 'r', encoding='utf-8') as f:
           for chunk in iter(lambda: f.read(8192), ''):
               yield analyze_chunk(chunk)
   ```

3. **Selective Deep Scanning**
   - **Quick Scan:** File counts, extensions, sizes (< 1 second)
   - **Standard Scan:** + Complexity, dependencies (< 30 seconds)
   - **Deep Scan:** + AST analysis, security auditing (< 2 minutes)

4. **Incremental/Cached Analysis**
   ```python
   class CachedCollector:
       def __init__(self, cache_dir):
           self.cache = SQLiteCache(cache_dir)
       
       def collect(self, file_path):
           file_hash = self._hash_file(file_path)
           cached = self.cache.get(file_hash)
           if cached and not self._file_changed(file_path, cached):
               return cached['data']
           
           data = self._analyze_fresh(file_path)
           self.cache.set(file_hash, data)
           return data
   ```

5. **Progressive Results Streaming**
   - Emit partial results as collectors complete
   - Dashboard updates in real-time
   - No blocking until all collectors finish

---

## 📋 Implementation Plan

### Phase 1: Schema Extension (Week 1)

**Deliverables:**
- ✅ `universal-dashboard-schema-v2.json` (complete schema definition)
- ✅ Schema validator with backward compatibility
- ✅ Migration script from v1 → v2

**Tasks:**
1. Define complete v2.0 schema with all sections
2. Add JSON Schema validators for each section
3. Create schema migration utility
4. Update mock data generators for testing
5. Document schema with examples

### Phase 2: Core Infrastructure (Week 1-2)

**Deliverables:**
- ✅ `UniversalCollectorBase` (language-agnostic foundation)
- ✅ `LanguageParserFactory` (pluggable parser system)
- ✅ `ScalableCollectorOrchestrator` (parallel processing)
- ✅ `CachedCollectorWrapper` (incremental mode)

**Tasks:**
1. Refactor `BaseDataCollector` → `UniversalCollectorBase`
2. Implement file chunking and parallel processing
3. Add SQLite-based caching layer
4. Create progress tracking and cancellation support
5. Build language detection utility

### Phase 3: Language-Specific Analyzers (Week 2-3)

**Deliverables:**
- ✅ `CSharpAnalyzer` (Classes, methods, MVC patterns, Web API)
- ✅ `TypeScriptAnalyzer` (Angular components, services, routing)
- ✅ `ColdFusionAnalyzer` (CFM pages, CFC components, queries)
- ✅ `SQLAnalyzer` (T-SQL, PL/SQL schema extraction)
- ✅ Enhanced `PythonAnalyzer` and `JavaScriptAnalyzer`

**Tasks:**

#### CSharpAnalyzer
```python
class CSharpAnalyzer(LanguageAnalyzer):
    def analyze(self, file_path):
        return {
            "classes": self._extract_classes(),
            "methods": self._extract_methods(),
            "complexity": self._calculate_complexity(),
            "mvc_controllers": self._detect_controllers(),
            "web_api_endpoints": self._extract_api_routes(),
            "dependency_injection": self._detect_di_patterns(),
            "orm_usage": self._detect_entity_framework(),
            "linq_queries": self._extract_linq()
        }
```

#### TypeScriptAnalyzer
```python
class TypeScriptAnalyzer(LanguageAnalyzer):
    def analyze(self, file_path):
        return {
            "components": self._extract_angular_components(),
            "services": self._extract_services(),
            "routes": self._extract_routing(),
            "rxjs_usage": self._detect_rxjs_patterns(),
            "state_management": self._detect_ngrx(),
            "api_calls": self._extract_http_calls()
        }
```

#### ColdFusionAnalyzer
```python
class ColdFusionAnalyzer(LanguageAnalyzer):
    def analyze(self, file_path):
        return {
            "cfm_pages": self._extract_cfm_pages(),
            "cfc_components": self._extract_cfc_components(),
            "cf_queries": self._extract_cfquery(),
            "includes": self._extract_cfinclude(),
            "functions": self._extract_functions(),
            "orm_usage": self._detect_cf_orm()
        }
```

#### SQLAnalyzer
```python
class SQLAnalyzer(LanguageAnalyzer):
    def analyze(self, file_path, db_type='sql_server'):
        return {
            "tables": self._extract_tables(),
            "views": self._extract_views(),
            "stored_procedures": self._extract_procedures(),
            "functions": self._extract_functions(),
            "triggers": self._extract_triggers(),
            "indexes": self._extract_indexes(),
            "foreign_keys": self._extract_fk_relationships(),
            "complexity": self._calculate_sql_complexity()
        }
```

### Phase 4: Specialized Collectors (Week 3-4)

**Deliverables:**
- ✅ `ArchitectureCollectorV2` (Full-stack layer detection)
- ✅ `FrontendCollector` (Angular/React/Vue/MVC analysis)
- ✅ `BackendCollector` (API endpoints, services, middleware)
- ✅ `DatabaseCollector` (Schema extraction, migrations)
- ✅ `InfrastructureCollector` (Cloud, CI/CD, IaC)
- ✅ `SecurityCollectorV2` (OWASP Top 10, CVE scanning)

**Architecture Detection Enhancements:**

```python
class ArchitectureCollectorV2:
    def detect_architecture(self):
        """Detect multi-tier, microservices, or monolith"""
        layers = {
            "presentation": self._detect_presentation_layer(),
            "business": self._detect_business_layer(),
            "data": self._detect_data_layer(),
            "infrastructure": self._detect_infrastructure_layer()
        }
        
        # For luum-fresh example:
        if self._has_mvc_structure() and self._has_api_layer():
            return "N-Tier Full-Stack (MVC + Web API)"
        elif self._has_microservices_structure():
            return "Microservices"
        elif self._is_monolith():
            return "Monolith"
    
    def _detect_presentation_layer(self):
        """Detect UI layer"""
        patterns = {
            "mvc_razor": ["Views", "Controllers", "*.cshtml"],
            "angular": ["ClientApp", "src/app", "*.component.ts"],
            "react": ["src/components", "*.jsx"],
            "coldfusion": ["*.cfm", "view/*"]
        }
        # Return detected patterns with file counts
```

**Database Collector:**

```python
class DatabaseCollector:
    def collect_schema(self, db_type):
        """Extract database schema from SQL files or live connection"""
        if self._has_sql_project():
            return self._analyze_sql_project()
        elif self._has_migrations():
            return self._analyze_migrations()
        elif self._has_db_connection():
            return self._query_live_schema()
    
    def _analyze_sql_project(self):
        """For TCBULK's HQY.TCCARD.Database.sqlproj"""
        return {
            "tables": self._parse_table_definitions(),
            "views": self._parse_views(),
            "procedures": self._parse_procedures(),
            "relationships": self._build_erd()
        }
```

### Phase 5: Testing & Validation (Week 4)

**Deliverables:**
- ✅ Comprehensive test suite for all analyzers
- ✅ Performance benchmarks (10K+ files)
- ✅ Validation against all 3 repositories
- ✅ Dashboard UI updates for new data

**Validation Matrix:**

| Repository | Quick Scan | Standard Scan | Deep Scan | Pass Criteria |
|------------|------------|---------------|-----------|---------------|
| luum-fresh | < 5s | < 30s | < 2m | All layers detected, 17 API endpoints, SQL schema extracted |
| V5.ColdFusion | < 3s | < 20s | < 90s | CFM/CFC detected, Oracle connections, Python scripts |
| TCBULK | < 2s | < 15s | < 60s | Angular components, C# API, SQL Server schema, SSRS reports |

### Phase 6: Documentation & Rollout (Week 4-5)

**Deliverables:**
- ✅ Updated user documentation
- ✅ API reference for new collectors
- ✅ Migration guide from v1 collectors
- ✅ Dashboard tutorial with examples
- ✅ Performance tuning guide

---

## 🔬 Technology Stack Analysis

### luum-fresh (Multi-App MVC Suite)

**Structure:**
```
Source/
├── Luum (Core Business Logic - ~60 domain folders)
├── Luum.Web (MVC Presentation - Razor views, Controllers)
├── Luum.Api (Web API - 17 controllers)
├── Luum.Core (Shared utilities, services)
├── Luum.Database (SQL Azure schema - Tables, Views, Procedures)
├── Luum.BackgroundQueue (Hangfire jobs)
├── Luum.Azure (ARM templates, Azure Functions)
├── Luum.UnitTests (xUnit tests)
└── Luum.IntegrationTests
```

**Key Technologies:**
- **Frontend:** MVC Razor views, jQuery, custom JavaScript
- **Backend:** ASP.NET MVC, Web API 2, .NET Framework 4.7+
- **Database:** SQL Azure (4,822 SQL files - tables, views, procedures)
- **ORM:** ADO.NET, Entity Framework (partial)
- **DI:** Autofac
- **Cloud:** Azure App Service, Azure Functions, Key Vault, Application Insights
- **Background Jobs:** Hangfire
- **Testing:** xUnit, Moq
- **Build:** MSBuild, Azure DevOps pipelines

**Collector Requirements:**
- Detect N-Tier MVC architecture
- Extract 17 API endpoints from controllers
- Analyze SQL Azure schema (tables, views, procedures, functions)
- Map MVC routes to controller actions
- Detect business domain entities (Accounts, Benefits, Commute, Payroll, etc.)
- Extract Azure resource dependencies
- Analyze Hangfire background job scheduling

### V5.ColdFusion (Enterprise App Suite)

**Structure:**
```
V5.ColdFusion/
├── AdjustmentManager (CFM app)
├── CatalogManager (CFM app)
├── CommonCFCs (Shared ColdFusion Components)
├── PayrollManager (CFM app)
├── ProcessManager (CFM app)
├── FulfillmentManager (CFM app)
├── CommuterPaymentManager (CFM app)
└── Common (Shared resources - CSS, JS, images, models, views)
```

**Key Technologies:**
- **Frontend:** ColdFusion pages (CFM), custom CSS/JavaScript
- **Backend:** ColdFusion Components (CFC), CFQuery
- **Database:** Oracle (PL/SQL procedures, packages)
- **Python Scripts:** 1,442 Python files (utilities, automation)
- **Email:** Email workflows (EmailManager)

**Collector Requirements:**
- Parse CFM files for page structure and logic
- Extract CFC components (methods, properties)
- Detect CFQuery database calls
- Analyze CFInclude dependencies
- Map application suite interconnections
- Detect Oracle database usage patterns
- Analyze Python utility scripts

### TCBULK (Full-Stack Angular)

**Structure:**
```
HQY.TCCARD/
├── HQY.TCCARD.Web (Angular + .NET Core)
│   ├── ClientApp (Angular 12+)
│   │   └── src/app (15 feature modules)
│   ├── Controllers (C# Web API)
│   └── Views (MVC fallback)
├── HQY.TCCARD.Business (Business logic layer)
├── HQY.TCCARD.Data (Entity Framework repository layer)
├── HQY.TCCARD.Domain (Domain entities)
├── HQY.TCCARD.Database (SQL Server .sqlproj)
└── HQY.TCCARD.Reports (SSRS reports - RDL files)
```

**Key Technologies:**
- **Frontend:** Angular 12+, TypeScript, RxJS, Angular Material
- **Backend:** .NET Core Web API, C#
- **Database:** SQL Server (107 SQL files - schema, migrations)
- **ORM:** Entity Framework Core
- **Reports:** SQL Server Reporting Services (SSRS - 8 RDL files)
- **Testing:** Jasmine/Karma (frontend), xUnit (backend)
- **Build:** Angular CLI, MSBuild

**Collector Requirements:**
- Detect Angular architecture (components, services, modules, routing)
- Extract API endpoints from C# controllers
- Analyze Entity Framework models and DbContext
- Map frontend → backend → database flow
- Extract SSRS report definitions
- Calculate Angular component complexity
- Detect RxJS patterns and state management

---

## 💾 Data Storage Strategy

### Current: Per-Project JSON Files
```
cortex-brain/dashboards/
└── {project-name}/
    ├── metadata.json
    ├── architecture.json
    ├── tech-stack.json
    ├── code-organization.json
    ├── security.json
    ├── team-metrics.json
    └── vendors.json
```

### Enhanced: Consolidated + Modular
```
cortex-brain/dashboards/
└── {project-name}/
    ├── dashboard-data-v2.json (Main consolidated file)
    ├── metadata.json (Basic info, scan timestamp)
    └── modules/ (Optional detailed breakdowns)
        ├── frontend-detailed.json
        ├── backend-detailed.json
        ├── database-schema.json
        ├── api-documentation.json
        └── security-audit.json
```

**Rationale:**
- **Consolidated:** Faster dashboard loading (1 HTTP request vs 7)
- **Modular:** Deep-dive views can lazy-load detailed modules
- **Backward Compatible:** v1 files remain for legacy dashboards

---

## 🎯 Success Metrics

### Performance Targets

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Small project (< 100 files) | 5s | 2s | 60% faster |
| Medium project (100-1K files) | 30s | 10s | 67% faster |
| Large project (1K-5K files) | Timeout (> 2m) | 30s | 75% faster |
| XL project (5K-10K files) | N/A | 60s | New capability |

### Coverage Targets

| Language/Framework | Current Support | Target | Status |
|--------------------|----------------|--------|--------|
| C# / .NET | 60% | 95% | Enhancement needed |
| TypeScript / Angular | 30% | 90% | New analyzer |
| JavaScript / React | 50% | 85% | Enhancement needed |
| Python | 80% | 95% | Minor improvements |
| ColdFusion | 0% | 80% | New analyzer |
| SQL (T-SQL, PL/SQL) | 20% | 85% | New analyzer |
| Java / Spring | 0% | 70% | Future phase |

### Quality Targets

| Metric | Target |
|--------|--------|
| Schema validation pass rate | 100% |
| Collector error rate | < 2% |
| False positive detection | < 5% |
| Dashboard load time | < 1s |
| Data freshness | Real-time / on-demand |

### UI Enhancement Targets

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Tabs shown for API project | 6 (all) | 4-5 (relevant) | 25% cleaner |
| Tabs shown for Full-Stack | 6 (all) | 10-12 (comprehensive) | 2x more info |
| Initial render time | 800ms | 300ms | 62% faster |
| Tab switch latency | 200ms | 50ms | 75% faster |
| Mobile usability score | 65/100 | 90/100 | 38% improvement |
| Accessibility score | 72/100 | 95/100 | 32% improvement |

---

## 🚧 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Large codebases timeout | High | High | Parallel processing, incremental mode, selective scanning |
| AST parsing errors | Medium | Medium | Fallback to regex patterns, error isolation per file |
| Language-specific edge cases | Medium | High | Comprehensive test suite, gradual rollout |
| Schema breaking changes | High | Low | Versioning, migration scripts, backward compatibility |
| Memory consumption | Medium | Medium | Streaming analysis, garbage collection, chunked processing |

---

## 🎨 Dashboard UI Enhancement - Adaptive Intelligence

### Overview

The enhanced dashboard will implement **context-aware component visibility** that dynamically shows/hides tabs, sections, and visualizations based on project type and available data. This ensures users only see relevant information without cluttering the interface with inapplicable sections.

### Current UI Structure

**Fixed Tabs (6):**
1. Overview - Health score, metrics summary
2. Architecture - Application type, tiers, components
3. Tech Stack - Languages, frameworks, libraries
4. Code Organization - Complexity, hotspots, duplications
5. Security - Vulnerabilities, OWASP issues
6. Vendors - Third-party dependencies

**Limitations:**
- ❌ All tabs always visible regardless of project type
- ❌ Empty sections shown when data unavailable
- ❌ No frontend/backend separation
- ❌ No database/API-specific views
- ❌ No project type indicators

---

### Enhanced UI Architecture

#### Project Type Detection & Tab Visibility

**Automatic Classification:**
```javascript
class ProjectTypeDetector {
    static detectProjectType(dashboardData) {
        const features = {
            hasFrontend: dashboardData.frontend?.components_count > 0,
            hasBackend: dashboardData.backend?.endpoints?.length > 0,
            hasDatabase: dashboardData.database?.schema?.tables?.length > 0,
            hasUI: dashboardData.frontend?.framework !== null,
            isAPI: dashboardData.backend?.api_type !== null,
            isMicroservices: dashboardData.architecture?.type === 'microservices',
            isLibrary: dashboardData.metadata?.project_type === 'library',
            isFullStack: null,
            isDatabaseProject: null
        };
        
        // Determine full-stack
        features.isFullStack = features.hasFrontend && features.hasBackend;
        
        // Determine database-only project
        features.isDatabaseProject = features.hasDatabase && 
                                      !features.hasFrontend && 
                                      !features.hasBackend;
        
        return {
            type: this._classifyType(features),
            features: features
        };
    }
    
    static _classifyType(features) {
        if (features.isFullStack) return 'full_stack';
        if (features.isDatabaseProject) return 'database';
        if (features.isAPI && !features.hasUI) return 'api';
        if (features.isMicroservices) return 'microservices';
        if (features.isLibrary) return 'library';
        if (features.hasFrontend) return 'frontend';
        return 'unknown';
    }
}
```

#### Adaptive Tab Configuration

**Tab Visibility Matrix:**

| Tab | Full-Stack | API Only | Frontend Only | Database Only | Microservices | Library |
|-----|------------|----------|---------------|---------------|---------------|---------|
| Overview | ✅ Always | ✅ Always | ✅ Always | ✅ Always | ✅ Always | ✅ Always |
| Architecture | ✅ Full view | ✅ Backend only | ✅ Frontend only | ✅ Schema only | ✅ Services map | ✅ Module structure |
| **Frontend** (NEW) | ✅ Show | ❌ Hide | ✅ Show | ❌ Hide | ✅ If UI exists | ❌ Hide |
| **Backend** (NEW) | ✅ Show | ✅ Show | ❌ Hide | ❌ Hide | ✅ Show | ✅ Show |
| **Database** (NEW) | ✅ Show | ✅ If DB used | ❌ Hide | ✅ Show | ✅ If DB used | ❌ Hide |
| **API Documentation** (NEW) | ✅ Show | ✅ Show | ❌ Hide | ❌ Hide | ✅ Show | ✅ If API exposed |
| Tech Stack | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show |
| Code Organization | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show |
| Security | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show |
| Testing | ✅ Show | ✅ Show | ✅ Show | ✅ If tests | ✅ Show | ✅ Show |
| **Infrastructure** (NEW) | ✅ Show | ✅ If deployed | ✅ If deployed | ✅ If deployed | ✅ Show | ❌ Hide |
| **Business Domain** (NEW) | ✅ Show | ✅ If entities | ❌ Hide | ✅ If entities | ✅ Show | ❌ Hide |
| Vendors | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show | ✅ Show |

**Implementation:**
```javascript
class AdaptiveTabManager {
    constructor(dashboardData) {
        this.data = dashboardData;
        this.projectType = ProjectTypeDetector.detectProjectType(dashboardData);
        this.tabs = this._buildTabConfiguration();
    }
    
    _buildTabConfiguration() {
        const tabs = [
            { id: 'overview', label: 'Overview', icon: '📊', alwaysShow: true },
            { id: 'architecture', label: 'Architecture', icon: '🏗️', alwaysShow: true },
            { 
                id: 'frontend', 
                label: 'Frontend', 
                icon: '🎨', 
                condition: () => this.projectType.features.hasFrontend,
                badge: () => this.data.frontend?.components_count || 0
            },
            { 
                id: 'backend', 
                label: 'Backend', 
                icon: '⚙️', 
                condition: () => this.projectType.features.hasBackend,
                badge: () => this.data.backend?.endpoints?.length || 0
            },
            { 
                id: 'database', 
                label: 'Database', 
                icon: '🗄️', 
                condition: () => this.projectType.features.hasDatabase,
                badge: () => this.data.database?.schema?.tables?.length || 0
            },
            { 
                id: 'api-docs', 
                label: 'API Docs', 
                icon: '📡', 
                condition: () => this.data.backend?.api_type !== null,
                badge: () => this.data.backend?.endpoints?.length || 0
            },
            { id: 'tech-stack', label: 'Tech Stack', icon: '🛠️', alwaysShow: true },
            { id: 'code-org', label: 'Code Quality', icon: '📈', alwaysShow: true },
            { id: 'security', label: 'Security', icon: '🔒', alwaysShow: true },
            { 
                id: 'testing', 
                label: 'Testing', 
                icon: '🧪', 
                condition: () => (this.data.testing?.unit_tests?.count || 0) > 0,
                badge: () => {
                    const coverage = this.data.testing?.unit_tests?.coverage_pct || 0;
                    return `${coverage}%`;
                }
            },
            { 
                id: 'infrastructure', 
                label: 'Infrastructure', 
                icon: '☁️', 
                condition: () => this.data.infrastructure?.cloud_provider !== null
            },
            { 
                id: 'business-domain', 
                label: 'Business Domain', 
                icon: '💼', 
                condition: () => (this.data.business_domain?.entities?.length || 0) > 0
            },
            { id: 'vendors', label: 'Dependencies', icon: '📦', alwaysShow: true }
        ];
        
        // Filter tabs based on conditions
        return tabs.filter(tab => {
            if (tab.alwaysShow) return true;
            if (tab.condition) return tab.condition();
            return true;
        });
    }
    
    getVisibleTabs() {
        return this.tabs;
    }
    
    renderTabs() {
        const navContainer = document.getElementById('tabNavigation');
        navContainer.innerHTML = this.tabs.map(tab => `
            <button class="nav-tab" data-tab="${tab.id}" title="${tab.label}">
                <span class="tab-icon">${tab.icon}</span>
                <span class="tab-label">${tab.label}</span>
                ${tab.badge ? `<span class="tab-badge">${tab.badge()}</span>` : ''}
            </button>
        `).join('');
    }
}
```

---

### New Dashboard Tabs & Visualizations

#### 1. Frontend Tab (Conditional)

**Visibility:** Only if `frontend.framework !== null`

**Sections:**
- **Framework Overview**
  - Framework name, version, bundle size
  - Component count, route count
  - State management detection
  - UI library (Material, Bootstrap, etc.)

- **Component Tree Visualization**
  - Hierarchical tree view of components
  - Parent-child relationships
  - Component complexity heatmap
  - Click to see component details

- **Route Map**
  - Visual route hierarchy
  - Route → Component → API mappings
  - Lazy-loaded routes indicator
  - Guard/middleware annotations

- **Performance Metrics**
  - Bundle size breakdown
  - Component render complexity
  - Unused dependencies
  - Tree-shaking opportunities

- **Dependencies**
  - Production dependencies with versions
  - Dev dependencies
  - Peer dependency warnings
  - Outdated package alerts

**Example for TCBULK (Angular):**
```
📊 Framework: Angular 12.2.0
📦 Bundle Size: 2.4 MB (optimized: 1.8 MB)
🎨 Components: 45 (15 feature modules)
🗺️ Routes: 28 routes
🎭 State Management: NgRx (8 stores, 24 actions)
🎨 UI Library: Angular Material 12.x

Component Breakdown:
├── Core (5 components)
│   ├── Navigation
│   ├── Footer
│   └── Login
├── Account (6 components)
├── Card Management (8 components)
└── Card Search (7 components)
```

#### 2. Backend Tab (Conditional)

**Visibility:** Only if `backend.endpoints.length > 0`

**Sections:**
- **API Overview**
  - Framework, version, API type (REST/SOAP/GraphQL/gRPC)
  - Total endpoints, authentication method
  - Middleware/filters
  - Background jobs

- **Endpoint Explorer**
  - Interactive endpoint list with filters
  - Method (GET/POST/PUT/DELETE), path, controller
  - Authentication requirements
  - Request/response models
  - Complexity score, dependencies

- **Service Architecture**
  - Service layer visualization
  - Business logic services
  - Data access services
  - Integration services
  - Dependency graph

- **API Health**
  - Endpoint complexity distribution
  - Authentication coverage
  - Error handling coverage
  - Validation coverage

- **Background Jobs**
  - Job name, schedule (cron)
  - Purpose, dependencies
  - Execution history (if available)

**Example for luum-fresh (Web API):**
```
⚙️ Framework: ASP.NET Web API 2 (.NET Framework 4.7.2)
📡 API Type: REST
🔐 Authentication: JWT Bearer + Custom Token Manager
🎯 Endpoints: 17 controllers, 89 endpoints

Endpoints by Category:
├── Commute API (3 controllers, 21 endpoints)
├── Connected Accounts (2 controllers, 8 endpoints)
├── Configuration (1 controller, 5 endpoints)
├── Mobile API (4 controllers, 24 endpoints)
└── Integration (7 controllers, 31 endpoints)

Middleware Pipeline:
1. CORS Handler
2. JWT Authentication
3. Global Exception Filter
4. Request Logging
5. Response Compression

Background Jobs (Hangfire):
├── Trip Logging Reminder (Daily @ 6 AM)
├── Payroll Processing (Weekly @ Sunday 2 AM)
├── Email Queue Processor (Every 5 minutes)
└── SFTP File Watcher (Continuous)
```

#### 3. Database Tab (Conditional)

**Visibility:** Only if `database.schema.tables.length > 0`

**Sections:**
- **Database Overview**
  - Platform, version
  - Schema stats (tables, views, procedures, functions)
  - ORM detected
  - Migration status

- **Schema Visualization**
  - Interactive Entity-Relationship Diagram (ERD)
  - Table relationships with foreign keys
  - Index visualization
  - Click table to see details

- **Table Explorer**
  - Sortable/filterable table list
  - Table name, column count, row estimate
  - Indexes, foreign keys, triggers
  - Complexity score

- **Stored Procedure Analyzer**
  - Procedure list with complexity metrics
  - Parameter count, LOC
  - Dependency analysis
  - Performance hints

- **Migration History**
  - Migration timeline
  - Pending migrations
  - Schema version tracking

**Example for luum-fresh (SQL Azure):**
```
🗄️ Database: SQL Azure (SQL Server 2019)
📊 Schema Stats:
   - Tables: 127
   - Views: 38
   - Stored Procedures: 89
   - Functions: 24
   - User-Defined Types: 12

🔗 ORM: Entity Framework 6.4 (partial), ADO.NET

Top 10 Tables by Complexity:
1. Commutes (28 columns, 12 FK, 8 indexes) - 500K+ rows
2. Accounts (22 columns, 8 FK, 6 indexes) - 120K+ rows
3. Transactions (31 columns, 10 FK, 12 indexes) - 2M+ rows
...

Most Complex Stored Procedures:
1. sp_ProcessMonthlyPayroll (287 LOC, complexity: 42)
2. sp_CalculateCommuteBenefits (198 LOC, complexity: 35)
3. sp_GenerateMonthlyReport (156 LOC, complexity: 28)
```

**Example for V5.ColdFusion (Oracle):**
```
🗄️ Database: Oracle 19c
📊 Schema Stats:
   - Tables: 94
   - Views: 22
   - Packages: 15
   - Procedures: 67
   - Functions: 31

🔗 ORM: ColdFusion ORM (Hibernate)

Top PL/SQL Packages:
1. PKG_PAYROLL_PROCESSING (12 procedures, 8 functions)
2. PKG_ADJUSTMENT_CALC (8 procedures, 5 functions)
3. PKG_CATALOG_MANAGER (10 procedures, 3 functions)
```

#### 4. API Documentation Tab (Conditional)

**Visibility:** Only if `backend.api_type !== null`

**Sections:**
- **OpenAPI/Swagger Viewer** (if swagger.json found)
  - Interactive API explorer
  - Try-it-out functionality
  - Request/response examples
  - Authentication testing

- **SOAP WSDL Viewer** (if WSDL found)
  - Service operations
  - Message definitions
  - SOAP envelope examples

- **GraphQL Schema** (if GraphQL detected)
  - Type definitions
  - Query/Mutation/Subscription docs
  - Schema visualization

- **Endpoint Documentation**
  - Auto-generated from code annotations
  - Request/response models
  - Status codes
  - Example payloads

**Example for V5.PrevalidationWS (SOAP):**
```
📡 API Type: SOAP Web Service (ASMX)
📄 WSDL: Available at /WebService.asmx?WSDL

Operations (3):
1. ValidatePSFFile
   - Input: FileContent (base64), EncryptionType, FileSettings
   - Output: ValidationResult (IsValid, Errors[], ProcessedRows)
   - Authentication: Custom Token (CustTokenManager)

2. GetFileConfiguration
   - Input: ConfigurationKey
   - Output: FileSettings (Delimiter, Encoding, Columns)

3. InvalidateCache
   - Input: None
   - Output: CacheInvalidationResult
   - Authorization: Admin only
```

#### 5. Infrastructure Tab (Conditional)

**Visibility:** Only if `infrastructure.cloud_provider !== null`

**Sections:**
- **Cloud Overview**
  - Provider (Azure/AWS/GCP)
  - Deployment type (App Service/Kubernetes/VM/Serverless)
  - Regions, availability zones

- **Resource Topology**
  - Visual diagram of cloud resources
  - App Services, Databases, Storage, Functions
  - Virtual networks, subnets
  - Inter-resource dependencies

- **CI/CD Pipeline**
  - Pipeline tool (Azure DevOps/GitHub Actions/Jenkins)
  - Build/deploy stages
  - Automated testing gates
  - Deployment frequency

- **Infrastructure as Code**
  - IaC tool detected (ARM/Terraform/CloudFormation)
  - Template files found
  - Resource definitions

- **Monitoring & Observability**
  - Monitoring tools (App Insights/CloudWatch/Datadog)
  - Alert rules
  - Log aggregation
  - APM integration

**Example for luum-fresh (Azure):**
```
☁️ Cloud Provider: Microsoft Azure
🚀 Deployment: Azure App Service + Azure Functions

Resources Detected:
├── App Services (3)
│   ├── luum-web-prod (Standard S2, Auto-scale 2-10)
│   ├── luum-api-prod (Standard S2, Auto-scale 2-10)
│   └── luum-admin-prod (Basic B1)
├── Azure Functions (2)
│   ├── BackgroundQueue (Consumption plan)
│   └── SFTP-Processor (Premium EP1)
├── SQL Azure
│   ├── luum-db-prod (Standard S3, 100 DTU)
│   └── luum-warehouse-prod (Standard S2, 50 DTU)
├── Storage Accounts (2)
│   ├── luumfiles (Blob storage, 500 GB)
│   └── luumsftp (File storage, 100 GB)
├── Key Vault
│   └── luum-secrets (23 secrets, 4 certificates)
└── Application Insights
    └── luum-monitoring (Workspace-based)

📋 IaC: ARM Templates (15 files in Luum.Azure/)
🔄 CI/CD: Azure DevOps Pipelines (.pipelines/)
   - Build: .NET Core build, npm build, SQL deploy
   - Deploy: Multi-stage (Dev → QA → Prod)
   - Tests: Unit tests, integration tests
   - Gates: Manual approval for Prod
```

#### 6. Business Domain Tab (Conditional)

**Visibility:** Only if `business_domain.entities.length > 0`

**Sections:**
- **Domain Model Visualization**
  - Entity-relationship diagram
  - Aggregate roots highlighted
  - Value objects
  - Domain events

- **Entity Explorer**
  - Entity list with properties
  - Relationships (1:1, 1:N, M:N)
  - Invariants/rules
  - Click to see usage

- **Workflow Visualization**
  - Business process flows
  - Decision points
  - State transitions
  - Integration points

- **Business Rules**
  - Extracted rules from code
  - Validation rules
  - Calculation logic
  - Policy enforcement

**Example for luum-fresh (Domain-Driven Design):**
```
💼 Domain Model: 42 entities, 18 aggregates

Core Aggregates:
├── Account (Root)
│   ├── AccountSettings (Entity)
│   ├── AccountBalance (Value Object)
│   └── PaymentMethod (Entity)
├── Commute (Root)
│   ├── TripLog (Entity)
│   ├── CommuteMode (Value Object)
│   └── RouteSegment (Value Object)
├── Benefit (Root)
│   ├── BenefitElection (Entity)
│   ├── BenefitAmount (Value Object)
│   └── BenefitEligibility (Value Object)
└── Payroll (Root)
    ├── PayrollCycle (Entity)
    ├── PayrollItem (Entity)
    └── PayrollDeduction (Value Object)

Key Workflows:
1. Trip Logging & Validation (8 steps)
2. Monthly Benefit Calculation (12 steps)
3. Payroll Processing (15 steps)
4. Account Onboarding (6 steps)

Business Rules (Top 10):
1. Commute mode eligibility based on distance
2. Pre-tax benefit limits (IRS regulations)
3. Payroll deduction timing
4. Employer subsidy calculations
...
```

#### 7. Testing Tab (Enhanced)

**Sections:**
- **Test Coverage Overview**
  - Overall coverage percentage with trend
  - Coverage by layer (frontend/backend/database)
  - Coverage heatmap by file

- **Test Suite Breakdown**
  - Unit tests (count, pass rate, coverage)
  - Integration tests
  - E2E tests
  - Performance tests

- **Test Quality Metrics**
  - Assertion density
  - Test smells detected
  - Flaky test detection
  - Test execution time

- **Uncovered Critical Paths**
  - High-complexity code without tests
  - Public API endpoints untested
  - Critical business logic gaps

**Example for TCBULK:**
```
🧪 Test Coverage: 78% overall

Coverage by Layer:
├── Frontend (Angular): 82%
│   ├── Components: 85% (45 of 53)
│   ├── Services: 92% (23 of 25)
│   └── Pipes: 67% (4 of 6)
├── Backend (C# API): 74%
│   ├── Controllers: 68% (15 of 22)
│   ├── Services: 84% (21 of 25)
│   └── Repositories: 91% (10 of 11)
└── Database: 45%
    ├── Stored Procedures: 32% (8 of 25)
    └── Functions: 67% (6 of 9)

Test Suite:
├── Unit Tests: 187 tests, 100% pass rate
├── Integration Tests: 42 tests, 95% pass rate
└── E2E Tests (Protractor): 28 tests, 89% pass rate

⚠️ Critical Gaps:
1. CardTransferController.ProcessBulkTransfer (complexity: 28, coverage: 0%)
2. PaymentService.CalculateFees (complexity: 19, coverage: 0%)
3. sp_GenerateMonthlyStatement (147 LOC, no tests)
```

---

### Enhanced Overview Tab

**Additional Widgets:**

1. **Project Type Badge**
   - Large, prominent badge showing project classification
   - Icon and color-coded
   - Quick facts (e.g., "Full-Stack Angular + .NET Core")

2. **Layer Health Cards**
   - Separate health scores for Frontend, Backend, Database, Infrastructure
   - Only show applicable layers
   - Click to jump to detailed tab

3. **Technology Radar**
   - Visual representation of tech stack currency
   - Concentric circles: Current, Acceptable, Outdated, Deprecated
   - Click technologies to see details

4. **Critical Metrics Dashboard**
   - KPIs based on project type
   - Full-Stack: Frontend coverage, API endpoint count, DB table count
   - API: Endpoint count, authentication, complexity
   - Database: Table count, procedure complexity, migration status

5. **Quick Actions**
   - Context-sensitive actions based on project type
   - "View API Documentation" for API projects
   - "Analyze Database Schema" for DB-heavy projects
   - "Review Component Tree" for frontend projects

---

### Responsive Layout System

#### Desktop View (> 1200px)
```
┌─────────────────────────────────────────────────────┐
│  Sidebar (280px)        │  Main Content (Flex)      │
│  ├── Header             │  ├── Tab Content          │
│  ├── Source Selector    │  ├── Visualizations       │
│  ├── Adaptive Tabs      │  └── Data Grids           │
│  │   ├── Overview       │                            │
│  │   ├── Frontend ✅    │                            │
│  │   ├── Backend ✅     │                            │
│  │   ├── Database ✅    │                            │
│  │   └── ...            │                            │
│  └── Actions            │                            │
└─────────────────────────────────────────────────────┘
```

#### Tablet View (768px - 1200px)
```
┌─────────────────────────────────────────────────────┐
│  Top Bar (Collapsible Sidebar)                      │
├─────────────────────────────────────────────────────┤
│  Horizontal Tab Bar (Scrollable)                    │
├─────────────────────────────────────────────────────┤
│  Main Content                                        │
└─────────────────────────────────────────────────────┘
```

#### Mobile View (< 768px)
```
┌────────────────────┐
│  Top Bar + Hamburger│
├────────────────────┤
│  Tab Dropdown      │
├────────────────────┤
│  Content (Stacked) │
│  (No side-by-side) │
└────────────────────┘
```

---

### Dark/Light Theme with Project Type Colors

**Theme Accent Colors by Project Type:**
- **Full-Stack:** Purple/Blue gradient (#7b61ff → #00d4ff)
- **API:** Green/Teal (#00ff88 → #00d4ff)
- **Frontend:** Pink/Purple (#ff61d8 → #7b61ff)
- **Database:** Orange/Yellow (#ff9500 → #ffcc00)
- **Microservices:** Multi-color (each service different hue)
- **Library:** Grey/Blue (#6c7a89 → #95a5a6)

---

### Performance Optimizations

1. **Lazy Tab Loading**
   - Only render active tab content
   - Cache rendered tabs for quick switching
   - Dispose hidden tab resources

2. **Virtual Scrolling**
   - For large data tables (e.g., 1000+ files)
   - Only render visible rows
   - Smooth scrolling performance

3. **Progressive Data Loading**
   - Load overview data first (< 100ms)
   - Load detailed tab data on-demand
   - Show loading skeletons while fetching

4. **Web Workers for Heavy Computation**
   - Complexity calculations
   - Graph layout algorithms
   - Large dataset filtering/sorting

5. **Caching Strategy**
   - LocalStorage for recent dashboard views
   - Service Worker for offline support
   - Cache invalidation on data refresh

---

### Accessibility Features

1. **Keyboard Navigation**
   - Tab switching: `Alt + 1-9`
   - Section focus: `Tab` key
   - Quick search: `/` key

2. **Screen Reader Support**
   - ARIA labels for all interactive elements
   - Tab announcements
   - Data table descriptions

3. **High Contrast Mode**
   - Alternative color scheme for visibility
   - Increased border widths
   - Icon + text labels

4. **Focus Indicators**
   - Clear focus outlines
   - Skip-to-content links
   - Landmark regions

---

### Export & Sharing

1. **Export Options**
   - JSON (raw data)
   - CSV (tabular data)
   - PDF (full report with charts)
   - PNG (individual visualizations)

2. **Report Generation**
   - Executive summary (1 page)
   - Detailed report (multi-page with all sections)
   - Custom report builder (select sections)

3. **Shareable Links**
   - Generate unique URL with embedded data
   - Password protection option
   - Expiration dates

4. **Integration**
   - Azure DevOps Work Item links
   - GitHub Issues
   - Slack/Teams notifications

---

### Implementation Priority

**Phase 1 (Week 3):** Core adaptive UI
- Project type detection
- Tab visibility logic
- Basic conditional rendering

**Phase 2 (Week 4):** New tabs
- Frontend tab (Angular/React/MVC)
- Backend tab (API endpoints, services)
- Database tab (schema visualization)

**Phase 3 (Week 5):** Enhanced tabs
- API Documentation tab
- Infrastructure tab
- Business Domain tab
- Testing tab enhancements

**Phase 4 (Week 6):** Polish & UX
- Responsive layouts
- Accessibility features
- Export functionality
- Performance optimizations

---

## 📅 Timeline

**Total Duration:** 4-5 weeks (Extended to 6 weeks with UI enhancements)

| Phase | Duration | Parallel Work |
|-------|----------|---------------|
| Phase 1: Schema Extension | 3 days | Can run parallel with Phase 2 infrastructure |
| Phase 2: Core Infrastructure | 5 days | File processing, caching, orchestration |
| Phase 3: Language Analyzers | 7 days | C#, TS, CF, SQL analyzers can be parallel |
| Phase 4: Specialized Collectors | 5 days | Architecture, frontend, backend, database |
| Phase 5: Testing & Validation | 3 days | Automated tests, manual validation |
| Phase 6: Documentation | 2 days | User docs, API reference, migration guide |

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5  
**Parallel Opportunities:** Language analyzers (Phase 3), specialized collectors (Phase 4)

---

## 🔄 Migration Strategy

### For Existing Dashboards

1. **Backward Compatibility Mode**
   - v1 collectors remain functional
   - v2 collectors write to separate files
   - Dashboard UI supports both formats

2. **Gradual Migration**
   - Small projects migrate first (< 100 files)
   - Validate results against v1 data
   - Expand to medium projects (100-1K files)
   - Finally migrate large projects

3. **Rollback Plan**
   - Keep v1 collectors until v2 proven stable
   - Feature flag to toggle v1/v2
   - Automated data comparison tool

---

## 📚 References

### Existing CORTEX Documentation
- Dashboard Launcher: `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`
- Current Schema: `cortex-brain/dashboards/schema/health-data-schema.json`
- Base Collector: `src/dashboard/data/base_collector.py`
- Parallel Orchestrator: `src/dashboard/data/parallel_collector.py`

### External References
- **C# AST Parsing:** Roslyn Compiler API
- **TypeScript Parsing:** TypeScript Compiler API (tsc)
- **ColdFusion Parsing:** CFLint patterns, regex-based
- **SQL Parsing:** sqlparse (Python), TSQLParser
- **OWASP Top 10 2021:** https://owasp.org/Top10/
- **Maintainability Index:** https://docs.microsoft.com/en-us/visualstudio/code-quality/code-metrics-values

---

## ✅ Next Steps

### Immediate Actions (This Week)

1. **Review & Approve Plan**
   - Stakeholder review of enhancement scope
   - Prioritize language analyzers (C#, TS, CF, SQL)
   - Confirm timeline and resource allocation

2. **Prototype Core Infrastructure**
   - Build `ScalableCollectorOrchestrator` with parallel processing
   - Test on luum-fresh (4.8K files) to validate performance
   - Benchmark against current collectors

3. **Define v2 Schema**
   - Complete JSON Schema definition
   - Create validation suite
   - Generate mock data for testing

4. **Start C# Analyzer**
   - Highest priority (covers luum-fresh and TCBULK)
   - Detect MVC patterns, Web API endpoints, Entity Framework
   - Extract complexity metrics

### Follow-Up Tasks

- [ ] Create feature branch: `feature/dashboard-enhancement-universal`
- [ ] Set up test data fixtures for all 3 repositories
- [ ] Design dashboard UI mockups for new data sections (Figma/Adobe XD)
- [ ] Build interactive prototypes for new tabs (Frontend, Backend, Database)
- [ ] Schedule weekly progress reviews

---

## 📊 UI Enhancement Summary

### Key Innovations

1. **Context-Aware Visibility**
   - Intelligent tab showing/hiding based on project type
   - Empty state elimination (no blank sections)
   - Badge indicators for data availability

2. **Project-Specific Views**
   - **API Projects:** Focus on endpoints, authentication, performance
   - **Full-Stack Apps:** Comprehensive frontend + backend + database views
   - **Database Projects:** Deep schema analysis, ERD visualization
   - **Frontend-Only:** Component trees, bundle analysis, routing
   - **Microservices:** Service topology, inter-service dependencies

3. **Rich Visualizations**
   - Interactive ERD diagrams for database schema
   - Component hierarchy trees for frontend
   - Service dependency graphs for microservices
   - API endpoint explorer with try-it-out
   - Infrastructure topology maps

4. **Enhanced Information Density**
   - From 6 fixed tabs → 7-13 adaptive tabs
   - From 20 data points → 150+ contextual metrics
   - From static tables → interactive, drillable visualizations
   - From single-source data → multi-layer architecture views

5. **Performance-First Design**
   - Lazy tab loading (only active tab rendered)
   - Virtual scrolling for large datasets
   - Web Workers for heavy computation
   - Service Worker offline support
   - < 300ms initial render, < 50ms tab switching

### Comparison: Before vs After

| Aspect | Before (v1) | After (v2) | Improvement |
|--------|-------------|------------|-------------|
| **Tabs** | 6 fixed tabs | 7-13 adaptive tabs | 2x more relevant |
| **Project Support** | API projects only | All project types | Universal |
| **Data Points** | ~20 metrics | ~150 contextual metrics | 7.5x richer |
| **Visualizations** | Tables, basic charts | Interactive graphs, ERDs, trees | 10x more visual |
| **Mobile Support** | Basic (65/100) | Responsive (90/100) | 38% better |
| **Accessibility** | Limited (72/100) | WCAG AAA (95/100) | 32% better |
| **Load Time** | 800ms | 300ms | 2.7x faster |
| **Empty Sections** | Shown | Hidden | 100% reduction |
| **Language Support** | Python, C# (basic) | 8+ languages | 4x coverage |

### User Experience Enhancements

**For Developers:**
- Instant project type recognition
- Jump directly to relevant sections
- Deep-dive into specific layers (frontend/backend/database)
- Export detailed reports for documentation

**For Architects:**
- Comprehensive architecture visualization
- Dependency mapping across layers
- Security posture at-a-glance
- Infrastructure topology understanding

**For Managers:**
- Executive summary dashboard
- Health trends over time
- Technical debt quantification
- Resource allocation insights

**For DevOps:**
- CI/CD pipeline visibility
- Deployment configuration review
- Infrastructure resource mapping
- Monitoring integration status

---

## 🎯 Success Criteria

**The dashboard enhancement will be considered successful when:**

1. ✅ **Universal Compatibility:** Successfully analyzes and displays data for:
   - Full-Stack apps (luum-fresh)
   - ColdFusion apps (V5.ColdFusion)
   - Angular apps (TCBULK)
   - API-only projects (V5.PrevalidationWS)

2. ✅ **Adaptive Intelligence:** 
   - Correctly identifies project type (95%+ accuracy)
   - Shows only relevant tabs (0 empty sections)
   - Provides contextual insights per project type

3. ✅ **Performance Targets Met:**
   - < 300ms initial load
   - < 50ms tab switching
   - < 60s data collection for 10K+ files

4. ✅ **Rich Visualizations:**
   - Interactive ERD for database projects
   - Component tree for frontend projects
   - Service graph for microservices
   - API explorer for API projects

5. ✅ **User Satisfaction:**
   - 90%+ positive feedback from developers
   - 80%+ reduction in "where's the data?" questions
   - 3x increase in dashboard usage frequency

---

**End of Plan**
