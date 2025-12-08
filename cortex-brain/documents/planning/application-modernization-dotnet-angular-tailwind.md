# Application Modernization Plan: .NET Core + Angular + Tailwind CSS

**Plan ID:** APP-MOD-001  
**Version:** 1.0  
**Created:** December 8, 2025  
**Author:** Asif Hussain  
**Status:** draft  
**Target Location:** `cortex-sample-apps\Cortex-SDD`

---

## 🎯 Overview

**Objective:** Rewrite sample application using latest technology stack (.NET Core + Angular latest + Tailwind CSS) with Clean Architecture, following TDD Mastery methodology.

**Complexity Assessment:** HIGH
- **Rationale:** Full-stack rewrite with modern framework migrations, requires security considerations, database schema migrations, comprehensive testing strategy, and framework integration complexity.
- **Plan Generation Strategy:** Incremental (skeleton → P1 → P2 → P3)

**Current State:**
- BadMonolith: .NET 8 minimal API + Angular (monolithic, no tests, no architecture)
- CleanSolidApp: ASP.NET Core Web API + Angular (layered, SOLID principles)
- Cortex-Clean: .NET 8 + Angular 19 (Clean Architecture + CQRS, 90%+ test coverage)

**Target State:**
- New application in `cortex-sample-apps\Cortex-SDD`
- .NET Core 9 (latest) backend with Clean Architecture + CQRS
- Angular 19 (latest) frontend with standalone components + Tailwind CSS
- Comprehensive TDD implementation (90%+ coverage)
- Side-by-side comparison documentation

---

## 📋 Definition of Ready (DoR)

### Functional Requirements
1. ✅ **Scope Defined:** Full-stack task management application with CRUD operations
2. ✅ **Success Criteria:** Production-ready application with 90%+ test coverage, Clean Architecture implementation, modern UI with Tailwind CSS
3. ✅ **Dependencies Identified:** .NET 9 SDK, Angular CLI 19, Node.js 20+, SQLite/EF Core 9
4. ✅ **Resource Availability:** All tooling available, no external API dependencies
5. ✅ **Acceptance Criteria:** Application runs locally, all tests pass, responsive UI with Tailwind, architecture documentation complete

### TDD Requirements (Auto-Injected)
6. ✅ **TDD Mastery Workflow:** RED→GREEN→REFACTOR mandatory for all code
7. ✅ **RED Phase Validation:** Tests MUST fail before implementation
8. ✅ **Git Checkpoints:** Required at RED, GREEN, REFACTOR phases
9. ✅ **Coverage Targets:** Domain: 90%, Application: 85%, Infrastructure: 70%, API: 80%
10. ✅ **Test File Validation:** Per-layer test files required for all production code
11. ✅ **Quality Validation:** No empty/placeholder tests (UnitTest1, Test1, etc.)

---

## ✅ Definition of Done (DoD)

### Completion Criteria
1. ✅ **Implementation Complete:** All layers implemented with full CRUD operations
2. ✅ **Documentation:** Architecture diagrams, API documentation, deployment guide
3. ✅ **Code Review:** Clean Architecture validated, SOLID principles applied
4. ✅ **Deployment Ready:** Can be deployed to production environment
5. ✅ **Comparison Document:** Side-by-side comparison highlighting before/after changes

### TDD Requirements (Auto-Injected)
6. ✅ **TDD Workflow Followed:** Git history shows test-first commits (RED→GREEN→REFACTOR)
7. ✅ **Test-First Commits:** RED phase commits before GREEN phase commits
8. ✅ **Coverage Thresholds Met:** All minimum coverage per layer achieved
9. ✅ **No Test Skips:** No ignored tests without documented justification
10. ✅ **Per-Layer Coverage Met:** Domain: 90%, Application: 85%, Infrastructure: 70%, API: 80%
11. ✅ **No Placeholder Tests:** Zero empty test methods in codebase

---

## 📐 Architecture Overview

### Backend Stack
- **.NET Core 9:** Latest LTS version
- **ASP.NET Core:** Web API with minimal APIs
- **Entity Framework Core 9:** Database access with migrations
- **MediatR 13:** CQRS pattern implementation
- **FluentValidation 12:** Input validation
- **Serilog 10:** Structured logging
- **xUnit + FluentAssertions + Moq:** Testing stack

