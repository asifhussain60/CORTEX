# CORTEX 4.0 Brain Architecture & Storage Options

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 9, 2025  
**Classification:** Technical Architecture Document

---

## 📋 Executive Summary

Comprehensive brain architecture for CORTEX 4.0 organization-level deployment, covering:
- Storage technology options (SQL Server, PostgreSQL, MongoDB, SQLite, hybrid)
- 4-tier federation strategy (Company → Team → Project)
- Learning and forgetting mechanisms
- Company-level Tier 0 governance (immutable business rules)
- Data lifecycle management

---

## 🏗️ Brain Storage Options (Comparison)

### Option 1: SQL Server (Recommended for Microsoft Shops)

**Architecture:**
```
Company Brain: SQL Server (existing instance)
├── Database: cortex_company
├── Schemas: cortex_team_backend, cortex_team_frontend, etc.
└── Tables: policies, patterns, metrics, conversations

Team Brains: SQL Server schemas (same instance)
├── cortex_team_backend (Backend team)
├── cortex_team_frontend (Frontend team)
└── cortex_team_devops (DevOps team)

Project Brains: SQLite files (per repository)
├── repo1/.cortex/brain.db
├── repo2/.cortex/brain.db
└── repo3/.cortex/brain.db
```

**Pros:**
- ✅ Leverage existing SQL Server infrastructure ($0 new database cost)
- ✅ Familiar to DBAs (standard backup/recovery procedures)
- ✅ Excellent ACID compliance (critical for patterns)
- ✅ Full-text search built-in
- ✅ Row-level security for team isolation
- ✅ Azure SQL option for cloud deployments

**Cons:**
- ❌ Windows/Azure-centric (less portable)
- ❌ Licensing costs if not already owned
- ❌ Heavier resource footprint

**Best For:** Organizations already using SQL Server, Microsoft-centric stacks, Azure cloud

**Cost:**
- Existing SQL Server: $0/year
- New SQL Server Standard: $3,700/year (2-core license)
- Azure SQL Database: $100-300/month ($1,200-3,600/year)

---

### Option 2: PostgreSQL (Recommended for Open-Source Preference)

**Architecture:**
```
Company Brain: PostgreSQL database
├── Schemas: company, team_backend, team_frontend
└── Tables: policies, patterns, metrics (similar to SQL Server)

Team Brains: PostgreSQL schemas (same database)
Project Brains: SQLite files (per repository)
```

**Pros:**
- ✅ Free and open-source ($0 licensing)
- ✅ Excellent performance and scalability
- ✅ Rich JSON support (flexible pattern storage)
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Cloud options: AWS RDS, Azure Database for PostgreSQL, Google Cloud SQL
- ✅ Full-text search (tsvector/tsquery)
- ✅ Row-level security (RLS) for team isolation

**Cons:**
- ❌ Less familiar to SQL Server DBAs
- ❌ Requires PostgreSQL expertise

**Best For:** Organizations preferring open-source, multi-platform environments, cloud-agnostic

**Cost:**
- Self-hosted PostgreSQL: $0/year (infrastructure only)
- AWS RDS PostgreSQL: $50-200/month ($600-2,400/year)
- Azure Database for PostgreSQL: $50-200/month

---

### Option 3: MongoDB (Document-Oriented)

**Architecture:**
```
Company Brain: MongoDB database
├── Collections: policies, patterns, metrics, conversations
└── Documents: JSON-based (flexible schema)

Team Brains: MongoDB collections with team_id field
Project Brains: SQLite files (per repository)
```

**Pros:**
- ✅ Schema flexibility (evolve patterns without migrations)
- ✅ Native JSON support (perfect for AI/LLM data)
- ✅ Horizontal scaling (sharding for large orgs)
- ✅ Cloud options: MongoDB Atlas (managed)
- ✅ Fast writes (async pattern storage)

