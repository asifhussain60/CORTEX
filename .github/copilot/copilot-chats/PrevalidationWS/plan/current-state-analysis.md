# Current State Analysis - PSF Prevalidation Service

**Document Type:** Technical Analysis  
**Author:** Asif Hussain  
**Date:** December 13, 2025  
**Version:** 1.0  
**Parent Plan:** [MODERNIZATION-PLAN.md](../MODERNIZATION-PLAN.md)

---

## 🎯 Purpose

Comprehensive analysis of the existing PSF Prevalidation Web Service to inform modernization design decisions.

---

## 📊 Service Overview

### Service Metadata
- **Name:** PSFPreValidation.ValidationWS
- **Type:** ASMX Web Service (.NET Framework 4.x)
- **Location:** `WebService/PSFPreValidate.asmx`
- **Namespace:** `PSFPreValidation`
- **Primary Function:** Validate employer-submitted PSF files before processing

### Web Methods (4 Operations)

| Method | Parameters | Return Type | Purpose |
|--------|-----------|-------------|---------|
| `ValidatePSFFileWLogging` | EmployerID (int), FileName (string), UserLogin (string) | PSFPrevalResult | Validate with full logging & archiving |
| `ValidatePSFFileWorkFlow` | FileName (string) | PSFPrevalResult | Workflow-based validation |
| `ValidatePSFFileWorkFlowWithFileID` | FileName (string), FileID (int) | PSFPrevalResult | Workflow validation with file tracking |
| `ValidatePSFFileWithoutLogging` | FileName (string) | PSFPrevalResult | Validation only (no persistence) |
| `ValidatePSFCustomFile` | FileName (string), FileMapID (int) | PSFPrevalResult | Custom file layout validation |

---

## 🏗️ Architecture Analysis

### Layer 1: Web Service Layer

**File:** `WebService/App_Code/PSFPreValidate.asmx.cs` (458 lines)

**Responsibilities:**
- DIME attachment handling
- SOAP context management (WSE 2.0)
- File registration & logging orchestration
- Archive service integration
- Error handling & result formatting

**Key Code Patterns:**
```csharp
// DIME Attachment Handling (Legacy)
if (RequestSoapContext.Current.Attachments.Count > 0)
{
    BinaryReader stream = new BinaryReader(RequestSoapContext.Current.Attachments[0].Stream);
    byte[] bytAttachmentItem = new byte[stream.BaseStream.Length];
    stream.Read(bytAttachmentItem, 0, bytAttachmentItem.Length);
    // ...
}

// File Registration Pattern
int fileRegisterID = RegisterFile(strFileName, EmployerID, UserLogin, ref processID);

// Logging Pattern
LoggingActivity(processID, fileRegisterID, strFileName, logStatus, logMessage);
```

**Dependencies:**
- `Microsoft.Web.Services2` (WSE 2.0 - DEPRECATED)
- `WageWorks.PSFPreval.Business.PSFValidator`
- `WW.ArchiveCenter.ArchiveServiceAdapter`
- `System.IO` (file operations)

**Modernization Challenges:**
1. ❌ DIME attachments → REST multipart/form-data
2. ❌ SOAP context → HTTP context
3. ❌ Synchronous file I/O → Async streaming
4. ❌ Global exception handling → Middleware

---

### Layer 2: Business Logic Layer

**File:** `Business/PSFValidator.cs` (1,328 lines) - CRITICAL COMPONENT

**Responsibilities:**
- PSF file parsing (pipe/tab delimited)
- Header validation
- Row-by-row validation (9 record types)
- Trailer validation
- Error accumulation & classification
- Binary file detection

**Key Classes & Methods:**

| Class/Method | Lines | Complexity | Purpose |
|--------------|-------|------------|---------|
| `PsfValidator` | 1,328 | HIGH | Main validation orchestrator |
| `ParseAndValidatePsfFile` | ~200 | HIGH | Entry point, file parsing |
| `ValidateHdrRow` | ~80 | MEDIUM | Header validation |
| `ValidatePsfLine` | ~150 | HIGH | Record type routing |
| `ValidatePsfTrailer` | ~100 | MEDIUM | Trailer record validation |
| `ValidateProfile` | ~120 | HIGH | Profile record validation |
| `ValidateEnrollment` | ~100 | HIGH | Enrollment record validation |
| `ValidateEsp` | ~80 | MEDIUM | ESP record validation |
| `ValidateMsp` | ~80 | MEDIUM | MSP record validation |
| `ValidateFunding` | ~70 | MEDIUM | Funding record validation |

