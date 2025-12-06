# Sample Apps Anti-Patterns & Clean Code Analysis

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** 2025-12-06  
**Purpose:** Analysis of BadMonolith vs CleanSolidApp for TDD Implementation Orchestrator enhancement

---

## 🎯 Analysis Objective

Extract anti-patterns from BadMonolith and clean practices from CleanSolidApp to enhance the TDD Implementation Orchestrator's REFACTOR phase detection capabilities.

---

## 🚨 BadMonolith Anti-Patterns (What to Fix)

### Backend Anti-Patterns (.NET Minimal API)

**1. God Endpoint Pattern**
- **Location:** `Program.cs` lines 16-142
- **Issue:** Single endpoint handles all CRUD operations via query string action parameter
- **Impact:** No REST principles, unmaintainable, untestable
- **Detection:** Single endpoint with multiple conditional branches (>3 if/else blocks)

```csharp
app.MapMethods("/api/tasks", new[] { "GET", "POST", "PUT", "DELETE" }, async (HttpContext ctx) =>
{
    string action = ctx.Request.Query["action"];
    // 120+ lines of logic in one handler
```

**2. SQL Injection Vulnerabilities**
- **Location:** Lines 56-59, 89, 104, 121, 134
- **Issue:** String concatenation for SQL queries, no parameterization
- **Impact:** Critical security vulnerability
- **Detection:** String concatenation with SQL keywords (`"SELECT" + variable`)

```csharp
cmd.CommandText = "SELECT * FROM Tasks WHERE Title LIKE '%" + filter + "%'";
cmd.CommandText = "INSERT INTO Tasks(Title, IsCompleted) VALUES('" + title + "', 0)";
```

**3. Hard-Coded Credentials**
- **Location:** Line 11
- **Issue:** Connection string with credentials directly in code
- **Impact:** Security vulnerability, no environment-specific config
- **Detection:** String literal containing "Password=" or "pwd="

```csharp
string connString = "Server=localhost;Database=CortexBadDb;User Id=sa;Password=Your_password123;";
```

**4. Global Mutable State**
- **Location:** Line 13
- **Issue:** Global list used as cache, shared across requests
- **Impact:** Thread-safety issues, race conditions
- **Detection:** Static/global collections at file scope

```csharp
List<Dictionary<string, object>> CachedTasks = new List<Dictionary<string, object>>();
```

**5. No Dependency Injection**
- **Issue:** Direct `new SqlConnection()` in handlers, no abstraction
- **Impact:** Tight coupling, untestable, no mocking capability
- **Detection:** `new` keyword with concrete classes in business logic

**6. No Error Handling**
- **Issue:** No try-catch, no logging, silent failures
- **Impact:** Unhandled exceptions crash app, no observability
- **Detection:** Async methods without exception handling

**7. No Input Validation**
- **Issue:** Accepts any input, no sanitization or validation
- **Impact:** Invalid data in database, potential crashes
- **Detection:** Direct use of request data without validation logic

**8. Magic Strings Everywhere**
- **Issue:** "action", "filter", "id", table names as literals
- **Impact:** Typo-prone, refactoring nightmare
- **Detection:** String literals used as dictionary keys or query parameters (>5 occurrences)

### Frontend Anti-Patterns (Angular)

**1. Smart Component Anti-Pattern**
- **Location:** `app.component.ts` entire file
- **Issue:** Component directly calls HttpClient, no service layer
- **Impact:** Tight coupling, untestable, logic duplication
- **Detection:** `HttpClient` injected in component (not service)

```typescript
constructor(private http: HttpClient) {}
```

**2. No Models/Types**
- **Issue:** Using `any[]` and `any` for tasks
- **Impact:** No type safety, runtime errors
- **Detection:** `any` type usage in Angular components (>3 occurrences)

```typescript
tasks: any[] = [];
```

**3. No Separation of Concerns**
- **Issue:** API logic, state management, UI all in one component
- **Impact:** Unmaintainable, untestable
- **Detection:** Component with HTTP calls + template + state management

**4. Hard-Coded API URL**
- **Issue:** API URL as string literal in component
- **Impact:** No environment-specific config
- **Detection:** HTTP URLs as string literals (not environment variables)

```typescript
apiUrl = 'http://localhost:5000/api/tasks';
```

---

## ✅ CleanSolidApp Best Practices (What to Apply)

### Backend Clean Architecture

**1. Layered Architecture**
- **Structure:**
  - `Domain/` - Entities (TaskItem.cs)
  - `Application/` - Interfaces + Services (ITaskRepository, ITaskService, TaskService)
  - `Infrastructure/` - Data access (TaskRepository, AppDbContext)
  - `API/` - Controllers (TasksController)
