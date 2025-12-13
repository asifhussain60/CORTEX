# Test Strategy

**Project:** PSF Prevalidation WS Modernization  
**Target:** 130+ tests, 95% coverage (RA baseline: 130 tests, 90% coverage)  
**Approach:** TDD (RED→GREEN→REFACTOR) with phase-by-phase coverage gates

---

## 🎯 Testing Philosophy

**From RA Migration Success:**
- 130 automated tests across all layers
- 90%+ code coverage with quality gates
- 100% contract compatibility verification
- TDD mandatory (write test BEFORE implementation)

**PrevalidationWS Enhancements:**
- Target 95% coverage (PSFValidator most critical at 1,328 lines)
- 14 error type validations (from current PSFValidator)
- 9 record type validations (PAF, PAI, PRF, etc.)
- File format compatibility (fixed-width, delimited, XML)
- Performance testing (1-3 sec validation time, 100+ concurrent requests)

---

## 🧪 Test Pyramid

```
                    ┌─────────────────┐
                    │  E2E Tests (5)  │  5% - Full workflow
                    └─────────────────┘
                ┌────────────────────────┐
                │ Integration Tests (20) │  15% - API + DB + External
                └────────────────────────┘
            ┌────────────────────────────────┐
            │   Component Tests (35)         │  25% - Service layer
            └────────────────────────────────┘
        ┌────────────────────────────────────────┐
        │      Unit Tests (70)                   │  55% - Business logic
        └────────────────────────────────────────┘

Total: 130 tests (matching RA migration success)
```

**Distribution:**
- Unit Tests: 70 (55%) - Validators, parsers, business rules
- Component Tests: 35 (25%) - Service orchestration, repository patterns
- Integration Tests: 20 (15%) - API → Database → External services
- E2E Tests: 5 (5%) - Full prevalidation workflow

---

## 📋 Test Coverage Gates (Phase-by-Phase)

### Phase 3: Domain Models & Validators (60% Coverage)
**Deadline:** Week 4-5  
**Focus:** Core business logic without external dependencies

**Required Tests (30 unit tests):**
```csharp
// Domain Models (10 tests)
ValidationResultTests.cs
- ValidateFile_ValidPAFRecord_ReturnsSuccess
- ValidateFile_InvalidRecordType_ReturnsError
- ValidateFile_MissingRequiredField_ReturnsValidationError
- ValidationResult_SerializesToJson_Correctly
- ValidationResult_DeserializesFromJson_Correctly
- ValidationErrors_EmptyList_IsValid
- ValidationErrors_ContainsError_IsInvalid
- ValidationSeverity_Critical_BlocksProcessing
- ValidationSeverity_Warning_AllowsProcessing
- ValidationMetadata_TracksProcessingTime

// Validators (20 tests - most critical)
PSFValidatorTests.cs
- ParseAndValidatePsfFile_ValidPAFRecord_ReturnsSuccess
- ParseAndValidatePsfFile_InvalidRecordType_ReturnsErrorType1
- ParseAndValidatePsfFile_InvalidFormat_ReturnsErrorType2
- ParseAndValidatePsfFile_EmptyFile_ReturnsErrorType3
- ParseAndValidatePsfFile_ExceedsMaxLines_ReturnsErrorType4
- ParseAndValidatePsfFile_InvalidHeaderRecord_ReturnsErrorType5
- ParseAndValidatePsfFile_MissingRequiredData_ReturnsErrorType6
- ParseAndValidatePsfFile_InvalidDataFormat_ReturnsErrorType7
- ParseAndValidatePsfFile_InvalidDate_ReturnsErrorType8
- ParseAndValidatePsfFile_InvalidNumeric_ReturnsErrorType9
- ParseAndValidatePsfFile_InvalidCurrency_ReturnsErrorType10
- ParseAndValidatePsfFile_DuplicateRecord_ReturnsErrorType11
- ParseAndValidatePsfFile_InvalidChecksum_ReturnsErrorType12
- ParseAndValidatePsfFile_InvalidControlTotal_ReturnsErrorType13
- ParseAndValidatePsfFile_UnknownRecordType_ReturnsErrorType14
- ParseAndValidatePsfFile_AllNineRecordTypes_AllValidate
- ParseAndValidatePsfFile_10MBFile_CompletesWithin3Seconds
- ParseAndValidatePsfFile_SpecialCharacters_HandledCorrectly
- ParseAndValidatePsfFile_UTF8Encoding_ParsedCorrectly
- ParseAndValidatePsfFile_ANSIEncoding_ParsedCorrectly
```