### Frontend Stack
- **Angular 19:** Latest version with standalone components
- **Tailwind CSS 4:** Utility-first CSS framework
- **TypeScript 5.7:** Type safety
- **RxJS 8:** Reactive programming
- **Jasmine + Karma:** Testing framework

### Architecture Pattern
- **Clean Architecture:** Domain → Application → Infrastructure → API
- **CQRS:** Command Query Responsibility Segregation
- **Repository Pattern:** Data abstraction
- **Dependency Injection:** Built-in .NET DI container

---

## 🔧 Implementation Phases

### Phase 1: Project Setup & Infrastructure (RED→GREEN→REFACTOR)

**Objective:** Create solution structure, configure tooling, establish testing infrastructure

**Tasks:**

**1.1 Backend Solution Setup (TDD)**
- **RED:** Create failing test for solution structure validation
- **GREEN:** Create .NET 9 solution with Clean Architecture layers:
  - `Cortex.SDD.Domain` (Class Library)
  - `Cortex.SDD.Application` (Class Library)
  - `Cortex.SDD.Infrastructure` (Class Library)
  - `Cortex.SDD.API` (ASP.NET Core Web API)
  - `Cortex.SDD.Tests.Unit` (xUnit)
  - `Cortex.SDD.Tests.Integration` (xUnit)
- **REFACTOR:** Organize project references, configure build settings
- **Git Checkpoint:** Commit with message "feat: setup backend solution structure (GREEN)"

**1.2 Frontend Application Setup (TDD)**
- **RED:** Create failing test for Angular app initialization
- **GREEN:** Initialize Angular 19 application with standalone components:
  ```bash
  ng new frontend --standalone --style=scss --routing --ssr=false
  ```
- Install Tailwind CSS 4:
  ```bash
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init
  ```
- **REFACTOR:** Configure Tailwind in `tailwind.config.js`, update styles
- **Git Checkpoint:** Commit with message "feat: setup Angular + Tailwind frontend (GREEN)"

**1.3 Database Configuration (TDD)**
- **RED:** Write failing integration test for DbContext initialization
- **GREEN:** Configure EF Core 9 with SQLite, create `ApplicationDbContext`
- **REFACTOR:** Add connection string configuration, migration setup
- **Git Checkpoint:** Commit with message "feat: configure database with EF Core 9 (GREEN)"

**1.4 Testing Infrastructure (TDD)**
- **RED:** Create failing meta-test for test infrastructure
- **GREEN:** Configure xUnit, FluentAssertions, Moq, NSubstitute
- Configure Jasmine/Karma for Angular
- Setup test helpers and base classes
- **REFACTOR:** Create test utilities, factories, builders
- **Git Checkpoint:** Commit with message "feat: establish testing infrastructure (GREEN)"

**Deliverables:**
- ✅ Solution compiles without errors
- ✅ All projects reference correct layers
- ✅ Angular app runs with Tailwind configured
- ✅ Database connection validated
- ✅ Test runners execute successfully

**Coverage Target:** Infrastructure: 70%

---

### Phase 2: Domain Layer Implementation (RED→GREEN→REFACTOR)

**Objective:** Implement core business logic with comprehensive test coverage

**Tasks:**

**2.1 Task Entity & Validation (TDD)**
- **RED:** Write failing tests for `TaskEntity` (20+ test cases):
  - Constructor validation
  - Title length constraints (1-200 chars)
  - Description max length (1000 chars)
  - Status transitions
  - Completion toggle
  - CreatedAt/UpdatedAt timestamps
- **GREEN:** Implement `TaskEntity` with validation logic
- **REFACTOR:** Extract validation to `TaskValidationService`
- **Git Checkpoint:** Commit with message "feat: implement Task entity (GREEN)"

**2.2 Domain Interfaces (TDD)**
- **RED:** Write failing tests for repository contracts
- **GREEN:** Create interfaces:
  - `ITaskRepository` (CRUD + query methods)
  - `IUnitOfWork` (transaction management)
- **REFACTOR:** Add XML documentation comments
- **Git Checkpoint:** Commit with message "feat: define domain interfaces (GREEN)"

**2.3 Domain Exceptions (TDD)**
- **RED:** Write failing tests for exception scenarios
- **GREEN:** Implement custom exceptions:
  - `TaskNotFoundException`
  - `InvalidTaskStateException`
  - `DomainValidationException`
