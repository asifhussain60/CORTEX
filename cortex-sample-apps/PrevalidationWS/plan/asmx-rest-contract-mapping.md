# API Contract Mapping - ASMX to REST

**Document Type:** Contract Specification  
**Author:** Asif Hussain  
**Date:** December 13, 2025  
**Version:** 1.0  
**Parent Plan:** [MODERNIZATION-PLAN.md](../MODERNIZATION-PLAN.md)  
**Related:** [Current State Analysis](../analysis/current-state-analysis.md)

---

## 🎯 Purpose

Define 100% backward-compatible REST API contracts mapped from legacy ASMX web service operations. This document ensures zero functionality loss during migration.

---

## 📋 Contract Mapping Summary

| ASMX Operation | REST Endpoint | HTTP Method | Compatibility |
|----------------|---------------|-------------|---------------|
| ValidatePSFFileWLogging | `/api/v1/prevalidations/validate` | POST | 100% |
| ValidatePSFFileWorkFlow | `/api/v1/prevalidations/validate-workflow` | POST | 100% |
| ValidatePSFFileWorkFlowWithFileID | `/api/v1/prevalidations/validate-workflow/{fileId}` | POST | 100% |
| ValidatePSFFileWithoutLogging | `/api/v1/prevalidations/validate-without-logging` | POST | 100% |
| ValidatePSFCustomFile | `/api/v1/prevalidations/validate-custom` | POST | 100% |
| N/A | `/api/v1/prevalidations/health` | GET | New |

---

## 🔄 Operation 1: ValidatePSFFileWLogging

### ASMX Contract (Legacy)

```csharp
[WebMethod]
public PSFPrevalResult ValidatePSFFileWLogging(int EmployerID, string FileName, string UserLogin)
{
    // Implementation
}

// Request (SOAP)
<ValidatePSFFileWLogging xmlns="http://tempuri.org/">
    <EmployerID>12345</EmployerID>
    <FileName>PSF_D12345_20251213.txt</FileName>
    <UserLogin>jsmith</UserLogin>
    <Attachments>
        <DIME attachment with file content>
    </Attachments>
</ValidatePSFFileWLogging>

// Response (SOAP)
<ValidatePSFFileWLoggingResponse xmlns="http://tempuri.org/">
    <ValidatePSFFileWLoggingResult>
        <ParseResult>NoCriticalDataError</ParseResult>
        <ErrorMessage></ErrorMessage>
        <CriticalErrorCount>0</CriticalErrorCount>
        <MaxBadRecords>100</MaxBadRecords>
        <FieldsBeyondLayoutFlag>false</FieldsBeyondLayoutFlag>
    </ValidatePSFFileWLoggingResult>
</ValidatePSFFileWLoggingResponse>
```

### REST Contract (Modern)

```
POST /api/v1/prevalidations/validate
Content-Type: multipart/form-data
Authorization: Bearer <token>

Request Body (multipart/form-data):
--boundary
Content-Disposition: form-data; name="employerId"

12345
--boundary
Content-Disposition: form-data; name="userLogin"

jsmith
--boundary
Content-Disposition: form-data; name="file"; filename="PSF_D12345_20251213.txt"
Content-Type: text/plain

<file content>
--boundary--

Response (200 OK):
{
    "parseResult": "NoCriticalDataError",
    "errorMessage": "",
    "criticalErrorCount": 0,
    "maxBadRecords": 100,
    "fieldsBeyondLayoutFlag": false
}

Error Response (400 Bad Request):
{
    "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
    "title": "One or more validation errors occurred.",
    "status": 400,
    "errors": {
        "employerId": ["The employerId field is required."]
    }
}
```

### Field Mapping

| ASMX Field | REST Field | Data Type | Transformation |
|------------|-----------|-----------|----------------|
| EmployerID | employerId | int → number | PascalCase → camelCase |
| FileName | file (form field name) | string → string | Extracted from multipart |
| UserLogin | userLogin | string → string | PascalCase → camelCase |
| Attachment (DIME) | file (multipart) | byte[] → Stream | DIME → multipart/form-data |
| ParseResult (enum) | parseResult | PSFParseResult → string | Enum → string (JSON) |
| ErrorMessage | errorMessage | string → string | PascalCase → camelCase |
| CriticalErrorCount | criticalErrorCount | int → number | PascalCase → camelCase |
| MaxBadRecords | maxBadRecords | int → number | PascalCase → camelCase |
| FieldsBeyondLayoutFlag | fieldsBeyondLayoutFlag | bool → boolean | PascalCase → camelCase |

