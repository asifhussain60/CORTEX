# Account Funding Invoices — Modernized REST API

**Updated:** 2026-02-22 | **Source:** WCF Legacy `GCInteraction` Services  
**Runtime:** .NET 8 | **Pattern:** Clean Architecture + EF Core + Azure Services

---

## What This Application Does

Manages **reimbursement account (RA) funding invoices** — the financial records that track employer
and employee contributions to HSA/FSA/HRA accounts. Migrated from three legacy WCF transactions:

| Legacy WCF Class | REST Endpoint | Operation |
|---|---|---|
| `XAddFundingInvoice.cs` | `POST /api/v1/funding-invoices` | Create payroll-based funding invoice |
| `XGenerateFundingInvoice.cs` | `POST /api/v1/funding-invoices/generate` | Generate on-demand invoice (peg logic) |
| `Updater_CreateAccountFundingInvoices.cs` | `POST /api/v1/funding-invoices/batch` | Batch create invoices for multiple subaccounts |
| `XUpdateFundingBatch.cs` | `PUT /api/v1/funding-batches/{batchId}` | Update batch status |

---

## Domain Model

```mermaid
classDiagram
    class FundingBatch {
        +string BatchId
        +string BatchNumber
        +DateTime BatchDate
        +string Status
        +decimal TotalAmount
        +int InvoiceCount
        +string CreatedBy
    }
    class FundingInvoice {
        +string InvoiceId
        +string BatchId
        +string SubaccountId
        +string InvoiceNumber
        +decimal Amount
        +string Status
        +DateTime InvoiceDate
        +DateTime DueDate
        +string CreatedBy
    }
    class Subaccount {
        +string SubaccountId
        +string AccountNumber
        +string AccountType
        +string MemberId
        +decimal Balance
        +string Status
        +DateTime OpenedDate
    }
    class CashInOut {
        +string TransactionId
        +string BatchId
        +string TransactionType
        +decimal Amount
        +DateTime TransactionDate
        +string Status
        +string ReferenceNumber
    }
    FundingBatch "1" --> "many" FundingInvoice : contains
    FundingInvoice "many" --> "1" Subaccount : belongs to
    FundingBatch "1" --> "many" CashInOut : tracks
```

---

## API Reference

### POST `/api/v1/funding-invoices`
Creates a payroll-based funding invoice for a single subaccount.

**Request:**
```json
{
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "reimbursementPlanId": "RP-001",
  "employerFundingDefault": 500.00,
  "employeeFundingDefault": 250.00,
  "effectiveDate": "2026-01-15T00:00:00Z",
  "invoiceDescription": "Payroll funding Q1",
  "isLSA": false,
  "createdBy": "payroll-system"
}
```

**Response `201 Created`:**
```json
{
  "invoiceId": "INV-2026-001",
  "batchId": "BATCH-001",
  "subaccountId": "SA-001",
  "invoiceNumber": "FI-20260115-001",
  "amount": 750.00,
  "status": "Pending"
}
```

---

### POST `/api/v1/funding-invoices/generate`
Generates an on-demand invoice only if subaccount balance is below the peg amount.

**Business Rule:** If `balance < invoiceAmount`, create invoice. Otherwise return `"not needed"`.

**Request:**
```json
{
  "subaccountId": "SA-001",
  "invoiceAmount": 500.00,
  "invoiceDate": "2026-01-15T00:00:00Z",
  "createdBy": "system"
}
```

**Response `200 OK`:**
```json
{
  "result": "invoice created",
  "invoiceId": "INV-2026-002",
  "cashInOutId": "CIO-001"
}
```

---

### POST `/api/v1/funding-invoices/batch`
Creates funding invoices for multiple subaccounts in a single batch operation.
Handles partial success — failed subaccounts are reported without rolling back successes.

**Request:**
```json
{
  "cashInOutId": "CIO-BATCH-001",
  "subaccountIds": ["SA-001", "SA-002", "SA-003"],
  "employerFundingAmount": 500.00,
  "createdBy": "payroll-system"
}
```

