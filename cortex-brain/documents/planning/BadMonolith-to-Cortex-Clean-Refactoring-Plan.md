# BadMonolith to Cortex-Clean Refactoring Plan

**Project:** Refactor BadMonolith to Clean Architecture  
**Target Folder:** `cortex-sample-apps/Cortex-Clean`  
**Methodology:** TDD Mastery + Clean Architecture + SOLID Principles  
**Plan ID:** badmonolith-refactor-001  
**Created:** December 6, 2025  
**Status:** pending_approval

---

## 🎯 Project Vision

Transform the BadMonolith application (a deliberately poorly-designed task management system) into a showcase of Clean Architecture, SOLID principles, and TDD Mastery. This refactoring will serve as a teaching example demonstrating CORTEX's ability to restructure monolithic code into maintainable, testable, and scalable applications.

### Current State Analysis

**Backend Issues (Program.cs - 141 lines):**
- ❌ God-endpoint handling all HTTP methods via query params
- ❌ SQL injection vulnerabilities (string concatenation)
- ❌ Hard-coded connection strings with credentials
- ❌ Global mutable state (`CachedTasks`)
- ❌ No error handling, logging, or validation
- ❌ No separation of concerns (routing, business logic, data access in one file)
- ❌ Zero tests

**Frontend Issues (app.component.ts):**
- ❌ All business logic in single component
- ❌ Direct HTTP calls in UI layer
- ❌ No state management
- ❌ No error handling
- ❌ No abstraction (services, models)
- ❌ Zero tests

### Target State

**Backend (Clean Architecture):**
- ✅ Domain Layer: Entities, interfaces, domain services
- ✅ Application Layer: Use cases, DTOs, validators
- ✅ Infrastructure Layer: EF Core, repositories, logging
- ✅ API Layer: Controllers with proper HTTP verbs, middleware
- ✅ 90%+ test coverage with TDD workflow
- ✅ Configuration management with secrets
- ✅ Structured logging and error handling

**Frontend (Angular Clean Architecture):**
- ✅ Feature modules with smart/dumb component separation
- ✅ State management (NgRx or standalone signals)
- ✅ Service layer abstraction
- ✅ Domain models and interfaces
- ✅ 85%+ test coverage
- ✅ Error handling and loading states

**Documentation System:**
- ✅ Docsify-based learning library
- ✅ Auto-generated architecture diagrams
- ✅ Per-phase documentation updates
- ✅ Code examples with before/after comparisons

---

## 📋 Definition of Ready (DoR)

### Functional Requirements
1. ✅ BadMonolith application analyzed and anti-patterns documented
2. ✅ Clean Architecture structure defined for both backend and frontend
3. ✅ Database schema reviewed and domain model designed
4. ✅ Target folder `cortex-sample-apps/Cortex-Clean` identified
5. ✅ Docsify documentation structure planned

### Technical Requirements
6. ✅ .NET 8 SDK available for backend development
7. ✅ Angular CLI available for frontend development
8. ✅ SQL Server LocalDB or equivalent for development database
9. ✅ Docsify CLI installed for documentation generation
10. ✅ Git repository configured for checkpoint management

### TDD Requirements (Auto-Injected)
11. ✅ TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)
12. ✅ Tests MUST fail before implementation (RED phase validation)
13. ✅ Git checkpoints required at RED, GREEN, REFACTOR phases
14. ✅ Test coverage targets defined: Backend 90%, Frontend 85%

### Documentation Requirements
15. ✅ Docsify documentation automated via custom orchestrator extension
16. ✅ Each phase includes architecture decision records (ADRs)
17. ✅ Before/after code comparisons for each refactoring

---

## 🏗️ Phase Breakdown

### Phase 1: Foundation & Infrastructure Setup
**Duration:** 8 hours  
**Objectives:** 
- Create project structure for Cortex-Clean
- Setup backend Clean Architecture layers
- Configure testing framework and CI skeleton
- Initialize Docsify documentation structure