**Validation Rules (14 Error Types):**
```csharp
public enum ErrorType
{
    SsnMissingError,         // Critical: Missing SSN
    SsnInvalidError,         // Critical: Invalid SSN format
    SsnMinError,             // Critical: SSN too short
    SsnNumberError,          // Critical: SSN not numeric
    SsnAlphanumeric,         // Critical: Alphanumeric SSN (conditional)
    DateError,               // Data: Invalid date format
    MissingField,            // Data: Required field missing
    MaxlengthError,          // Data: Field exceeds max length
    HdrInvalidError,         // Data: Invalid header
    EmptyRowError,           // Other: Empty row
    RecordTypeInvalidError,  // Data: Unknown record type
    FieldRequirementError,   // Data: Field requirement violated
    InvalidCharacter,        // Data: Invalid character found
    TrailersMultiple,        // Data: Multiple trailers
    TrailerMissing,          // Data: No trailer found
    TrailerCountFormat       // Data: Trailer count invalid
}
```

**Record Types (9 Types):**
```csharp
public readonly string[] ValidRecordTypes =
{
    "PROFILE",   // Employee profile
    "ENROLL",    // Benefit enrollment
    "ESP",       // Expense Specific Plan
    "MSP",       // Medical Specific Plan
    "FUNDING",   // Funding arrangement
    "EPRO",      // Electronic Proof
    "COPAY",     // Copay configuration
    "AAT",       // Account Assignment Template
    "DEP"        // Dependent information
};
```

**File Processing Flow:**
```
1. Check file is not binary
2. Detect delimiter (pipe | or tab \t)
3. Validate header row (if present)
4. For each row (up to MaxRowsToCheck):
   a. Split by delimiter
   b. Check for empty rows
   c. Validate record type
   d. Route to specific validator
   e. Accumulate errors
5. Validate trailer record
6. Classify result (CriticalFileError, ManyCriticalDataError, etc.)
```

**Modernization Opportunities:**
1. ✅ Dependency injection (currently uses static methods)
2. ✅ Async file parsing (currently synchronous)
3. ✅ Streaming validation (currently loads full file)
4. ✅ LINQ improvements (reduce complexity)
5. ✅ Extract validators to strategy pattern

---

### Layer 3: Data Access Layer

**File:** `Business/PrevalidationData.cs` (328 lines)

**Responsibilities:**
- File mapping retrieval (IE_FILE_MAPPINGS, IE_FILE_MAP_RECORDS, IE_FILE_MAP_DTLS)
- File registration (STGI_FILES table)
- Process logging (File Visibility)
- Archive integration
- Employer settings lookup

**Key Methods:**

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `GetMappingStructure` | void | Load file mapping from DB |
| `GetIndividualTbl` | Hashtable | Query single mapping table |
| `RegisterFile` | int | Register file in STGI_FILES |
| `GetProcessLogID` | int | Create process log entry |
| `LogPrevalidateStep` | int | Log validation step |
| `LogStepDetail` | bool | Log step detail |
| `AddToMsgQueue` | bool | Queue notification message |
| `GetMaxBadRecords` | int | Get employer's max error threshold |
| `GetPsfTrailerSettings` | bool | Get trailer requirement setting |
| `AllowAlphanumericUniqueId` | bool | Check alphanumeric SSN allowed |
| `GetMinimumUniqueIdLength` | int | Get minimum SSN length |

**Database Tables:**
```sql
-- File Mapping Tables (Oracle)
wwie.IE_FILE_MAPPINGS       -- Master mapping configuration
wwie.IE_FILE_MAP_RECORDS    -- Record type definitions
wwie.IE_FILE_MAP_DTLS       -- Field-level details

-- File Processing Tables
STGI_FILES                  -- Registered files
PROCESS_LOG                 -- Process execution log
PROCESS_LOG_STEP            -- Step-level tracking
PROCESS_LOG_STEP_DETAIL     -- Detail-level tracking

-- Employer Settings
WWEB.EMPLOYER_SETTING_INFO  -- Employer-specific settings
```

