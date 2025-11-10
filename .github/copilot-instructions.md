# CORTEX Repository - Development Instructions

This is the **CORTEX** cognitive framework repository - an AI enhancement system that gives GitHub Copilot long-term memory, context awareness, and strategic planning capabilities.

---

## 💬 Response Style (NEW!)

**Default:** Concise responses (50-150 words) with key info upfront.

**You control detail level:**
- "be concise" / "keep it brief" → Quick summary  
- "show details" / "give me more" → Structured breakdown (200-400 words)
- "explain fully" / "show everything" → Complete technical detail

Your preference persists across the conversation.

---

## 🧠 What is CORTEX?

CORTEX transforms GitHub Copilot from an amnesiac intern into a continuously improving development partner through:

- **Memory** - Last 20 conversations preserved across sessions
- **Learning** - Accumulates patterns from every interaction
- **Intelligence** - 4-tier brain architecture (Instinct, Memory, Knowledge, Context)
- **Coordination** - 10 specialist agents working together

---

## 🏗️ Architecture

### 4-Tier Brain System

- **Tier 0 (Instinct):** Immutable governance rules (`cortex-brain/brain-protection-rules.yaml`)
  - **SKULL Protection Layer:** Test validation enforcement (prevents untested changes)
- **Tier 1 (Working Memory):** Last 20 conversations in SQLite
- **Tier 2 (Knowledge Graph):** Learned patterns in YAML (`cortex-brain/knowledge-graph.yaml`)
- **Tier 3 (Development Context):** Git metrics, test coverage, project health

### 10 Specialist Agents

**LEFT BRAIN (Tactical):**
- Executor - Implements features
- Tester - Creates comprehensive tests
- Validator - Quality assurance
- Work Planner - Task breakdown
- Documenter - Auto-generates docs

**RIGHT BRAIN (Strategic):**
- Intent Detector - Routes requests
- Architect - System design
- Health Validator - Project diagnosis
- Pattern Matcher - Finds similar problems
- Learner - Accumulates wisdom

### Plugin System

CORTEX uses an extensible plugin architecture. All plugins:
- Inherit from `BasePlugin` (`src/plugins/base_plugin.py`)
- Register via plugin registry
- Can add commands via command registry
- Hook into lifecycle events

**Current Plugins:**
**Current plugins with commands:**

### 🖥️  Platform & Environment

- **platform_switch:** `/setup` (aliases: /env, /environment, /configure) - Setup/reconfigure development environment

---

## 🚀 Quick Commands

Use `/CORTEX` for full entry point, or use natural language:

- "Add authentication" → Plans and implements
- "Continue" → Resumes last conversation
- "Test this feature" → Generates comprehensive tests
- "Make it purple" → Remembers earlier context
- "Setup environment" → Platform-specific configuration

---

## 📦 Project Structure

```
CORTEX/
├── cortex-brain/           # Cognitive storage (Tier 0-3)
├── src/                    # Source code
│   ├── plugins/            # Extensible plugin system
│   ├── tier0/              # Governance & protection
│   ├── tier1/              # Conversation memory
│   ├── tier2/              # Knowledge graph
│   ├── tier3/              # Development context
│   └── cortex_agents/      # 10 specialist agents
├── prompts/                # AI context prompts
│   ├── user/               # Entry points
│   └── shared/             # Modular documentation
├── scripts/                # Automation tools
├── tests/                  # Comprehensive test suite
└── docs/                   # Human-readable documentation
```

---

## 🔧 Development Guidelines

### SKULL Protection Layer

**CRITICAL:** All fixes must pass SKULL validation before claiming complete.

**The 4 SKULL Rules:**
1. **SKULL-001:** Test Before Claim (BLOCKING) - Never claim "Fixed ✅" without running tests
2. **SKULL-002:** Integration Verification (BLOCKING) - Integrations need end-to-end tests
3. **SKULL-003:** Visual Regression (WARNING) - CSS/UI changes need visual validation
4. **SKULL-004:** Retry Without Learning (WARNING) - Diagnose failures before retrying

**Quick Reference:** `.github/SKULL-QUICK-REFERENCE.md`

---

### Adding New Plugins

