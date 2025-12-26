# Legacy API Specification Generation & Migration Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Status:** 🎯 PLANNING  

---

## 🎯 Executive Summary

**Problem Statement:**  
Legacy APIs lack documented requirements, making it impossible for PMs/BAs to validate modernized implementations. Direct code-to-code conversions miss opportunities to correct architectural issues (domain boundary violations, framework underutilization, entity exposure).

**Solution:**  
Implement a **3-phase specification-first migration** workflow that generates human-readable business logic specifications from legacy code, enables non-technical validation, then uses validated specs as source-of-truth for modernization.

**Success Criteria:**
- ✅ Non-technical stakeholders can validate business logic
- ✅ Specifications capture all business rules, data flows, and constraints
- ✅ Generated artifacts serve as agent long-term memory
- ✅ Modernized code adheres to RA domain standards (DomainFramework, ClassicModernization)
- ✅ Zero domain boundary violations
- ✅ Leverages OOB .NET capabilities instead of reimplementing

---

## 🏗️ Three-Phase Workflow

### Phase 1: Legacy Code Reverse Engineering → Business Specification

**Input:** Legacy WCF/SOAP API source code  
**Output:** Human-readable business specification (markdown + diagrams)  
**Duration:** 2-3 days per API group (5-10 endpoints)

#### 1.1 Static Code Analysis

**CORTEX Agent Tasks:**
- Parse legacy code (XAdd*, XUpdate*, XClose* transaction classes)
- Extract business rules, validation logic, conditional flows
- Map data dependencies and external service calls
- Identify database operations (CRUD patterns)
- Document state transitions and status workflows

**Deliverables:**
```markdown
## Business Logic Specification: [API Name]

### Operation: XAddFundingInvoice
**Business Purpose:** Create a funding invoice for RA account replenishment

#### Preconditions
- Employer must exist and be active
- Subaccount must exist and allow funding
- Funding frequency must be configured

#### Business Rules
1. **Dual-Track Funding:** System MUST calculate both employer and employee contributions
2. **LSA Detection:** IF plan is LSA, THEN invoice description = "LSA Funding", ELSE "RA Funding"
3. **Template Update:** IF UpdateTemplate flag = true, THEN update FundingTemplate entity
4. **Payroll Frequency:** IF frequency = Payroll, THEN create ScheduledDeduction
5. **Threshold Check:** IF funding amount < minimum ($10), THEN reject with error

#### Data Flow
Input → Employer Lookup → Plan Validation → Contribution Calculation → Invoice Creation → CashInOut Creation → Optional: ScheduledDeduction

#### Side Effects
- Creates CashInOut record (category: RAFunding)
- May create ScheduledDeduction (if Payroll frequency)
- May update FundingTemplate (if UpdateTemplate = true)
- Updates subaccount balance (pending)

#### Error Scenarios
- Employer not found → UserMessageException
- Subaccount inactive → ValidationException
- Amount below minimum → BusinessRuleException
```

**Tooling:**
- Roslyn syntax analysis for C# parsing
- Control flow graph generation
- Business rule extraction via pattern matching
- Mermaid diagrams for data flows

#### 1.2 Dynamic Behavior Analysis

**CORTEX Agent Tasks:**
- Identify runtime dependencies (database queries, external APIs)
- Map entity relationships and foreign key constraints
- Document transaction boundaries and rollback scenarios
- Capture implicit business rules (coded assumptions)

**Deliverables:**
- Entity relationship diagrams (ERD)
- Sequence diagrams for complex workflows
- Dependency maps (services, repositories, external APIs)

#### 1.3 PM/BA Review Checkpoint

**Non-Technical Validation:**
- Business logic accuracy review (PMs validate rules)
- Completeness check (BAs validate all scenarios covered)
- Edge case identification (missing validations, error handling)
- Approval gate: Specification must be signed off before Phase 2

**Artifacts:**
- Approved specification (markdown)
- Review comments and clarifications
- Business rule prioritization (must-have vs. nice-to-have)

---

