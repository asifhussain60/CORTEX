# Entity-Relationship Diagram — CortexLabs FinTrack

```mermaid
erDiagram
    USER {
        int Id PK
        string UserName UK "Required, max 50"
        string Email UK "Required, max 100"
        string PasswordHash "BCrypt hashed"
        UserRole Role "Admin or User"
        bool IsActive "Default true"
        datetime CreatedAt "Audit field"
        string CreatedBy "Audit field"
        datetime ModifiedAt "Audit field"
        string ModifiedBy "Audit field"
    }

    TRANSACTION {
        int Id PK
        string Description "Required, max 200"
        decimal Amount "Required, positive"
        TransactionCategory Category "Enum"
        TransactionType Type "Income or Expense"
        datetime Date "Required"
        int UserId FK
        datetime CreatedAt "Audit field"
        datetime ModifiedAt "Audit field"
    }

    ACCOUNT {
        int Id PK
        string Name "Required, max 100"
        decimal Balance "Default 0"
        int UserId FK
        AccountType AccountType "Checking, Savings, Investment"
        datetime CreatedAt "Audit field"
        datetime ModifiedAt "Audit field"
        bytes ConcurrencyToken "Optimistic concurrency"
    }

    REPORT {
        int Id PK
        string Title "Required"
        string Content "Report body"
        int GeneratedBy FK
        datetime GeneratedAt
    }

    USER ||--o{ TRANSACTION : "has many"
    USER ||--o{ ACCOUNT : "owns"
    USER ||--o{ REPORT : "generates"
```

## Key Changes from BadMonolith

| Aspect | BadMonolith | Refactored |
|--------|------------|------------|
| Naming | Mixed (snake_case, camelCase, PascalCase) | Consistent PascalCase |
| Types | String for everything | Enums (TransactionType, UserRole, etc.) |
| Audit | No audit fields | CreatedAt, CreatedBy, ModifiedAt, ModifiedBy |
| Validation | None | DataAnnotations + service layer |
| Concurrency | None | ConcurrencyToken on Account |
| Password | Plaintext (named password_hash) | Actual BCrypt hash |