**Tasks:**

#### 1.1 - Project Structure Creation
**Description:** Create folder structure for Clean Architecture backend  
**Estimated Time:** 1 hour  
**Dependencies:** None  
**Test Requirements:**
- RED: Test that solution file references all projects
- GREEN: Create projects with proper dependencies
- REFACTOR: Organize with Directory.Build.props for shared settings

**Deliverables:**
```
Cortex-Clean/
├── backend/
│   ├── Cortex.Clean.Domain/         # Entities, Interfaces, Domain Services
│   ├── Cortex.Clean.Application/    # Use Cases, DTOs, Validators
│   ├── Cortex.Clean.Infrastructure/ # EF Core, Repositories, External Services
│   ├── Cortex.Clean.API/            # Controllers, Middleware, Program.cs
│   └── Cortex.Clean.Tests/          # All test projects
├── frontend/
│   └── cortex-clean-app/            # Angular application
├── docs/                             # Docsify documentation
└── README.md
```

#### 1.2 - Domain Layer Implementation
**Description:** Create core domain entities and interfaces  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1.1  
**Test Requirements:**
- RED: Write tests for Task entity validation rules
- GREEN: Implement Task entity with business rules
- REFACTOR: Extract validation logic to domain services

**Deliverables:**
- `Task` entity with validation
- `ITaskRepository` interface
- `TaskDomainService` for business rules
- Domain exceptions (TaskNotFoundException, InvalidTaskException)
- 95%+ unit test coverage

#### 1.3 - Testing Infrastructure Setup
**Description:** Configure xUnit, FluentAssertions, Moq, AutoFixture  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 1.1  
**Test Requirements:**
- RED: Test that test utilities are discoverable
- GREEN: Create test base classes and factories
- REFACTOR: Extract common test patterns

**Deliverables:**
- Test project with all NuGet packages
- `TestFixture` base class
- `TaskFactory` for test data
- CI configuration (GitHub Actions or Azure Pipelines)

#### 1.4 - Docsify Documentation Initialization
**Description:** Create documentation structure with automated update system  
**Estimated Time:** 2 hours  
**Dependencies:** Task 1.1  
**Test Requirements:**
- RED: Test documentation generator can parse project structure
- GREEN: Implement basic documentation generator
- REFACTOR: Extract template system for reusability

**Deliverables:**
- Docsify configured with sidebar and search
- Documentation generator script (`docs/generate-docs.py`)
- Initial pages: Architecture Overview, TDD Workflow, Phase 1 Progress
- Automated update hook for planner orchestrator

#### 1.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 1, validate DoD, update documentation  
**Estimated Time:** 1.5 hours  
**Dependencies:** Tasks 1.1-1.4  
**Test Requirements:**
- Verify all tests pass
- Validate test coverage meets 90% threshold
- Documentation generated successfully

---

### Phase 2: Backend Application Layer & Use Cases
**Duration:** 10 hours  
**Objectives:**
- Implement CQRS pattern with use cases
- Add validation with FluentValidation
- Create DTOs and mapping profiles
- Full test coverage with TDD

**Tasks:**

#### 2.1 - CQRS Command/Query Setup
**Description:** Implement MediatR for CQRS pattern  
**Estimated Time:** 2 hours  
**Dependencies:** Phase 1 complete  
**Test Requirements:**
- RED: Test that handlers are registered in DI container
- GREEN: Configure MediatR with pipeline behaviors
- REFACTOR: Extract common handler patterns

**Deliverables:**
- MediatR NuGet package installed
- `ICommand<TResponse>` and `IQuery<TResponse>` marker interfaces
- Pipeline behavior for logging and validation
- Handler base classes

#### 2.2 - Task Use Cases Implementation
**Description:** Create commands and queries for task operations  
**Estimated Time:** 4 hours  
**Dependencies:** Task 2.1  
**Test Requirements:**
- RED: Write handler tests first (should fail)
- GREEN: Implement handlers to pass tests
- REFACTOR: Extract common validation logic