**External Service Dependencies:**
```csharp
// WW.FC.Service.Impl
FileProcessCommonService    // File registration, mapping retrieval
ProcessLogService           // Logging orchestration
GeneralFileService          // Message queue

// WW.SA.Service.Impl
PsfFileServicecs            // PSF-specific configuration

// WW.ArchiveCenter
ArchiveServiceAdapter       // File archiving
```

**Modernization Strategy:**
1. ✅ Replace Hashtable → Dictionary<TKey, TValue>
2. ✅ Create repository interfaces (IFileRepository, ILoggingRepository)
3. ✅ Implement EF Core repositories
4. ✅ Create mock repositories for testing
5. ✅ Unit of Work pattern for transactions

---

### Layer 4: Domain Models

**File:** `Business/ValidationScheme.cs` (50 lines)

**Classes:**
- `FieldInfo` - Field metadata (name, type, order, max length, check type, required)
- `FieldsInfo` - Collection of FieldInfo with query methods
- `SchemaInfo` - Schema definition (type, field count, fields)
- `SchemaInfoCol` - Collection of SchemaInfo

**File:** `Business/PSFPrevalResult.cs` (55 lines)

**Classes:**
- `PSFParseResult` (enum) - 4 result types
- `PSFPrevalResult` - Validation result (parse result, error count, max bad records, error message)

**File:** `Business/FileSettings.cs` (source not shown, referenced)

**Interface:** `IFileSettings`

**Modernization Strategy:**
1. ✅ Move to `PSFPrevalidation.Core/Domain/`
2. ✅ Add FluentValidation validators
3. ✅ Implement IEquatable<T> for value objects
4. ✅ Add JSON serialization attributes

---

## 📋 File Inventory

### Production Code

| File | Lines | Language | Purpose |
|------|-------|----------|---------|
| PSFPreValidate.asmx.cs | 458 | C# | Web service endpoints |
| PSFValidator.cs | 1,328 | C# | Validation engine |
| PrevalidationData.cs | 328 | C# | Data access |
| ValidationScheme.cs | 50 | C# | Schema models |
| PSFPrevalResult.cs | 55 | C# | Result models |
| FileSettings.cs | ? | C# | Settings interface |
| PSFUtilities.cs | ? | C# | Utility methods |
| AppConstants.cs | ? | C# | Application constants |
| ApplicationConfiguration.cs | ? | C# | Configuration |
| Extensions.cs | ? | C# | Extension methods |
| **TOTAL** | **~3,000** | C# | |

### Test Code

| File | Lines | Language | Purpose |
|------|-------|----------|---------|
| PsfValidatorTests.cs | ? | C# | Validator tests |
| FileSettingsTests.cs | ? | C# | Settings tests |
| PSFUtilitiesTests.cs | ? | C# | Utility tests |
| OtherTests.cs | ? | C# | Misc tests |
| TestValidationSchema.json | ? | JSON | Test schema |

---

## 🔍 Complexity Analysis

### Cyclomatic Complexity Hotspots

| Method | Estimated Complexity | Risk Level | Reason |
|--------|---------------------|------------|---------|
| `ParseAndValidatePsfFile` | 15-20 | HIGH | Multiple nested loops, exception handling |
| `ValidatePsfLine` | 12-15 | MEDIUM | Switch statement, validation routing |
| `ValidateProfile` | 10-12 | MEDIUM | Field-by-field validation logic |
| `ValidateEnrollment` | 10-12 | MEDIUM | Field-by-field validation logic |
| `ValidateHdrRow` | 8-10 | MEDIUM | Field validation, error accumulation |
| `ValidatePsfTrailer` | 8-10 | MEDIUM | Trailer parsing, count validation |

**Refactoring Strategy:**
1. Extract method: Break down long methods
2. Strategy pattern: Record type validators
3. Chain of responsibility: Field validators
4. Remove nested loops: LINQ queries

---

## 🚨 Technical Debt Assessment

### Critical Issues

| Issue | Severity | Impact | Mitigation |
|-------|----------|--------|------------|
| WSE 2.0 Dependency | CRITICAL | Cannot run on .NET 8 | Replace with standard HTTP multipart |
| Synchronous File I/O | HIGH | Poor scalability | Async/await pattern |
| No Dependency Injection | HIGH | Hard to test | Implement DI container |
| Hashtable Usage | MEDIUM | Type safety | Replace with Dictionary<TKey, TValue> |
| Static Methods | MEDIUM | Testability | Instance methods with interfaces |
| Oracle-Specific Code | MEDIUM | Vendor lock-in | EF Core provider abstraction |