- **REFACTOR:** Add exception factories
- **Git Checkpoint:** Commit with message "feat: implement domain exceptions (GREEN)"

**2.4 Domain Services (TDD)**
- **RED:** Write failing tests for business rule validation
- **GREEN:** Implement `TaskValidationService` with business rules
- **REFACTOR:** Extract validation rules to separate methods
- **Git Checkpoint:** Commit with message "feat: implement domain services (GREEN)"

**Deliverables:**
- ✅ All domain entities with validation
- ✅ Complete interface definitions
- ✅ Exception hierarchy
- ✅ Domain services with business logic
- ✅ 90%+ domain layer test coverage

**Coverage Target:** Domain: 90%

---

### Phase 3: Application Layer Implementation (RED→GREEN→REFACTOR)

**Objective:** Implement CQRS pattern with MediatR, commands, queries, and validators

**Tasks:**

**3.1 Commands & Handlers (TDD)**
- **RED:** Write failing tests for each command handler (50+ tests):
  - `CreateTaskCommand` + `CreateTaskCommandHandler`
  - `UpdateTaskCommand` + `UpdateTaskCommandHandler`
  - `DeleteTaskCommand` + `DeleteTaskCommandHandler`
  - `ToggleTaskCompletionCommand` + handler
- **GREEN:** Implement all command handlers with repository calls
- **REFACTOR:** Extract common handler logic to base class
- **Git Checkpoint:** Commit with message "feat: implement CQRS commands (GREEN)"

**3.2 Queries & Handlers (TDD)**
- **RED:** Write failing tests for query handlers (30+ tests):
  - `GetAllTasksQuery` + handler
  - `GetTaskByIdQuery` + handler
  - `GetTasksByStatusQuery` + handler
  - `SearchTasksQuery` + handler
- **GREEN:** Implement query handlers with optimized projections
- **REFACTOR:** Add pagination, filtering, sorting
- **Git Checkpoint:** Commit with message "feat: implement CQRS queries (GREEN)"

**3.3 DTOs & Mapping (TDD)**
- **RED:** Write failing tests for DTO mapping
- **GREEN:** Create DTOs:
  - `TaskDto`
  - `CreateTaskDto`
  - `UpdateTaskDto`
  - Mapping extensions
- **REFACTOR:** Use AutoMapper or manual mappers
- **Git Checkpoint:** Commit with message "feat: implement DTOs and mapping (GREEN)"

**3.4 FluentValidation (TDD)**
- **RED:** Write failing tests for validators (40+ test cases)
- **GREEN:** Implement validators:
  - `CreateTaskCommandValidator`
  - `UpdateTaskCommandValidator`
  - `ValidationBehavior` (MediatR pipeline)
- **REFACTOR:** Extract common validation rules
- **Git Checkpoint:** Commit with message "feat: implement FluentValidation (GREEN)"

**Deliverables:**
- ✅ All CQRS commands/queries implemented
- ✅ Complete DTO layer
- ✅ Comprehensive validation rules
- ✅ 85%+ application layer test coverage

**Coverage Target:** Application: 85%

---

### Phase 4: Infrastructure Layer Implementation (RED→GREEN→REFACTOR)

**Objective:** Implement data access, repositories, and database migrations

**Tasks:**

**4.1 DbContext & Entity Configuration (TDD)**
- **RED:** Write failing integration tests for DbContext operations
- **GREEN:** Implement `ApplicationDbContext` with:
  - `DbSet<TaskEntity>` 
  - Entity configurations (Fluent API)
  - Soft delete support
  - Audit fields (CreatedAt, UpdatedAt)
- **REFACTOR:** Split entity configurations into separate files
- **Git Checkpoint:** Commit with message "feat: implement DbContext (GREEN)"

**4.2 Repository Implementation (TDD)**
- **RED:** Write failing tests for repository methods (30+ tests)
- **GREEN:** Implement `TaskRepository`:
  - CRUD operations
  - Query methods (GetAll, GetById, Search)
  - Async/await patterns
- **REFACTOR:** Extract base repository pattern
- **Git Checkpoint:** Commit with message "feat: implement repositories (GREEN)"

**4.3 Database Migrations (TDD)**
- **RED:** Write failing test for migration application
- **GREEN:** Create EF Core migrations:
  ```bash
  dotnet ef migrations add InitialCreate
  ```
- **REFACTOR:** Add seed data migration
- **Git Checkpoint:** Commit with message "feat: create database migrations (GREEN)"

