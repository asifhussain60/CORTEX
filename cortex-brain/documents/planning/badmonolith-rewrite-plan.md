# BadMonolith → Cortex-SDD Rewrite Plan

**Created:** December 8, 2025  
**Author:** CORTEX Planning System 2.0  
**Project:** BadMonolith Complete Rewrite (Software-Driven Development)  
**Target Stack:** .NET Core 8+ | Angular 18+ | Tailwind CSS 3.4+  
**Target Location:** `cortex-sample-apps\Cortex-SDD`

---

## 📋 Executive Summary

**Objective:** Transform BadMonolith (anti-pattern showcase) into Cortex-SDD (Software-Driven Development reference app) using modern tech stack, TDD Mastery, and best practices. Build comprehensive learning library throughout development for knowledge retention and reuse.

**Technology Stack:**
- **Backend:** .NET 8 Web API with Clean Architecture
- **Frontend:** Angular 18 with Tailwind CSS 3.4
- **Database:** SQL Server with EF Core 8
- **Testing:** xUnit, Jasmine/Karma, 80%+ coverage with TDD Mastery
- **Infrastructure:** Docker, CI/CD ready
- **Documentation:** 30+ learning library guides created progressively

**Timeline Estimate:** 5-7 weeks (200-280 hours) - includes Phase 6 comparison documentation and learning library

**Team Size:** 1-2 developers

---

## 🎯 Definition of Ready (DoR)

### Technical Prerequisites

✅ **Environment Setup**
- [ ] .NET 8 SDK installed
- [ ] Node.js 20+ and npm 10+ installed
- [ ] Angular CLI 18+ installed globally
- [ ] SQL Server 2019+ or LocalDB available
- [ ] Docker Desktop installed (optional)
- [ ] VS Code / Visual Studio 2022 configured

✅ **Architecture Decisions**
- [ ] Clean Architecture layers defined (Domain, Application, Infrastructure, API)
- [ ] Angular architecture approved (modules, lazy loading, state management)
- [ ] Database schema designed with proper normalization
- [ ] API contract defined (OpenAPI/Swagger spec)
- [ ] Security requirements documented (JWT, CORS, rate limiting)

✅ **Quality Gates**
- [ ] TDD workflow enforced (RED → GREEN → REFACTOR)
- [ ] Code coverage threshold: Backend 80%, Frontend 70%
- [ ] SonarQube/ESLint rules configured
- [ ] Git branching strategy agreed (feature branches, PR reviews)

✅ **Dependencies**
- [ ] NuGet packages list approved (EF Core, MediatR, FluentValidation, AutoMapper, Serilog)
- [ ] npm packages list approved (Angular Material or PrimeNG, RxJS, TailwindCSS)
- [ ] DevOps tools available (GitHub Actions or Azure DevOps)

### Business Prerequisites

- [ ] Functional requirements documented
- [ ] UI/UX mockups approved (Figma/Adobe XD)
- [ ] Non-functional requirements defined (performance, scalability)
- [ ] Stakeholder sign-off obtained

---

## 🏗️ Architecture Design

### Backend: Clean Architecture (.NET 8)

**Location:** `cortex-sample-apps\Cortex-SDD\backend\`

```
Cortex-SDD.sln
├── src/
│   ├── CortexSDD.Domain/           # Core business logic (entities, enums, exceptions)
│   │   ├── Entities/
│   │   │   └── Task.cs
│   │   ├── Common/
│   │   │   └── BaseEntity.cs
│   │   └── Exceptions/
│   │       └── TaskNotFoundException.cs
│   │
│   ├── CortexSDD.Application/      # Use cases, DTOs, interfaces
│   │   ├── Common/
│   │   │   ├── Interfaces/
│   │   │   │   └── IApplicationDbContext.cs
│   │   │   └── Mappings/
│   │   │       └── MappingProfile.cs
│   │   ├── Tasks/
│   │   │   ├── Commands/
│   │   │   │   ├── CreateTask/
│   │   │   │   │   ├── CreateTaskCommand.cs
│   │   │   │   │   ├── CreateTaskCommandHandler.cs
│   │   │   │   │   └── CreateTaskCommandValidator.cs
│   │   │   │   ├── UpdateTask/
│   │   │   │   └── DeleteTask/
│   │   │   ├── Queries/
│   │   │   │   ├── GetTasks/
│   │   │   │   │   ├── GetTasksQuery.cs
│   │   │   │   │   └── GetTasksQueryHandler.cs
│   │   │   │   └── GetTaskById/
│   │   │   └── DTOs/
│   │   │       ├── TaskDto.cs
│   │   │       └── TaskListDto.cs
│   │   └── DependencyInjection.cs
│   │
│   ├── CortexSDD.Infrastructure/   # EF Core, external services
│   │   ├── Data/
│   │   │   ├── ApplicationDbContext.cs
│   │   │   ├── Configurations/
│   │   │   │   └── TaskConfiguration.cs
│   │   │   └── Migrations/
│   │   ├── Repositories/
│   │   │   └── TaskRepository.cs (if needed)
│   │   └── DependencyInjection.cs
│   │
│   └── CortexSDD.API/              # Web API controllers, middleware
│       ├── Controllers/
│       │   └── TasksController.cs
│       ├── Middleware/
│       │   ├── ExceptionHandlingMiddleware.cs
│       │   └── RequestLoggingMiddleware.cs
│       ├── Program.cs
│       ├── appsettings.json
│       └── appsettings.Development.json
│
└── tests/
    ├── CortexSDD.Domain.Tests/
    ├── CortexSDD.Application.Tests/
    ├── CortexSDD.Infrastructure.Tests/
    └── CortexSDD.API.Tests/
        ├── Controllers/
        │   └── TasksControllerTests.cs
        └── Integration/
            └── TasksEndpointTests.cs
