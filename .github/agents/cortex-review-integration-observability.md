# CORTEX Review Agent: Integration, Observability & Operational Flaws

## System Integration Issues, Monitoring Gaps & Production Readiness

**Purpose:** Identify gaps in system integration, missing observability, inadequate error visibility, and operational blindspots that cause silent failures or undetectable degradation in production.

**Why Critical:** Integration and observability failures are invisible during development but catastrophic in production. Problems go undetected until customer impact occurs.

---

## CHECKS PERFORMED

### 1. Integration Boundary Failures

**What to look for:**
- Missing error handling at system boundaries (API calls, DB, external services)
- No timeout configuration on external calls
- No retry logic with exponential backoff
- Silent failures (errors swallowed without logging)
- Incompatible data format assumptions between systems

**Search patterns:**
```bash
# Find external API calls
grep -rn "requests\.\|boto3\|api\.\|http\." cortex/ --include="*.py" | grep -v "test\|mock"

# Find database calls without error handling
grep -rn "\.query\|\.execute\|\.save\|\.delete" cortex/ --include="*.py" | grep -v "try\|except"

# Find missing timeout configuration
grep -rn "requests\.\|\.get\|\.post\|\.query" cortex/ --include="*.py" | grep -v "timeout"

# Find bare except (silent failures)
grep -rn "except:" cortex/ --include="*.py" | grep -v "ALLOWED\|pragma"

# Find external service assumptions
grep -rn "assume\|expect\|format.*=\|response\[" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ INTEGRATION FAILURE: No timeout on external call
def fetch_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    # If API hangs, this blocks forever!
    return response.json()

# ✅ FIX: Add timeout and retry
def fetch_user_data(user_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"https://api.example.com/users/{user_id}",
                timeout=5.0  # Fail fast
            )
            response.raise_for_status()
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"API call failed, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)

# ❌ INTEGRATION FAILURE: Silent failure
def sync_with_external_system():
    try:
        send_data_to_external_api(data)
    except:
        pass  # Silently ignore - data never synced!

# ✅ FIX: Proper error handling
def sync_with_external_system():
    try:
        send_data_to_external_api(data)
    except Exception as e:
        logger.error(f"Failed to sync with external API: {e}", exc_info=True)
        raise  # Propagate or handle appropriately

# ❌ INTEGRATION FAILURE: Assumption about data format
def parse_response(api_response):
    return api_response['user']['profile']['email']  # KeyError if structure changes

# ✅ FIX: Validate structure
def parse_response(api_response):
    try:
        user = api_response.get('user', {})
        profile = user.get('profile', {})
        email = profile.get('email')
        if not email:
            raise ValueError("Email not found in API response")
        return email
    except (TypeError, AttributeError) as e:
        logger.error(f"Unexpected API response format: {api_response}", exc_info=True)
        raise
```

---

### 2. Observability Gaps

**What to look for:**
- Missing logging at critical points
- No structured logging (makes log analysis hard)
- Missing metrics/counters for important operations
- No correlation IDs for distributed tracing
- Error messages that don't contain enough context
- No monitoring/alerting hooks

**Search patterns:**
```bash
# Find logging statements
grep -rn "logger\.\|print(" cortex/ --include="*.py" | wc -l

# Find critical sections without logging
grep -rn "def process\|def execute\|def handle\|def save" cortex/ --include="*.py" | head -20
# Then check if logged

# Find unstructured logging
grep -rn "logger\..*f\"\|logger\..*%" cortex/ --include="*.py"

# Find missing context in errors
grep -rn "raise.*Error\|raise.*Exception" cortex/ --include="*.py" | grep -v "message\|reason\|context"

# Find metrics/monitoring code
grep -rn "counter\|meter\|histogram\|gauge\|prometheus\|statsd" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ OBSERVABILITY: Missing context in error
def process_payment(amount):
    if amount <= 0:
        raise ValueError("Invalid amount")  # Missing: what amount was passed?

# ✅ FIX: Include context
def process_payment(amount):
    if amount <= 0:
        raise ValueError(f"Invalid amount: {amount}. Must be positive.")

# ❌ OBSERVABILITY: Unstructured logging
logger.info(f"User {user_id} processed {item_count} items")
# Hard to parse and aggregate in log analysis tools

# ✅ FIX: Structured logging
logger.info("User processed items", extra={
    "user_id": user_id,
    "item_count": item_count,
    "duration_ms": int((time.time() - start) * 1000),
})

# ❌ OBSERVABILITY: Missing correlation ID
def process_order(order_id):
    logger.info(f"Processing order {order_id}")
    fetch_user(order.user_id)  # No way to correlate these logs

# ✅ FIX: Use correlation ID
def process_order(order_id):
    correlation_id = request.headers.get("X-Correlation-ID")
    logger.info(f"Processing order", extra={
        "order_id": order_id,
        "correlation_id": correlation_id,
    })
    fetch_user(order.user_id, correlation_id=correlation_id)

# ❌ OBSERVABILITY: No metrics
def calculate_complex_value(data):
    result = expensive_calculation(data)  # How long does this take in production?
    return result

# ✅ FIX: Add metrics
def calculate_complex_value(data):
    start = time.time()
    result = expensive_calculation(data)
    duration_ms = (time.time() - start) * 1000
    metrics.histogram("calculation_duration_ms", duration_ms)
    logger.debug(f"Calculation completed in {duration_ms}ms")
    return result
```