**Deliverables:**
- `CreateTaskCommand` + `CreateTaskCommandHandler`
- `GetTasksQuery` + `GetTasksQueryHandler`
- `UpdateTaskCommand` + `UpdateTaskCommandHandler`
- `DeleteTaskCommand` + `DeleteTaskCommandHandler`
- `ToggleTaskCompletionCommand` + handler
- DTOs: `TaskDto`, `CreateTaskRequest`, `UpdateTaskRequest`
- 90%+ test coverage per handler

#### 2.3 - FluentValidation Integration
**Description:** Add request validation with FluentValidation  
**Estimated Time:** 2 hours  
**Dependencies:** Task 2.2  
**Test Requirements:**
- RED: Test validation failures for invalid inputs
- GREEN: Implement validators
- REFACTOR: Extract common validation rules

**Deliverables:**
- `CreateTaskCommandValidator` (title required, max length 255)
- `UpdateTaskCommandValidator`
- Validation pipeline behavior
- Validation exception handling
- 95%+ validator test coverage

#### 2.4 - AutoMapper Configuration
**Description:** Setup object mapping between domain and DTOs  
**Estimated Time:** 1 hour  
**Dependencies:** Task 2.2  
**Test Requirements:**
- RED: Test mapping configurations
- GREEN: Create mapping profiles
- REFACTOR: Simplify complex mappings

**Deliverables:**
- `TaskMappingProfile`
- AutoMapper DI registration
- Mapping tests

#### 2.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 2, update documentation  
**Estimated Time:** 1 hour  
**Dependencies:** Tasks 2.1-2.4  

---

### Phase 3: Infrastructure Layer & Data Access
**Duration:** 8 hours  
**Objectives:**
- Implement EF Core with repository pattern
- Add database migrations
- Configure logging and configuration
- Secure connection string management

**Tasks:**

#### 3.1 - EF Core DbContext Setup
**Description:** Create DbContext with entity configurations  
**Estimated Time:** 2 hours  
**Dependencies:** Phase 2 complete  
**Test Requirements:**
- RED: Test DbContext configuration
- GREEN: Implement DbContext and entity configs
- REFACTOR: Extract configuration patterns

**Deliverables:**
- `CleanTaskDbContext`
- `TaskEntityConfiguration` (Fluent API)
- Connection string from `appsettings.json` (User Secrets for local dev)
- DbContext registration in DI

#### 3.2 - Repository Implementation
**Description:** Implement repository pattern with EF Core  
**Estimated Time:** 3 hours  
**Dependencies:** Task 3.1  
**Test Requirements:**
- RED: Write integration tests with in-memory database
- GREEN: Implement repositories
- REFACTOR: Extract common repository logic to base class

**Deliverables:**
- `TaskRepository : ITaskRepository`
- Integration tests using `WebApplicationFactory`
- Repository pattern validation (no IQueryable leakage)
- 85%+ integration test coverage

#### 3.3 - Database Migrations
**Description:** Create initial migration and seed data  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 3.1  
**Test Requirements:**
- RED: Test migration can be applied to empty database
- GREEN: Create migration with seed data
- REFACTOR: Extract seed logic to separate class

**Deliverables:**
- Initial migration: `20251206_InitialCreate`
- Seed data for demo tasks
- Migration documentation

#### 3.4 - Logging & Configuration
**Description:** Add Serilog structured logging  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 3.1  
**Test Requirements:**
- RED: Test log output formatting
- GREEN: Configure Serilog with enrichers
- REFACTOR: Extract logging configuration

**Deliverables:**
- Serilog configured (Console + File sinks)
- Request logging middleware
- Exception logging middleware
- Log correlation IDs

#### 3.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 3, update documentation  
**Estimated Time:** 1 hour  
**Dependencies:** Tasks 3.1-3.4  