**Cons:**
- ❌ Less mature full-text search
- ❌ No ACID transactions across collections (older versions)
- ❌ Requires NoSQL expertise
- ❌ Higher storage overhead

**Best For:** Organizations with NoSQL expertise, need extreme flexibility, plan to scale beyond org-level

**Cost:**
- Self-hosted MongoDB: $0/year
- MongoDB Atlas: $60-300/month ($720-3,600/year)

---

### Option 4: Hybrid (SQL + File Storage)

**Architecture:**
```
Company Brain: SQL Server/PostgreSQL (structured data)
├── Tables: policies, teams, users, metrics
└── Purpose: Governance, relationships, analytics

Pattern Storage: Azure Blob Storage / S3 (JSON files)
├── patterns/team_backend/error_handling_2024_12.json
├── patterns/team_frontend/react_patterns_2024_11.json
└── Purpose: Large pattern documents, versioning

Search Index: Azure Cognitive Search / Elasticsearch
└── Purpose: Fast pattern search, recommendations

Project Brains: SQLite files (per repository)
```

**Pros:**
- ✅ Best of both worlds (structured + unstructured)
- ✅ Lower database storage costs (blob storage cheap)
- ✅ Versioning built-in (blob snapshots)
- ✅ Scalable search (dedicated search engine)
- ✅ Easier backup (file-based patterns)

**Cons:**
- ❌ More complex architecture
- ❌ Consistency challenges (multiple systems)
- ❌ More moving parts to maintain

**Best For:** Large organizations (150+ devs), need to scale, have DevOps expertise

**Cost:**
- Database: $100-200/month
- Blob Storage: $10-30/month (very cheap)
- Cognitive Search: $250-300/month
- **Total:** $360-530/month ($4,320-6,360/year)

---

### Option 5: Lightweight (SQLite Only)

**Architecture:**
```
Company Brain: SQLite file (~/.cortex/company/brain.db)
Team Brains: SQLite files (~/.cortex/teams/{team_id}/brain.db)
Project Brains: SQLite files ({repo}/.cortex/brain.db)
```

**Pros:**
- ✅ Zero infrastructure cost
- ✅ Simple deployment (just files)
- ✅ No database server required
- ✅ Perfect for small organizations (<50 devs)
- ✅ Easy backup (copy files)

**Cons:**
- ❌ No concurrent write scaling (locks)
- ❌ No network access (local files only)
- ❌ No advanced features (row-level security)
- ❌ Limited full-text search

**Best For:** Small teams (10-50 devs), proof-of-concept, budget-constrained

**Cost:** $0/year (no infrastructure)

---

## 📊 Storage Option Comparison Table

| Criteria | SQL Server | PostgreSQL | MongoDB | Hybrid | SQLite Only |
|----------|-----------|------------|---------|--------|-------------|
| **Cost (existing)** | $0 | $0 | $0 | $4-6K/year | $0 |
| **Cost (new)** | $1.2-3.7K | $0-2.4K | $0-3.6K | $4-6K/year | $0 |
| **Scalability** | Excellent | Excellent | Excellent | Excellent | Poor |
| **Complexity** | Medium | Medium | Medium | High | Low |
| **Microsoft Stack Fit** | Perfect | Good | Fair | Good | Good |
| **Open-Source** | ❌ | ✅ | ✅ | Mixed | ✅ |
| **Cloud-Ready** | Azure | Multi-cloud | Multi-cloud | Multi-cloud | ❌ |
| **Best For Org Size** | 50-200+ | 50-200+ | 100-500+ | 150-1000+ | 10-50 |

---

## 🎯 Recommended Configuration by Organization Size

**Small Org (10-50 developers):**
- **Recommendation:** SQLite Only
- **Rationale:** Zero cost, simple, sufficient for small teams
- **Limitations:** Must stay small (concurrency issues beyond 50 devs)

