# AST Scanner Validation Plan: Reimbursement Accounts Domain

**Version:** 1.0  
**Created:** December 11, 2025  
**Author:** Asif Hussain

---

## 🎯 Plan Overview

**Goal:** Validate CORTEX's AST scanning capabilities by reverse engineering the Reimbursement Accounts codebase.

**Success Criteria:**
- ✅ Successfully parse all .cs files without errors
- ✅ Extract complete domain model (entities, value objects, aggregates)
- ✅ Map all service dependencies and relationships
- ✅ Generate architecture diagram from code analysis
- ✅ Identify all external dependencies and versions
- ✅ Calculate test coverage metrics

---

## 📋 Phase 1: Environment Setup & Reconnaissance

### 1.1 Verify Target Repository Access
**Objective:** Ensure CORTEX can read target codebase

**Tasks:**
- [ ] Verify path exists: `C:\PROJECTS\Product.ReimbursementAccounts`
- [ ] List repository structure (folders, file counts)
- [ ] Identify solution files (.sln) and project files (.csproj)
- [ ] Detect .NET version and framework dependencies

**Validation:**
- Repository accessible
- File listing generated
- Framework version identified

**Output Location:** `analysis-results/01-repository-structure.md`

---

### 1.2 AST Scanner Capability Assessment
**Objective:** Determine current AST scanning capabilities for C#

**Tasks:**
- [ ] Review existing AST scanners in CORTEX
- [ ] Check for C#/.NET parser support
- [ ] Identify gaps (if Python-only AST exists)
- [ ] Research C# AST libraries (Roslyn, NRefactory, etc.)

**Validation:**
- AST capabilities documented
- Gap analysis complete
- Remediation plan (if needed)

**Output Location:** `analysis-results/02-ast-capability-assessment.md`

---

## 📋 Phase 2: AST Scanning Execution

### 2.1 Basic Code Parsing
**Objective:** Parse all C# files and validate syntax

**Tasks:**
- [ ] Scan all `.cs` files in repository
- [ ] Parse each file into AST representation
- [ ] Log any parsing errors or warnings
- [ ] Generate file inventory (LOC, class count, etc.)

**Validation:**
- 100% of files parsed successfully
- No critical parsing errors
- Inventory report generated

**Output Location:** `ast-outputs/file-inventory.json`

---

### 2.2 Domain Model Extraction
**Objective:** Extract all domain entities and relationships

**Tasks:**
- [ ] Identify domain entities (classes in Domain/ or Models/ folders)
- [ ] Extract properties, methods, and relationships
- [ ] Map inheritance hierarchies
- [ ] Identify value objects vs. entities
- [ ] Detect aggregate roots (if DDD pattern used)

**Validation:**
- All domain classes catalogued
- Relationships mapped (1:1, 1:Many, Many:Many)
- Entity vs. Value Object classification

**Output Location:** `domain-models/entity-relationship-diagram.md`

---

### 2.3 Service Layer Analysis
**Objective:** Map service dependencies and patterns

**Tasks:**
- [ ] Identify all service classes (suffix: Service, Manager, Handler)
- [ ] Extract constructor dependencies (DI analysis)
- [ ] Map service → repository relationships
- [ ] Identify business logic patterns
- [ ] Detect CQRS/MediatR usage (if present)

**Validation:**
- Service dependency graph created
- Business logic patterns documented
- DI container configuration understood

**Output Location:** `analysis-results/03-service-layer-analysis.md`

---

### 2.4 Data Access Pattern Analysis
**Objective:** Understand data persistence strategy

**Tasks:**
- [ ] Identify repository pattern usage
- [ ] Map Entity Framework/Dapper usage
- [ ] Extract DbContext configurations
- [ ] Analyze database migration files
- [ ] Document data access patterns

**Validation:**
- Data access pattern identified
- ORM/Database technology confirmed
- Schema understanding documented

**Output Location:** `analysis-results/04-data-access-patterns.md`

---

### 2.5 API Contract Extraction
**Objective:** Document all API endpoints and contracts

**Tasks:**
- [ ] Identify controllers (WebAPI or MVC)
- [ ] Extract all endpoint routes and HTTP methods
- [ ] Map request/response DTOs
- [ ] Document authentication/authorization attributes
- [ ] Generate OpenAPI/Swagger-like documentation

**Validation:**
- All endpoints catalogued
- DTO schemas extracted
- Auth requirements documented

**Output Location:** `analysis-results/05-api-contracts.md`

---

## 📋 Phase 3: Dependency & Architecture Analysis

### 3.1 Dependency Mapping
**Objective:** Extract all external dependencies