```

**Key Patterns:**
- **CQRS:** MediatR for command/query separation
- **Repository Pattern:** EF Core DbContext as unit of work
- **Validation:** FluentValidation for input validation
- **Mapping:** AutoMapper for DTO transformations
- **Logging:** Serilog with structured logging
- **Error Handling:** Global exception middleware with ProblemDetails

### Frontend: Angular 18 + Tailwind CSS

**Location:** `cortex-sample-apps\Cortex-SDD\frontend\`

```
cortex-sdd-app/
├── src/
│   ├── app/
│   │   ├── core/                         # Singleton services, guards, interceptors
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts
│   │   │   │   └── error-handler.service.ts
│   │   │   ├── interceptors/
│   │   │   │   ├── auth.interceptor.ts
│   │   │   │   └── error.interceptor.ts
│   │   │   ├── guards/
│   │   │   │   └── auth.guard.ts
│   │   │   └── core.module.ts
│   │   │
│   │   ├── shared/                       # Reusable components, directives, pipes
│   │   │   ├── components/
│   │   │   │   ├── loading-spinner/
│   │   │   │   └── confirmation-dialog/
│   │   │   ├── directives/
│   │   │   ├── pipes/
│   │   │   └── shared.module.ts
│   │   │
│   │   ├── features/                     # Feature modules (lazy loaded)
│   │   │   └── tasks/
│   │   │       ├── components/
│   │   │       │   ├── task-list/
│   │   │       │   │   ├── task-list.component.ts
│   │   │       │   │   ├── task-list.component.html
│   │   │       │   │   ├── task-list.component.scss
│   │   │       │   │   └── task-list.component.spec.ts
│   │   │       │   ├── task-detail/
│   │   │       │   └── task-form/
│   │   │       ├── services/
│   │   │       │   ├── task.service.ts
│   │   │       │   └── task.service.spec.ts
│   │   │       ├── models/
│   │   │       │   └── task.model.ts
│   │   │       ├── state/               # NgRx or signals (optional)
│   │   │       │   ├── task.actions.ts
│   │   │       │   ├── task.reducer.ts
│   │   │       │   └── task.selectors.ts
│   │   │       ├── tasks-routing.module.ts
│   │   │       └── tasks.module.ts
│   │   │
│   │   ├── app.component.ts
│   │   ├── app-routing.module.ts
│   │   └── app.module.ts
│   │
│   ├── assets/
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── styles.scss                      # Tailwind imports
│   └── main.ts
│
├── tailwind.config.js
├── angular.json
└── package.json
```

**Key Features:**
- **Standalone Components:** Angular 18+ standalone API (optional migration)
- **Signals:** Angular 17+ signals for reactive state
- **Lazy Loading:** Feature modules loaded on-demand
- **Tailwind CSS:** Utility-first styling with custom theme
- **Responsive Design:** Mobile-first approach
- **Accessibility:** WCAG 2.1 AA compliance
- **PWA Ready:** Service workers, offline support (optional)

### Database Schema

```sql
-- Clean, normalized schema with proper constraints

CREATE TABLE Tasks (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX) NULL,
    IsCompleted BIT NOT NULL DEFAULT 0,
    Priority INT NOT NULL DEFAULT 0,
    DueDate DATETIME2 NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy NVARCHAR(100) NULL,
    UpdatedBy NVARCHAR(100) NULL,
    
    CONSTRAINT CK_Tasks_Priority CHECK (Priority BETWEEN 0 AND 5),
    INDEX IX_Tasks_IsCompleted (IsCompleted),
    INDEX IX_Tasks_DueDate (DueDate)
);

