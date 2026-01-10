"""
Generate comprehensive CORTEX 6.0 architecture documentation
Creates modern HTML documentation with Google Fonts styling
"""

from pathlib import Path

# Base HTML template with styling
def get_html_template(title, breadcrumb_current, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX 6.0 - {title}</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&family=Crimson+Pro:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary: #00d4ff;
            --secondary: #7b2cbf;
            --accent: #ff006e;
            --success: #06ffa5;
            --warning: #ffbe0b;
            --danger: #ff006e;
            --bg-dark: #0a0a0f;
            --bg-darker: #050508;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #b0b0c0;
            --text-muted: #6c757d;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
            color: var(--text-primary);
            line-height: 1.8;
            min-height: 100vh;
        }}
        
        /* Breadcrumb */
        .breadcrumb {{
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            padding: 15px 30px;
            border-bottom: 1px solid var(--glass-border);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .breadcrumb-list {{
            list-style: none;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .breadcrumb-list a {{
            color: var(--primary);
            text-decoration: none;
            transition: all 0.3s;
            font-family: 'Space Grotesk', sans-serif;
        }}
        
        .breadcrumb-list a:hover {{ color: var(--accent); }}
        .breadcrumb-separator {{ color: var(--text-muted); }}
        .current {{ color: var(--text-secondary); }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 30px;
        }}
        
        h1 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.5em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}
        
        h2 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2em;
            color: var(--primary);
            margin: 50px 0 25px;
        }}
        
        h3 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.6em;
            color: var(--text-primary);
            margin: 35px 0 15px;
        }}
        
        .subtitle {{
            font-family: 'Crimson Pro', serif;
            font-size: 1.5em;
            color: var(--text-secondary);
            font-style: italic;
            margin-bottom: 30px;
        }}
        
        p {{
            margin-bottom: 20px;
            font-size: 1.05em;
            color: var(--text-secondary);
        }}
        
        .glass-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 30px;
            margin: 30px 0;
        }}
        
        .glass-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
            transition: all 0.3s;
        }}
        
        code {{
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 3px 8px;
            border-radius: 4px;
            color: var(--primary);
        }}
        
        pre {{
            background: rgba(0, 0, 0, 0.5);
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            border-left: 4px solid var(--primary);
            margin: 20px 0;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        ul, ol {{
            margin: 20px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 10px 0;
            color: var(--text-secondary);
        }}
        
        .highlight-box {{
            background: rgba(0, 212, 255, 0.1);
            border-left: 4px solid var(--primary);
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        
        .warning-box {{
            background: rgba(255, 190, 11, 0.1);
            border-left: 4px solid var(--warning);
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        
        .scroll-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 1000;
            color: #000;
            font-weight: bold;
        }}
        
        .scroll-top.visible {{ opacity: 1; }}
        .scroll-top:hover {{ background: var(--secondary); }}
    </style>
</head>
<body>
    <nav class="breadcrumb">
        <ul class="breadcrumb-list">
            <li><a href="../../templates/plan-viewer/cortex-plan-viewer.html">🏠 Home</a></li>
            <li><span class="breadcrumb-separator">›</span></li>
            <li><a href="#architecture">Architecture</a></li>
            <li><span class="breadcrumb-separator">›</span></li>
            <li class="current">{breadcrumb_current}</li>
        </ul>
    </nav>

    <div class="container">
        {content}
    </div>

    <div class="scroll-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">↑</div>

    <script>
        window.addEventListener('scroll', () => {{
            const scrollTop = document.querySelector('.scroll-top');
            if (window.scrollY > 500) {{
                scrollTop.classList.add('visible');
            }} else {{
                scrollTop.classList.remove('visible');
            }}
        }});
    </script>
</body>
</html>"""

# Content for each documentation file
docs = {
    "orchestration-design.html": {
        "title": "Orchestration Design",
        "breadcrumb": "Orchestration Design",
        "content": """
<h1>Orchestration Design</h1>
<p class="subtitle">How CORTEX 6.0 Orchestrators Work Together</p>

<div class="glass-card">
    <h2>🎭 Orchestration Philosophy</h2>
    <p>CORTEX 6.0 uses a <strong>hierarchical orchestration model</strong> where the MasterOrchestrator acts as the central coordinator, routing requests to specialized orchestrators based on capability and intent.</p>
    
    <div class="highlight-box">
        <strong>Key Principle:</strong> Every orchestrator operates autonomously within its domain, but all requests flow through governance enforcement and audit logging.
    </div>
</div>

<div class="glass-card">
    <h2>🔄 Request Flow Pipeline</h2>
    <pre><code>Request → GovernanceMerger → MasterOrchestrator → TodoManager → Execute
            (merge rules)      (evaluate)          (create tasks)</code></pre>
    
    <h3>Step 1: Governance Merger</h3>
    <p>Merges rules from 4 tiers (Tier 0 SKULL + Tier 1 Business + Tier 2 Standards + Tier 3 Learned).</p>
    <ul>
        <li><strong>Input:</strong> User request + current epic context</li>
        <li><strong>Process:</strong> Load rules, resolve conflicts (Tier 0 wins), inject epic-specific rules</li>
        <li><strong>Output:</strong> Merged governance ruleset</li>
    </ul>
    
    <h3>Step 2: MasterOrchestrator Evaluation</h3>
    <p>Evaluates request against merged ruleset, determines required actions.</p>
    <ul>
        <li><strong>Input:</strong> Request + merged governance</li>
        <li><strong>Process:</strong> Match intent pattern, check prerequisites, validate AC-IDs</li>
        <li><strong>Output:</strong> required_actions list</li>
    </ul>
    
    <h3>Step 3: TodoManager Task Creation</h3>
    <p>Converts required_actions into trackable, dependency-ordered tasks.</p>
    <ul>
        <li><strong>Input:</strong> required_actions from MasterOrchestrator</li>
        <li><strong>Process:</strong> Create task objects, resolve dependencies, assign priorities</li>
        <li><strong>Output:</strong> Ordered task queue</li>
    </ul>
    
    <h3>Step 4: Execution</h3>
    <p>MasterOrchestrator executes tasks in dependency order, logs to audit.</p>
    <ul>
        <li><strong>Input:</strong> Ordered task queue</li>
        <li><strong>Process:</strong> Execute, monitor, handle failures, update state</li>
        <li><strong>Output:</strong> Execution results + evidence bundles</li>
    </ul>
</div>

<div class="glass-card">
    <h2>🎯 Routing Patterns</h2>
    
    <h3>1. Pattern-Based Routing</h3>
    <p>Predefined patterns match requests to orchestrators:</p>
    <pre><code>Pattern: "plan", "create a plan"
→ Planning v5 Orchestrator (AC-PLAN-*)

Pattern: "implement", "build", "create", "fix"
→ TDD-Master v1 (AC-TDD-*)

Pattern: "ado", "azure devops"
→ ADO v2 Orchestrator (AC-ADO-*)</code></pre>
    
    <h3>2. LLM Intent Classification</h3>
    <p>When no pattern matches, LLM classifies intent:</p>
    <ul>
        <li><strong>Input:</strong> Ambiguous request</li>
        <li><strong>Process:</strong> Semantic analysis, capability matching</li>
        <li><strong>Output:</strong> Best-fit orchestrator + confidence score</li>
    </ul>
    
    <h3>3. Capability-Based Selection</h3>
    <p>Orchestrators declare capabilities; MasterOrchestrator matches:</p>
    <pre><code>Request: "Analyze code for security vulnerabilities"
Capabilities Matched:
- Crawler Orchestrator (code analysis)
- Security Scanner (vulnerability detection)
Selected: Security Scanner (higher specificity)</code></pre>
</div>

<div class="glass-card">
    <h2>⚙️ Autonomous vs Interactive Modes</h2>
    
    <h3>🛡️ Autonomous Mode (Default)</h3>
    <p>Orchestrator executes end-to-end without user intervention:</p>
    <ul>
        <li><strong>When:</strong> Request fully specified, no ambiguity</li>
        <li><strong>Behavior:</strong> Execute all phases, persist state, create evidence</li>
        <li><strong>Example:</strong> "Implement user authentication" → TDD-Master runs RED→GREEN→REFACTOR</li>
    </ul>
    
    <div class="highlight-box">
        <strong>Governance Enforcement:</strong> CORE-001 requires autonomous execution in small increments (&lt;500 lines per phase).
    </div>
    
    <h3>💬 Interactive Mode</h3>
    <p>Orchestrator pauses for user input:</p>
    <ul>
        <li><strong>When:</strong> Ambiguous request, multiple valid options, approval required</li>
        <li><strong>Behavior:</strong> Present options, wait for user choice, resume execution</li>
        <li><strong>Example:</strong> "Refactor this module" → Present refactoring strategies, user selects</li>
    </ul>
    
    <div class="warning-box">
        <strong>Warning:</strong> Interactive mode should be rare. Most operations should execute autonomously.
    </div>
</div>

<div class="glass-card">
    <h2>📋 Orchestrator Lifecycle</h2>
    
    <h3>Phase -2: Setup Verification (CORE-006)</h3>
    <pre><code>1. Check dependencies (AC-IDs, files, environment)
2. Detect false positives (file exists but not functional)
3. Validate governance compliance
4. Load context (tracking, AC-INDEX, plan state)
→ PASS: Proceed to Phase -1
→ FAIL: Block execution, remediate dependencies</code></pre>
    
    <h3>Phase -1: Context Loading</h3>
    <pre><code>1. Load progress-tracker.json (current state)
2. Load holistic-snowball-plan.yaml (plan state)
3. Load AC-INDEX.yaml (acceptance criteria)
4. Load governance rules (4-tier merge)
→ Context complete: Proceed to Phase 0</code></pre>
    
    <h3>Phase 0 to N: Execution</h3>
    <pre><code>FOR each task in task_queue:
    1. Log start (audit, state)
    2. Execute task logic
    3. Validate output (tests, governance)
    4. Create evidence bundle
    5. Log completion
    → Next task</code></pre>
    
    <h3>Phase N+1: Teardown + REFACTOR (CORE-007)</h3>
    <pre><code>1. Run whole-file REFACTOR (remove unused imports, clean code)
2. Validate refactored code (tests still pass)
3. Git commit (follow /cortex-git-commit pattern)
4. Update plan state (phase complete, AC-IDs validated)
5. Archive artifacts
→ Orchestrator complete</code></pre>
</div>

<div class="glass-card">
    <h2>🔗 Cross-Orchestrator Communication</h2>
    
    <h3>Event Bus Pattern</h3>
    <p>Orchestrators communicate via event publishing:</p>
    <pre><code>TDD-Master completes AC-TDD-001
→ Publishes: OrchestrationCompleteEvent
→ Evidence System subscribes, creates bundle
→ MasterOrchestrator updates tracking</code></pre>
    
    <h3>Shared State via State Manager</h3>
    <p>All orchestrators read/write through centralized State Manager:</p>
    <ul>
        <li><strong>Atomic Updates:</strong> File locking prevents race conditions</li>
        <li><strong>State Recovery:</strong> Hourly backups, automatic rollback on corruption</li>
        <li><strong>Audit Trail:</strong> Every state change logged</li>
    </ul>
</div>

<div class="glass-card">
    <h2>📊 Example: Implementing a Feature</h2>
    
    <h3>Request: "Implement user authentication with OAuth2"</h3>
    
    <pre><code><strong>Step 1: Governance Merge</strong>
- Load SKULL rules (CORE-001 to CORE-023)
- Load active epic rules (CORTEX-6.0-Foundation)
- Merge → Enforce TDD (CORE-008), incremental execution (CORE-001)

<strong>Step 2: MasterOrchestrator Routes</strong>
- Intent: "implement" → TDD-Master v1
- AC-ID: AC-TDD-015 (User Authentication)
- Dependencies: AC-AUDIT-001, AC-GOV-001, AC-STATE-001

<strong>Step 3: TodoManager Creates Tasks</strong>
1. Write failing test: test_oauth2_flow()
2. Implement OAuth2Provider class
3. Implement token validation
4. Integration test with mock OAuth server
5. REFACTOR: Extract helper functions
6. Create evidence bundle

<strong>Step 4: TDD-Master Executes</strong>
Phase -2: Verify foundation AC-IDs complete
Phase -1: Load context (plan, AC-INDEX)
Phase 0: Write test (RED)
Phase 1: Implement OAuth2Provider (GREEN)
Phase 2: Refactor (REFACTOR)
Phase 3: Integration tests
Phase N+1: Teardown, git commit, evidence bundle

<strong>Result:</strong>
- AC-TDD-015 completed
- Evidence bundle created
- Tests passing (100% coverage)
- Audit trail complete
- Plan updated</code></pre>
</div>
"""
    },
    
    "brain-architecture.html": {
        "title": "Brain Architecture",
        "breadcrumb": "Brain Architecture",
        "content": """
<h1>Brain Architecture</h1>
<p class="subtitle">CORTEX vs Business Knowledge Separation</p>

<div class="glass-card">
    <h2>🧠 Knowledge Hierarchy</h2>
    <p>CORTEX 6.0 organizes knowledge into <strong>4 tiers</strong> with strict separation between CORTEX core knowledge and business-specific knowledge.</p>
    
    <div class="highlight-box">
        <strong>Principle:</strong> CORTEX core knowledge (how to orchestrate, govern, audit) is separate from business knowledge (what to build, for whom, why).
    </div>
</div>

<div class="glass-card">
    <h2>📂 Tier 0: CORTEX Core (Immutable)</h2>
    <p><strong>Location:</strong> <code>cortex-brain/tier0/</code></p>
    <p><strong>Category:</strong> CORTEX_CORE</p>
    <p><strong>Precedence:</strong> HIGHEST</p>
    
    <h3>Contents:</h3>
    <ul>
        <li><strong>Governance Rules:</strong> 23 SKULL rules (core-rules.yaml)</li>
        <li><strong>Orchestration Patterns:</strong> How orchestrators execute</li>
        <li><strong>Audit Schema:</strong> Log structure, retention policies</li>
        <li><strong>Evidence Templates:</strong> Bundle structure, validation</li>
        <li><strong>State Schema:</strong> progress-tracker.json structure</li>
    </ul>
    
    <div class="warning-box">
        <strong>Immutability:</strong> Tier 0 rules cannot be overridden. They protect CORTEX operational integrity.
    </div>
    
    <h3>Example: CORE-001 (Incremental Execution)</h3>
    <pre><code>rule_id: CORE-001
name: Incremental Autonomous Execution
severity: blocked
validation:
  - Operations split into &lt;500 line increments
  - State persisted between increments
  - Token usage capped at 80%
enforcement:
  trigger: orchestrator_execution_start
  action: block_if_operation_too_large</code></pre>
</div>

<div class="glass-card">
    <h2>📋 Tier 1: Business Context (Dynamic)</h2>
    <p><strong>Location:</strong> <code>cortex-brain/tier1/</code></p>
    <p><strong>Category:</strong> BUSINESS_TIER_0</p>
    <p><strong>Precedence:</strong> HIGH</p>
    
    <h3>Contents:</h3>
    <ul>
        <li><strong>Active Epic:</strong> Current project requirements (active-epic.yaml)</li>
        <li><strong>Acceptance Criteria:</strong> AC-INDEX.yaml (what "done" means)</li>
        <li><strong>Progress Tracking:</strong> progress-tracker.json (runtime state)</li>
        <li><strong>Evidence Bundles:</strong> Proof of AC-ID completion</li>
        <li><strong>Epic-Specific Rules:</strong> Temporary governance (e.g., "Use Python 3.11 for ML")</li>
    </ul>
    
    <div class="highlight-box">
        <strong>Dynamic Nature:</strong> Tier 1 content changes per epic. When epic completes, content archives.
    </div>
    
    <h3>Example: Active Epic Entry</h3>
    <pre><code>epic_id: "CORTEX-6.0-Foundation"
phase: "Phase 1"
ac_ids: ["AC-AUDIT-001", "AC-GOV-001", "AC-STATE-001"]
status: "in_progress"
requirements:
  - "Audit latency &lt;5ms p99"
  - "4-tier governance enforced"
  - "SQLite WAL for state persistence"
dynamic_rules:
  - rule_id: "EPIC-001"
    name: "Phase 1 Complete Before Phase 2"
    enforcement: "block_phase_2_until_phase_1_complete"</code></pre>
</div>

<div class="glass-card">
    <h2>🏢 Tier 2: Company Practices (Organizational)</h2>
    <p><strong>Location:</strong> <code>cortex-brain/tier2/</code></p>
    <p><strong>Category:</strong> COMPANY_PRACTICES</p>
    <p><strong>Precedence:</strong> MEDIUM</p>
    
    <h3>Contents:</h3>
    <ul>
        <li><strong>Engineering Standards:</strong> Code style, naming conventions</li>
        <li><strong>Quality Gates:</strong> Test coverage thresholds, performance targets</li>
        <li><strong>Security Policies:</strong> Data encryption, access control</li>
        <li><strong>Deployment Practices:</strong> CI/CD pipelines, approval gates</li>
        <li><strong>Documentation Standards:</strong> README templates, API docs</li>
    </ul>
    
    <h3>Example: Engineering Standard</h3>
    <pre><code>standard_id: "ENG-STD-001"
name: "Test Coverage Requirement"
requirement: "&gt;= 90% for critical components, &gt;= 80% for standard"
enforcement: "block_pr_merge_if_below_threshold"
exceptions:
  - "UI components (visual testing instead)"
  - "Legacy code (gradual improvement plan required)"</code></pre>
</div>

<div class="glass-card">
    <h2>🎓 Tier 3: Knowledge Practices (Learned)</h2>
    <p><strong>Location:</strong> <code>cortex-brain/tier3/</code></p>
    <p><strong>Category:</strong> KNOWLEDGE_PRACTICES</p>
    <p><strong>Precedence:</strong> LOW</p>
    
    <h3>Contents:</h3>
    <ul>
        <li><strong>Learned Patterns:</strong> Successful implementations, optimizations</li>
        <li><strong>Performance Insights:</strong> "Use async I/O for file operations"</li>
        <li><strong>Common Pitfalls:</strong> "SQLite locks on Windows require retry logic"</li>
        <li><strong>Tool Recommendations:</strong> "Prefer Black over autopep8"</li>
        <li><strong>Integration Tips:</strong> "ADO API rate limits: 200 req/min"</li>
    </ul>
    
    <div class="highlight-box">
        <strong>Machine Learning:</strong> Tier 3 grows over time as CORTEX learns from execution patterns.
    </div>
    
    <h3>Example: Learned Pattern</h3>
    <pre><code>pattern_id: "LEARN-001"
name: "SQLite Retry Pattern"
description: "Windows file locking requires retry with exponential backoff"
code_example: |
  for attempt in range(3):
      try:
          db.write(data)
          break
      except sqlite3.OperationalError as e:
          if "locked" in str(e):
              time.sleep(2 ** attempt)
          else:
              raise
learned_from: "AC-STATE-002 implementation (Jan 2026)"
success_rate: 99.2%
recommendation: "Use for all SQLite writes"</code></pre>
</div>

<div class="glass-card">
    <h2>🔀 CORTEX vs Business Separation</h2>
    
    <h3>CORTEX Core Knowledge (How)</h3>
    <p><strong>Tiers:</strong> 0, 2 (partially)</p>
    <p><strong>Content Type:</strong></p>
    <ul>
        <li>How to orchestrate (MasterOrchestrator, TodoManager)</li>
        <li>How to enforce governance (GovernanceMerger, enforcement hooks)</li>
        <li>How to audit (EnhancedAuditLogger, hash chains)</li>
        <li>How to persist state (State Manager, atomic updates)</li>
        <li>How to validate (Evidence Bundle System)</li>
    </ul>
    
    <div class="highlight-box">
        <strong>Characteristic:</strong> Generic, reusable across any project. Not specific to CORTEX 6.0 implementation.
    </div>
    
    <h3>Business Knowledge (What, Why)</h3>
    <p><strong>Tiers:</strong> 1, 3</p>
    <p><strong>Content Type:</strong></p>
    <ul>
        <li>What to build (CORTEX 6.0 features: audit, governance, state)</li>
        <li>Why build it (production-grade AI orchestration needs)</li>
        <li>When to build (Phase 1 foundation before Phase 2 orchestration)</li>
        <li>Acceptance criteria (what defines "done" for each AC-ID)</li>
        <li>Project-specific constraints (Python 3.11+, SQLite, etc.)</li>
    </ul>
    
    <div class="highlight-box">
        <strong>Characteristic:</strong> Specific to current epic/project. Changes when epic changes.
    </div>
</div>

<div class="glass-card">
    <h2>🗂️ Memory Systems</h2>
    
    <h3>Working Memory (Tier 1)</h3>
    <p><strong>Duration:</strong> Current epic only</p>
    <p><strong>Storage:</strong> <code>cortex-brain/tier1/tracking/progress-tracker.json</code></p>
    <p><strong>Content:</strong></p>
    <ul>
        <li>Active epic context</li>
        <li>Current phase, current todo</li>
        <li>Completed AC-IDs</li>
        <li>Blockers, dependencies</li>
    </ul>
    <p><strong>Analogy:</strong> Human short-term memory (focused on current task)</p>
    
    <h3>Long-Term Memory (Tier 0, 2, 3)</h3>
    <p><strong>Duration:</strong> Permanent (Tier 0) or evolving (Tier 2, 3)</p>
    <p><strong>Storage:</strong> YAML files in respective tier folders</p>
    <p><strong>Content:</strong></p>
    <ul>
        <li>Core rules (Tier 0): Never change</li>
        <li>Company standards (Tier 2): Update quarterly</li>
        <li>Learned patterns (Tier 3): Continuous learning</li>
    </ul>
    <p><strong>Analogy:</strong> Human long-term memory (accumulated knowledge)</p>
    
    <h3>Episodic Memory (Evidence Bundles)</h3>
    <p><strong>Duration:</strong> Per AC-ID, archived after epic</p>
    <p><strong>Storage:</strong> <code>cortex-brain/tier1/evidence-bundles/{AC-ID}/</code></p>
    <p><strong>Content:</strong></p>
    <ul>
        <li>What was done (manifest.yaml)</li>
        <li>How it was validated (test_results.json)</li>
        <li>When it happened (audit_trace.jsonl)</li>
        <li>Performance achieved (performance_metrics.json)</li>
    </ul>
    <p><strong>Analogy:</strong> Human episodic memory (specific events, experiences)</p>
</div>

<div class="glass-card">
    <h2>🔄 Knowledge Flow</h2>
    
    <h3>Governance Enforcement Flow</h3>
    <pre><code>Request
→ GovernanceMerger loads Tier 0, 1, 2, 3
→ Merges with precedence (0 > 1 > 2 > 3)
→ Resolves conflicts (Tier 0 always wins)
→ Produces merged_ruleset
→ MasterOrchestrator enforces merged_ruleset
→ Logs enforcement to audit (Tier 1)</code></pre>
    
    <h3>Learning Flow (Tier 3 Growth)</h3>
    <pre><code>Orchestrator completes AC-ID
→ Evidence bundle created (Tier 1)
→ Performance metrics analyzed
→ Pattern extraction:
   - High success rate? → Add to Tier 3 as recommendation
   - Performance improvement? → Add to Tier 3 as insight
   - Common failure? → Add to Tier 3 as pitfall
→ Tier 3 updated (machine learning loop)</code></pre>
</div>

<div class="glass-card">
    <h2>📊 Tier Statistics</h2>
    
    <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
            <tr style="background: rgba(0, 212, 255, 0.2); border-bottom: 2px solid var(--primary);">
                <th style="padding: 15px; text-align: left;">Tier</th>
                <th style="padding: 15px; text-align: left;">File Count</th>
                <th style="padding: 15px; text-align: left;">Update Frequency</th>
                <th style="padding: 15px; text-align: left;">Storage Size</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 12px;">Tier 0 (Core)</td>
                <td style="padding: 12px;">~10 files</td>
                <td style="padding: 12px;">Never (immutable)</td>
                <td style="padding: 12px;">~50 KB</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 12px;">Tier 1 (Business)</td>
                <td style="padding: 12px;">~200 files/epic</td>
                <td style="padding: 12px;">Every execution</td>
                <td style="padding: 12px;">~5 MB/epic</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 12px;">Tier 2 (Company)</td>
                <td style="padding: 12px;">~30 files</td>
                <td style="padding: 12px;">Quarterly</td>
                <td style="padding: 12px;">~200 KB</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--glass-border);">
                <td style="padding: 12px;">Tier 3 (Learned)</td>
                <td style="padding: 12px;">~100 files</td>
                <td style="padding: 12px;">Continuous (ML)</td>
                <td style="padding: 12px;">~1 MB</td>
            </tr>
        </tbody>
    </table>
</div>
"""
    }
}

# Create output directory
output_dir = Path("d:/PROJECTS/CORTEX/docs/architecture")
output_dir.mkdir(parents=True, exist_ok=True)

# Generate files
for filename, doc_data in docs.items():
    content = get_html_template(
        title=doc_data["title"],
        breadcrumb_current=doc_data["breadcrumb"],
        content=doc_data["content"]
    )
    
    filepath = output_dir / filename
    filepath.write_text(content, encoding='utf-8')
    print(f"✓ Created: {filepath}")

print(f"\n✅ Generated {len(docs)} architecture documentation files")
