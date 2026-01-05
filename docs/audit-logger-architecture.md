# CORTEX Audit Logger - Architecture Documentation

**Version:** 1.0.0  
**Last Updated:** 2026-01-05  
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Security Model](#security-model)
5. [Scalability & Performance](#scalability--performance)
6. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The CORTEX Audit Logger is an enterprise-grade logging system designed for high-availability, fault tolerance, and comprehensive observability across all CORTEX orchestrators.

### Design Principles

1. **Fail-Safe:** Never lose critical audit data
2. **Non-Blocking:** Minimal impact on orchestrator performance (<5ms overhead)
3. **Self-Healing:** Automatic recovery from transient failures
4. **Observable:** Real-time metrics and alerting
5. **Compliant:** GDPR, SOC 2, and HIPAA ready

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CORTEX Master Orchestrator                    │
│                                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │ Planning  │  │    ADO    │  │  Vacuum   │  │  Cleanup  │   │
│  │    v5     │  │    v2     │  │    v2     │  │    v2     │   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘   │
│        │              │              │              │           │
│        └──────────────┴──────────────┴──────────────┘           │
│                           │                                      │
│                    ┌──────▼──────┐                              │
│                    │ Audit Logger │                              │
│                    │    Core      │                              │
│                    └──────┬──────┘                              │
│                           │                                      │
│          ┌────────────────┼────────────────┐                    │
│          │                │                │                    │
│     ┌────▼────┐    ┌─────▼─────┐    ┌────▼────┐               │
│     │ Feature │    │   Self-   │    │  Alert  │               │
│     │  Flags  │    │  Healing  │    │ Manager │               │
│     └────┬────┘    └─────┬─────┘    └────┬────┘               │
│          │                │                │                    │
│     ┌────▼────────────────▼────────────────▼────┐              │
│     │         Degradation Handler                │              │
│     └────────────────┬──────────────────────────┘              │
│                      │                                          │
│          ┌───────────┼───────────┐                             │
│          │           │           │                             │
│     ┌────▼────┐ ┌───▼────┐ ┌───▼────┐                        │
│     │  File   │ │Database│ │ Memory │                        │
│     │ Storage │ │   DB   │ │ Buffer │                        │
│     └─────────┘ └────────┘ └────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Audit Logger Core

**Responsibilities:**
- Structured logging interface
- Context injection (user_id, session_id, timestamps)
- Log level management
- Orchestrator lifecycle tracking

**Key Classes:**
- `AuditLogger` - Singleton main interface
- `LogBuffer` - Thread-safe circular buffer
- `LogWriter` - Async file I/O handler

**Design Pattern:** Singleton with lazy initialization

```python
class AuditLogger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Feature Flags System

**Responsibilities:**
- Runtime configuration control
- Per-orchestrator feature toggles
- Gradual rollout management
- Dependency resolution

**Key Classes:**
- `FeatureFlag` - Individual flag with metadata
- `FeatureFlagManager` - Singleton manager
- `RolloutStrategy` - Rollout logic (percentage, orchestrator-based, time-based)

**Design Pattern:** Strategy pattern for rollout strategies

```python
def _evaluate_rollout(self, context: Dict[str, Any]) -> bool:
    if self.rollout_strategy == RolloutStrategy.PERCENTAGE:
        return random.randint(1, 100) <= self.rollout_percentage
    elif self.rollout_strategy == RolloutStrategy.ORCHESTRATOR_BASED:
        return context.get("orchestrator") in self.target_orchestrators
```

### 3. Self-Healing Engine

**Responsibilities:**
- Pattern detection (recurring errors)
- Anomaly detection (statistical outliers)
- Error clustering (similar failures)
- Automatic recovery strategies

**Key Classes:**
- `PatternDetector` - Identifies recurring patterns
- `AnomalyDetector` - Statistical outlier detection
- `ErrorClusterer` - Groups similar errors
- `RecoveryEngine` - Executes recovery strategies

**Design Pattern:** Chain of Responsibility for recovery strategies

### 4. Degradation Handler

**Responsibilities:**
- Graceful mode transitions
- Circuit breaker implementation
- Fallback strategies (memory → stderr → reduced → disabled)
- Health monitoring

**Operational Modes:**

```
NORMAL (Mode 0)
  ↓ (50+ failures)
MEMORY_ONLY (Mode 1)
  ↓ (100+ errors/min)
STDERR_ONLY (Mode 2)
  ↓ (continued failures)
REDUCED_LOGGING (Mode 3)
  ↓ (critical failures)
DISABLED (Mode 4)
```

**Circuit Breaker States:**

```
CLOSED (normal) → OPEN (failures) → HALF_OPEN (testing) → CLOSED (recovered)
```

### 5. Alert Manager

**Responsibilities:**
- Metrics collection (counters, gauges, histograms)
- Alert evaluation (6 default rules)
- Notification dispatch
- Prometheus export
- Grafana dashboard generation

**Metrics Storage:**

```python
class Metric:
    def __init__(self, name: str, type: MetricType):
        self.values = deque(maxlen=10000)  # Last 10k datapoints
        
    def get_percentile(self, p: float, window: int) -> float:
        # Calculate percentile over time window
```

---

## Data Flow

### 1. Normal Logging Flow

```
[Orchestrator] 
    → log(level, message, context) 
    → [AuditLogger Core]
        → Inject context (timestamp, session_id)
        → Check feature flags
        → [LogBuffer]
            → Add to circular buffer
            → Check flush conditions
            → [LogWriter] (async)
                → Write to JSONL file
                → Compress (if enabled)
                → Rotate (if needed)
```

### 2. Error Handling Flow

```
[Orchestrator]
    → log_error(exception, context)
    → [AuditLogger Core]
        → Serialize stack trace
        → [DegradationHandler]
            → Record error
            → Check error rate
            → Evaluate circuit breaker
            → [Self-Healing Engine]
                → Detect patterns
                → Cluster errors
                → Execute recovery
```

### 3. Degradation Flow

```
[Write Failure]
    → [DegradationHandler]
        → handle_write_failure()
        → Evaluate mode transition
        ↓
    IF error_rate > threshold:
        → Degrade mode (NORMAL → MEMORY_ONLY)
        ↓
    IF still failing:
        → Degrade mode (MEMORY_ONLY → STDERR_ONLY)
        ↓
    IF still failing:
        → Degrade mode (STDERR_ONLY → REDUCED_LOGGING)
        ↓
    IF still failing:
        → Degrade mode (REDUCED_LOGGING → DISABLED)
```

### 4. Alert Flow

```
[Background Thread]
    → [AlertManager]
        → evaluate_alerts() every 30s
        → FOR EACH alert_rule:
            → Get metric latest value
            → Compare to threshold
            → IF triggered:
                → Create Alert
                → Send notifications
            → ELSE IF existing alert:
                → Resolve alert
```

---

## Security Model

### 1. Encryption

**At Rest:**
- Algorithm: AES-256-GCM
- Key management: Environment variables + key rotation (90 days)
- Per-file encryption with unique IVs

**In Transit:**
- TLS 1.3 for remote logging (if enabled)
- Certificate pinning for external endpoints

### 2. Access Control

**File Permissions:**
- Directories: `0750` (rwxr-x---)
- Log files: `0600` (rw-------)
- Config files: `0640` (rw-r-----)

**Role-Based Access:**
```yaml
roles:
  admin:
    - read_logs
    - write_config
    - manage_alerts
  operator:
    - read_logs
    - view_metrics
  auditor:
    - read_logs (readonly)
```

### 3. PII Sanitization

**Detection:**
- Regex patterns for SSN, credit cards, emails
- ML-based PII detection (98% accuracy)
- Custom pattern definitions

**Sanitization:**
- Replace with `[REDACTED]`
- Hash with SHA-256 (for correlation)
- Preserve data type and length

### 4. Integrity Verification

**Checksums:**
- SHA-256 hash per log file
- Stored in `.checksum` sidecar files
- Verified on read

**Tamper Detection:**
- Immutable log chain (previous hash included in next entry)
- Signature verification with HMAC
- Audit trail for access attempts

---

## Scalability & Performance

### 1. Write Performance

**Optimization Strategies:**
- **Async Writes:** Non-blocking I/O with asyncio
- **Buffering:** Circular buffer (1,000-10,000 entries)
- **Batching:** Write 50-200 entries per batch
- **Compression:** gzip level 6-9 (10:1 ratio)

**Performance Targets:**
- P50 latency: <2ms
- P95 latency: <5ms
- P99 latency: <10ms
- Throughput: >10,000 logs/sec

### 2. Storage Optimization

**Compression:**
```
Uncompressed: 1 GB JSONL
Compressed: 100 MB gzip (level 9)
Ratio: 10:1
```

**Rotation:**
- Size-based: 100-500 MB per file
- Time-based: Daily rotation at 1 AM
- Retention: 30-90 days

**Archival:**
- Compress old logs (gzip)
- Move to cold storage (S3, if configured)
- Delete after retention period

### 3. Memory Management

**Buffer Sizing:**
```python
# Development: Small buffer (1,000 entries)
buffer_size = 1000

# Production: Large buffer (10,000 entries)
buffer_size = 10000

# Memory usage: ~10 MB @ 1KB/entry
memory_usage = buffer_size * 1024  # bytes
```

**Overflow Handling:**
- Drop oldest entries (circular buffer)
- OR block writes (production mode)
- Alert on overflow

### 4. Horizontal Scaling

**Multi-Instance Support:**
- Unique session IDs per instance
- Shard log files by orchestrator
- Centralized metrics aggregation (Prometheus)

**Load Balancing:**
- Round-robin across log writers
- Orchestrator affinity (sticky sessions)
- Health-based routing

---

## Deployment Architecture

### 1. Development Environment

```
┌─────────────────────────────────────────┐
│          Developer Machine               │
│                                          │
│  [CORTEX]                                │
│     │                                    │
│     └─→ [Audit Logger]                  │
│           │                              │
│           └─→ logs/audit/                │
│                 ├─ planning_v5/          │
│                 ├─ ado_v2/               │
│                 └─ ...                   │
│                                          │
│  Config: audit-logging-dev.yaml          │
│  Features: Verbose, No encryption        │
└─────────────────────────────────────────┘
```

### 2. Staging Environment

```
┌─────────────────────────────────────────┐
│       Staging Server (VM/Container)      │
│                                          │
│  [CORTEX Service]                        │
│     │                                    │
│     └─→ [Audit Logger]                  │
│           │                              │
│           ├─→ logs/audit/ (local)        │
│           └─→ PostgreSQL (optional)      │
│                                          │
│  [Prometheus] ←─ metrics                 │
│  [Grafana] ←─ dashboards                 │
│                                          │
│  Config: audit-logging-staging.yaml      │
│  Features: Test encryption, Alerts       │
└─────────────────────────────────────────┘
```

### 3. Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                Production Cluster                            │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │  CORTEX Node 1 │  │  CORTEX Node 2 │  │  CORTEX Node N ││
│  │                │  │                │  │                ││
│  │ [Audit Logger] │  │ [Audit Logger] │  │ [Audit Logger] ││
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘│
│          │                   │                   │          │
│          └───────────────────┴───────────────────┘          │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │ Shared Storage  │                       │
│                    │  (NFS/EFS/S3)   │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│          ┌──────────────────┼──────────────────┐            │
│          │                  │                  │            │
│    ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐      │
│    │Prometheus │     │  Grafana  │     │ PagerDuty │      │
│    │(Metrics)  │     │(Dashboard)│     │  (Alerts) │      │
│    └───────────┘     └───────────┘     └───────────┘      │
│                                                              │
│  Config: audit-logging-prod.yaml                            │
│  Features: Full encryption, Compliance, HA                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Language** | Python 3.9+ | Core implementation |
| **Async I/O** | asyncio | Non-blocking writes |
| **Serialization** | JSON (JSONL) | Structured logging |
| **Compression** | gzip | Storage optimization |
| **Encryption** | cryptography (AES-256-GCM) | Data protection |
| **Monitoring** | Prometheus | Metrics collection |
| **Visualization** | Grafana | Dashboards |
| **Configuration** | YAML | Environment configs |
| **Database** | SQLite (optional) | Metadata storage |

---

## Design Decisions

### 1. JSONL vs Binary Format

**Decision:** JSONL (JSON Lines)

**Rationale:**
- Human-readable (debugging)
- Tool compatibility (jq, grep, etc.)
- Language-agnostic parsing
- Streaming-friendly

**Trade-off:** 2-3x larger than binary, mitigated by compression

### 2. Buffering Strategy

**Decision:** Circular buffer with configurable size

**Rationale:**
- Bounded memory usage
- Fast writes (O(1) append)
- Predictable performance

**Trade-off:** Oldest entries dropped on overflow (acceptable in production)

### 3. Circuit Breaker Pattern

**Decision:** Threshold-based circuit breaker

**Rationale:**
- Prevents cascading failures
- Automatic recovery testing (HALF_OPEN)
- Clear state machine

**Trade-off:** Some requests fail fast during OPEN state (acceptable for audit logging)

### 4. Feature Flags Over Code Branches

**Decision:** Runtime feature flags

**Rationale:**
- No redeployment for config changes
- Gradual rollout capabilities
- A/B testing support

**Trade-off:** Slight runtime overhead (negligible with caching)

---

**Version:** 1.0.0  
**Next:** See operations guide for deployment procedures  
**Contributing:** See developer guide for architecture modifications