**Tasks:**
- [ ] Parse all `.csproj` files
- [ ] Extract NuGet package references and versions
- [ ] Identify framework dependencies
- [ ] Map transitive dependencies
- [ ] Check for known vulnerabilities (optional)

**Validation:**
- Complete dependency tree
- Version information accurate
- Dependency graph visualized

**Output Location:** `analysis-results/06-dependency-graph.md`

---

### 3.2 Architecture Pattern Detection
**Objective:** Identify architectural patterns in use

**Tasks:**
- [ ] Detect layering (Presentation, Application, Domain, Infrastructure)
- [ ] Identify patterns (DDD, Clean Architecture, Onion, Hexagonal)
- [ ] Map cross-cutting concerns (logging, validation, caching)
- [ ] Analyze folder structure alignment with architecture
- [ ] Document deviations from standard patterns

**Validation:**
- Architecture pattern identified
- Layer boundaries documented
- Pattern adherence score calculated

**Output Location:** `analysis-results/07-architecture-analysis.md`

---

### 3.3 Test Coverage Analysis
**Objective:** Analyze existing test coverage

**Tasks:**
- [ ] Identify test projects (*.Tests, *.UnitTests, etc.)
- [ ] Map tests to production code
- [ ] Calculate coverage metrics (if test results available)
- [ ] Identify untested classes/methods
- [ ] Analyze test quality (mocking, assertions, etc.)

**Validation:**
- Test coverage % calculated
- Gaps identified
- Test quality report generated

**Output Location:** `analysis-results/08-test-coverage-analysis.md`

---

## 📋 Phase 4: Synthesis & Reporting

### 4.1 Generate Comprehensive Domain Report
**Objective:** Synthesize all findings into master report

**Tasks:**
- [ ] Compile all analysis outputs
- [ ] Generate executive summary
- [ ] Create visual diagrams (entity relationships, dependencies)
- [ ] Document key insights and patterns
- [ ] Provide recommendations for improvement

**Validation:**
- Master report complete
- All analyses integrated
- Actionable insights provided

**Output Location:** `analysis-results/00-MASTER-DOMAIN-ANALYSIS.md`

---

### 4.2 CORTEX Capability Validation
**Objective:** Document what CORTEX can/cannot do

**Tasks:**
- [ ] Document successful AST operations
- [ ] Identify limitations encountered
- [ ] Propose enhancements for CORTEX
- [ ] Update CORTEX documentation with findings

**Validation:**
- Capability matrix complete
- Enhancement backlog created
- Documentation updated

**Output Location:** `findings/cortex-capability-report.md`

---

## 🚀 Execution Commands

### Manual Execution Steps

```powershell
# Step 1: Verify repository access
cd C:\PROJECTS\Product.ReimbursementAccounts
Get-ChildItem -Recurse -Filter *.cs | Measure-Object

# Step 2: Execute CORTEX AST scanning (command TBD based on capability)
# Example: python -m src.orchestrators.ast_scanner --target "C:\PROJECTS\Product.ReimbursementAccounts"

# Step 3: Review outputs in RA-Domain/analysis-results/
```

### Expected CORTEX Integration

```bash
# Future ideal command
cortex scan-domain --path "C:\PROJECTS\Product.ReimbursementAccounts" --output "cortex-brain/admin/RA-Domain"
```

---

## 📊 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Files Parsed Successfully | 100% | ⏳ Pending |
| Domain Entities Extracted | All | ⏳ Pending |
| Service Dependencies Mapped | All | ⏳ Pending |
| API Endpoints Documented | All | ⏳ Pending |
| Test Coverage Calculated | Yes | ⏳ Pending |
| Architecture Pattern Identified | Yes | ⏳ Pending |

---

## 🔍 Next Steps After Completion

1. **Apply Learnings:** Use findings to enhance CORTEX AST capabilities
2. **Template Creation:** Build domain analysis templates for future repos
3. **Automation:** Create automated AST scanning workflows
4. **Documentation:** Update CORTEX guides with .NET analysis examples
5. **Extension:** Apply same process to other domains/repositories

---

## 📚 References

- **CORTEX AST Documentation:** `src/orchestrators/code_analyzer/README.md` (if exists)
- **Roslyn API:** https://docs.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/
- **Domain-Driven Design:** Eric Evans, "Domain-Driven Design" (2003)

---

**Status:** 🟡 READY FOR EXECUTION  
**Estimated Duration:** 4-8 hours (depending on AST capabilities)  
**Risk Level:** LOW (read-only analysis)

---

**Author:** Asif Hussain | **CORTEX Admin Operations**
