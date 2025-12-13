# Risk Register

**Project:** PSF Prevalidation WS Modernization  
**Based On:** RA Migration Lessons Learned  
**Total Risks:** 38 (from lessons learned) + 12 PrevalidationWS-specific = 50  
**Last Updated:** Phase 0 (Before Implementation)

---

## 🎯 Risk Management Strategy

**Approach:** Convert all 38 RA migration lessons learned into preventive controls.

**Risk Categories:**
1. Environment & Tooling (BLOCKER-001)
2. Contract Compatibility (BLOCKER-002)
3. Schema Validation (BLOCKER-003)
4. Test Coverage
5. Data Layer Architecture
6. Deployment Automation
7. Monitoring & Observability
8. Documentation
9. Performance & Scalability
10. Security & Compliance

**Risk Levels:**
- 🔴 **CRITICAL:** Will block deployment (Likelihood: High, Impact: High)
- 🟠 **HIGH:** Will cause significant delay (Likelihood: High, Impact: Medium)
- 🟡 **MEDIUM:** May cause minor delay (Likelihood: Medium, Impact: Low)
- 🟢 **LOW:** Minimal impact (Likelihood: Low, Impact: Low)

---

## 🔴 CRITICAL Risks (Blocker Prevention)

### RISK-001: SDK Missing on Build Server
**Lesson Learned:** BLOCKER-001 from RA Migration  
**RA Impact:** 2-week delay when .NET 8 SDK not installed on build server  
**Root Cause:** Assumed SDK already present, discovered during Phase 2  
**Likelihood:** High (if not checked)  
**Impact:** High (2+ week delay)  

**Prevention (Phase 0):**
- ✅ Pre-flight verification script (`pre-flight-check.ps1`)
- ✅ Verify .NET SDK 8.0+ on ALL machines (dev, build, deployment)
- ✅ Azure DevOps pipeline includes `UseDotNet@2` task
- ✅ Document SDK version in `README.md`

**Detection:**
```powershell
# Run before Phase 1 Day 1
.\cortex\plan\scripts\pre-flight-check.ps1
# Expected: "✅ .NET SDK 8.x installed"
```

**Mitigation Plan (if occurs):**
1. Install .NET SDK 8.0 from https://dotnet.microsoft.com/download/dotnet/8.0
2. Verify with `dotnet --version`
3. Re-run pre-flight script
4. Update pipeline YAML with explicit SDK version

**Status:** 🟢 MITIGATED (pre-flight script created)

---

### RISK-002: WCF Proxy Created Too Late
**Lesson Learned:** BLOCKER-002 from RA Migration  
**RA Impact:** 6-day delay when WCF proxy delayed until Phase 5  
**Root Cause:** Contract testing framework not ready until late in project  
**Likelihood:** High (if WCF proxy deferred)  
**Impact:** High (6+ day delay)  

**Prevention (Phase 2):**
- ✅ Create WCF proxy IMMEDIATELY in Phase 2 (not Phase 5)
- ✅ Add contract verification tests in Phase 4a (before implementation)
- ✅ Run 100+ contract tests against ASMX and REST side-by-side
- ✅ Block Phase 5 if contract compatibility < 100%

**Implementation Timeline:**
```
Phase 2 (Week 2):
  - Create WCF proxy targeting ASMX service
  - Verify proxy can call ValidatePSFFileWLogging
  - Document proxy usage in test-strategy.md

Phase 4a (Week 6):
  - Create contract verification framework
  - Run 100+ parallel tests (ASMX vs REST)
  - Achieve 100% compatibility gate
```

**Detection:**
- Phase 2 deliverable checklist includes "WCF proxy created and tested"
- Phase 4a gate: "Contract compatibility = 100%" (not 99%, not 98%)

**Mitigation Plan (if occurs):**
1. STOP all Phase 5 work immediately
2. Create WCF proxy (2-3 days)
3. Run contract verification tests
4. Fix any compatibility breaks
5. Resume Phase 5 only after 100% compatibility

**Status:** 🟡 PLANNED (Phase 2 deliverable defined)

---

### RISK-003: Schema Validation Skipped
**Lesson Learned:** BLOCKER-003 from RA Migration  
**RA Impact:** Potential runtime breaks discovered in production  
**Root Cause:** Schema validation treated as optional, not mandatory gate  
**Likelihood:** High (if not enforced)  
**Impact:** High (production incidents)  

**Prevention (Phase 5a):**
- ✅ Phase 5a MANDATORY gate: Schema validation before integration tests
- ✅ Validate all 14 error types from PSFValidator
- ✅ Validate all 9 record types (PAF, PAI, PRF, etc.)
- ✅ Test file format compatibility (fixed-width, delimited, XML)
- ✅ Block Phase 6 deployment if schema validation fails