-- Audit table (optional)
CREATE TABLE TaskAuditLog (
    AuditId INT IDENTITY(1,1) PRIMARY KEY,
    TaskId INT NOT NULL,
    Action NVARCHAR(50) NOT NULL, -- Created, Updated, Deleted
    ChangedBy NVARCHAR(100) NOT NULL,
    ChangedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    OldValue NVARCHAR(MAX) NULL,
    NewValue NVARCHAR(MAX) NULL
);
```

---

## 📚 Learning Library Strategy

**Purpose:** Build a comprehensive, reusable knowledge base throughout the rewrite process that serves as both documentation and training material for future projects.

### Learning Library Structure

**Location:** `cortex-sample-apps\Cortex-SDD\docs\learning-library\`

**Total Documents:** 30+ guides covering all aspects of modern .NET and Angular development

**Organization:**
```
docs/learning-library/
├── README.md                              # Master index with learning paths
├── phase1-foundation-setup.md            # Phase 1 overview and decisions
├── phase2-api-development.md             # Phase 2 implementation guide
├── phase3-ui-development.md              # Phase 3 component development
├── phase4-authentication.md              # Phase 4 security features
├── phase5-deployment.md                  # Phase 5 production deployment
├── phase6-transformation-analysis.md     # Phase 6 comparison and insights
├── clean-architecture-primer.md          # Architecture patterns explained
├── cqrs-with-mediatr.md                  # CQRS implementation guide
├── ef-core-setup.md                      # EF Core configuration patterns
├── angular18-standalone.md               # Angular 18 features
├── tailwind-setup.md                     # Tailwind CSS integration
├── fluentvalidation-guide.md             # Validation patterns
├── api-testing-strategies.md             # Testing approaches
├── swagger-documentation.md              # API documentation
├── angular-reactive-forms.md             # Form patterns
├── tailwind-component-patterns.md        # Reusable CSS patterns
├── angular-testing.md                    # Component testing
├── rxjs-patterns.md                      # Observable patterns
├── accessibility-checklist.md            # WCAG 2.1 compliance
├── jwt-security.md                       # Token security
├── authorization-policies.md             # Policy-based auth
├── search-optimization.md                # Full-text search
├── security-best-practices.md            # OWASP Top 10
├── docker-containerization.md            # Container best practices
├── monitoring-observability.md           # APM and logging
├── performance-optimization.md           # Optimization strategies
├── cicd-pipeline.md                      # Pipeline patterns
├── production-runbook.md                 # Operational procedures
├── tdd-lessons-learned.md                # TDD insights
├── migration-strategies.md               # Data migration
└── complete-reference-guide.md           # Comprehensive reference
```

### Learning Library Benefits

**For This Project:**
1. **Progressive Documentation** - Capture decisions and patterns as they're made
2. **Knowledge Retention** - Don't lose implementation insights over 5-7 weeks
3. **Onboarding Aid** - New team members can quickly understand architecture
4. **Quality Assurance** - Document the "why" behind every technical decision

**For Future Projects:**
5. **Reusable Templates** - Copy-paste starting points for similar projects
6. **Training Material** - Use as curriculum for team skill development
7. **Reference Architecture** - Proven patterns with real-world examples
8. **Troubleshooting Guide** - Common issues and solutions documented

**For the Organization:**
9. **Institutional Knowledge** - Prevent knowledge loss from turnover
10. **Standardization** - Consistent patterns across projects
11. **Faster Delivery** - Reduce research time on subsequent projects
12. **Quality Baseline** - Established best practices for all teams

### Documentation Standards

**Each Learning Library Document Must Include:**

1. **Purpose Statement** - What this document teaches
2. **Prerequisites** - Required knowledge or setup
3. **Step-by-Step Guide** - Detailed implementation instructions
4. **Code Examples** - Real code from Cortex-SDD with explanations
5. **Common Pitfalls** - Things that went wrong and how to avoid them
6. **Best Practices** - Recommended approaches and patterns
7. **Related Documents** - Links to other learning library entries
8. **Further Reading** - External resources for deeper understanding

**Quality Criteria:**
- **Actionable** - Reader can follow and reproduce
- **Context-Rich** - Explain the "why" not just the "how"
- **Example-Driven** - Show real code from the project
- **Updated** - Reflect actual implementation decisions
- **Searchable** - Include tags and keywords

### Learning Path Recommendations

The `README.md` index will provide learning paths for different roles:

**For Backend Developers:**
1. Clean Architecture Primer → EF Core Setup → CQRS with MediatR
2. FluentValidation Guide → API Testing Strategies → JWT Security
3. Performance Optimization → Docker Containerization

**For Frontend Developers:**
1. Angular 18 Standalone → Tailwind Setup → Angular Reactive Forms
2. RxJS Patterns → Angular Testing → Accessibility Checklist
3. Tailwind Component Patterns → Performance Optimization

**For Full-Stack Developers:**
1. Phase overviews (1-6) → Complete Reference Guide
2. Security Best Practices → Monitoring Observability
3. CI/CD Pipeline → Production Runbook

**For Architects:**
1. Clean Architecture Primer → CQRS with MediatR
2. Security Best Practices → Monitoring Observability
3. Transformation Analysis → Migration Strategies

### Maintenance and Evolution

**Living Documentation:**
- Update documents as implementation evolves
- Add "lessons learned" sections after phase completion
- Include metrics and evidence (test coverage, performance)
- Cross-link related documents for easy navigation

**Version Control:**
- All learning library docs tracked in git
- Document creation date and last updated date
- Change log for significant updates

---

## 📅 Implementation Phases

### Phase 1: Foundation Setup (Week 1)

**Goal:** Establish project structure, CI/CD, and core infrastructure

**Backend Tasks:**
1. Create solution structure with Clean Architecture layers
2. Configure EF Core with code-first migrations
3. Implement base entities and common interfaces
4. Set up MediatR, FluentValidation, AutoMapper
5. Configure Serilog with file/console sinks
6. Add global exception handling middleware
7. Configure Swagger/OpenAPI documentation
8. Set up xUnit test projects with FluentAssertions

**Frontend Tasks:**
1. Create Angular 18 workspace with standalone components
2. Configure Tailwind CSS with custom theme
3. Set up ESLint, Prettier, Husky for code quality
4. Create core module with API service
5. Create shared module with reusable components
6. Configure environment variables
7. Set up Karma/Jasmine for unit tests
8. Add Angular Material or PrimeNG (optional)

**DevOps Tasks:**
1. Create GitHub Actions workflow for CI/CD
2. Configure SonarQube or CodeQL for code analysis
3. Set up Docker Compose for local development
4. Configure database migrations pipeline

**TDD Requirements:**
- ✅ RED: Write failing test for ApplicationDbContext initialization
- ✅ GREEN: Implement DbContext with Tasks DbSet
- ✅ REFACTOR: Extract configuration to separate class
- ✅ Test coverage: 80%+ for infrastructure layer

**DoD for Phase 1:**
- [ ] All projects build successfully
- [ ] Database migrations run without errors
- [ ] Swagger UI accessible at `/swagger`
- [ ] CI/CD pipeline passes all checks
- [ ] Test coverage meets thresholds (80% backend, 70% frontend)
- [ ] Code review completed
- [ ] **Learning Library:** Phase 1 documentation created
  - [ ] `docs/learning-library/phase1-foundation-setup.md` - Setup guide with decisions made
  - [ ] `docs/learning-library/clean-architecture-primer.md` - Clean Architecture explanation
  - [ ] `docs/learning-library/ef-core-setup.md` - EF Core configuration patterns
  - [ ] `docs/learning-library/angular18-standalone.md` - Angular 18 standalone components guide
  - [ ] `docs/learning-library/tailwind-setup.md` - Tailwind CSS integration steps

---

### Phase 2: Task Management API (Week 2)

**Goal:** Implement complete CRUD operations for tasks with validation

**Backend Tasks:**
1. Create Task entity with proper validation
2. Implement CreateTaskCommand with handler and validator
3. Implement UpdateTaskCommand with handler and validator
4. Implement DeleteTaskCommand with handler
5. Implement GetTasksQuery with filtering and pagination
6. Implement GetTaskByIdQuery with handler
7. Add TasksController with all endpoints
8. Configure CORS for Angular app

**API Endpoints:**
```
POST   /api/tasks              - Create new task
GET    /api/tasks              - Get all tasks (with filters)
GET    /api/tasks/{id}         - Get specific task
PUT    /api/tasks/{id}         - Update task
PATCH  /api/tasks/{id}/toggle  - Toggle completion status
DELETE /api/tasks/{id}         - Delete task
```

**TDD Workflow:**

**Test 1: Create Task**
- ✅ RED: Write test expecting task creation to return 201 with task DTO
- ✅ GREEN: Implement CreateTaskCommand, handler, controller action
- ✅ REFACTOR: Extract validation logic to FluentValidation validator

**Test 2: Get Tasks**
- ✅ RED: Write test expecting empty list when no tasks exist
- ✅ GREEN: Implement GetTasksQuery and handler
- ✅ REFACTOR: Add filtering and pagination support

**Test 3: Input Validation**
- ✅ RED: Write test expecting 400 when title is empty
- ✅ GREEN: Add FluentValidation rules
- ✅ REFACTOR: Create reusable validation behavior pipeline

**Test 4: Not Found Handling**
- ✅ RED: Write test expecting 404 when task doesn't exist
- ✅ GREEN: Throw TaskNotFoundException in handler
- ✅ REFACTOR: Add global exception handler for 404 responses

**Test Coverage Requirements:**
- Unit tests: 80%+ (commands, queries, validators)
- Integration tests: Key endpoints (GET, POST, PUT, DELETE)
- Edge cases: Empty inputs, SQL injection attempts, concurrent updates

**DoD for Phase 2:**
- [ ] All CRUD endpoints functional and tested
- [ ] FluentValidation rules enforce business logic
- [ ] Exception handling returns proper HTTP status codes
- [ ] Swagger documentation complete for all endpoints
- [ ] Integration tests pass with in-memory database
- [ ] Code review completed
- [ ] API contract matches OpenAPI spec
- [ ] **Learning Library:** Phase 2 documentation created
  - [ ] `docs/learning-library/phase2-api-development.md` - CRUD implementation guide
  - [ ] `docs/learning-library/cqrs-with-mediatr.md` - CQRS pattern explanation with examples
  - [ ] `docs/learning-library/fluentvalidation-guide.md` - Validation patterns and best practices
  - [ ] `docs/learning-library/api-testing-strategies.md` - Unit and integration testing approaches
  - [ ] `docs/learning-library/swagger-documentation.md` - API documentation best practices

---

### Phase 3: Angular Task UI (Week 3)

**Goal:** Build responsive task management interface with Tailwind CSS

**Frontend Tasks:**
1. Create TaskService with HTTP methods
2. Implement Task model and DTOs
3. Create TaskListComponent with data table
4. Create TaskFormComponent for create/edit
5. Create TaskDetailComponent with modal
6. Add loading states and error handling
7. Implement optimistic UI updates
8. Add toast notifications for user feedback
9. Style all components with Tailwind CSS
10. Add responsive design for mobile/tablet

**UI Features:**
- Task list with sorting, filtering, pagination
- Add task button with modal form
- Inline edit for task title (double-click)
- Checkbox for completion toggle with animation
- Delete confirmation dialog
- Priority badges with color coding
- Due date display with "overdue" indicator
- Empty state illustration when no tasks

**TDD Workflow:**

**Test 1: Task Service**
- ✅ RED: Write test expecting TaskService.getTasks() to return Observable<Task[]>
- ✅ GREEN: Implement TaskService with HttpClient
- ✅ REFACTOR: Add error handling with retry logic

**Test 2: Task List Component**
- ✅ RED: Write test expecting task list to render 3 tasks
- ✅ GREEN: Implement TaskListComponent with *ngFor
- ✅ REFACTOR: Extract task item to child component

**Test 3: Task Form Validation**
- ✅ RED: Write test expecting form to be invalid when title is empty
- ✅ GREEN: Add ReactiveFormsModule with validators
- ✅ REFACTOR: Create custom validators for due date

**Test 4: Optimistic Updates**
- ✅ RED: Write test expecting task to appear immediately on create
- ✅ GREEN: Add task to local array before HTTP call
- ✅ REFACTOR: Rollback on error with toast notification

**Tailwind Styling Example:**
```html
<div class="container mx-auto px-4 py-8">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-gray-800">My Tasks</h1>
    <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg 
                   transition-colors duration-200 flex items-center gap-2">
      <svg class="w-5 h-5"><!-- Plus icon --></svg>
      Add Task
    </button>
  </div>
  
  <div class="bg-white rounded-lg shadow-md overflow-hidden">
    <div *ngFor="let task of tasks" 
         class="p-4 border-b hover:bg-gray-50 transition-colors cursor-pointer">
      <div class="flex items-center gap-3">
        <input type="checkbox" [checked]="task.isCompleted"
               class="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500">
        <span [class.line-through]="task.isCompleted" 
              [class.text-gray-500]="task.isCompleted"
              class="flex-1 text-lg">{{ task.title }}</span>
        <span class="px-3 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
          Priority {{ task.priority }}
        </span>
      </div>
    </div>
  </div>