---

### Phase 4: API Layer & HTTP Endpoints
**Duration:** 6 hours  
**Objectives:**
- Create RESTful controllers
- Add Swagger/OpenAPI documentation
- Implement proper HTTP status codes
- CORS and error handling middleware

**Tasks:**

#### 4.1 - Tasks Controller Implementation
**Description:** Create RESTful controller for task operations  
**Estimated Time:** 2.5 hours  
**Dependencies:** Phase 3 complete  
**Test Requirements:**
- RED: Write controller integration tests
- GREEN: Implement controller actions
- REFACTOR: Extract common controller patterns

**Deliverables:**
- `TasksController` with proper verbs:
  - `GET /api/tasks` (list with optional filter)
  - `GET /api/tasks/{id}` (single task)
  - `POST /api/tasks` (create)
  - `PUT /api/tasks/{id}` (update)
  - `DELETE /api/tasks/{id}` (delete)
  - `PATCH /api/tasks/{id}/toggle` (toggle completion)
- Proper HTTP status codes (200, 201, 204, 400, 404, 500)
- 90%+ controller test coverage

#### 4.2 - Swagger/OpenAPI Configuration
**Description:** Add API documentation with Swashbuckle  
**Estimated Time:** 1 hour  
**Dependencies:** Task 4.1  
**Test Requirements:**
- RED: Test Swagger UI is accessible
- GREEN: Configure Swagger with XML comments
- REFACTOR: Add examples and descriptions

**Deliverables:**
- Swashbuckle NuGet package
- XML documentation generation enabled
- Swagger UI at `/swagger`
- API examples for all endpoints

#### 4.3 - Global Error Handling
**Description:** Implement global exception middleware  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 4.1  
**Test Requirements:**
- RED: Test exception responses
- GREEN: Implement exception middleware
- REFACTOR: Create ProblemDetails factory

**Deliverables:**
- `ExceptionMiddleware` with ProblemDetails responses
- Domain exception mapping (404 for NotFound, 400 for Validation)
- Structured error logging
- Exception tests

#### 4.4 - CORS & Security Headers
**Description:** Configure CORS for frontend integration  
**Estimated Time:** 1 hour  
**Dependencies:** Task 4.1  
**Test Requirements:**
- RED: Test CORS preflight requests
- GREEN: Configure CORS policy
- REFACTOR: Extract to configuration

**Deliverables:**
- CORS policy for `http://localhost:4200`
- Security headers middleware
- HTTPS redirection (production)

#### 4.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 4, update documentation  
**Estimated Time:** 1 hour  
**Dependencies:** Tasks 4.1-4.4  

---

### Phase 5: Frontend Architecture Foundation
**Duration:** 8 hours  
**Objectives:**
- Setup Angular project with Clean Architecture
- Create feature modules
- Implement state management
- Setup testing infrastructure

**Tasks:**

#### 5.1 - Angular Project Setup
**Description:** Create Angular app with strict mode and standalone components  
**Estimated Time:** 1.5 hours  
**Dependencies:** Phase 4 complete  
**Test Requirements:**
- RED: Test app bootstraps successfully
- GREEN: Create Angular project with routing
- REFACTOR: Configure path mappings

**Deliverables:**
- Angular 17+ project (standalone components)
- Strict TypeScript configuration
- Path mappings (`@core`, `@shared`, `@features`)
- ESLint + Prettier configuration

#### 5.2 - Core Module & Services
**Description:** Create core services (HTTP, error handling, logging)  
**Estimated Time:** 2 hours  
**Dependencies:** Task 5.1  
**Test Requirements:**
- RED: Write service tests
- GREEN: Implement core services
- REFACTOR: Extract HTTP interceptors

**Deliverables:**
- `ApiService` (HTTP wrapper with error handling)
- `LoggerService` (console wrapper)
- `ErrorHandlerService`
- HTTP interceptors for auth/logging
- 90%+ service test coverage