**Response `201 Created`:**
```json
{
  "successCount": 2,
  "failureCount": 1,
  "failedSubaccounts": ["SA-002"]
}
```

---

## Architecture

```mermaid
graph TD
    Client -->|HTTP| API[Account.FundingInvoices.API]
    API --> Core[Account.FundingInvoices.Core]
    API --> Infra[Account.FundingInvoices.Infrastructure]

    subgraph API Layer
        Ctrl1[FundingInvoiceController]
        Ctrl2[FundingBatchController]
        MW[Middleware Stack]
    end

    subgraph Core Layer
        Svc1[IFundingInvoiceService]
        Svc2[IFundingBatchService]
        Repo1[IFundingInvoiceRepository]
        Repo2[IFundingBatchRepository]
        Repo3[ISubaccountRepository]
        Repo4[ICashInOutRepository]
        UoW[IUnitOfWork]
        Validators
        DTOs
    end

    subgraph Infrastructure Layer
        EFCtx[TransactionInvoicesDbContext]
        EFRepo1[EFCoreFundingInvoiceRepository]
        EFRepo2[EFCoreFundingBatchRepository]
        Mock[Mock Repositories]
        Router[DataLayerRouter]
        Encrypt[AzureKeyVaultEncryptionService]
        Feature[AzureAppConfigFeatureFlagService]
    end

    Ctrl1 --> Svc1
    Ctrl2 --> Svc2
    Svc1 --> Repo1
    Svc1 --> Repo3
    Svc1 --> Repo4
    Svc2 --> Repo2
    Router --> EFRepo1
    Router --> Mock
    Feature --> Router
```

---

## Middleware Stack

| Middleware | Purpose |
|---|---|
| `AuditLoggingMiddleware` | Records all API calls for HIPAA audit trail |
| `DataEncryptionMiddleware` | Encrypts/decrypts PHI fields via Azure Key Vault |
| `MetricsMiddleware` | Emits latency and throughput metrics to Application Insights |
| `ProblemDetailsMiddleware` | Normalises all errors to RFC 7807 `ProblemDetails` format |

---

## Canary Deployment

The `DataLayerRouter` implements progressive rollout from Mock → EF Core repositories:

```mermaid
stateDiagram-v2
    [*] --> MockLayer: Initial Deploy (0% real traffic)
    MockLayer --> Canary: Feature flag enabled (10%)
    Canary --> Progressive: Metrics healthy (10% → 25% → 50%)
    Progressive --> Production: 100% EF Core
    Canary --> Rollback: Error rate > threshold
    Progressive --> Rollback: Latency P99 > 500ms
    Rollback --> MockLayer: Auto-reverted
```

---

## Running Locally

```bash
# Restore dependencies
dotnet restore

# Build
dotnet build

# Run unit tests
dotnet test tests/Account.FundingInvoices.UnitTests/

# Run integration tests
dotnet test tests/Account.FundingInvoices.IntegrationTests/

# Start API (development mode — uses Mock repositories)
dotnet run --project src/Account.FundingInvoices.API/

# API available at: http://localhost:5000/api/v1/
# Swagger UI: http://localhost:5000/swagger
```

---

## Test Coverage

| Layer | Test Project | Key Areas |
|---|---|---|
| Unit | `Account.FundingInvoices.UnitTests` | Services, validators, mock repos, encryption, metrics, feature flags |
| Integration | `Account.FundingInvoices.IntegrationTests` | EF Core repos, schema validation, feature flag integration, rollback monitoring |

---

## Related Specifications

- [OpenAPI Spec — Batch Create](../account-api-specs/specifications/updater-createrafundinginvoices/openapi.yaml)
- [OpenAPI Spec — Generate Invoice](../account-api-specs/specifications/xgeneratefundinginvoice/openapi.yaml)
- [Sequence Diagram — Batch Create](../account-api-specs/specifications/updater-createrafundinginvoices/diagrams/sequence.mmd)
- [Sequence Diagram — Generate Invoice](../account-api-specs/specifications/xgeneratefundinginvoice/diagrams/sequence.mmd)