</div>
```

**Test Coverage Requirements:**
- Component tests: 70%+ (all user interactions)
- Service tests: 80%+ (HTTP calls, error handling)
- Integration tests: End-to-end user flows (Cypress optional)

**DoD for Phase 3:**
- [ ] All UI components functional and styled
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Loading states show during API calls
- [ ] Error messages display user-friendly content
- [ ] Accessibility audit passes (keyboard navigation, ARIA labels)
- [ ] Cross-browser testing completed (Chrome, Firefox, Safari, Edge)
- [ ] Code review completed
- [ ] **Learning Library:** Phase 3 documentation created
  - [ ] `docs/learning-library/phase3-ui-development.md` - Angular component development guide
  - [ ] `docs/learning-library/angular-reactive-forms.md` - Form validation and reactive patterns
  - [ ] `docs/learning-library/tailwind-component-patterns.md` - Reusable Tailwind CSS patterns
  - [ ] `docs/learning-library/angular-testing.md` - Component and service testing strategies
  - [ ] `docs/learning-library/rxjs-patterns.md` - RxJS operators and error handling
  - [ ] `docs/learning-library/accessibility-checklist.md` - WCAG 2.1 AA compliance guide

---

### Phase 4: Advanced Features (Week 4)

**Goal:** Add authentication, authorization, and advanced functionality

**Backend Tasks:**
1. Implement JWT authentication with refresh tokens
2. Add user management (register, login, profile)
3. Add authorization policies (admin, user roles)
4. Implement task filtering by user
5. Add soft delete for tasks
6. Implement task search with full-text indexing
7. Add caching with Redis (optional)
8. Implement rate limiting middleware

**Frontend Tasks:**
1. Create authentication service with JWT storage
2. Implement login/register forms
3. Add auth guard for protected routes
4. Add auth interceptor for API calls
5. Implement user profile page
6. Add advanced filtering (date range, priority, status)
7. Implement task search with debounce
8. Add dark mode toggle with Tailwind

**TDD Workflow:**

**Test 1: JWT Authentication**
- ✅ RED: Write test expecting 401 for unauthorized requests
- ✅ GREEN: Implement JWT middleware
- ✅ REFACTOR: Extract token validation to separate service

**Test 2: Authorization Policies**
- ✅ RED: Write test expecting 403 when user tries to delete admin task
- ✅ GREEN: Add policy-based authorization
- ✅ REFACTOR: Create custom authorization handlers

**Test 3: Search Functionality**
- ✅ RED: Write test expecting search to return matching tasks
- ✅ GREEN: Implement full-text search query
- ✅ REFACTOR: Add search index optimization

**DoD for Phase 4:**
- [ ] Authentication flow works end-to-end
- [ ] Authorization prevents unauthorized access
- [ ] Search returns relevant results in <200ms
- [ ] Security audit completed (OWASP Top 10)
- [ ] Performance testing completed (load testing with k6)
- [ ] Code review completed
- [ ] **Learning Library:** Phase 4 documentation created
  - [ ] `docs/learning-library/phase4-authentication.md` - JWT implementation guide
  - [ ] `docs/learning-library/jwt-security.md` - Token security and refresh strategies
  - [ ] `docs/learning-library/authorization-policies.md` - Policy-based authorization patterns
  - [ ] `docs/learning-library/search-optimization.md` - Full-text search and indexing
  - [ ] `docs/learning-library/security-best-practices.md` - OWASP Top 10 mitigation guide

---

### Phase 5: Polish & Deployment (Weeks 5-6)

**Goal:** Production-ready deployment with monitoring

**Tasks:**
1. Set up Application Insights or ELK stack for logging
2. Configure health checks endpoint
3. Add API versioning
4. Implement database connection resilience (Polly)
5. Configure HTTPS and security headers
6. Create Docker images for API and Angular
7. Set up Kubernetes manifests (optional)
8. Configure Azure App Service or AWS deployment
9. Set up monitoring dashboards
10. Create production runbook documentation

**Performance Optimizations:**
- Enable response compression
- Add output caching for GET endpoints
- Implement lazy loading for Angular routes
- Optimize bundle size with tree shaking
- Add CDN for static assets
- Configure database indexes

**DoD for Phase 5:**
- [ ] Application deployed to production
- [ ] Monitoring dashboards show metrics
- [ ] Health checks return 200 OK
- [ ] Performance benchmarks meet SLAs (API <200ms, UI <2s load)
- [ ] Security scan passes (no critical vulnerabilities)
- [ ] Documentation complete (README, API docs, deployment guide)
- [ ] Stakeholder acceptance obtained
- [ ] **Learning Library:** Phase 5 documentation created
  - [ ] `docs/learning-library/phase5-deployment.md` - Production deployment guide
  - [ ] `docs/learning-library/docker-containerization.md` - Docker best practices for .NET and Angular
  - [ ] `docs/learning-library/monitoring-observability.md` - Application Insights/ELK setup
  - [ ] `docs/learning-library/performance-optimization.md` - Bundle optimization and caching strategies
  - [ ] `docs/learning-library/cicd-pipeline.md` - GitHub Actions/Azure DevOps pipeline patterns
  - [ ] `docs/learning-library/production-runbook.md` - Operational procedures and troubleshooting

---

### Phase 6: Before/After Comparison & Documentation (Week 7)

**Goal:** Create comprehensive comparison documentation showcasing transformation from BadMonolith to Cortex-SDD

**Deliverables:**
1. Side-by-side comparison document
2. TDD Mastery implementation report
3. Lessons learned summary
4. Reference architecture guide

**Comparison Document Tasks:**
1. Create visual side-by-side code comparisons (before/after)
2. Document anti-pattern elimination with evidence
3. Capture metrics improvements (performance, maintainability, test coverage)
4. Generate architecture comparison diagrams
5. Create "what changed and why" narrative for each layer
6. Document security improvements with vulnerability elimination proof
7. Compile test coverage reports (before: 0%, after: 80%+)
8. Create developer experience comparison (DX improvements)

**TDD Mastery Documentation Tasks:**
1. Document all RED → GREEN → REFACTOR cycles
2. Capture test-first success metrics
3. Show test suite evolution throughout phases
4. Document TDD challenges overcome
5. Provide code examples of TDD workflow
6. Calculate time saved by catching bugs early
7. Show correlation between test coverage and defect rate

**Comparison Document Structure:**

```markdown
# BadMonolith → Cortex-SDD Transformation Report