---

### 3. Error Propagation & Recovery

**What to look for:**
- Errors swallowed without context
- No graceful degradation paths
- Missing fallback mechanisms
- Error handling too far from source (errors lose context)
- No circuit breaker for failing dependencies
- Health check endpoints not implemented

**Search patterns:**
```bash
# Find error suppression
grep -rn "except.*:\s*pass\|except.*:\s*return\|except.*:\s*continue" cortex/ --include="*.py"

# Find try/except without logging
grep -rn "try:" cortex/ --include="*.py" | head -30
# Check if corresponding except blocks log

# Find missing circuit breakers
grep -rn "circuit.*break\|fail.*fast\|fallback" cortex/ --include="*.py"

# Find health check endpoints
grep -rn "health\|status\|ping\|readiness\|liveness" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ ERROR SUPPRESSION: Silent failure
def get_config():
    try:
        return load_config_from_api()
    except:
        return DEFAULT_CONFIG  # Silent fallback

# ✅ FIX: Log and handle gracefully
def get_config():
    try:
        return load_config_from_api()
    except Exception as e:
        logger.warning(f"Failed to load config from API, using default: {e}")
        metrics.increment("config_load_failures")
        return DEFAULT_CONFIG

# ❌ ERROR RECOVERY: No circuit breaker
def call_external_service():
    # If service is down, we keep hammering it!
    return requests.get("https://external-service.com/api")

# ✅ FIX: Use circuit breaker
from pybreaker import CircuitBreaker

external_service_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

@external_service_breaker
def call_external_service():
    return requests.get("https://external-service.com/api", timeout=5)

# ❌ ERROR CONTEXT: Error loses context
def process_user_batch(users):
    for user in users:
        try:
            process_user(user)
        except Exception:
            # Which user failed? No context!
            pass

# ✅ FIX: Add context to error
def process_user_batch(users):
    for user in users:
        try:
            process_user(user)
        except Exception as e:
            logger.error(f"Failed to process user {user.id}", exc_info=True, extra={
                "user_id": user.id,
                "user_email": user.email,
            })
            # Decide: re-raise, continue, or queue for retry?
```

---

### 4. Data Consistency & Integrity

**What to look for:**
- No validation at system boundaries
- Missing version checks on imported data
- No checksum/hash verification
- Partial updates without rollback
- Missing cascade delete handling
- No referential integrity enforcement

**Search patterns:**
```bash
# Find validation code
grep -rn "validate\|check\|verify\|assert" cortex/ --include="*.py" | wc -l

# Find data imports/parsing
grep -rn "load\|parse\|deserialize\|from_dict" cortex/ --include="*.py"

# Find database operations without constraints
grep -rn "\.delete\|\.update\|\.insert" cortex/ --include="*.py" | grep -v "cascade"

# Find missing checksums/hashes
grep -rn "hash\|checksum\|digest\|integrity" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ DATA INTEGRITY: No validation on import
def import_user_data(data):
    user = User(**data)  # What if required fields missing?
    user.save()

# ✅ FIX: Validate before save
def import_user_data(data):
    required_fields = ['id', 'email', 'name']
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    
    user = User(**data)
    user.full_clean()  # Django validation
    user.save()

# ❌ DATA INTEGRITY: Partial update without atomicity
def update_user(user_id, name, email):
    user = User.get(user_id)
    user.name = name
    user.save()  # What if this fails?
    user.email = email
    user.save()  # Email never updated

# ✅ FIX: Atomic update
def update_user(user_id, name, email):
    user = User.get(user_id)
    with transaction.atomic():
        user.name = name
        user.email = email
        user.save()

# ❌ DATA INTEGRITY: Delete without cascade
def delete_user(user_id):
    user = User.get(user_id)
    user.delete()  # Orphaned posts left behind

# ✅ FIX: Define cascade behavior
class User(Model):
    # ...
    posts = relationship('Post', cascade='all,delete-orphan')
```