**Coverage Target:**
- PSFValidator.cs: 95% (1,328 lines - most critical)
- Domain models: 70% (simple DTOs)
- FluentValidation rules: 90%

**Gate:** Cannot proceed to Phase 4 if coverage < 60%

---

### Phase 4: Services & Repositories (75% Coverage)
**Deadline:** Week 6-7  
**Focus:** Service orchestration, data access, contract verification

**Required Tests (40 component + integration tests):**
```csharp
// Service Layer (25 component tests)
PrevalidationServiceTests.cs
- ValidateFileAsync_CallsValidator_ReturnsResult
- ValidateFileAsync_NullStream_ThrowsArgumentException
- ValidateFileAsync_EmptyStream_ReturnsValidationError
- ValidateFileAsync_LargeFile_HandlesGracefully
- ValidateFileAsync_ConcurrentRequests_AllSucceed
- ValidateWorkflowAsync_CallsWorkflowEngine_ReturnsStatus
- GetValidationHistoryAsync_ReturnsPagedResults
- LogValidationAsync_WritesToDatabase_ReturnsSuccess
- DeleteOldLogsAsync_RemovesExpiredRecords
- GetValidationMetricsAsync_ReturnsStatistics

// Repository Layer (15 integration tests)
PrevalidationRepositoryTests.cs
- SaveValidationResultAsync_InsertsRecord_ReturnsId
- GetValidationByIdAsync_ExistingId_ReturnsResult
- GetValidationByIdAsync_NonExistentId_ReturnsNull
- GetValidationHistoryAsync_FiltersBy UserId_ReturnsUserRecords
- GetValidationHistoryAsync_FiltersByDateRange_ReturnsDateRangeRecords
- UpdateValidationStatusAsync_ExistingId_Updates Status
- DeleteValidationAsync_ExistingId_SoftDeletes
- SaveBlobReferenceAsync_StoresMetadata_ReturnsUri
- GetBlobByIdAsync_ExistingId_ReturnsUri
- BulkInsertValidationsAsync_1000Records_CompletesWithin5Seconds
- Transaction_Rollback_OnError_MaintainsDataIntegrity
- ConnectionPooling_100ConcurrentQueries_NoLeaks
- OracleDataReader_LargeResultSet_StreamsData
- OracleParameter_SqlInjection_Prevented
- RepositoryPattern_MockSwap_WorksInTests
```

**Coverage Target:**
- Service layer: 90% (core business orchestration)
- Repository layer: 85% (data access)
- API controllers: 80% (thin pass-through layer)

**Gate:** Cannot proceed to Phase 5 if coverage < 75%

---

### Phase 4a: Contract Verification (100% Compatibility)
**Deadline:** Week 6 (before Phase 5)  
**Focus:** ASMX vs REST side-by-side testing