## Executive Summary
- Project overview
- Key metrics (LOC, complexity, test coverage, performance)
- Timeline and effort
- ROI calculation

## Architecture Comparison
- Before: Monolithic chaos (diagrams)
- After: Clean Architecture (diagrams)
- Layer-by-layer breakdown

## Code Quality Comparison
### Backend
- Program.cs (143 lines) → Clean Architecture (distributed)
- SQL injection vulnerability → Parameterized queries
- No validation → FluentValidation pipeline
- Global state → Dependency injection

### Frontend
- Single component (50 lines) → Feature modules (organized)
- No services → Service layer with RxJS
- Inline styles → Tailwind CSS utility classes
- No tests → 70%+ test coverage

## Security Improvements
- Hard-coded credentials → Environment variables/Key Vault
- SQL injection → EF Core parameterization
- No authentication → JWT with refresh tokens
- No authorization → Policy-based RBAC
- No HTTPS → TLS 1.3 enforced
- No input validation → Multi-layer validation

## Performance Improvements
- Before: No caching, N+1 queries, no indexing
- After: Response caching, optimized queries, strategic indexes
- Load time: ~5s → <2s
- API response: ~500ms → <200ms P95

## Test Coverage Transformation
- Before: 0 tests, 0% coverage
- After: 150+ tests, 82% backend, 74% frontend coverage
- Defect detection: 0 bugs caught in dev → 23 bugs caught pre-production

## Maintainability Metrics
- Cyclomatic complexity: Avg 25 → Avg 4
- Code duplication: 40% → 2%
- Technical debt ratio: 45% → 3%
- Time to add feature: ~3 days → ~4 hours

## Developer Experience
- Before: Fear-driven development, manual testing, unclear structure
- After: TDD confidence, automated testing, clear patterns

## Lessons Learned
- What worked well
- What was challenging
- What we'd do differently
- Recommendations for similar projects
```

**TDD Mastery Section Tasks:**
1. Extract all RED commits from git history
2. Extract all GREEN commits from git history
3. Extract all REFACTOR commits from git history
4. Calculate TDD adherence percentage (target: 100%)
5. Document test suite metrics (execution time, flakiness)
6. Show defect prevention evidence (bugs caught in RED phase)
7. Compare estimation accuracy with/without TDD

**Documentation Locations:**
- `cortex-sample-apps\Cortex-SDD\TRANSFORMATION-REPORT.md` (main comparison doc)
- `cortex-sample-apps\Cortex-SDD\TDD-MASTERY-REPORT.md` (TDD-specific analysis)
- `cortex-sample-apps\Cortex-SDD\LESSONS-LEARNED.md` (retrospective)
- `cortex-sample-apps\Cortex-SDD\docs\before-after-screenshots\` (visual comparisons)
- `cortex-sample-apps\Cortex-SDD\docs\architecture-diagrams\` (C4 model diagrams)

**Automated Metrics Collection:**
```bash
# Run analysis scripts to generate metrics
dotnet tool install --global dotnet-coverage
dotnet tool install --global dotnet-sonarscanner

# Backend metrics
dotnet test --collect:"XPlat Code Coverage"
dotnet sonarscanner begin /k:"cortex-sdd"
dotnet build
dotnet sonarscanner end

# Frontend metrics
ng test --code-coverage --watch=false
npm run lint
npm run analyze # Bundle size analysis

