# CORTEX Agent Inventory

**Created:** January 2, 2026  
**Phase:** 0 - Foundation Setup (Task 0.3)  
**Purpose:** Complete catalog of agents with configuration dependencies

---

## Agent Classification

**Total:** 20+ specialized agents  
**Tier 1 (Core):** 4 agents (intent routing, classification)  
**Tier 2-3 (Specialized):** 16+ agents (domain-specific operations)

---

## Tier 1: Core Agents

### 1. Intent Router

**File:** `src/cortex_agents/intent_router.py`  
**Purpose:** Route user commands to appropriate orchestrators/agents  
**Configuration:** Hardcoded pattern matching in Python

**Current Behavior:**
- Parses user request
- Matches against regex patterns
- Returns orchestrator name + confidence score
- Fallback to generic response

**Configuration Source:**
```python
# Hardcoded in intent_router.py
PATTERNS = {
    "planning": r"(create|make) (a )?plan",
    "ado": r"ado (story|feature|bug)",
    "maintenance": r"(system )?maintenance",
    # ... 20+ patterns
}
```

**Issues:**
1. Pattern matching brittle (exact phrases required)
2. No ML-based classification as primary method
3. Configuration not externalizable
4. Can't add patterns without code change

**Dependency Analysis:**
- Reads: `CORTEX.prompt.md` (hardcoded path)
- Uses: String regex matching
- Returns: Orchestrator name string

**Migration Strategy:**
- Phase 7: Use `LLMIntentClassifier` as primary
- Externalize patterns to YAML config
- Add telemetry for pattern effectiveness

---

### 2. LLM Intent Classifier

**File:** `src/cortex_agents/llm_intent_classifier.py`  
**Purpose:** AI-powered intent classification with confidence scores  
**Configuration:** Inline prompts

**Current Behavior:**
- Sends user request + orchestrator capabilities to LLM
- Gets classification with confidence (0.0-1.0)
- Falls back to pattern matching if confidence low
- Currently secondary to regex patterns

**Strengths:**
- Handles synonyms, typos, natural phrasing
- Confidence scoring enables smart fallback
- Learns from orchestrator capabilities

**Issues:**
1. Not primary classification method (should be!)
2. Prompts hardcoded in Python
3. No caching of classifications
4. API latency (~200-500ms)

**Dependency Analysis:**
- Reads: Orchestrator capability descriptions
- Calls: OpenAI GPT-4 API
- Returns: `(orchestrator_name, confidence_score)`

**Migration Strategy:**
- Phase 7: Make LLM classifier primary method
- Add classification result caching
- Externalize prompts to templates
- Implement prompt versioning

---

### 3. Investigation Router

**File:** `src/cortex_agents/investigation_router.py`  
**Purpose:** Route deep investigation requests to specialized agents  
**Configuration:** Pattern matching with investigation types

**Current Behavior:**
- Analyzes investigation type (security, performance, bug, architecture)
- Routes to appropriate specialized agent
- Coordinates multi-agent investigations

**Investigation Types:**
```python
INVESTIGATION_TYPES = {
    "security": SecurityScannerAgent,
    "performance": PerformanceAnalyzerAgent,
    "rca": RCAAgent,
    "architecture": ArchitectureAnalyzerAgent
}
```

**Issues:**
1. Agent registry hardcoded
2. No investigation state persistence
3. Can't parallelize multi-agent investigations
4. No investigation history tracking

**Dependency Analysis:**
- Uses: Pattern matching + keyword extraction
- Coordinates: Multiple specialized agents
- Stores: None (stateless)

**Migration Strategy:**
- Phase 7: Externalize agent registry to config
- Add investigation tracking to database
- Support parallel agent execution
- Add investigation report templates

---

### 4. Welcome Banner Agent

**File:** `src/cortex_agents/welcome_banner_agent.py`  
**Purpose:** Display ASCII banner and capabilities on introduction  
**Configuration:** Hardcoded ASCII art

**Current Behavior:**
- Triggered by "intro", "hello", "what is cortex"
- Displays ASCII banner
- Lists capabilities from response templates
- Shows quick command reference

**Strengths:**
- Great user experience
- Clear capability overview
- Fast response (no API calls)

**Issues:**
1. ASCII art hardcoded (not configurable)
2. Capability list manually updated
3. No version information display

**Dependency Analysis:**
- Reads: `response-templates-v4.yaml:introduction`
- Returns: Formatted markdown string

**Migration Strategy:**
- Low priority (works well)
- Phase 7: Auto-generate capability list from orchestrator registry
- Add version/build information

