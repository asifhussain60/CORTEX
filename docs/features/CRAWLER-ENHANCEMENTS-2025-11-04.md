# Crawler Enhancements - November 4, 2025

## 🎯 Overview

Enhanced the KDS multi-threaded crawler system to support comprehensive modern framework detection and database discovery.

---

## ✨ UI Crawler Enhancements (v2.0.0)

### New Framework Detection

The UI crawler now detects and analyzes **all major modern frameworks**:

#### Modern Frameworks Supported

| Framework | Detection Method | File Patterns | Key Features Extracted |
|-----------|-----------------|---------------|------------------------|
| **Angular (2+)** | `@Component`, `@NgModule`, `@Injectable` decorators | `*.ts`, `*.html` | Components, services, dependency injection, templates |
| **React** | `import React`, hooks (`useState`, `useEffect`) | `*.tsx`, `*.jsx` | Components, functional components, hooks |
| **Vue.js** | Existing support | `*.vue` | Components, props |
| **Blazor** | `.razor` files | `*.razor` | Components, parameters, @inject, routes |
| **Svelte** | Existing support | `*.svelte` | Components |
| **AngularJS (1.x)** | `angular.module`, `$scope`, `$inject` | `*.js` | Modules, controllers, directives, services |

### Enhanced Detection Logic

**Phase 0: Framework Detection**
```powershell
[0/5] Detecting UI frameworks...
  ✅ Angular 17.0.0 detected via package.json
  ✅ React 18.2.0 detected via package.json
  ✅ Blazor detected via .razor files
  ✅ AngularJS detected via code sampling
```

**Multi-Strategy Detection:**
1. **package.json** scanning for dependencies
2. **File pattern** detection (.razor, .vue, etc.)
3. **Code sampling** for framework-specific patterns
4. **Bower/legacy** support for older projects

### Angular-Specific Extraction

```typescript
// Detects and extracts:
@Component({
  selector: 'app-example',    // ✅ Selector extracted
  templateUrl: './example.html' // ✅ Template URL extracted
})
export class ExampleComponent {
  constructor(
    private http: HttpClient,   // ✅ DI extracted
    private router: Router      // ✅ DI extracted
  ) {}
}
```

### Component Type Classification

Now identifies specific component types:
- `angular-component` - Modern Angular (2+)
- `angularjs-controller` - AngularJS 1.x
- `react-typescript-component` - React with TypeScript
- `react-component` - React with JavaScript
- `blazor-component` - Blazor
- `vue-component` - Vue.js
- `svelte-component` - Svelte

### Output Enhancements

```json
{
  "statistics": {
    "frameworks_detected": ["angular", "react", "blazor"],
    "framework_counts": {
      "angular": 45,
      "react": 23,
      "blazor": 12
    }
  }
}
```

---

## 🗄️ New Database Crawler (v1.0.0)

### Purpose

Discovers database configurations, schemas, and relationships **without requiring live database access**.

### Features

#### 1. Connection String Discovery

Searches multiple configuration sources:
- `appsettings.json`, `appsettings.*.json`
- `web.config`, `app.config`
- `.env` files
- `database.yml`, `ormconfig.json`
- `knexfile.js` (Node.js projects)

#### 2. Provider Detection

Automatically identifies database providers:
- **SQL Server** - `Data Source=`, `Server=`
- **PostgreSQL** - `Host=`, `postgres://`
- **MySQL** - `mysql://`
- **MongoDB** - `mongodb://`, `mongodb+srv://`
- **SQLite** - `.db`, `.sqlite` files

#### 3. Entity Model Extraction

Parses DbContext files to discover:
- Entity names and DbSet properties
- Entity properties (columns)
- Relationships (one-to-many, many-to-one)
- Navigation properties

Example extraction:
```csharp
public class ApplicationDbContext : DbContext
{
    public DbSet<User> Users { get; set; }  // ✅ Extracted
    public DbSet<Session> Sessions { get; set; }  // ✅ Extracted
}

public class User {
    public int Id { get; set; }  // ✅ Property extracted
    public string Name { get; set; }  // ✅ Property extracted
    public ICollection<Session> Sessions { get; set; }  // ✅ Relationship extracted
}
```

#### 4. Migration Discovery

Finds and catalogs migration files:
- EF Core migrations (`*Migration.cs`)
- SQL migrations (`migrations/*.sql`)
- Alembic (Python) migrations
- Node.js migration files

#### 5. Live Database Crawling (Optional)

With `-ConnectAndCrawl` flag:
```powershell
.\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp" -ConnectAndCrawl
```

Connects to SQL Server and extracts:
- All tables from `INFORMATION_SCHEMA`
- Column names and data types
- Schema information

**Security Note:** Live crawling is **disabled by default** and requires explicit opt-in.

### Output Structure

