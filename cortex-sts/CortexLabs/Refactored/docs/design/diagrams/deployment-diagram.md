# Deployment Diagram — CortexLabs FinTrack

```mermaid
graph TB
    subgraph "Client Browser"
        FE[Frontend<br/>index.html + app.js<br/>TypeScript compiled to ES2022]
    end

    subgraph "Application Server"
        subgraph "ASP.NET Core 8.0 Runtime"
            MW_CORS[CORS Middleware<br/>Configured origins only]
            MW_LOG[Request Logging<br/>Correlation IDs]
            MW_ERR[Error Handling<br/>ProblemDetails format]
            MW_AUTH[Auth Middleware<br/>JWT validation]
            EP_API[API Endpoints<br/>/api/v1/*]
            SVC[Application Services<br/>UserService, TransactionService,<br/>AccountService, AuthService]
        end

        subgraph "Data Layer"
            REPO_LAYER[Repository Layer<br/>Parameterized Queries]
            SQLITE[(SQLite Database<br/>fintrack.db<br/>WAL mode)]
        end
    end

    subgraph "Configuration"
        ENV[Environment Variables<br/>- CORS_ORIGINS<br/>- JWT_SECRET<br/>- CONNECTION_STRING<br/>- SMTP_* credentials]
    end

    FE -->|HTTPS| MW_CORS
    MW_CORS --> MW_LOG
    MW_LOG --> MW_ERR
    MW_ERR --> MW_AUTH
    MW_AUTH --> EP_API
    EP_API --> SVC
    SVC --> REPO_LAYER
    REPO_LAYER --> SQLITE
    ENV -.->|reads at startup| SVC

    style FE fill:#4CAF50,color:#fff
    style SQLITE fill:#607D8B,color:#fff
    style ENV fill:#FFC107,color:#000
    style MW_ERR fill:#f44336,color:#fff
    style MW_AUTH fill:#9C27B0,color:#fff
```

## Deployment Notes

| Aspect | BadMonolith | Refactored |
|---|---|---|
| Secrets | Hardcoded in appsettings.json | Environment variables |
| CORS | AllowAnyOrigin() | Configured allowlist |
| Middleware | None (catch in global handler) | Pipeline: CORS → Logging → Error → Auth |
| Database | Inline CREATE TABLE in Program.cs | DatabaseInitializer (idempotent) |
| Health | Always returns "healthy" | Checks DB connectivity |
| Error format | Raw stack traces | RFC 7807 ProblemDetails |
