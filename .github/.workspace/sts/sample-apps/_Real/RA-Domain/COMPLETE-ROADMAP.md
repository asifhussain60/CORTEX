# EVERYTHING About Payment Accounts Repository

**Purpose:** Comprehensive knowledge extraction roadmap  
**Created:** December 11, 2025  
**Scope:** COMPLETE repository understanding, not just Rollover logic

---

## 🎯 What "EVERYTHING" Means

### Business Domain Knowledge
- [ ] **All Plan Types** - FlexAccount, HealthSavings, HealthReimbursement, DependentCare, Limited FlexAccount, etc.
- [ ] **All Workflows** - Registration, Requests, Payment, Rollover, Expiration, Termination
- [ ] **Business Rules** - Eligibility, Contribution limits, Grace periods, Run-out periods
- [ ] **Compliance** - RegulatoryAgency regulations, PrivacyRegulation, state-specific rules
- [ ] **Stakeholders** - Customers, Organizations, Admins, Third-party administrators

### Technical Architecture
- [ ] **All Projects** - Purpose and responsibility of each .csproj
- [ ] **All Layers** - Domain, Application, Infrastructure, Presentation
- [ ] **All Patterns** - DDD, Repository, CQRS, Event Sourcing (if used)
- [ ] **All Dependencies** - NuGet packages, external services, databases
- [ ] **All Integrations** - APIs, message queues, batch jobs, webhooks

### Data Models
- [ ] **All Entities** - Domain models, aggregates, value objects
- [ ] **All Relationships** - Foreign keys, navigation properties, compositions
- [ ] **All Enums** - Status codes, plan types, request statuses
- [ ] **All DTOs** - API contracts, view models, command objects
- [ ] **Database Schema** - Tables, indexes, constraints (inferred from code)

### Functional Areas
- [ ] **Account Management** - Creation, updates, deactivation
- [ ] **Request Processing** - Submission, approval, denial, payment
- [ ] **Balance Tracking** - Contributions, deductions, rollover, expiration
- [ ] **Rollover Logic** - Year-end processing, grace periods, rollovers
- [ ] **Ledger Management** - Transaction history, reconciliation
- [ ] **Reporting** - Customer statements, organization reports, compliance reports
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
- [ ] Extract spike document insights (`646888-spike-rollover-performance-v2.md`, etc.)
- [ ] Find README files in each project folder
- [ ] Review any wiki links or external documentation references

#### Business Glossary Extraction
- [ ] Identify all domain-specific terms
- [ ] Document acronyms (FlexAccount, HealthSavings, HealthReimbursement, EOY, etc.)
- [ ] Map business concepts to code entities
- [ ] Extract compliance terminology (RegulatoryAgency regulations, etc.)

#### Plan Types Discovery
- [ ] Find plan type enumerations
- [ ] Document each plan type's characteristics
- [ ] Map plan type to business rules
- [ ] Identify plan type specific workflows

#### Workflow Mapping
- [ ] **Registration Workflow** - How members enroll in accounts
- [ ] **Contribution Workflow** - How money flows into accounts
- [ ] **Request Workflow** - Submission → Approval → Payment
- [ ] **Rollover Workflow** - Year-end processing
- [ ] **Expiration Workflow** - Use-it-or-lose-it rules
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
1. `App.RolloverTransferTracking.Endpoint` - NServiceBus endpoint
2. `App.PaymentAccounts.ApplicationServices` - Application layer
3. `App.PaymentAccounts.Rollover.Jobs` - Carry over batch jobs
4. `App.PaymentAccounts.FlexPlan.Jobs` - FlexPlan batch jobs
5. `App.PaymentAccounts.PercentPlanLedger.Jobs` - Ledger batch jobs
6. `App.Organization.Domain` - Organization domain library
7. `App.Customer.Domain` - Customer domain library
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
- [ ] `PaymentAccount`
- [ ] `Request`
- [ ] `Transaction`
- [ ] `Balance`
- [ ] `Customer`
- [ ] `Organization`
- [ ] `Plan`
- [ ] `Contribution`
- [ ] `Payment`
- [ ] _(All others)_