### Business Logic Mapping

| ASMX Logic | REST Logic | Notes |
|-----------|-----------|-------|
| GetAgentId() from SOAP context | Extract from JWT claims | UsernameToken → Bearer token |
| File archiving (ArchiveService) | Same, async | Keep existing integration |
| File registration (RegisterFile) | Same, async | Keep existing database calls |
| Logging (LoggingActivity) | Same, async | File Visibility integration |
| File movement (success/error folders) | Azure Blob Storage containers | File system → cloud storage |
| Error log file creation | Application Insights logging | File → structured logging |

---

## 🔄 Operation 2: ValidatePSFFileWorkFlow

### ASMX Contract (Legacy)

```csharp
[WebMethod]
public PSFPrevalResult ValidatePSFFileWorkFlow(string FileName)
{
    // Implementation
}

// Request (SOAP)
<ValidatePSFFileWorkFlow xmlns="http://tempuri.org/">
    <FileName>PSF_D12345_20251213.txt</FileName>
</ValidatePSFFileWorkFlow>

// Response - Same as Operation 1
```

### REST Contract (Modern)

```
POST /api/v1/prevalidations/validate-workflow
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
    "fileName": "PSF_D12345_20251213.txt"
}

Response (200 OK):
{
    "parseResult": "NoCriticalDataError",
    "errorMessage": "",
    "criticalErrorCount": 0,
    "maxBadRecords": 100,
    "fieldsBeyondLayoutFlag": false
}
```

### Field Mapping

| ASMX Field | REST Field | Data Type | Transformation |
|------------|-----------|-----------|----------------|
| FileName | fileName | string → string | PascalCase → camelCase |
| (Derived from filename) | employerId | int → number | Parsed from filename |

### Business Logic Mapping

| ASMX Logic | REST Logic | Notes |
|-----------|-----------|-------|
| GetEmployerID(fileName) | Parse from fileName | Regex extraction: `D?(\d+)` |
| File read from PSFPickupLocation | Azure Blob Storage read | Pickup container |
| AddToMsgQueue (if FieldsBeyondLayout) | Azure Service Bus | Message queue |

---

## 🔄 Operation 3: ValidatePSFFileWorkFlowWithFileID

### ASMX Contract (Legacy)

```csharp
[WebMethod]
public PSFPrevalResult ValidatePSFFileWorkFlowWithFileID(string FileName, int FileID)
{
    // Implementation
}
```

### REST Contract (Modern)

```
POST /api/v1/prevalidations/validate-workflow/{fileId}
Content-Type: application/json
Authorization: Bearer <token>

Path Parameters:
- fileId: integer (required)

Request Body:
{
    "fileName": "PSF_D12345_20251213.txt"
}

Response (200 OK):
{
    "parseResult": "NoCriticalDataError",
    "errorMessage": "",
    "criticalErrorCount": 0,
    "maxBadRecords": 100,
    "fieldsBeyondLayoutFlag": false
}
```

### Field Mapping

| ASMX Field | REST Field | Data Type | Transformation |
|------------|-----------|-----------|----------------|
| FileName | fileName | string → string | PascalCase → camelCase |
| FileID | fileId | int → number (path param) | PascalCase → camelCase |

---

## 🔄 Operation 4: ValidatePSFFileWithoutLogging

### ASMX Contract (Legacy)

```csharp
[WebMethod]
public PSFPrevalResult ValidatePSFFileWithoutLogging(string FileName)
{
    // DIME attachment required
}
```

### REST Contract (Modern)

```
POST /api/v1/prevalidations/validate-without-logging
Content-Type: multipart/form-data
Authorization: Bearer <token>

Request Body (multipart/form-data):
--boundary
Content-Disposition: form-data; name="file"; filename="PSF_D12345_20251213.txt"
Content-Type: text/plain

<file content>
--boundary--

Response (200 OK):
{
    "parseResult": "NoCriticalDataError",
    "errorMessage": "",
    "criticalErrorCount": 0,
    "maxBadRecords": 100,
    "fieldsBeyondLayoutFlag": false
}
```

