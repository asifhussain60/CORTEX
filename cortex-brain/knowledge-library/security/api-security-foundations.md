# 🔐 API Security Foundations

**Author:** Asif Hussain  
**Version:** 1.0.0  
**Last Updated:** December 30, 2025  
**Status:** ✅ Active  
**Category:** Security Knowledge Library  

---

## 📋 Executive Summary

This document provides comprehensive guidance on securing APIs, covering authentication, authorization, input validation, rate limiting, and common attack prevention. It incorporates the OWASP API Security Top 10 and provides practical implementation patterns.

**Related Documents:**
- `owasp-top-10-guide.md` - Web application vulnerabilities
- `threat-modeling-framework.md` - Threat analysis methodology
- `access-control-patterns.md` - Authorization patterns

---

## 🏗️ API Security Architecture

### Security Layers Overview

```mermaid
graph TB
    subgraph "Internet 🌐"
        CLIENT[("👤 API Client")]
        ATTACKER[("☠️ Attacker")]
    end
    
    subgraph "Edge Security 🛡️"
        WAF["🔥 Web Application Firewall<br/>OWASP Rules, Rate Limiting"]
        DDoS["🌊 DDoS Protection<br/>Traffic Analysis"]
        CDN["☁️ CDN<br/>SSL Termination"]
    end
    
    subgraph "API Gateway Layer 🚪"
        GW["🔌 API Gateway<br/>Authentication, Authorization"]
        RATE["⏱️ Rate Limiter<br/>Throttling"]
        CACHE["⚡ Cache<br/>Response Caching"]
    end
    
    subgraph "Application Layer 🏢"
        AUTH["🔐 Auth Service<br/>OAuth 2.0, JWT"]
        API["⚙️ API Service<br/>Business Logic"]
        VALID["✅ Validation<br/>Input Sanitization"]
    end
    
    subgraph "Data Layer 💾"
        DB[("💾 Database<br/>Encrypted at Rest")]
        SECRETS["🔑 Secrets Manager<br/>API Keys, Certs"]
    end
    
    CLIENT --> WAF
    ATTACKER -.->|"Attack Vector"| WAF
    WAF --> DDoS
    DDoS --> CDN
    CDN --> GW
    GW --> RATE
    RATE --> AUTH
    AUTH --> API
    API --> VALID
    VALID --> DB
    AUTH --> SECRETS
    
    style ATTACKER fill:#ff4444,stroke:#cc0000,color:white
    style WAF fill:#4CAF50,stroke:#388E3C,color:white
    style AUTH fill:#2196F3,stroke:#1976D2,color:white
    style SECRETS fill:#9C27B0,stroke:#7B1FA2,color:white
```

---

## 🔐 Authentication

### OAuth 2.0 Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant C as 🖥️ Client App
    participant AS as 🔐 Auth Server
    participant RS as 🔌 Resource Server
    
    U->>C: Click "Login"
    C->>AS: Authorization Request
    AS->>U: Login Page
    U->>AS: Credentials
    AS->>AS: Validate Credentials
    AS->>C: Authorization Code
    C->>AS: Token Request (Code + Client Secret)
    AS->>AS: Validate Code
    AS->>C: Access Token + Refresh Token
    C->>RS: API Request (Bearer Token)
    RS->>RS: Validate Token
    RS->>C: Protected Resource
    C->>U: Display Data
```

### Token Types

| Token Type | Lifetime | Storage | Use Case |
|------------|----------|---------|----------|
| **Access Token** | 15-60 min | Memory | API authorization |
| **Refresh Token** | 7-30 days | Secure storage | Token renewal |
| **ID Token** | 15-60 min | Memory | User identity |
| **API Key** | Long-lived | Server config | Service-to-service |

### JWT Structure

```mermaid
graph LR
    subgraph "JWT Token Structure"
        H["📋 Header<br/>alg: RS256<br/>typ: JWT"]
        P["📦 Payload<br/>sub, iat, exp<br/>custom claims"]
        S["🔏 Signature<br/>HMAC/RSA<br/>verification"]
    end
    
    H -->|"."| P
    P -->|"."| S
    
    style H fill:#e91e63,color:white
    style P fill:#9c27b0,color:white
    style S fill:#3f51b5,color:white
```

### JWT Security Best Practices

```python
# ✅ Good: Strong algorithm, short expiry
jwt.encode(
    payload={
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iss": "https://api.example.com",
        "aud": "https://app.example.com"
    },
    key=private_key,
    algorithm="RS256"  # Asymmetric signing
)

