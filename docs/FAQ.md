# CORTEX FAQ (Frequently Asked Questions)

**Last Updated:** November 20, 2025  
**Version:** 3.0  
**Status:** Production Ready

---

## 📖 How to Use This FAQ

- Use **Ctrl+F** (Windows/Linux) or **Cmd+F** (Mac) to search for keywords
- Questions are organized by category - scroll to relevant section
- Each answer includes links to detailed documentation
- Can't find your answer? [Open a GitHub Issue](https://github.com/asifhussain60/CORTEX/issues)

---

## 🏗️ Architecture & Design

This section provides information about 🏗️ architecture & design. See related documentation in the navigation menu for detailed guides.


### Q: What is the tier system and why 4 tiers?

**A:** CORTEX uses a 4-tier hierarchical architecture inspired by human memory systems:

- **Tier 0 (Entry Point):** Validates and routes all incoming requests - like a security checkpoint
- **Tier 1 (Working Memory):** Stores active conversation context - like short-term memory
- **Tier 2 (Knowledge Graph):** Connects related concepts and patterns - like associative memory
- **Tier 3 (Long-term Storage):** Persistent historical data - like long-term memory

**Why 4 tiers?** This separation enables:
- 97% token reduction (only load what's needed)
- Context-aware responses (remember past conversations)
- Knowledge preservation (never lose important insights)
- Performance optimization (fast lookups, minimal overhead)

**Learn more:** **Architecture Overview** (see navigation menu for related documentation)

---

### Q: How does the agent coordination system work?

**A:** CORTEX uses a "split-brain" architecture with 10 specialized agents:

**Left Hemisphere (Execution):**
- **Executor Agent:** Implements code
- **Tester Agent:** Writes and runs tests
- **Validator Agent:** Checks quality

**Right Hemisphere (Strategic):**
- **Architect Agent:** Designs systems
- **Work Planner Agent:** Plans features
- **Documenter Agent:** Creates documentation
- **Pattern Matcher Agent:** Identifies code patterns
- **Intent Detector Agent:** Classifies user requests
- **Health Validator Agent:** Monitors system health
- **Optimizer Agent:** Improves performance

**Corpus Callosum (Router):** Routes requests to appropriate agents based on intent.

**Example workflow:** "Add authentication" → Work Planner (plan) → Architect (design) → Executor (implement) → Tester (verify) → Validator (quality check)

**Learn more:** **Agent System Guide** (see navigation menu for related documentation)

---

### Q: What is the Brain Protection layer?

**A:** Brain Protection is CORTEX's governance system that prevents self-harm through SKULL rules (Seven Key Universal Logic Locks):

1. **No self-deletion of brain files** - Can't delete tier databases or protection rules
2. **No recursive operations** - Prevents infinite loops that corrupt memory
3. **No breaking changes without validation** - All schema changes must pass validation
4. **No bypassing safety checks** - Entry point validation is mandatory
5. **No unconstrained loops** - All operations have timeout limits
6. **No direct database manipulation** - Must use tier APIs
7. **No configuration override** - Critical settings are immutable

These rules ensure CORTEX can improve itself without accidentally destroying its own memory or capabilities.

**Learn more:** **Brain Protection Rules** (see navigation menu for related documentation)

---

### Q: How does CORTEX maintain context across conversations?

**A:** CORTEX uses a multi-tier memory system with automatic context injection:

1. **Conversation Capture:** All GitHub Copilot Chat interactions are automatically captured
2. **Markdown Parsing:** Conversations are structured into messages with roles (user/assistant/system)
3. **Tier 1 Storage:** Recent conversations stored in working memory SQLite database
4. **Relevance Scoring:** When you ask a new question, CORTEX searches past conversations and scores them for relevance (0-1 scale)
5. **Context Injection:** Top relevant conversations (score >0.50) are auto-injected into the response
6. **Learning:** Patterns and entities extracted to Tier 2 knowledge graph for long-term learning

**Example:**
```
You (Monday): "Use PostgreSQL for main DB and Redis for caching"
[CORTEX captures this architectural decision]

You (Wednesday): "Implement the caching layer"
[CORTEX auto-injects the PostgreSQL/Redis decision from Monday]
CORTEX: "Based on your PostgreSQL + Redis decision from Monday, here's the caching implementation..."
```

**Learn more:** **Conversation Tracking Guide** (see navigation menu for related documentation)

---

### Q: What's the difference between Tier 1 and Tier 2 storage?

**A:** 

| Feature | Tier 1 (Working Memory) | Tier 2 (Knowledge Graph) |
|---------|------------------------|-------------------------|
| **Purpose** | Active conversation context | Semantic relationships & patterns |
| **Retention** | Recent (last 24-48 hours) | Persistent (permanent) |
| **Content** | Full conversation messages | Extracted entities, patterns, relationships |
| **Query Speed** | Very fast (<50ms) | Fast (<200ms) |
| **Storage** | SQLite (conversations.db) | SQLite (knowledge_graph.db) |
| **Example Data** | "User asked about JWT tokens yesterday" | "JWT tokens → Authentication → Security → Best Practices" |

**Use case:** Tier 1 for "What did I ask about 10 minutes ago?", Tier 2 for "What's the relationship between authentication and security?"

---

### Q: Can I customize the agent system?

**A:** Yes! CORTEX supports custom agent development through the plugin system:

1. **Create Agent Class:** Extend `BaseAgent` from `src/cortex_agents/base_agent.py`
2. **Implement Methods:** `analyze()`, `execute()`, `validate()`
3. **Register Agent:** Add to `cortex-brain/agents/custom-agents.yaml`
4. **Deploy:** Place in `src/cortex_agents/custom/` directory

**Example:**
```python
from src.cortex_agents.base_agent import BaseAgent

class CodeReviewerAgent(BaseAgent):
    def analyze(self, context):
        # Analyze code quality
        pass
    
    def execute(self, plan):
        # Generate code review report
        pass
```

**Learn more:** **Agent Development Guide** (see navigation menu for related documentation)

---

## 🚀 Setup & Installation

This section provides information about 🚀 setup & installation. See related documentation in the navigation menu for detailed guides.


### Q: What are the system requirements for CORTEX?

**A:** 

**Minimum Requirements:**
- **OS:** Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python:** 3.9 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB for CORTEX + dependencies
- **VS Code:** Latest version with GitHub Copilot extension
- **Git:** 2.30 or higher

**Recommended for Best Performance:**
- Python 3.11 (fastest SQLite support)
- 16GB RAM (for large knowledge graphs)
- SSD storage (faster database operations)

**Learn more:** **Installation Guide** (see navigation menu for related documentation)

---

### Q: How do I install CORTEX on Windows/Mac/Linux?

**A:** Installation is identical across all platforms:

**Step 1: Clone Repository**
```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

**Step 2: Run Setup**
```bash
python setup_cortex.py
```

The setup script automatically:
- Detects your OS and configures accordingly
- Installs Python dependencies (PyYAML, SQLite, etc.)
- Creates tier databases (Tier 0-3)
- Initializes brain protection rules
- Validates installation

**Step 3: Verify Installation**
```bash
python -m pytest tests/
```

**Platform-specific notes:**
- **Windows:** Use PowerShell (not CMD)
- **Mac:** May need `python3` instead of `python`
- **Linux:** Ensure `python3-dev` installed

**Learn more:** **Quick Start Guide** (see navigation menu for related documentation)

---

### Q: Do I need admin privileges to install?

**A:** No, CORTEX installs in user space and doesn't require administrator/root privileges.

**Installation locations:**
- **Windows:** `%USERPROFILE%\AppData\Local\CORTEX`
- **Mac/Linux:** `~/.cortex`

**Exception:** If installing Python system-wide packages (not recommended), you might need admin. Use virtual environments instead:

```bash
python -m venv cortex-env
source cortex-env/bin/activate  # Mac/Linux
cortex-env\Scripts\activate     # Windows
python setup_cortex.py
```

---

### Q: How do I configure GitHub Copilot to use CORTEX?

**A:** CORTEX integrates automatically via GitHub Copilot Chat custom instructions:

**Step 1: Create Custom Instruction File**
```bash
# Automatically done by setup script
# Manual: Copy .github/prompts/CORTEX.prompt.md to VS Code settings
```

**Step 2: Enable in VS Code**
1. Open VS Code Settings (Ctrl+,)
2. Search for "GitHub Copilot Chat"
3. Find "Prompt Files" setting
4. Add path to CORTEX.prompt.md

**Step 3: Test Integration**
Open Copilot Chat and type:
```
/CORTEX help
```

You should see CORTEX's formatted response with command table.

**Learn more:** **Configuration Reference** (see navigation menu for related documentation)

---

### Q: What Python version is required?

**A:** 

**Minimum:** Python 3.9  
**Recommended:** Python 3.11 or higher

**Why Python 3.11+?**
- 25% faster SQLite operations
- Improved type hinting support
- Better error messages for debugging
- Native TOML support (future feature)

**Check your version:**
```bash
python --version
```

**Upgrade if needed:**
- **Windows:** Download from python.org
- **Mac:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11`

**Learn more:** **Setup Guide** (see navigation menu for related documentation)

---

### Q: Can I use CORTEX without GitHub Copilot?

**A:** Partially. CORTEX is designed to enhance GitHub Copilot, but some features work standalone:

**Works without Copilot:**
- Documentation generation (`python scripts/generate_docs.py`)
- Conversation import (manual file import)
- Knowledge graph queries (CLI tools)
- Brain health monitoring

**Requires Copilot:**
- Interactive planning workflows
- Conversation capture (ambient mode)
- Context injection in responses
- Agent coordination (routed through Copilot Chat)

**Alternative:** Use CORTEX CLI mode for standalone operations.

---

## 💡 Usage & Operations

This section provides information about 💡 usage & operations. See related documentation in the navigation menu for detailed guides.


### Q: How do I generate documentation?

**A:** Use natural language in GitHub Copilot Chat:

**Simple command:**
```
Generate documentation
```

**With options:**
```
Generate documentation --profile comprehensive
Generate documentation --dry-run
Generate documentation --component diagrams
```

**What gets generated:**
- 14+ Mermaid diagrams
- 14+ DALL-E prompts (enhanced)
- Architecture narratives
- "The Awakening of CORTEX" story
- Executive summary
- Complete MkDocs site
- FAQ section

**Output location:** `docs/` folder

**Preview generated docs:**
```bash
cd docs
mkdocs serve
# Visit http://localhost:8000
```

**Learn more:** **Documentation Operations** (see navigation menu for related documentation)

---

### Q: How do I plan a new feature?

**A:** CORTEX provides interactive feature planning:

**Basic command:**
```
plan authentication feature
```

**CORTEX will:**
1. **Ask clarifying questions** (What type of auth? JWT? OAuth? Session-based?)
2. **Generate planning template** (DoR, DoD, acceptance criteria)
3. **Create planning file** (cortex-brain/documents/planning/features/PLAN-[date]-authentication.md)
4. **Open in VS Code** for review and editing
5. **Wait for approval** ("approve plan")
6. **Hook into pipeline** (auto-inject into development context)

**With screenshot (Vision API):**
```
plan login feature
[Attach UI mockup screenshot]
```

CORTEX extracts UI elements (buttons, inputs, labels) and auto-generates acceptance criteria.

**Learn more:** **Feature Planning Guide** (see navigation menu for related documentation)

---

### Q: How does conversation tracking work?

**A:** CORTEX captures GitHub Copilot Chat conversations automatically:

**Ambient Mode (Automatic):**
1. **Background Daemon:** Monitors VS Code chat sessions
2. **Markdown Export:** Conversations saved to `.md` files
3. **Auto-Import:** New conversations imported to Tier 1 every 5 minutes
4. **Context Injection:** Relevant past conversations added to future responses

**Manual Mode (Explicit):**
```
capture conversation #file:conversation.md
```

**What's captured:**
- User messages (your questions/requests)
- Assistant messages (Copilot responses)
- System messages (CORTEX metadata)
- Timestamps and session IDs
- File references and code snippets

**Privacy:** All data stored locally (no cloud sync). You control what's captured.

**Learn more:** **Tracking Guide** (see navigation menu for related documentation)

---

### Q: Can I use CORTEX with existing projects?

**A:** Yes! CORTEX is workspace-agnostic:

**Option 1: Install Globally (Recommended)**
```bash
# Install CORTEX once
cd ~/CORTEX
python setup_cortex.py

# Use in any VS Code workspace
# CORTEX detects workspace root automatically
```

**Option 2: Per-Project Installation**
```bash
cd your-project/
git clone https://github.com/asifhussain60/CORTEX.git .cortex
cd .cortex
python setup_cortex.py
```

**Integration Steps:**
1. Open your project in VS Code
2. GitHub Copilot Chat automatically has CORTEX available
3. Use CORTEX commands: `/CORTEX help`, `plan feature`, etc.
4. CORTEX learns your project structure automatically

**Migration:** CORTEX won't interfere with your project files (stores data in `cortex-brain/` folder)

---

### Q: How do I capture and import conversations?

**A:** 

**Method 1: Automatic Capture (Ambient)**
Already enabled after setup. Conversations auto-imported every 5 minutes.

**Method 2: Manual Capture from File**
```bash
# Save Copilot Chat to .md file first (use VS Code export)
# Then in Copilot Chat:
capture conversation #file:path/to/conversation.md
```

**Method 3: Bulk Import**
```bash
python scripts/import_conversations.py --dir conversations/ --recursive
```

**What happens after import:**
1. **Parsing:** Markdown structured into messages
2. **Entity Extraction:** Classes, functions, files identified
3. **Tier 1 Storage:** Conversation saved to working memory
4. **Tier 2 Learning:** Patterns extracted to knowledge graph
5. **Context Injection:** Available for future responses

**Verification:**
```
show context
```

Lists all captured conversations with relevance scores.

**Learn more:** **Conversation Import Guide** (see navigation menu for related documentation)

---

### Q: What commands does CORTEX support?

**A:** CORTEX uses natural language - no rigid syntax required. Common patterns:

**Help & Status:**
- `help` or `/CORTEX help`
- `status`
- `show capabilities`

**Documentation:**
- `generate documentation`
- `generate docs --dry-run`
- `refresh docs`

**Planning:**
- `plan [feature name]`
- `plan ado feature`
- `resume plan [name]`
- `approve plan`

**Conversation Management:**
- `capture conversation #file:[path]`
- `show context`
- `forget [topic]`
- `clear memory`

**Operations:**
- `setup environment`
- `validate brain`
- `health check`
- `optimize performance`

**Learn more:** **Operations Reference** (see navigation menu for related documentation)

---

## 🔧 Troubleshooting

This section provides information about 🔧 troubleshooting. See related documentation in the navigation menu for detailed guides.


### Q: CORTEX doesn't respond - what's wrong?

**A:** Common causes and solutions:

**1. GitHub Copilot Chat not detecting CORTEX:**
```bash
# Check if prompt file is loaded
# VS Code Settings → GitHub Copilot Chat → Prompt Files
# Should include: .github/prompts/CORTEX.prompt.md
```

**2. Python environment issues:**
```bash
# Verify Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt
```

**3. Brain database corruption:**
```bash
# Validate brain health
python scripts/validate_brain.py

# Reset if corrupted (WARNING: loses history)
python scripts/reset_brain.py --tier all
```

**4. VS Code extension conflict:**
- Disable other AI assistant extensions temporarily
- Restart VS Code
- Test with: `help`

**Still not working?** Enable debug logging:
```python
# In cortex.config.json
{
  "logging": {
    "level": "DEBUG",
    "file": "cortex-brain/logs/debug.log"
  }
}
```

**Learn more:** **Troubleshooting Guide** (see navigation menu for related documentation)

---

### Q: Documentation generation fails - how to fix?

**A:** 

**Error: "MkDocs build failed"**
```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material pymdown-extensions

# Rebuild
mkdocs build --clean
```

**Error: "YAML parsing error"**
```bash
# Validate YAML files
python -m yaml cortex-brain/capabilities.yaml
python -m yaml cortex-operations.yaml

# Fix syntax errors reported
```

**Error: "Image not found"**
```bash
# Check image paths in markdown
# Relative paths should be: ../images/diagrams/[category]/[name].png

# Verify image files exist
ls docs/images/diagrams/
```

**Error: "Module not found"**
```bash
# Ensure you're in CORTEX root directory
cd ~/CORTEX  # or wherever CORTEX is installed

# Run from correct location
python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py
```

**Learn more:** [Documentation Operations](operations/workflows.md#troubleshooting)

---

### Q: Python dependencies won't install - solutions?

**A:** 

**Error: "Permission denied"**
```bash
# Don't use sudo! Use virtual environment instead
python -m venv cortex-env
source cortex-env/bin/activate
pip install -r requirements.txt
```

**Error: "Package version conflict"**
```bash
# Create fresh virtual environment
rm -rf cortex-env
python -m venv cortex-env
source cortex-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Error: "SSL certificate verify failed"**
```bash
# Temporary workaround (corporate proxy)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Permanent fix: Update certificates
pip install --upgrade certifi
```

**Error: "Wheel build failed"**
```bash
# Install build tools
# Windows: Install Visual Studio Build Tools
# Mac: xcode-select --install
# Linux: sudo apt install python3-dev build-essential
```

**Learn more:** **Installation Troubleshooting** (see navigation menu for related documentation)

---

### Q: MkDocs build errors - common causes?

**A:** 

**1. Missing theme:**
```bash
pip install mkdocs-material
```

**2. Invalid navigation structure:**
```yaml
# In mkdocs.yml - check for:
# - Mismatched indentation (use 2 spaces, not tabs)
# - Missing file references
# - Duplicate nav entries
```

**3. Broken links:**
```bash
# Run link checker
mkdocs build --strict
# Reports all broken links
```

**4. Plugin errors:**
```bash
# Install missing plugins
pip install pymdown-extensions mkdocs-mermaid2-plugin

# Or disable plugins temporarily:
# In mkdocs.yml, comment out plugins section
```

**5. Encoding issues:**
```bash
# Ensure all .md files are UTF-8 encoded
# Convert if needed:
iconv -f ISO-8859-1 -t UTF-8 file.md > file_utf8.md
```

**Learn more:** **MkDocs Configuration** (see navigation menu for related documentation)

---

### Q: How do I reset CORTEX brain database?

**A:** 

**⚠️ WARNING:** Resetting loses all conversation history and learned patterns. Backup first!

**Full Reset (All Tiers):**
```bash
# Backup first
python scripts/backup_brain.py --output backups/

# Reset all tiers
python scripts/reset_brain.py --tier all --confirm

# Reinitialize
python setup_cortex.py --init-only
```

**Partial Reset (Specific Tier):**
```bash
# Reset only Tier 1 (working memory)
python scripts/reset_brain.py --tier 1

# Reset only Tier 2 (knowledge graph)
python scripts/reset_brain.py --tier 2
```

**Soft Reset (Clear Data, Keep Schema):**
```bash
python scripts/reset_brain.py --soft --tier all
```

**Restore from Backup:**
```bash
python scripts/restore_brain.py --backup backups/cortex-brain-2025-11-20.zip
```

**Learn more:** **Brain Management** (see navigation menu for related documentation)

---

### Q: CORTEX responses are slow - how to optimize?

**A:** 

**1. Optimize Tier 1 Database:**
```bash
# Vacuum and analyze
python scripts/optimize_brain.py --tier 1

# Archive old conversations (>30 days)
python scripts/archive_conversations.py --age 30
```

**2. Reduce Context Injection:**
```python
# In cortex.config.json
{
  "context": {
    "max_conversations": 3,  # Default: 5
    "relevance_threshold": 0.70  # Default: 0.50
  }
}
```

**3. Enable Caching:**
```python
# In cortex.config.json
{
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600
  }
}
```

**4. Upgrade Hardware:**
- Use SSD (not HDD) for databases
- Increase RAM to 16GB+
- Upgrade to Python 3.11 (25% faster SQLite)

**Benchmark:**
```bash
python scripts/benchmark.py
# Should show <500ms for context injection
```

**Learn more:** **Performance Optimization** (see navigation menu for related documentation)

---

## 🔬 Advanced Topics

This section provides information about 🔬 advanced topics. See related documentation in the navigation menu for detailed guides.


### Q: How do I extend CORTEX with custom plugins?

**A:** 

**Step 1: Create Plugin Class**
```python
# src/plugins/my_custom_plugin.py
from src.plugins.base_plugin import BasePlugin

class MyCustomPlugin(BasePlugin):
    def get_name(self):
        return "my_custom_plugin"
    
    def get_commands(self):
        return ["custom command", "run custom"]
    
    def execute(self, context):
        # Your plugin logic here
        return {"status": "success", "data": "Custom result"}
```

**Step 2: Register Plugin**
```yaml
# cortex-brain/plugins/custom-plugins.yaml
plugins:
  - name: my_custom_plugin
    module: src.plugins.my_custom_plugin
    class: MyCustomPlugin
    enabled: true
```

**Step 3: Test Plugin**
```
custom command
```

**Plugin Examples:**
- Database crawler (SQLite/PostgreSQL/MongoDB)
- Platform switcher (Windows ↔ Mac ↔ Linux)
- Report generator (PDF/HTML/JSON)
- Code analyzer (complexity metrics)

**Learn more:** **Plugin Development** (see navigation menu for related documentation)

---

### Q: Can I modify the tier system architecture?

**A:** Yes, but with caution. Tier system is core to CORTEX's memory model.

**Safe modifications:**
- Add custom tables to existing tiers
- Extend tier APIs with new methods
- Add indexes for performance
- Modify retention policies

**Unsafe modifications:**
- Changing tier count (4 is optimal)
- Removing core tables (schema dependencies)
- Bypassing tier APIs (breaks encapsulation)
- Modifying without schema migrations

**Example: Add custom table to Tier 2**
```python
# Create migration script
# scripts/migrations/add_custom_table.py

def upgrade():
    conn = sqlite3.connect('cortex-brain/tier2/knowledge_graph.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS custom_patterns (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            pattern_data JSON,
            confidence REAL
        )
    ''')
    conn.commit()
```

**Learn more:** **Architecture Customization** (see navigation menu for related documentation)

---

### Q: How do I backup and restore CORTEX brain?

**A:** 

**Automatic Backups (Recommended):**
```python
# In cortex.config.json
{
  "backup": {
    "enabled": true,
    "schedule": "daily",
    "retention_days": 30,
    "location": "backups/"
  }
}
```

**Manual Backup:**
```bash
# Full backup (all tiers)
python scripts/backup_brain.py --output backups/manual-backup.zip

# Specific tier
python scripts/backup_brain.py --tier 2 --output backups/tier2-backup.zip

# Include conversation files
python scripts/backup_brain.py --include-conversations
```

**Restore:**
```bash
# Full restore
python scripts/restore_brain.py --backup backups/cortex-brain-2025-11-20.zip

# Dry run (preview)
python scripts/restore_brain.py --backup backups/cortex-brain-2025-11-20.zip --dry-run

# Selective restore (Tier 2 only)
python scripts/restore_brain.py --backup backups/tier2-backup.zip --tier 2
```

**Cloud Sync (Optional):**
```bash
# Sync to OneDrive/Dropbox/Google Drive
python scripts/sync_brain.py --provider onedrive --remote-path CORTEX-Backup/
```

**Learn more:** **Backup & Recovery** (see navigation menu for related documentation)

---

### Q: How does the optimization system work (97% token reduction)?

**A:** CORTEX achieves 97.2% token reduction through modular architecture:

**Before (Monolithic):**
- Single 8,701-line prompt file
- 74,047 input tokens per request
- All documentation loaded every time

**After (Modular):**
- Core entry point: 400 lines (2,078 tokens)
- Modules loaded on-demand: story.md, setup-guide.md, technical-reference.md
- Response templates (YAML) loaded without Python execution
- Documentation split into 15+ focused files

**Optimization Principles:**

1. **Lazy Loading:** Load only what's needed for current request
2. **Response Templates:** Pre-formatted responses (no computation)
3. **YAML Over Code:** Static data in YAML (not Python docstrings)
4. **Intent Detection:** Route to specific module early
5. **Caching:** Reuse previous responses when appropriate

**Breakdown:**
- Entry point: 2,078 tokens (always loaded)
- Module average: 2,500 tokens (loaded if needed)
- Template average: 300 tokens (YAML only)

**Example Request:**
```
User: "help"
Tokens used: 2,078 (entry) + 300 (template) = 2,378 total
Vs. old monolithic: 74,047 tokens
Reduction: 96.8%
```

**Learn more:** **Optimization Principles** (see navigation menu for related documentation)

---

### Q: Can I deploy CORTEX in a team environment?

**A:** Yes! CORTEX supports team deployment with shared knowledge:

**Option 1: Shared Brain (Read-Only)**
```yaml
# cortex.config.json (each team member)
{
  "brain": {
    "shared_path": "//network-share/cortex-brain/",
    "mode": "read-only",
    "local_overrides": true
  }
}
```

**Option 2: Centralized Server (API)**
```bash
# On server
python scripts/serve_brain_api.py --port 8080

# On client
# cortex.config.json
{
  "brain": {
    "api_endpoint": "http://cortex-server:8080",
    "cache_locally": true
  }
}
```

**Option 3: Git-Based Sync**
```bash
# Commit brain updates
cd cortex-brain/
git add tier2/knowledge_graph.db
git commit -m "Update: New patterns learned"
git push

# Team members pull updates
git pull
```

**Privacy Considerations:**
- Tier 1 (working memory) stays local (recent conversations)
- Tier 2 (knowledge graph) can be shared (patterns, no raw conversations)
- Tier 3 (long-term storage) optional (historical archive)

**Learn more:** **Team Deployment** (see navigation menu for related documentation)

---

## 🤝 Contributing & Development

This section provides information about 🤝 contributing & development. See related documentation in the navigation menu for detailed guides.


### Q: How can I contribute to CORTEX?

**A:** We welcome contributions! Here's how:

**1. Report Bugs or Request Features**
- [Open a GitHub Issue](https://github.com/asifhussain60/CORTEX/issues)
- Use templates: Bug Report or Feature Request
- Provide context: OS, Python version, error logs

**2. Submit Code Contributions**
```bash
# Fork repository
# Create feature branch
git checkout -b feature/my-feature

# Make changes, add tests
pytest tests/

# Commit with clear message
git commit -m "feat: Add custom plugin support"

# Push and create PR
git push origin feature/my-feature
```

**3. Improve Documentation**
- Fix typos, clarify explanations
- Add examples and use cases
- Update FAQ with common questions
- Translate docs (internationalization)

**4. Share Your Use Cases**
- Blog posts, tutorials, videos
- Community discussions
- Conference talks

**Contribution Guidelines:** **CONTRIBUTING.md** (see navigation menu for related documentation)

---

### Q: What's the testing strategy?

**A:** CORTEX uses layered testing methodology:

**1. Unit Tests (Fast)**
- Test individual functions/classes in isolation
- Mock external dependencies
- Run in <1 second
- Coverage: 80%+ required

**2. Integration Tests (Medium)**
- Test component interactions (agents, tiers, routers)
- Use test databases (not production)
- Run in <10 seconds
- Coverage: Key workflows

**3. System Tests (Slow)**
- Test end-to-end workflows
- Documentation generation, conversation import
- Run in <60 seconds
- Coverage: User stories

**4. Acceptance Tests (Manual)**
- User experience validation
- Planning workflow usability
- Documentation quality review

**Run tests:**
```bash
# All tests
pytest tests/

# Specific layer
pytest tests/unit/
pytest tests/integration/
pytest tests/system/

# With coverage
pytest --cov=src --cov-report=html
```

**Test-Driven Development (TDD):** Write tests before implementation.

**Learn more:** **Testing Strategy** (see navigation menu for related documentation)

---

### Q: How do I run CORTEX tests locally?

**A:** 

**Prerequisites:**
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Verify installation
pytest --version
```

**Run All Tests:**
```bash
cd ~/CORTEX
pytest tests/ -v
```

**Run Specific Test File:**
```bash
pytest tests/unit/test_brain_protector.py -v
```

**Run with Coverage:**
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
# Open htmlcov/index.html for detailed report
```

**Run Fast Tests Only:**
```bash
pytest tests/ -m "not slow"
```

**Debug Failing Test:**
```bash
pytest tests/unit/test_brain_protector.py -v -s --pdb
# -s: Show print statements
# --pdb: Drop into debugger on failure
```

**Continuous Testing (Watch Mode):**
```bash
pip install pytest-watch
ptw tests/ -- --cov=src
```

**Learn more:** **Developer Guide** (see navigation menu for related documentation)

---

### Q: Where is the development roadmap?

**A:** 

**Current Release:** v3.0 (Production Ready)

**Upcoming Features:**

**v3.1 (Q1 2025):**
- Vision API integration (screenshot-driven planning)
- Enhanced FAQ with search analytics
- Performance optimizations (sub-100ms context injection)
- Mobile documentation support

**v3.2 (Q2 2025):**
- Multi-user support (shared brain mode)
- Cloud sync (OneDrive, Dropbox, Google Drive)
- Advanced plugin marketplace
- Real-time collaboration features

**v4.0 (Q3 2025):**
- Neural-inspired learning (self-improvement)
- Multi-language support (Python, JavaScript, C#, Java)
- IDE plugins (PyCharm, IntelliJ, Eclipse)
- Enterprise features (SSO, audit logs, compliance)

**Community Requests:**
- Vote on features in [GitHub Discussions](https://github.com/asifhussain60/CORTEX/discussions)
- Feature requests: [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)

**Learn more:** **ROADMAP.md** (see navigation menu for related documentation)

---

### Q: How do I report bugs or request features?

**A:** 

**Report Bugs:**
1. Go to [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)
2. Click "New Issue"
3. Select "Bug Report" template
4. Fill in:
   - **Describe the bug:** Clear summary
   - **To Reproduce:** Step-by-step instructions
   - **Expected behavior:** What should happen
   - **Actual behavior:** What actually happened
   - **Environment:** OS, Python version, CORTEX version
   - **Logs:** Include error messages, stack traces

**Request Features:**
1. Go to [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)
2. Click "New Issue"
3. Select "Feature Request" template
4. Fill in:
   - **Is your feature related to a problem?** Context
   - **Describe the solution:** What you want
   - **Describe alternatives:** Other approaches considered
   - **Additional context:** Screenshots, examples, use cases

**Community Discussion:**
- [GitHub Discussions](https://github.com/asifhussain60/CORTEX/discussions) for brainstorming
- GitHub Discussions for community support and Q&A

**Response Time:**
- Bugs: 24-48 hours
- Feature requests: 1-2 weeks
- Security issues: Immediate (email: asif@example.com)

---

### Q: What license does CORTEX use?

**A:** CORTEX uses a **Proprietary License** with limited open-source access.

**Key Points:**
- **Free for personal use:** Students, hobbyists, open-source projects
- **Commercial use requires license:** Enterprise features, team deployment
- **Source code available:** Read, study, modify for personal use
- **Contributions welcome:** Contributors retain rights, grant MIT license to project

**Full License:** **LICENSE** (see navigation menu for related documentation)

**Contact:** For commercial licensing inquiries, email: asif@example.com

---

## 💬 Still Have Questions?

- **GitHub Discussions:** [Ask the community](https://github.com/asifhussain60/CORTEX/discussions)
- **GitHub Issues:** [Report bugs or request features](https://github.com/asifhussain60/CORTEX/issues)
- **Documentation:** [Browse complete docs](index.md)
- **Email:** asif@example.com (for security or licensing questions)

---

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**