---

### 5. Deployment & Rollback Safety

**What to look for:**
- No backward compatibility checks for schema changes
- Missing data migration validation
- No feature flags for gradual rollout
- No rollback procedure documentation
- No deployment health checks

**Search patterns:**
```bash
# Find database schema changes
grep -rn "class Meta:\|db_column\|migration" cortex/ --include="*.py"

# Find feature toggles/flags
grep -rn "feature_enabled\|is_feature_on\|flag\|feature_flag" cortex/ --include="*.py"

# Find deployment configuration
grep -rn "version\|release\|tag\|build" cortex/ --include="*.py" | head -20
```

**Red Flags:**
```python
# ❌ DEPLOYMENT: Breaking schema change without backward compatibility
# Old version: user.email (string)
# New version:
class User:
    email = EmailField()  # Changed type - breaks if old code reads

# ✅ FIX: Gradual migration
# Step 1: Add new column, keep old
# Step 2: Dual-write to both columns
# Step 3: Migrate data
# Step 4: Code uses new column
# Step 5: Remove old column

# ❌ DEPLOYMENT: No feature flag for risky changes
def calculate_price():
    # New algorithm - what if it has a bug?
    return new_pricing_algorithm(item)

# ✅ FIX: Use feature flag
def calculate_price():
    if is_feature_enabled("new_pricing"):
        return new_pricing_algorithm(item)
    return old_pricing_algorithm(item)

# ❌ DEPLOYMENT: No health check
# Service deployed but no way to verify it's healthy

# ✅ FIX: Health check endpoint
@app.get("/health")
def health_check():
    checks = {
        "database": check_database(),
        "external_service": check_external_service(),
        "cache": check_cache(),
    }
    all_ok = all(checks.values())
    status_code = 200 if all_ok else 503
    return {"status": "ok" if all_ok else "error", "checks": checks}, status_code
```

---

### 6. Configuration Management

**What to look for:**
- Hard-coded configuration values
- Missing environment-specific configurations
- No configuration validation on startup
- Configuration secrets exposed in logs
- Configuration changes require redeployment

**Search patterns:**
```bash
# Find hard-coded values
grep -rn "= \"[a-zA-Z0-9]\+\"\|= '[a-zA-Z0-9]\+'\|= [0-9]\+" cortex/ --include="*.py" | grep -v "test\|assert"

# Find environment variables
grep -rn "os\.environ\|os\.getenv\|getenv" cortex/ --include="*.py"

# Find configuration files
find cortex/ -name "*.config\|*.conf\|*.yml\|*.yaml" -type f
```

**Red Flags:**
```python
# ❌ CONFIG: Hard-coded values
API_KEY = "sk_live_ABC123"
DB_HOST = "prod-db.example.com"
MAX_RETRIES = 5

# ✅ FIX: Use environment variables and defaults
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

DB_HOST = os.getenv("DB_HOST", "localhost")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ❌ CONFIG: Secrets in logs
logger.info(f"Connecting to database with password: {db_password}")

# ✅ FIX: Never log secrets
logger.info(f"Connecting to database {db_host}")
```

---

### 7. Production Readiness Checklist

**What to look for:**
- Missing monitoring endpoints
- No graceful shutdown handling
- No request rate limiting
- No request size limits
- No database connection pooling
- Missing authentication/authorization enforcement