- **Benefit:** Clear separation of concerns, testable, maintainable

**2. Dependency Injection**
- **Location:** `Program.cs` lines 8-13
- **Pattern:** Register interfaces with implementations
- **Benefit:** Loose coupling, testability, flexibility

```csharp
builder.Services.AddScoped<ITaskRepository, TaskRepository>();
builder.Services.AddScoped<ITaskService, TaskService>();
```

**3. Repository Pattern**
- **Location:** `ITaskRepository.cs`, `TaskRepository.cs`
- **Pattern:** Interface defines contract, implementation uses EF Core
- **Benefit:** Data access abstraction, swappable implementations

**4. Entity Framework Core (ORM)**
- **Location:** `AppDbContext.cs`, `TaskRepository.cs`
- **Pattern:** DbContext with migrations, parameterized queries
- **Benefit:** No SQL injection, type-safe queries, automatic parameterization

**5. RESTful API Design**
- **Location:** `TasksController.cs`
- **Pattern:** HTTP verbs map to CRUD, proper status codes, resource-based routes
- **Benefit:** Standard API design, predictable, client-friendly

```csharp
[HttpGet] // GET /api/tasks
[HttpPost] // POST /api/tasks
[HttpPut("{id:int}")] // PUT /api/tasks/5
[HttpDelete("{id:int}")] // DELETE /api/tasks/5
```

**6. Configuration from appsettings.json**
- **Location:** `Program.cs` line 9
- **Pattern:** `builder.Configuration.GetConnectionString("DefaultConnection")`
- **Benefit:** Environment-specific config, no hardcoded credentials

**7. Strong Typing**
- **Pattern:** Domain entities, DTOs (CreateTaskRequest, UpdateTaskStatusRequest)
- **Benefit:** Compile-time safety, validation, documentation

### Frontend Clean Practices

**1. Service Layer**
- **Location:** `task.service.ts`
- **Pattern:** Injectable service handles all HTTP, components consume service
- **Benefit:** Reusability, testability, single source of truth

```typescript
@Injectable({ providedIn: 'root' })
export class TaskService { ... }
```

**2. TypeScript Models**
- **Location:** `task.model.ts`
- **Pattern:** Interface defines task structure
- **Benefit:** Type safety, IntelliSense, compile-time errors

```typescript
export interface TaskItem {
  id: number;
  title: string;
  isCompleted: boolean;
}
```

**3. Dumb Components**
- **Location:** `task-list.component.ts`
- **Pattern:** Component delegates business logic to service, focuses on UI
- **Benefit:** Testable, reusable, clean

**4. Observable Patterns**
- **Pattern:** Service returns `Observable<T>`, component subscribes
- **Benefit:** Reactive programming, async handling, cancellation

---

## 🔍 Detection Rules for TDD Orchestrator

### High-Priority Anti-Patterns (BLOCKED)

| Anti-Pattern | Detection Heuristic | Severity | Auto-Fix |
|-------------|---------------------|----------|----------|
| SQL Injection | String concat with SQL keywords | CRITICAL | Yes (parameterize) |
| Hard-coded credentials | `Password=` or `pwd=` in string literal | CRITICAL | No (log blocker) |
| No error handling | Async method without try-catch | HIGH | Yes (wrap in try-catch) |
| God method | Method >100 lines OR >5 conditional branches | HIGH | Yes (extract methods) |
| Global mutable state | Static/global collections | HIGH | No (suggest DI) |

### Medium-Priority Code Smells (WARN)

| Code Smell | Detection Heuristic | Severity | Auto-Fix |
|------------|---------------------|----------|----------|
| Magic strings | String literal as key >5 times | MEDIUM | Yes (extract constant) |
| `any` type overuse | `any` type >3 occurrences | MEDIUM | No (suggest interfaces) |
| No DI | `new` keyword in business logic | MEDIUM | No (suggest DI) |
| Long parameter list | Method with >4 parameters | MEDIUM | Yes (extract DTO) |
| Duplicate code | Same 5+ line block appears >2 times | MEDIUM | Yes (extract method) |

### SOLID Violations (REFACTOR)

| Principle | Detection Heuristic | Severity | Auto-Fix |
|-----------|---------------------|----------|----------|
| SRP | Class with >10 methods OR >300 lines | MEDIUM | No (suggest split) |
| OCP | Switch/if-else on type >3 branches | MEDIUM | No (suggest strategy pattern) |
| LSP | Base class with empty/throw methods | LOW | No (suggest redesign) |
| ISP | Interface with >7 methods | LOW | No (suggest segregation) |
| DIP | High-level depends on low-level (concrete) | MEDIUM | No (suggest abstraction) |