**Medium Org (50-200 developers) - Microsoft Stack:**
- **Recommendation:** SQL Server
- **Rationale:** Leverage existing infrastructure, familiar to team
- **Cost:** $0 if existing, $1,200-3,700/year if new

**Medium Org (50-200 developers) - Open-Source Preference:**
- **Recommendation:** PostgreSQL
- **Rationale:** Free, excellent performance, cloud-agnostic
- **Cost:** $0 self-hosted, $600-2,400/year managed

**Large Org (200-500 developers):**
- **Recommendation:** Hybrid (SQL + Blob + Search)
- **Rationale:** Scalability, performance, cost optimization
- **Cost:** $4,320-6,360/year

---

## 🧠 4-Tier Brain Architecture (Organization-Level)

### Tier 0: Governance (Immutable Business Rules)

**Purpose:** Company-wide policies that CORTEX NEVER deviates from

**Storage Location:**
```
Company Brain: cortex_company.policies
Team Brains: Inherit + extend company policies
Project Brains: Read-only view of policies
```

**Schema:**
```sql
CREATE TABLE cortex_company.policies (
    policy_id INT PRIMARY KEY IDENTITY,
    category VARCHAR(50),  -- security, compliance, coding_standards, architecture
    name VARCHAR(200),
    description TEXT,
    enforcement_level VARCHAR(20),  -- MANDATORY, RECOMMENDED, OPTIONAL
    rule_type VARCHAR(50),  -- PROHIBITION, REQUIREMENT, GUIDELINE
    rule_expression TEXT,  -- JSON rule definition
    created_at DATETIME2,
    created_by VARCHAR(100),
    version INT DEFAULT 1,
    active BIT DEFAULT 1,
    
    -- Audit trail
    last_modified_at DATETIME2,
    last_modified_by VARCHAR(100),
    change_reason TEXT
);

CREATE TABLE cortex_company.policy_violations (
    violation_id INT PRIMARY KEY IDENTITY,
    policy_id INT FOREIGN KEY REFERENCES policies(policy_id),
    user_id VARCHAR(100),
    violation_timestamp DATETIME2,
    violation_context TEXT,  -- What CORTEX attempted
    blocked BIT DEFAULT 1,  -- Whether action was blocked
    override_reason TEXT NULL  -- If admin overrode
);
```

**Example Policies:**

**1. Security Policy (MANDATORY):**
```json
{
  "policy_id": 1,
  "category": "security",
  "name": "No Hardcoded Secrets",
  "enforcement_level": "MANDATORY",
  "rule_type": "PROHIBITION",
  "rule_expression": {
    "type": "regex_prohibition",
    "patterns": [
      "password\\s*=\\s*['\"].*['\"]",
      "api[_-]?key\\s*=\\s*['\"].*['\"]",
      "secret\\s*=\\s*['\"].*['\"]",
      "connectionString\\s*=\\s*['\"].*['\"]"
    ],
    "message": "CORTEX detected hardcoded secret. Use Azure Key Vault or environment variables.",
    "action": "BLOCK_AND_SUGGEST_ALTERNATIVE"
  }
}
```

**2. Financial Data Policy (MANDATORY):**
```json
{
  "policy_id": 2,
  "category": "compliance",
  "name": "PCI DSS Compliance - No Credit Card Logging",
  "enforcement_level": "MANDATORY",
  "rule_type": "PROHIBITION",
  "rule_expression": {
    "type": "content_prohibition",
    "patterns": [
      "creditCard",
      "cardNumber",
      "cvv",
      "\\b\\d{13,19}\\b"
    ],
    "contexts": ["logging", "console_output", "exception_messages"],
    "message": "CORTEX detected potential credit card data in logging. PCI DSS prohibits this.",
    "action": "BLOCK_AND_REQUIRE_APPROVAL"
  }
}
```

