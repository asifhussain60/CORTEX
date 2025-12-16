# AST Enhancement Tracker

**Purpose:** Track AST scanner capability gaps discovered during RA Domain analysis  
**Status:** 🟡 ACTIVE TRACKING  
**Created:** December 11, 2025

---

## 🎯 Enhancement Categories

1. **Parser** - Syntax parsing capabilities (languages, constructs)
2. **Analyzer** - Semantic analysis (relationships, dependencies)
3. **Extractor** - Data extraction from code (metadata, documentation)
4. **Reporter** - Output generation and visualization
5. **Integration** - External tool integration

---

## 📊 Enhancement Summary

| Category | Total | HIGH | MEDIUM | LOW | Completed |
|----------|-------|------|--------|-----|-----------|
| Parser | 0 | 0 | 0 | 0 | 0 |
| Analyzer | 0 | 0 | 0 | 0 | 0 |
| Extractor | 0 | 0 | 0 | 0 | 0 |
| Reporter | 0 | 0 | 0 | 0 | 0 |
| Integration | 0 | 0 | 0 | 0 | 0 |

**Update after each batch execution**

---

## 🔧 Batch 1: Reconnaissance Enhancements

### Enhancement #001: XML Project File Parsing
- **Category:** Parser
- **Priority:** HIGH
- **Feasibility:** Easy
- **Current Gap:** Cannot parse .csproj, .sln files for metadata
- **Proposed Solution:** Integrate Python `xml.etree.ElementTree` for XML parsing
- **Example Use Case:** Extract NuGet package references, framework version, project dependencies
- **Status:** ⏳ Pending

### Enhancement #002: Multi-File Metadata Aggregation
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot aggregate metadata across multiple project files
- **Proposed Solution:** Build project graph builder that traverses .sln → .csproj → references
- **Example Use Case:** Generate complete dependency graph for solution
- **Status:** ⏳ Pending

---

## 🔧 Batch 2: Rollover Logic Enhancements

### Enhancement #003: Method Signature with XML Doc Extraction
- **Category:** Extractor
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot extract XML documentation comments (`/// <summary>`)
- **Proposed Solution:** Parse trivia/comments in AST, associate with methods
- **Example Use Case:** Extract business logic explanation from `CalculateForefeitAndCarryoverBalanceEOYAllEmployersIdAsyncV2`
- **Status:** ⏳ Pending

### Enhancement #004: Feature Flag Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot detect feature flag usage patterns
- **Proposed Solution:** Pattern recognition for `FeatureFlag`, `if (featureEnabled)` structures
- **Example Use Case:** Track `SplitJobPerformanceV2` feature flag usage across codebase
- **Status:** ⏳ Pending

### Enhancement #005: Batch Processing Pattern Recognition
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Hard
- **Current Gap:** Cannot detect batch processing architectural patterns
- **Proposed Solution:** Machine learning or heuristic-based pattern detection (SemaphoreSlim, batch sizes)
- **Example Use Case:** Identify all batch processing methods similar to rollover logic
- **Status:** ⏳ Pending

### Enhancement #006: Async/Await Pattern Analysis
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot analyze async method call chains
- **Proposed Solution:** Build async call graph analyzer
- **Example Use Case:** Map async workflow from rollover trigger → completion
- **Status:** ⏳ Pending

---

## 🔧 Batch 3: Application Composition Enhancements

### Enhancement #007: Project Reference Resolution
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot resolve ProjectReference links between .csproj files
- **Proposed Solution:** Parse `<ProjectReference>` elements, build dependency graph
- **Example Use Case:** Map dependencies between Apps and Libs projects
- **Status:** ⏳ Pending

### Enhancement #008: Entry Point Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot automatically detect application entry points
- **Proposed Solution:** Search for `Main`, `Configure`, `ConfigureServices` methods
- **Example Use Case:** Identify startup configuration for each application project
- **Status:** ⏳ Pending

### Enhancement #009: NuGet Package Extraction
- **Category:** Extractor
- **Priority:** HIGH
- **Feasibility:** Easy
- **Current Gap:** Cannot extract NuGet package references from XML
- **Proposed Solution:** Parse `<PackageReference>` elements from .csproj
- **Example Use Case:** Generate complete technology stack report
- **Status:** ⏳ Pending

---

## 🔧 Batch 4: Domain Entity Enhancements

### Enhancement #010: C# Attribute Parsing
- **Category:** Parser
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot parse C# attributes (Data Annotations, EF configurations)
- **Proposed Solution:** Extend AST parser to extract attribute nodes and arguments
- **Example Use Case:** Extract `[Required]`, `[MaxLength(50)]`, `[Table("TableName")]`
- **Status:** ⏳ Pending