### Phase 2: Specification → Modern Implementation Design

**Input:** Approved business specification  
**Output:** Technical design document with RA domain compliance

#### 2.1 Architecture Design (RA Domain Standards)

**CORTEX Agent Tasks:**
- Map business operations to REST endpoints (RESTful design)
- Design Clean Architecture with proper project separation (5 layers)
- Apply DomainFramework patterns (entities, value objects, aggregates)
- Leverage ClassicModernization libraries (adapters, migration helpers)
- Enforce domain boundaries (RA entities only, no cross-domain exposure)

**Design Principles:**
1. **Clean Architecture Enforcement:** Follow layer dependency rules from `clean-architecture-layer-definitions.md`
2. **Project Separation:** Create separate projects per layer (compiler-enforced boundaries)
3. **Domain Isolation:** RA API MUST NOT expose Employer, Plan, or Payroll entities directly
4. **Wrapper Pattern:** External entities MUST be wrapped in RA DTOs (e.g., `RAEmployerSummary`)
5. **OOB .NET First:** Use built-in capabilities (FluentValidation, EF Core, IOptions) before custom implementations
6. **DomainFramework Alignment:** Entities inherit from `BaseEntity`, use `IAuditable`, `ISoftDeletable`
7. **ClassicModernization:** Use migration adapters for legacy database access

**Layer Structure (MANDATORY):**

**Domain Layer (`RA.DomainCore`):**
- Entities, Value Objects, Aggregates
- Repository Interfaces (IFundingInvoiceRepository)
- Domain Events, Validators, Specifications
- ❌ NO dependencies on ANY other layer

**Use Case Layer (`RA.UseCase`):**
- Use Case implementations (CreateFundingInvoiceUseCase)
- External port interfaces (IFinanceClient, IParagonApiClient)
- ✅ MAY depend on Domain layer ONLY

**Internal Infrastructure Layer (`RA.Data.SqlServer`):**
- Repository implementations
- EF Core DbContext, configurations
- ✅ MAY depend on Domain layer ONLY

**External Infrastructure Layer (`RA.Client.FinanceDomain`):**
- HTTP clients for external APIs
- Message queue adapters
- ✅ MAY depend on Use Case + Domain layers

**Presentation Layer (`RA.Api.Host`):**
- Controllers, DTOs, Middleware
- ✅ Implementation: Depends on Domain + Use Case ONLY
- ✅ Hosting/DI: References ALL layers for registration

**Deliverables:**
```markdown
## Technical Design: Funding Invoice API

### Project Structure (Clean Architecture)

**RA.DomainCore** (Domain Layer)
- Entities: FundingInvoice, FundingBatch, CashInOut
- Value Objects: Money, FundingFrequency
- Repository Interfaces: IFundingInvoiceRepository, ICashInOutRepository
- Validators: FundingInvoiceValidator (business rules)
- Dependencies: NONE

**RA.UseCase** (Use Case Layer)
- Use Cases: CreateFundingInvoiceUseCase, GenerateFundingInvoiceUseCase
- Port Interfaces: IParagonApiClient, IFinanceClient
- DTOs: CreateFundingInvoiceCommand, FundingInvoiceResult
- Dependencies: RA.DomainCore

**RA.Data.SqlServer** (Internal Infrastructure)
- Repositories: FundingInvoiceRepository, CashInOutRepository
- DbContext: RADbContext
- EF Core Configurations: FundingInvoiceConfiguration
- Dependencies: RA.DomainCore

**RA.Client.FinanceDomain** (External Infrastructure)
- Clients: FinanceClient : IFinanceClient
- DTOs: FinanceBalanceResponse
- Dependencies: RA.UseCase, RA.DomainCore (optional)

**RA.Api.Host** (Presentation Layer)
- Controllers: FundingInvoiceController (thin, auth, routing)
- Request/Response Models: CreateFundingInvoiceRequest, FundingInvoiceResponse
- Middleware: ExceptionHandlingMiddleware
- Dependencies: RA.DomainCore, RA.UseCase (code), ALL (DI setup)

### REST Endpoints
- POST /api/v1/ra/funding-invoices
- GET /api/v1/ra/funding-invoices/{id}
- PATCH /api/v1/ra/funding-invoices/{id}

### Domain Boundary Enforcement
- ❌ BAD: Return `Employer` entity directly
- ✅ GOOD: Return `RAEmployerSummary` DTO with RA-relevant fields only
- ❌ BAD: Controller → Repository directly
- ✅ GOOD: Controller → Use Case → Repository

### Framework Utilization
- **Validation:** FluentValidation (OOB, not custom)
- **Mapping:** AutoMapper or Mapster (OOB, not manual)
- **Logging:** ILogger<T> (OOB, not custom logger)
- **Configuration:** IOptions<T> (OOB, not static config)
- **Async:** async/await everywhere (OOB, no .Result or .Wait())

### Layer Dependency Validation
```csharp
// RA.DomainCore.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <!-- NO REFERENCES -->
  </ItemGroup>
