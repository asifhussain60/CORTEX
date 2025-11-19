# Model Context Protocol (MCP) Integration - CORTEX 4.0 Planning

**Date:** November 19, 2025  
**Author:** Asif Hussain  
**Status:** Planning Phase  
**Target Release:** CORTEX 4.0 (Q3 2026)

---

## 🎯 Executive Summary

Model Context Protocol (MCP) is an open standard created by Anthropic that enables AI models to securely connect to external data sources and tools. For CORTEX, MCP integration represents a fundamental architectural evolution - transforming from a purely local-first system to an **adaptive local-first system** that can optionally leverage external knowledge while maintaining core privacy and offline capabilities.

**Key Decision:** MCP integration is a **CORTEX 4.0 feature** due to architectural complexity and the need for backward compatibility preservation.

---

## 🏗️ What is Model Context Protocol?

### Core Concepts

**MCP enables AI systems to:**
1. **Connect to External Resources** - Databases, APIs, file systems, business tools
2. **Expose Tool Capabilities** - AI can invoke tools through standardized interfaces
3. **Maintain Context** - Long-running conversations with persistent context
4. **Preserve Security** - User controls what data AI can access

**MCP Components:**

```
┌─────────────────────────────────────────────────────┐
│                    AI Model                         │
│            (GitHub Copilot, Claude)                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ MCP Protocol
                  │
┌─────────────────▼───────────────────────────────────┐
│              MCP Host (CORTEX)                      │
│  - Manages connections to MCP servers               │
│  - Routes requests                                  │
│  - Handles authentication                           │
│  - Aggregates responses                             │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────┐
        │         │         │         │
┌───────▼──┐ ┌───▼────┐ ┌──▼────┐ ┌──▼────────┐
│ Pylance  │ │ GitHub │ │ MSSQL │ │ Filesystem│
│  Server  │ │ Server │ │ Server│ │   Server  │
└──────────┘ └────────┘ └───────┘ └───────────┘
   (Python)   (Issues)   (DB)      (Files)
```

### Why MCP Matters for CORTEX

**Current State (CORTEX 3.0):**
- ✅ Completely local-first (no external dependencies)
- ✅ Zero cloud services required
- ✅ Full offline operation
- ❌ No access to external knowledge (Stack Overflow, GitHub Docs, API specs)
- ❌ Limited to local codebase context only
- ❌ Cannot leverage language-specific analysis tools

**With MCP (CORTEX 4.0):**
- ✅ **Maintain local-first core** (no breaking change to privacy model)
- ✅ **Optionally enhance with external sources** (user controlled, opt-in)
- ✅ **Access specialized tools** (Pylance for Python, ESLint for JS, Ruff for linting)
- ✅ **Query external docs** (Stack Overflow, MDN, language specs) when online
- ✅ **Database introspection** (SQL Server, PostgreSQL schemas)
- ✅ **Business tool integration** (Jira, GitHub Issues, Slack)

---

## 🎨 CORTEX 4.0 MCP Architecture

### Adaptive Local-First Design

**Core Principle:** CORTEX remains fully functional offline. MCP servers are **optional enhancements** that activate when available.

```python
# CORTEX 4.0 Knowledge Resolution (Adaptive)

class AdaptiveKnowledgeResolver:
    """
    Resolves knowledge queries using tiered fallback:
    1. Tier 1 (Working Memory) - Always available
    2. Tier 2 (Knowledge Graph) - Always available
    3. Tier 3 (Context Intelligence) - Always available
    4. MCP Servers (Optional) - If enabled and online
    5. Cached MCP Responses - If previously fetched
    """
    
    def resolve_query(self, query: str, context: dict) -> dict:
        # Step 1: Check local tiers first (fast, always available)
        local_result = self.query_local_tiers(query, context)
        
        if local_result["confidence"] >= 0.8:
            return local_result  # High confidence from local data
        
        # Step 2: Optionally enhance with MCP (if enabled)
        if self.config.get("mcp_enabled", False) and self.is_online():
            mcp_result = self.query_mcp_servers(query, context)
            
            # Merge local + MCP results
            return self.merge_results(local_result, mcp_result)
        
        # Step 3: Check MCP cache (previously fetched external data)
        cached = self.get_cached_mcp_response(query)
        if cached:
            return self.merge_results(local_result, cached)
        
        # Step 4: Return local-only result (offline mode)
        return local_result
```