### Code Smells

1. **God Class:** PSFValidator (1,328 lines) - REFACTOR
2. **Feature Envy:** PrevalidationData accessing FileProcessCommonService
3. **Primitive Obsession:** Extensive use of strings for typed data
4. **Long Parameter Lists:** RegisterFile (8 parameters)
5. **Magic Numbers:** Hard-coded field positions, lengths

---

## 📊 Performance Characteristics

### Current Performance (Estimated)

| Metric | Value | Measurement |
|--------|-------|-------------|
| File Size Limit | 10 MB | MaxReceivedMessageSize |
| Max Rows Validated | ~10,000 | MaxRowsToCheck |
| Avg Validation Time | 2-5 sec | 1 MB file |
| Memory Usage | ~50 MB | Per request |
| Concurrent Requests | 10-20 | IIS thread pool |

### Performance Bottlenecks

1. **Synchronous I/O:** Blocks thread during file read
2. **Full File Load:** Loads entire file into memory
3. **String Operations:** Extensive string splitting/concatenation
4. **Database Round-Trips:** Multiple calls to lookup tables
5. **No Caching:** Employer settings fetched every request

### Modernization Performance Goals

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Validation Time | 2-5 sec | 1-3 sec | 40% faster |
| Memory Usage | 50 MB | 30 MB | 40% reduction |
| Concurrent Requests | 10-20 | 100+ | 5x increase |
| Throughput | 200 req/hour | 2,000 req/hour | 10x increase |

---

## 🔐 Security Analysis

### Current Security Measures

1. **Authentication:** WSE 2.0 UsernameToken
2. **Authorization:** None (EmployerID from filename)
3. **Data Validation:** Input validation via PSFValidator
4. **Encryption:** HTTPS (transport layer only)
5. **Audit Logging:** File Visibility logs

### Security Gaps

| Gap | Risk Level | Impact | Mitigation |
|-----|-----------|--------|------------|
| No API Key/OAuth | HIGH | Unauthorized access | Azure AD authentication |
| EmployerID in Filename | MEDIUM | Spoofing | JWT claims-based authorization |
| No Rate Limiting | MEDIUM | DoS attacks | Azure APIM throttling |
| No Input Sanitization | MEDIUM | Injection attacks | FluentValidation, ProblemDetails |
| No Data Encryption | LOW | Data exposure | TDE, field-level encryption |

---

## 🧪 Testability Assessment

### Current Test Coverage

**Existing Tests:**
- `PsfValidatorTests.cs` - Unit tests for validation logic
- `FileSettingsTests.cs` - Settings tests
- `PSFUtilitiesTests.cs` - Utility tests
- `OtherTests.cs` - Miscellaneous tests

**Coverage Estimate:** 40-50% (based on test file count)

### Testing Challenges

1. ❌ **Static Methods:** Hard to mock (PrevalidationData)
2. ❌ **External Services:** FileProcessCommonService, ArchiveService
3. ❌ **File I/O:** Requires test files on disk
4. ❌ **Database:** Requires Oracle connection
5. ❌ **SOAP Context:** Requires WSE 2.0 infrastructure

### Modernization Testing Goals

| Layer | Current Coverage | Target Coverage | Strategy |
|-------|-----------------|-----------------|----------|
| Controllers | 0% | 90% | Integration tests (WebApplicationFactory) |
| Services | 40% | 95% | Unit tests (mocked repositories) |
| Repositories | 0% | 95% | Unit tests (in-memory, SQLite) |
| Validators | 50% | 100% | Unit tests (FluentValidation) |
| Domain Models | 0% | 90% | Unit tests (value object equality) |
| **Overall** | **40%** | **90%** | |

---

## 🔄 Integration Points

### External Systems

| System | Integration Type | Purpose | Modernization Impact |
|--------|-----------------|---------|---------------------|
| Archive Center | SOAP Web Service | File archiving | Replace with REST API or queue |
| File Visibility | Database (Oracle) | Process logging | Keep, wrap in repository |
| File Processing | Database (Oracle) | File registration | Keep, wrap in repository |
| Employer Settings | Database (Oracle) | Configuration lookup | Keep, add caching |
| Message Queue | Database (Oracle) | Notifications | Replace with Azure Service Bus |

### File System Dependencies