#### 5.3 - Domain Models & Interfaces
**Description:** Define TypeScript interfaces and models  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 5.1  
**Test Requirements:**
- RED: Test model validation
- GREEN: Create models with validation
- REFACTOR: Extract common validators

**Deliverables:**
- `Task` interface
- `CreateTaskRequest` interface
- `UpdateTaskRequest` interface
- Model validators (Zod or class-validator)
- 85%+ validator coverage

#### 5.4 - State Management Setup
**Description:** Configure NgRx or Angular Signals for state  
**Estimated Time:** 2 hours  
**Dependencies:** Task 5.2  
**Test Requirements:**
- RED: Test state mutations
- GREEN: Implement state management
- REFACTOR: Extract state patterns

**Deliverables:**
- State management solution (NgRx Store or Signals)
- Task state (list, loading, error)
- Actions/effects or signal services
- State tests (90%+ coverage)

#### 5.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 5, update documentation  
**Estimated Time:** 1 hour  
**Dependencies:** Tasks 5.1-5.4  

---

### Phase 6: Frontend Feature Implementation
**Duration:** 10 hours  
**Objectives:**
- Implement task list feature
- Create smart/dumb component architecture
- Add loading/error states
- Full test coverage

**Tasks:**

#### 6.1 - Task Service Layer
**Description:** Create service for task API operations  
**Estimated Time:** 2 hours  
**Dependencies:** Phase 5 complete  
**Test Requirements:**
- RED: Write service tests with mocked HTTP
- GREEN: Implement service methods
- REFACTOR: Extract common HTTP patterns

**Deliverables:**
- `TaskService` with methods:
  - `getTasks(filter?: string): Observable<Task[]>`
  - `getTask(id: number): Observable<Task>`
  - `createTask(request: CreateTaskRequest): Observable<Task>`
  - `updateTask(id: number, request: UpdateTaskRequest): Observable<void>`
  - `deleteTask(id: number): Observable<void>`
  - `toggleCompletion(id: number): Observable<void>`
- HTTP error handling
- 95%+ service test coverage

#### 6.2 - Smart Container Component
**Description:** Create container component for task list  
**Estimated Time:** 2.5 hours  
**Dependencies:** Task 6.1  
**Test Requirements:**
- RED: Write component tests
- GREEN: Implement container logic
- REFACTOR: Extract state logic

**Deliverables:**
- `TaskListContainerComponent` (smart)
- State management integration
- Loading/error handling
- 85%+ component test coverage

#### 6.3 - Presentation Components
**Description:** Create dumb components for UI  
**Estimated Time:** 3 hours  
**Dependencies:** Task 6.2  
**Test Requirements:**
- RED: Write component tests
- GREEN: Implement presentational components
- REFACTOR: Extract reusable sub-components

**Deliverables:**
- `TaskListComponent` (displays tasks)
- `TaskItemComponent` (single task row)
- `TaskFormComponent` (create/edit form)
- `LoadingSpinnerComponent`
- `ErrorMessageComponent`
- Angular Material or standalone CSS
- 90%+ component test coverage

#### 6.4 - Integration & E2E Tests
**Description:** Add end-to-end tests with Playwright  
**Estimated Time:** 2 hours  
**Dependencies:** Tasks 6.1-6.3  
**Test Requirements:**
- RED: Write E2E scenarios
- GREEN: Implement E2E tests
- REFACTOR: Extract page objects

**Deliverables:**
- Playwright configuration
- E2E tests: Create task, toggle completion, delete task
- Page object models
- CI integration for E2E tests

#### 6.5 - Git Checkpoint & Phase Review
**Description:** Commit Phase 6, update documentation  
**Estimated Time:** 0.5 hours  
**Dependencies:** Tasks 6.1-6.4  

---

