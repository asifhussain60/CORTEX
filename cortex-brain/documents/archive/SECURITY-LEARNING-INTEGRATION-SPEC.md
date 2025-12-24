# CORTEX 4.0: Security & Best Practices Learning Agent

**Version:** 1.0  
**Status:** 🟢 APPROVED - Integrated into CORTEX 4.0 Master Plan  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Approved:** December 18, 2025  
**Integration:** Phase 2 (Weeks 4-8), Phase 3 (Weeks 9-13)

---

## 📋 Executive Summary

The Security Learning Agent enhances CORTEX 4.0 with proactive security enforcement and compliance automation by:

- **Learning** from authoritative sources (OWASP, CWE, NVD, PCI-DSS, HIPAA, GDPR)
- **Enforcing** security best practices during planning, development, and review
- **Adapting** to user's tech stack for context-aware validation
- **Self-updating** knowledge base with latest security standards

**Strategic Value:** First AI coding assistant with compliance-aware orchestration.

**Timeline Impact:** +0 weeks (40 hours parallel work within Phase 2-3)  
**Risk Level:** 🟢 LOW (leverages RAG infrastructure)  
**Dependencies:** Phase 2 RAG implementation, Tier 2 enhancement

---

## 🏗️ Architecture Integration

### Tier 2 Knowledge Graph Enhancement

**Existing (Phase 2 Planned):**
```
cortex-brain/tier2/
├── rag_stores/
│   └── domain_guidelines.db          # User-uploaded docs
└── retrieval/
    ├── semantic_search.py
    └── embedding_engine.py
```

**Enhanced (Security Integration):**
```
cortex-brain/tier2/
├── rag_stores/
│   ├── domain_guidelines.db          # User-uploaded docs (planned)
│   ├── security_patterns.db          # OWASP/CWE/CVE (NEW)
│   ├── tech_stack_patterns.db        # Framework best practices (NEW)
│   └── compliance_rules.db           # PCI/HIPAA/GDPR (NEW)
├── retrieval/
│   ├── semantic_search.py            # Shared by all stores
│   ├── embedding_engine.py           # Shared infrastructure
│   └── context_ranker.py             # Prioritize relevant patterns
└── learning/
    ├── security_learning_agent.py    # NEW - Main agent
    ├── tech_stack_profiler.py        # NEW - Detect frameworks
    └── pattern_ingestion_pipeline.py # NEW - Load external sources
```

### Agent Framework Extension

**New Agent:**
```python
src/cortex_agents/security_learning_agent.py

class SecurityLearningAgent:
    """
    Learns security best practices and enforces during orchestration.
    
    Responsibilities:
    - Ingest OWASP Top 10, CWE, NVD data
    - Profile user's tech stack
    - Provide security patterns to orchestrators
    - Update knowledge base on schedule
    """
    
    def __init__(self, brain_interface, config):
        self.tier2 = brain_interface.tier2
        self.config = config
        self.tech_stack = None
    
    def profile_tech_stack(self, workspace_path: Path) -> TechStack:
        """Detect frameworks from requirements.txt, package.json, etc."""
        ...
    
    def validate_security(self, code: str, context: str) -> List[SecurityViolation]:
        """Check code against security patterns."""
        ...
    
    def get_security_test_patterns(self, feature: str) -> List[TestPattern]:
        """Suggest security tests for feature."""
        ...
    
    def check_compliance(self, code: str, standard: str) -> ComplianceReport:
        """Validate against PCI/HIPAA/GDPR."""
        ...
```

### Tier 0 SKULL Enhancement