#### Relationship Mapping
- [ ] One-to-One relationships
- [ ] One-to-Many relationships
- [ ] Many-to-Many relationships
- [ ] Aggregate roots (if DDD used)
- [ ] Value objects vs entities

#### Enum Cataloging
- [ ] Plan types
- [ ] Request statuses
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
- [ ] `CarryoverDollarsDomainService` (Rollover logic)
- [ ] Requests processing services
- [ ] Balance calculation services
- [ ] Ledger services
- [ ] Account management services
- [ ] _(All others)_

#### Use Case Extraction
Group services by functional area:
- [ ] **Account Management** use cases
- [ ] **Request Processing** use cases
- [ ] **Balance Management** use cases
- [ ] **Rollover** use cases
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
- [ ] Rollover year-end processing
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
- [ ] Expiration calculations
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
  - [ ] Per-organization override flags
  - [ ] Rollout coverage percentage
- [ ] Processing metrics
  - [ ] Average batch processing time
  - [ ] Throughput (accounts/minute)
  - [ ] Error rate by batch
- [ ] Data source: `rollover-service-methods.json` (lines 398-471)

#### Regulatory Compliance Dashboard
- [ ] RegulatoryAgency rules enforcement
  - [ ] FlexAccount rollover limit: $640 (2025)
  - [ ] HealthSavings rollover: 100% (unlimited)
  - [ ] HealthReimbursement rollover: Organization-defined
  - [ ] DependentCare: $0 (expiration only)
- [ ] Audit trail coverage
  - [ ] `BalanceChangeAudit` entity tracking
  - [ ] `RolloverTransferTracking` entity
  - [ ] Transaction correlation IDs
  - [ ] Event publishing for compliance
- [ ] PrivacyRegulation compliance
  - [ ] Protected Health Information (PHI) handling
  - [ ] Audit requirements met
- [ ] PaymentSecurity scope
  - [ ] `Card` entity (debit cards)
  - [ ] `CardTransaction` entity
  - [ ] Payment data protection
- [ ] BenefitsRegulation disclosure requirements
  - [ ] Participant disclosure gaps
  - [ ] Form 5500 generation (CarryoverDollars method)
- [ ] Data sources: `rollover-service-methods.json`, `batch-3-1-entities.json`, `p0-issues-tracker.html`

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
- [ ] Data source: `rollover-service-methods.json` (PublishBalanceChangedById method, lines 265-347)

#### Technical Debt ROI Calculator
- [ ] Debt item catalog (from `technical-debt-register.json`)
  - [ ] TD-001: CarryoverDollars 717 LOC ($50k/year, 40 hrs)
  - [ ] TD-002: Zero test coverage ($500k/year, 40 hrs)
  - [ ] TD-003: Requests CQRS refactor ($40k/year, 35 hrs)
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
  - [ ] Core entities: Organization, Customer, PaymentAccount, PaymentPlan
  - [ ] Compliance entities: BalanceChangeAudit, RolloverTransferTracking
  - [ ] Transaction entities: Card, CardTransaction, ActualCoverage
- [ ] Multi-tenant hierarchy
  - [ ] Organization (tenant root)
  - [ ] Customer (belongs to Organization)
  - [ ] PaymentAccount (belongs to Customer)
  - [ ] Plans, Requests, Transactions (belong to Account)
- [ ] Business capability mapping
  - [ ] Account Management: PaymentAccountBalanceService
  - [ ] Request Processing: PaymentAccountBalanceService
  - [ ] Year-End Processing: CarryoverDollars, CarryoverShared, RolloverSettings
  - [ ] Plan Management: PercentPlanLedgerDomainService
- [ ] Compliance entity highlighting
  - [ ] Audit trail entities (yellow)
  - [ ] PaymentSecurity scope entities (red)
  - [ ] PrivacyRegulation protected entities (blue)
- [ ] Navigation properties visualization
  - [ ] One-to-Many relationships
  - [ ] Many-to-Many relationships
  - [ ] Aggregate roots (if DDD)