**Search patterns:**
```bash
# Find monitoring setup
grep -rn "prometheus\|statsd\|monitoring\|metrics" cortex/ --include="*.py"

# Find shutdown handling
grep -rn "shutdown\|cleanup\|finally\|atexit" cortex/ --include="*.py"

# Find rate limiting
grep -rn "rate.*limit\|throttle\|ratelimit" cortex/ --include="*.py"

# Find auth middleware
grep -rn "authenticate\|authorize\|permission\|token\|jwt" cortex/ --include="*.py"

# Find connection pooling
grep -rn "pool\|poolsize\|max.*connection" cortex/ --include="*.py"
```

---

## OUTPUT FORMAT

**Create YAML report:** `_workspaces/roadmap/issues/Findings-INTEG-YYYYMMDD.yaml`

```yaml
integration_observability_findings:
  metadata:
    agent: "INTEGRATION_OBSERVABILITY_OPERATIONAL"
    timestamp: "2026-01-23T14:30:00Z"
    confidence_grades: ["A", "B"]
    evidence_locations: ["cortex/api/", "cortex/execution/", "cortex/infrastructure/"]

  integration_boundary_failures:
    - finding_id: "INTEG-001"
      severity: "CRITICAL"
      component: "cortex/api/external_service_client.py"
      issue: "No timeout on external API calls"
      lines: [45, 67, 89]
      evidence_grade: "A"
      evidence_text: "requests.get() calls at lines 45, 67, 89 lack timeout parameter"
      affected_ac_ids: ["AC-API-001"]
      fix_complexity: "LOW"
      
    - finding_id: "INTEG-002"
      severity: "CRITICAL"
      component: "cortex/execution/executor.py"
      issue: "Silent failures in error handling (bare except)"
      error_suppression_count: 3
      evidence_grade: "A"
      affected_ac_ids: ["AC-EXEC-002"]

  observability_gaps:
    - finding_id: "OBS-001"
      severity: "HIGH"
      component: "cortex/orchestrators/orchestrator.py"
      issue: "Missing structured logging at critical points"
      critical_points_unlogged: 8
      evidence_grade: "B"
      example: "process_phase() has no logging - cannot debug phase failures in production"
      affected_ac_ids: ["AC-ORCH-001"]
      
    - finding_id: "OBS-002"
      severity: "MEDIUM"
      component: "cortex/api/"
      issue: "No correlation IDs for distributed tracing"
      evidence_grade: "B"
      current_state: "All API calls isolated, cannot trace request through system"
      affected_ac_ids: ["AC-API-002"]

  error_recovery_gaps:
    - finding_id: "ERR-001"
      severity: "HIGH"
      component: "cortex/infrastructure/external_api.py"
      issue: "No circuit breaker for failing dependency"
      failure_scenario: "If external service is down, all calls timeout"
      evidence_grade: "B"
      affected_ac_ids: ["AC-INFRA-001"]
      
  data_integrity_gaps:
    - finding_id: "DATA-001"
      severity: "MEDIUM"
      component: "cortex/models/"
      issue: "No input validation at service boundaries"
      missing_validations: 5
      evidence_grade: "A"
      affected_ac_ids: ["AC-MODEL-001"]

  deployment_safety_gaps:
    - finding_id: "DEPLOY-001"
      severity: "MEDIUM"
      component: "cortex/api/"
      issue: "No health check endpoint"
      evidence_grade: "A"
      impact: "Cannot verify deployment health before routing traffic"
      affected_ac_ids: ["AC-DEPLOY-001"]

  summary:
    critical_findings: 2
    high_findings: 4
    medium_findings: 5
    total_integration_issues: 11
    production_ready: false
    recommendation: "Address CRITICAL integration failures before production deployment"
```

---

## DECISION LOGIC

```yaml
decision_tree:
  found_critical_integration_failure:
    issue: "External calls without timeout"
    severity: "CRITICAL"
    action: "FIX IMMEDIATELY - Add timeout to all external calls"
    timeline: "URGENT (2 hours)"
    blocks_production: true
    
  found_observability_gap:
    issue: "Missing critical logging/metrics"
    severity: "HIGH"
    action: "Add structured logging and metrics collection"
    timeline: "Before production"
    blocks_production: true
    
  found_error_suppression:
    issue: "Bare except or silent failures"
    severity: "HIGH"
    action: "Replace with proper error handling and logging"
    timeline: "Before production"
    blocks_production: true
    
  missing_health_checks:
    issue: "No health/readiness endpoints"
    severity: "MEDIUM"
    action: "Implement health check endpoints"
    timeline: "Before production"
    blocks_production: true
```