1. **Create plugin file** in `src/plugins/`
2. **Inherit from BasePlugin:**
   ```python
   from src.plugins.base_plugin import BasePlugin, PluginMetadata
   
   class MyPlugin(BasePlugin):
       def _get_metadata(self) -> PluginMetadata:
           # Plugin info
       
       def initialize(self) -> bool:
           # Setup logic
       
       def execute(self, request: str, context: Dict) -> Dict:
           # Main logic
       
       def cleanup(self) -> bool:
           # Teardown
   ```

3. **Register commands** (optional):
   ```python
   def register_commands(self) -> List[CommandMetadata]:
       return [
           CommandMetadata(
               command="/mycommand",
               natural_language_equivalent="my feature",
               plugin_id=self.metadata.plugin_id,
               description="Does something cool"
           )
       ]
   ```

4. **Register plugin:**
   ```python
   def register() -> BasePlugin:
       return MyPlugin()
   ```

5. **Update entry point** - Plugin commands automatically available via command registry!

### Testing

- Run all tests: `pytest`
- Run specific suite: `pytest tests/plugins/`
- Test coverage: `pytest --cov=src`

### Documentation

- Update `.github/prompts/CORTEX.prompt.md` if adding major features (or run sync script)
- Update plugin list in `.github/copilot-instructions.md` (this file) via `python scripts/sync_plugin_commands.py`
- Run doc refresh: `python scripts/refresh_docs.py`

---

## 🎯 Current Status

**Version:** 5.0 (CORTEX 2.0 - Modular Architecture)  
**Phase:** Production Ready  
**Token Optimization:** 97.2% reduction achieved  
**Test Coverage:** 82 tests passing

**Recent Enhancements:**
- ✅ Modular entry point (97% token reduction)
- ✅ Platform auto-detection (Mac/Windows/Linux)
- ✅ Plugin command registry
- ✅ YAML-based brain protection rules
- ✅ GitHub Copilot integration (this file!)

---

## 🔌 Plugin Extensibility

**Command Registry System:**

When plugins register commands via `register_commands()`, they automatically become available:
- In natural language routing
- In slash command shortcuts
- In CORTEX entry point documentation

**No manual updates needed** - the command registry handles integration automatically!

**Example workflow for new plugin:**
1. Create plugin with `register_commands()`
2. Plugin registers with command registry on initialization
3. Commands immediately available in `/CORTEX` and natural language
4. Entry point auto-discovers new commands

---

## 📚 Key Files

- **Entry Point:** `.github/prompts/CORTEX.prompt.md` - Use `/CORTEX` command in Copilot Chat
- **Baseline Context:** `.github/copilot-instructions.md` - Auto-loaded for all chats (this file)
- **Plugin Base:** `src/plugins/base_plugin.py` - Plugin foundation
- **Command Registry:** `src/plugins/command_registry.py` - Command management
- **Brain Rules:** `cortex-brain/brain-protection-rules.yaml` - Governance
- **Knowledge Graph:** `cortex-brain/knowledge-graph.yaml` - Learned patterns
- **Config:** `cortex.config.json` - Multi-machine paths

---

## 💡 Usage Tips

- **Always use `/CORTEX`** for consistent entry point
- **Plugins auto-register** - no manual entry point updates
- **Test locally first** before committing plugin changes
- **Follow BasePlugin contract** for compatibility
- **Use command registry** for slash commands

---

## 🆘 Troubleshooting

**Plugin not found:**
- Check `register()` function exists
- Verify plugin in `src/plugins/` directory
- Ensure `BasePlugin` inheritance

**Command not recognized:**
- Check `register_commands()` returns list
- Verify command registry import
- Test command registration in plugin tests

**Path issues:**
- Check `cortex.config.json` machine paths
- Verify `CORTEX_ROOT` environment variable
- Use `config.py` for path resolution

---

## 🎯 Next Steps for Contributors

1. **Read the story:** `prompts/shared/story.md` - Understanding CORTEX
2. **Review architecture:** `docs/architecture/` - System design
3. **Check current plugins:** `src/plugins/` - Examples
4. **Add your plugin:** Follow guidelines above
5. **Test thoroughly:** `pytest tests/plugins/test_your_plugin.py`
6. **Update docs:** Entry point auto-discovers commands!

---

*This file provides baseline context for all GitHub Copilot interactions in the CORTEX repository. Use `/CORTEX` for full capabilities.*

*Last Updated: 2025-11-10 | CORTEX 2.0 Modular Architecture + Response Templates*
