# EVERYTHING About Reimbursement Accounts Repository

**Purpose:** Comprehensive knowledge extraction roadmap  
**Created:** December 11, 2025  
**Scope:** COMPLETE repository understanding, not just Carry Over logic

---

## 🎯 What "EVERYTHING" Means

### Business Domain Knowledge
- [ ] **All Plan Types** - FSA, HSA, HRA, Dependent Care, Limited FSA, etc.
- [ ] **All Workflows** - Enrollment, Claims, Reimbursement, Carry Over, Forfeiture, Termination
- [ ] **Business Rules** - Eligibility, Contribution limits, Grace periods, Run-out periods
- [ ] **Compliance** - IRS regulations, HIPAA, state-specific rules
- [ ] **Stakeholders** - Members, Employers, Admins, Third-party administrators

### Technical Architecture
- [ ] **All Projects** - Purpose and responsibility of each .csproj
- [ ] **All Layers** - Domain, Application, Infrastructure, Presentation
- [ ] **All Patterns** - DDD, Repository, CQRS, Event Sourcing (if used)
- [ ] **All Dependencies** - NuGet packages, external services, databases
- [ ] **All Integrations** - APIs, message queues, batch jobs, webhooks

### Data Models
- [ ] **All Entities** - Domain models, aggregates, value objects
- [ ] **All Relationships** - Foreign keys, navigation properties, compositions
- [ ] **All Enums** - Status codes, plan types, claim statuses
- [ ] **All DTOs** - API contracts, view models, command objects
- [ ] **Database Schema** - Tables, indexes, constraints (inferred from code)

### Functional Areas
- [ ] **Account Management** - Creation, updates, deactivation
- [ ] **Claims Processing** - Submission, approval, denial, reimbursement
- [ ] **Balance Tracking** - Contributions, deductions, carry over, forfeiture
- [ ] **Carry Over Logic** - Year-end processing, grace periods, rollovers
- [ ] **Ledger Management** - Transaction history, reconciliation
- [ ] **Reporting** - Member statements, employer reports, compliance reports
- [ ] **Notifications** - Email, SMS, push notifications
- [ ] **Security** - Authentication, authorization, data encryption

### Code Quality
- [ ] **All Test Coverage** - Unit, integration, E2E tests
- [ ] **All Code Smells** - P0-P3 issues, technical debt
- [ ] **All Performance Bottlenecks** - N+1 queries, memory leaks
- [ ] **All Security Vulnerabilities** - SQL injection, XSS, CSRF risks

---

## 📋 Comprehensive Discovery Checklist

### Phase 1: Business Domain (Batch 2 - 90 mins)

#### Documentation Review
- [ ] Read ALL markdown files in root folder
- [ ] Extract spike document insights (`646888-spike-carryover-performance-v2.md`, etc.)
- [ ] Find README files in each project folder
- [ ] Review any wiki links or external documentation references

#### Business Glossary Extraction
- [ ] Identify all domain-specific terms
- [ ] Document acronyms (FSA, HSA, HRA, EOFY, etc.)
- [ ] Map business concepts to code entities
- [ ] Extract compliance terminology (IRS regulations, etc.)

#### Plan Types Discovery
- [ ] Find plan type enumerations
- [ ] Document each plan type's characteristics
- [ ] Map plan type to business rules
- [ ] Identify plan type specific workflows

#### Workflow Mapping
- [ ] **Enrollment Workflow** - How members enroll in accounts
- [ ] **Contribution Workflow** - How money flows into accounts
- [ ] **Claim Workflow** - Submission → Approval → Reimbursement
- [ ] **Carry Over Workflow** - Year-end processing
- [ ] **Forfeiture Workflow** - Use-it-or-lose-it rules
- [ ] **Termination Workflow** - Account closure, final disbursements

---

### Phase 2: Project Structure (Batch 1 & 3 - 75 mins)

#### Repository Metrics
- [ ] Total C# files count
- [ ] Total lines of code
- [ ] .NET version(s) used
- [ ] Solution structure (.sln analysis)

