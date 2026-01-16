# TECHNICAL IMPLEMENTATION GUIDE: Domain Brain Architecture

**Date**: January 16, 2026  
**Phase**: Pre-Phase 1 Planning  
**Audience**: Implementation Team (Architects, Backend Engineers, QA)

---

## TABLE OF CONTENTS
1. [Pre-Phase 1 Decisions](#pre-phase-1-decisions)
2. [Domain Brain API Specification](#domain-brain-api-specification)
3. [Data Model Definition](#data-model-definition)
4. [Implementation Components](#implementation-components)
5. [Testing Strategy](#testing-strategy)
6. [Performance Targets](#performance-targets)

---

## PRE-PHASE 1 DECISIONS

### Decision 1: Storage Mechanism

**Option A: File-Based (YAML in Git)**
```yaml
cortex-brain/tier3/domains/
├── cortex/
│   ├── authentication.yaml
│   ├── api-layer.yaml
│   └── database-layer.yaml
├── business/
│   ├── customer-lifecycle.yaml
│   ├── revenue-operations.yaml
│   └── risk-management.yaml
└── mappings/
    ├── customer_to_apis.yaml
    └── revenue_to_services.yaml
```

**Pros:**
- ✅ Git-backed (version history)
- ✅ Human-readable (can review changes)
- ✅ Auditable (commit messages)
- ✅ Zero infrastructure (no database)

**Cons:**
- ❌ Slower for large domains (must parse entire YAML)
- ❌ Harder to query (linear search)
- ❌ Concurrent writes risky (merge conflicts)

**Option B: SQLite with Git Checkpoints**
```python
# cortex-brain/domain-brain.db (SQLite)
# Automatically committed as checkpoint
```

**Pros:**
- ✅ Fast queries (indexed)
- ✅ Queryable (SQL)
- ✅ Handles concurrent writes
- ✅ Can do transactions

**Cons:**
- ❌ Binary format (harder to review)
- ❌ Schema migrations needed
- ❌ Infrastructure overhead

**RECOMMENDATION**: **Option A (File-Based)**
- Aligns with CORTEX's "code as config" philosophy
- Performance adequate for knowledge workload (domains << code)
- Simplicity trumps optimization (start here, optimize later if needed)

---

### Decision 2: Conflict Resolution Strategy

**When Source A and Source B define domain D differently:**

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **MERGE** | Combine all perspectives | Non-contradicting attributes |
| **LENS_SYNTHESIZE** | Ask LENS to reconcile | Complex conflicts |
| **DEFER** | Mark for manual review | Safety-critical conflicts |
| **SOURCE_PRIORITY** | Hierarchy wins | When hierarchy is known |

**Conflict Hierarchy (recommended):**
```python
CONFLICT_HIERARCHY = {
    "BKIO": 1,              # Business knows business domains best
    "RELATIONSHIPS": 2,     # Code relationships are factual
    "AST": 3,              # AST is factual but limited
    "GIT": 4,              # Git history is factual but coarse
    "LENS": 5,             # LENS is synthesized (lower priority)
}
```

**RECOMMENDATION**: **HIERARCHY + DEFER**
- Priority: BKIO > RELATIONSHIPS > AST > GIT > LENS
- If conflict involves different priorities: higher wins
- If conflict within same priority: DEFER to manual review

---

### Decision 3: Approval Workflow

**For Business Domain Ingestion (BKIO):**

| Step | Actor | Action |
|------|-------|--------|
| 1 | BKIO | Scan business documents |
| 2 | BKIO | Parse and extract domains |
| 3 | BKIO | Validate against schema |
| 4 | BKIO | Display extracted data |
| 5 | Human | Review and approve/reject |
| 6 | BKIO | Publish if approved |
| 7 | BKIO | Log audit entry with approver |

**Approval Gate Implementation:**
```python
class ApprovalGate:
    """Interactive approval mechanism."""
    
    def request_approval(self, domain_data: Dict, entities: List[str]) -> Result[bool]:
        """Request human approval for domain ingestion."""
        
        print(f"\n{'='*60}")
        print(f"Domain: {domain_data['domain_id']}")
        print(f"Name: {domain_data['domain_name']}")
        print(f"Entities found: {len(entities)}")
        print("-" * 60)
        for entity in entities:
            print(f"  • {entity}")
        print(f"{'='*60}\n")
        
        while True:
            response = input("Approve ingestion? [Y/N/Review]: ").strip().upper()
            if response == "Y":
                return Ok(True)
            elif response == "N":
                return Ok(False)
            elif response == "REVIEW":
                self._show_detailed_review(domain_data)
```

**RECOMMENDATION**: **Interactive (CLI-based)**
- Simple, no tool dependencies
- Human can review before approving
- Audit trail includes approval timestamp/user

---

### Decision 4: API Specification

**Core API Operations:**

```python
class DomainBrainAPI:
    """Canonical API for Domain Brain operations."""
    
    # =========================================================================
    # QUERY OPERATIONS
    # =========================================================================
    
    async def query_domain(
        self,
        domain_id: str,
        version: Optional[str] = None,  # ISO timestamp or "latest"
    ) -> Result[Dict[str, Any]]:
        """Query a domain definition.
        
        Args:
            domain_id: Unique domain identifier
            version: Version to retrieve (default: latest)
        
        Returns:
            Result containing domain dict or error
        
        Raises:
            DomainNotFoundError: If domain doesn't exist
        """
    
    async def list_domains(
        self,
        tier: Optional[str] = None,  # "CORTEX" or "BUSINESS"
        source: Optional[str] = None,  # "AST", "BKIO", etc.
    ) -> Result[List[str]]:
        """List all domains with optional filtering.
        
        Returns:
            Result containing list of domain IDs
        """
    
    async def search_domains(
        self,
        query: str,
    ) -> Result[List[Dict]]:
        """Search domains by name or attributes.
        
        Returns:
            Result containing matching domains
        """
    
    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================
    
    async def upsert_domain(
        self,
        domain_id: str,
        domain_data: Dict[str, Any],
        source: str,  # "AST", "BKIO", "RELATIONSHIPS", "GIT", "LENS"
        ac_id: str,
        approved_by: Optional[str] = None,
    ) -> Result[None]:
        """Create or update a domain.
        
        Args:
            domain_id: Unique domain identifier
            domain_data: Domain definition (must pass schema validation)
            source: Component that created/updated domain
            ac_id: Acceptance Criteria ID (for audit)
            approved_by: Human approver (if required)
        
        Returns:
            Result with success/error
        
        Side effects:
            • Validates domain_data against schema
            • Detects conflicts with existing domain
            • Creates audit trail entry
            • Computes and records hash chain
        
        Raises:
            SchemaValidationError: If domain_data invalid
            ConflictDetectedError: If conflicts found
        """
    
    async def delete_domain(
        self,
        domain_id: str,
        ac_id: str,
        reason: str,
    ) -> Result[None]:
        """Delete a domain (with reason for audit trail).
        
        Returns:
            Result with success/error
        
        Side effects:
            • Does NOT physically delete (immutable)
            • Marks as "deleted" with timestamp + reason
            • Creates audit trail entry
        """
    
    # =========================================================================
    # CONFLICT RESOLUTION
    # =========================================================================
    
    async def detect_conflicts(
        self,
        new_domain: Dict[str, Any],
        existing_domain: Dict[str, Any],
    ) -> Result[List[ConflictDescriptor]]:
        """Detect conflicts between two domain versions.
        
        Returns:
            Result containing list of conflicts (or empty if none)
        
        Example conflicts:
            • Return type changed: AuthToken → User
            • Entity removed: lifecycle_stage removed
            • Mapping broken: API endpoint no longer exists
        """
    
    async def resolve_conflict(
        self,
        domain_id: str,
        conflict_id: str,
        resolution: ConflictResolution,  # MERGE | DEFER | HIERARCHY
        ac_id: str,
    ) -> Result[None]:
        """Resolve a detected conflict.
        
        Returns:
            Result with success/error
        
        Side effects:
            • Updates domain based on resolution strategy
            • Creates audit trail entry
            • May trigger human review if DEFER
        """
    
    # =========================================================================
    # AUDIT & VERSIONING
    # =========================================================================
    
    async def get_audit_trail(
        self,
        domain_id: str,
    ) -> Result[List[AuditEntry]]:
        """Get complete audit trail for a domain.
        
        Returns:
            Result containing list of audit entries (chronological)
        
        Each entry contains:
            {
                "timestamp": "2026-01-16T10:30:00Z",
                "operation": "CREATE",
                "source": "AST",
                "ac_id": "IR-001-01",
                "approved_by": "alice@example.com",
                "hash": "a1b2c3d4...",
                "previous_hash": "9z8y7x6w...",
                "change_summary": "Added function authenticate()"
            }
        """
    
    async def get_domain_versions(
        self,
        domain_id: str,
    ) -> Result[List[str]]:
        """Get list of all historical versions (timestamps).
        
        Returns:
            Result containing list of ISO timestamps
        """
    
    async def get_domain_at_version(
        self,
        domain_id: str,
        timestamp: str,
    ) -> Result[Dict[str, Any]]:
        """Get domain state at specific timestamp.
        
        Returns:
            Result containing domain as it was at that time
        """
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    async def validate_domain(
        self,
        domain_data: Dict[str, Any],
    ) -> Result[None]:
        """Validate domain against schema (without writing).
        
        Returns:
            Result with success or validation errors
        
        Checks:
            • Required fields present
            • Type constraints satisfied
            • Referential integrity
            • No circular dependencies
        """
```

---

## DOMAIN BRAIN API SPECIFICATION

### Data Model

```python
@dataclass
class Domain:
    """Represents a domain definition."""
    
    domain_id: str                           # Unique identifier
    domain_name: str                         # Human-readable name
    tier: str                                # "CORTEX" or "BUSINESS"
    entities: List[Entity]                   # Contained entities
    mappings: List[Mapping]                  # Cross-domain mappings
    metadata: DomainMetadata                 # Created/modified info
    audit_entries: List[AuditEntry]         # Immutable change log

@dataclass
class Entity:
    """Represents an entity within a domain."""
    
    entity_id: str                           # Unique within domain
    entity_name: str                         # Human-readable
    entity_type: str                         # "function", "class", "concept"
    attributes: Dict[str, Any]               # Flexible attributes
    relationships: List[str]                 # Entity IDs this relates to

@dataclass
class Mapping:
    """Represents a mapping between two domains."""
    
    mapping_id: str                          # Unique identifier
    from_domain: str                         # Source domain_id
    to_domain: str                           # Target domain_id
    from_entity: Optional[str]               # Specific entity (if applicable)
    to_entity: Optional[str]                 # Specific entity (if applicable)
    relationship: str                        # Description of relationship
    strength: float                          # 0.0-1.0 confidence

@dataclass
class DomainMetadata:
    """Metadata about domain creation/modification."""
    
    created_at: str                          # ISO timestamp
    created_by_ac_id: str                    # AC-ID that created
    modified_at: str                         # ISO timestamp
    modified_by: str                         # Source component
    approved_by: Optional[str]               # Human approver (if applicable)
    version: str                             # Semantic version
    status: str                              # "active", "deprecated", "deleted"

@dataclass
class AuditEntry:
    """Single audit trail entry."""
    
    timestamp: str                           # ISO timestamp
    operation: str                           # "CREATE", "UPDATE", "DELETE"
    source: str                              # "AST", "BKIO", etc.
    ac_id: str                               # Acceptance Criteria ID
    approved_by: Optional[str]               # Human approver
    hash: str                                # SHA-256 of this entry
    previous_hash: str                       # Previous hash (for chain)
    change_summary: str                      # Human-readable change
    details: Optional[Dict]                  # Additional details

@dataclass
class ConflictDescriptor:
    """Describes a detected conflict."""
    
    conflict_id: str                         # Unique identifier
    domain_id: str                           # Which domain
    conflict_type: str                       # "TYPE_CHANGE", "ENTITY_REMOVED", etc.
    severity: str                            # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str                         # Human-readable description
    old_value: Any                           # Previous value
    new_value: Any                           # Proposed value
    suggested_resolution: str                # "MERGE", "DEFER", "HIERARCHY"
```

### Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Domain Definition",
  "type": "object",
  "properties": {
    "domain_id": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$",
      "minLength": 3,
      "maxLength": 50,
      "description": "Unique domain identifier"
    },
    "domain_name": {
      "type": "string",
      "minLength": 3,
      "maxLength": 100,
      "description": "Human-readable domain name"
    },
    "tier": {
      "type": "string",
      "enum": ["CORTEX", "BUSINESS"],
      "description": "Domain tier classification"
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "entity_id": {"type": "string"},
          "entity_name": {"type": "string"},
          "entity_type": {
            "type": "string",
            "enum": ["function", "class", "concept", "process", "rule"]
          },
          "attributes": {"type": "object"},
          "relationships": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["entity_id", "entity_name", "entity_type"]
      },
      "minItems": 1,
      "description": "Entities within this domain"
    },
    "mappings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "mapping_id": {"type": "string"},
          "from_domain": {"type": "string"},
          "to_domain": {"type": "string"},
          "relationship": {"type": "string"},
          "strength": {"type": "number", "minimum": 0, "maximum": 1}
        },
        "required": ["mapping_id", "from_domain", "to_domain", "relationship"]
      },
      "description": "Cross-domain mappings"
    }
  },
  "required": ["domain_id", "domain_name", "tier", "entities"],
  "additionalProperties": false
}
```

---

## IMPLEMENTATION COMPONENTS

### Component 1: DomainBrainAPI

**File**: `src/core/domain_brain/domain_brain_api.py`  
**Size**: ~300 lines  
**Tests**: ~200 lines  
**Dependencies**: ConsistencyValidator, AuditLogger

```python
class DomainBrainAPI:
    """Core API for Domain Brain operations."""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.domains_path = self.workspace_root / "cortex-brain/tier3/domains"
        self.domains_path.mkdir(parents=True, exist_ok=True)
        
        self.validator = ConsistencyValidator()
        self.audit_logger = AuditLogger(self.workspace_root)
        
        self._domain_cache = {}  # In-memory cache with TTL
        self._cache_ttl = 300    # 5 minutes
    
    async def query_domain(self, domain_id: str) -> Result[Dict]:
        """Query domain from disk or cache."""
        # 1. Check cache
        if domain_id in self._domain_cache:
            return Ok(self._domain_cache[domain_id])
        
        # 2. Load from disk
        file_path = self.domains_path / f"{domain_id}.yaml"
        if not file_path.exists():
            return Err(DomainNotFoundError(domain_id))
        
        # 3. Parse YAML
        try:
            with open(file_path) as f:
                domain_data = yaml.safe_load(f)
            
            # 4. Cache result
            self._domain_cache[domain_id] = domain_data
            return Ok(domain_data)
        except Exception as e:
            return Err(str(e))
    
    async def upsert_domain(
        self,
        domain_id: str,
        domain_data: Dict,
        source: str,
        ac_id: str,
        approved_by: Optional[str] = None,
    ) -> Result[None]:
        """Create or update domain."""
        # 1. Validate schema
        validation_result = await self.validator.validate(domain_data)
        if validation_result.is_err():
            return validation_result
        
        # 2. Check for conflicts
        existing = await self.query_domain(domain_id)
        if existing.is_ok():
            conflicts = await self.detect_conflicts(
                domain_data,
                existing.unwrap()
            )
            if conflicts.is_err():
                return conflicts
            
            if conflicts.unwrap():
                # Handle conflicts based on strategy
                result = await self._handle_conflicts(
                    domain_id,
                    domain_data,
                    conflicts.unwrap()
                )
                if result.is_err():
                    return result
        
        # 3. Write to disk
        file_path = self.domains_path / f"{domain_id}.yaml"
        try:
            with open(file_path, 'w') as f:
                yaml.dump(domain_data, f)
        except Exception as e:
            return Err(f"Failed to write domain: {e}")
        
        # 4. Create audit entry
        await self.audit_logger.log_operation(
            domain_id=domain_id,
            operation="UPSERT",
            source=source,
            ac_id=ac_id,
            approved_by=approved_by,
            details=domain_data
        )
        
        # 5. Invalidate cache
        if domain_id in self._domain_cache:
            del self._domain_cache[domain_id]
        
        return Ok(None)