### MCP Server Integration Points

**CORTEX 4.0 will integrate with these MCP servers:**

#### 1. **Pylance MCP Server** ✅ (ALREADY INTEGRATED!)

**Status:** CORTEX already has Pylance MCP integration via GitHub Copilot!

**Tools Available:**
- `mcp_pylance_mcp_s_pylanceImports` - Get all imports across workspace
- `mcp_pylance_mcp_s_pylanceInstalledTopLevelModules` - Available Python modules
- `mcp_pylance_mcp_s_pylanceWorkspaceUserFiles` - All Python files in workspace
- `mcp_pylance_mcp_s_pylanceRunCodeSnippet` - Execute Python code
- `mcp_pylance_mcp_s_pylanceInvokeRefactoring` - Apply refactorings (fix imports, etc.)

**CORTEX 4.0 Enhancement:** Deeper integration with Tier 2 Knowledge Graph

```python
# Example: Use Pylance to discover Python dependencies
from mcp_pylance import PylanceTools

class PythonKnowledgeEnhancer:
    def enhance_tier2_with_pylance(self, workspace_root: str):
        """Use Pylance MCP to enrich Tier 2 knowledge graph"""
        
        # Get all Python files
        files = PylanceTools.get_workspace_user_files(workspace_root)
        
        # Get imports for each file
        for file in files:
            imports = PylanceTools.get_imports(workspace_root, file)
            
            # Store in Tier 2 as file relationships
            for imported_module in imports:
                kg.track_relationship(
                    file_a=file,
                    file_b=imported_module,
                    relationship_type="imports",
                    strength=1.0,
                    context="Discovered via Pylance MCP"
                )
```

**Benefits:**
- ✅ Python-specific insights (imports, module availability)
- ✅ Refactoring capabilities (auto-fix imports)
- ✅ Type analysis (future: type-aware suggestions)

#### 2. **MSSQL MCP Server** (Planned)

**Purpose:** Database schema introspection for SQL Server

**Use Cases:**
- Generate SQL queries based on actual schema
- Suggest table/column names (autocomplete)
- Validate foreign key relationships
- Generate Entity Framework models from database

**Integration:**
```python
# Example: Use MSSQL MCP to generate queries
from mcp_mssql import MSSQLTools

class SQLQueryAssistant:
    def generate_query(self, user_request: str, connection_id: str):
        """Generate SQL query using actual database schema"""
        
        # Get schema from MSSQL MCP
        tables = MSSQLTools.list_tables(connection_id)
        
        # Use Tier 2 patterns + live schema
        pattern = kg.search_patterns(query="SELECT query templates")
        
        # Generate query with schema-aware completion
        query = self.generate_sql_with_schema(user_request, tables, pattern)
        
        return query
```

**Benefits:**
- ✅ Schema-aware SQL generation
- ✅ Reduced syntax errors (real column names)
- ✅ Foreign key relationship discovery

#### 3. **Filesystem MCP Server** (Planned)

**Purpose:** Safe file system operations with permissions

**Use Cases:**
- Read project files outside CORTEX workspace
- Search across multiple repositories
- Backup/restore operations
- Log file analysis

**Integration:**
```python
# Example: Use Filesystem MCP for multi-repo analysis
from mcp_filesystem import FilesystemTools

class MultiRepoAnalyzer:
    def analyze_monorepo(self, repos: list[str]):
        """Analyze multiple repositories safely"""
        
        for repo in repos:
            # Request permission to access repo
            if not FilesystemTools.has_permission(repo):
                FilesystemTools.request_permission(repo, reason="Analysis")
            
            # Safe file operations
            files = FilesystemTools.list_files(repo, pattern="**/*.py")
            
            # Store relationships in Tier 2
            for file in files:
                content = FilesystemTools.read_file(file)
                kg.analyze_and_store(file, content, namespace=f"repo.{repo}")
```

**Benefits:**
- ✅ Multi-repository support
- ✅ Permission-based security
- ✅ Cross-project pattern learning