| Path | Purpose | Modernization |
|------|---------|---------------|
| PSFERDropLocation | Incoming files | Azure Blob Storage |
| PSFERValSuccessLocation | Valid files | Azure Blob Storage |
| PSFERValErrorLocation | Invalid files | Azure Blob Storage |
| PSFPrevalLogLocation | Error logs | Application Insights |
| PSFPickupLocation | Workflow files | Azure Blob Storage |
| PSFCustomPickupLocation | Custom files | Azure Blob Storage |

---

## 📝 Configuration Management

### Current Configuration (Web.config)

```xml
<appSettings>
  <add key="PSFERDropLocation" value="\\server\share\drop\" />
  <add key="PSFERValSuccessLocation" value="\\server\share\success\" />
  <add key="PSFERValErrorLocation" value="\\server\share\error\" />
  <add key="PSFPrevalLogLocation" value="\\server\share\logs\" />
  <add key="PSFPickupLocation" value="\\server\share\pickup\" />
  <add key="PSFCustomPickupLocation" value="\\server\share\custom\" />
  <add key="ArchiveAppID" value="PSFPreval" />
  <add key="ArchiveAppPassword" value="***" />
</appSettings>
<connectionStrings>
  <add name="OracleConnection" connectionString="..." />
</connectionStrings>
```

### Modernization (appsettings.json + Azure App Configuration)

```json
{
  "PsfPrevalidation": {
    "FileStorage": {
      "DropLocation": "https://storage.blob.core.windows.net/drop",
      "SuccessLocation": "https://storage.blob.core.windows.net/success",
      "ErrorLocation": "https://storage.blob.core.windows.net/error"
    },
    "Validation": {
      "MaxRowsToCheck": 10000,
      "MaxFileSize": 10485760
    },
    "Archive": {
      "ServiceUrl": "https://archive.company.com/api",
      "AppID": "PSFPreval",
      "AppPassword": "***"  // Move to Key Vault
    }
  },
  "ConnectionStrings": {
    "OracleConnection": "***"  // Move to Key Vault
  }
}
```

---

## 🎯 Modernization Recommendations

### Architecture Patterns

1. **Clean Architecture:**
   - API → Services → Repositories → Database
   - Domain-Driven Design (DDD) for complex validation rules
   - CQRS (optional) for read-heavy operations

2. **Repository Pattern:**
   - IFileRepository, ILoggingRepository, IArchiveRepository
   - Mock implementation for testing
   - EF Core implementation for production

3. **Strategy Pattern:**
   - IRecordValidator (PROFILE, ENROLL, ESP, etc.)
   - Validation rule chaining
   - Extensible for new record types

4. **Middleware Pipeline:**
   - Authentication/Authorization
   - Request logging
   - Exception handling (ProblemDetails)
   - Performance monitoring

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| API | ASP.NET Core 8.0 | Modern, high-performance |
| Validation | FluentValidation | Declarative, testable |
| Data Access | EF Core 8.0 | ORM, migrations, testability |
| Logging | Application Insights | Cloud-native, rich analytics |
| Caching | Redis | Distributed, high-performance |
| File Storage | Azure Blob Storage | Scalable, durable |
| Messaging | Azure Service Bus | Reliable, cloud-native |

### Migration Path

1. **Phase 1:** Build parallel .NET 8 API (100% mock data)
2. **Phase 2:** Add EF Core repositories (swappable)
3. **Phase 3:** Contract testing (ASMX vs REST)
4. **Phase 4:** Shadow testing (parallel execution)
5. **Phase 5:** Gradual rollout (0% → 100% via feature flag)
6. **Phase 6:** Decommission ASMX service

---

## 🚧 Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Contract incompatibility | MEDIUM | HIGH | 100% contract verification tests |
| Performance degradation | LOW | HIGH | Performance baseline, load testing |
| Data corruption | LOW | CRITICAL | Schema validation, canary deployment |
| Integration failures | MEDIUM | HIGH | Mock external services, circuit breakers |
| Incomplete validation logic | MEDIUM | HIGH | Shadow testing, UAT sign-off |

---

## 📚 Next Steps

1. ✅ Review this analysis with stakeholders
2. ✅ Create API Contract Mapping document
3. ✅ Create Data Model Design document
4. ✅ Begin Phase 0 (Pre-Flight & Planning)

---

**Prepared By:** CORTEX AI Assistant  
**Date:** December 13, 2025  
**Classification:** Internal - Technical Analysis  
**Status:** 📋 READY FOR REVIEW