**New Security Rules:**
```yaml
# cortex-brain/brain-protection-rules.yaml

SECURITY_FIRST_ENFORCEMENT:
  description: "Validate code against OWASP Top 10 and compliance frameworks"
  enabled: true
  priority: HIGH
  
  triggers:
    - PlanningOrchestrator.validate_dor()
    - QAOrchestrator.security_audit()
    - SanitizationOrchestrator.pii_detection()
    - TDDOrchestrator.generate_tests()
  
  validations:
    SQL_INJECTION_PREVENTION:
      description: "Require parameterized queries"
      patterns:
        - raw_sql_concatenation
        - unsafe_orm_usage
      severity: CRITICAL
      
    XSS_PREVENTION:
      description: "Require output encoding"
      patterns:
        - unescaped_user_input
        - unsafe_html_rendering
      severity: HIGH
      
    AUTH_BYPASS_DETECTION:
      description: "Ensure authorization checks"
      patterns:
        - missing_auth_decorator
        - hardcoded_credentials
      severity: CRITICAL
      
    PII_EXPOSURE_CHECK:
      description: "Flag unencrypted sensitive data"
      patterns:
        - plaintext_ssn
        - unencrypted_credit_card
        - exposed_health_data
      severity: HIGH
  
  compliance_frameworks:
    PCI_DSS:
      enabled: false  # User-configurable
      requirements:
        - encrypted_card_data
        - secure_transmission
        - access_logging
    
    HIPAA:
      enabled: false
      requirements:
        - phi_encryption
        - audit_trails
        - access_controls
    
    GDPR:
      enabled: true  # Default for global apps
      requirements:
        - data_minimization
        - consent_tracking
        - right_to_deletion

TECH_STACK_AWARENESS:
  description: "Apply framework-specific security patterns"
  enabled: true
  
  frameworks:
    fastapi:
      patterns: [dependency_injection_auth, pydantic_validation]
    django:
      patterns: [csrf_middleware, orm_injection_prevention]
    react:
      patterns: [dangerouslySetInnerHTML_check, xss_prevention]
    flask:
      patterns: [wtforms_csrf, secure_cookie_config]
```

---

## 📅 Implementation Timeline

### Phase 2: Foundation (Weeks 4-8) - 28 Hours

#### Week 4: Schema & Profiler (12 hours)
- [ ] **Day 1-2:** Security patterns DB schema design (4 hours)
  - Table: `security_patterns` (pattern_id, owasp_id, cwe_id, description, code_example, severity)
  - Table: `tech_stack_patterns` (pattern_id, framework, version, best_practice, anti_pattern)
  - Table: `compliance_rules` (rule_id, standard, requirement, validation_logic)
  - Indexes for fast lookup

- [ ] **Day 3-4:** Tech Stack Profiler implementation (8 hours)
  - Parse `requirements.txt`, `package.json`, `pom.xml`, `*.csproj`
  - Detect frameworks (Django, Flask, FastAPI, React, Angular, Spring Boot, .NET Core)
  - Version detection and compatibility checks
  - Cache results in Tier 3 dev context

#### Week 6: OWASP Integration (8 hours)
- [ ] **Day 1:** OWASP Top 10 data ingestion (4 hours)
  - Download OWASP Top 10 2021 JSON/XML
  - Parse and load into `security_patterns` table
  - Map to code pattern examples
  - Create search index

