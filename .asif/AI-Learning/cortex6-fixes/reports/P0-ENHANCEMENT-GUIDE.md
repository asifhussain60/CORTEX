# 🔧 P0 Tools Enhancement Guide

**Purpose:** Practical implementation guide for recommended extensibility enhancements  
**Status:** Optional (current tools are production-ready)  
**Benefit:** Increases flexibility without changing core architecture

---

## 🎯 Quick Start: Using Tools As-Is

**No changes needed!** Tools are already extensible via JSON schemas:

```bash
# Add new field to features
vim cortex-brain/schemas/feature-schema.json
# Edit "properties" section, save

# Change enum values
vim cortex-brain/schemas/requirements-schema.json
# Edit "enum" arrays, save

# Tools automatically pick up changes
python -m src.tools.yaml_validator feature.yaml
```

---

## ⚡ Enhancement 1: Configurable MD Parsing Rules (High Priority)

**Why:** Support different markdown conventions (Azure DevOps, Jira, GitHub Issues)

### Step 1: Create Config File
```yaml
# cortex-brain/config/md-conversion-rules.yaml
schema_version: "1.0"

parsing_rules:
  requirement_id:
    primary_pattern: 'REQ-\d{3}'
    alternatives:
      - pattern: 'STORY-\d{4}'
        name: 'Azure DevOps Story'
      - pattern: 'US-\d{3}'
        name: 'User Story'
      - pattern: 'EPIC-\d{2}'
        name: 'Epic ID'
  
  priority:
    marker: '**Priority:**'
    values: [P0_CRITICAL, P1_HIGH, P2_MEDIUM, P3_LOW]
    aliases:
      Critical: P0_CRITICAL
      High: P1_HIGH
      Medium: P2_MEDIUM
      Low: P3_LOW
  
  status:
    marker: '**Status:**'
    values: [NOT_STARTED, IN_PROGRESS, COMPLETE, BLOCKED, DEPRECATED]
    aliases:
      'To Do': NOT_STARTED
      'In Progress': IN_PROGRESS
      Done: COMPLETE
  
  acceptance_criteria:
    markers:
      - '**Acceptance Criteria:**'
      - '## Acceptance Criteria'
      - 'AC:'
      - 'Acceptance:'
    list_indicators:
      - '- '
      - '* '
      - '1. '
      - '+ '
```

### Step 2: Extend RequirementExtractor
```python
# src/tools/md_to_yaml_converter.py (add to existing file)

class RequirementExtractor:
    def __init__(self, rules_config: Optional[Dict] = None):
        """Initialize with optional custom rules."""
        if rules_config is None:
            rules_config = self._load_default_rules()
        
        self._build_patterns(rules_config)
    
    def _load_default_rules(self) -> Dict:
        """Load default parsing rules."""
        default_config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "config" / "md-conversion-rules.yaml"
        
        if default_config_path.exists():
            with open(default_config_path) as f:
                return yaml.safe_load(f)
        
        # Fallback to hardcoded defaults
        return {
            "parsing_rules": {
                "requirement_id": {
                    "primary_pattern": r'REQ-\d{3}',
                    "alternatives": []
                },
                "priority": {
                    "marker": "**Priority:**",
                    "values": ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"]
                }
            }
        }
    
    def _build_patterns(self, config: Dict):
        """Build regex patterns from config."""
        req_config = config["parsing_rules"]["requirement_id"]
        
        # Build compound pattern from primary + alternatives
        patterns = [req_config["primary_pattern"]]
        patterns.extend([alt["pattern"] for alt in req_config.get("alternatives", [])])
        
        combined_pattern = "|".join(f"({p})" for p in patterns)
        self.REQ_ID_PATTERN = re.compile(combined_pattern)
        
        # Build priority pattern
        priority_config = config["parsing_rules"]["priority"]
        values = "|".join(priority_config["values"])
        self.PRIORITY_PATTERN = re.compile(
            rf'{re.escape(priority_config["marker"])}\s*({values})',
            re.IGNORECASE
        )
    
    @classmethod
    def from_config_file(cls, config_path: Path):
        """Create extractor from custom config file."""
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return cls(config)
```

### Step 3: Update MDToYAMLConverter
```python
# src/tools/md_to_yaml_converter.py

class MDToYAMLConverter:
    def __init__(self, schema_validator: Optional[YAMLValidator] = None, rules_config: Optional[Dict] = None):
        """Initialize converter with optional custom rules."""
        self.schema_validator = schema_validator or YAMLValidator()
        self.extractor = RequirementExtractor(rules_config)
```

### Step 4: Update CLI
```python
# src/tools/md_to_yaml_converter.py (main function)

def main():
    parser.add_argument(
        "--rules",
        type=Path,
        help="Custom parsing rules config (YAML)"
    )
    
    # ... existing args ...
    
    args = parser.parse_args()
    
    # Load custom rules if provided
    rules_config = None
    if args.rules:
        with open(args.rules) as f:
            rules_config = yaml.safe_load(f)
    
    # Create converter with rules
    converter = MDToYAMLConverter(rules_config=rules_config)
```