**Schema Validation Checklist:**
```
Phase 5a Schema Validation (Week 9):
  ✅ PAF record validation (19 fields)
  ✅ PAI record validation (8 fields)
  ✅ PRF record validation (17 fields)
  ✅ Invalid format detection (14 error types)
  ✅ File encoding validation (UTF-8, ANSI)
  ✅ DIME attachment → multipart/form-data
  ✅ 100+ schema test cases passing

Gate: CANNOT proceed to Phase 6 without 100% schema validation
```

**Detection:**
- Phase 5a deliverable: "Schema Validation Report" with 100% pass rate
- Automated tests in `SchemaValidationTests.cs` (130+ tests)

**Mitigation Plan (if occurs):**
1. STOP Phase 6 deployment
2. Identify schema mismatches (compare ASMX vs REST)
3. Fix validation logic in validators
4. Re-run full schema test suite
5. Resume deployment only after 100% pass

**Status:** 🟡 PLANNED (Phase 5a gate defined)

---

## 🟠 HIGH Risks

### RISK-004: Test Coverage Below Target
**Lesson Learned:** LS-01 from Test Coverage Strategy  
**RA Success:** 130 tests, 90%+ coverage  
**PrevalidationWS Target:** 95% coverage (PSFValidator most critical)  
**Likelihood:** Medium  
**Impact:** High (cannot deploy with < 90% coverage)  

**Prevention (Phases 3-5):**
- Phase 3 gate: 60% coverage (domain models, basic validators)
- Phase 4 gate: 75% coverage (services, repositories)
- Phase 5 gate: 90% coverage (integration tests)
- Target: 95% coverage on PSFValidator (1,328 lines)

**Coverage Breakdown:**
```
Layer 1 (API Controllers):      80% coverage (simple pass-through)
Layer 2 (Services):             90% coverage (business logic)
Layer 3 (Validators):           95% coverage (PSFValidator critical)
Layer 4 (Repositories):         85% coverage (data access)
Layer 5 (Domain Models):        70% coverage (DTOs)
```

**Detection:**
```powershell
# Run after each phase
dotnet test --collect:"XPlat Code Coverage"
reportgenerator -reports:coverage.cobertura.xml -targetdir:coveragereport
# Check coveragereport/index.html
```

**Mitigation Plan:**
1. Identify uncovered code paths (use coverage report)
2. Write missing unit tests (RED→GREEN→REFACTOR)
3. Prioritize high-risk code (PSFValidator, error handling)
4. Re-run coverage until gate met

**Status:** 🟡 PLANNED (phase-by-phase gates defined)

---

### RISK-005: Oracle Connection String Hardcoded
**Lesson Learned:** LS-15 from Mock Data Layer  
**RA Success:** Swappable Mock/EF Core via configuration  
**PrevalidationWS Risk:** Connection string in app.config  
**Likelihood:** Medium (requires refactoring)  
**Impact:** High (security, testability)  

**Current State (Business/PrevalidationData.cs):**
```csharp
// RISK: Hardcoded connection string logic
string connectionString = ConfigurationManager.ConnectionStrings["OracleConnection"].ConnectionString;
OracleConnection conn = new OracleConnection(connectionString);
```

**Prevention (Phase 3):**
- Use ASP.NET Core configuration (`appsettings.json`, Key Vault)
- Inject `IConfiguration` into repository constructors
- Support multiple environments (Dev, Test, Prod)

**Refactored Approach:**
```csharp
// Phase 3 implementation
public class PrevalidationRepository : IPrevalidationRepository
{
    private readonly string _connectionString;
    
    public PrevalidationRepository(IConfiguration configuration)
    {
        _connectionString = configuration.GetConnectionString("OracleConnection");
    }
    
    public async Task<ValidationResult> ValidateFileAsync(Stream fileStream)
    {
        using var conn = new OracleConnection(_connectionString);
        await conn.OpenAsync();
        // ...
    }
}
```

**appsettings.json:**
```json
{
  "ConnectionStrings": {
    "OracleConnection": "Data Source=..."
  }
}
```

**Detection:**
- Code review Phase 3: No `ConfigurationManager` usage
- All connection strings from `IConfiguration`

**Mitigation Plan:**
1. Refactor PrevalidationData to use dependency injection
2. Move connection string to `appsettings.json`
3. Add Key Vault integration for production
4. Update tests to use mock connection strings

**Status:** 🟡 PLANNED (Phase 3 refactoring)

---