### Enhancement #011: Navigation Property Detection
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot detect navigation properties for ER diagrams
- **Proposed Solution:** Identify `ICollection<T>`, `IEnumerable<T>`, foreign key patterns
- **Example Use Case:** Auto-generate entity relationship diagrams
- **Status:** ⏳ Pending

### Enhancement #012: Generic Type Resolution
- **Category:** Parser
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot resolve generic type parameters (`T` in `ICollection<T>`)
- **Proposed Solution:** Implement generic type constraint analysis
- **Example Use Case:** Determine entity type in `ICollection<PaymentAccount>`
- **Status:** ⏳ Pending

### Enhancement #013: Inheritance Hierarchy Mapping
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot build inheritance trees
- **Proposed Solution:** Parse base class, interfaces, build tree structure
- **Example Use Case:** Generate inheritance diagram for domain entities
- **Status:** ⏳ Pending

---

## 🔧 Batch 5: Background Jobs Enhancements

### Enhancement #014: Job Scheduling Attribute Detection
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot extract cron expressions or scheduling attributes
- **Proposed Solution:** Parse scheduling attributes (Quartz, Hangfire, etc.)
- **Example Use Case:** Document when rollover jobs execute
- **Status:** ⏳ Pending

### Enhancement #015: Dependency Injection Container Analysis
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Hard
- **Current Gap:** Cannot analyze DI container registrations
- **Proposed Solution:** Parse `services.AddTransient`, `services.AddScoped` calls
- **Example Use Case:** Map all registered services and their lifetimes
- **Status:** ⏳ Pending

---

## 🔧 Batch 6: NServiceBus Enhancements

### Enhancement #016: NServiceBus Handler Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot detect message handler implementations
- **Proposed Solution:** Identify `IHandleMessages<T>` implementations
- **Example Use Case:** Map all message handlers in endpoint
- **Status:** ⏳ Pending

### Enhancement #017: Message Type Extraction
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot categorize message types (Command, Event, Query)
- **Proposed Solution:** Parse marker interfaces or naming conventions
- **Example Use Case:** Generate message catalog for NServiceBus endpoint
- **Status:** ⏳ Pending

### Enhancement #018: Saga Detection
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Medium
- **Current Gap:** Cannot detect NServiceBus sagas
- **Proposed Solution:** Identify `Saga<T>` base class usage
- **Example Use Case:** Document long-running processes (if sagas exist)
- **Status:** ⏳ Pending

---

## 🔧 Batch 7: Application Services Enhancements

### Enhancement #019: Constructor Injection Parameter Extraction
- **Category:** Extractor
- **Priority:** HIGH
- **Feasibility:** Easy
- **Current Gap:** Cannot extract constructor parameters for DI analysis
- **Proposed Solution:** Parse constructor signatures, extract parameter types
- **Example Use Case:** Generate service dependency graph
- **Status:** ⏳ Pending

### Enhancement #020: Interface Implementation Mapping
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot map interface → implementation relationships
- **Proposed Solution:** Parse interface inheritance, cross-reference implementations
- **Example Use Case:** Document abstraction usage in service layer
- **Status:** ⏳ Pending

### Enhancement #021: DTO vs Entity Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot distinguish DTOs from entities
- **Proposed Solution:** Heuristic analysis (folder location, naming, attributes)
- **Example Use Case:** Separate domain models from data transfer objects
- **Status:** ⏳ Pending

---

## 🔧 Batch 8: Use Case Enhancements

### Enhancement #022: XML Doc Comment Extraction
- **Category:** Extractor
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot extract XML documentation for use case descriptions
- **Proposed Solution:** Parse `///` comments above methods
- **Example Use Case:** Generate API documentation from code comments
- **Status:** ⏳ Pending

### Enhancement #023: Method Call Graph Generation
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Hard
- **Current Gap:** Cannot trace method call chains
- **Proposed Solution:** Build call graph from method invocations in AST
- **Example Use Case:** Map use case flow from controller → service → repository
- **Status:** ⏳ Pending

### Enhancement #024: Use Case Flow Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Hard
- **Current Gap:** Cannot automatically detect business use case boundaries
- **Proposed Solution:** Pattern recognition for orchestration methods
- **Example Use Case:** Identify "Process Rollover" as complete use case
- **Status:** ⏳ Pending

---

## 🔧 Batch 9: Data Access Enhancements