### Business Logic Mapping

| ASMX Logic | REST Logic | Notes |
|-----------|-----------|-------|
| Save file to PSFERDropLocation | Save to memory stream | No file persistence |
| Validate file | Same validation logic | No logging, no archiving |
| Delete file after validation | No file saved | Skip delete |

---

## 🔄 Operation 5: ValidatePSFCustomFile

### ASMX Contract (Legacy)

```csharp
[WebMethod]
public PSFPrevalResult ValidatePSFCustomFile(string FileName, int FileMapID)
{
    // Implementation
}
```

### REST Contract (Modern)

```
POST /api/v1/prevalidations/validate-custom
Content-Type: application/json
Authorization: Bearer <token>

Request Body:
{
    "fileName": "CUSTOM_D12345_20251213.txt",
    "fileMapId": 5
}

Response (200 OK):
{
    "parseResult": "NoCriticalDataError",
    "errorMessage": "",
    "criticalErrorCount": 0,
    "maxBadRecords": 100,
    "fieldsBeyondLayoutFlag": false
}
```

### Field Mapping

| ASMX Field | REST Field | Data Type | Transformation |
|------------|-----------|-----------|----------------|
| FileName | fileName | string → string | PascalCase → camelCase |
| FileMapID | fileMapId | int → number | PascalCase → camelCase |

### Business Logic Mapping

| ASMX Logic | REST Logic | Notes |
|-----------|-----------|-------|
| Read from PSFCustomPickupLocation | Azure Blob Storage (custom container) | Custom file layout |
| GetCustEmployerID(fileName) | Parse from fileName | Different format: position 2 |
| ParseAndValidateCustomPSFFile | Custom validation with FileMapID | Dynamic schema |

---

## 🆕 Operation 6: Health Check (New)

### REST Contract (Modern)

```
GET /api/v1/prevalidations/health
Authorization: Bearer <token> (optional)

Response (200 OK):
{
    "status": "Healthy",
    "checks": {
        "database": "Healthy",
        "blobStorage": "Healthy",
        "archiveService": "Healthy",
        "messageQueue": "Healthy"
    },
    "timestamp": "2025-12-13T10:30:00Z"
}

Response (503 Service Unavailable):
{
    "status": "Unhealthy",
    "checks": {
        "database": "Unhealthy",
        "blobStorage": "Healthy",
        "archiveService": "Degraded",
        "messageQueue": "Healthy"
    },
    "timestamp": "2025-12-13T10:30:00Z"
}
```

---

## 📊 Data Type Mappings

### Enum Mappings

```csharp
// ASMX (C# enum)
public enum PSFParseResult 
{
    CriticalFileError,       // 0
    ManyCriticalDataError,   // 1
    SomeCriticalDataError,   // 2
    NoCriticalDataError      // 3
}

// REST (JSON string)
{
    "parseResult": "CriticalFileError"  // String representation
}
```

**Serialization:**
```csharp
[JsonConverter(typeof(StringEnumConverter))]
public PSFParseResult ParseResult { get; set; }
```

### Date/Time Mappings

```csharp
// ASMX (DateTime)
DateTime.Now  // "12/13/2025 10:30:00 AM"

// REST (ISO 8601)
"2025-12-13T10:30:00Z"
```

---

## 🔐 Authentication/Authorization Mapping

### ASMX (WSE 2.0 UsernameToken)

```xml
<wsse:Security>
    <wsse:UsernameToken>
        <wsse:Username>jsmith</wsse:Username>
        <wsse:Password Type="PasswordText">***</wsse:Password>
    </wsse:UsernameToken>
</wsse:Security>
```

### REST (JWT Bearer Token)

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

JWT Claims:
{
    "sub": "jsmith",
    "name": "John Smith",
    "employerId": "12345",
    "roles": ["PSFValidator"],
    "exp": 1702468200
}
```

---

## 📝 Error Response Mappings

### ASMX (SOAP Fault)

```xml
<soap:Fault>
    <faultcode>soap:Server</faultcode>
    <faultstring>File was not uploaded successfully! Please try again.</faultstring>
    <detail>
        <Exception>
            <Message>File was not uploaded successfully! Please try again.</Message>
        </Exception>
    </detail>