**Required Tests (25 contract tests):**
```csharp
// Contract Verification Framework
ContractCompatibilityTests.cs
- ValidatePSFFileWLogging_SameInput_AsmxRestResultsMatch
- ValidatePSFFileWorkFlow_SameInput_AsmxRestResultsMatch
- GetValidationHistory_SameUser_AsmxRestResultsMatch
- DeleteOldLogs_SameDateRange_AsmxRestResultsMatch
- GetUserDetails_SameUserId_AsmxRestResultsMatch
- GetTransactionStatus_SameTransactionId_AsmxRestResultsMatch

// Field Mapping (10 tests)
FieldMappingTests.cs
- PascalCase_To_CamelCase_AllFieldsMapped
- SOAP_Fault_To_ProblemDetails_AllErrorsMapped
- DIME_Attachment_To_Multipart_FilesMatch
- WSE_Security_To_JWT_AuthenticationMatches
- SOAP_Headers_To_HTTP_Headers_AllHeadersMapped
- DateTimeFormat_ASMX_To_ISO8601_Matches
- DecimalFormat_ASMX_To_JSON_PrecisionMaintained
- EnumValues_ASMX_To_REST_AllValuesMatch
- NullHandling_ASMX_To_REST_BehaviorMatches
- ArraySerialization_ASMX_To_REST_OrderPreserved

// Error Scenarios (9 tests)
ErrorCompatibilityTests.cs
- InvalidFile_ASMX_REST_SameErrorCode
- MissingField_ASMX_REST_SameErrorMessage
- AuthenticationFailure_ASMX_REST_Same401
- AuthorizationFailure_ASMX_REST_Same403
- FileTooBig_ASMX_REST_Same413
- ServerError_ASMX_REST_Same500
- Timeout_ASMX_REST_Same504
- InvalidContentType_ASMX_REST_Same415
- RateLimitExceeded_ASMX_REST_Same429
```

**Gate:** MUST achieve 100% contract compatibility (not 99%, not 98%)  
**Blocker Prevention:** BLOCKER-002 from RA migration (WCF proxy delayed)

---

### Phase 5: Integration & Performance (90% Coverage)
**Deadline:** Week 8-10  
**Focus:** Full API testing, database integration, performance benchmarks

**Required Tests (30 integration + performance tests):**
```csharp
// Integration Tests (20 tests)
PrevalidationApiIntegrationTests.cs
- POST_ValidateFile_ValidFile_Returns200
- POST_ValidateFile_InvalidFile_Returns400
- POST_ValidateFile_UnauthenticatedUser_Returns401
- POST_ValidateFile_UnauthorizedUser_Returns403
- POST_ValidateFile_FileTooBig_Returns413
- POST_ValidateFile_ConcurrentRequests_AllSucceed
- POST_ValidateWorkflow_ValidRequest_Returns200
- GET_ValidationHistory_ValidUser_ReturnsPagedResults
- GET_ValidationHistory_EmptyResults_Returns200
- DELETE_OldLogs_ValidDateRange_Returns204
- GET_UserDetails_ExistingUser_Returns200
- GET_UserDetails_NonExistentUser_Returns404
- GET_TransactionStatus_ExistingTransaction_Returns200
- POST_ValidateFile_DatabaseDown_Returns503
- POST_ValidateFile_BlobStorageDown_Returns503
- POST_ValidateFile_ServiceBusDown_LogsWarning
- HealthCheck_AllServicesUp_ReturnsHealthy
- HealthCheck_DatabaseDown_ReturnsUnhealthy
- Swagger_UI_Accessible_Returns200
- OpenAPI_Spec_Valid_NoErrors

// Performance Tests (10 tests)
PerformanceTests.cs
- ValidateFile_1MBFile_CompletesWithin2Seconds
- ValidateFile_10MBFile_CompletesWithin5Seconds
- ValidateFile_50MBFile_CompletesWithin15Seconds
- ValidateFile_100ConcurrentRequests_AllCompleteWithin10Seconds
- ValidateFile_MemoryUsage_Below50MB
- ValidateFile_CPUUsage_Below80Percent
- DatabaseQuery_1000Records_CompletesWithin1Second
- BlobUpload_10MBFile_CompletesWithin3Seconds
- EndToEndWorkflow_CompleteValidation_CompletesWithin10Seconds
- LoadTest_1000RequestsPerMinute_NoErrors
```