**3. Architecture Policy (RECOMMENDED):**
```json
{
  "policy_id": 3,
  "category": "architecture",
  "name": "Microservices Communication via Message Queue",
  "enforcement_level": "RECOMMENDED",
  "rule_type": "GUIDELINE",
  "rule_expression": {
    "type": "pattern_suggestion",
    "trigger": "cross_service_http_call_detected",
    "message": "Consider using Azure Service Bus for async communication",
    "alternative_pattern_id": "async_messaging_pattern_001"
  }
}
```

**Policy Enforcement Mechanism:**

```python
# src/tier0/policy_enforcer.py
class PolicyEnforcer:
    """Enforces company Tier 0 policies - CORTEX NEVER deviates."""
    
    def enforce(self, action: str, context: Dict) -> PolicyDecision:
        """
        Check if proposed action violates any MANDATORY policies.
        
        Returns:
            PolicyDecision: ALLOW, BLOCK, WARN_AND_ALLOW
        """
        violated_policies = self.check_violations(action, context)
        
        # MANDATORY policies ALWAYS block
        mandatory_violations = [p for p in violated_policies if p.enforcement_level == "MANDATORY"]
        if mandatory_violations:
            self.log_violation(mandatory_violations, context)
            return PolicyDecision(
                decision="BLOCK",
                reason=f"Violates {len(mandatory_violations)} MANDATORY company policies",
                policies=mandatory_violations,
                alternative_suggestions=self.get_alternatives(mandatory_violations)
            )
        
        # RECOMMENDED policies warn but allow
        recommended_violations = [p for p in violated_policies if p.enforcement_level == "RECOMMENDED"]
        if recommended_violations:
            return PolicyDecision(
                decision="WARN_AND_ALLOW",
                reason="Violates RECOMMENDED guidelines",
                policies=recommended_violations,
                alternative_suggestions=self.get_alternatives(recommended_violations)
            )
        
        return PolicyDecision(decision="ALLOW")
```

**How Policies Are Created:**

1. **CTO/Security Team defines policies** (Governance Committee)
2. **Policies stored in `cortex_company.policies`** (version controlled)
3. **All CORTEX operations check policies before execution**
4. **Violations logged for audit** (`policy_violations` table)
5. **Policies can be updated but require approval workflow**

---

### Tier 1: Working Memory (Conversation Context)

**Purpose:** Recent conversations, active context, short-term patterns

**Storage Location:**
```
Company Brain: Aggregated metrics only (no individual conversations)
Team Brains: Team-level conversations (anonymized)
Project Brains: Full conversation history (local)
```

**Schema:**
```sql
-- Project Brain (SQLite)
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT,
    started_at TIMESTAMP,
    last_activity_at TIMESTAMP,
    operation_type TEXT,  -- planning, tdd, review, ado
    context TEXT,  -- JSON: files involved, work items, patterns used
    outcome TEXT,  -- success, failure, partial
    token_count INT,
    duration_seconds INT
);

CREATE TABLE conversation_messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT FOREIGN KEY,
    timestamp TIMESTAMP,
    role TEXT,  -- user, assistant
    content TEXT,  -- Full message content
    patterns_referenced TEXT,  -- JSON array of pattern_ids
    files_modified TEXT  -- JSON array of file paths
);
```

**FIFO Management (Prevent Bloat):**
```python
class ConversationManager:
    """Manages Tier 1 working memory with FIFO eviction."""
    
    MAX_CONVERSATIONS = 70  # Last 70 conversations kept
    
    def add_conversation(self, conversation: Conversation):
        """Add new conversation, evict oldest if over limit."""
        self.db.insert_conversation(conversation)
        
        # Count conversations
        count = self.db.count_conversations()
        if count > self.MAX_CONVERSATIONS:
            # Evict oldest, but promote valuable patterns first
            oldest = self.db.get_oldest_conversations(count - self.MAX_CONVERSATIONS)
            for conv in oldest:
                self.promote_patterns(conv)  # Extract patterns before deletion
                self.db.delete_conversation(conv.id)
    
    def promote_patterns(self, conversation: Conversation):
        """
        Before deleting conversation, extract valuable patterns to Tier 2.
        """
        # Analyze conversation for reusable patterns
        patterns = self.pattern_extractor.extract(conversation)
        for pattern in patterns:
            if pattern.quality_score > 0.7:  # High quality
                self.tier2.save_pattern(pattern)
```