### Enhancement #025: Repository Pattern Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot detect repository pattern usage
- **Proposed Solution:** Identify `IRepository<T>` or naming conventions
- **Example Use Case:** List all repositories in application
- **Status:** ⏳ Pending

### Enhancement #026: EF DbContext Mapping
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot extract DbContext configurations
- **Proposed Solution:** Parse `DbContext` class, `DbSet<T>` properties
- **Example Use Case:** Generate database schema from DbContext
- **Status:** ⏳ Pending

### Enhancement #027: Migration File Parsing
- **Category:** Parser
- **Priority:** LOW
- **Feasibility:** Medium
- **Current Gap:** Cannot parse EF migration files
- **Proposed Solution:** Analyze migration `Up`/`Down` methods
- **Example Use Case:** Generate database schema evolution timeline
- **Status:** ⏳ Pending

### Enhancement #028: LINQ Query Analysis
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Hard
- **Current Gap:** Cannot analyze LINQ query expressions
- **Proposed Solution:** Parse LINQ syntax, extract query semantics
- **Example Use Case:** Document complex queries in repositories
- **Status:** ⏳ Pending

---

## 🔧 Batch 10: Test Coverage Enhancements

### Enhancement #029: Test Framework Attribute Detection
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot detect test framework attributes (xUnit, NUnit, MSTest)
- **Proposed Solution:** Parse `[Fact]`, `[Test]`, `[TestMethod]` attributes
- **Example Use Case:** Categorize tests by framework
- **Status:** ⏳ Pending

### Enhancement #030: Test-to-Production Mapping
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Hard
- **Current Gap:** Cannot automatically map tests to production code
- **Proposed Solution:** Naming convention + dependency analysis
- **Example Use Case:** Calculate test coverage % per class
- **Status:** ⏳ Pending

### Enhancement #031: Mock/Stub Detection
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Medium
- **Current Gap:** Cannot detect mocking framework usage
- **Proposed Solution:** Identify Moq, NSubstitute patterns
- **Example Use Case:** Document test isolation strategies
- **Status:** ⏳ Pending

### Enhancement #032: Assertion Pattern Analysis
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Medium
- **Current Gap:** Cannot analyze assertion patterns
- **Proposed Solution:** Parse `Assert.*`, `Should.*` calls
- **Example Use Case:** Validate test quality (assertion count per test)
- **Status:** ⏳ Pending

---

## 🔧 Batch 11: Plan Type Enhancements

### Enhancement #033: Enum Value Extraction with Descriptions
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot extract enum values with XML doc comments
- **Proposed Solution:** Parse enum members + associated comments
- **Example Use Case:** Document all plan types with descriptions
- **Status:** ⏳ Pending

### Enhancement #034: Conditional Logic Pattern Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Hard
- **Current Gap:** Cannot detect business logic branching by plan type
- **Proposed Solution:** Analyze `if`, `switch` statements on plan type
- **Example Use Case:** Document plan type specific business rules
- **Status:** ⏳ Pending

### Enhancement #035: Strategy Pattern Recognition
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Hard
- **Current Gap:** Cannot detect strategy pattern usage
- **Proposed Solution:** Identify interface + multiple implementations
- **Example Use Case:** Document plan type specific calculation strategies
- **Status:** ⏳ Pending

---

## 🔧 Batch 12: Integration Enhancements

### Enhancement #036: HTTP Client Pattern Detection
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot detect HTTP client usage patterns
- **Proposed Solution:** Identify `HttpClient`, `IHttpClientFactory` usage
- **Example Use Case:** Map all external API calls
- **Status:** ⏳ Pending

### Enhancement #037: Connection String Extraction
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot extract configuration settings
- **Proposed Solution:** Parse appsettings.json, environment variables
- **Example Use Case:** Document all database connections
- **Status:** ⏳ Pending

### Enhancement #038: Configuration Binding Analysis
- **Category:** Analyzer
- **Priority:** LOW
- **Feasibility:** Medium
- **Current Gap:** Cannot trace configuration binding to POCOs
- **Proposed Solution:** Parse `IOptions<T>`, `Configure<T>` patterns
- **Example Use Case:** Document all configuration classes
- **Status:** ⏳ Pending

---

## 🔧 Batch 13: Business Logic Enhancements

### Enhancement #039: Calculation Method Pattern Detection
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Medium
- **Current Gap:** Cannot detect calculation methods
- **Proposed Solution:** Identify methods with numeric return types, math operations
- **Example Use Case:** Catalog all balance calculation methods
- **Status:** ⏳ Pending