</Project>

// RA.UseCase.csproj
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <ProjectReference Include="..\RA.DomainCore\RA.DomainCore.csproj" />
  </ItemGroup>
</Project>

// RA.Api.Host.csproj
<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <ProjectReference Include="..\RA.DomainCore\RA.DomainCore.csproj" />
    <ProjectReference Include="..\RA.UseCase\RA.UseCase.csproj" />
    <!-- For DI ONLY: -->
    <ProjectReference Include="..\RA.Data.SqlServer\RA.Data.SqlServer.csproj" />
    <ProjectReference Include="..\RA.Client.FinanceDomain\RA.Client.FinanceDomain.csproj" />
  </ItemGroup>
</Project>
```
```

#### 2.2 Migration Strategy

**CORTEX Agent Tasks:**
- Define phased rollout (feature flags, A/B testing)
- Identify data migration requirements (schema changes, data transformation)
- Design rollback plan (revert strategy, data consistency)
- Plan integration testing (legacy vs. modern parity)

**Deliverables:**
- Migration plan (timeline, phases, checkpoints)
- Feature flag configuration
- Rollback procedures
- Test strategy (unit, integration, E2E)

---

### Phase 3: Implementation with Continuous Validation

**Input:** Approved technical design  
**Output:** Production-ready REST API with 100% specification parity

#### 3.1 TDD-First Implementation

**CORTEX Agent Workflow:**
1. **RED Phase:** Generate failing tests from specification
   - Business rule tests (FluentValidation assertions)
   - Data flow tests (mocked dependencies)
   - Error scenario tests (exception handling)

2. **GREEN Phase:** Implement minimal code to pass tests
   - Controller actions (routing, model binding)
   - Service methods (business logic)
   - Repository methods (data access)

3. **REFACTOR Phase:** Apply RA standards
   - DomainFramework patterns
   - ClassicModernization adapters
   - Remove custom implementations (use OOB)

#### 3.2 Specification Traceability

**Requirement:** Every business rule in specification MUST map to test + implementation

**Traceability Matrix:**
| Specification Rule | Test Class | Test Method | Implementation |
|--------------------|------------|-------------|----------------|
| Dual-Track Funding | `FundingInvoiceServiceTests` | `CreateAsync_CalculatesBothEmployerAndEmployee` | `FundingInvoiceService.CreateAsync:L45-L52` |
| LSA Detection | `FundingInvoiceServiceTests` | `CreateAsync_SetsLsaDescription_WhenPlanIsLsa` | `FundingInvoiceService.CreateAsync:L58-L62` |
| Threshold Validation | `CreateFundingInvoiceValidator` | `Should_Fail_WhenAmountBelowMinimum` | `CreateFundingInvoiceValidator:L18-L20` |

**Tooling:**
- Automated traceability report generation
- Coverage analysis (specification coverage, not just code coverage)
- Gap detection (unimplemented rules, untested scenarios)

#### 3.3 PM/BA Validation Checkpoint