---

### Tier 2: Knowledge Graph (Long-Term Patterns)

**Purpose:** Org-wide patterns, best practices, lessons learned

**Storage Location:**
```
Company Brain: Approved organization-wide patterns
Team Brains: Team-specific patterns
Project Brains: Project-specific patterns (candidates for promotion)
```

**Schema:**
```sql
CREATE TABLE cortex_company.patterns (
    pattern_id INT PRIMARY KEY IDENTITY,
    pattern_name VARCHAR(200),
    pattern_type VARCHAR(50),  -- code_pattern, architecture, testing, security
    category VARCHAR(50),  -- error_handling, authentication, caching, etc.
    
    -- Pattern Content
    description TEXT,
    problem_statement TEXT,  -- What problem does this solve?
    solution TEXT,  -- How to solve it?
    example_code TEXT,  -- Code snippet (anonymized)
    when_to_use TEXT,  -- Guidance on applicability
    edge_cases TEXT,  -- Known limitations
    
    -- Metadata
    created_at DATETIME2,
    created_by_team INT FOREIGN KEY REFERENCES teams(team_id),
    promoted_from_project VARCHAR(200),  -- Original repo
    
    -- Quality Metrics
    usage_count INT DEFAULT 0,  -- How many times used
    success_rate DECIMAL(5,2),  -- % of successful applications
    rating_avg DECIMAL(3,2),  -- User ratings (1-5)
    rating_count INT DEFAULT 0,
    
    -- Lifecycle
    status VARCHAR(20),  -- draft, approved, deprecated
    approval_date DATETIME2 NULL,
    approved_by VARCHAR(100) NULL,
    deprecation_reason TEXT NULL,
    
    -- Versioning
    version INT DEFAULT 1,
    previous_version_id INT NULL FOREIGN KEY REFERENCES patterns(pattern_id)
);

CREATE TABLE cortex_company.pattern_usage (
    usage_id INT PRIMARY KEY IDENTITY,
    pattern_id INT FOREIGN KEY REFERENCES patterns(pattern_id),
    user_id VARCHAR(100),
    team_id INT,
    project_repo VARCHAR(200),
    used_at DATETIME2,
    success BIT,  -- Did it work?
    feedback TEXT NULL,  -- User comments
    modified BIT  -- Did user modify the pattern?
);

CREATE TABLE cortex_company.pattern_relationships (
    relationship_id INT PRIMARY KEY IDENTITY,
    pattern_id_1 INT FOREIGN KEY REFERENCES patterns(pattern_id),
    pattern_id_2 INT FOREIGN KEY REFERENCES patterns(pattern_id),
    relationship_type VARCHAR(50),  -- COMPLEMENTS, REPLACES, CONFLICTS_WITH
    strength DECIMAL(3,2)  -- 0.0-1.0 (for recommendations)
);
```

**Pattern Promotion Workflow:**

```
1. Developer uses CORTEX successfully on feature
   ↓
2. CORTEX extracts pattern from conversation
   ↓
3. Pattern saved to Project Brain (status: draft)
   ↓
4. If used 3+ times successfully → Suggest promotion to Team Brain
   ↓
5. Team Lead reviews and approves → Promoted to Team Brain
   ↓
6. If 2+ teams use pattern → Suggest promotion to Company Brain
   ↓
7. Architecture Review Board approves → Company Brain (official)
```

**Learning Mechanism:**