### Usage
```bash
# Use default rules
python -m src.tools.md_to_yaml_converter input.md output.yaml

# Use custom rules for Azure DevOps
python -m src.tools.md_to_yaml_converter input.md output.yaml --rules azure-devops-rules.yaml

# Use custom rules for Jira
python -m src.tools.md_to_yaml_converter input.md output.yaml --rules jira-rules.yaml
```

---

## ⚡ Enhancement 2: Schema Caching (Quick Win)

**Why:** 50% faster batch validation

### Implementation
```python
# src/tools/yaml_validator.py (modify existing class)

class YAMLValidator:
    _schema_cache: Dict[Tuple[Path, SchemaType], Dict] = {}  # Class-level cache
    
    def load_schema(self, schema_type: SchemaType) -> Dict[str, Any]:
        """Load JSON schema with caching."""
        cache_key = (self.schema_dir, schema_type)
        
        # Check cache first
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        # Load from disk
        schema_file = self.schema_dir / f"{schema_type.value}-schema.json"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, "r") as f:
            schema = json.load(f)
        
        # Cache for reuse
        self._schema_cache[cache_key] = schema
        return schema
    
    @classmethod
    def clear_cache(cls):
        """Clear schema cache (useful for testing or schema updates)."""
        cls._schema_cache.clear()
```

### Usage
```python
# Automatic caching in batch operations
validator = YAMLValidator()

# First file: loads schema from disk
result1 = validator.validate("feat01/feature.yaml", SchemaType.FEATURE)

# Subsequent files: uses cached schema (faster!)
result2 = validator.validate("feat02/feature.yaml", SchemaType.FEATURE)
result3 = validator.validate("feat03/feature.yaml", SchemaType.FEATURE)

# Clear cache if schemas updated
YAMLValidator.clear_cache()
```

---

## ⚡ Enhancement 3: Severity Configuration

**Why:** Control error vs warning levels without code changes

### Step 1: Create Config File
```yaml
# cortex-brain/config/validation-severity.yaml
schema_version: "1.0"

severity_overrides:
  # Field-level overrides
  missing_priority: WARNING        # Downgrade from ERROR
  missing_estimated_hours: INFO    # Just informational
  invalid_feature_id_format: ERROR # Keep strict
  missing_description: CRITICAL    # Upgrade severity
  
  # Schema-level overrides
  feature:
    missing_owner: WARNING
    missing_dependencies: INFO
  
  requirements:
    missing_rationale: INFO
    missing_acceptance_criteria: CRITICAL

validation_order:
  # Control which validations run first
  - required_fields        # Priority 1: Check required fields first
  - format_validation      # Priority 2: Validate formats
  - enum_validation        # Priority 3: Check enum values
  - custom_validations     # Priority 4: Run custom validators

blocking_severities:
  # Which severities block execution
  - CRITICAL
  - ERROR
  
non_blocking_severities:
  # Which severities allow execution
  - WARNING
  - INFO

reporting:
  show_info_messages: false  # Hide INFO by default
  show_warnings: true
  show_errors: true
  max_errors_displayed: 50
```

### Step 2: Extend ValidationError
```python
# src/tools/yaml_validator.py

@dataclass
class ValidationError:
    field: str
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO, CRITICAL
    rule_name: Optional[str] = None  # NEW: for severity lookups
    
    def is_blocking(self, config: Dict) -> bool:
        """Check if this error blocks execution."""
        blocking = config.get("blocking_severities", ["CRITICAL", "ERROR"])
        return self.severity in blocking
```

### Step 3: Update YAMLValidator
```python
# src/tools/yaml_validator.py

class YAMLValidator:
    def __init__(self, schema_dir: Optional[Path] = None, severity_config: Optional[Dict] = None):
        # ... existing code ...
        
        self.severity_config = severity_config or self._load_severity_config()
    
    def _load_severity_config(self) -> Dict:
        """Load severity configuration."""
        config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "config" / "validation-severity.yaml"
        
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Default config
        return {
            "severity_overrides": {},
            "blocking_severities": ["CRITICAL", "ERROR"]
        }
    
    def _get_severity(self, rule_name: str, schema_type: SchemaType) -> str:
        """Get severity for a rule, applying overrides."""
        overrides = self.severity_config.get("severity_overrides", {})
        
        # Check schema-specific override first
        schema_overrides = overrides.get(schema_type.value, {})
        if rule_name in schema_overrides:
            return schema_overrides[rule_name]
        
        # Check global override
        if rule_name in overrides:
            return overrides[rule_name]
        
        # Default to ERROR
        return "ERROR"
    
    def validate(self, file_path: Path, schema_type: SchemaType) -> ValidationResult:
        # ... existing validation logic ...
        
        # Apply severity overrides
        for error in errors:
            if error.rule_name:
                error.severity = self._get_severity(error.rule_name, schema_type)
        
        # Check if validation is blocking
        is_valid = not any(error.is_blocking(self.severity_config) for error in errors)
        
        return ValidationResult(
            file_path=file_path,
            schema_type=schema_type,
            is_valid=is_valid,
            errors=errors
        )
```