#### Project Catalog
For EACH .csproj file, document:
- [ ] Project name
- [ ] Project type (API, Jobs, Services, Library, Tests)
- [ ] Target framework
- [ ] Primary responsibility
- [ ] Key dependencies

**Projects to Analyze:**
1. `Hqy.CarryoverTransferTracking.Endpoint` - NServiceBus endpoint
2. `Hqy.ReimbursementAccounts.ApplicationServices` - Application layer
3. `Hqy.ReimbursementAccounts.CarryOver.Jobs` - Carry over batch jobs
4. `Hqy.ReimbursementAccounts.FlexPlan.Jobs` - FlexPlan batch jobs
5. `Hqy.ReimbursementAccounts.PercentPlanLedger.Jobs` - Ledger batch jobs
6. `Hqy.Employer.Domain` - Employer domain library
7. `Hqy.Member.Domain` - Member domain library
8. _(All other projects in Apps/, Libs/, Tests/ folders)_

#### Dependency Analysis
- [ ] NuGet package inventory (all packages across all projects)
- [ ] Project reference graph
- [ ] External service dependencies
- [ ] Database dependencies

---

### Phase 3: Domain Models (Batch 4 - 60 mins)

#### Entity Extraction
For ALL domain entities:
- [ ] Class name and namespace
- [ ] Properties (name, type, attributes)
- [ ] Navigation properties
- [ ] Base classes and interfaces
- [ ] XML documentation comments

**Key Entities to Find:**
- [ ] `ReimbursementAccount`
- [ ] `Claim`
- [ ] `Transaction`
- [ ] `Balance`
- [ ] `Member`
- [ ] `Employer`
- [ ] `Plan`
- [ ] `Contribution`
- [ ] `Reimbursement`
- [ ] _(All others)_

#### Relationship Mapping
- [ ] One-to-One relationships
- [ ] One-to-Many relationships
- [ ] Many-to-Many relationships
- [ ] Aggregate roots (if DDD used)
- [ ] Value objects vs entities

#### Enum Cataloging
- [ ] Plan types
- [ ] Claim statuses
- [ ] Account statuses
- [ ] Transaction types
- [ ] All other enumerations

---

### Phase 4: Application Services (Batch 7 - 60 mins)

#### Service Layer Analysis
For EACH service class:
- [ ] Service name
- [ ] Constructor dependencies (DI analysis)
- [ ] Public methods (use cases)
- [ ] Business logic patterns
- [ ] Repository usage

**Key Services to Analyze:**
- [ ] `CarryoverDollarsDomainService` (Carry Over logic)
- [ ] Claims processing services
- [ ] Balance calculation services
- [ ] Ledger services
- [ ] Account management services
- [ ] _(All others)_

#### Use Case Extraction
Group services by functional area:
- [ ] **Account Management** use cases
- [ ] **Claims Processing** use cases
- [ ] **Balance Management** use cases
- [ ] **Carry Over** use cases
- [ ] **Reporting** use cases
- [ ] **Notifications** use cases

---

### Phase 5: Data Access (Batch 9 - 45 mins)

#### Repository Pattern
- [ ] Identify repository interfaces
- [ ] Map repository implementations
- [ ] Document CRUD methods
- [ ] Find custom query methods
- [ ] Identify Entity Framework usage

#### Database Inference
Without direct database access, infer:
- [ ] Table names (from entity mappings)
- [ ] Column types (from properties)
- [ ] Indexes (from query patterns)
- [ ] Relationships (from navigation properties)
- [ ] Stored procedures (from repository methods)

---

### Phase 6: Background Jobs (Batch 5 - 45 mins)

#### Job Discovery
For EACH background job:
- [ ] Job name
- [ ] Trigger/schedule (cron, timer, event-driven)
- [ ] Job logic (what it does)
- [ ] Dependencies (services used)
- [ ] Error handling

**Key Jobs:**
- [ ] Carry Over year-end processing
- [ ] FlexPlan jobs
- [ ] PercentPlan ledger jobs
- [ ] Scheduled reports
- [ ] Data synchronization jobs
- [ ] _(All others)_

---

### Phase 7: Messaging & Integration (Batches 6 & 12 - 90 mins)