**Performance Baselines (from current ASMX):**
- Current: 2-5 sec validation time, 50 MB memory
- Target: 1-3 sec validation time, 30 MB memory (50% faster, 40% less memory)

**Coverage Target:**
- Overall: 90% across all layers
- PSFValidator: 95% (maintained from Phase 3)

**Gate:** Cannot deploy to Test if coverage < 90% OR performance < baseline

---

### Phase 5a: Schema Validation (Mandatory Gate)
**Deadline:** Week 9  
**Focus:** 100% schema compatibility before integration tests

**Required Tests (35 schema tests):**
```csharp
// Schema Validation Tests
SchemaValidationTests.cs
- PAF_Record_19Fields_AllValidate
- PAI_Record_8Fields_AllValidate
- PRF_Record_17Fields_AllValidate
- PRI_Record_Fields_AllValidate
- PAH_Record_Fields_AllValidate
- PFL_Record_Fields_AllValidate
- PFH_Record_Fields_AllValidate
- PTF_Record_Fields_AllValidate
- PTH_Record_Fields_AllValidate
- FixedWidth_Format_ParsedCorrectly
- Delimited_Format_ParsedCorrectly
- XML_Format_ParsedCorrectly
- UTF8_Encoding_HandledCorrectly
- ANSI_Encoding_HandledCorrectly
- SpecialCharacters_EscapedCorrectly
- ErrorType1_InvalidRecordType_Detected
- ErrorType2_InvalidFormat_Detected
- ErrorType3_EmptyFile_Detected
- ErrorType4_ExceedsMaxLines_Detected
- ErrorType5_InvalidHeader_Detected
- ErrorType6_MissingData_Detected
- ErrorType7_InvalidDataFormat_Detected
- ErrorType8_InvalidDate_Detected
- ErrorType9_InvalidNumeric_Detected
- ErrorType10_InvalidCurrency_Detected
- ErrorType11_DuplicateRecord_Detected
- ErrorType12_InvalidChecksum_Detected
- ErrorType13_InvalidControlTotal_Detected
- ErrorType14_UnknownRecordType_Detected
- AllRecordTypes_SingleFile_AllValidate
- MixedEncodings_SingleFile_DetectedAndHandled
- LargeFile_10000Records_AllValidate
- CorruptFile_PartialData_GracefullyHandled
- EmptyRecords_SkippedOrReported
- CommentLines_IgnoredCorrectly
```

**Gate:** MUST achieve 100% schema validation (BLOCKER-003 prevention)  
**Blocker Prevention:** BLOCKER-003 from RA migration (schema validation afterthought)

---

## 🔴 TDD Workflow (RED→GREEN→REFACTOR)

**Mandatory Process (Enforced by CORTEX SKULL Rule):**

### RED Phase: Test Fails First
```csharp
// Step 1: Write failing test
[Fact]
public void ValidateFile_InvalidRecordType_ReturnsErrorType1()
{
    // Arrange
    var validator = new PSFValidator();
    var fileStream = CreateTestFile("INVALID_RECORD_TYPE");
    
    // Act
    var result = validator.ParseAndValidatePsfFile(fileStream);
    
    // Assert
    Assert.False(result.IsValid);
    Assert.Equal(ErrorType.InvalidRecordType, result.ErrorType);
    Assert.Equal("1", result.ErrorCode); // ERROR TYPE 1
}

// Step 2: Run test - MUST FAIL
// dotnet test --filter "ValidateFile_InvalidRecordType_ReturnsErrorType1"
// Expected: Test Explorer shows RED
```

**Validation:**
- Test MUST fail before any implementation
- If test passes immediately → BUG (test not testing anything)
- RED phase validates test correctness

---