#### 4. **GitHub MCP Server** (Planned)

**Purpose:** Access GitHub Issues, PRs, Discussions

**Use Cases:**
- Import GitHub Issues as ADO work items
- Reference PR discussions in context
- Link code changes to issues automatically
- Discover related issues/PRs

**Integration:**
```python
# Example: Import GitHub Issue as ADO work item
from mcp_github import GitHubTools

class GitHubIntegration:
    def import_issue_as_ado(self, issue_url: str):
        """Import GitHub Issue into CORTEX ADO system"""
        
        # Fetch issue from GitHub MCP
        issue = GitHubTools.get_issue(issue_url)
        
        # Create ADO work item
        ado_item = ADOManager.create_work_item(
            title=issue["title"],
            description=issue["body"],
            labels=issue["labels"],
            source="GitHub",
            source_id=issue["number"]
        )
        
        return ado_item
```

**Benefits:**
- ✅ GitHub Issues ↔ CORTEX ADO synchronization
- ✅ PR context integration
- ✅ Issue-driven development workflow

#### 5. **Stack Overflow MCP Server** (Planned)

**Purpose:** Query Stack Overflow for solutions

**Use Cases:**
- Error message search
- Best practice discovery
- Framework-specific guidance
- Community knowledge

**Integration:**
```python
# Example: Enhance error correction with Stack Overflow
from mcp_stackoverflow import StackOverflowTools

class EnhancedErrorCorrector:
    def fix_error_with_context(self, error_message: str, code: str):
        """Fix error using local patterns + Stack Overflow knowledge"""
        
        # Step 1: Check Tier 2 local patterns
        local_fix = kg.search_patterns(query=f"error: {error_message}")
        
        if local_fix["confidence"] >= 0.8:
            return local_fix  # High confidence local fix
        
        # Step 2: Query Stack Overflow (if enabled and online)
        if self.config.get("mcp_stackoverflow_enabled", False):
            so_results = StackOverflowTools.search(
                query=error_message,
                tags=self.detect_tags(code),  # e.g., ["python", "asyncio"]
                sort="votes",
                limit=3
            )
            
            # Learn from Stack Overflow answer
            kg.store_pattern(
                title=f"Fix for: {error_message}",
                pattern_type="error_solution",
                confidence=0.7,  # External source
                context={
                    "error": error_message,
                    "solution": so_results[0]["answer"],
                    "source": "Stack Overflow",
                    "votes": so_results[0]["score"]
                },
                scope="application",
                namespaces=["external", "stackoverflow"]
            )
            
            return so_results[0]
```

**Benefits:**
- ✅ Access to millions of solved problems
- ✅ Community-validated solutions
- ✅ Learn from expert answers

---

## ⚙️ Configuration & Privacy

### User Control (Opt-In Model)

**CORTEX 4.0 Configuration:**

```yaml
# cortex.config.json (CORTEX 4.0)

mcp:
  enabled: false  # Global MCP toggle (off by default)
  
  servers:
    pylance:
      enabled: true  # Already integrated
      auto_enhance_tier2: true  # Use Pylance to enrich knowledge graph
    
    mssql:
      enabled: false
      connections:
        - name: "Production DB"
          connection_string: "${MSSQL_CONNECTION_STRING}"
          read_only: true  # Safety: Only SELECT queries allowed
    
    filesystem:
      enabled: false
      allowed_paths:  # Whitelist of accessible paths
        - "${HOME}/projects/*"
        - "/opt/company/repos/*"
      blocked_paths:  # Blacklist (takes precedence)
        - "${HOME}/.ssh/*"
        - "${HOME}/.aws/*"
    
    github:
      enabled: false
      auth_token: "${GITHUB_TOKEN}"
      rate_limit: 60  # requests per hour
      cache_duration: 3600  # 1 hour
    
    stackoverflow:
      enabled: false
      api_key: "${STACKOVERFLOW_API_KEY}"  # Optional: Higher rate limits with key
      rate_limit: 30  # requests per hour
      cache_duration: 86400  # 24 hours (answers rarely change)
  
  privacy:
    never_send_to_external:
      - "*.env"
      - "*.key"
      - "*.pem"
      - "secrets/*"
      - "credentials/*"
    
    log_external_queries: true  # Audit trail
    require_user_approval: true  # Confirm before each external query
    offline_mode: false  # Force offline (ignore MCP even if enabled)
```