```python
class PatternLearner:
    """Learns patterns from successful conversations."""
    
    def extract_pattern(self, conversation: Conversation) -> Optional[Pattern]:
        """
        Extract reusable pattern from conversation.
        
        Criteria for extraction:
        1. Conversation marked successful by user
        2. Contains code or architecture decision
        3. Problem + solution structure identifiable
        4. Not a one-off solution (reusable)
        """
        if not conversation.outcome == "success":
            return None
        
        # Use LLM to analyze conversation
        analysis = self.llm.analyze(
            conversation.messages,
            prompt="""
            Analyze this conversation and extract a reusable pattern if present.
            Pattern structure:
            - Problem: What issue was being solved?
            - Solution: How was it solved?
            - Code: Example implementation
            - When to use: Applicability guidance
            
            Return JSON or null if no pattern found.
            """
        )
        
        if analysis.pattern_found:
            pattern = Pattern(
                name=analysis.pattern_name,
                type=analysis.pattern_type,
                problem_statement=analysis.problem,
                solution=analysis.solution,
                example_code=self.anonymize_code(analysis.code),
                status="draft",
                quality_score=self.calculate_quality(analysis)
            )
            return pattern
        
        return None
    
    def anonymize_code(self, code: str) -> str:
        """Remove company-specific details from code."""
        # Remove API keys, credentials
        code = re.sub(r'api[_-]?key\s*=\s*["\'].*?["\']', 'api_key = "YOUR_API_KEY"', code)
        # Remove internal URLs
        code = re.sub(r'https?://internal\..*?/', 'https://your-internal-url/', code)
        # Remove company database names
        code = re.sub(r'Database=CompanyDB', 'Database=YOUR_DATABASE', code)
        return code
```

---

### Tier 3: Development Context (Project Metrics)

**Purpose:** Code hotspots, team performance, technical debt

**Storage Location:**
```
Company Brain: Aggregated org-wide metrics
Team Brains: Team performance metrics
Project Brains: Repository-specific metrics
```

**Schema:**
```sql
CREATE TABLE cortex_project.code_hotspots (
    hotspot_id INTEGER PRIMARY KEY,
    file_path TEXT,
    churn_rate REAL,  -- Changes per week
    defect_density REAL,  -- Bugs per KLOC
    complexity_score INT,  -- Cyclomatic complexity
    last_modified TIMESTAMP,
    risk_level TEXT  -- LOW, MEDIUM, HIGH, CRITICAL
);

CREATE TABLE cortex_project.developer_metrics (
    metric_id INTEGER PRIMARY KEY,
    user_id TEXT,
    week_start DATE,
    commits INT,
    lines_added INT,
    lines_deleted INT,
    pr_count INT,
    pr_review_count INT,
    avg_pr_cycle_time_hours REAL
);
```

**Forgetting Mechanism (Data Lifecycle):**

```python
class BrainDataLifecycleManager:
    """Manages data retention and forgetting across all tiers."""
    
    RETENTION_POLICIES = {
        "tier1_conversations": 90,  # days
        "tier2_patterns_draft": 180,  # days
        "tier2_patterns_unused": 365,  # days
        "tier3_metrics_detailed": 180,  # days
        "tier3_metrics_aggregated": 730  # 2 years
    }
    
    def forget_old_data(self):
        """
        Periodically clean up old data (runs weekly).
        """
        # Tier 1: Delete conversations older than 90 days
        self.delete_old_conversations(days=90)
        
        # Tier 2: Archive unused patterns
        self.archive_unused_patterns(
            status="draft",
            days_unused=180,
            archive_location="cortex_company.archived_patterns"
        )
        
        # Tier 3: Aggregate and delete detailed metrics
        self.aggregate_old_metrics(days=180)
    
    def archive_unused_patterns(self, status: str, days_unused: int, archive_location: str):
        """
        Move unused patterns to archive (not deleted, just out of active brain).
        """
        unused_patterns = self.db.query("""
            SELECT pattern_id FROM cortex_company.patterns
            WHERE status = ?
              AND usage_count = 0
              AND DATEDIFF(day, created_at, GETDATE()) > ?
        """, [status, days_unused])
        
        for pattern_id in unused_patterns:
            # Move to archive table
            self.db.execute(f"""
                INSERT INTO {archive_location}
                SELECT * FROM cortex_company.patterns WHERE pattern_id = ?
            """, [pattern_id])
            
            # Delete from active brain
            self.db.execute("""
                DELETE FROM cortex_company.patterns WHERE pattern_id = ?
            """, [pattern_id])
```