---

## Tier 2-3: Specialized Agents

### 5. ADO Agent

**File:** `src/cortex_agents/ado_agent.py`  
**Purpose:** Azure DevOps work item management  
**Configuration:** ADO API credentials (environment variables)

**Current Behavior:**
- Creates user stories, features, bugs
- Generates acceptance criteria
- Estimates story points
- Links related work items

**Issues:**
1. Should be orchestrator, not agent
2. Credentials in environment (not secure storage)
3. No rate limiting
4. No offline mode/caching

**Dependency Analysis:**
- Requires: ADO PAT token
- Calls: Azure DevOps REST API
- Stores: None (ADO is source of truth)

**Migration Strategy:**
- Phase 6: Extract to ADO Orchestrator v2
- Move credentials to secure config
- Add request caching
- Implement rate limiting

---

### 6. Learning Capture Agent

**File:** `src/cortex_agents/learning_capture_agent.py`  
**Purpose:** Capture conversations to JSONL for learning  
**Configuration:** File paths hardcoded

**Current Behavior:**
- Appends conversation turns to JSONL
- Captures user request + CORTEX response
- Includes timestamps and metadata
- Used by onboarding and analysis

**Strengths:**
- Append-only (safe, no overwrites)
- Structured JSON format
- Includes rich metadata

**Issues:**
1. JSONL path hardcoded
2. No rotation/archival strategy
3. No PII scrubbing
4. Unbounded growth

**Dependency Analysis:**
- Writes: `cortex-brain/conversation-context.jsonl`
- Format: JSON Lines (one object per line)
- Used by: Onboarding, session resumer

**Migration Strategy:**
- Phase 7: Externalize paths to config
- Add log rotation (by size/date)
- Implement PII scrubbing
- Add compression for archives

---

### 7. Session Resumer

**File:** `src/cortex_agents/session_resumer.py`  
**Purpose:** Restore previous conversation sessions  
**Configuration:** Session log paths

**Current Behavior:**
- Reads JSONL session logs
- Reconstructs conversation context
- Allows user to pick session to resume
- Injects context into current conversation

**Strengths:**
- Valuable feature (resume work)
- Works reliably
- User-friendly session selection

**Issues:**
1. JSONL path hardcoded
2. Loads entire session into memory
3. No session search/filter
4. No session metadata (title, date, etc.)

**Dependency Analysis:**
- Reads: `cortex-brain/conversation-context.jsonl`
- Parses: JSON Lines format
- Returns: Reconstructed context string

**Migration Strategy:**
- Phase 7: Store sessions in SQLite
- Add session metadata (title, tags, date)
- Implement session search
- Stream large sessions instead of full load

---

### 8. Profile Agent

**File:** `src/cortex_agents/profile_agent.py`  
**Purpose:** User profiling and preference management  
**Configuration:** `cortex-brain/user-dictionary.yaml`

**Current Behavior:**
- Stores user preferences (coding style, frameworks)
- Learns from user corrections
- Applies preferences to responses
- Manages user-specific vocabulary

**Strengths:**
- Personalization improves UX
- Learns over time
- YAML format (human-editable)

**Issues:**
1. No schema validation for user dict
2. No preference versioning
3. Single user only (no multi-user support)
4. No preference inheritance/profiles

**Dependency Analysis:**
- Reads/Writes: `cortex-brain/user-dictionary.yaml`
- Format: YAML (flat key-value)
- Used by: Response generation, code formatting

**Migration Strategy:**
- Phase 7: Add schema validation
- Support multiple user profiles
- Version preferences (track changes)
- Add preference categories

---

### 9. Screenshot Analyzer

**File:** `src/cortex_agents/screenshot_analyzer.py`  
**Purpose:** Analyze attached images using Vision API  
**Configuration:** OpenAI API key

**Current Behavior:**
- Auto-detects image attachments
- Sends to GPT-4V for analysis
- Extracts UI elements, errors, diagrams
- Injects analysis into conversation context

**Strengths:**
- Automatic (no user prompting needed)
- Fast (<500ms)
- Integrates with all orchestrators

**Issues:**
1. No image caching (re-analyzes same images)
2. API key in environment
3. No cost tracking
4. No local vision model option

**Dependency Analysis:**
- Requires: OpenAI API key
- Calls: GPT-4V API
- Returns: Analysis string
- Middleware: `vision_context_middleware.py`

**Migration Strategy:**
- Phase 7: Add image hash caching
- Track API costs per analysis
- Support local vision models
- Add analysis quality metrics

---

### 10. Security Scanner Agent