**4.4 Unit of Work & Logging (TDD)**
- **RED:** Write failing tests for transaction handling
- **GREEN:** Implement `UnitOfWork` pattern with Serilog integration
- **REFACTOR:** Add structured logging, performance tracking
- **Git Checkpoint:** Commit with message "feat: implement UoW and logging (GREEN)"

**Deliverables:**
- ✅ Complete data access layer
- ✅ Database migrations created
- ✅ Repository pattern implemented
- ✅ 70%+ infrastructure test coverage

**Coverage Target:** Infrastructure: 70%

---

### Phase 5: API Layer Implementation (RED→GREEN→REFACTOR)

**Objective:** Create REST API with controllers, middleware, and Swagger documentation

**Tasks:**

**5.1 Controllers (TDD)**
- **RED:** Write failing integration tests for API endpoints (40+ tests):
  - GET /api/tasks (list all)
  - GET /api/tasks/{id} (get by ID)
  - POST /api/tasks (create)
  - PUT /api/tasks/{id} (update)
  - DELETE /api/tasks/{id} (delete)
  - PATCH /api/tasks/{id}/toggle (toggle completion)
- **GREEN:** Implement `TasksController` with MediatR integration
- **REFACTOR:** Add response caching, compression
- **Git Checkpoint:** Commit with message "feat: implement API controllers (GREEN)"

**5.2 Middleware & Error Handling (TDD)**
- **RED:** Write failing tests for error handling
- **GREEN:** Implement middleware:
  - `ExceptionHandlingMiddleware`
  - `RequestLoggingMiddleware`
  - `ValidationExceptionMiddleware`
- **REFACTOR:** Standardize error response format
- **Git Checkpoint:** Commit with message "feat: implement middleware (GREEN)"

**5.3 Dependency Injection & Configuration (TDD)**
- **RED:** Write failing tests for DI container setup
- **GREEN:** Configure services in `Program.cs`:
  - MediatR registration
  - Repository registration
  - Database registration
  - CORS policy for Angular frontend
  - Swagger/OpenAPI
- **REFACTOR:** Extract configuration to extension methods
- **Git Checkpoint:** Commit with message "feat: configure dependency injection (GREEN)"

**5.4 API Documentation (TDD)**
- **RED:** Write failing test for Swagger generation
- **GREEN:** Configure Swagger with:
  - XML documentation comments
  - Example requests/responses
  - Authentication schemes
- **REFACTOR:** Add API versioning support
- **Git Checkpoint:** Commit with message "feat: implement API documentation (GREEN)"

**Deliverables:**
- ✅ Complete REST API implementation
- ✅ Middleware pipeline configured
- ✅ Swagger documentation accessible
- ✅ 80%+ API layer test coverage

**Coverage Target:** API: 80%

---

### Phase 6: Frontend Core Implementation (RED→GREEN→REFACTOR)

**Objective:** Implement Angular application with standalone components and Tailwind CSS

**Tasks:**

**6.1 Models & Interfaces (TDD)**
- **RED:** Write failing tests for TypeScript models
- **GREEN:** Create models:
  - `Task.model.ts` (matches backend DTOs)
  - `TaskStatus.enum.ts`
  - `ApiResponse.model.ts`
- **REFACTOR:** Add type guards, validation helpers
- **Git Checkpoint:** Commit with message "feat: implement frontend models (GREEN)"

**6.2 HTTP Service (TDD)**
- **RED:** Write failing tests for HTTP operations (20+ tests)
- **GREEN:** Implement `TaskService`:
  - GET all tasks (with filtering)
  - GET task by ID
  - POST create task
  - PUT update task
  - DELETE task
  - PATCH toggle completion
  - Error handling with RxJS operators
- **REFACTOR:** Extract HTTP interceptors
- **Git Checkpoint:** Commit with message "feat: implement HTTP service (GREEN)"

**6.3 State Management (TDD)**
- **RED:** Write failing tests for state management
- **GREEN:** Implement `TaskStateService` using RxJS BehaviorSubject:
  - Task list state
  - Loading state
  - Error state
  - Filter state
- **REFACTOR:** Add optimistic updates
- **Git Checkpoint:** Commit with message "feat: implement state management (GREEN)"