- [ ] **Day 2:** Security pattern search API (4 hours)
  - Reuse RAG semantic search infrastructure
  - Query by vulnerability type, severity, framework
  - Context-aware ranking (prioritize user's tech stack)
  - Test with sample queries

#### Week 7: CWE Integration (6 hours)
- [ ] **Day 1:** CWE database ingestion (4 hours)
  - Download CWE Top 25 Most Dangerous Software Weaknesses
  - Map CWE IDs to OWASP categories
  - Load into `security_patterns` with cross-references
  - Update search index

- [ ] **Day 2:** Compliance rules setup (2 hours)
  - Load PCI-DSS requirements (subset relevant to code)
  - Load HIPAA technical safeguards
  - Load GDPR data protection principles
  - User-configurable enable/disable

#### Week 8: Agent Implementation (2 hours)
- [ ] **Day 1:** SecurityLearningAgent core (2 hours)
  - Implement agent class with DI integration
  - Connect to Tier 2 security stores
  - Expose validation API for orchestrators
  - Unit tests (30 test cases)

**Phase 2 Total:** 28 hours (~3.5 days spread over 4 weeks)

---

### Phase 3: Orchestrator Integration (Weeks 9-13) - 12 Hours

#### Week 8: Planning Orchestrator (2 hours)
- [ ] **PlanningOrchestrator DoR Enhancement:**
  ```python
  def _check_security_requirements(self, plan):
      """Validate security considerations in plan."""
      if not SecurityLearningAgent.is_available():
          return True  # Graceful degradation
      
      violations = []
      
      # Check if auth/authz addressed
      if self._requires_authentication(plan):
          if not plan.includes_auth_strategy():
              violations.append("Missing authentication strategy")
      
      # Check for sensitive data handling
      if self._handles_sensitive_data(plan):
          if not plan.includes_encryption():
              violations.append("Sensitive data without encryption plan")
      
      # Framework-specific checks
      tech_stack = SecurityAgent.profile_tech_stack()
      violations.extend(SecurityAgent.validate_plan(plan, tech_stack))
      
      return len(violations) == 0, violations
  ```

#### Week 8: Scaffolding Orchestrator (3 hours)
- [ ] **Secure-by-Default Templates:**
  - Auth middleware templates (JWT, OAuth2, session-based)
  - Input validation boilerplate
  - Secure configuration defaults (HTTPS, CSRF protection)
  - Framework-specific security patterns

#### Week 10: QA Orchestrator (4 hours)
- [ ] **Security Audit Phase:**
  ```python
  def run_security_audit(self):
      """Run security checks on codebase."""
      agent = SecurityLearningAgent()
      
      results = {
          'vulnerabilities': [],
          'compliance_issues': [],
          'recommendations': []
      }
      
      # Scan for OWASP Top 10
      for file in self.get_code_files():
          violations = agent.validate_security(file.read(), file.path)
          results['vulnerabilities'].extend(violations)
      
      # Check compliance (if enabled)
      if self.config.compliance.pci_dss:
          results['compliance_issues'].extend(
              agent.check_compliance(self.codebase, 'PCI-DSS')
          )
      
      return self.format_security_report(results)
  ```

#### Week 10: TDD Orchestrator Enhancement (2 hours)
- [ ] **Security Test Pattern Suggestions:**
  ```python
  def generate_test_cases(self, feature):
      tests = super().generate_test_cases(feature)
      
      # Add security tests
      if SecurityLearningAgent.is_available():
          security_tests = SecurityAgent.get_security_test_patterns(feature)
          tests.extend(security_tests)
          # Examples: SQL injection tests, XSS tests, auth bypass attempts
      
      return tests
  ```

#### Week 10: Maintenance Orchestrator (1 hour)
- [ ] **Security Pattern Updates:**
  - Add phase to update security patterns (weekly/monthly)
  - Check for new OWASP updates
  - Refresh CWE database
  - Log update metrics

**Phase 3 Total:** 12 hours (~1.5 days during orchestrator migration)

---

### Phase 6 (Optional): Auto-Update Pipeline (Weeks 20) - 14 Hours

**Deferred to Phase 6 (Polish) - Not blocking 4.0 launch:**

- [ ] Scheduled OWASP updates (weekly) - 4 hours
- [ ] NVD CVE polling (daily) - 6 hours  
- [ ] Security coverage dashboard - 4 hours

---

## 🔧 Technical Implementation Details

### Security Patterns Database Schema

```sql
-- Security patterns from OWASP/CWE
CREATE TABLE security_patterns (
    pattern_id TEXT PRIMARY KEY,
    owasp_id TEXT,              -- e.g., "A03:2021-Injection"
    cwe_id INTEGER,              -- e.g., 89 (SQL Injection)
    category TEXT,               -- injection, xss, auth, crypto, etc.
    severity TEXT,               -- CRITICAL, HIGH, MEDIUM, LOW
    title TEXT,
    description TEXT,
    vulnerable_code_example TEXT,
    secure_code_example TEXT,
    frameworks TEXT,             -- JSON array: ["django", "flask"]
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tech stack specific patterns
CREATE TABLE tech_stack_patterns (
    pattern_id TEXT PRIMARY KEY,
    framework TEXT,              -- django, react, fastapi, etc.
    version_min TEXT,
    version_max TEXT,
    pattern_type TEXT,           -- best_practice, anti_pattern, security
    title TEXT,
    description TEXT,
    code_example TEXT,
    severity TEXT,
    references TEXT,             -- JSON array of URLs
    created_at TIMESTAMP
);

-- Compliance requirements
CREATE TABLE compliance_rules (
    rule_id TEXT PRIMARY KEY,
    standard TEXT,               -- PCI-DSS, HIPAA, GDPR, SOC2
    requirement_id TEXT,         -- e.g., "PCI-3.4"
    category TEXT,
    description TEXT,
    validation_logic TEXT,       -- Python code snippet or regex
    severity TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Indexes for fast lookup
CREATE INDEX idx_security_owasp ON security_patterns(owasp_id);
CREATE INDEX idx_security_cwe ON security_patterns(cwe_id);
CREATE INDEX idx_security_category ON security_patterns(category);
CREATE INDEX idx_techstack_framework ON tech_stack_patterns(framework);
CREATE INDEX idx_compliance_standard ON compliance_rules(standard);
```

### Tech Stack Profiler Implementation

```python
# src/operations/utilities/tech_stack_profiler.py

from pathlib import Path
from typing import Dict, List
import json
import toml
import xml.etree.ElementTree as ET

class TechStackProfiler:
    """Detect user's tech stack from project files."""
    
    KNOWN_FRAMEWORKS = {
        'python': ['django', 'flask', 'fastapi', 'tornado', 'pyramid'],
        'javascript': ['react', 'vue', 'angular', 'svelte', 'next'],
        'java': ['spring', 'spring-boot', 'quarkus', 'micronaut'],
        'csharp': ['asp.net', 'asp.net-core', 'blazor'],
        'go': ['gin', 'echo', 'fiber'],
        'rust': ['actix', 'rocket', 'axum']
    }
    
    @staticmethod
    def detect_from_workspace(workspace_path: Path) -> Dict[str, List[str]]:
        """
        Scan workspace for tech indicators.
        
        Returns:
            {
                'backend': ['django==4.2', 'fastapi==0.104.0'],
                'frontend': ['react@18.2.0'],
                'database': ['postgresql'],
                'cloud': ['terraform', 'aws']
            }
        """
        stack = {
            'backend': [],
            'frontend': [],
            'database': [],
            'cloud': [],
            'security': []
        }
        
        # Python dependencies
        req_file = workspace_path / 'requirements.txt'
        if req_file.exists():
            stack['backend'].extend(TechStackProfiler._parse_python_deps(req_file))
        
        # JavaScript dependencies
        pkg_file = workspace_path / 'package.json'
        if pkg_file.exists():
            stack['frontend'].extend(TechStackProfiler._parse_js_deps(pkg_file))
        
        # Java dependencies
        pom_file = workspace_path / 'pom.xml'
        if pom_file.exists():
            stack['backend'].extend(TechStackProfiler._parse_maven_deps(pom_file))
        
        # .NET dependencies
        for csproj in workspace_path.rglob('*.csproj'):
            stack['backend'].extend(TechStackProfiler._parse_dotnet_deps(csproj))
        
        # Infrastructure
        if (workspace_path / 'terraform').exists():
            stack['cloud'].append('terraform')
        if (workspace_path / 'Dockerfile').exists():
            stack['cloud'].append('docker')
        
        return stack
    
    @staticmethod
    def _parse_python_deps(req_file: Path) -> List[str]:
        """Parse requirements.txt for framework detection."""
        deps = []
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name and version
                if '==' in line:
                    pkg, ver = line.split('==')
                    deps.append(f"{pkg}=={ver}")
                elif '>=' in line or '<=' in line:
                    deps.append(line)
        return deps
    
    @staticmethod
    def _parse_js_deps(pkg_file: Path) -> List[str]:
        """Parse package.json for framework detection."""
        data = json.loads(pkg_file.read_text())
        deps = []
        
        for section in ['dependencies', 'devDependencies']:
            if section in data:
                for pkg, ver in data[section].items():
                    deps.append(f"{pkg}@{ver}")
        
        return deps
    
    @staticmethod
    def _parse_maven_deps(pom_file: Path) -> List[str]:
        """Parse pom.xml for Java framework detection."""
        tree = ET.parse(pom_file)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        
        deps = []
        for dep in root.findall('.//m:dependency', ns):
            group_id = dep.find('m:groupId', ns)
            artifact_id = dep.find('m:artifactId', ns)
            version = dep.find('m:version', ns)
            
            if all([group_id, artifact_id]):
                ver_str = f":{version.text}" if version is not None else ""
                deps.append(f"{group_id.text}:{artifact_id.text}{ver_str}")
        
        return deps
    
    @staticmethod
    def _parse_dotnet_deps(csproj_file: Path) -> List[str]:
        """Parse .csproj for .NET framework detection."""
        tree = ET.parse(csproj_file)
        root = tree.getroot()
        
        deps = []
        for ref in root.findall('.//PackageReference'):
            pkg = ref.get('Include')
            ver = ref.get('Version')
            if pkg:
                deps.append(f"{pkg}@{ver}" if ver else pkg)
        
        return deps
```

### Security Learning Agent Core

```python
# src/cortex_agents/security_learning_agent.py

from typing import List, Dict, Optional
from pathlib import Path
import sqlite3
from dataclasses import dataclass

@dataclass
class SecurityViolation:
    pattern_id: str
    severity: str
    file_path: str
    line_number: int
    description: str
    vulnerable_code: str
    fix_suggestion: str
    owasp_id: Optional[str] = None
    cwe_id: Optional[int] = None

class SecurityLearningAgent:
    """
    Security and compliance enforcement agent.
    
    Integrates with Tier 2 knowledge graph to provide:
    - Security pattern validation
    - Compliance checking (PCI, HIPAA, GDPR)
    - Tech stack-aware recommendations
    - Security test pattern generation
    """
    
    def __init__(self, brain_interface, config):
        self.tier2 = brain_interface.tier2
        self.config = config
        self.db_path = Path(config.cortex_brain_path) / 'tier2' / 'rag_stores' / 'security_patterns.db'
        self.tech_stack = None
    
    @staticmethod
    def is_available() -> bool:
        """Check if security patterns DB exists."""
        return (Path('cortex-brain/tier2/rag_stores/security_patterns.db').exists())
    
    def profile_tech_stack(self, workspace_path: Path) -> Dict[str, List[str]]:
        """Detect frameworks from workspace files."""
        from src.operations.utilities.tech_stack_profiler import TechStackProfiler
        self.tech_stack = TechStackProfiler.detect_from_workspace(workspace_path)
        return self.tech_stack
    
    def validate_security(self, code: str, file_path: str) -> List[SecurityViolation]:
        """
        Check code against security patterns.
        
        Returns list of violations found.
        """
        violations = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get relevant patterns for user's tech stack
            frameworks = self._extract_frameworks(self.tech_stack)
            
            cursor.execute("""
                SELECT pattern_id, owasp_id, cwe_id, severity, 
                       description, secure_code_example
                FROM security_patterns
                WHERE category IN ('injection', 'xss', 'auth', 'crypto', 'sensitive-data')
                  AND (frameworks IS NULL OR frameworks LIKE ? OR frameworks LIKE ?)
            """, (f'%{frameworks[0]}%', f'%{frameworks[1]}%'))
            
            for row in cursor.fetchall():
                pattern_id, owasp_id, cwe_id, severity, desc, fix = row
                
                # Check if vulnerable pattern exists in code
                if self._matches_vulnerable_pattern(code, pattern_id):
                    violations.append(SecurityViolation(
                        pattern_id=pattern_id,
                        severity=severity,
                        file_path=file_path,
                        line_number=self._find_line_number(code, pattern_id),
                        description=desc,
                        vulnerable_code=self._extract_vulnerable_code(code, pattern_id),
                        fix_suggestion=fix,
                        owasp_id=owasp_id,
                        cwe_id=cwe_id
                    ))
        
        return violations
    
    def get_security_test_patterns(self, feature: str) -> List[str]:
        """
        Suggest security test cases for a feature.
        
        Returns list of test code snippets.
        """
        tests = []
        
        # Determine what kind of security tests are relevant
        if 'auth' in feature.lower():
            tests.extend(self._auth_test_patterns())
        
        if any(word in feature.lower() for word in ['database', 'query', 'sql']):
            tests.extend(self._injection_test_patterns())
        
        if any(word in feature.lower() for word in ['form', 'input', 'user']):
            tests.extend(self._xss_test_patterns())
        
        return tests
    
    def check_compliance(self, code: str, standard: str) -> Dict[str, List[str]]:
        """
        Validate code against compliance standards.
        
        Args:
            code: Source code to check
            standard: 'PCI-DSS', 'HIPAA', 'GDPR', 'SOC2'
        
        Returns:
            {
                'violations': ['PCI-3.4: Unencrypted card data'],
                'warnings': ['PCI-8.2: Weak password policy'],
                'compliant': ['PCI-6.5: Input validation present']
            }
        """
        if not self.config.compliance.get(standard.lower().replace('-', '_'), False):
            return {'violations': [], 'warnings': [], 'compliant': []}
        
        results = {'violations': [], 'warnings': [], 'compliant': []}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rule_id, requirement_id, description, 
                       validation_logic, severity
                FROM compliance_rules
                WHERE standard = ? AND enabled = TRUE
            """, (standard,))
            
            for row in cursor.fetchall():
                rule_id, req_id, desc, logic, severity = row
                
                # Execute validation logic
                if self._evaluate_compliance_rule(code, logic):
                    results['compliant'].append(f"{req_id}: {desc}")
                else:
                    if severity == 'CRITICAL':
                        results['violations'].append(f"{req_id}: {desc}")
                    else:
                        results['warnings'].append(f"{req_id}: {desc}")
        
        return results
    
    # Helper methods
    def _extract_frameworks(self, tech_stack: Dict) -> List[str]:
        """Extract framework names from tech stack."""
        frameworks = []
        for category in tech_stack.values():
            for dep in category:
                # Extract base framework name (before version)
                name = dep.split('==')[0].split('@')[0].split(':')[0]
                frameworks.append(name.lower())
        return frameworks[:2]  # Top 2 frameworks
    
    def _matches_vulnerable_pattern(self, code: str, pattern_id: str) -> bool:
        """Check if code matches known vulnerable pattern."""
        # Simplified - real implementation would use AST analysis
        vulnerability_indicators = {
            'sql_injection': ['raw_sql =', '.execute(f"', '+ sql', 'query % '],
            'xss': ['dangerouslySetInnerHTML', 'v-html=', 'innerHTML ='],
            'auth_bypass': ['if not user', 'user == None', '@login_not_required']
        }
        
        for pattern_type, indicators in vulnerability_indicators.items():
            if pattern_type in pattern_id:
                return any(indicator in code for indicator in indicators)
        
        return False
    
    def _find_line_number(self, code: str, pattern_id: str) -> int:
        """Find line number of vulnerability."""
        # Simplified - real implementation would track during pattern matching
        return 1
    
    def _extract_vulnerable_code(self, code: str, pattern_id: str) -> str:
        """Extract vulnerable code snippet."""
        # Simplified - real implementation would extract context around match
        return code[:100]
    
    def _auth_test_patterns(self) -> List[str]:
        """Generate auth security test patterns."""
        return [
            "def test_unauthorized_access_denied():",
            "def test_auth_bypass_attempt_fails():",
            "def test_weak_password_rejected():"
        ]
    
    def _injection_test_patterns(self) -> List[str]:
        """Generate SQL injection test patterns."""
        return [
            "def test_sql_injection_prevented():",
            "def test_parameterized_query_used():",
            "def test_orm_injection_blocked():"
        ]
    
    def _xss_test_patterns(self) -> List[str]:
        """Generate XSS test patterns."""
        return [
            "def test_output_encoding_applied():",
            "def test_script_tag_escaped():",
            "def test_xss_payload_neutralized():"
        ]
    
    def _evaluate_compliance_rule(self, code: str, logic: str) -> bool:
        """Evaluate compliance rule validation logic."""
        # Simplified - real implementation would safely execute validation
        return True
```

---

## 🧪 Testing Strategy

### Unit Tests (30 test cases)

```python
# tests/agents/test_security_learning_agent.py

def test_tech_stack_profiler_detects_python():
    """Test Python framework detection."""
    profiler = TechStackProfiler()
    stack = profiler.detect_from_workspace(Path('test_fixtures/python_project'))
    assert 'django' in str(stack['backend'])

def test_security_agent_detects_sql_injection():
    """Test SQL injection pattern detection."""
    agent = SecurityLearningAgent(mock_brain, mock_config)
    code = 'query = "SELECT * FROM users WHERE id=" + user_id'
    violations = agent.validate_security(code, 'test.py')
    assert len(violations) > 0
    assert violations[0].owasp_id == 'A03:2021-Injection'

def test_security_agent_suggests_auth_tests():
    """Test security test pattern generation."""
    agent = SecurityLearningAgent(mock_brain, mock_config)
    tests = agent.get_security_test_patterns('user authentication')
    assert len(tests) >= 3
    assert any('unauthorized' in t.lower() for t in tests)

def test_compliance_checker_pci_dss():
    """Test PCI-DSS compliance validation."""
    agent = SecurityLearningAgent(mock_brain, mock_config)
    code = 'card_number = "4111111111111111"'  # Plaintext card
    results = agent.check_compliance(code, 'PCI-DSS')
    assert len(results['violations']) > 0

def test_graceful_degradation_when_db_missing():
    """Test agent handles missing security DB gracefully."""
    assert SecurityLearningAgent.is_available() == False
    # Orchestrators should continue without security checks
```

### Integration Tests (15 test cases)

```python
# tests/integration/test_security_orchestrator_integration.py

def test_planning_orchestrator_security_validation():
    """Test PlanningOrchestrator uses security checks."""
    orchestrator = PlanningOrchestrator(config)
    plan = create_test_plan(includes_auth=False)
    is_valid, errors = orchestrator.validate_dor(plan)
    assert not is_valid
    assert 'security' in str(errors).lower()

def test_qa_orchestrator_security_audit():
    """Test QAOrchestrator runs security audit."""
    orchestrator = QAOrchestrator(config)
    results = orchestrator.run_security_audit()
    assert 'vulnerabilities' in results
    assert 'compliance_issues' in results

def test_tdd_orchestrator_security_tests():
    """Test TDDOrchestrator suggests security tests."""
    orchestrator = TDDOrchestrator(config)
    tests = orchestrator.generate_test_cases('login endpoint')
    security_tests = [t for t in tests if 'security' in t.lower()]
    assert len(security_tests) > 0
```

---

## 📊 Success Metrics

### Phase 2 Deliverables (Week 8 End)
- [ ] Security patterns DB operational with 200+ patterns
- [ ] OWASP Top 10 2021 fully loaded
- [ ] CWE Top 25 integrated
- [ ] Tech stack profiler detects 10+ frameworks
- [ ] Security search API <100ms response time
- [ ] 30/30 unit tests passing

### Phase 3 Deliverables (Week 13 End)
- [ ] PlanningOrchestrator rejects plans without security consideration (for auth/data features)
- [ ] QAOrchestrator security audit phase operational
- [ ] TDDOrchestrator suggests 3+ security tests per feature
- [ ] SKULL security rules enforced
- [ ] 15/15 integration tests passing
- [ ] Zero false positives in test codebase

### Phase 5 Validation (Week 19)
- [ ] 90%+ test coverage for security agent
- [ ] <5% false positive rate
- [ ] Security checks add <200ms overhead to orchestrators
- [ ] Documentation complete (4 guides)

---

## 📚 Documentation Artifacts

1. **User Guide:** `cortex-brain/documents/implementation-guides/security-learning-agent-guide.md`
2. **API Reference:** `docs/security-learning-api.md`
3. **Compliance Setup:** `cortex-brain/documents/implementation-guides/compliance-configuration.md`
4. **Pattern Authoring:** `cortex-brain/documents/implementation-guides/custom-security-patterns.md`

---

## 🚨 Risk Mitigation

| Risk | Mitigation Strategy | Status |
|------|---------------------|--------|
| Phase 2 RAG delays | Security DB separate, can work independently | 🟢 LOW |
| False positives | Confidence scoring + user feedback loop | 🟡 MEDIUM |
| Performance impact | Async validation, lazy loading | 🟢 LOW |
| External API failures | Cache-first strategy, fallback to local DB | 🟢 LOW |
| Scope creep | Defer auto-update to Phase 6 | 🟢 LOW |

---

## 🔄 Configuration

```json
// cortex.config.json (NEW section)
{
  "security_learning": {
    "enabled": true,
    "auto_update": false,  // Phase 6 feature
    "frameworks": ["owasp", "cwe"],
    "validation_threshold": 0.7,  // Confidence score
    "max_check_time_ms": 500
  },
  
  "compliance": {
    "pci_dss": false,  // User must explicitly enable
    "hipaa": false,
    "gdpr": true,      // Default for global apps
    "soc2": false
  },
  
  "security_enforcement": {
    "planning_dor": true,   // Require security in plans
    "qa_audit": true,       // Run security audits
    "tdd_tests": true,      // Suggest security tests
    "severity_threshold": "HIGH"  // Only CRITICAL/HIGH block
  }
}
```

---

## 📅 Rollout Plan

### Week 8: Internal Alpha
- Security DB populated
- Agent operational but not enforced
- Internal testing with CORTEX codebase

### Week 10: Orchestrator Integration
- Conditional security checks enabled
- Monitor for false positives
- Tune pattern matching thresholds

### Week 13: Beta (Soft Launch)
- Security features enabled by default
- User opt-out available
- Collect feedback

### Week 19: Production Ready
- All tests passing
- Documentation complete
- Metrics dashboards operational

---

## 🎯 Next Steps

**Immediate (Week 4 - Starting Now):**
1. [ ] Create security patterns DB schema
2. [ ] Set up Tier 2 directory structure
3. [ ] Implement TechStackProfiler skeleton
4. [ ] Write first 10 unit tests

**Next Week (Week 5):**
5. [ ] Complete TechStackProfiler implementation
6. [ ] Test with 3 sample projects (Python, JS, Java)

**Week 6-8:**
7. [ ] OWASP data ingestion
8. [ ] CWE integration
9. [ ] Security agent core implementation

**Phase 3 (Weeks 9-13):**
10. [ ] Orchestrator integration (conditional checks)
11. [ ] SKULL rules enhancement
12. [ ] Integration testing

---

**Status:** 🟢 Ready to begin Phase 2 security work alongside RAG implementation.