**File:** `src/cortex_agents/security_scanner_agent.py`  
**Purpose:** Scan code for security vulnerabilities  
**Configuration:** Validation rules YAML

**Current Behavior:**
- Scans code for common vulnerabilities
- Checks dependencies for CVEs
- Validates configuration security
- Generates security reports

**Strengths:**
- Comprehensive rule set
- Clear severity scoring
- Actionable recommendations

**Issues:**
1. Rules manually maintained
2. No CVE database updates
3. Slow for large codebases
4. Many false positives

**Dependency Analysis:**
- Reads: `cortex-brain/validation-rules.yaml`
- Calls: External CVE databases (optional)
- Returns: Security report JSON

**Migration Strategy:**
- Phase 7: Integrate with OWASP rulesets
- Auto-update CVE database
- Add whitelist for false positives
- Parallelize scanning

---

### 11-20. Additional Agents

Brief catalog of remaining agents:

| Agent | Purpose | Config Source | Priority |
|-------|---------|---------------|----------|
| **RCA Agent** | Root cause analysis | Investigation patterns | 🟡 P1 |
| **Supply Chain Security** | Dependency scanning | Package manifests | 🟡 P1 |
| **Incident Response** | Auto-remediation | Runbooks YAML | 🟡 P1 |
| **Performance Analyzer** | Performance profiling | Benchmark configs | 🟢 P2 |
| **Architecture Analyzer** | Code structure analysis | Architecture rules | 🟢 P2 |
| **Metrics Collector** | Telemetry collection | Metric definitions | 🟢 P2 |
| **Dashboard Generator** | Visualization creation | Chart configs | 🟢 P3 |
| **Backup Manager** | State backup/restore | Backup policies | 🟢 P3 |
| **Test Generator** | Automatic test creation | Test templates | 🟢 P3 |
| **Refactoring Assistant** | Code improvement suggestions | Refactoring patterns | 🟢 P3 |

---

## Configuration Source Summary

| Config Type | Count | Examples |
|-------------|-------|----------|
| **Hardcoded** | 8 | Intent patterns, paths, API endpoints |
| **Environment Variables** | 5 | API keys, credentials |
| **YAML Files** | 7 | User dict, rules, capabilities |
| **JSON Files** | 3 | Session logs, tracking |
| **JSONL Files** | 2 | Conversations, learning |
| **Prompt Files** | 4 | Markdown instruction files |

**Problem:** No centralized configuration management.

---

## Agent-to-Agent Dependencies

```
IntentRouter
  ├─ Calls → LLMIntentClassifier (if pattern match fails)
  └─ Routes to → InvestigationRouter (if investigation detected)

InvestigationRouter
  ├─ Coordinates → SecurityScannerAgent
  ├─ Coordinates → RCAAgent
  ├─ Coordinates → PerformanceAnalyzer
  └─ Coordinates → ArchitectureAnalyzer

LearningCaptureAgent
  ├─ Used by → All agents (passive capture)
  └─ Read by → SessionResumer

ProfileAgent
  ├─ Used by → All agents (apply preferences)
  └─ Updated by → User corrections

ScreenshotAnalyzer
  ├─ Triggered by → Image attachment detection
  └─ Used by → Planning, Debug, ADO orchestrators
```

**Issue:** Circular dependencies possible, no dependency injection.

---

## v5.0 Agent Layer Vision

### Proposed Changes

1. **Agent Registry:** Centralized config-driven registry
   ```yaml
   agents:
     intent_router:
       class: IntentRouter
       config: config/intent-router.yaml
       priority: 1
   ```

2. **Configuration Externalization:** All agents read from YAML configs

3. **Database Integration:** Agents can query planning state, sessions

4. **MCP Protocol:** Agents can invoke orchestrators via MCP

5. **Dependency Injection:** Agents receive dependencies at initialization

### Migration Priority

**High Priority (Phase 7):**
- IntentRouter → Use LLM classifier as primary
- LearningCaptureAgent → Add log rotation
- SessionResumer → SQLite storage
- ADO Agent → Extract to orchestrator

**Medium Priority (Phase 7-8):**
- InvestigationRouter → Externalize registry
- ProfileAgent → Multi-user support
- ScreenshotAnalyzer → Add caching

**Low Priority (Phase 9+):**
- Remaining agents → Assess individual needs
- Documentation agents → Keep as-is (work well)
- Utility agents → Minor improvements

---

**Status:** ✅ Agent Inventory Complete  
**Phase 0 Complete:** All Task 0.3 artifacts delivered  
**Next:** Create git checkpoint for Phase 0