**Non-Technical Validation:**
- Demo API with Swagger UI (interactive testing)
- Walk through each business rule with test execution
- Compare legacy behavior side-by-side (dual-run testing)
- Final approval gate before production

---

## 📋 Artifact Catalog (Agent Long-Term Memory)

### Per-API Artifacts

**Location:** `cortex-brain/documents/api-specifications/ra-domain/[api-name]/`

1. **Business Specification** (`business-spec.md`)
   - Business rules, data flows, error scenarios
   - PM/BA approval signatures and review comments
   - Version history (changes, rationale)

2. **Technical Design** (`technical-design.md`)
   - Architecture diagrams (layering, dependencies)
   - RA domain compliance checklist
   - Framework utilization matrix

3. **Traceability Matrix** (`traceability.csv`)
   - Spec rule → Test → Implementation mapping
   - Coverage percentage per rule
   - Gap analysis report

4. **Migration Plan** (`migration-plan.md`)
   - Phased rollout timeline
   - Feature flag strategy
   - Rollback procedures

5. **Test Results** (`test-results.md`)
   - Unit test coverage (target: 80%+)
   - Integration test scenarios
   - Legacy parity validation results

6. **Review History** (`review-history.md`)
   - Code review comments
   - Architectural review findings
   - PM/BA validation notes

### Cross-API Knowledge Base

**Location:** `cortex-brain/knowledge-graph/ra-domain/`

- **Common Business Rules** (`common-rules.yaml`)
  - Reusable validation rules (funding thresholds, status transitions)
  - Cross-cutting concerns (audit logging, error handling)

- **Domain Patterns** (`domain-patterns.yaml`)
  - Standard DTO wrappers (RAEmployerSummary, RAPlanSummary)
  - Repository patterns (async CRUD, soft delete)
  - Service patterns (orchestration, transaction management)

- **Migration Lessons** (`lessons-learned.yaml`)
  - Anti-patterns to avoid (entity exposure, synchronous I/O)
  - Successful patterns (adapter pattern, feature flags)
  - Performance optimizations (caching, lazy loading)

---

## 🚀 CORTEX Agent Configuration

### Agent Prompt Template (Phase 1: Reverse Engineering)

```yaml
agent: legacy-specification-generator
version: 1.0
context:
  - cortex-brain/knowledge-graph/ra-domain/domain-patterns.yaml
  - cortex-brain/documents/api-specifications/ra-domain/[similar-api]/business-spec.md

system_prompt: |
  You are a business analyst agent specializing in reverse engineering legacy code into human-readable specifications.
  
  YOUR GOAL: Generate a complete business specification from legacy WCF code that:
  1. Can be validated by non-technical stakeholders (PMs, BAs)
  2. Captures ALL business rules, validations, and data flows
  3. Documents error scenarios and edge cases
  4. Serves as source-of-truth for modern implementation
  
  CONSTRAINTS:
  - Use plain language (avoid jargon)
  - Include concrete examples for each business rule
  - Generate diagrams for complex workflows (Mermaid syntax)
  - Cross-reference similar RA APIs for consistency
  
  OUTPUT FORMAT: Follow template in cortex-brain/templates/business-specification-template.md

input_files:
  - path: Segment4/HETransactions/XAddFundingInvoice.cs
    type: legacy_source
  - path: Segment4/HETransactions.Contracts/XAddFundingInvoice.Shared.cs
    type: legacy_contract

output:
  - path: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/business-spec.md
    type: markdown
  - path: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/data-flow.mmd
    type: mermaid_diagram
```

### Agent Prompt Template (Phase 2: Technical Design)