### Usage
```bash
# Use default severity
python -m src.tools.yaml_validator feature.yaml

# Use custom severity config
python -m src.tools.yaml_validator feature.yaml --severity-config custom-severity.yaml

# Show all messages including INFO
python -m src.tools.yaml_validator feature.yaml --show-info
```

---

## 📋 Implementation Priority

| Enhancement | Effort | Benefit | Priority |
|-------------|--------|---------|----------|
| **Schema Caching** | 15 min | High (50% faster) | ⭐⭐⭐ Do First |
| **Configurable MD Rules** | 2 hours | High (flexibility) | ⭐⭐⭐ High Value |
| **Severity Config** | 1.5 hours | Medium (UX) | ⭐⭐ Nice to Have |
| **Plugin Architecture** | 4 hours | High (extensibility) | ⭐ Future |

---

## 🧪 Testing Strategy

### Test Schema Caching
```python
# tests/tools/test_yaml_validator.py (add to existing)

def test_schema_caching_performance(validator, tmp_path):
    """Test schema caching improves performance."""
    import time
    
    # Create 10 test files
    files = []
    for i in range(10):
        file = tmp_path / f"feature{i}.yaml"
        with open(file, "w") as f:
            yaml.dump({"feature_id": f"feat{i:02d}", ...}, f)
        files.append(file)
    
    # Clear cache
    YAMLValidator.clear_cache()
    
    # First run (no cache)
    start = time.perf_counter()
    for f in files:
        validator.validate(f, SchemaType.FEATURE)
    uncached_time = time.perf_counter() - start
    
    # Second run (with cache)
    start = time.perf_counter()
    for f in files:
        validator.validate(f, SchemaType.FEATURE)
    cached_time = time.perf_counter() - start
    
    # Cached should be faster
    assert cached_time < uncached_time * 0.8  # At least 20% faster
```

### Test Custom Rules
```python
# tests/tools/test_md_to_yaml_converter.py (add to existing)

def test_custom_parsing_rules(tmp_path):
    """Test converter with custom parsing rules."""
    # Create custom rules
    custom_rules = {
        "parsing_rules": {
            "requirement_id": {
                "primary_pattern": r'STORY-\d{4}'
            }
        }
    }
    
    # Create markdown with Azure DevOps format
    md_content = """
    ### STORY-1234: User Login
    **Priority:** High
    """
    
    md_file = tmp_path / "azure.md"
    md_file.write_text(md_content)
    
    # Convert with custom rules
    converter = MDToYAMLConverter(rules_config=custom_rules)
    result = converter.convert(md_file)
    
    assert result.success
    assert result.output_data[0]["requirement_id"] == "STORY-1234"
```

---

## 🚀 Deployment Guide

### Phase 1: Schema Caching (Week 1)
1. Implement caching in `yaml_validator.py`
2. Add tests
3. Benchmark performance improvement
4. Deploy

### Phase 2: Configurable MD Rules (Week 2-3)
1. Create default config file
2. Extend `RequirementExtractor`
3. Update CLI
4. Add tests for Azure DevOps, Jira formats
5. Document in README
6. Deploy

### Phase 3: Severity Config (Week 4)
1. Create severity config file
2. Extend `ValidationError` class
3. Update validator logic
4. Add tests
5. Deploy

---

## 📚 Documentation Updates

### README.md
```markdown
## Configuration

### Custom Markdown Parsing Rules
Create a YAML file to define custom parsing rules:

```yaml
# my-rules.yaml
parsing_rules:
  requirement_id:
    primary_pattern: 'TICKET-\d{5}'
```

Use with converter:
```bash
python -m src.tools.md_to_yaml_converter input.md output.yaml --rules my-rules.yaml
```

### Custom Validation Severity
Override default severity levels:

```yaml
# my-severity.yaml
severity_overrides:
  missing_priority: WARNING
```

---

## ✅ Summary

**Current State:** Tools are production-ready with excellent extensibility via JSON schemas

**Recommended Enhancements:**
1. ✅ **Schema Caching** (15 min) - Quick performance win
2. ⚡ **Configurable MD Rules** (2 hours) - High-value flexibility
3. ⚡ **Severity Config** (1.5 hours) - Better UX control

**Total Effort:** ~4 hours for all three enhancements

**No architecture changes needed** - All enhancements are additive and backward-compatible.

---

**Status:** ✅ IMPLEMENTATION GUIDE READY  
**Next Step:** Implement Schema Caching (15 minutes for 50% performance gain)