</soap:Fault>
```

### REST (RFC 7807 Problem Details)

```json
{
    "type": "https://api.company.com/errors/file-upload-failed",
    "title": "File Upload Failed",
    "status": 400,
    "detail": "File was not uploaded successfully! Please try again.",
    "instance": "/api/v1/prevalidations/validate",
    "traceId": "00-4bf92f3577b34da6a3ce929d0e0e4736-00"
}
```

---

## 🧪 Contract Verification Test Plan

### Test Scenarios (100+ Required)

| Scenario | ASMX Input | REST Input | Expected Match |
|----------|-----------|-----------|----------------|
| Happy path - No errors | EmployerID=12345, valid PSF file | employerId=12345, valid file | 100% |
| Critical file error | Binary file | Binary file | 100% |
| Many critical data errors | 101+ errors | 101+ errors | 100% |
| Missing SSN | Row with blank SSN | Row with blank SSN | 100% |
| Invalid date | Invalid date format | Invalid date format | 100% |
| Trailer missing | No trailer record | No trailer record | 100% |
| Fields beyond layout | Extra fields | Extra fields | 100% |
| Custom file map | FileMapID=5 | fileMapId=5 | 100% |

### Automated Test Framework

```csharp
[Fact]
public async Task ValidateFile_HappyPath_MatchesAsmxBehavior()
{
    // Arrange
    var testFile = CreateTestPsfFile(scenarioName: "HappyPath");
    
    // Act - Invoke ASMX
    var asmxResult = await _asmxProxy.ValidatePSFFileWLoggingAsync(
        employerId: 12345,
        fileName: "PSF_D12345_20251213.txt",
        userLogin: "jsmith",
        fileContent: testFile
    );
    
    // Act - Invoke REST
    var restResponse = await _restClient.PostAsync("/api/v1/prevalidations/validate", 
        CreateMultipartFormData(
            employerId: 12345,
            userLogin: "jsmith",
            file: testFile
        )
    );
    var restResult = await restResponse.Content.ReadFromJsonAsync<PSFPrevalResult>();
    
    // Assert - 100% contract match
    var comparison = _validator.CompareResults(asmxResult, restResult);
    comparison.IsMatch.Should().BeTrue("100% contract compatibility required");
    comparison.Differences.Should().BeEmpty();
    
    // Assert - Specific fields
    restResult.ParseResult.Should().Be(asmxResult.ParseResult);
    restResult.CriticalErrorCount.Should().Be(asmxResult.CriticalErrorCount);
    restResult.ErrorMessage.Should().Be(asmxResult.ErrorMessage);
}
```

---

## 📋 Implementation Checklist

### Phase 1: Contract Definition
- [x] Document all ASMX operations
- [x] Define REST endpoint mappings
- [x] Create request/response DTOs
- [x] Define error response formats

### Phase 2: DTO Implementation
- [ ] Create `ValidateFileRequest` DTO
- [ ] Create `ValidateFileWorkflowRequest` DTO
- [ ] Create `ValidateCustomFileRequest` DTO
- [ ] Create `PSFPrevalResult` DTO
- [ ] Add JSON serialization attributes
- [ ] Add FluentValidation validators

### Phase 3: Controller Stubs
- [ ] Create `PrevalidationController`
- [ ] Implement all 6 endpoints (stubs)
- [ ] Add Swagger documentation
- [ ] Add request/response examples

### Phase 4: Contract Tests
- [ ] Implement 100+ test scenarios
- [ ] Create ASMX proxy wrapper
- [ ] Create REST client wrapper
- [ ] Implement contract validator
- [ ] Achieve 100% match rate

---

## 🚀 Next Steps

1. ✅ Review this contract mapping with stakeholders
2. ✅ Begin Phase 1 (Foundation & Infrastructure)
3. ✅ Implement DTOs in `PSFPrevalidation.Core/Contracts/`
4. ✅ Create controller stubs in `PSFPrevalidation.API/Controllers/`

---

**Prepared By:** CORTEX AI Assistant  
**Date:** December 13, 2025  
**Classification:** Internal - Contract Specification  
**Status:** 📋 READY FOR REVIEW