- [ ] Data sources: `batch-3-1-entities.json`, `business-value-scan.json`, `complete-csharp-analysis.json`

#### Executive Narrative Generation (NEW)
- [x] **AST-to-Narrative Synthesis** - Transform JSON data + code comments into business-focused textual narrative ✅
- [x] Target document: `documents/executive-narrative-what-this-application-does.md` ✅
- [x] **Orchestrator Built** - `src/orchestrators/ast_narrative_orchestrator.py` (600 lines, 5-phase workflow) ✅
- [x] **Operation Registered** - `generate_narrative_from_ast` in cortex-operations.yaml ✅
- [x] **Initial Narrative Complete** - 3,847-word executive narrative generated ✅
- [x] **Dashboard Integration** - Index.html enhanced with collapsible narrative section ✅

#### Comment Extraction Enhancement (NEW - Phase 11b)
- [ ] **Build Comment Extractor** - `scripts/comment_extractor.py` (Option A implementation)
  - [ ] **C# Comment Parser** - Extract all comment types from 256 files
    - [ ] XML documentation comments (`/// <summary>`, `<param>`, `<returns>`)
    - [ ] Single-line comments (`// comment`)
    - [ ] Multi-line comments (`/* comment */`)
    - [ ] Preprocessor regions (`#region`, `#endregion`)
    - [ ] TODO/FIXME/HACK markers (technical debt indicators)
  - [ ] **Comment Classification** - Categorize by business relevance
    - [ ] **Critical:** Regulatory references (RegulatoryAgency Pub 969, PrivacyRegulation §164.312, PaymentSecurity)
    - [ ] **High:** Business rule explanations (eligibility, contribution limits)
    - [ ] **Medium:** Workflow descriptions (request processing steps)
    - [ ] **Low:** Technical notes (implementation details)
    - [ ] **Skip:** Auto-generated (copyright headers, tool output)
  - [ ] **Context Mapping** - Link comments to AST entities
    - [ ] Extract file path, line number, containing class/method
    - [ ] Associate with AST entities from existing JSON files
    - [ ] Identify comment-to-entity relationships (class docs, method docs, inline)
  - [ ] **Output Generation** - Create `analysis-results/comment-extraction.json`
    - [ ] Schema: `{file_path, comments: [{type, line_number, content, context, business_relevance}]}`
    - [ ] Estimated 500-1,000 comments from 256 files
    - [ ] Deduplicate boilerplate comments
    - [ ] Flag regulatory keywords for compliance section
  - [ ] **Quality Filters** - Maximize signal-to-noise ratio
    - [ ] Minimum comment length (>10 chars, skip `// TODO`)
    - [ ] Regulatory keyword detection (RegulatoryAgency, PrivacyRegulation, PCI, BenefitsRegulation, ACA)
    - [ ] Business term matching (grace period, expiration, rollover, run-out)
    - [ ] Technical debt markers (TODO count, FIXME count, HACK count)

- [ ] **Integrate Comments into Narrative Orchestrator**
  - [ ] Add Phase 1b: `aggregate_comment_data()` method
  - [ ] Update synthesis prompts to include comment insights
  - [ ] New template section: "Developer Insights" (business rules from comments)
  - [ ] Link comments to narrative sections:
    - [ ] Section 5 (Compliance): Use regulatory comments
    - [ ] Section 4 (Workflows): Use process explanation comments
    - [ ] Section 3 (Capabilities): Use feature description comments
    - [ ] Section 6 (Architecture): Use design decision comments

- [ ] **Regenerate Enhanced Narrative**
  - [ ] Run orchestrator with AST + Comment data
  - [ ] Target: 4,500-5,000 words (enhanced from 3,847)
  - [ ] Compare before/after quality:
    - [ ] Count regulatory citations (expect 2x increase)
    - [ ] Count business rule explanations (expect 3x increase)
    - [ ] Measure non-technical language percentage (target >95%)
  - [ ] Update index.html with enhanced narrative
  - [ ] Deploy to OneDrive for stakeholder review