### GREEN Phase: Minimal Implementation
```csharp
// Step 3: Write minimal code to pass test
public class PSFValidator
{
    public ValidationResult ParseAndValidatePsfFile(Stream fileStream)
    {
        using var reader = new StreamReader(fileStream);
        var firstLine = reader.ReadLine();
        
        // Minimal logic to pass test
        if (!IsValidRecordType(firstLine))
        {
            return new ValidationResult
            {
                IsValid = false,
                ErrorType = ErrorType.InvalidRecordType,
                ErrorCode = "1"
            };
        }
        
        return new ValidationResult { IsValid = true };
    }
    
    private bool IsValidRecordType(string line)
    {
        var validTypes = new[] { "PAF", "PAI", "PRF", "PRI", "PAH", "PFL", "PFH", "PTF", "PTH" };
        var recordType = line.Substring(0, 3);
        return validTypes.Contains(recordType);
    }
}

// Step 4: Run test - MUST PASS
// dotnet test --filter "ValidateFile_InvalidRecordType_ReturnsErrorType1"
// Expected: Test Explorer shows GREEN
```

**Validation:**
- Write ONLY enough code to pass test
- No extra features, no premature optimization
- GREEN phase validates implementation correctness

---

### REFACTOR Phase: Improve Code Quality
```csharp
// Step 5: Refactor for maintainability (tests still pass)
public class PSFValidator
{
    private static readonly HashSet<string> ValidRecordTypes = new()
    {
        "PAF", "PAI", "PRF", "PRI", "PAH", "PFL", "PFH", "PTF", "PTH"
    };
    
    public ValidationResult ParseAndValidatePsfFile(Stream fileStream)
    {
        using var reader = new StreamReader(fileStream);
        var firstLine = reader.ReadLine();
        
        if (!IsValidRecordType(firstLine))
        {
            return ValidationResult.Error(
                ErrorType.InvalidRecordType,
                "1",
                $"Invalid record type in line 1: {firstLine?.Substring(0, 3)}"
            );
        }
        
        return ValidationResult.Success();
    }
    
    private bool IsValidRecordType(string line)
    {
        if (string.IsNullOrEmpty(line) || line.Length < 3)
            return false;
            
        return ValidRecordTypes.Contains(line.Substring(0, 3));
    }
}

// Step 6: Run ALL tests - MUST PASS
// dotnet test
// Expected: All tests GREEN after refactor
```

**Validation:**
- Tests still pass after refactoring
- Code cleaner, more maintainable
- REFACTOR phase validates design quality

---

## 📊 Coverage Reporting

**Tools:**
```powershell
# Install coverage tools
dotnet tool install -g dotnet-reportgenerator-globaltool

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage"

# Generate HTML report
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coveragereport -reporttypes:Html

# Open report
Start-Process coveragereport/index.html
```

**Coverage Thresholds (configured in `Directory.Build.props`):**
```xml
<PropertyGroup>
  <CoverageThreshold_Line>90</CoverageThreshold_Line>
  <CoverageThreshold_Branch>80</CoverageThreshold_Branch>
  <CoverageThreshold_Method>90</CoverageThreshold_Method>
</PropertyGroup>
```

**CI/CD Integration (Azure DevOps):**
```yaml
- task: DotNetCoreCLI@2
  displayName: 'Run tests with coverage'
  inputs:
    command: 'test'
    projects: '**/*Tests.csproj'
    arguments: '--configuration Release --collect:"XPlat Code Coverage"'
    
- task: PublishCodeCoverageResults@1
  displayName: 'Publish coverage report'
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
    failIfCoverageEmpty: true
    
- script: |
    dotnet tool install -g dotnet-reportgenerator-globaltool
    reportgenerator -reports:$(Agent.TempDirectory)/**/coverage.cobertura.xml -targetdir:$(Build.SourcesDirectory)/coveragereport -reporttypes:"HtmlInline_AzurePipelines;Cobertura"
  displayName: 'Generate coverage report'
  
- task: PublishPipelineArtifact@1
  inputs:
    targetPath: '$(Build.SourcesDirectory)/coveragereport'
    artifact: 'CodeCoverageReport'
```

