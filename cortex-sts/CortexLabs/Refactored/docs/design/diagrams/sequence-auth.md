# Sequence Diagram — Authentication Flow

```mermaid
sequenceDiagram
    participant Client as Frontend (app.ts)
    participant API as AuthEndpoints
    participant MW as ErrorHandlingMiddleware
    participant Auth as AuthService
    participant Repo as UserRepository
    participant DB as SQLite

    Client->>API: POST /api/v1/auth/login<br/>{username, password} in body
    API->>MW: Request passes through middleware
    MW->>API: Adds correlation ID header

    API->>Auth: Authenticate(username, password)
    Auth->>Repo: FindByUsername(username)
    Repo->>DB: SELECT * FROM Users<br/>WHERE UserName = @username
    Note over DB: Parameterized query<br/>(no SQL injection)
    DB-->>Repo: User record (or null)
    Repo-->>Auth: User entity

    alt User not found
        Auth-->>API: AuthResult.Failed
        API-->>Client: 401 Unauthorized<br/>(no info disclosure —<br/>same error for wrong user vs password)
    else User found
        Auth->>Auth: BCrypt.Verify(password, user.PasswordHash)
        alt Password incorrect
            Auth-->>API: AuthResult.Failed
            API-->>Client: 401 Unauthorized
        else Password correct
            Auth->>Auth: Generate JWT token
            Auth-->>API: AuthResult.Success(token, role)
            API->>API: Log "User {username} authenticated"<br/>(ILogger, not Console.WriteLine)
            API-->>Client: 200 OK {token, role}
        end
    end

    Note over Client: Token stored securely<br/>(not localStorage)
```

## Security Improvements over BadMonolith

| Vulnerability | BadMonolith | Refactored |
|---|---|---|
| SQL injection in login | `WHERE user_name = '{username}'` | `WHERE UserName = @username` |
| Credentials in URL | Query params `?username=...&password=...` | Request body (POST) |
| Info disclosure | Different error for wrong user vs password | Same 401 for both |
| Token storage | `localStorage.setItem("auth_token", ...)` | Secure cookie or memory |
| Password storage | Plaintext despite field name | BCrypt hash |
| Audit logging | `Console.WriteLine` | `ILogger.LogInformation` |