**6.4 Tailwind Configuration (TDD)**
- **RED:** Write failing tests for component styling
- **GREEN:** Configure Tailwind:
  - Custom theme colors
  - Custom utilities
  - Responsive breakpoints
  - Dark mode support
- **REFACTOR:** Create reusable CSS classes
- **Git Checkpoint:** Commit with message "feat: configure Tailwind theme (GREEN)"

**Deliverables:**
- ✅ Complete service layer
- ✅ State management implemented
- ✅ Tailwind configured with custom theme
- ✅ 80%+ frontend service test coverage

---

### Phase 7: Frontend Components (RED→GREEN→REFACTOR)

**Objective:** Build UI components with Tailwind CSS styling

**Tasks:**

**7.1 Task List Component (TDD)**
- **RED:** Write failing component tests (15+ tests)
- **GREEN:** Implement `TaskListComponent` (standalone):
  - Display all tasks
  - Filter by status (All/Active/Completed)
  - Sort options
  - Loading state
  - Empty state
  - Tailwind styling (cards, grid layout)
- **REFACTOR:** Extract filter/sort logic to separate components
- **Git Checkpoint:** Commit with message "feat: implement task list component (GREEN)"

**7.2 Task Item Component (TDD)**
- **RED:** Write failing component tests (12+ tests)
- **GREEN:** Implement `TaskItemComponent` (standalone):
  - Display task details
  - Toggle completion checkbox
  - Edit button
  - Delete button
  - Tailwind styling (hover states, transitions)
- **REFACTOR:** Add animations with Tailwind
- **Git Checkpoint:** Commit with message "feat: implement task item component (GREEN)"

**7.3 Task Form Component (TDD)**
- **RED:** Write failing form tests (20+ tests)
- **GREEN:** Implement `TaskFormComponent` (standalone):
  - Create/edit mode
  - Reactive forms with validation
  - Title input (required, max length)
  - Description textarea
  - Status dropdown
  - Submit/cancel buttons
  - Tailwind form styling
- **REFACTOR:** Extract form validation to separate service
- **Git Checkpoint:** Commit with message "feat: implement task form component (GREEN)"

**7.4 Layout & Navigation (TDD)**
- **RED:** Write failing layout tests
- **GREEN:** Implement layout components:
  - `HeaderComponent` (navigation, logo)
  - `FooterComponent`
  - Responsive sidebar (mobile menu)
  - Tailwind responsive utilities
- **REFACTOR:** Add accessibility features (ARIA labels, keyboard navigation)
- **Git Checkpoint:** Commit with message "feat: implement layout components (GREEN)"

**Deliverables:**
- ✅ All UI components implemented
- ✅ Responsive design with Tailwind
- ✅ Form validation working
- ✅ 75%+ component test coverage

---

### Phase 8: Integration & End-to-End Testing (RED→GREEN→REFACTOR)

**Objective:** Ensure frontend and backend integration, E2E workflows validated

**Tasks:**

**8.1 API Integration Tests (TDD)**
- **RED:** Write failing integration tests (25+ tests)
- **GREEN:** Test API endpoints with real database:
  - CRUD operations
  - Validation scenarios
  - Error handling
  - Concurrency scenarios
- **REFACTOR:** Add test data builders
- **Git Checkpoint:** Commit with message "feat: implement API integration tests (GREEN)"

**8.2 Frontend Integration Tests (TDD)**
- **RED:** Write failing integration tests (20+ tests)
- **GREEN:** Test component interactions:
  - Create task workflow
  - Edit task workflow
  - Delete task workflow
  - Filter/sort functionality
- **REFACTOR:** Add mock HTTP responses
- **Git Checkpoint:** Commit with message "feat: implement frontend integration tests (GREEN)"

**8.3 E2E Test Suite (Optional TDD)**
- **RED:** Write failing E2E scenarios
- **GREEN:** Implement E2E tests with Playwright or Cypress:
  - User registration/login flow
  - Complete task management workflow
  - Responsive design validation
- **REFACTOR:** Add CI/CD pipeline integration
- **Git Checkpoint:** Commit with message "feat: implement E2E test suite (GREEN)"

**8.4 Performance Testing (TDD)**
- **RED:** Write failing performance tests
- **GREEN:** Test performance benchmarks:
  - API response times (<200ms)
  - Frontend rendering (<1s)
  - Database query performance
- **REFACTOR:** Add performance monitoring
- **Git Checkpoint:** Commit with message "feat: implement performance tests (GREEN)"