```yaml
agent: modern-architecture-designer
version: 1.0
context:
  - cortex-brain/documents/api-specifications/ra-domain/funding-invoice/business-spec.md (APPROVED)
  - cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md
  - cortex-brain/documents/guidelines/architecture/architecture-diagrams-and-patterns.md
  - cortex-brain/knowledge-graph/ra-domain/domain-patterns.yaml
  - Platform.Classic/.github/instructions/ra-domain-standards.md
  - DomainFramework documentation
  - ClassicModernization library reference

system_prompt: |
  You are an architect agent specializing in RA domain modernization with Clean Architecture.
  
  YOUR GOAL: Design a modern REST API implementation that:
  1. Maps 100% to approved business specification
  2. Enforces Clean Architecture with 5-layer project separation
  3. Enforces RA domain boundaries (no cross-domain entity exposure)
  4. Leverages DomainFramework and ClassicModernization libraries
  5. Uses OOB .NET capabilities (no custom reimplementations)
  6. Follows compiler-enforced dependency rules
  
  MANDATORY ARCHITECTURE RULES:
  
  **Layer Separation (Compiler-Enforced):**
  - Domain (*.DomainCore): NO dependencies, defines entities + repository interfaces
  - Use Case (*.UseCase): Depends on Domain ONLY, orchestrates business logic
  - Internal Infrastructure (*.Data.*): Depends on Domain ONLY, implements repositories
  - External Infrastructure (*.Client.*): Depends on Use Case + (optional) Domain
  - Presentation (*.Api.Host): Code depends on Domain + Use Case, DI setup references ALL
  
  **Project Reference Validation:**
  - REJECT any design where Domain references other layers
  - REJECT any design where Use Case references Infrastructure
  - REJECT any design where Internal Infrastructure references External Infrastructure
  - REQUIRE separate .csproj files for each layer
  
  **Domain Boundary Enforcement:**
  - ❌ REJECT any design that exposes Employer, Plan, Payroll entities directly
  - ❌ REJECT custom validation/logging/mapping when OOB exists
  - ✅ REQUIRE wrapper DTOs for all external entities (RAEmployerSummary, RAPlanSummary)
  - ✅ REQUIRE async/await for all I/O operations
  - ✅ REQUIRE FluentValidation for business rules
  - ✅ REQUIRE port interfaces (defined in Domain/UseCase, implemented in Infrastructure)
  
  **Pattern Selection:**
  - Simple CRUD → Controller → Use Case → Repository
  - Complex Logic → Controller → Use Case → Multiple Repositories + Domain
  - Cross-Domain → Controller → Use Case → External Client + Repository
  - Reference: architecture-diagrams-and-patterns.md for sequence diagrams
  
  OUTPUT FORMAT: Follow template in cortex-brain/templates/technical-design-template.md

input:
  - business_specification: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/business-spec.md
  - architecture_guidelines: cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md
  - pattern_reference: cortex-brain/documents/guidelines/architecture/architecture-diagrams-and-patterns.md
  - similar_implementations:
    - cortex-brain/documents/api-specifications/ra-domain/contribution/technical-design.md
    - cortex-brain/documents/api-specifications/ra-domain/distribution/technical-design.md

output:
  - technical_design: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/technical-design.md
  - project_structure: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/project-structure.txt
  - architecture_diagrams: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/architecture.mmd
  - dependency_validation: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/dependency-matrix.md
  - traceability_template: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/traceability.csv
```

### Agent Prompt Template (Phase 3: TDD Implementation)