```

### Component 2: ConsistencyValidator

**File**: `src/core/domain_brain/consistency_validator.py`  
**Size**: ~250 lines  
**Tests**: ~150 lines  

```python
class ConsistencyValidator:
    """Validates domains against schema."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        if schema_path is None:
            schema_path = (
                Path(__file__).parent / "schemas" / "domain-schema.json"
            )
        
        with open(schema_path) as f:
            self.schema = json.load(f)
        
        self.validator = jsonschema.Draft7Validator(self.schema)
    
    async def validate(self, domain_data: Dict) -> Result[None]:
        """Validate domain against schema."""
        errors = []
        
        # 1. JSON Schema validation
        for error in self.validator.iter_errors(domain_data):
            errors.append(f"Schema error: {error.message}")
        
        if errors:
            return Err(f"Validation failed: {', '.join(errors)}")
        
        # 2. Referential integrity checks
        domain_id = domain_data.get("domain_id")
        entities = domain_data.get("entities", [])
        mappings = domain_data.get("mappings", [])
        
        entity_ids = {e["entity_id"] for e in entities}
        
        for mapping in mappings:
            from_entity = mapping.get("from_entity")
            to_entity = mapping.get("to_entity")
            
            if from_entity and from_entity not in entity_ids:
                errors.append(
                    f"Mapping references unknown entity: {from_entity}"
                )
        
        if errors:
            return Err(f"Referential integrity: {', '.join(errors)}")
        
        # 3. Circular dependency checks
        if self._has_circular_dependency(mappings):
            errors.append("Circular dependency detected")
        
        if errors:
            return Err(f"Circular dependency: {', '.join(errors)}")
        
        return Ok(None)
    
    async def detect_conflicts(
        self,
        new_domain: Dict,
        existing_domain: Dict,
    ) -> Result[List[ConflictDescriptor]]:
        """Detect conflicts between domain versions."""
        conflicts = []
        
        # 1. Entity type changes
        old_types = {e["entity_id"]: e["entity_type"] 
                     for e in existing_domain.get("entities", [])}
        new_types = {e["entity_id"]: e["entity_type"] 
                     for e in new_domain.get("entities", [])}
        
        for entity_id in old_types:
            if entity_id in new_types:
                if old_types[entity_id] != new_types[entity_id]:
                    conflicts.append(ConflictDescriptor(
                        conflict_id=f"TYPE_{entity_id}",
                        domain_id=new_domain["domain_id"],
                        conflict_type="TYPE_CHANGE",
                        severity="MEDIUM",
                        description=f"Entity {entity_id} type changed",
                        old_value=old_types[entity_id],
                        new_value=new_types[entity_id],
                    ))
        
        # 2. Removed entities
        for entity_id in old_types:
            if entity_id not in new_types:
                conflicts.append(ConflictDescriptor(
                    conflict_id=f"REMOVED_{entity_id}",
                    domain_id=new_domain["domain_id"],
                    conflict_type="ENTITY_REMOVED",
                    severity="HIGH",
                    description=f"Entity {entity_id} removed",
                    old_value=entity_id,
                    new_value=None,
                ))
        
        return Ok(conflicts)
```

### Component 3: AuditLogger

**File**: `src/core/domain_brain/audit_logger.py`  
**Size**: ~200 lines  
**Tests**: ~150 lines  

```python
class AuditLogger:
    """Maintains immutable audit trail with hash chain."""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.audit_path = (
            self.workspace_root / "cortex-brain/tier3/audit-trail"
        )
        self.audit_path.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.audit_path / "domain-updates.log"
        self._current_hash = self._load_last_hash()
    
    async def log_operation(
        self,
        domain_id: str,
        operation: str,
        source: str,
        ac_id: str,
        approved_by: Optional[str],
        details: Dict,
    ) -> Result[None]:
        """Log operation to immutable audit trail."""
        
        # 1. Create entry
        timestamp = datetime.utcnow().isoformat() + "Z"
        entry_content = {
            "timestamp": timestamp,
            "domain_id": domain_id,
            "operation": operation,
            "source": source,
            "ac_id": ac_id,
            "approved_by": approved_by,
            "details_hash": self._hash_object(details),
        }
        
        # 2. Compute hash
        entry_json = json.dumps(entry_content, sort_keys=True)
        current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        
        # 3. Create chain entry
        chain_entry = {
            "timestamp": timestamp,
            "domain_id": domain_id,
            "operation": operation,
            "source": source,
            "ac_id": ac_id,
            "hash": current_hash,
            "previous_hash": self._current_hash,
        }
        
        # 4. Write to audit log
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(chain_entry) + "\n")
            
            self._current_hash = current_hash
            return Ok(None)
        except Exception as e:
            return Err(f"Failed to write audit log: {e}")
    
    async def get_audit_trail(
        self,
        domain_id: str,
    ) -> Result[List[Dict]]:
        """Retrieve audit trail for domain."""
        entries = []
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry["domain_id"] == domain_id:
                        entries.append(entry)
            
            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to read audit log: {e}")
    
    def _hash_object(self, obj: Dict) -> str:
        """Compute SHA-256 hash of object."""
        json_str = json.dumps(obj, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _load_last_hash(self) -> str:
        """Load last hash from audit log."""
        if not self.log_file.exists():
            return "0" * 64  # Initial hash
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry["hash"]
        except:
            pass
        
        return "0" * 64
```

---

## TESTING STRATEGY

### Test Structure

```
tests/unit/domain_brain/
├── test_domain_brain_api.py       (50+ tests)
├── test_consistency_validator.py  (40+ tests)
├── test_audit_logger.py           (30+ tests)
└── fixtures/
    └── sample_domains.yaml        (test data)

tests/integration/domain_brain/
├── test_domain_brain_full_flow.py (20+ tests)
└── test_conflict_resolution.py    (15+ tests)
```

### Unit Tests: DomainBrainAPI

```python
class TestDomainBrainAPI:
    """Test DomainBrainAPI class."""
    
    @pytest.mark.ac("BD-002-01-01")
    def test_query_domain_not_found(self):
        """Should return error for non-existent domain."""
        api = DomainBrainAPI()
        result = api.query_domain("non-existent")
        assert result.is_err()
        assert "not found" in str(result).lower()
    
    @pytest.mark.ac("BD-002-01-01")
    def test_upsert_domain_valid(self):
        """Should successfully insert valid domain."""
        api = DomainBrainAPI()
        domain_data = {
            "domain_id": "test-domain",
            "domain_name": "Test Domain",
            "tier": "CORTEX",
            "entities": [
                {
                    "entity_id": "test-entity",
                    "entity_name": "Test Entity",
                    "entity_type": "function"
                }
            ]
        }
        
        result = api.upsert_domain(
            domain_id="test-domain",
            domain_data=domain_data,
            source="TEST",
            ac_id="AC-TEST-01"
        )
        
        assert result.is_ok()
    
    @pytest.mark.ac("BD-002-01-02")
    def test_upsert_domain_invalid_schema(self):
        """Should reject domain with invalid schema."""
        api = DomainBrainAPI()
        domain_data = {
            "domain_id": "test-domain",
            # Missing required: domain_name, tier
        }
        
        result = api.upsert_domain(
            domain_id="test-domain",
            domain_data=domain_data,
            source="TEST",
            ac_id="AC-TEST-01"
        )
        
        assert result.is_err()
        assert "schema" in str(result).lower() or "required" in str(result).lower()
    
    @pytest.mark.ac("BD-002-01-03")
    def test_conflict_detection(self):
        """Should detect conflicts between domain versions."""
        api = DomainBrainAPI()
        
        old_domain = {
            "domain_id": "auth",
            "entities": [
                {"entity_id": "authenticate", "entity_type": "function"}
            ]
        }
        
        new_domain = {
            "domain_id": "auth",
            "entities": [
                {"entity_id": "authenticate", "entity_type": "class"}
            ]
        }
        
        conflicts = api.detect_conflicts(new_domain, old_domain)
        assert len(conflicts) > 0
        assert any(c["conflict_type"] == "TYPE_CHANGE" for c in conflicts)
```

---

## PERFORMANCE TARGETS

### Query Performance

| Operation | Target | With Cache | Without Cache |
|-----------|--------|------------|---------------|
| **query_domain** | < 100ms | 1ms | 50ms |
| **list_domains** | < 500ms | 5ms | 200ms |
| **search_domains** | < 1000ms | 50ms | 500ms |

### Write Performance

| Operation | Target |
|-----------|--------|
| **upsert_domain** | < 500ms (includes validation + audit) |
| **detect_conflicts** | < 200ms |
| **resolve_conflict** | < 300ms |

### Caching

- **TTL**: 5 minutes (300 seconds)
- **Max size**: 1000 domains in cache
- **Invalidation**: On write, automatically evict from cache

### Audit Trail

- **Write latency**: < 100ms (append to log)
- **Read latency**: < 500ms (read entire log)
- **Retention**: 100% (never delete audit entries)

---

## NEXT STEPS

1. **Week 1**: Finalize all 5 pre-Phase 1 decisions ✓
2. **Week 2**: Design review with team ✓
3. **Week 2-4**: Implement Phase 1 components
4. **Week 4**: Performance testing & optimization
5. **Week 5**: Proceed to Phase 2 (adapters)

---

**Prepared by**: GitHub Copilot | **Date**: January 16, 2026