### Privacy Guarantees

**CORTEX 4.0 Privacy Model:**

1. **Local-First Remains Default** - MCP disabled by default
2. **Explicit Opt-In** - User must enable MCP servers individually
3. **Granular Control** - Enable only specific servers (e.g., Pylance yes, Stack Overflow no)
4. **Sensitive Data Protection** - Never send `.env`, keys, credentials to external servers
5. **Offline Mode** - Full functionality without MCP
6. **Audit Trail** - Log all external queries for transparency
7. **User Approval** - Prompt before first external query

**Example User Experience:**

```
User: "How do I fix asyncio.run() error in Python?"

CORTEX: "I found a local solution (Tier 2: 65% confidence)
         
         Would you like me to also check Stack Overflow?
         (This will send the error message to stackoverflow.com)
         
         [Yes, check Stack Overflow] [No, use local solution only]"

User: Clicks "Yes"

CORTEX: "✅ Querying Stack Overflow...
         📊 Found 3 solutions (sorted by votes)
         💾 Caching result locally (24h)
         📝 Logged query to cortex-brain/logs/mcp-queries.log
         
         Top solution (42 votes):
         [Shows Stack Overflow answer]"
```

---

## 🎯 Implementation Roadmap

### Phase 1: MCP Foundation (Weeks 1-4)

**Goal:** Establish MCP host infrastructure

**Deliverables:**
- [ ] `src/mcp/mcp_host.py` - MCP host implementation
- [ ] `src/mcp/server_registry.py` - MCP server registry
- [ ] `src/mcp/protocol.py` - MCP protocol handling
- [ ] MCP configuration schema in `cortex.config.json`
- [ ] Privacy enforcement layer

**Success Criteria:**
- CORTEX can connect to local Pylance MCP server
- Configuration toggles work (enable/disable servers)
- Privacy rules block sensitive data from external queries

---

### Phase 2: Pylance Deep Integration (Weeks 5-8)

**Goal:** Enhance Tier 2 Knowledge Graph with Pylance insights

**Deliverables:**
- [ ] Python dependency graph auto-generated from Pylance
- [ ] Import relationship tracking (file A imports B)
- [ ] Module availability checking (before suggesting imports)
- [ ] Refactoring integration (fix imports, organize imports)

**Success Criteria:**
- Tier 2 automatically discovers Python file relationships
- CORTEX suggests correct imports based on available modules
- Import errors reduced by 80% (Pylance validation)

---

### Phase 3: Database Introspection (Weeks 9-12)

**Goal:** Add MSSQL MCP server for schema-aware SQL generation

**Deliverables:**
- [ ] MSSQL MCP client implementation
- [ ] Schema caching (local Tier 2 storage)
- [ ] SQL query generation using live schema
- [ ] Entity Framework model generation

**Success Criteria:**
- CORTEX generates SQL queries with correct table/column names
- Foreign key relationships auto-discovered
- Zero SQL syntax errors from wrong column names

---

### Phase 4: External Knowledge (Weeks 13-16)

**Goal:** Add Stack Overflow and GitHub MCP servers

**Deliverables:**
- [ ] Stack Overflow MCP client
- [ ] GitHub MCP client
- [ ] Error correction enhancement (Stack Overflow integration)
- [ ] GitHub Issue ↔ ADO synchronization

**Success Criteria:**
- Error corrections include Stack Overflow solutions when local confidence < 80%
- GitHub Issues importable as ADO work items
- External knowledge cached locally (reduce API calls)

---

### Phase 5: Testing & Polish (Weeks 17-20)

**Goal:** Production-ready MCP integration

**Deliverables:**
- [ ] Integration tests for all MCP servers
- [ ] Performance benchmarks (response time with MCP)
- [ ] Privacy audit (verify no data leaks)
- [ ] User documentation (MCP setup guide)
- [ ] Migration guide (CORTEX 3.0 → 4.0)