---

## 🧩 Test Organization

**Project Structure:**
```
cortex/modernized/
├── src/
│   ├── PSFPrevalidation.Api/
│   ├── PSFPrevalidation.Core/
│   ├── PSFPrevalidation.Infrastructure/
│   └── PSFPrevalidation.Shared/
└── tests/
    ├── PSFPrevalidation.UnitTests/          # 70 tests (55%)
    │   ├── Validators/
    │   │   ├── PSFValidatorTests.cs        # 20 tests
    │   │   ├── PAFRecordValidatorTests.cs  # 10 tests
    │   │   └── ... (other validators)
    │   ├── Models/
    │   │   ├── ValidationResultTests.cs
    │   │   └── ... (domain models)
    │   └── Parsers/
    │       ├── FixedWidthParserTests.cs
    │       └── ... (file parsers)
    ├── PSFPrevalidation.ComponentTests/     # 35 tests (25%)
    │   ├── Services/
    │   │   ├── PrevalidationServiceTests.cs
    │   │   └── WorkflowServiceTests.cs
    │   └── Repositories/
    │       ├── PrevalidationRepositoryTests.cs
    │       └── MockPrevalidationRepositoryTests.cs
    ├── PSFPrevalidation.IntegrationTests/   # 20 tests (15%)
    │   ├── Api/
    │   │   ├── PrevalidationApiIntegrationTests.cs
    │   │   └── ContractCompatibilityTests.cs
    │   ├── Database/
    │   │   ├── OracleIntegrationTests.cs
    │   │   └── EFCoreIntegrationTests.cs
    │   └── Performance/
    │       ├── PerformanceTests.cs
    │       └── LoadTests.cs
    └── PSFPrevalidation.E2ETests/           # 5 tests (5%)
        ├── FullWorkflowTests.cs
        ├── BlueGreenDeploymentTests.cs
        └── RollbackTests.cs
```

**Test Naming Convention:**
```csharp
// Pattern: {MethodName}_{Scenario}_{ExpectedBehavior}
[Fact]
public void ParseAndValidatePsfFile_ValidPAFRecord_ReturnsSuccess() { }

[Fact]
public void ParseAndValidatePsfFile_InvalidRecordType_ReturnsErrorType1() { }

[Fact]
public void ParseAndValidatePsfFile_EmptyFile_ReturnsErrorType3() { }
```

---

## 🎯 Phase-by-Phase Test Deliverables

| Phase | Tests | Coverage | Duration | Gate Criteria |
|-------|-------|----------|----------|---------------|
| Phase 3 | 30 unit tests | 60% | Week 4-5 | 60% coverage, all tests pass |
| Phase 4 | +40 component tests | 75% | Week 6-7 | 75% coverage, all tests pass |
| Phase 4a | +25 contract tests | - | Week 6 | 100% contract compatibility |
| Phase 5 | +30 integration tests | 90% | Week 8-10 | 90% coverage, performance baseline |
| Phase 5a | +35 schema tests | - | Week 9 | 100% schema validation |
| Phase 6 | +5 E2E tests | 90% | Week 11 | All 130 tests pass |

**Total:** 130 tests, 90-95% coverage (matches RA migration success)

---

## 📚 Related Documents

- [Master Plan](MODERNIZATION-PLAN.md) - Overall project plan
- [Risk Register](risk-register.md) - Testing risks (RISK-004)
- [API Contract Mapping](asmx-rest-contract-mapping.md) - Contract test scenarios
- [Lessons Learned](prevalidation-ws-migration-lessons-learned-plan.md) - LS-01 to LS-10

---

**Owner:** QA Lead + Technical Lead  
**Last Updated:** Phase 0 (Before Implementation)