### RISK-006: DIME Attachment Migration Complexity
**Lesson Learned:** PrevalidationWS-specific (not in RA)  
**Current State:** ASMX uses DIME (Direct Internet Message Encapsulation)  
**Target State:** REST uses `multipart/form-data`  
**Likelihood:** High (format change required)  
**Impact:** High (file upload broken if wrong)  

**Current ASMX Implementation (WebService/PSFPreValidate.asmx.cs):**
```csharp
[WebMethod]
[SoapDocumentMethod]
public PSFPrevalResult ValidatePSFFileWLogging(...)
{
    // Get DIME attachment
    DimeAttachment attachment = RequestSoapContext.Current.Attachments[0];
    Stream fileStream = attachment.Stream;
    string fileName = attachment.Type.Name;
    // ...
}
```

**Target REST Implementation:**
```csharp
[HttpPost("validate")]
public async Task<ActionResult<ValidationResult>> ValidateFile(
    [FromForm] IFormFile file,
    [FromForm] ValidationRequest request)
{
    // Multipart form data
    using var stream = file.OpenReadStream();
    string fileName = file.FileName;
    // Call validator with stream
}
```

**Migration Challenges:**
1. DIME → multipart/form-data format conversion
2. File size limits (50 MB current, need to maintain)
3. Content-Type detection (application/octet-stream)
4. Temporary file cleanup

**Prevention (Phase 4):**
- Create file upload handler in Phase 4
- Test with 10+ MB files (stress test)
- Verify Content-Type handling
- Test parallel uploads (10+ concurrent)

**Detection:**
```csharp
// Phase 4a contract test
[Fact]
public async Task ValidateFile_MultipartUpload_MatchesAsmxDimeAttachment()
{
    // Upload 10 MB file via ASMX (DIME)
    var asmxResult = await _asmxProxy.ValidatePSFFileWLoggingAsync(testFile);
    
    // Upload same file via REST (multipart)
    var restResult = await _restClient.PostAsync("/api/v1/prevalidations/validate", multipartContent);
    
    // Compare results byte-by-byte
    Assert.Equal(asmxResult.ValidationErrors, restResult.ValidationErrors);
}
```

**Mitigation Plan:**
1. Review DIME attachment code in ASMX
2. Create equivalent multipart handler
3. Test with real PSF files (1 KB to 50 MB)
4. Verify error handling (file too large, corrupt file)

**Status:** 🟠 ACTIVE (requires Phase 4 implementation)

---

### RISK-007: Performance Regression
**Lesson Learned:** LS-30 from Monitoring & Observability  
**Current Performance (Business/PSFValidator.cs):**
- Validation time: 2-5 seconds per file
- Memory usage: 50 MB peak
- File size limit: 50 MB

**Target Performance:**
- Validation time: 1-3 seconds per file (50% faster)
- Memory usage: 30 MB peak (40% less)
- File size limit: 100 MB (2x larger)

**Risk:** .NET 8 migration introduces performance regression  
**Likelihood:** Medium (new framework, new patterns)  
**Impact:** High (user complaints, SLA breach)  

**Prevention (Phase 5b):**
- Load testing with 100+ concurrent requests
- Memory profiling (dotMemory, PerfView)
- Benchmarking framework (BenchmarkDotNet)
- Comparison tests (ASMX vs REST side-by-side)

**Performance Test Suite:**
```csharp
// Phase 5b performance tests
[Fact]
public async Task ValidateFile_1MBFile_CompletesWithin2Seconds()
{
    var stopwatch = Stopwatch.StartNew();
    var result = await _validator.ValidateFileAsync(testStream);
    stopwatch.Stop();
    
    Assert.True(stopwatch.ElapsedMilliseconds < 2000, 
        $"Validation took {stopwatch.ElapsedMilliseconds}ms (expected < 2000ms)");
}

[Fact]
public async Task ValidateFile_100ConcurrentRequests_AllCompleteWithin10Seconds()
{
    var tasks = Enumerable.Range(0, 100)
        .Select(_ => _validator.ValidateFileAsync(testStream))
        .ToArray();
    
    var stopwatch = Stopwatch.StartNew();
    await Task.WhenAll(tasks);
    stopwatch.Stop();
    
    Assert.True(stopwatch.ElapsedMilliseconds < 10000);
}
```

**Detection:**
- Phase 5b deliverable: "Performance Test Report"
- Automated performance tests in CI/CD pipeline
- Application Insights metrics (P95, P99 latency)

**Mitigation Plan:**
1. Profile slow code paths (dotTrace, PerfView)
2. Optimize hot paths (file parsing, database queries)
3. Add caching (Redis for validation rules)
4. Scale horizontally (Azure App Service)

**Status:** 🟡 PLANNED (Phase 5b performance testing)

---

## 🟡 MEDIUM Risks