```yaml
agent: tdd-implementation-orchestrator
version: 2.0
context:
  - cortex-brain/documents/api-specifications/ra-domain/funding-invoice/business-spec.md
  - cortex-brain/documents/api-specifications/ra-domain/funding-invoice/technical-design.md
  - cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md
  - cortex-brain/brain-protection-rules.yaml (TDD_ENFORCEMENT)

system_prompt: |
  You are a TDD implementation agent specializing in Clean Architecture enforcement.
  
  YOUR GOAL: Implement REST API with 100% traceability to business specification via RED→GREEN→REFACTOR cycle while maintaining strict layer boundaries.
  
  PHASE RED (Write Failing Tests):
  - For EACH business rule in specification, generate failing test
  - Test MUST validate exact behavior described in spec
  - Include error scenarios, edge cases, boundary conditions
  - Tests go in separate test projects per layer:
    - RA.DomainCore.Tests (domain validators, specifications)
    - RA.UseCase.Tests (use case orchestration, mocked dependencies)
    - RA.Api.Host.Tests (controller integration tests)
  
  PHASE GREEN (Minimal Implementation):
  - Implement ONLY enough code to pass tests
  - Follow Clean Architecture layer structure from technical design
  - Use DomainFramework/ClassicModernization libraries
  - ENFORCE project references (compiler validates boundaries)
  
  PHASE REFACTOR (Clean Architecture Compliance):
  - Remove any custom implementations (replace with OOB .NET)
  - Verify layer dependencies match Project Reference Matrix
  - Enforce domain boundaries (no entity exposure)
  - Add XML documentation with spec traceability comments
  - Validate with domain_boundary_checker.py
  
  LAYER IMPLEMENTATION ORDER:
  1. Domain Layer (entities, interfaces, validators) - NO dependencies
  2. Use Case Layer (orchestration) - depends on Domain only
  3. Infrastructure Layers (repositories, clients) - implement interfaces
  4. Presentation Layer (controllers) - thin, delegates to Use Case
  
  MANDATORY VALIDATION:
  - Run domain_boundary_checker.py after each layer
  - Verify project references match technical design
  - Ensure no cross-layer violations (compiler enforces)
  
  TRACEABILITY: Every test/implementation MUST reference specification section
  Example: 
  ```csharp
  // Implements: business-spec.md § 3.2 "Dual-Track Funding"
  // Project: RA.UseCase/Fees/CreateFundingInvoiceUseCase.cs
  ```
  
  OUTPUT: Generate traceability report showing spec → test → code mapping

tdd_config:
  test_framework: xUnit
  mocking: Moq
  validation: FluentValidation
  coverage_target: 80%
  
  mandatory_patterns:
    - async_await: true
    - repository_pattern: true
    - use_case_pattern: true (orchestration, not service layer)
    - dto_mapping: true
    - domain_framework: true
    - clean_architecture: true (5-layer separation)

  project_structure:
    domain: RA.DomainCore
    use_case: RA.UseCase
    internal_infrastructure: RA.Data.SqlServer
    external_infrastructure: RA.Client.FinanceDomain
    presentation: RA.Api.Host

output:
  - domain_layer: RA.DomainCore/Entities/, RA.DomainCore/Repositories/
  - use_case_layer: RA.UseCase/Fees/CreateFundingInvoiceUseCase.cs
  - infrastructure: RA.Data.SqlServer/Repositories/FundingInvoiceRepository.cs
  - presentation: RA.Api.Host/Controllers/FundingInvoiceController.cs
  - tests: RA.DomainCore.Tests/, RA.UseCase.Tests/, RA.Api.Host.Tests/
  - traceability: cortex-brain/documents/api-specifications/ra-domain/funding-invoice/traceability.csv
```

---

## 🎯 Success Metrics

### Specification Quality
- ✅ 100% PM/BA approval rate (no unvalidated specs)
- ✅ <5% clarification requests post-approval
- ✅ 100% business rule coverage (no implicit logic)

### Implementation Quality
- ✅ 100% specification-to-code traceability
- ✅ 80%+ test coverage (unit + integration)
- ✅ 0 domain boundary violations (automated checks)
- ✅ 100% OOB framework utilization (no custom reimplementations)
- ✅ 100% DomainFramework/ClassicModernization adherence

### Process Efficiency
- ✅ Specification generation: 2-3 days per API group
- ✅ Technical design: 1-2 days per API group
- ✅ Implementation: 3-5 days per API group
- ✅ Total cycle time: 6-10 days (vs. 15-20 days direct migration)

### Long-Term Value
- ✅ Reusable specifications for maintenance/enhancements
- ✅ Knowledge base for future RA APIs
- ✅ Onboarding documentation for new team members
- ✅ Compliance audit trail (business rules → code)

---

## 🔄 Continuous Improvement Loop

### Post-Migration Review