```json
{
  "area": "Database",
  "connection_strings": [
    {
      "name": "DefaultConnection",
      "provider": "SQL Server",
      "server": "localhost",
      "database": "MyAppDb",
      "authentication": "Windows Authentication",
      "environment": "Development"
    }
  ],
  "providers": ["SQL Server", "MongoDB"],
  "entities": [
    {
      "name": "User",
      "dbset_name": "Users",
      "properties": [
        { "name": "Id", "type": "int" },
        { "name": "Email", "type": "string" }
      ],
      "relationships": [
        {
          "type": "one-to-many",
          "target": "Session",
          "property": "Sessions"
        }
      ]
    }
  ],
  "migrations": [
    {
      "name": "InitialCreate",
      "timestamp": "20231104120000",
      "operations": ["CreateTable", "CreateIndex"]
    }
  ],
  "statistics": {
    "total_connections": 2,
    "total_entities": 15,
    "total_migrations": 8,
    "total_relationships": 23
  }
}
```

---

## 🔄 Orchestrator Integration

The database crawler is now integrated into the orchestrator:

### Deep Mode
```powershell
.\orchestrator.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp" -Mode deep
```

Runs **5 crawlers in parallel**:
1. UI Crawler (enhanced)
2. API Crawler
3. Service Crawler
4. Test Crawler
5. **Database Crawler** (NEW)

### Quick Mode
```powershell
.\orchestrator.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp" -Mode quick
```

Runs UI and Test crawlers only (no database scanning).

---

## 📊 Performance Targets

| Crawler | Target | Scope |
|---------|--------|-------|
| **UI Crawler** | <2 min | 2000+ files, multi-framework |
| **Database Crawler** | <2 min | Config discovery only |
| **Database Crawler (Live)** | <5 min | With live DB connection |

---

## 🎯 Use Cases

### 1. Multi-Framework Projects

Projects using multiple UI frameworks (e.g., migrating from AngularJS to Angular):
```
Detected Frameworks:
  ✅ AngularJS 1.6.0 (legacy, 150 files)
  ✅ Angular 17.0.0 (migration in progress, 45 files)
  ✅ Blazor (admin panel, 12 files)
```

### 2. Database Discovery

Understanding data models without DB access:
```
Connection Strings: 3
Providers: SQL Server, MongoDB
Entities: 28 tables
Relationships: 67 foreign keys
Migrations: 43 versions
```

### 3. Technology Stack Mapping

Complete project understanding:
```yaml
technology_stack:
  frontend:
    frameworks: ["Angular 17", "Blazor"]
    ui_libraries: ["Bootstrap 5", "Material UI"]
  backend:
    language: "C# 12"
    framework: "ASP.NET Core 8.0"
  database:
    providers: ["SQL Server 2022", "Redis"]
    entities: 28
    total_tables: 35
```

---

## 🔒 Security Considerations

### Database Crawler

1. **No live connections by default** - Only parses config files
2. **Opt-in live crawling** - Requires explicit `-ConnectAndCrawl` flag
3. **Connection strings logged** - Only metadata, not credentials
4. **Read-only operations** - No write/modify operations on databases

### Recommended Usage

**Development/Local:**
```powershell
# Safe - config parsing only
.\database-crawler.ps1 -WorkspaceRoot "."

# With live crawl for local dev DB
.\database-crawler.ps1 -WorkspaceRoot "." -ConnectAndCrawl
```

**Production/CI:**
```powershell
# Never use -ConnectAndCrawl in production
.\orchestrator.ps1 -WorkspaceRoot "." -Mode deep
```

---

## 📝 Files Changed

### Modified
- `scripts/crawlers/ui-crawler.ps1` - v2.0.0 (enhanced framework detection)
- `scripts/crawlers/orchestrator.ps1` - Added database crawler integration

### Created
- `scripts/crawlers/database-crawler.ps1` - v1.0.0 (NEW)
- `docs/features/CRAWLER-ENHANCEMENTS-2025-11-04.md` - This document

---

## 🚀 Next Steps

### Recommended Testing

1. **Run UI crawler on multi-framework project:**
   ```powershell
   .\scripts\crawlers\ui-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\YourApp"
   ```

2. **Test database crawler:**
   ```powershell
   .\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\YourApp"
   ```

3. **Full orchestrator run:**
   ```powershell
   .\scripts\crawlers\orchestrator.ps1 -WorkspaceRoot "D:\PROJECTS\YourApp" -Mode deep
   ```

### Future Enhancements

- [ ] GraphQL schema detection
- [ ] REST API endpoint discovery from database models
- [ ] Database index recommendations
- [ ] Entity Framework relationship validation
- [ ] NoSQL schema pattern detection (MongoDB, Cosmos DB)
- [ ] Database performance analysis (query patterns from code)

---

## ✅ Summary

**UI Crawler:** Now detects **Angular, React, Vue, Blazor, Svelte, and AngularJS** with framework-specific pattern extraction.

**Database Crawler:** Discovers connection strings, entity models, and schema information from **appsettings.json, web.config, DbContext files**, with optional live database crawling.

**Orchestrator:** Integrated database crawler for complete project analysis in **deep mode**.

**Version:** KDS v6.0 Multi-Threaded Crawler Architecture
**Date:** November 4, 2025
**Status:** ✅ Production Ready
