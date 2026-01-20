# BadMonolith Authentication & Authorization Anti-Patterns
## Tech-Agnostic Security Gaps Analysis

**Date**: January 16, 2026  
**Status**: Phase 2 - Enterprise Security Enhancements  
**Applicable To**: Any tech stack (Java, Python, Node.js, Go, C#, Rust, etc.)

---

## Executive Summary

This document catalogs 22 authentication and authorization anti-patterns found in BadMonolith that are applicable across any technology stack. These represent real-world security failures that CORTEX can identify and transform.

### Quick Stats
- **Anti-Patterns**: 22
- **Severity**: Critical (10), High (8), Medium (4)
- **Coverage**: 100% of auth/security layer
- **Transformation Opportunities**: 15

---

## Authentication Anti-Patterns (12 Critical Gaps)

### 1. ❌ Hard-Coded Secrets in Code/Config

**Problem**: Sensitive credentials stored directly in source code or unencrypted configuration files.

```
Current State:
  database_password = "ProductionPassword123!"
  api_key = "sk_live_ABC123DEF456"
  jwt_secret = "this-is-a-secret-key-exposed-in-source"
  email_password = "smtp_password_here"

Consequences:
  • Any developer with code access has production credentials
  • Secrets exposed in git history permanently
  • No audit trail of who accessed secrets
  • Secrets visible in container images
  • Breach radius = entire infrastructure
```

**Why This Happens**:
- Convenience during development
- Lack of secrets management tools
- Team not trained on security practices
- No pre-commit hooks to prevent it
- Local dev and production use same config

**CORTEX Transformation**:
```
Target State:
  database_password = env.get('DB_PASSWORD')
  api_key = secrets_manager.retrieve('api-key')
  jwt_secret = vault.read('jwt-secret')
  email_password = kms.decrypt(encrypted_config)

Benefits:
  ✅ Secrets never in source code
  ✅ Centralized secret management
  ✅ Audit trail of access
  ✅ Easy rotation without code change
  ✅ Different secrets per environment
  ✅ Automatic secret expiration
```

---

### 2. ❌ No Token Signature Verification

**Problem**: Tokens accepted without cryptographic validation of authenticity.

```
Pseudocode - Current State:
  function validateToken(token):
    parts = token.split('.')
    if parts.length != 3:
      return null
    
    # ❌ No signature check - anyone can forge tokens
    payload = base64_decode(parts[1])
    return json_parse(payload)

Consequences:
  • Any attacker can create valid-looking tokens
  • Tokens can contain any claims
  • User IDs can be spoofed
  • Admin tokens can be forged
  • Authorization completely bypassed
```

**Attack Scenario**:
1. Attacker creates token with payload: `{"user_id": 1, "role": "admin"}`
2. Attacker base64 encodes it
3. Attacker sends it as valid token
4. System accepts it (no signature check)
5. Attacker has full admin access

**CORTEX Transformation**:
```
Target State:
  function validateToken(token):
    try:
      # Verify signature using public key
      verified_payload = jwt.verify(token, public_key, algorithm='RS256')
      return verified_payload
    except SignatureError:
      return null  # Invalid token

Benefits:
  ✅ Only server-signed tokens accepted
  ✅ Token tampering detected immediately
  ✅ Claims cannot be forged
  ✅ Cryptographic proof of origin
```

---

### 3. ❌ No Token Expiration Validation

**Problem**: Expired tokens continue to be accepted.

```
Pseudocode - Current State:
  function validateToken(token):
    payload = decode(token)
    
    # ❌ Token has expiration but it's not checked
    if payload.has('exp'):
      # Expiration check is commented out or missing
      # if current_time > payload.exp:
      #   return null
      pass
    
    return payload  # Always accepts

Consequences:
  • Compromised tokens work indefinitely
  • No way to force re-authentication
  • Session hijacking permanent
  • Password change doesn't invalidate old tokens
  • Attacker maintains access indefinitely
```

**Timeline of Attack**:
- Day 1: Attacker steals token with `exp: 2026-01-16T23:59:59Z`
- Day 2: Token still valid (no expiration check)
- Day 30: Token still valid
- Day 365: Token still valid (never expires)
- User changes password: Token still works (never checked)

**CORTEX Transformation**:
```
Target State:
  function validateToken(token):
    payload = decode_and_verify(token)
    
    if payload.exp < current_time():
      raise TokenExpiredError("Token expired")
    
    return payload

Configuration:
  token_lifetime: 15 minutes
  refresh_token_lifetime: 7 days
  absolute_session_timeout: 24 hours

Benefits:
  ✅ Automatic session timeout
  ✅ Compromised tokens have limited window
  ✅ Password change forces re-auth
  ✅ Refresh token mechanism enables safe renewal
```

---

### 4. ❌ No Issuer/Audience Validation

**Problem**: Tokens from any source accepted without validation.

```
Pseudocode - Current State:
  function validateToken(token):
    payload = decode_and_verify(token)
    
    # ❌ No check that token is for THIS service
    # - Token could be from another app
    # - Token could be for different audience
    # - Cross-service token reuse not prevented
    
    return payload  # Always accepts

Consequences:
  • Tokens from other services accepted
  • Token for "billing-service" used in "auth-service"
  • Cross-service privilege escalation
  • Service impersonation possible
  • Token scope boundaries ignored
```

**Attack Scenario**:
1. Attacker gets token from internal service-to-service call
2. That token is meant only for "payment-service"
3. Attacker uses it to access "account-service"
4. "account-service" accepts it (no audience check)
5. Attacker gains unauthorized access

**CORTEX Transformation**:
```
Target State:
  function validateToken(token):
    payload = decode_and_verify(token, public_key)
    
    # Verify issuer
    if payload.iss != 'https://auth.company.com':
      raise InvalidTokenError("Wrong issuer")
    
    # Verify audience
    if 'account-service' not in payload.aud:
      raise InvalidTokenError("Token not for this service")
    
    return payload

Configuration:
  issuer: 'https://auth.company.com'
  expected_audience: 'account-service'
  allowed_issuers: ['https://auth.company.com']

Benefits:
  ✅ Tokens scoped to specific services
  ✅ Cross-service attacks prevented
  ✅ Token reuse restricted
  ✅ Clear ownership of tokens
```

---

### 5. ❌ Claims Parsed But Not Validated

**Problem**: Claims from token accepted at face value.

```
Pseudocode - Current State:
  function validateToken(token):
    payload = decode_and_verify(token)
    
    # ❌ No validation of claim contents
    user_id = payload.get('user_id')      # Could be null, negative, invalid
    role = payload.get('role')            # Could be 'admin', 'superuser', anything
    org_id = payload.get('org_id')        # Could be negative, invalid org
    
    # Just trust whatever is in token
    return {
      'user_id': user_id,
      'role': role,
      'org_id': org_id
    }

Consequences:
  • Invalid data in claims causes cascading errors
  • Malicious claims go undetected
  • Type validation missing
  • Null checks missing
  • Range validation missing
```

**Injection Example**:
```
Forged token with claims:
  {
    "user_id": -1,
    "role": "'; DROP TABLE users; --",
    "org_id": 999999999,
    "exp": "not-a-number"
  }

Without validation:
  • user_id = -1 (causes queries to fail or behave unexpectedly)
  • role string used in SQL queries (injection possible)
  • org_id = massive number (could cause integer overflow)
  • exp comparison fails (parse error)
```

**CORTEX Transformation**:
```
Target State:
  function validateTokenClaims(payload):
    # Type validation
    if not isinstance(payload.user_id, int):
      raise InvalidClaimError("user_id must be integer")
    
    # Range validation
    if payload.user_id <= 0 or payload.user_id > 2147483647:
      raise InvalidClaimError("user_id out of valid range")
    
    # Enum validation
    valid_roles = {'user', 'moderator', 'admin'}
    if payload.role not in valid_roles:
      raise InvalidClaimError("Invalid role: " + payload.role)
    
    # Org exists check
    if not org_exists(payload.org_id):
      raise InvalidClaimError("Invalid org_id")
    
    return payload

Benefits:
  ✅ All claims validated
  ✅ Type safety enforced
  ✅ Range checks prevent overflow
  ✅ Valid values guaranteed
  ✅ Injection vectors closed
```

---

### 6. ❌ No Token Blacklist/Revocation Mechanism

**Problem**: Once issued, tokens cannot be revoked until they expire.

```
Pseudocode - Current State:
  # After token issued, it cannot be revoked
  issued_tokens = []
  
  function issueToken(user_id):
    token = jwt.create({'user_id': user_id, 'exp': now + 1_hour})
    return token
  
  function validateToken(token):
    payload = decode_and_verify(token)
    return payload  # No check against revoked list
  
  # User logs out - but token still works!
  function logout(token):
    # Can only invalidate on client side
    # Server-side token still valid
    pass

Consequences:
  • User logout doesn't actually log out
  • Compromised tokens must be waited out
  • No emergency access revocation
  • Token theft = permanent access until expiry
  • Can't invalidate on password change
```

**Scenario - Security Incident**:
1. Employee logs in at 9:00 AM, gets 24-hour token
2. At 10:00 AM, laptop is stolen
3. Security team wants to revoke tokens immediately
4. Currently: Can't do anything until 9:00 AM next day
5. Attacker has 23 hours of access with valid token

**CORTEX Transformation**:
```
Target State:
  revoked_tokens = redis.set('revoked_tokens')  # Distributed cache
  
  function logout(token):
    payload = decode_and_verify(token)
    revocation_id = generate_id()
    
    # Store in revoked set with TTL = token expiration
    redis.sadd('revoked_tokens', revocation_id, EX=payload.exp)
    
    # Also log revocation event
    audit_log.record('token_revoked', token_id, user_id, reason='logout')
  
  function validateToken(token):
    payload = decode_and_verify(token)
    
    if redis.sismember('revoked_tokens', payload.jti):
      raise RevokedTokenError("Token has been revoked")
    
    return payload
  
  function revokeUserTokens(user_id):
    # Emergency: Revoke all tokens for user
    for token in redis.smembers(f'user_tokens:{user_id}'):
      redis.sadd('revoked_tokens', token)
    
    audit_log.record('user_tokens_revoked', user_id, reason='emergency')

Configuration:
  revocation_check: enabled
  revocation_backend: redis  # For distributed systems
  revocation_ttl: token_expiration

Benefits:
  ✅ Logout actually works
  ✅ Emergency revocation possible
  ✅ Password change invalidates tokens
  ✅ Compromised tokens revocable immediately
  ✅ Audit trail of all revocations
```

---

### 7. ❌ Silent Failure on Invalid Tokens

**Problem**: Invalid tokens accepted without error reporting.

```
Pseudocode - Current State:
  function validateToken(token):
    try:
      payload = decode_and_verify(token)
      return payload
    catch:
      # ❌ All errors silently ignored
      return null
  
  function authorizeRequest(request):
    token = extract_token(request.headers)
    
    if not token:
      # ❌ Missing auth header silently allows request
      user = null
    else:
      user = validateToken(token)
    
    # ❌ Continue processing even with invalid token
    return processRequest(request, user)

Consequences:
  • No indication of auth failures in logs
  • Attackers can't tell if token format is wrong
  • Debugging authentication issues impossible
  • Security incidents go unnoticed
  • No audit trail of failed attempts
  • Rate limiting attacks on auth can't be detected
```

**Attack - Brute Force Token Discovery**:
1. Attacker sends 10,000 random tokens
2. All silently rejected with no logs
3. Attacker never knows format is wrong
4. Could continue indefinitely without detection
5. Security team has no idea of attack

**CORTEX Transformation**:
```
Target State:
  function validateToken(token):
    try:
      payload = decode_and_verify(token)
      audit_log.record('token_validated', user_id, ip_address)
      return payload
    except SignatureError as e:
      audit_log.warn('invalid_token_signature', token_hash, ip_address)
      raise InvalidTokenError("Token signature verification failed")
    except ExpiredError as e:
      audit_log.warn('token_expired', token_id, ip_address)
      raise InvalidTokenError("Token has expired")
    except InvalidFormatError as e:
      audit_log.warn('malformed_token', ip_address, token_format)
      raise InvalidTokenError("Token format invalid")
  
  function authorizeRequest(request):
    token = extract_token(request.headers)
    
    if not token:
      audit_log.warn('missing_auth_header', request.endpoint, ip_address)
      return error_response(401, "Authorization header required")
    
    try:
      user = validateToken(token)
    except InvalidTokenError as e:
      audit_log.warn('auth_failed', reason=str(e), ip_address)
      return error_response(401, "Invalid or expired token")
    
    return processRequest(request, user)

Monitoring:
  • Alert on > 5 failed auth attempts from same IP
  • Alert on token format errors (possible attack)
  • Alert on suspicious claim patterns
  • Track auth failure rate by endpoint

Benefits:
  ✅ All failures logged
  ✅ Attack detection possible
  ✅ Audit trail of auth events
  ✅ Rate limiting possible
  ✅ Security incidents visible
```

---

### 8. ❌ All Requests Require Authentication Token

**Problem**: No way to define public endpoints; strict authentication on everything.

```
Pseudocode - Current State:
  function authorizeRequest(request):
    endpoint = request.path
    
    # ❌ Every endpoint requires token
    token = extract_token(request.headers)
    if not token:
      return error_response(401, "Unauthorized")
    
    user = validateToken(token)
    if not user:
      return error_response(401, "Unauthorized")
    
    # All endpoints require user context
    request.user = user
    return processRequest(request)

Consequences:
  • Documentation endpoints require auth (breaks discoverability)
  • Health check endpoints require auth (breaks monitoring)
  • No way to list API capabilities without token
  • Third-party integration impossible
  • Public APIs can't be exposed
  • OAuth/OIDC flows broken
```

**Scenario - Service Integration Failure**:
1. Monitoring system tries to hit `/health` endpoint
2. Returns 401 (requires token)
3. Monitoring gives false alert (service down)
4. Cannot have anonymous health checks
5. Third parties cannot integrate

**CORTEX Transformation**:
```
Target State:
  function authorizeRequest(request):
    endpoint = request.path
    
    # Define public endpoints
    public_endpoints = {
      '/health',
      '/health/live',
      '/health/ready',
      '/api/docs',
      '/api/docs/swagger',
      '/api/version',
      '/auth/login',
      '/auth/register',
      '/auth/refresh'
    }
    
    # Check if endpoint is public
    if endpoint in public_endpoints:
      return processRequest(request, user=null)
    
    # Private endpoints require authentication
    token = extract_token(request.headers)
    if not token:
      return error_response(401, "Authorization required for this endpoint")
    
    user = validateToken(token)
    if not user:
      return error_response(401, "Invalid token")
    
    request.user = user
    return processRequest(request)
  
  @route('/health')  # Public
  function health():
    return {'status': 'healthy'}
  
  @route('/api/tasks')  # Private - requires auth
  @require_auth()
  function get_tasks(user):
    return tasks_for_user(user.id)

Configuration:
  public_endpoints:
    - /health
    - /health/*
    - /api/docs
    - /auth/login
    - /auth/register
    - /api/version
  
  protected_endpoints:
    - /api/tasks
    - /api/users
    - /api/admin

Benefits:
  ✅ Monitoring can check health
  ✅ Documentation discoverable
  ✅ OAuth flows work
  ✅ Third-party integration possible
  ✅ API versioning endpoints public
```

---

### 9-12. Additional Authentication Gaps

**9. ❌ No Rate Limiting on Auth Attempts**
- Credential stuffing attacks possible
- Brute force password guessing not throttled
- Account enumeration via timing attacks

**10. ❌ No Account Lockout After Failed Attempts**
- Unlimited password guessing
- No progressive delays
- Compromised accounts not flagged

**11. ❌ Passwords Stored in Plaintext/Weak Hash**
- Password breach = all accounts compromised
- No salt, weak algorithms
- Rainbow table attacks succeed

**12. ❌ No Multi-Factor Authentication Option**
- Single factor authentication weak
- Stolen passwords = full access
- No recovery mechanism

---

## Authorization Anti-Patterns (10 Critical Gaps)

### 13. ❌ Hard-Coded Authorization Rules in Code

**Problem**: Access control logic scattered throughout codebase.

```
Pseudocode - Current State:
  @route('/api/tasks/{id}')
  function update_task(task_id):
    # ❌ Auth check mixed with business logic
    user_name = get_current_user()
    
    if user_name not in ['admin', 'system', 'root']:
      return error_response(403, "Forbidden")
    
    task = get_task(task_id)
    task.update(request.json)
    return task
  
  @route('/api/users/{id}/delete')
  function delete_user(user_id):
    # ❌ Different auth check, hard-coded differently
    user = get_current_user()
    
    if user.id == 1:  # Hard-coded admin ID
      # Allow deletion
      delete_user(user_id)
      return {'status': 'deleted'}
    
    return error_response(403, "Forbidden")
  
  @route('/api/reports')
  function get_reports():
    # ❌ Yet another different auth check
    if not (get_current_user().role == 'admin' or 
            get_current_user().role == 'manager'):
      return error_response(403, "Forbidden")
    
    return get_all_reports()

Consequences:
  • Authorization logic duplicated everywhere
  • Inconsistent access control
  • Easy to miss authorization check
  • Hard to audit all access rules
  • Changes require code modifications across files
  • Testing authorization difficult
  • Role changes require code deployment
```

**Example - Authorization Bypass**:
1. Developer adds new endpoint: `/api/dangerous`
2. Forgets to add auth check
3. Public access to dangerous endpoint
4. No centralized review of access rules
5. Oversight goes unnoticed until audit

**CORTEX Transformation**:
```
Target State:
  # Centralized authorization policies
  authorization_policies = {
    '/api/tasks/create': ['user', 'admin'],
    '/api/tasks/{id}/update': ['admin'],
    '/api/tasks/{id}/delete': ['admin'],
    '/api/users/list': ['admin'],
    '/api/users/{id}/delete': ['admin'],
    '/api/reports': ['admin', 'manager'],
    '/api/admin/settings': ['admin'],
  }
  
  @route('/api/tasks/create')
  @require_role(['user', 'admin'])
  function create_task():
    return task_service.create(request.json)
  
  @route('/api/tasks/{id}/delete')
  @require_role(['admin'])
  function delete_task(task_id):
    return task_service.delete(task_id)
  
  @route('/api/users/list')
  @require_role(['admin'])
  function list_users():
    return user_service.list_all()
  
  # Authorization enforcement (centralized)
  def check_authorization(endpoint, user):
    required_roles = authorization_policies.get(endpoint)
    
    if not required_roles:
      raise UnauthenticatedError("Endpoint not defined in policy")
    
    if user.role not in required_roles:
      raise ForbiddenError(f"Role '{user.role}' not authorized for {endpoint}")
    
    audit_log.record('access_granted', user.id, endpoint)
    return true
  
  # Middleware enforces for all requests
  middleware.add(AuthorizationMiddleware(check_authorization))

Configuration:
  authorization_backend: database  # Store policies in DB
  policy_cache_ttl: 5_minutes
  audit_all_authorization: true
  emergency_override_enabled: false

Benefits:
  ✅ All rules in one place
  ✅ Consistent access control
  ✅ Easy to review access policies
  ✅ Changes don't require code deployment
  ✅ Comprehensive authorization audit
  ✅ New endpoints must declare requirements
  ✅ Role changes immediate (cached)
```

---

### 14. ❌ No Resource-Level Authorization

**Problem**: User can access any resource of a type, not just their own.

```
Pseudocode - Current State:
  @route('/api/tasks/{id}')
  function get_task(task_id):
    # ❌ Only checks if authenticated
    if not is_authenticated():
      return error_response(401, "Unauthorized")
    
    # ❌ No check if user owns this task
    task = get_task_by_id(task_id)
    return task
  
  # Any authenticated user can:
  # - View any task: /api/tasks/1, /api/tasks/2, ...
  # - View anyone's account: /api/users/123, /api/users/456, ...
  # - Modify anyone's data
  # - Delete anyone's resources

Consequences:
  • Any user can access any resource
  • Data isolation doesn't exist
  • Privilege escalation to any resource
  • Horizontal access control bypass
  • Multi-tenant data leaks
  • GDPR violations (unauthorized data access)
```

**Attack - Resource Enumeration**:
```
Attacker:
  1. Login with any account
  2. GET /api/tasks/1  (gets task 1)
  3. GET /api/tasks/2  (gets task 2)
  4. GET /api/tasks/3  (gets task 3)
  ... systematically enumerate all tasks
  5. GET /api/users/1  (gets user 1 profile)
  6. GET /api/users/2  (gets user 2 profile)
  ... view all user data

Result:
  • Complete data dump without authorization
  • All users' personal information exposed
  • All tasks visible to competitors
```

**CORTEX Transformation**:
```
Target State:
  @route('/api/tasks/{id}')
  def get_task(task_id):
    user = get_current_user()
    
    if not is_authenticated():
      return error_response(401, "Unauthorized")
    
    task = get_task_by_id(task_id)
    
    # Verify user owns this task
    if task.owner_id != user.id and user.role != 'admin':
      audit_log.warn('unauthorized_resource_access', user.id, 'task', task_id)
      return error_response(403, "Forbidden")
    
    audit_log.record('resource_accessed', user.id, 'task', task_id)
    return task
  
  @route('/api/users/{user_id}')
  def get_user_profile(user_id):
    user = get_current_user()
    
    if not is_authenticated():
      return error_response(401, "Unauthorized")
    
    # Only allow viewing own profile or admin viewing any profile
    if user_id != user.id and user.role != 'admin':
      audit_log.warn('unauthorized_profile_access', user.id, user_id)
      return error_response(403, "Forbidden")
    
    return get_user_by_id(user_id)
  
  @route('/api/tasks/{id}')
  @method('PUT')
  def update_task(task_id):
    user = get_current_user()
    task = get_task_by_id(task_id)
    
    # Owner can update own tasks
    # Admin can update any task
    if task.owner_id != user.id and user.role != 'admin':
      audit_log.warn('unauthorized_resource_update', user.id, 'task', task_id)
      return error_response(403, "Forbidden")
    
    task.update(request.json)
    audit_log.record('resource_updated', user.id, 'task', task_id)
    return task

Resource Authorization Rules:
  task:
    read: [owner, admin, task_viewer_role]
    write: [owner, admin]
    delete: [owner, admin]
  
  user_profile:
    read: [self, admin]
    write: [self, admin]
    delete: [admin]
  
  report:
    read: [admin, manager, report_viewer]
    write: [admin]
    delete: [admin]

Benefits:
  ✅ Users can only access own resources
  ✅ Data isolation enforced
  ✅ Privilege escalation prevented
  ✅ Multi-tenant safety
  ✅ GDPR compliance (no unauthorized access)
  ✅ Audit trail of all access
```

---

### 15-22. Additional Authorization Gaps

**15. ❌ No Audit Logging for Access Denials**
- Failed access attempts not logged
- Attack patterns invisible
- Compliance violations (SOC 2, HIPAA)

**16. ❌ Role/Permission Data in Code (Not Database)**
- Roles hard-coded as strings
- Role changes require deployment
- No dynamic permission updates

**17. ❌ No Permission Hierarchy or Inheritance**
- Each role must be explicitly defined
- Admin privileges not inherited by super-admin
- Impossible to create role groups

**18. ❌ Case-Sensitive Role Comparisons**
- Role: 'Admin' != 'admin'
- Typos cause access denials
- Inconsistent role naming

**19. ❌ No Delegation or Group-Based Access**
- Cannot grant access to teams/groups
- Only individual user grants
- Doesn't scale

**20. ❌ In-Memory Role Storage (Lost on Restart)**
- Roles added dynamically stored in memory
- App restart loses all custom roles
- No persistence for role changes

**21. ❌ Cache Never Invalidated**
- Role changes don't take effect
- Users keep old cached roles
- Could take hours to propagate

**22. ❌ No Emergency Override or Break Glass**
- Cannot grant access in emergencies
- Cannot revoke access in security incidents
- No incident response capability

---

## Summary: Auth/Authz Anti-Patterns

| # | Anti-Pattern | Severity | Risk |
|---|---|---|---|
| 1 | Hard-coded secrets | Critical | Breach radius = infrastructure |
| 2 | No signature verification | Critical | Token forgery |
| 3 | No expiration check | Critical | Permanent access |
| 4 | No issuer/audience | High | Cross-service attacks |
| 5 | Claims not validated | High | Injection attacks |
| 6 | No revocation mechanism | Critical | Compromised tokens work forever |
| 7 | Silent auth failures | High | Attack detection impossible |
| 8 | All requests require auth | Medium | Public APIs impossible |
| 9 | No rate limiting | High | Brute force attacks |
| 10 | No account lockout | High | Unlimited guessing |
| 11 | Weak password storage | Critical | Database breach = all accounts |
| 12 | No MFA | High | Single-factor weak |
| 13 | Hard-coded auth rules | High | Inconsistent enforcement |
| 14 | No resource-level auth | Critical | Horizontal privilege escalation |
| 15 | No audit logging | High | Compliance violations |
| 16 | Roles in code | Medium | Requires deployments |
| 17 | No permission hierarchy | Medium | Doesn't scale |
| 18 | Case-sensitive roles | Low | Inconsistent access |
| 19 | No delegation | Medium | Individual-only access |
| 20 | In-memory storage | High | Lost on restart |
| 21 | Cache never invalidated | High | Stale permissions |
| 22 | No emergency override | Medium | Incident response impossible |

---

## CORTEX Transformation Impact

### Before (Current BadMonolith State)
```
Vulnerabilities: 22 critical security gaps
Token Security: Unverified, non-expiring, globally scoped
Authorization: Hard-coded, inconsistent, no audit
Data Access: Any authenticated user can access anything
Incident Response: Cannot revoke access, emergency access impossible
Compliance: No audit trail, unauthorized access possible
```

### After (CORTEX Transformed)
```
Vulnerabilities: 0 (all addressed)
Token Security: Signed, expiring, scoped, revocable
Authorization: Policy-based, consistent, audited
Data Access: Resource-level control enforced
Incident Response: Emergency revocation possible
Compliance: Complete audit trail maintained
```

**Estimated CORTEX Transformation Time**: 8-12 hours  
**Code Changes Required**: 15-20 files  
**Test Coverage Needed**: 50+ new security tests  
**Deployment Strategy**: Blue-green with rollback capability

---

*Auth/Authz Anti-Patterns Catalog Complete*  
*Applicable to: Any tech stack (Java, Python, Node.js, Go, C#, Rust, etc.)*  
*Date: January 16, 2026*