**After each API migration, capture:**
1. **Specification Gaps:** Business rules missed in reverse engineering
2. **Design Patterns:** Successful architectures to replicate
3. **Common Issues:** Anti-patterns to avoid (add to knowledge base)
4. **Tooling Enhancements:** Automation opportunities (code parsing, diagram generation)

**Update Knowledge Base:**
- Add new common rules to `common-rules.yaml`
- Document new patterns in `domain-patterns.yaml`
- Update agent prompts based on lessons learned

### Agent Refinement

**Monthly calibration:**
- Review traceability coverage (target: 100%)
- Analyze specification quality (PM/BA feedback)
- Refine prompts for better output quality
- Update templates based on stakeholder preferences

---

## 📚 Templates & Tooling

### Required Templates

**Location:** `cortex-brain/templates/ra-domain/`

1. `business-specification-template.md` - Consistent spec format
2. `technical-design-template.md` - Architecture documentation
3. `traceability-matrix-template.csv` - Spec-to-code mapping
4. `migration-plan-template.md` - Rollout planning

### Required Tooling

**CORTEX Utilities:**
- `legacy_code_parser.py` - Extract business rules from C# code
- `specification_generator.py` - Generate markdown specs from parsed rules
- `traceability_validator.py` - Verify spec-to-code mapping
- `domain_boundary_checker.py` - Detect entity exposure violations + layer dependency violations
- `project_reference_validator.py` - Validate .csproj references match Clean Architecture rules

### Integration with Existing CORTEX

**Orchestrator:** `ra_specification_migration_orchestrator.py`
- Coordinates 3-phase workflow
- Manages PM/BA approval gates
- Generates artifact catalog
- Updates knowledge base

**Commands:**
- `plan ado ra-api [legacy-file]` - Generate Phase 1 spec
- `design ra-api [spec-file]` - Generate Phase 2 design
- `implement ra-api [design-file]` - Execute Phase 3 TDD

---

## 🚀 Next Steps

### Immediate Actions (Week 1)

1. **Create Templates**
   - Business specification template
   - Technical design template
   - Traceability matrix template

2. **Configure Agents**
   - Set up legacy-specification-generator agent
   - Set up modern-architecture-designer agent
   - Configure TDD implementation orchestrator

3. **Pilot Migration**
   - Select simple API (e.g., XUpdateFundingBatch)
   - Execute 3-phase workflow end-to-end
   - Validate with PM/BA stakeholders

### Short-Term Goals (Month 1)

4. **Build Tooling**
   - Legacy code parser (Roslyn-based)
   - Specification generator
   - Domain boundary checker

5. **Knowledge Base Initialization**
   - Extract common rules from existing RA APIs
   - Document domain patterns (from ra-modernized review)
   - Create lessons-learned from funding invoice migration

6. **Process Validation**
   - Migrate 3-5 APIs using new process
   - Measure cycle time vs. direct migration
   - Gather PM/BA feedback on specification quality

### Long-Term Vision (Quarter 1)

7. **Scale Across RA Domain**
   - Migrate all funding APIs (10-15 endpoints)
   - Migrate contribution APIs
   - Migrate distribution APIs

8. **Cross-Domain Expansion**
   - Adapt process for Employer domain
   - Adapt process for Plan domain
   - Create domain-specific agent configurations

9. **Continuous Improvement**
   - Automate specification generation (80% automation target)
   - Build interactive validation UI for PM/BA review
   - Integrate with ADO (auto-create work items from specs)

---

## 📖 References

- **Existing Review:** `Platform.Classic/cortex/ra-modernized/.review/`
- **Clean Architecture Guidelines:** `cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md`
- **Architecture Patterns:** `cortex-brain/documents/guidelines/architecture/architecture-diagrams-and-patterns.md`
- **Domain Standards:** `Platform.Classic/.github/instructions/ra-domain-standards.md` (to be created)
- **DomainFramework:** [Internal documentation link]
- **ClassicModernization:** [Internal documentation link]
- **CORTEX Planning System:** `cortex-brain/manifests/orchestrators/planning-system-manifest.yaml`

---

**End of Plan**