### RISK-008: Documentation Drift
**Lesson Learned:** LS-33 from Documentation Strategy  
**RA Success:** Living documentation updated with code  
**Risk:** Documentation becomes outdated during implementation  
**Likelihood:** Medium  
**Impact:** Medium (onboarding delays)  

**Prevention:**
- Update README.md with every phase
- Keep API documentation in code (XML comments, Swagger)
- Review docs in code review checklist

**Status:** 🟡 PLANNED

---

### RISK-009: Deployment Rollback Complexity
**Lesson Learned:** LS-25 from Deployment Automation  
**RA Success:** Blue-green deployment with instant rollback  
**Risk:** Rollback not tested until production incident  
**Likelihood:** Low  
**Impact:** High (if needed in emergency)  

**Prevention (Phase 7):**
- Practice blue-green deployment in Test environment
- Document rollback procedure
- Test rollback scenarios (database incompatibility, API breaking changes)

**Status:** 🟡 PLANNED (Phase 7)

---

### RISK-010: Key Personnel Unavailable
**Risk:** Technical lead or key developer unavailable mid-project  
**Likelihood:** Low (19-week timeline)  
**Impact:** Medium (1-2 week delay)  

**Prevention:**
- Cross-train team on all phases
- Document all design decisions
- Pair programming during critical phases

**Status:** 🟢 ACCEPTED (inherent project risk)

---

## 🟢 LOW Risks

### RISK-011 to RISK-050
*(PrevalidationWS-specific risks and remaining 28 lessons learned mapped to preventive controls)*

**Categories:**
- Dependency version conflicts (NuGet packages)
- Third-party library changes (Oracle.EntityFrameworkCore)
- Network connectivity during deployment
- Database migration failures
- Configuration drift between environments
- Security vulnerabilities in dependencies
- Compliance requirements (SOC 2, GDPR)
- Team morale and burnout
- Scope creep (feature requests mid-project)

**Status:** 🟢 MONITORED (tracked in weekly risk review)

---

## 📊 Risk Dashboard

**Overall Risk Score:** 🟡 MEDIUM

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Environment & Tooling | 1 | 0 | 1 | 2 | 4 |
| Contract Compatibility | 1 | 1 | 2 | 3 | 7 |
| Schema Validation | 1 | 0 | 1 | 2 | 4 |
| Test Coverage | 0 | 1 | 2 | 5 | 8 |
| Data Layer | 0 | 1 | 2 | 4 | 7 |
| Deployment | 0 | 1 | 3 | 3 | 7 |
| Monitoring | 0 | 0 | 2 | 3 | 5 |
| Documentation | 0 | 0 | 1 | 2 | 3 |
| Performance | 0 | 1 | 1 | 2 | 4 |
| Security | 0 | 0 | 1 | 2 | 3 |
| **Total** | **3** | **5** | **16** | **28** | **52** |

**Mitigation Status:**
- ✅ Mitigated: 1 (RISK-001 via pre-flight script)
- 🟡 Planned: 7 (RISK-002 to RISK-009)
- 🟢 Accepted: 1 (RISK-010)
- 🔵 Monitored: 43 (RISK-011 to RISK-050)

---

## 🔄 Risk Review Process

**Weekly Risk Review (Every Friday):**
1. Review all 🔴 Critical and 🟠 High risks
2. Update mitigation status based on phase progress
3. Identify new risks from current week's work
4. Escalate blockers to stakeholders

**Phase Gate Risk Review:**
- Phase 0: Verify RISK-001 mitigated (pre-flight passed)
- Phase 2: Verify RISK-002 mitigation started (WCF proxy created)
- Phase 4a: Verify RISK-002 mitigated (contract compatibility 100%)
- Phase 5a: Verify RISK-003 mitigated (schema validation 100%)
- Phase 5b: Verify RISK-007 mitigated (performance tests passed)
- Phase 7: Verify RISK-009 mitigated (rollback tested)

**Escalation Criteria:**
- Any 🔴 Critical risk not mitigated before its phase
- Any 🟠 High risk trending worse week-over-week
- 3+ new risks identified in single week

---

## 📚 Related Documents

- [Master Plan](MODERNIZATION-PLAN.md) - Overall project plan
- [Lessons Learned](prevalidation-ws-migration-lessons-learned-plan.md) - All 38 lessons
- [Phase 0: Pre-Flight](phase-0-pre-flight.md) - BLOCKER-001 prevention
- [Test Strategy](test-strategy.md) - Coverage gates and TDD workflow

---

**Next Review:** After Phase 0 pre-flight script execution  
**Owner:** Technical Lead  
**Last Updated:** Phase 0 (Before Implementation)