### Phase 7: Documentation & Knowledge Transfer
**Duration:** 6 hours  
**Objectives:**
- Complete Docsify documentation
- Create architecture diagrams
- Document lessons learned
- Comparison with BadMonolith

**Tasks:**

#### 7.1 - Architecture Documentation
**Description:** Create comprehensive architecture guides  
**Estimated Time:** 2 hours  
**Dependencies:** Phase 6 complete  
**Test Requirements:**
- Validate documentation accuracy
- Review with stakeholders

**Deliverables:**
- Clean Architecture overview
- Layer dependency diagrams (using Mermaid)
- CQRS pattern explanation
- Repository pattern documentation
- TDD workflow documentation

#### 7.2 - Before/After Comparisons
**Description:** Document refactoring transformations  
**Estimated Time:** 2 hours  
**Dependencies:** Task 7.1  
**Test Requirements:**
- Validate code examples
- Verify metrics accuracy

**Deliverables:**
- Side-by-side code comparisons
- Metrics comparison (lines of code, complexity, test coverage)
- Anti-pattern identification in BadMonolith
- Solution patterns in Cortex-Clean
- Lessons learned document

#### 7.3 - Developer Onboarding Guide
**Description:** Create guide for new developers  
**Estimated Time:** 1.5 hours  
**Dependencies:** Task 7.1  
**Test Requirements:**
- Walkthrough with fresh developer
- Validate setup instructions

**Deliverables:**
- Getting started guide
- Development workflow documentation
- Testing guide
- Contribution guidelines
- Troubleshooting FAQ

#### 7.4 - Docsify Finalization
**Description:** Polish documentation site  
**Estimated Time:** 0.5 hours  
**Dependencies:** Tasks 7.1-7.3  

**Deliverables:**
- Navigation sidebar complete
- Search functionality tested
- Code syntax highlighting
- Responsive design validated

---

## ✅ Definition of Done (DoD)

### Functional Completeness
1. ✅ All task CRUD operations working in Cortex-Clean backend
2. ✅ Frontend displays task list with create, update, delete, toggle functionality
3. ✅ API returns proper HTTP status codes and error messages
4. ✅ Database migrations applied successfully
5. ✅ No SQL injection vulnerabilities (parameterized queries only)

### Code Quality
6. ✅ Clean Architecture maintained: Domain → Application → Infrastructure → API
7. ✅ SOLID principles followed (single responsibility, dependency inversion)
8. ✅ No hard-coded connection strings or credentials
9. ✅ All components have single responsibility
10. ✅ Dependency injection used throughout

### Testing Requirements
11. ✅ Backend test coverage ≥90% (unit + integration)
12. ✅ Frontend test coverage ≥85% (unit + component)
13. ✅ E2E tests cover critical user journeys
14. ✅ All tests pass in CI pipeline
15. ✅ TDD workflow documented in git history (RED→GREEN→REFACTOR commits)

### TDD Requirements (Auto-Injected)
16. ✅ RED phase verified: All tests written first and failed initially
17. ✅ GREEN phase verified: Minimal implementation to pass tests
18. ✅ REFACTOR phase verified: Code improved while tests remain green
19. ✅ Git checkpoints at phase boundaries with passing tests

### Documentation Requirements
20. ✅ Docsify documentation complete with all phases documented
21. ✅ Architecture diagrams generated and current
22. ✅ Before/after comparisons for each refactoring
23. ✅ ADRs (Architecture Decision Records) for key decisions
24. ✅ Developer onboarding guide complete

### Deployment Readiness
25. ✅ API runs successfully with `dotnet run`
26. ✅ Frontend runs successfully with `ng serve`
27. ✅ Database migrations can be applied to fresh database
28. ✅ Configuration management uses environment variables
29. ✅ README with setup instructions complete

---

## 📊 Success Metrics

### Quantitative
- **Lines of Code Reduction:** Target 40% reduction through proper abstraction
- **Cyclomatic Complexity:** Average <5 per method
- **Test Coverage:** Backend 90%+, Frontend 85%+
- **Build Time:** <2 minutes for full solution
- **API Response Time:** <200ms for typical operations