#### NServiceBus Endpoint
- [ ] All message handlers
- [ ] Message types (commands, events, queries)
- [ ] Published events
- [ ] Consumed messages
- [ ] Saga patterns (if any)

#### External Integrations
- [ ] HTTP API clients
- [ ] Third-party service calls
- [ ] Database integrations
- [ ] File system operations
- [ ] Email/SMS gateways

---

### Phase 8: Business Logic (Batch 13 - 60 mins)

#### Calculation Methods
- [ ] Balance calculations
- [ ] Carry over amount calculations
- [ ] Forfeiture calculations
- [ ] Contribution limit validations
- [ ] Eligibility determinations

#### Validation Rules
- [ ] Input validations
- [ ] Business rule validations
- [ ] Data integrity checks
- [ ] Compliance validations

#### Date/Time Logic
- [ ] Plan year calculations
- [ ] Fiscal year logic
- [ ] Grace period determinations
- [ ] Run-out period calculations
- [ ] Deadline enforcement

---

### Phase 9: Testing (Batch 10 - 45 mins)

#### Test Inventory
- [ ] Total test projects
- [ ] Total test methods
- [ ] Test frameworks used (xUnit, NUnit, MSTest)
- [ ] Mocking frameworks (Moq, NSubstitute)

#### Coverage Mapping
- [ ] % of classes with tests
- [ ] % of methods with tests
- [ ] Test-to-production ratio
- [ ] Uncovered critical paths

---

### Phase 10: Code Quality (Batch 16 - 90 mins)

#### Issue Detection
- [ ] P0 issues (null refs, race conditions, transactions)
- [ ] P1 issues (N+1 queries, performance, memory)
- [ ] P2 issues (complexity, coupling, duplication)
- [ ] P3 issues (documentation, style, minor)

#### Risk Assessment
- [ ] Highest risk files (by issue count)
- [ ] Most complex methods
- [ ] Least tested areas
- [ ] Performance bottlenecks

---

### Phase 11: AST Deep Analysis Dashboard Pages (NEW - 120 mins)

#### Performance Metrics Dashboard
- [ ] V2 batch processing architecture visualization
  - [ ] Batch size: 1,000 accounts/batch
  - [ ] Concurrency: 10 parallel workers
  - [ ] 85% performance improvement vs V1
  - [ ] Pre-fetch optimization details (eliminate N+1 queries)
- [ ] Feature flag rollout status
  - [ ] `SplitJobPerformanceV2` global flag
  - [ ] Per-employer override flags
  - [ ] Rollout coverage percentage
- [ ] Processing metrics
  - [ ] Average batch processing time
  - [ ] Throughput (accounts/minute)
  - [ ] Error rate by batch
- [ ] Data source: `carryover-service-methods.json` (lines 398-471)

#### Regulatory Compliance Dashboard
- [ ] IRS rules enforcement
  - [ ] FSA carryover limit: $640 (2025)
  - [ ] HSA carryover: 100% (unlimited)
  - [ ] HRA carryover: Employer-defined
  - [ ] Dependent Care: $0 (forfeiture only)
- [ ] Audit trail coverage
  - [ ] `BalanceChangeAudit` entity tracking
  - [ ] `CarryoverTransferTracking` entity
  - [ ] Transaction correlation IDs
  - [ ] Event publishing for compliance
- [ ] HIPAA compliance
  - [ ] Protected Health Information (PHI) handling
  - [ ] Audit requirements met
- [ ] PCI-DSS scope
  - [ ] `Card` entity (debit cards)
  - [ ] `CardTransaction` entity
  - [ ] Payment data protection
- [ ] ERISA disclosure requirements
  - [ ] Participant disclosure gaps
  - [ ] Form 5500 generation (CarryoverDollars method)
- [ ] Data sources: `carryover-service-methods.json`, `batch-3-1-entities.json`, `p0-issues-tracker.html`

#### Integration Architecture Diagram
- [ ] NServiceBus event flow
  - [ ] `BalanceChangedEvent` publishing
  - [ ] Event payload structure
  - [ ] Publisher: CarryoverDollarsDomainService
- [ ] Downstream subscribers
  - [ ] Statements generation system
  - [ ] Reporting/analytics system
  - [ ] Third-party integrations