---

## 🔒 Code Isolation Strategy (PREVENT CORTEX CODE IN USER REPOS)

### The Problem

CORTEX must NEVER add its own code (brain files, config files, orchestrators) into user repositories. This would:
- Pollute user codebases
- Create maintenance nightmare
- Violate separation of concerns
- Reduce adoption (developers fear contamination)

### Solution: Multi-Layer Protection

#### Layer 1: File System Isolation

**CORTEX Installation Location:**
```
~/.cortex/                          # User's home directory (NOT in repos)
├── company/
│   └── brain/                      # Company brain (organization-wide)
├── teams/
│   ├── backend/brain/              # Team brains (per team)
│   ├── frontend/brain/
│   └── devops/brain/
├── config/
│   └── cortex.config.json          # User settings
└── extensions/
    ├── vs_extension/               # Visual Studio extension
    └── vscode_extension/           # VS Code extension
```

**Project Brain Location (Per Repository):**
```
user-repo/                          # User's repository
├── .cortex/                        # ONLY brain data, nothing else
│   ├── brain.db                    # SQLite database (project brain)
│   ├── .gitignore                  # ALWAYS ignore this folder
│   └── README.md                   # Explains what this is
├── src/
│   └── app.cs                      # USER CODE (never CORTEX code)
└── tests/
    └── app.test.cs                 # USER CODE
```

**What's in `.cortex/.gitignore` (Auto-Created):**
```gitignore
# CORTEX Project Brain - Do NOT commit to repository
*
!.gitignore
!README.md

# This folder contains local CORTEX data:
# - Conversation history
# - Local patterns
# - Performance metrics
#
# It should NOT be committed because:
# 1. Contains user-specific data
# 2. Can be regenerated
# 3. May contain sensitive information
#
# CORTEX automatically creates and manages this folder.
```

#### Layer 2: Git Pre-Commit Hook

**Auto-Install Git Hook:**

```python
# src/tier0/code_isolation_enforcer.py
class CodeIsolationEnforcer:
    """Prevents CORTEX code from being committed to user repos."""
    
    def install_git_hook(self, repo_path: str):
        """
        Install pre-commit hook that blocks CORTEX code.
        """
        hook_path = os.path.join(repo_path, ".git", "hooks", "pre-commit")
        
        hook_script = """#!/usr/bin/env python3
# CORTEX Pre-Commit Hook - Prevents CORTEX code in user repos

import sys
import subprocess

# Files that should NEVER be committed
FORBIDDEN_PATTERNS = [
    "cortex_brain/**",           # Brain infrastructure
    "cortex_agents/**",          # CORTEX agents
    "cortex_orchestrators/**",   # Orchestrators
    "**/.cortex/brain.db",       # Local brain (should be in .gitignore)
    "**/cortex.config.json",     # CORTEX config (user-specific)
]

def check_forbidden_files():
    # Get staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    staged_files = result.stdout.strip().split("\\n")
    
    forbidden_found = []
    for file in staged_files:
        for pattern in FORBIDDEN_PATTERNS:
            if fnmatch.fnmatch(file, pattern):
                forbidden_found.append(file)
    
    if forbidden_found:
        print("❌ CORTEX CODE ISOLATION VIOLATION")
        print("\\nThe following CORTEX files should NOT be in user repositories:")
        for file in forbidden_found:
            print(f"  - {file}")
        print("\\nCORTEX code belongs in ~/.cortex/, not in project repos.")
        print("\\nCommit blocked. Please remove these files.\\n")
        sys.exit(1)

if __name__ == "__main__":
    check_forbidden_files()
"""
        
        with open(hook_path, 'w') as f:
            f.write(hook_script)
        
        # Make executable
        os.chmod(hook_path, 0o755)
        
        print(f"✅ Git hook installed: {hook_path}")
```