### Qualitative
- **Maintainability:** New developers can add features without modifying existing code
- **Testability:** Business logic testable without infrastructure
- **Scalability:** Layers can be deployed independently
- **Security:** No vulnerabilities in OWASP Top 10

---

## 🔄 Automated Documentation System

### Integration with Planning Orchestrator

A custom documentation orchestrator extension will be created to automate Docsify updates:

**Location:** `src/orchestrators/documentation_orchestrator.py`

**Functionality:**
1. **Phase Completion Hook:** Triggered automatically at end of each phase
2. **Content Generation:**
   - Architecture diagrams (Mermaid)
   - Code metrics (coverage, complexity)
   - Git history analysis (TDD commit patterns)
   - Before/after diffs
3. **Docsify Integration:**
   - Updates `docs/_sidebar.md` with new pages
   - Generates markdown files in `docs/phases/`
   - Embeds code examples with syntax highlighting
4. **Template System:**
   - Phase summary template
   - Architecture decision template
   - Refactoring comparison template

**Usage:**
```python
from src.orchestrators.documentation_orchestrator import DocumentationOrchestrator

# Auto-invoked by planning orchestrator at phase boundaries
doc_orchestrator = DocumentationOrchestrator(
    project_path="cortex-sample-apps/Cortex-Clean",
    docs_path="cortex-sample-apps/Cortex-Clean/docs"
)

doc_orchestrator.document_phase_completion(
    phase_number=1,
    phase_name="Foundation & Infrastructure Setup",
    tasks_completed=["1.1", "1.2", "1.3", "1.4"],
    metrics={
        "test_coverage": 92,
        "lines_added": 450,
        "lines_deleted": 0
    }
)
```

**Deliverables:**
- Auto-generated phase summaries
- Interactive architecture diagrams
- Searchable code examples
- Live metrics dashboard (embedded in docs)

---

## 🎯 Risk Assessment

### Technical Risks
1. **EF Core Migration Issues** - Mitigation: Test with fresh database, document rollback
2. **Frontend State Complexity** - Mitigation: Use proven state management (NgRx or Signals)
3. **Test Coverage Gaps** - Mitigation: Enforce coverage gates in CI

### Schedule Risks
1. **Phase 2 Complexity** - Mitigation: Break into smaller tasks if needed
2. **Documentation Time** - Mitigation: Automate with orchestrator

---

## 📅 Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Foundation | 8 hours | 8 hours |
| Phase 2: Application Layer | 10 hours | 18 hours |
| Phase 3: Infrastructure | 8 hours | 26 hours |
| Phase 4: API Layer | 6 hours | 32 hours |
| Phase 5: Frontend Foundation | 8 hours | 40 hours |
| Phase 6: Frontend Features | 10 hours | 50 hours |
| Phase 7: Documentation | 6 hours | 56 hours |

**Total Estimated Effort:** 56 hours (7 working days)

---

## 🚀 Getting Started

### Approval Process
1. Review this plan document
2. Confirm DoR requirements met
3. Approve plan: `approve plan badmonolith-refactor-001`
4. Execute autonomously: `execute all phases autonomously`

### Manual Execution
Alternatively, execute phase-by-phase:
1. `execute phase 1`
2. Review Phase 1 results
3. `execute phase 2`
4. Continue until Phase 7

---

## 📝 Notes

- This plan uses CORTEX Planning System 2.0 with autonomous execution support
- TDD requirements are automatically enforced by Brain Protector (SKULL)
- Documentation is auto-generated at phase boundaries
- Git checkpoints ensure rollback capability
- All code in `Cortex-Clean` folder is independent of CORTEX codebase (git isolation)

---

**Plan Status:** Ready for approval  
**Next Action:** Review and approve plan, then execute autonomously