- [ ] Message queue topology
  - [ ] Event bus architecture
  - [ ] Message routing rules
  - [ ] Retry/dead-letter policies
- [ ] Integration points
  - [ ] HTTP APIs (if any)
  - [ ] Batch job triggers
  - [ ] Database integrations
- [ ] Data source: `carryover-service-methods.json` (PublishBalanceChangedById method, lines 265-347)

#### Technical Debt ROI Calculator
- [ ] Debt item catalog (from `technical-debt-register.json`)
  - [ ] TD-001: CarryoverDollars 717 LOC ($50k/year, 40 hrs)
  - [ ] TD-002: Zero test coverage ($500k/year, 40 hrs)
  - [ ] TD-003: Claims CQRS refactor ($40k/year, 35 hrs)
  - [ ] TD-004: Missing docs ($20k/year, 16 hrs)
- [ ] ROI calculations
  - [ ] Total annual savings: $610,000
  - [ ] Total effort: 131 hours (3.3 weeks)
  - [ ] Average ROI: $4,656/hour
  - [ ] Payback period per item
- [ ] Priority matrix
  - [ ] CRITICAL (TD-001, TD-002) - $550k savings
  - [ ] HIGH (TD-003, TD-004) - $60k savings
  - [ ] Sprint allocation recommendations
- [ ] Interactive filters
  - [ ] By severity (CRITICAL → LOW)
  - [ ] By type (Complexity, Test Gap, Documentation)
  - [ ] By ROI (highest → lowest)
- [ ] Data source: `technical-debt-register.json`

#### Domain Model Visualization
- [ ] Entity relationship diagram
  - [ ] 30 entities total (revised from 56)
  - [ ] Core entities: Employer, Member, ReimbursementAccount, ReimbursementPlan
  - [ ] Compliance entities: BalanceChangeAudit, CarryoverTransferTracking
  - [ ] Transaction entities: Card, CardTransaction, ActualCoverage
- [ ] Multi-tenant hierarchy
  - [ ] Employer (tenant root)
  - [ ] Member (belongs to Employer)
  - [ ] ReimbursementAccount (belongs to Member)
  - [ ] Plans, Claims, Transactions (belong to Account)
- [ ] Business capability mapping
  - [ ] Account Management: ReimbursementAccountBalanceService
  - [ ] Claims Processing: ReimbursementAccountBalanceService
  - [ ] Year-End Processing: CarryoverDollars, CarryoverShared, RolloverSettings
  - [ ] Plan Management: PercentPlanLedgerDomainService
- [ ] Compliance entity highlighting
  - [ ] Audit trail entities (yellow)
  - [ ] PCI-DSS scope entities (red)
  - [ ] HIPAA protected entities (blue)
- [ ] Navigation properties visualization
  - [ ] One-to-Many relationships
  - [ ] Many-to-Many relationships
  - [ ] Aggregate roots (if DDD)
- [ ] Data sources: `batch-3-1-entities.json`, `business-value-scan.json`, `complete-csharp-analysis.json`

---

### Phase 12: Architecture (Batch 14 - 45 mins)

#### Pattern Detection
- [ ] Architecture style (Clean, Hexagonal, Layered)
- [ ] DDD patterns (aggregates, repositories, domain events)
- [ ] CQRS usage
- [ ] Event sourcing (if any)

#### Dependency Analysis
- [ ] Layer dependencies (valid vs violations)
- [ ] Circular dependencies
- [ ] Dependency inversion compliance
- [ ] Interface segregation

---

## 📊 Final Deliverables

### Complete Documentation Set

1. **Executive Summary** (`discovery/00-EXECUTIVE-SUMMARY.md`)
   - What the application does (business perspective)
   - Key capabilities
   - Technology stack
   - Architecture overview

2. **Business Domain Guide** (`discovery/complete-business-domain-map.md`)
   - All functional areas
   - Business workflows
   - Plan types
   - Compliance requirements

3. **Technical Architecture** (`analysis-results/complete-architecture-guide.md`)
   - All projects and their purposes
   - Layer responsibilities
   - Integration points
   - Technology choices