**Deliverables:**
- ✅ Complete integration test suite
- ✅ E2E workflows validated
- ✅ Performance benchmarks met
- ✅ All tests passing

---

### Phase 9: Documentation & Deployment (TDD Optional)

**Objective:** Complete architecture documentation, deployment guides, and README

**Tasks:**

**9.1 Architecture Documentation**
- Create architecture diagrams:
  - Clean Architecture layers diagram
  - CQRS flow diagram
  - Database schema diagram
  - Frontend component hierarchy
- Document design decisions in ADR format
- **Git Checkpoint:** Commit with message "docs: add architecture documentation"

**9.2 API Documentation**
- Generate Swagger/OpenAPI spec
- Add Postman collection
- Create API usage examples
- **Git Checkpoint:** Commit with message "docs: add API documentation"

**9.3 Deployment Guide**
- Create `DEPLOYMENT.md` with:
  - Prerequisites (SDK versions)
  - Backend setup instructions
  - Frontend build process
  - Database migration steps
  - Environment variable configuration
  - Docker containerization (optional)
- **Git Checkpoint:** Commit with message "docs: add deployment guide"

**9.4 README & Contributing**
- Update `README.md` with:
  - Project overview
  - Tech stack details
  - Quick start guide
  - Architecture summary
  - Testing instructions
- Create `CONTRIBUTING.md`
- **Git Checkpoint:** Commit with message "docs: complete project README"

**Deliverables:**
- ✅ Complete architecture documentation
- ✅ API documentation published
- ✅ Deployment guide created
- ✅ README comprehensive and up-to-date

---

### Phase 10: Side-by-Side Comparison Document (FINAL PHASE)

**Objective:** Create comprehensive comparison highlighting before/after changes

**Tasks:**

**10.1 Technology Stack Comparison**
- Document technology changes:
  - Backend: .NET 8 → .NET 9
  - Frontend: Angular variations → Angular 19 latest
  - CSS: No framework / basic CSS → Tailwind CSS 4
  - Database: EF Core 8 → EF Core 9
  - Testing: Various → xUnit + Jasmine unified
- Create comparison table with versions
- **Git Checkpoint:** Commit with message "docs: add tech stack comparison"

**10.2 Architecture Evolution**
- Compare architectural approaches:
  - BadMonolith (no architecture) → Clean Architecture
  - No separation → 4-layer separation (Domain/App/Infra/API)
  - Direct SQL → EF Core with Repository pattern
  - No CQRS → MediatR + CQRS
- Create before/after architecture diagrams
- **Git Checkpoint:** Commit with message "docs: add architecture comparison"

**10.3 Code Quality Metrics**
- Compare metrics:
  - Test coverage: 0% → 90%+
  - Lines of code (per layer)
  - Cyclomatic complexity
  - Dependency count
  - Bundle size (frontend)
  - Performance benchmarks
- Create metrics dashboard/table
- **Git Checkpoint:** Commit with message "docs: add quality metrics comparison"

**10.4 Developer Experience Improvements**
- Document DX improvements:
  - No tests → Comprehensive TDD workflow
  - No documentation → Complete API docs + Swagger
  - Monolithic → Modular architecture
  - No type safety → Full TypeScript coverage
  - Inline styles → Tailwind utility classes
- List benefits and developer productivity gains
- **Git Checkpoint:** Commit with message "docs: add developer experience comparison"

**10.5 Final Comparison Document**
- Create `cortex-sample-apps/Cortex-SDD/COMPARISON.md` with:
  - Executive summary
  - Technology stack comparison table
  - Architecture evolution (diagrams + narrative)
  - Code quality metrics
  - Developer experience improvements
  - Migration lessons learned
  - Recommendations for future projects
- Add side-by-side code snippets showing improvements
- **Git Checkpoint:** Commit with message "docs: complete side-by-side comparison document"

**Deliverables:**
- ✅ `COMPARISON.md` created and comprehensive
- ✅ Before/after diagrams included
- ✅ Metrics table with quantifiable improvements
- ✅ Code snippet comparisons provided
- ✅ Migration lessons documented

---

## 📊 Success Metrics

### Test Coverage Targets
- **Domain Layer:** 90%+ (MUST meet)
- **Application Layer:** 85%+ (MUST meet)
- **Infrastructure Layer:** 70%+ (MUST meet)
- **API Layer:** 80%+ (MUST meet)
- **Frontend Services:** 80%+
- **Frontend Components:** 75%+