# ❌ Bad: Weak algorithm, no expiry
jwt.encode({"user": user_id}, "weak_secret", algorithm="HS256")
```

---

## 🔓 Authorization

### RBAC vs ABAC

```mermaid
graph TB
    subgraph "RBAC (Role-Based)"
        USER1["👤 User"]
        ROLE["📋 Role: Admin"]
        PERM["✅ Permissions"]
        
        USER1 --> ROLE --> PERM
    end
    
    subgraph "ABAC (Attribute-Based)"
        USER2["👤 User"]
        ATTR1["📊 Attributes<br/>Department: HR"]
        ATTR2["📊 Resource<br/>Type: Document"]
        POLICY["📜 Policy Engine"]
        DECISION["✅ Access Decision"]
        
        USER2 --> ATTR1
        ATTR1 --> POLICY
        ATTR2 --> POLICY
        POLICY --> DECISION
    end
    
    style ROLE fill:#2196F3
    style POLICY fill:#4CAF50
```

### Authorization Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as 👤 Client
    participant GW as 🚪 API Gateway
    participant AUTH as 🔐 Auth Service
    participant API as ⚙️ API
    participant PDP as 📜 Policy Engine
    
    C->>GW: Request + Token
    GW->>AUTH: Validate Token
    AUTH-->>GW: Token Valid + Claims
    GW->>API: Forward Request
    API->>PDP: Check Permission(user, action, resource)
    PDP->>PDP: Evaluate Policies
    
    alt Authorized
        PDP-->>API: ✅ Allowed
        API-->>GW: Response
        GW-->>C: 200 OK
    else Unauthorized
        PDP-->>API: ❌ Denied
        API-->>GW: Error
        GW-->>C: 403 Forbidden
    end
```

---

## ✅ Input Validation

### Validation Layers

```mermaid
graph TB
    INPUT["📥 API Input"]
    
    subgraph "Layer 1: Schema Validation"
        SCHEMA["📋 JSON Schema<br/>Type, Format, Required"]
    end
    
    subgraph "Layer 2: Business Validation"
        BIZ["⚙️ Business Rules<br/>Range, Relationships"]
    end
    
    subgraph "Layer 3: Security Validation"
        SEC["🔐 Security Checks<br/>Injection, XSS, Path"]
    end
    
    subgraph "Layer 4: Sanitization"
        SANITIZE["🧹 Sanitize<br/>Encode, Escape, Normalize"]
    end
    
    INPUT --> SCHEMA
    SCHEMA -->|"Valid"| BIZ
    SCHEMA -->|"Invalid"| REJECT1["❌ 400 Bad Request"]
    BIZ -->|"Valid"| SEC
    BIZ -->|"Invalid"| REJECT2["❌ 422 Unprocessable"]
    SEC -->|"Safe"| SANITIZE
    SEC -->|"Malicious"| REJECT3["❌ 400 Bad Request"]
    SANITIZE --> PROCESS["✅ Process Request"]
    
    style REJECT1 fill:#ff4444
    style REJECT2 fill:#ff4444
    style REJECT3 fill:#ff4444
    style PROCESS fill:#4CAF50
```

### Common Injection Prevention

| Attack | Prevention | Example |
|--------|------------|---------|
| **SQL Injection** | Parameterized queries | `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))` |
| **NoSQL Injection** | Type validation | Reject `$where`, `$regex` in input |
| **XSS** | Output encoding | `html.escape(user_input)` |
| **Command Injection** | Avoid shell execution | Use subprocess with list args |
| **Path Traversal** | Normalize paths | `os.path.normpath(input)`, reject `..` |

### Validation Example

```python
from pydantic import BaseModel, Field, validator
import re

class UserCreateRequest(BaseModel):
    """Validated user creation request."""
    
    email: str = Field(..., max_length=254)
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=12)
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special char')
        return v
```

---

## ⏱️ Rate Limiting

### Rate Limiting Architecture

```mermaid
graph LR
    subgraph "Client Requests"
        C1["👤 User A"]
        C2["👤 User B"]
        C3["🤖 Bot"]
    end
    
    subgraph "Rate Limiter"
        RL["⏱️ Rate Limiter<br/>Token Bucket / Sliding Window"]
        COUNTER[("📊 Counter Store<br/>Redis")]
    end
    
    subgraph "Decisions"
        ALLOW["✅ 200 OK"]
        REJECT["❌ 429 Too Many"]
    end
    
    C1 -->|"10 req/min"| RL
    C2 -->|"10 req/min"| RL
    C3 -->|"1000 req/min"| RL
    RL --> COUNTER
    RL -->|"Under limit"| ALLOW
    RL -->|"Over limit"| REJECT
    
    style C3 fill:#ff4444
    style REJECT fill:#ff9800
```

### Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
Retry-After: 60
```

### Implementation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Token Bucket** | Tokens replenish at fixed rate | Burst-tolerant limits |
| **Sliding Window** | Count requests in rolling window | Precise rate control |
| **Fixed Window** | Count in fixed time buckets | Simple implementation |
| **Leaky Bucket** | Constant output rate | Queue smoothing |

---

## 🔴 OWASP API Security Top 10 (2023)

### Threat Overview

```mermaid
graph TB
    subgraph "API Security Top 10"
        A1["API1: BOLA<br/>Broken Object Level Auth"]
        A2["API2: Broken Authentication"]
        A3["API3: BOPLA<br/>Broken Object Property Level Auth"]
        A4["API4: Unrestricted Resource Consumption"]
        A5["API5: BFLA<br/>Broken Function Level Auth"]
        A6["API6: Server Side Request Forgery"]
        A7["API7: Security Misconfiguration"]
        A8["API8: Lack of Protection from Automated Threats"]
        A9["API9: Improper Inventory Management"]
        A10["API10: Unsafe Consumption of APIs"]
    end
    
    style A1 fill:#ff0000,color:white
    style A2 fill:#ff3333,color:white
    style A3 fill:#ff6666,color:white
    style A4 fill:#ff9999
    style A5 fill:#ffcccc
```

### API1: Broken Object Level Authorization (BOLA)

**Threat:** Attacker manipulates object IDs to access unauthorized resources.

```mermaid
sequenceDiagram
    participant A as ☠️ Attacker
    participant API as 🔌 API
    participant DB as 💾 Database
    
    A->>API: GET /api/users/123/profile
    Note over API: Attacker changes ID
    A->>API: GET /api/users/456/profile
    
    alt Vulnerable API
        API->>DB: SELECT * FROM users WHERE id=456
        DB-->>API: User 456 Data
        API-->>A: 200 OK (Other user's data!)
    else Protected API
        API->>API: Check user_id == token.sub
        API-->>A: 403 Forbidden
    end
```

**Prevention:**

```python
# ✅ Correct: Verify ownership
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_user_profile(user_id)

# ❌ Vulnerable: No ownership check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int):
    return await get_user_profile(user_id)  # Anyone can access any profile!
```

---

## 🔒 Transport Security

### TLS Configuration

```mermaid
graph LR
    subgraph "TLS Handshake"
        C["👤 Client"] -->|"1. ClientHello"| S["🔌 Server"]
        S -->|"2. ServerHello + Cert"| C
        C -->|"3. Key Exchange"| S
        S -->|"4. Finished"| C
        C <-->|"5. Encrypted Data"| S
    end
    
    style C fill:#2196F3
    style S fill:#4CAF50
```

### Recommended TLS Settings

| Setting | Recommendation |
|---------|----------------|
| **Protocol** | TLS 1.2+ (prefer 1.3) |
| **Ciphers** | ECDHE+AESGCM, ECDHE+CHACHA20 |
| **Key Exchange** | ECDHE (X25519, P-256) |
| **HSTS** | Enabled, min 1 year |
| **Certificate** | Let's Encrypt or commercial CA |

---

## 📊 API Security Checklist

### Authentication ✅

- [ ] Use OAuth 2.0 / OpenID Connect
- [ ] Implement MFA for sensitive operations
- [ ] Use short-lived access tokens (15-60 min)
- [ ] Secure refresh token storage
- [ ] Invalidate tokens on logout

### Authorization ✅

- [ ] Implement RBAC or ABAC
- [ ] Check authorization at every endpoint
- [ ] Verify object ownership (prevent BOLA)
- [ ] Use principle of least privilege

### Input Validation ✅

- [ ] Validate all input against schemas
- [ ] Use parameterized queries
- [ ] Sanitize output to prevent XSS
- [ ] Reject unexpected fields

### Rate Limiting ✅

- [ ] Implement per-user rate limits
- [ ] Protect authentication endpoints
- [ ] Use exponential backoff for retries
- [ ] Return proper 429 responses

### Logging & Monitoring ✅

- [ ] Log all authentication events
- [ ] Log authorization failures
- [ ] Monitor for anomalies
- [ ] Alert on suspicious patterns

---

## 🔗 Integration with CORTEX

### Security Injection in Plans

When CORTEX Planning System detects API-related features, it automatically includes:

1. **Threat Model** - STRIDE analysis for API endpoints
2. **Security Tests** - Authentication/authorization test generation
3. **Security Documentation** - API security requirements

### Knowledge References

```yaml
# In planning_orchestrator.py
security_knowledge:
  api_security: "cortex-brain/knowledge-library/security/api-security-foundations.md"
  threat_modeling: "cortex-brain/knowledge-library/security/threat-modeling-framework.md"
  access_control: "cortex-brain/knowledge-library/security/access-control-patterns.md"
```

---

## 📚 References

- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [NIST API Security Guidelines](https://csrc.nist.gov/)

---

**Maintained by:** CORTEX Development Team  
**Last Updated:** December 30, 2025