# Performance benchmarking
k6 run performance-tests.js
```

**Visual Comparison Assets:**
1. Screenshot: BadMonolith Program.cs with SQL injection highlighted
2. Screenshot: Cortex-SDD clean architecture structure
3. Diagram: BadMonolith monolithic architecture
4. Diagram: Cortex-SDD layered architecture with dependencies
5. Chart: Test coverage progression (Phase 1-5)
6. Chart: Performance improvements (response times)
7. Chart: Code quality metrics (complexity, duplication)
8. Video: Side-by-side UI demo (BadMonolith vs Cortex-SDD)

**DoD for Phase 6:**
- [ ] TRANSFORMATION-REPORT.md completed with all sections
- [ ] TDD-MASTERY-REPORT.md shows 100% TDD adherence
- [ ] All metrics captured with before/after evidence
- [ ] Visual assets created (screenshots, diagrams, charts)
- [ ] Code examples documented with explanations
- [ ] Lessons learned reviewed with team
- [ ] Documentation peer reviewed
- [ ] Final presentation created for stakeholders
- [ ] **Learning Library:** Phase 6 documentation created
  - [ ] `docs/learning-library/phase6-transformation-analysis.md` - Complete transformation journey
  - [ ] `docs/learning-library/tdd-lessons-learned.md` - TDD Mastery insights and metrics
  - [ ] `docs/learning-library/migration-strategies.md` - Data migration and deployment patterns
  - [ ] `docs/learning-library/complete-reference-guide.md` - Comprehensive Cortex-SDD reference
  - [ ] **Learning Library Index:** `docs/learning-library/README.md` created
    - [ ] Consolidated index of all 30+ learning documents
    - [ ] Organized by phase and topic
    - [ ] Quick reference links and search tags
    - [ ] Recommended learning paths for different roles

---

## 🧪 TDD Mastery Integration

**CRITICAL:** Every feature in Phases 1-5 MUST follow TDD Mastery workflow. This section explains how CORTEX's TDD Mastery system is applied throughout the rewrite.

### TDD Mastery Overview

**What is TDD Mastery?**
TDD Mastery is CORTEX's enforced test-driven development workflow that guarantees quality through the RED → GREEN → REFACTOR cycle. It's not optional—it's baked into every development phase.

**Commands:** `start tdd`, `run tests`, `suggest refactorings`  
**Guide:** `.github/prompts/modules/tdd-mastery-guide.md`

### TDD Mastery Workflow Per Phase

#### Phase 1: Foundation Setup
**TDD Application:**
- RED: Write failing test for `ApplicationDbContext` initialization
- GREEN: Implement `DbContext` with `Tasks` DbSet  
- REFACTOR: Extract entity configuration to `TaskConfiguration`

**Example:**
```csharp
// RED: Test fails because ApplicationDbContext doesn't exist
[Fact]
public void ApplicationDbContext_ShouldInitializeTasksDbSet()
{
    var options = new DbContextOptionsBuilder<ApplicationDbContext>()
        .UseInMemoryDatabase(databaseName: "TestDb")
        .Options;
    
    using var context = new ApplicationDbContext(options);
    
    context.Tasks.Should().NotBeNull();
}
// COMMIT: "RED: ApplicationDbContext should initialize Tasks DbSet"

// GREEN: Minimal implementation
public class ApplicationDbContext : DbContext
{
    public DbSet<Domain.Entities.Task> Tasks { get; set; }
    
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) 
        : base(options) { }
}
// COMMIT: "GREEN: Implement ApplicationDbContext with Tasks DbSet"

// REFACTOR: Add entity configuration
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfiguration(new TaskConfiguration());
}
// COMMIT: "REFACTOR: Extract Task configuration to TaskConfiguration class"
```

**TDD Metrics for Phase 1:**
- Target: 15 RED → GREEN → REFACTOR cycles
- Test coverage: 80%+ infrastructure layer
- All tests pass before Phase 2 starts

#### Phase 2: Task Management API
**TDD Application:**
- RED: Test expects 201 Created response with task DTO
- GREEN: Implement CreateTaskCommand handler
- REFACTOR: Add FluentValidation, AutoMapper

**Example:**
```csharp
// RED: Controller endpoint test fails
[Fact]
public async Task CreateTask_ValidRequest_Returns201Created()
{
    // Arrange
    var client = _factory.CreateClient();
    var request = new { title = "Test Task" };
    
    // Act
    var response = await client.PostAsJsonAsync("/api/tasks", request);
    
    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.Created);
    var task = await response.Content.ReadFromJsonAsync<TaskDto>();
    task.Title.Should().Be("Test Task");
}
// COMMIT: "RED: CreateTask endpoint should return 201 with task DTO"

// GREEN: Implement endpoint
[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateTaskCommand command)
{
    var result = await _mediator.Send(command);
    return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
}
// COMMIT: "GREEN: Implement CreateTask endpoint with MediatR"

// REFACTOR: Add validation
public class CreateTaskCommandValidator : AbstractValidator<CreateTaskCommand>
{
    public CreateTaskCommandValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(255);
        RuleFor(x => x.Priority).InclusiveBetween(0, 5);
    }
}
// COMMIT: "REFACTOR: Add FluentValidation to CreateTaskCommand"
```

**TDD Metrics for Phase 2:**
- Target: 25 RED → GREEN → REFACTOR cycles (5 per CRUD operation)
- Test coverage: 85%+ application/API layers
- Integration tests: All endpoints tested

#### Phase 3: Angular Task UI
**TDD Application:**
- RED: Test expects TaskService to return Observable<Task[]>
- GREEN: Implement TaskService with HttpClient
- REFACTOR: Add error handling with retry logic

**Example:**
```typescript
// RED: Service test fails
it('should fetch tasks from API', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', isCompleted: false },
    { id: 2, title: 'Task 2', isCompleted: true }
  ];
  
  service.getTasks().subscribe(tasks => {
    expect(tasks).toEqual(mockTasks);
  });
  
  const req = httpMock.expectOne(`${environment.apiUrl}/tasks`);
  expect(req.request.method).toBe('GET');
  req.flush(mockTasks);
});
// COMMIT: "RED: TaskService should fetch tasks from API"