### Enhancement #040: Constant/Magic Number Extraction
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot extract constants used in business logic
- **Proposed Solution:** Parse `const`, `readonly`, literal values in calculations
- **Example Use Case:** Document business rule constants (batch size = 1000)
- **Status:** ⏳ Pending

### Enhancement #041: Validation Attribute Parsing
- **Category:** Extractor
- **Priority:** MEDIUM
- **Feasibility:** Easy
- **Current Gap:** Cannot extract validation rules from attributes
- **Proposed Solution:** Parse `[Required]`, `[Range]`, custom validation attributes
- **Example Use Case:** Document input validation rules
- **Status:** ⏳ Pending

### Enhancement #042: Date Calculation Logic Analysis
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Hard
- **Current Gap:** Cannot analyze date/time calculations
- **Proposed Solution:** Detect `DateTime`, `DateTimeOffset` operations
- **Example Use Case:** Document fiscal year, plan year calculations
- **Status:** ⏳ Pending

---

## 🔧 Batch 14: Architecture Enhancements

### Enhancement #043: Architecture Pattern Detection Algorithms
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Hard
- **Current Gap:** Cannot automatically detect architecture patterns
- **Proposed Solution:** Machine learning or heuristic-based pattern matching
- **Example Use Case:** Identify DDD, Clean Architecture, CQRS patterns
- **Status:** ⏳ Pending

### Enhancement #044: Layer Boundary Violation Detection
- **Category:** Analyzer
- **Priority:** HIGH
- **Feasibility:** Hard
- **Current Gap:** Cannot detect architectural violations
- **Proposed Solution:** Define layer rules, analyze cross-layer dependencies
- **Example Use Case:** Flag domain layer depending on infrastructure
- **Status:** ⏳ Pending

### Enhancement #045: Dependency Direction Analysis
- **Category:** Analyzer
- **Priority:** MEDIUM
- **Feasibility:** Medium
- **Current Gap:** Cannot verify dependency inversion principle
- **Proposed Solution:** Build dependency graph, check direction compliance
- **Example Use Case:** Validate inner layers don't depend on outer layers
- **Status:** ⏳ Pending

---

## 📊 Priority Matrix

### HIGH Priority (Must Have - 15 items)
- #001 XML Project File Parsing
- #003 Method Signature with XML Doc Extraction
- #007 Project Reference Resolution
- #009 NuGet Package Extraction
- #010 C# Attribute Parsing
- #011 Navigation Property Detection
- #015 Dependency Injection Container Analysis
- #019 Constructor Injection Parameter Extraction
- #022 XML Doc Comment Extraction
- #023 Method Call Graph Generation
- #026 EF DbContext Mapping
- #030 Test-to-Production Mapping
- #039 Calculation Method Pattern Detection
- #043 Architecture Pattern Detection Algorithms
- #044 Layer Boundary Violation Detection

### MEDIUM Priority (Should Have - 23 items)
- #002, #004, #006, #008, #012, #013, #014, #016, #017, #020, #021, #024, #025, #028, #029, #033, #034, #036, #037, #040, #041, #042, #045

### LOW Priority (Nice to Have - 7 items)
- #005, #018, #027, #031, #032, #035, #038

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- XML parsing (#001, #009)
- C# attribute parsing (#010)
- Constructor/method signature extraction (#019, #003)

### Phase 2: Relationships (Weeks 3-4)
- Navigation properties (#011)
- Project references (#007)
- Dependency injection analysis (#015)

### Phase 3: Advanced Analysis (Weeks 5-6)
- Method call graphs (#023)
- Architecture pattern detection (#043, #044)
- Test mapping (#030)

### Phase 4: Specialized Features (Weeks 7-8)
- NServiceBus support (#016, #017)
- EF DbContext analysis (#026)
- Business logic patterns (#039, #040)

---

## 📝 Notes

**Update this document after each batch execution with new discoveries**

**Format for new enhancements:**
```markdown
### Enhancement #XXX: {Title}
- **Category:** {Parser|Analyzer|Extractor|Reporter|Integration}
- **Priority:** {HIGH|MEDIUM|LOW}
- **Feasibility:** {Easy|Medium|Hard}
- **Current Gap:** {what cannot be done today}
- **Proposed Solution:** {how to implement}
- **Example Use Case:** {specific RA domain example}
- **Status:** {⏳ Pending | 🔨 In Progress | ✅ Complete}
```

---

**Last Updated:** December 11, 2025  
**Total Enhancements Tracked:** 45  
**Batches Completed:** 0 / 15

