# AST Scanner Test Scenarios

**Purpose:** Specific test cases for validating AST scanning against RA domain  
**Created:** December 11, 2025

---

## Test Scenario 1: Basic File Parsing

**Objective:** Verify CORTEX can parse C# files without errors

**Input:**
- Target: `C:\PROJECTS\Product.Example\**\*.cs`
- Expected: 100+ C# files

**Test Steps:**
1. Enumerate all .cs files in repository
2. Parse each file into AST
3. Log success/failure for each file
4. Generate summary report

**Success Criteria:**
- ✅ All files parsed without critical errors
- ✅ AST depth > 0 for each file
- ✅ Line count matches actual LOC

**Expected Output:** `ast-outputs/parsing-summary.json`

---

## Test Scenario 2: Entity Extraction

**Objective:** Extract domain entities with properties and relationships

**Input:**
- Target: Classes in `/Domain/Entities/` or `/Models/` folders
- Expected: 10-50 entity classes

**Test Steps:**
1. Identify classes marked as entities (by folder or attributes)
2. Extract class name, namespace, base class
3. Extract all properties (name, type, attributes)
4. Map navigation properties (FK relationships)
5. Generate entity catalog

**Success Criteria:**
- ✅ All entity classes found
- ✅ Properties extracted with correct types
- ✅ Relationships mapped (1:1, 1:Many, Many:Many)

**Expected Output:** `domain-models/entities.json`

---

## Test Scenario 3: Service Dependency Analysis

**Objective:** Map service layer dependencies via constructor injection

**Input:**
- Target: Classes ending in "Service", "Manager", "Handler"
- Expected: 20-100 service classes

**Test Steps:**
1. Identify service classes by naming convention
2. Extract constructor parameters
3. Map parameter types to other services/repositories
4. Build dependency graph
5. Detect circular dependencies

**Success Criteria:**
- ✅ All services identified
- ✅ Dependencies mapped accurately
- ✅ Dependency graph generated
- ✅ Circular dependencies flagged (if any)

**Expected Output:** `analysis-results/service-dependency-graph.json`

---

## Test Scenario 4: API Endpoint Extraction

**Objective:** Document all REST API endpoints

**Input:**
- Target: Controller classes (inherit from ControllerBase or Controller)
- Expected: 5-20 controllers, 50-200 endpoints

**Test Steps:**
1. Find all controller classes
2. Extract route attributes (class and method level)
3. Extract HTTP method attributes (GET, POST, PUT, DELETE)
4. Extract request/response DTOs
5. Extract authorization attributes
6. Generate API documentation

**Success Criteria:**
- ✅ All controllers found
- ✅ Routes correctly composed (base + method)
- ✅ DTOs extracted
- ✅ Auth requirements documented

**Expected Output:** `analysis-results/api-endpoints.json`

---

## Test Scenario 5: Repository Pattern Detection

**Objective:** Identify repository pattern usage and data access

**Input:**
- Target: Classes ending in "Repository" or implementing IRepository<T>
- Expected: 10-30 repository classes

**Test Steps:**
1. Identify repository classes
2. Extract generic type parameters (entity type)
3. Map methods (CRUD operations)
4. Identify DbContext usage
5. Document custom queries

**Success Criteria:**
- ✅ All repositories found
- ✅ Entity mappings correct
- ✅ CRUD methods catalogued
- ✅ Custom queries documented

**Expected Output:** `analysis-results/repository-analysis.json`

---

## Test Scenario 6: Dependency Version Extraction

**Objective:** Extract all NuGet package dependencies

**Input:**
- Target: All .csproj files in repository
- Expected: 5-15 projects, 50-200 package references

**Test Steps:**
1. Find all .csproj files
2. Parse XML to extract PackageReference elements
3. Extract package name, version, and target project
4. Build dependency tree
5. Identify version conflicts

**Success Criteria:**
- ✅ All .csproj files parsed
- ✅ All PackageReferences extracted
- ✅ Version conflicts detected
- ✅ Dependency tree visualized

**Expected Output:** `analysis-results/dependency-tree.json`

---

## Test Scenario 7: Test Coverage Mapping

**Objective:** Map test files to production code

**Input:**
- Target: Test projects (*.Tests, *.UnitTests, *.IntegrationTests)
- Expected: 1-5 test projects, 100-500 test methods

**Test Steps:**
1. Identify test projects by naming convention
2. Extract test classes and methods
3. Map tests to production classes (by naming or imports)
4. Calculate coverage (% of classes with tests)
5. Identify untested classes

**Success Criteria:**
- ✅ All test projects found
- ✅ Test methods extracted
- ✅ Test-to-production mapping complete
- ✅ Coverage % calculated
- ✅ Gaps identified

**Expected Output:** `analysis-results/test-coverage-map.json`

---

## Test Scenario 8: Architecture Pattern Detection

**Objective:** Identify architectural patterns in use

**Input:**
- Target: Entire repository structure
- Expected: Clean Architecture, DDD, or layered architecture

**Test Steps:**
1. Analyze folder structure
2. Detect layer separation (Domain, Application, Infrastructure, Presentation)
3. Identify pattern markers (aggregates, value objects, repositories, etc.)
4. Map dependencies between layers
5. Validate dependency direction (inner → outer)
6. Calculate architecture compliance score

**Success Criteria:**
- ✅ Architecture pattern identified
- ✅ Layers correctly mapped
- ✅ Dependency violations flagged
- ✅ Compliance score > 70%

**Expected Output:** `analysis-results/architecture-pattern-report.md`

---

## Execution Checklist

- [ ] **Scenario 1:** Basic File Parsing
- [ ] **Scenario 2:** Entity Extraction
- [ ] **Scenario 3:** Service Dependency Analysis
- [ ] **Scenario 4:** API Endpoint Extraction
- [ ] **Scenario 5:** Repository Pattern Detection
- [ ] **Scenario 6:** Dependency Version Extraction
- [ ] **Scenario 7:** Test Coverage Mapping
- [ ] **Scenario 8:** Architecture Pattern Detection

---

## Validation Dashboard

| Scenario | Status | Files Generated | Issues Found |
|----------|--------|----------------|--------------|
| 1. File Parsing | ⏳ | - | - |
| 2. Entity Extraction | ⏳ | - | - |
| 3. Service Dependencies | ⏳ | - | - |
| 4. API Endpoints | ⏳ | - | - |
| 5. Repository Pattern | ⏳ | - | - |
| 6. Dependencies | ⏳ | - | - |
| 7. Test Coverage | ⏳ | - | - |
| 8. Architecture | ⏳ | - | - |

---

**Next:** Execute scenarios sequentially, updating dashboard after each completion.