### Performance Targets
- API response time: <200ms (p95)
- Frontend initial load: <2s
- Time to interactive: <3s
- Lighthouse score: 90+ (all categories)
- Bundle size: <500KB (gzipped)

### Code Quality Targets
- Zero critical security vulnerabilities
- Zero code smells (SonarQube)
- Cyclomatic complexity: <10 per method
- All SOLID principles applied
- 100% XML documentation coverage

---

## 🔄 Git Workflow & TDD Checkpoints

### Checkpoint Strategy
- **RED Phase:** Commit failing test with prefix "test(red):"
- **GREEN Phase:** Commit minimal implementation with prefix "feat:"
- **REFACTOR Phase:** Commit improvements with prefix "refactor:"

### Example Git History
```
test(red): add failing tests for TaskEntity validation
feat: implement TaskEntity with basic validation (GREEN)
refactor: extract validation to TaskValidationService
test(red): add failing tests for CreateTaskCommand
feat: implement CreateTaskCommandHandler (GREEN)
refactor: extract common handler logic to base class
```

### Branch Strategy
- `main` - Stable, reviewed code
- `feature/phase-X` - Phase-specific development
- `test/red-phase-X` - RED phase test commits

---

## 🚨 Risks & Mitigation

### Risk 1: Framework Version Incompatibilities
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Use latest stable versions, check compatibility matrix, maintain version lockfile

### Risk 2: Migration Complexity
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation:** Incremental approach, comprehensive testing, rollback plan

### Risk 3: Learning Curve (Tailwind CSS)
- **Likelihood:** Low
- **Impact:** Low
- **Mitigation:** Use Tailwind documentation, component library examples, pair programming

### Risk 4: Test Coverage Gaps
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** TDD enforcement, automated coverage checks, peer review

---

## 📚 References

### Technology Documentation
- [.NET 9 Documentation](https://docs.microsoft.com/en-us/dotnet/core/)
- [Angular 19 Documentation](https://angular.dev/)
- [Tailwind CSS 4 Documentation](https://tailwindcss.com/docs)
- [Entity Framework Core 9](https://docs.microsoft.com/en-us/ef/core/)
- [MediatR](https://github.com/jbogard/MediatR)
- [FluentValidation](https://docs.fluentvalidation.net/)

### CORTEX Resources
- Planning Orchestrator Guide: `.github/prompts/modules/planning-orchestrator-guide.md`
- TDD Mastery Guide: `.github/prompts/modules/tdd-mastery-guide.md`
- Brain Protection Rules: `cortex-brain/brain-protection-rules.yaml`
- Response Templates: `cortex-brain/response-templates.yaml`

---

## 📝 Notes

### Plan Generation Strategy
This plan uses **incremental generation** due to HIGH complexity:
- **Skeleton phase:** Project setup + infrastructure (Phase 1)
- **Phase 1 generation:** Domain + Application layers (Phases 2-3)
- **Phase 2 generation:** Infrastructure + API (Phases 4-5)
- **Phase 3 generation:** Frontend + Testing + Documentation (Phases 6-10)

This prevents response length failures while maintaining comprehensive planning.

### TDD Enforcement
All phases strictly follow RED→GREEN→REFACTOR with git checkpoints. Brain Protector challenges violations with evidence-based recommendations.

### Autonomous Execution Compatibility
This plan is designed for autonomous execution with the command:
```
execute all phases autonomously
```

Progress monitoring will track:
- Phase completion (1-10)
- Task completion percentage
- ETA based on task velocity
- Git checkpoint success/failure

---

## 🎯 Next Steps

1. **Review Plan:** Validate scope, timeline, resource requirements
2. **Approve Plan:** Use `approve plan` command to move to approved state
3. **Execute:** Choose execution mode:
   - **Manual:** Execute phases one-by-one with approval gates
   - **Autonomous:** Use `execute all phases autonomously` for end-to-end execution
4. **Monitor:** Track progress via CORTEX dashboard or console output
5. **Document:** Capture learnings in `cortex-brain/documents/learning/milestones/`

---

**Plan Status:** draft  
**Location:** `cortex-brain/documents/planning/application-modernization-dotnet-angular-tailwind.md`  
**Ready for Approval:** Yes  
**Autonomous Execution Compatible:** Yes