- [ ] **Comment Extraction Deliverables**
  - [ ] `scripts/comment_extractor.py` (300 lines, production-ready)
  - [ ] `analysis-results/comment-extraction.json` (500-1,000 comments)
  - [ ] `analysis-results/comment-statistics.json` (metrics: total, by type, regulatory count)
  - [ ] Updated `documents/executive-narrative-what-this-application-does.md` (4,500+ words)
  - [ ] Dashboard page: `toolkit/templates/onedrive/developers/developer-insights.html`
    - [ ] Top regulatory comments (RegulatoryAgency/PrivacyRegulation citations)
    - [ ] Business rule comments by entity
    - [ ] Technical debt markers (TODO/FIXME visualization)
    - [ ] Comment coverage metrics (files with docs vs. undocumented)

#### Original Tooling Options (Archived)
- [x] **Option 1:** Manual Copilot synthesis ✅ PROVEN SUCCESSFUL
- [x] **Option 2:** Semi-automated orchestrator ✅ IMPLEMENTED
- [ ] **Option 3:** Open-source alternative (Continue.dev) - Deferred

#### Narrative Structure (Implemented)
- [x] **Section 1:** What the application is (healthcare benefits platform) ✅
- [x] **Section 2:** Who uses it (employers, members, admins) ✅
- [x] **Section 3:** Key capabilities (14 functional areas) ✅
- [x] **Section 4:** Core workflows (registration, claims, rollover, etc.) ✅
- [x] **Section 5:** Regulatory compliance (RegulatoryAgency, PrivacyRegulation, PaymentSecurity, BenefitsRegulation) ✅
- [x] **Section 6:** Technical architecture (at business level) ✅
- [x] **Section 7:** Integration ecosystem (NServiceBus, APIs, batch jobs) ✅

#### Enhanced Narrative Structure (With Comments)
- [ ] **Section 8:** Developer Insights (NEW - from comment extraction)
  - [ ] Regulatory compliance context (RegulatoryAgency/PrivacyRegulation citations from code comments)
  - [ ] Business rule rationale (why rules exist, not just what they are)
  - [ ] Known limitations (TODO/FIXME analysis with business impact)
  - [ ] Design decisions (architectural choices explained by original developers)

#### Data Sources (Current)
- [x] All 14 JSON files from `analysis-results/` ✅
- [x] Existing markdown: `BUSINESS-USE-CASES.md`, `EXECUTIVE-SUMMARY-BATCHES-1-7.md` ✅
- [x] AST method signatures for workflow inference ✅
- [x] Entity relationships for data model explanation ✅

#### Enhanced Data Sources (With Comments)
- [ ] `comment-extraction.json` - 500-1,000 developer comments with context
- [ ] `comment-statistics.json` - Comment coverage and quality metrics
- [ ] Regulatory keyword index - RegulatoryAgency/PrivacyRegulation/PaymentSecurity references mapped to files
- [ ] Business term glossary - Extracted from comments (grace period, expiration, etc.)

#### Success Criteria (Achieved)
- [x] Non-technical language (business stakeholder friendly) ✅ 100%
- [x] Explains "what" and "why", not "how" ✅
- [x] Includes real metrics from AST analysis ✅ (256 files, 30 entities, 1,113 methods)
- [x] References regulatory requirements with business impact ✅ (RegulatoryAgency Pub 969, PrivacyRegulation §164.312)

#### Enhanced Success Criteria (With Comments)
- [ ] Developer tribal knowledge preserved (comments capture "why" decisions were made)
- [ ] Regulatory citations doubled (expect 20+ RegulatoryAgency/PrivacyRegulation references from comments)
- [ ] Business rule explanations tripled (expect 40+ rule contexts from comments)
- [ ] Technical debt quantified (TODO/FIXME count mapped to business risk)
- [ ] Comment coverage baseline (% files with meaningful documentation)

---

### Phase 12: Architecture (Batch 14 - 45 mins)
  - [ ] Compliance entities: BalanceChangeAudit, RolloverTransferTracking
  - [ ] Transaction entities: Card, CardTransaction, ActualCoverage