4. **Data Model Documentation** (`domain-models/complete-data-model.md`)
   - All entities with relationships
   - Entity relationship diagrams
   - Enum catalogs
   - DTO specifications

5. **Use Case Catalog** (`analysis-results/use-cases-by-category.md`)
   - Grouped by functional area
   - Input/output specifications
   - Business rules per use case

6. **Code Quality Report** (`findings/issue-summary-dashboard.md`)
   - P0-P3 issues
   - Risk scores
   - Remediation priorities

7. **AST Enhancement Backlog** (`findings/ast-enhancement-backlog.md`)
   - All 52+ enhancements
   - Implementation roadmap

8. **CORTEX Enhancement Plan** (`findings/cortex-enhancement-backlog.md`)
   - New orchestrators needed
   - Existing orchestrator improvements
   - Multi-language support strategy

### OneDrive Dashboard Pages (AST Deep Analysis)

9. **Performance Metrics Dashboard** (`toolkit/templates/onedrive/managers/performance-metrics.html`)
   - V2 batch processing: 1,000 accounts/batch, 10 workers, 85% improvement
   - Feature flag rollout: `SplitJobPerformanceV2` global + per-employer
   - Processing metrics: throughput, error rates, batch timing
   - Data source: `carryover-service-methods.json`

10. **Regulatory Compliance Dashboard** (`toolkit/templates/onedrive/regulatory/compliance-overview.html`)
    - IRS rules: FSA $640, HSA 100%, HRA custom, Dependent Care $0
    - Audit trail: BalanceChangeAudit, CarryoverTransferTracking entities
    - HIPAA/PCI-DSS/ERISA compliance status
    - Data sources: `carryover-service-methods.json`, `batch-3-1-entities.json`, P0 tracker

11. **Integration Architecture Diagram** (`toolkit/templates/onedrive/developers/integration-architecture.html`)
    - NServiceBus event flow: BalanceChangedEvent publishing
    - Downstream subscribers: statements, reporting, analytics
    - Message queue topology and routing
    - Data source: `carryover-service-methods.json` (PublishBalanceChangedById)

12. **Technical Debt ROI Calculator** (`toolkit/templates/onedrive/managers/technical-debt-roi.html`)
    - $610k total annual savings, 131 hours effort
    - TD-002: $500k savings (zero test coverage) - 40 hrs
    - TD-001: $50k savings (717 LOC complexity) - 40 hrs
    - Interactive priority matrix by severity/type/ROI
    - Data source: `technical-debt-register.json`

13. **Domain Model Visualization** (`toolkit/templates/onedrive/developers/domain-model.html`)
    - 30 entities with relationship diagram
    - Multi-tenant hierarchy: Employer → Member → Account
    - 4 business capabilities mapped to services
    - Compliance entities highlighted (audit, PCI-DSS, HIPAA)
    - Data sources: `batch-3-1-entities.json`, `business-value-scan.json`

---

## 🚀 Execution Strategy

### Automated Analysis First
```bash
# Run comprehensive Python AST analysis
python cortex-brain/admin/RA-Domain/scripts/analyze_ra_domain.py

# Expected output:
# - complete-csharp-analysis.json (all classes, methods, properties)
# - business-terms.json (domain vocabulary)
# - analysis-summary.txt (metrics)
```

### Then Execute Batches 1-17
Follow `test-plan-v2-batched.md` for systematic analysis

### Knowledge Synthesis
After all batches, compile everything into final deliverables

---

## 📈 Success Metrics

- [ ] **100% Project Coverage** - Every .csproj analyzed
- [ ] **100% Functional Area Coverage** - All business workflows documented
- [ ] **Entity Catalog Complete** - All domain models extracted
- [ ] **Use Case Catalog Complete** - All capabilities documented
- [ ] **Code Quality Baseline** - All P0-P3 issues identified
- [ ] **AST Enhancement Backlog** - Complete roadmap for CORTEX improvements

---

**Status:** 🟢 READY FOR COMPREHENSIVE ANALYSIS

**Next:** Run `python scripts/analyze_ra_domain.py` to kickstart automated extraction