// GREEN: Implement service
@Injectable()
export class TaskService {
  constructor(private http: HttpClient) {}
  
  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${environment.apiUrl}/tasks`);
  }
}
// COMMIT: "GREEN: Implement TaskService.getTasks()"

// REFACTOR: Add error handling
getTasks(): Observable<Task[]> {
  return this.http.get<Task[]>(`${environment.apiUrl}/tasks`).pipe(
    retry({ count: 3, delay: 1000 }),
    catchError(this.handleError)
  );
}
// COMMIT: "REFACTOR: Add retry logic and error handling to TaskService"
```

**TDD Metrics for Phase 3:**
- Target: 20 RED → GREEN → REFACTOR cycles
- Test coverage: 75%+ frontend (components, services)
- Component tests: All user interactions tested

#### Phase 4: Advanced Features
**TDD Application:**
- RED: Test expects 401 Unauthorized for protected endpoint
- GREEN: Implement JWT authentication middleware
- REFACTOR: Extract token validation to AuthService

**TDD Metrics for Phase 4:**
- Target: 18 RED → GREEN → REFACTOR cycles
- Test coverage maintained: 80%+ backend, 70%+ frontend
- Security tests: All authentication/authorization paths tested

#### Phase 5: Polish & Deployment
**TDD Application:**
- RED: Test expects health check endpoint to return 200 OK
- GREEN: Implement health check endpoint
- REFACTOR: Add database connectivity check

**TDD Metrics for Phase 5:**
- Target: 10 RED → GREEN → REFACTOR cycles
- Test coverage: Maintain thresholds through deployment
- Integration tests: End-to-end smoke tests passing

### TDD Enforcement Rules

**SKULL Tier 0 Instincts (Cannot Bypass):**
1. **TDD_ENFORCEMENT:** RED → GREEN → REFACTOR mandatory for all features
2. **RED_PHASE_VALIDATION:** Tests MUST fail before implementation begins
3. **TEST_LOCATION_SEPARATION:** Cortex-SDD tests in `tests/`, never in `cortex-brain/`
4. **COVERAGE_THRESHOLD_ENFORCEMENT:** Backend ≥80%, Frontend ≥70%

**Brain Protector Challenges:**
If you try to skip TDD or write implementation before tests, Brain Protector will challenge with evidence:
- "TDD-first development has 94% success rate vs 67% without tests"
- "Projects with <70% coverage have 3.2x more production defects"
- "RED phase validation prevents 87% of logic errors"

### TDD Metrics Dashboard

**Tracked Throughout Phases 1-5:**
```yaml
tdd_metrics:
  total_features: 0          # Incremented each feature
  red_commits: 0             # RED phase commits
  green_commits: 0           # GREEN phase commits
  refactor_commits: 0        # REFACTOR phase commits
  tdd_adherence: 100%        # (red + green + refactor) / total_features * 100
  
  test_suite:
    total_tests: 0
    passing_tests: 0
    failing_tests: 0
    skipped_tests: 0
    execution_time_ms: 0
    
  coverage:
    backend_coverage: 0%     # Target: ≥80%
    frontend_coverage: 0%    # Target: ≥70%
    overall_coverage: 0%
    
  defects:
    caught_in_red_phase: 0   # Bugs caught by failing tests
    caught_in_green_phase: 0 # Bugs caught during implementation
    escaped_to_production: 0 # Bugs found after deployment
    
  quality:
    flaky_tests: 0           # Tests with intermittent failures
    test_debt_ratio: 0%      # Untested code / total code
```

**Reporting:**
- Daily: Test suite execution report
- Weekly: Coverage trends and TDD adherence
- Phase completion: Comprehensive TDD metrics report
- Phase 6: Final TDD Mastery Report with all data

### TDD Best Practices for Cortex-SDD

1. **Write the test first, always** - No exceptions
2. **See the test fail** - Verify RED phase before implementing
3. **Minimal implementation** - Just enough code to pass GREEN
4. **Refactor ruthlessly** - Clean code while tests are green
5. **Commit at each phase** - RED → GREEN → REFACTOR as separate commits
6. **Run tests continuously** - Every few minutes during development
7. **Keep tests fast** - Unit tests <100ms, integration tests <1s
8. **Test one thing** - Each test has single clear purpose
9. **Use test names as documentation** - `CreateTask_EmptyTitle_Returns400BadRequest`
10. **Mock external dependencies** - Database, APIs, file system

### TDD Anti-Patterns to Avoid

❌ **Don't:**
- Write implementation before test (violates RED phase)
- Skip REFACTOR phase ("code works, ship it")
- Write tests after implementation (not TDD)
- Make tests depend on each other (brittle)
- Test implementation details (test behavior)
- Ignore failing tests ("I'll fix it later")
- Skip edge cases ("that'll never happen")

✅ **Do:**
- Follow RED → GREEN → REFACTOR religiously
- Refactor tests just like production code
- Use arrange-act-assert pattern consistently
- Test happy path AND edge cases
- Keep test coverage above thresholds
- Fix failing tests immediately
- Treat test code as first-class citizen

---

## ✅ Definition of Done (DoD)

### Code Quality

- [ ] **Test Coverage:** Backend ≥80%, Frontend ≥70%
- [ ] **TDD Workflow:** All features follow RED → GREEN → REFACTOR
- [ ] **Code Review:** At least one approved review per PR
- [ ] **Static Analysis:** SonarQube quality gate passed (0 critical issues)
- [ ] **Linting:** No ESLint/StyleCop warnings
- [ ] **Security Scan:** No vulnerabilities with CVSS ≥7.0

### Functionality

- [ ] **All Acceptance Criteria Met:** Feature works as specified
- [ ] **Edge Cases Handled:** Invalid inputs, network errors, concurrent access
- [ ] **Cross-Browser Compatible:** Chrome, Firefox, Safari, Edge (latest 2 versions)
- [ ] **Responsive Design:** Works on mobile (375px+), tablet (768px+), desktop (1024px+)
- [ ] **Accessibility:** WCAG 2.1 AA compliance (lighthouse score ≥90)

### Documentation

- [ ] **API Documentation:** Swagger/OpenAPI complete with examples
- [ ] **Code Comments:** Complex logic documented with XML/JSDoc comments
- [ ] **README Updated:** Installation, configuration, running instructions
- [ ] **Architecture Diagrams:** C4 model diagrams for system/container/component levels
- [ ] **Deployment Guide:** Step-by-step production deployment instructions

### DevOps

- [ ] **CI/CD Pipeline:** Build, test, deploy automated
- [ ] **Database Migrations:** Applied successfully in all environments
- [ ] **Environment Configuration:** Dev, staging, production configs validated
- [ ] **Monitoring:** Application Insights/ELK configured with alerts
- [ ] **Rollback Plan:** Documented and tested

### Performance

- [ ] **API Response Times:** P95 <200ms for CRUD operations
- [ ] **Frontend Load Time:** Initial load <2s on 3G connection
- [ ] **Database Queries:** N+1 queries eliminated, indexes optimized
- [ ] **Bundle Size:** Angular production build <500KB (gzipped)
- [ ] **Lighthouse Score:** Performance ≥90, Best Practices ≥95

### Security

- [ ] **Authentication:** JWT tokens with secure storage (httpOnly cookies)
- [ ] **Authorization:** Role-based access control enforced
- [ ] **Input Validation:** All inputs validated (FluentValidation + Angular validators)
- [ ] **SQL Injection:** Parameterized queries only (EF Core)
- [ ] **XSS Prevention:** Content sanitization in Angular
- [ ] **HTTPS:** All traffic encrypted, HSTS enabled
- [ ] **CORS:** Configured for approved origins only
- [ ] **Secrets Management:** No secrets in code (Azure Key Vault or environment variables)

---

## 🔄 TDD Workflow Integration

### Mandatory Process for Every Feature

**Phase: RED (Failing Test)**
1. Write test that describes expected behavior
2. Run test and verify it FAILS (proves test is valid)
3. Commit test with message: `RED: [feature description]`

**Phase: GREEN (Minimal Implementation)**
1. Write simplest code to make test pass
2. Run test and verify it PASSES
3. Do NOT refactor yet
4. Commit code with message: `GREEN: [feature description]`

**Phase: REFACTOR (Clean Code)**
1. Improve code quality while keeping tests green
2. Run tests continuously during refactoring
3. Apply SOLID principles, remove duplication
4. Commit refactored code with message: `REFACTOR: [improvement description]`

### Example: Create Task Command

**RED Phase:**
```csharp
// tests/Application.Tests/Tasks/Commands/CreateTaskCommandTests.cs
[Fact]
public async Task Handle_ValidRequest_CreatesTask()
{
    // Arrange
    var command = new CreateTaskCommand { Title = "Test Task" };
    var handler = new CreateTaskCommandHandler(_mockContext.Object);
    
    // Act
    var result = await handler.Handle(command, CancellationToken.None);
    
    // Assert
    result.Should().NotBeNull();
    result.Id.Should().BeGreaterThan(0);
    result.Title.Should().Be("Test Task");
}
// RUN TEST → FAILS (CreateTaskCommand doesn't exist)
// COMMIT: "RED: Create task command should return task DTO"
```

**GREEN Phase:**
```csharp
// src/Application/Tasks/Commands/CreateTask/CreateTaskCommand.cs
public class CreateTaskCommand : IRequest<TaskDto>
{
    public string Title { get; set; }
}

public class CreateTaskCommandHandler : IRequestHandler<CreateTaskCommand, TaskDto>
{
    private readonly IApplicationDbContext _context;
    
    public CreateTaskCommandHandler(IApplicationDbContext context)
    {
        _context = context;
    }
    
    public async Task<TaskDto> Handle(CreateTaskCommand request, CancellationToken ct)
    {
        var task = new Domain.Entities.Task { Title = request.Title };
        _context.Tasks.Add(task);
        await _context.SaveChangesAsync(ct);
        return new TaskDto { Id = task.Id, Title = task.Title };
    }
}
// RUN TEST → PASSES
// COMMIT: "GREEN: Implement create task command handler"
```

**REFACTOR Phase:**
```csharp
// Add validation, AutoMapper, better error handling
public class CreateTaskCommandValidator : AbstractValidator<CreateTaskCommand>
{
    public CreateTaskCommandValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(255);
    }
}

// Update handler to use AutoMapper
public async Task<TaskDto> Handle(CreateTaskCommand request, CancellationToken ct)
{
    var entity = new Domain.Entities.Task 
    { 
        Title = request.Title,
        CreatedAt = DateTime.UtcNow 
    };
    
    _context.Tasks.Add(entity);
    await _context.SaveChangesAsync(ct);
    
    return _mapper.Map<TaskDto>(entity);
}
// RUN TESTS → ALL PASS
// COMMIT: "REFACTOR: Add validation and AutoMapper to create task"
```

---

## 📊 Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | Backend 80%+, Frontend 70%+ | CodeCov reports |
| Build Time | <3 minutes | CI/CD pipeline |
| API Response Time (P95) | <200ms | Application Insights |
| Frontend Load Time | <2s on 3G | Lighthouse |
| Deployment Frequency | Daily | GitHub releases |
| Mean Time to Recovery | <1 hour | Incident logs |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code Duplication | <3% | SonarQube |
| Cyclomatic Complexity | <10 per method | Static analysis |
| Critical Vulnerabilities | 0 | Security scans |
| Code Review Coverage | 100% of PRs | GitHub PR stats |
| TDD Adherence | 100% of features | Git commit messages |

---

## 🚀 Migration Strategy

### Data Migration from BadMonolith

**Step 1: Export Data**
```sql
-- Export existing tasks from BadMonolith database
SELECT Id, Title, IsCompleted 
INTO #TempTasks
FROM BadMonolith..Tasks;
```

**Step 2: Transform Data**
```sql
-- Add new columns with default values
ALTER TABLE #TempTasks ADD 
    Description NVARCHAR(MAX) NULL,
    Priority INT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE();
```

**Step 3: Import to Cortex-SDD**
```csharp
// Use EF Core migration to bulk insert
using var context = new ApplicationDbContext(options);
var tasks = await LoadFromTempTable();
context.Tasks.AddRange(tasks);
await context.SaveChangesAsync();
```

### Deployment Strategy

**Blue-Green Deployment:**
1. Deploy Cortex-SDD to new environment (green)
2. Run parallel testing against both environments
3. Switch traffic from BadMonolith (blue) to Cortex-SDD (green)
4. Monitor for 24 hours before decommissioning blue

**Rollback Plan:**
- Keep BadMonolith database backup for 30 days
- DNS switch to revert to old application if critical issues found
- Database restore scripts tested in staging

---

## 📚 Learning Resources

### Backend
- [Clean Architecture by Jason Taylor](https://github.com/jasontaylordev/CleanArchitecture)
- [MediatR Documentation](https://github.com/jbogard/MediatR/wiki)
- [EF Core Best Practices](https://learn.microsoft.com/en-us/ef/core/performance/)

### Frontend
- [Angular Official Documentation](https://angular.io/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Angular Testing Library](https://testing-library.com/docs/angular-testing-library/intro/)

### Testing
- [TDD with .NET Core](https://learn.microsoft.com/en-us/dotnet/core/testing/)
- [Angular Testing Best Practices](https://angular.io/guide/testing)

---

## 🎯 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Timeline overrun due to scope creep | Medium | High | Strict change control, prioritize MVP |
| Data migration failures | Low | High | Multiple dry runs, rollback plan tested |
| Performance issues at scale | Medium | Medium | Load testing in staging, database indexing |
| Third-party dependency vulnerabilities | Low | Medium | Automated security scanning, quick updates |
| Team learning curve on new stack | Medium | Low | Learning library guides, pair programming, knowledge sharing |
| TDD discipline breakdown under pressure | Low | High | Brain Protector enforcement, daily TDD metrics review |
| Documentation becomes outdated | Low | Medium | Update learning library at each phase completion, living docs |

---

## 📝 Next Steps

1. **Review & Approve Plan:** Stakeholder sign-off on architecture and 5-7 week timeline
2. **Environment Setup:** Configure dev machines with required tools (.NET 8, Node 20+, Angular CLI 18+)
3. **Create Repository:** Initialize `cortex-sample-apps\Cortex-SDD\` with CI/CD templates
4. **Learning Library Setup:** Create `docs/learning-library/` structure with README template
5. **Phase 1 Kickoff:** Begin foundation setup (Week 1 tasks)
6. **TDD Mastery Activation:** Enable TDD workflow tracking from day one
7. **Documentation Discipline:** Create learning library docs as each feature completes
8. **Daily Standups:** Track progress, TDD adherence, blockers, and adjust plan as needed
9. **Weekly Reviews:** Review TDD metrics, test coverage trends, and documentation completeness

---

**Plan Status:** ✅ READY FOR APPROVAL

**Estimated Start Date:** TBD  
**Estimated Completion Date:** TBD (5-7 weeks from start)  
**Target Location:** `cortex-sample-apps\Cortex-SDD\`

**Key Deliverables:**
- Production-ready Cortex-SDD application (backend + frontend)
- 80%+ backend, 70%+ frontend test coverage with TDD
- **30+ Learning Library Guides** (progressive documentation throughout all phases)
- TRANSFORMATION-REPORT.md (before/after comparison)
- TDD-MASTERY-REPORT.md (complete TDD workflow analysis)
- LESSONS-LEARNED.md (retrospective and recommendations)
- Learning Library Master Index with role-based learning paths

**Questions/Concerns:** Contact CORTEX Planning System for clarifications