---

## 🏗️ Recommended Refactoring Patterns

### Pattern 1: God Endpoint → Controller + Service + Repository

**Before (BadMonolith):**
```csharp
app.MapMethods("/api/tasks", ..., async (HttpContext ctx) => {
    // 120 lines of CRUD logic
});
```

**After (CleanSolidApp):**
```csharp
// Controller (API layer)
[ApiController]
[Route("api/[controller]")]
public class TasksController : ControllerBase {
    private readonly ITaskService _service;
    // Clean, focused methods
}

// Service (Application layer)
public class TaskService : ITaskService {
    private readonly ITaskRepository _repo;
    // Business logic
}

// Repository (Infrastructure layer)
public class TaskRepository : ITaskRepository {
    private readonly AppDbContext _ctx;
    // Data access
}
```

### Pattern 2: String Concatenation SQL → ORM

**Before:**
```csharp
cmd.CommandText = "SELECT * FROM Tasks WHERE Title LIKE '%" + filter + "%'";
```

**After:**
```csharp
var query = _ctx.Tasks.AsQueryable();
if (!string.IsNullOrWhiteSpace(filter))
    query = query.Where(t => t.Title.Contains(filter));
return await query.ToListAsync();
```

### Pattern 3: Hard-Coded Config → Configuration System

**Before:**
```csharp
string connString = "Server=localhost;Database=CortexBadDb;User Id=sa;Password=Your_password123;";
```

**After:**
```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=CleanDb;..."
  }
}
```

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
```

### Pattern 4: Smart Component → Service + Dumb Component

**Before:**
```typescript
export class AppComponent {
    constructor(private http: HttpClient) {}
    load() {
        this.http.get<any[]>('http://localhost:5000/api/tasks').subscribe(...);
    }
}
```

**After:**
```typescript
// Service
@Injectable({ providedIn: 'root' })
export class TaskService {
    private readonly baseUrl = environment.apiUrl;
    getTasks(): Observable<TaskItem[]> { ... }
}

// Component
export class TaskListComponent {
    constructor(private taskService: TaskService) {}
    load() { this.taskService.getTasks().subscribe(...); }
}
```

---

## 📊 Metrics for Success

When refactoring BadMonolith → CORTEX-Clean, track:

1. **Cyclomatic Complexity:** Reduced from 15+ to <5 per method
2. **Method Length:** Reduced from 120+ lines to <20 lines
3. **Class Responsibility:** Split 1 monolith into 4+ focused classes
4. **Test Coverage:** Increased from 0% to >80%
5. **Security Vulnerabilities:** Reduced from 5+ to 0
6. **Magic Numbers/Strings:** Extracted to constants (0 inline strings)
7. **Dependency Coupling:** Reduced from tight coupling to interface-based DI

---

## 🎯 Orchestrator Enhancement Recommendations

### 1. Add .NET-Specific Rules

Add to `_validate_solid()`:
- Detect `MapMethods` with >50 lines → Suggest controller extraction
- Detect ADO.NET without parameters → Flag SQL injection risk
- Detect connection string in code → Flag credential exposure

### 2. Add TypeScript-Specific Rules

Add to `_detect_redundancies()`:
- Detect `any` type in Angular components → Suggest interfaces
- Detect HttpClient in components → Suggest service extraction
- Detect hard-coded URLs → Suggest environment variables

### 3. Add Language-Agnostic Pattern Detection

- **God Class/Method:** AST analysis for method line count, branch complexity
- **Magic Values:** String literal frequency analysis
- **Duplicate Strings:** Hash literal strings, flag >3 occurrences
- **No Error Handling:** Detect async/await without try-catch

### 4. Add Security Scan Phase

Before REFACTOR phase, run security checks:
- SQL injection patterns (string concat with SQL keywords)
- Hard-coded credentials (regex for passwords/keys)
- XSS vulnerabilities (unescaped user input in HTML)
- Missing authentication/authorization attributes

---

## 🚀 Next Actions

1. ✅ Enhance `_validate_solid()` with .NET/TypeScript rules
2. ✅ Add `_detect_security_issues()` method
3. ✅ Add `_detect_magic_values()` method
4. ✅ Update refactoring pattern library with clean code patterns
5. ✅ Test orchestrator on BadMonolith → CORTEX-Clean transformation

---

**Status:** Analysis complete. Ready for orchestrator enhancement and refactoring execution.