#### Layer 3: IDE Extension Guardrails

**Visual Studio Extension:**

```csharp
// CORTEX VS Extension - FileSystemMonitor.cs
public class FileSystemMonitor
{
    /// <summary>
    /// Monitors file system operations and blocks CORTEX code from user projects.
    /// </summary>
    public void OnBeforeFileSave(object sender, FileSaveEventArgs e)
    {
        string filePath = e.FilePath;
        string projectRoot = GetProjectRoot(filePath);
        
        // Check if saving CORTEX infrastructure file to user project
        if (IsCortexInfrastructureFile(filePath) && IsUserProject(projectRoot))
        {
            MessageBox.Show(
                "⚠️ CORTEX CODE ISOLATION VIOLATION\\n\\n" +
                $"Cannot save CORTEX infrastructure file to user project:\\n{filePath}\\n\\n" +
                "CORTEX code belongs in ~/.cortex/, not in project repositories.",
                "CORTEX Protection",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
            
            e.Cancel = true;  // Block save operation
        }
    }
    
    private bool IsCortexInfrastructureFile(string filePath)
    {
        string[] cortexPatterns = new[]
        {
            @"\\cortex_brain\\",
            @"\\cortex_agents\\",
            @"\\cortex_orchestrators\\",
            @"\\cortex.config.json",
            @"brain.db"
        };
        
        return cortexPatterns.Any(p => filePath.Contains(p, StringComparison.OrdinalIgnoreCase));
    }
}
```

#### Layer 4: Project Brain Isolation

**Only Metadata in Repos:**

```
.cortex/
├── .gitignore               # ALWAYS committed (tells git to ignore rest)
├── README.md                # ALWAYS committed (explains folder purpose)
└── brain.db                 # NEVER committed (in .gitignore)
```

**Auto-Create .gitignore:**

```python
def init_project_brain(repo_path: str):
    """
    Initialize project brain with proper isolation.
    """
    cortex_dir = os.path.join(repo_path, ".cortex")
    os.makedirs(cortex_dir, exist_ok=True)
    
    # Create .gitignore (always committed)
    gitignore_path = os.path.join(cortex_dir, ".gitignore")
    with open(gitignore_path, 'w') as f:
        f.write("*\n!.gitignore\n!README.md\n")
    
    # Create README (always committed)
    readme_path = os.path.join(cortex_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write("""# CORTEX Project Brain

This folder contains CORTEX AI assistant data for this repository:

- **brain.db**: Local conversation history and patterns (NOT committed)
- **Metrics**: Code quality and performance tracking (NOT committed)

**Why is this folder here?**
CORTEX uses this to remember context about your project, making suggestions more relevant over time.

**Is this safe?**
Yes. This folder is in `.gitignore` and will NOT be committed to version control.

**Can I delete it?**
Yes. CORTEX will recreate it automatically. You'll lose conversation history but patterns are backed up to organization brain.

For more info: https://github.com/asifhussain60/CORTEX
""")
    
    # Create brain database (never committed)
    brain_db_path = os.path.join(cortex_dir, "brain.db")
    init_sqlite_brain(brain_db_path)
    
    print(f"✅ Project brain initialized: {cortex_dir}")
```

---

**Continue to Increment 2 (Test Coverage Strategy)?**

Type "continue" for Test Coverage Acceleration document (20% → 90%).
