# API Reference Guide

**Version:** 1.0  
**Base URL:** `https://your-api.com/api/v1`  
**Authentication:** Bearer Token (JWT)  
**Format:** JSON (application/json)

---

## 📋 Quick Reference

### Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/funding-invoices` | POST | Create invoice | ✅ Yes |
| `/funding-invoices/{id}` | GET | Get invoice | ✅ Yes |
| `/funding-invoices` | GET | List invoices | ✅ Yes |
| `/funding-invoices/{id}` | PUT | Update invoice | ✅ Yes |
| `/funding-invoices/{id}` | DELETE | Void invoice | ✅ Yes |
| `/funding-batches` | POST | Create batch | ✅ Yes |
| `/funding-batches/{id}` | GET | Get batch | ✅ Yes |
| `/funding-batches/{id}/close` | POST | Close batch | ✅ Yes |
| `/funding-batches/{id}/reopen` | POST | Reopen batch | ✅ Yes |
| `/health` | GET | Health check | ❌ No |

---

## 🔐 Authentication

### Obtaining Access Token

```http
POST https://auth-server.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=your-client-id
&client_secret=your-client-secret
&scope=funding-invoices:read funding-invoices:write
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "funding-invoices:read funding-invoices:write"
}
```

### Using Access Token

```http
GET /api/v1/funding-invoices/12345
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 💰 Funding Invoices

### Create Funding Invoice

**Endpoint:** `POST /api/v1/funding-invoices`

**Description:** Creates a new funding invoice with employer and employee contribution splits.

**Request Body:**

```json
{
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "reimbursementPlanId": "RP-001",
  "employerFundingDefault": 500.00,
  "employeeFundingDefault": 250.00,
  "effectiveDate": "2025-12-15T00:00:00Z",
  "invoiceDescription": "Payroll funding for December 2025",
  "isLSA": false,
  "updateTemplate": true,
  "createdBy": "system-user"
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `employerId` | string | ✅ Yes | Max 50 chars | Employer identifier |
| `subaccountId` | string | ✅ Yes | Max 50 chars | Subaccount identifier |
| `reimbursementPlanId` | string | ✅ Yes | Max 50 chars | Reimbursement plan ID |
| `employerFundingDefault` | decimal | ✅ Yes | >= 0 | Employer contribution amount |
| `employeeFundingDefault` | decimal | ✅ Yes | >= 0 | Employee contribution amount |
| `effectiveDate` | datetime | ✅ Yes | ISO 8601 | Invoice effective date |
| `invoiceDescription` | string | ❌ No | Max 500 chars | Optional description |
| `isLSA` | boolean | ✅ Yes | - | Limited Spending Account flag |
| `updateTemplate` | boolean | ✅ Yes | - | Update template flag |
| `createdBy` | string | ✅ Yes | Max 100 chars | User who created invoice |

**Response (201 Created):**

```json
{
  "invoiceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "invoiceNumber": "INV-0001",
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "reimbursementPlanId": "RP-001",
  "batchId": null,
  "amount": 750.00,
  "status": "Pending",
  "invoiceType": "Payroll",
  "effectiveDate": "2025-12-15T00:00:00Z",
  "createdDate": "2025-12-12T10:30:00Z",
  "createdBy": "system-user",
  "modifiedDate": null,
  "modifiedBy": null,
  "isVoided": false,
  "voidedDate": null,
  "voidedBy": null
}
```

**Location Header:**
```
Location: /api/v1/funding-invoices/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**Error Responses:**

| Status | Error | Description | Solution |
|--------|-------|-------------|----------|
| 400 | `ValidationError` | Invalid request data | Check required fields, data types |
| 401 | `Unauthorized` | Missing/invalid token | Provide valid Bearer token |
| 409 | `Conflict` | Duplicate invoice | Check if invoice already exists |
| 500 | `InternalServerError` | Server error | Contact support |

**Example Error Response (400):**

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "EmployerId": ["The EmployerId field is required."],
    "EmployerFundingDefault": ["The field EmployerFundingDefault must be between 0 and 999999."]
  },
  "traceId": "00-3fa85f6457174562b3fc2c963f66afa6-b3fc2c963f66afa6-00"
}
```

**cURL Example:**

```bash
curl -X POST "https://your-api.com/api/v1/funding-invoices" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employerId": "EMP-001",
    "subaccountId": "SA-001",
    "reimbursementPlanId": "RP-001",
    "employerFundingDefault": 500.00,
    "employeeFundingDefault": 250.00,
    "effectiveDate": "2025-12-15T00:00:00Z",
    "invoiceDescription": "Payroll funding",
    "isLSA": false,
    "updateTemplate": true,
    "createdBy": "api-user"
  }'
```

---

### Get Funding Invoice by ID

**Endpoint:** `GET /api/v1/funding-invoices/{id}`

**Description:** Retrieves a single funding invoice by its unique identifier.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | GUID | ✅ Yes | Invoice ID |

**Response (200 OK):**

```json
{
  "invoiceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "invoiceNumber": "INV-0001",
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "amount": 750.00,
  "status": "Pending",
  "effectiveDate": "2025-12-15T00:00:00Z",
  "createdDate": "2025-12-12T10:30:00Z"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 404 | `NotFound` | Invoice not found |
| 401 | `Unauthorized` | Missing/invalid token |

**cURL Example:**

```bash
curl -X GET "https://your-api.com/api/v1/funding-invoices/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### List Funding Invoices

**Endpoint:** `GET /api/v1/funding-invoices`

**Description:** Retrieves a paginated list of funding invoices with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `employerId` | string | ❌ No | - | Filter by employer ID |
| `subaccountId` | string | ❌ No | - | Filter by subaccount ID |
| `status` | string | ❌ No | - | Filter by status (Pending, Approved, Processed, Voided) |
| `batchId` | GUID | ❌ No | - | Filter by batch ID |
| `fromDate` | datetime | ❌ No | - | Filter by created date (start) |
| `toDate` | datetime | ❌ No | - | Filter by created date (end) |
| `pageNumber` | int | ❌ No | 1 | Page number (1-based) |
| `pageSize` | int | ❌ No | 50 | Page size (max 100) |

**Response (200 OK):**

```json
{
  "data": [
    {
      "invoiceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "invoiceNumber": "INV-0001",
      "employerId": "EMP-001",
      "amount": 750.00,
      "status": "Pending",
      "createdDate": "2025-12-12T10:30:00Z"
    },
    {
      "invoiceId": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
      "invoiceNumber": "INV-0002",
      "employerId": "EMP-001",
      "amount": 1000.00,
      "status": "Approved",
      "createdDate": "2025-12-11T09:15:00Z"
    }
  ],
  "pageNumber": 1,
  "pageSize": 50,
  "totalCount": 2,
  "totalPages": 1,
  "hasPreviousPage": false,
  "hasNextPage": false
}
```

**cURL Example:**

```bash
curl -X GET "https://your-api.com/api/v1/funding-invoices?employerId=EMP-001&status=Pending&pageSize=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Update Funding Invoice

**Endpoint:** `PUT /api/v1/funding-invoices/{id}`

**Description:** Updates an existing funding invoice (limited fields).

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | GUID | ✅ Yes | Invoice ID |

**Request Body:**

```json
{
  "status": "Approved",
  "invoiceDescription": "Updated description",
  "modifiedBy": "admin-user"
}
```

**Updatable Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Invoice status (Pending, Approved, Processed) |
| `invoiceDescription` | string | Optional description |
| `modifiedBy` | string | User making the update |

**Response (200 OK):**

```json
{
  "invoiceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "Approved",
  "invoiceDescription": "Updated description",
  "modifiedDate": "2025-12-12T11:00:00Z",
  "modifiedBy": "admin-user"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 404 | `NotFound` | Invoice not found |
| 400 | `ValidationError` | Invalid status transition |
| 409 | `Conflict` | Invoice already processed/voided |

---

### Void Funding Invoice

**Endpoint:** `DELETE /api/v1/funding-invoices/{id}`

**Description:** Voids (soft deletes) a funding invoice. Data is preserved with `isVoided = true`.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | GUID | ✅ Yes | Invoice ID |

**Request Body:**

```json
{
  "reason": "Duplicate invoice created in error",
  "voidedBy": "admin-user"
}
```

**Response (204 No Content)**

No response body.

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 404 | `NotFound` | Invoice not found |
| 409 | `Conflict` | Invoice already voided |

**cURL Example:**

```bash
curl -X DELETE "https://your-api.com/api/v1/funding-invoices/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Duplicate invoice",
    "voidedBy": "admin-user"
  }'
```

---

## 📦 Funding Batches

### Create Funding Batch

**Endpoint:** `POST /api/v1/funding-batches`

**Description:** Creates a new funding batch for grouping invoices.

**Request Body:**

```json
{
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "createdBy": "batch-processor"
}
```

**Response (201 Created):**

```json
{
  "batchId": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "batchNumber": "BATCH-0001",
  "employerId": "EMP-001",
  "subaccountId": "SA-001",
  "status": "Open",
  "totalAmount": 0.00,
  "invoiceCount": 0,
  "createdDate": "2025-12-12T10:30:00Z",
  "createdBy": "batch-processor"
}
```

---

### Get Funding Batch by ID

**Endpoint:** `GET /api/v1/funding-batches/{id}`

**Description:** Retrieves a single funding batch by ID.

**Response (200 OK):**

```json
{
  "batchId": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "batchNumber": "BATCH-0001",
  "employerId": "EMP-001",
  "status": "Open",
  "totalAmount": 3500.00,
  "invoiceCount": 5,
  "createdDate": "2025-12-12T10:30:00Z",
  "closedDate": null,
  "invoices": [
    {
      "invoiceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "invoiceNumber": "INV-0001",
      "amount": 750.00
    }
  ]
}
```

---

### Close Funding Batch

**Endpoint:** `POST /api/v1/funding-batches/{id}/close`

**Description:** Closes a funding batch, finalizes totals, and creates replenishment invoice if needed.

**Request Body:**

```json
{
  "closedBy": "batch-processor",
  "excludeInvoiceIds": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ]
}
```

**Response (200 OK):**

```json
{
  "batchId": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "status": "Closed",
  "totalAmount": 3500.00,
  "invoiceCount": 4,
  "excludedInvoiceCount": 1,
  "replenishmentInvoiceId": "6fa85f64-5717-4562-b3fc-2c963f66afa9",
  "closedDate": "2025-12-12T12:00:00Z",
  "closedBy": "batch-processor"
}
```

**Business Rules:**
- Excluded invoices are removed from batch
- Replenishment invoice created if needed
- All included invoices status updated to "Processed"
- Batch status changed to "Closed"

---

### Reopen Funding Batch

**Endpoint:** `POST /api/v1/funding-batches/{id}/reopen`

**Description:** Reopens a closed batch (reverses closure, deletes replenishment invoice).

**Request Body:**

```json
{
  "reopenedBy": "admin-user",
  "reason": "Corrections needed"
}
```

**Response (200 OK):**

```json
{
  "batchId": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
  "status": "Open",
  "totalAmount": 0.00,
  "invoiceCount": 0,
  "closedDate": null,
  "reopenedDate": "2025-12-12T14:00:00Z",
  "reopenedBy": "admin-user"
}
```

---

## 🏥 Health Check

### Health Endpoint

**Endpoint:** `GET /health`

**Description:** Returns service health status (no authentication required).

**Response (200 OK):**

```json
{
  "status": "Healthy",
  "dataLayer": "EFCore",
  "version": "1.0.0",
  "timestamp": "2025-12-12T10:30:00Z",
  "checks": {
    "database": "Healthy",
    "externalApis": "Healthy",
    "memory": "Healthy"
  }
}
```

**Response (503 Service Unavailable):**

```json
{
  "status": "Unhealthy",
  "dataLayer": "EFCore",
  "version": "1.0.0",
  "timestamp": "2025-12-12T10:30:00Z",
  "checks": {
    "database": "Unhealthy - Connection timeout",
    "externalApis": "Healthy",
    "memory": "Healthy"
  }
}
```

---

## 🔍 Response Codes

| Code | Status | Description | Common Causes |
|------|--------|-------------|---------------|
| 200 | OK | Success | GET, PUT requests |
| 201 | Created | Resource created | POST requests |
| 204 | No Content | Success, no body | DELETE requests |
| 400 | Bad Request | Invalid input | Validation errors |
| 401 | Unauthorized | Auth failed | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions | User lacks role |
| 404 | Not Found | Resource not found | Invalid ID |
| 409 | Conflict | Business rule violation | Duplicate, invalid state |
| 500 | Internal Server Error | Server error | Application exception |
| 503 | Service Unavailable | Service down | Database offline |

---

## 📊 Rate Limiting

**Limits:**
- **Authenticated:** 1000 requests per minute per token
- **Unauthenticated:** 10 requests per minute per IP (health endpoint only)

**Response Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1670851200
```

**Exceeded Limit (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "retryAfter": 60
}
```

---

## 🧪 Testing with Swagger UI

**Access Swagger:** `https://your-api.com/swagger`

**Steps:**
1. Click "Authorize" button
2. Enter Bearer token: `Bearer YOUR_TOKEN`
3. Click "Authorize"
4. Expand endpoint (e.g., `POST /funding-invoices`)
5. Click "Try it out"
6. Edit request body
7. Click "Execute"
8. View response

---

## 📚 Additional Resources

- **OpenAPI Specification:** `https://your-api.com/swagger/v1/swagger.json`
- **Postman Collection:** Available in `docs/postman/FundingInvoices.postman_collection.json`
- **Code Examples:** See `examples/` directory

---

**Last Updated:** December 12, 2025  
**API Version:** 1.0  
**Maintained By:** API Development Team