- [ ] Multi-tenant hierarchy
  - [ ] Organization (tenant root)
  - [ ] Customer (belongs to Organization)
  - [ ] PaymentAccount (belongs to Customer)
  - [ ] Plans, Requests, Transactions (belong to Account)
- [ ] Business capability mapping
  - [ ] Account Management: PaymentAccountBalanceService
  - [ ] Request Processing: PaymentAccountBalanceService
  - [ ] Year-End Processing: CarryoverDollars, CarryoverShared, RolloverSettings
  - [ ] Plan Management: PercentPlanLedgerDomainService
- [ ] Compliance entity highlighting
  - [ ] Audit trail entities (yellow)
  - [ ] PaymentSecurity scope entities (red)
  - [ ] PrivacyRegulation protected entities (blue)
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
   - Feature flag rollout: `SplitJobPerformanceV2` global + per-organization
   - Processing metrics: throughput, error rates, batch timing
   - Data source: `rollover-service-methods.json`

10. **Regulatory Compliance Dashboard** (`toolkit/templates/onedrive/regulatory/compliance-overview.html`)
    - RegulatoryAgency rules: FlexAccount $640, HealthSavings 100%, HealthReimbursement custom, DependentCare $0
    - Audit trail: BalanceChangeAudit, RolloverTransferTracking entities
    - PrivacyRegulation/PaymentSecurity/BenefitsRegulation compliance status
    - Data sources: `rollover-service-methods.json`, `batch-3-1-entities.json`, P0 tracker

11. **Integration Architecture Diagram** (`toolkit/templates/onedrive/developers/integration-architecture.html`)
    - NServiceBus event flow: BalanceChangedEvent publishing
    - Downstream subscribers: statements, reporting, analytics
    - Message queue topology and routing
    - Data source: `rollover-service-methods.json` (PublishBalanceChangedById)

12. **Technical Debt ROI Calculator** (`toolkit/templates/onedrive/managers/technical-debt-roi.html`)
    - $610k total annual savings, 131 hours effort
    - TD-002: $500k savings (zero test coverage) - 40 hrs
    - TD-001: $50k savings (717 LOC complexity) - 40 hrs
    - Interactive priority matrix by severity/type/ROI
    - Data source: `technical-debt-register.json`

13. **Domain Model Visualization** (`toolkit/templates/onedrive/developers/domain-model.html`)
    - 30 entities with relationship diagram
    - Multi-tenant hierarchy: Organization → Customer → Account
    - 4 business capabilities mapped to services
    - Compliance entities highlighted (audit, PaymentSecurity, PrivacyRegulation)
    - Data sources: `batch-3-1-entities.json`, `business-value-scan.json`

14. **Executive Narrative: What This Application Does** (`documents/executive-narrative-what-this-application-does.md`)
    - ✅ **Status:** Initial version complete (3,847 words)
    - Business-focused textual narrative (non-technical)
    - Synthesized from AST data + domain knowledge + use cases
    - Target audience: Leadership, product managers, business stakeholders
    - Explains: Business purpose, key capabilities, user workflows, compliance scope
    - Generated via: AST-to-Narrative orchestrator (Copilot synthesis)
    - Data sources: All JSON files + existing markdown deliverables
    - **Enhancement Planned:** Comment extraction to add developer insights (4,500+ words target)

15. **Developer Insights Dashboard** (`toolkit/templates/onedrive/developers/developer-insights.html`) - NEW
    - Top regulatory comments (RegulatoryAgency/PrivacyRegulation citations from code)
    - Business rule comments by entity (eligibility, contribution limits)
    - Technical debt markers (TODO/FIXME/HACK visualization with priority)
    - Comment coverage metrics (documented vs. undocumented files)
    - Regulatory keyword index (RegulatoryAgency Pub 969, PrivacyRegulation §164.312 references mapped)
    - Data source: `comment-extraction.json` (500-1,000 developer comments)

---

## 🚀 Execution Strategy

### Automated Analysis First
```bash
# Run comprehensive Python AST analysis
python cortex_brain/admin/RA-Domain/scripts/analyze_ra_domain.py

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