**Success Criteria:**
- 100% test pass rate
- MCP queries < 500ms average
- Privacy tests pass (no sensitive data leaked)
- User documentation complete

---

## 📊 Impact Analysis

### Benefits

**For Users:**
- ✅ **Smarter Suggestions** - External knowledge enhances local patterns
- ✅ **Faster Debugging** - Stack Overflow integration finds solutions faster
- ✅ **Better SQL** - Database introspection prevents syntax errors
- ✅ **Cross-Tool Workflow** - GitHub Issues ↔ CORTEX ADO integration

**For CORTEX:**
- ✅ **Competitive Advantage** - Match/exceed GitHub Copilot's external data access
- ✅ **Ecosystem Integration** - Standard MCP protocol enables future expansions
- ✅ **Community Growth** - Users can create custom MCP servers

### Risks & Mitigations

**Risk 1: Privacy Concerns**
- **Mitigation:** Opt-in only, explicit user approval, local-first remains default
- **Monitoring:** Audit trail logs all external queries

**Risk 2: Performance Degradation**
- **Mitigation:** Aggressive caching (24h for Stack Overflow), local-first resolution priority
- **Monitoring:** Performance benchmarks in CI/CD

**Risk 3: External API Rate Limits**
- **Mitigation:** Caching, rate limit configuration per server
- **Monitoring:** Track API quota usage, warn before limit

**Risk 4: Breaking Changes from 3.0**
- **Mitigation:** Backward compatibility mode (MCP disabled = CORTEX 3.0 behavior)
- **Migration:** Automated migration tool provided

---

## 🎓 Key Decisions

### Why CORTEX 4.0 (Not 3.1)?

**Reasons:**
1. **Architectural Complexity** - MCP requires host infrastructure, not a small enhancement
2. **Configuration Overhaul** - New MCP section in `cortex.config.json`
3. **Privacy Model Change** - From "never external" to "optionally external"
4. **Breaking Potential** - While backward compatible, behavior changes significantly
5. **Development Timeline** - 16-20 weeks is a major release cycle

**Decision:** MCP is a **major version feature** warranting 4.0 designation

---

### MCP Server Priority

**High Priority (Phase 1-2):**
1. ✅ Pylance (Already integrated - deepen usage)
2. MSSQL (Database introspection)

**Medium Priority (Phase 3-4):**
3. Stack Overflow (Error correction)
4. GitHub (Issue integration)

**Low Priority (Future):**
5. Filesystem (Multi-repo)
6. Slack (Notifications)
7. Jira (Work item sync)

---

## 📚 References

**MCP Specification:**
- Official MCP Docs: https://modelcontextprotocol.io
- Anthropic GitHub: https://github.com/anthropics/anthropic-quickstarts

**Existing CORTEX Documentation:**
- CORTEX 3.0 Roadmap: `cortex-brain/documents/planning/CORTEX-3.0-VS-4.0-FEATURE-ROADMAP.md`
- File Dependency Analysis: `cortex-brain/documents/analysis/FILE-DEPENDENCY-ANALYSIS.md` (Pylance MCP already used!)

**Integration Examples:**
- Pylance MCP Server: Already available in GitHub Copilot
- MSSQL MCP Tools: `mssql_connect`, `mssql_run_query`, `mssql_show_schema`

---

## ✅ Next Steps

**Immediate Actions:**
1. **Research Phase Complete** ✅ (This document)
2. **Prototype MCP Host** - Create proof-of-concept MCP client (Week 1-2)
3. **Pylance Deep Dive** - Test all Pylance MCP tools (Week 3)
4. **Privacy Framework** - Design sensitive data detection rules (Week 4)
5. **User Feedback** - Survey CORTEX users on MCP priorities (Ongoing)

**Decision Points:**
- [ ] Approve CORTEX 4.0 MCP architecture (this document)
- [ ] Prioritize MCP servers (Pylance → MSSQL → Stack Overflow → GitHub)
- [ ] Finalize privacy model (opt-in, audit trail, user approval)
- [ ] Set CORTEX 4.0 release date (Target: Q3 2026)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Repository:** https://github.com/asifhussain60/CORTEX
