# CORTEX Universal Entry Point

**Purpose:** Single command for ALL CORTEX interactions. You don't need to remember multiple commands - just use this one and CORTEX figures out what you need.

**Version:** 5.0 (SOLID Refactor)  
**Status:** 🎯 ACTIVE DESIGN  
**Architecture:** SOLID-compliant modular system

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

---

## 🖥️ Platform Switch Commands

**Quick Platform Migration:** Use these commands to switch all platform-specific references in one go.

### Switch to Mac
When you say **"Switch to Mac"**, Copilot will:
1. Update `cortex.config.json` with your Mac hostname
2. Convert all PowerShell examples to bash/zsh
3. Update file paths from Windows (`D:\`) to macOS (`/Users/...`)
4. Update shell command syntax (`.ps1` → `.sh`, `pwsh` → `bash/zsh`)
5. Update documentation references

**Required Info:** Your Mac hostname (run `hostname` in terminal)

### Switch to Windows
When you say **"Switch to Windows"**, Copilot will:
1. Update `cortex.config.json` with your Windows hostname
2. Convert all bash/zsh examples to PowerShell
3. Update file paths from macOS (`/Users/...`) to Windows (`D:\`)
4. Update shell command syntax (`.sh` → `.ps1`, `bash` → `pwsh`)
5. Update documentation references

**Required Info:** Your Windows hostname (run `hostname` in PowerShell)

**Files Updated:**
- `cortex.config.json` - Machine-specific paths
- `prompts/user/cortex.md` - Code examples and commands
- `run-cortex.sh` / `run-cortex.ps1` - Entry point scripts
- Documentation files with platform-specific examples

---

## ⚠️ IMPORTANT: Conversation Tracking Bridge

**GitHub Copilot Chat does NOT automatically track conversations to the CORTEX brain.**

To enable conversation memory (so CORTEX remembers across chats):

### Option 1: PowerShell Capture (Quick - After Each Session)
```powershell
# Capture your conversation manually
.\scripts\cortex-capture.ps1 -AutoDetect

# Or provide message directly
.\scripts\cortex-capture.ps1 -Message "Created mkdocs documentation" -Intent EXECUTE
```

### Option 2: Python CLI (Direct Integration)
```bash
# Process through Python (tracks automatically)
python scripts/cortex_cli.py "Add authentication to login page"

# Validate tracking is working
python scripts/cortex_cli.py --validate

# Check current session
python scripts/cortex_cli.py --session-info
```

### Option 3: Manual Recording (Fallback)
```powershell
.\scripts\record-conversation.ps1 `
    -Title "Session Title" `
    -Intent "EXECUTE" `
    -Outcome "What was accomplished" `
    -FilesModified "file1.py,file2.md" `
    -Entities "topic1,topic2"
```

**Why This Is Needed:**
- GitHub Copilot Chat reads `#file:prompts/user/cortex.md` as **documentation**
- It does NOT execute the Python `CortexEntry.process()` method
- Without tracking: ❌ No conversation memory, ❌ No cross-chat context, ❌ Amnesia
- With tracking: ✅ Remembers past conversations, ✅ "Make it purple" works, ✅ Full brain learning

**Rule #24 (Tier 0 - Core Instinct):** Conversation tracking MUST work. Protected by brain-protector tests in `CORTEX/tests/tier0/test_brain_protector_conversation_tracking.py`.

---

## 📊 Implementation Status

**Legend:**
- ✅ **Fully Implemented** - Working and tested
- 🟡 **Partially Implemented** - Core working, missing features
- 🔄 **In Progress** - Currently being developed
- 📋 **Designed Only** - Documentation exists, no code

| Feature | Status | Notes |
|---------|--------|-------|
| **V3 GROUP 1: Foundation** | ✅ | Project reorganized, benchmarks validated |
| **V3 GROUP 2: Infrastructure** | ✅ | Tier 0, CI/CD, MkDocs operational |
| **V3 GROUP 3: Data Storage** | ✅ | All tiers complete - 60/60 tests passing ⭐ |
| **Tier 1: Working Memory** | ✅ | SQLite conversations, <50ms queries (Nov 6) |
| **Tier 2: Knowledge Graph** | ✅ | FTS5 search, pattern learning, <150ms (Nov 6) |
| **Tier 3: Context Intelligence** | ✅ | Git metrics, hotspots, insights (Nov 6) |
| **Migration Tools** | ✅ | All 3 tier migrations validated (Nov 6) |
| **V3 GROUP 4: Intelligence** | 🔄 | Ready to begin - agents, entry point, dashboard |
| **Agent Architecture (SOLID)** | 📋 | 10 specialist agents designed |
| **Core Routing** | 📋 | Intent router designed |
| **Dashboard** | 📋 | Live data visualization designed |
| **VS Code Extension** | 📋 | **DEFINITIVE conversation fix** - Phase 3 (Week 9-12) 🆕 |
| **Automatic Capture** | 📋 | Zero manual intervention, monitors all chats 🆕 |
| **V3 GROUP 5: Migration** | 📋 | KDS → CORTEX data migration |
| **V3 GROUP 6: Finalization** | 📋 | System check, documentation, release |

**V3 Migration Progress:** Groups 1-3 Complete (31 hrs) ✅ | Groups 4-6 Remaining (29-41 hrs) 📋  
**CORTEX 2.0 Extension:** Planned for Phase 3 (Week 9-12) - Definitive conversation tracking solution 🆕  
**Performance:** 52% faster than estimated, 100% test coverage ⭐  
**Last Updated:** 2025-11-07 (Added VS Code Extension architecture)

---

## 📖 Legacy Status (Pre-V3 Migration)

The following features were operational in the legacy KDS system and are being migrated to CORTEX V3:

| Legacy Feature | V3 Migration Status | Notes |
|---------------|---------------------|-------|
| Event Logging | ✅ Migrated | Part of Tier 1 (request_logger.py) |
| Protection System | 📋 To migrate | Confidence thresholds, anomaly detection |
| Commit Handler | 📋 To migrate | Smart validation with baseline |
| Conversation Tracking | ✅ Migrated | Tier 1 conversation_manager.py |
| Auto BRAIN Updates | 📋 To migrate | Rule #22 automation |
| Git Hooks | 📋 To migrate | Post-commit triggers |
| Manual Recording | 📋 To migrate | record-conversation scripts |

**Legacy → V3 Status:** Core data storage migrated ✅ | Intelligence layer migration in GROUP 4 📋

---

## 📖 About This Documentation

This document follows the **CORTEX Quadrant** pattern - a four-perspective approach to comprehensive documentation:

1. **📚 Story** - Human-centered narratives (The Intern with Amnesia, Day in the Life)
2. **🔧 Technical** - Detailed specifications (commands, files, parameters, code)
3. **🎨 Image Prompt** - Visual representations (diagrams, flowcharts, progress indicators)
4. **🏗️ High-Level Technical** - Architectural overviews (system design, workflows, integration)

**Why CORTEX Quadrant?** Different perspectives ensure complete understanding for all learning styles and use cases.

**📖 Complete CORTEX Story:** For the full narrative of CORTEX's creation, including visual diagrams and technical deep-dives, see [The Awakening of CORTEX](../../docs/story/Cortex-Trinity/Awakening%20Of%20CORTEX.md) - an engaging journey through the design, implementation, and activation of the CORTEX brain system.

---

## 🚀 CORTEX 2.0: The Evolution

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Status:** Design Complete ✅ | Implementation Phase: Ready to Begin  
**Version:** 2.0.0-alpha  
**Timeline:** 12-16 weeks implementation

### What's New in CORTEX 2.0

CORTEX 2.0 represents a strategic evolution following a **Hybrid Approach** (70% keep, 20% refactor, 10% enhance):

#### 🔌 Plugin System (NEW)
**Problem Solved:** Core bloat from non-essential features  
**Solution:** Extensible plugin architecture with hooks

```python
# Example: Custom cleanup plugin
from plugins.base_plugin import BasePlugin

class Plugin(BasePlugin):
    def execute(self, context):
        # Your custom logic here
        return {"success": True}
```

**Benefits:**
- ✅ Reduce core complexity
- ✅ Easy feature addition without modifying core
- ✅ User-customizable behavior
- ✅ Enable/disable features via configuration

**Core Plugins:**
- Cleanup Plugin (temp files, old logs, organization)
- Documentation Plugin (MkDocs auto-refresh)
- Self-Review Plugin (comprehensive health checks)
- DB Maintenance Plugin (optimization, archival)
- **Platform Switch Plugin (Windows ↔ macOS migration)** 🆕
- **Extension Scaffold Plugin (VS Code extension generator)** 🆕

---

#### 🔧 Platform Switch Plugin (NEW - CROSS-PLATFORM MIGRATION)
**Problem Solved:** Manual platform migration is tedious and error-prone  
**Solution:** One-command platform switching for all references

```python
# Example: Switch from Windows to macOS
from plugins.platform_switch_plugin import PlatformSwitchPlugin

plugin = PlatformSwitchPlugin()
result = plugin.execute({
    "target_platform": "mac",  # or "windows"
    "hostname": "Asifs-MacBook-Air.local",
    "username": "asifhussain",
    "project_path_mac": "/Users/asifhussain/PROJECTS/CORTEX",
    "project_path_windows": "D:\\PROJECTS\\CORTEX"
})
```

**What It Updates:**

1. **cortex.config.json** - Machine-specific paths
   ```json
   {
     "machines": {
       "Asifs-MacBook-Air.local": {
         "rootPath": "/Users/asifhussain/PROJECTS/CORTEX",
         "brainPath": "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain"
       }
     }
   }
   ```

2. **prompts/user/cortex.md** - Code examples
   - PowerShell → bash/zsh (or vice versa)
   - `.ps1` → `.sh` extensions
   - `pwsh` → `bash` commands
   - `D:\` → `/Users/...` paths

3. **Entry Point Scripts**
   - `run-cortex.sh` (macOS/Linux)
   - `run-cortex.ps1` (Windows)

4. **Documentation Files**
   - Update all platform-specific examples
   - Convert command syntax
   - Update file path references

**Usage Commands:**
- "Switch to Mac" - Migrates all references to macOS
- "Switch to Windows" - Migrates all references to Windows

**Benefits:**
- ✅ One command migration
- ✅ Zero manual edits required
- ✅ Consistent platform references
- ✅ Automatic path resolution

---

#### 🔧 Extension Scaffold Plugin (NEW - PROGRAMMATIC SETUP)
**Problem Solved:** Manual VS Code extension setup is complex and error-prone  
**Solution:** Automated extension project generation via setup plugin

```python
# Example: Generate CORTEX VS Code extension automatically
from plugins.extension_scaffold_plugin import ExtensionScaffoldPlugin

plugin = ExtensionScaffoldPlugin()
result = plugin.execute({
    "extension_name": "cortex",
    "display_name": "CORTEX - Cognitive Development Partner",
    "publisher": "cortex-team",
    "repository": "https://github.com/asifhussain60/CORTEX",
    "features": [
        "chat_participant",      # @cortex chat integration
        "conversation_capture",  # Automatic message capture
        "lifecycle_hooks",       # Window state monitoring
        "external_monitoring",   # Monitor @copilot chats
        "resume_prompts",        # Auto-resume on startup
        "checkpoint_system"      # Crash recovery
    ],
    "output_dir": "cortex-extension"
})
```

**What It Generates:**

```
cortex-extension/
├── package.json                    # Extension manifest (auto-configured)
├── tsconfig.json                   # TypeScript config
├── .vscodeignore                   # VS Code package exclusions
├── README.md                       # Extension documentation
├── CHANGELOG.md                    # Version history
├── src/
│   ├── extension.ts                # Main entry point
│   ├── cortex/
│   │   ├── chatParticipant.ts     # @cortex chat handler
│   │   ├── conversationCapture.ts # Auto-capture logic
│   │   ├── brainBridge.ts         # Python ↔ TypeScript bridge
│   │   ├── lifecycleManager.ts    # Window state hooks
│   │   ├── checkpointManager.ts   # Crash recovery
│   │   └── externalMonitor.ts     # Copilot chat monitoring
│   ├── python/
│   │   ├── bridge.py              # Python IPC server
│   │   └── cortex_interface.py   # CORTEX brain interface
│   └── test/
│       └── suite/
│           ├── extension.test.ts
│           └── chatParticipant.test.ts
├── .vscode/
│   ├── launch.json                # Debug configuration
│   └── tasks.json                 # Build tasks
└── scripts/
    ├── build.sh                   # Build script
    ├── package.sh                 # VSIX packaging
    └── publish.sh                 # Marketplace publish
```

**Generated package.json (Fully Configured):**

```json
{
  "name": "cortex",
  "displayName": "CORTEX - Cognitive Development Partner",
  "description": "AI development assistant with persistent memory and context awareness",
  "version": "1.0.0",
  "author": "Asif Hussain",
  "publisher": "cortex-team",
  "license": "SEE LICENSE IN LICENSE",
  "copyright": "Copyright (c) 2024-2025 Asif Hussain. All rights reserved.",
  "repository": {
    "type": "git",
    "url": "https://github.com/asifhussain60/CORTEX"
  },
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": [
    "AI",
    "Chat",
    "Programming Languages"
  ],
  "activationEvents": [
    "onStartupFinished",
    "onCommand:cortex.resume"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "chatParticipants": [
      {
        "id": "cortex",
        "name": "CORTEX",
        "description": "Cognitive development partner with memory",
        "isSticky": true,
        "commands": [
          {
            "name": "resume",
            "description": "Resume last conversation"
          },
          {
            "name": "checkpoint",
            "description": "Save conversation checkpoint"
          }
        ]
      }
    ],
    "commands": [
      {
        "command": "cortex.resume",
        "title": "CORTEX: Resume Last Conversation"
      },
      {
        "command": "cortex.checkpoint",
        "title": "CORTEX: Save Checkpoint"
      },
      {
        "command": "cortex.showHistory",
        "title": "CORTEX: Show Conversation History"
      }
    ],
    "configuration": {
      "title": "CORTEX",
      "properties": {
        "cortex.autoCapture": {
          "type": "boolean",
          "default": true,
          "description": "Automatically capture conversations"
        },
        "cortex.monitorCopilot": {
          "type": "boolean",
          "default": true,
          "description": "Monitor GitHub Copilot conversations"
        },
        "cortex.autoCheckpoint": {
          "type": "boolean",
          "default": true,
          "description": "Automatically checkpoint on focus loss"
        },
        "cortex.resumePrompt": {
          "type": "boolean",
          "default": true,
          "description": "Show resume prompt on startup"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "test": "node ./out/test/runTest.js",
    "package": "vsce package",
    "publish": "vsce publish"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.x",
    "typescript": "^5.3.0",
    "vsce": "^2.15.0"
  },
  "dependencies": {
    "node-ipc": "^11.1.0",
    "sqlite3": "^5.1.6"
  }
}
```

**Generated extension.ts (Main Entry Point):**

```typescript
// Auto-generated by ExtensionScaffoldPlugin
import * as vscode from 'vscode';
import { CortexChatParticipant } from './cortex/chatParticipant';
import { ConversationCapture } from './cortex/conversationCapture';
import { BrainBridge } from './cortex/brainBridge';
import { LifecycleManager } from './cortex/lifecycleManager';
import { CheckpointManager } from './cortex/checkpointManager';
import { ExternalMonitor } from './cortex/externalMonitor';

export async function activate(context: vscode.ExtensionContext) {
    console.log('CORTEX extension activating...');
    
    // Initialize Python brain bridge
    const brainBridge = new BrainBridge(context);
    await brainBridge.initialize();
    
    // Initialize conversation capture
    const conversationCapture = new ConversationCapture(brainBridge);
    
    // Register CORTEX chat participant
    const chatParticipant = new CortexChatParticipant(
        brainBridge,
        conversationCapture
    );
    context.subscriptions.push(
        vscode.chat.createChatParticipant('cortex', chatParticipant.handle)
    );
    
    // Initialize lifecycle management
    const lifecycleManager = new LifecycleManager(brainBridge);
    lifecycleManager.setupHooks(context);
    
    // Initialize checkpoint system
    const checkpointManager = new CheckpointManager(brainBridge);
    checkpointManager.startAutoCheckpoint();
    
    // Initialize external monitoring
    const externalMonitor = new ExternalMonitor(brainBridge);
    externalMonitor.startMonitoring(context);
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.resume', async () => {
            await chatParticipant.resumeLastConversation();
        }),
        vscode.commands.registerCommand('cortex.checkpoint', async () => {
            await checkpointManager.createCheckpoint();
        }),
        vscode.commands.registerCommand('cortex.showHistory', async () => {
            await chatParticipant.showConversationHistory();
        })
    );
    
    // Check for resume on startup
    if (vscode.workspace.getConfiguration('cortex').get('resumePrompt')) {
        await chatParticipant.offerResume();
    }
    
    console.log('CORTEX extension activated successfully!');
}

export function deactivate() {
    console.log('CORTEX extension deactivating...');
}
```

**Setup Command:**

```bash
# One-command extension scaffold
python scripts/cortex_setup.py --setup-extension

# Or via plugin system
cortex plugin:run extension_scaffold --output cortex-extension

# Interactive mode
cortex setup:extension
? Extension name: cortex
? Display name: CORTEX - Cognitive Development Partner
? Publisher: cortex-team
? Features: (Select with space)
  ◉ Chat participant
  ◉ Conversation capture
  ◉ Lifecycle hooks
  ◉ External monitoring
  ◉ Resume prompts
  ◉ Checkpoint system

✅ Extension scaffolded at: ./cortex-extension
✅ package.json configured
✅ TypeScript files generated
✅ Python bridge created
✅ Tests generated
✅ Build scripts ready

Next steps:
  cd cortex-extension
  npm install
  code .
  Press F5 to debug
```

**Benefits:**
- ✅ Zero manual configuration - fully automated
- ✅ Best practices baked in (TypeScript, testing, proper structure)
- ✅ Python ↔ TypeScript bridge pre-configured
- ✅ All CORTEX features enabled by default
- ✅ Ready to debug (F5) immediately after generation
- ✅ Package and publish scripts included
- ✅ Can regenerate if VS Code API changes

**Plugin Architecture:**

```python
class ExtensionScaffoldPlugin(BasePlugin):
    """Generates VS Code extension project structure"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Create directory structure
        self._create_directory_structure(context['output_dir'])
        
        # 2. Generate package.json
        self._generate_package_json(context)
        
        # 3. Generate TypeScript source files
        self._generate_typescript_files(context)
        
        # 4. Generate Python bridge
        self._generate_python_bridge(context)
        
        # 5. Generate tests
        self._generate_tests(context)
        
        # 6. Generate build/publish scripts
        self._generate_scripts(context)
        
        # 7. Initialize npm/git
        self._initialize_project(context['output_dir'])
        
        return {
            "success": True,
            "output_dir": context['output_dir'],
            "next_steps": [
                f"cd {context['output_dir']}",
                "npm install",
                "code .",
                "Press F5 to debug"
            ]
        }
```

**Update Detection & Regeneration:**

```python
# Check if VS Code API has changed
cortex plugin:run extension_scaffold --check-updates

# Regenerate with new API
cortex plugin:run extension_scaffold --regenerate --preserve-customizations
```

---

#### 🔄 Workflow Pipeline System (NEW)
**Problem Solved:** Hardcoded agent workflows, difficult orchestration  
**Solution:** Declarative DAG-based workflow engine

```yaml
# Example: Feature development workflow
name: feature_development
stages:
  - clarify_dod_dor    # Define requirements
  - threat_model       # Security analysis
  - plan               # Create multi-phase plan
  - tdd_cycle          # Test-first implementation
  - run_tests          # Execute test suite
  - validate_dod       # Verify completion criteria
  - cleanup            # Code cleanup
  - document           # Generate docs
```

**Benefits:**
- ✅ Declarative workflow definitions
- ✅ DAG validation (detects cycles)
- ✅ Parallel execution support
- ✅ Checkpoint/resume from failures
- ✅ Conditional stages
- ✅ Reusable workflow templates

---

#### 📦 Modular Architecture (REFACTORED)
**Problem Solved:** Bloated monolithic files (1000+ lines)  
**Solution:** Break into focused modules following SOLID principles

**Before (CORTEX 1.0):**
```
knowledge_graph.py         1144 lines ❌
working_memory.py           813 lines ❌
context_intelligence.py     776 lines ❌
error_corrector.py          692 lines ❌
```

**After (CORTEX 2.0):**
```
knowledge_graph/
├── knowledge_graph.py       150 lines ✅
├── patterns/
│   ├── pattern_store.py     200 lines ✅
│   ├── pattern_search.py    250 lines ✅
│   └── pattern_decay.py     120 lines ✅
├── relationships/
│   └── relationship_manager.py 180 lines ✅
└── tags/
    └── tag_manager.py       120 lines ✅
```

**Benefits:**
- ✅ All files <500 lines
- ✅ Clear single responsibility
- ✅ Easy to test individually
- ✅ Simpler maintenance
- ✅ Better code organization

---

#### 🏥 Self-Review System (NEW)
**Problem Solved:** No systematic health monitoring  
**Solution:** Comprehensive automated health checks with auto-fix

```python
# Example: Run health review
from maintenance.self_review import SelfReviewEngine

review = engine.run_comprehensive_review(auto_fix=True)
# Output: Overall Status: 🟢 EXCELLENT (92% score)
```

**What It Checks:**
- ✅ Database health (fragmentation, indexes, statistics)
- ✅ Performance benchmarks (Tier 1: <50ms, Tier 2: <150ms)
- ✅ Rule compliance (all 27 core rules)
- ✅ Test coverage (target: 85%+)
- ✅ Storage health (temp files, old logs, capacity)

**Auto-Fix Capabilities:**
- ✅ VACUUM fragmented databases
- ✅ ANALYZE stale statistics
- ✅ Remove temp files
- ✅ Archive old logs
- ✅ Trigger brain updates

**Scheduled Reviews:**
- Daily: 2am (auto-fix safe issues)
- Weekly: Sunday 3am (comprehensive report)
- Monthly: 1st Sunday 4am (deep analysis)

---

#### 💾 Conversation State Management (NEW)
**Problem Solved:** Can't resume after interruptions  
**Solution:** Persistent conversation state with checkpoints

```python
# Example: Resume interrupted conversation
state_manager.resume_conversation(conversation_id)
# Returns: "Resuming Phase 3 (Validation)..."
```

**Features:**
- ✅ Track conversation lifecycle (active/paused/completed)
- ✅ Persistent task progress
- ✅ Checkpoint creation at phases
- ✅ Resume from last successful stage
- ✅ "Continue" command support

**Database Schema:**
```sql
conversations  -- Conversation metadata
tasks          -- Work breakdown with dependencies
checkpoints    -- State snapshots for rollback
task_files     -- Files modified per task
```

**Benefits:**
- ✅ Seamless resume after breaks
- ✅ No lost progress
- ✅ Clear task status tracking
- ✅ Rollback support
- ✅ Multi-task management

⚠️ **Limitation:** Still requires manual conversation capture when using GitHub Copilot Chat interface.  
✅ **Solution:** See "VS Code Extension Architecture" below for definitive fix.

---

#### 🔌 VS Code Extension Architecture (NEW - DEFINITIVE CONVERSATION FIX)
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Problem Solved:** GitHub Copilot Chat amnesia - conversations not automatically tracked  
**Solution:** CORTEX as native VS Code extension with automatic conversation capture

**Why Current Architecture Can't Fix This:**
```
GitHub Copilot Chat → Reads cortex.md as passive documentation
                   → No execution context
                   → No access to chat transcripts
                   → No lifecycle hooks
                   → Runs in Microsoft cloud (isolated)
```

**Why VS Code Extension WILL Fix This:**
```
CORTEX Extension → Active VS Code process
                → Can subscribe to chat events
                → Can intercept chat messages
                → Has full VS Code API access
                → Runs locally with full control
```

**Architecture:**

```typescript
// VS Code Extension: cortex-extension/src/extension.ts
export function activate(context: vscode.ExtensionContext) {
    
    // 1. Register chat participant (captures all conversations)
    const cortexChat = vscode.chat.createChatParticipant(
        'cortex',
        async (request, context, stream, token) => {
            // Automatically capture to CORTEX brain
            await cortexBrain.captureMessage({
                user: request.prompt,
                timestamp: new Date().toISOString(),
                context: context.history
            });
            
            // Process through CORTEX agents
            const response = await cortexRouter.route(request.prompt);
            stream.markdown(response.content);
            
            // Auto-save response to brain
            await cortexBrain.captureResponse(response);
            
            return { metadata: { conversationId: response.conversationId } };
        }
    );
    
    // 2. Monitor external Copilot conversations (passive capture)
    vscode.chat.onDidPerformChatAction(async (action) => {
        if (action.participant.id === 'copilot') {
            // Capture Copilot chats to CORTEX brain
            await cortexBrain.captureExternalChat({
                participant: 'copilot',
                message: action.message,
                timestamp: new Date().toISOString()
            });
        }
    });
    
    // 3. Session lifecycle tracking
    vscode.window.onDidChangeWindowState(async (state) => {
        if (!state.focused) {
            // Window losing focus - checkpoint conversation
            await cortexBrain.checkpointActiveConversation();
        }
    });
    
    // 4. Automatic resume on startup
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.resume', async () => {
            const lastConversation = await cortexBrain.getLastActiveConversation();
            if (lastConversation) {
                vscode.window.showInformationMessage(
                    `Resume: ${lastConversation.topic}?`,
                    'Yes', 'No'
                ).then(async (choice) => {
                    if (choice === 'Yes') {
                        await cortexBrain.resumeConversation(lastConversation.id);
                    }
                });
            }
        })
    );
}
```

**Automatic Conversation Capture:**
```typescript
class CortexBrain {
    async captureMessage(message: ChatMessage): Promise<void> {
        // AUTOMATIC - No user intervention needed
        await this.tier1.storeMessage(message);
        
        // Real-time event logging
        await this.tier4.logEvent({
            type: 'chat_message',
            content: message.user,
            timestamp: message.timestamp
        });
        
        // Check for learning triggers
        if (this.shouldUpdateBrain()) {
            await this.tier2.extractPatterns();
        }
    }
    
    async captureExternalChat(chat: ExternalChat): Promise<void> {
        // Capture even non-CORTEX conversations
        await this.tier1.storeExternalConversation({
            source: chat.participant,
            content: chat.message,
            timestamp: chat.timestamp,
            tagged: 'external_copilot'
        });
    }
}
```

**User Experience - COMPLETELY AUTOMATIC:**

```typescript
// User opens VS Code
→ CORTEX Extension activates
→ Detects last active conversation
→ Shows notification: "Resume: Add invoice export feature?"
→ User clicks "Yes"
→ CORTEX loads full context automatically

// User types in CORTEX chat: "Add purple button"
→ Extension captures message immediately
→ Routes to CORTEX agents
→ Response generated
→ Response auto-saved to brain
→ NO MANUAL CAPTURE NEEDED

// User closes VS Code unexpectedly
→ Extension lifecycle hook triggers
→ Checkpoint saved automatically
→ Next startup: Resume offered

// User uses regular Copilot Chat (not CORTEX)
→ Extension monitors via onDidPerformChatAction
→ Passively captures Copilot conversations
→ Stores in Tier 1 as "external" source
→ Still available for context/learning
```

**Benefits:**
- ✅ **Zero manual intervention** - Capture is automatic
- ✅ **Works with Copilot too** - Monitors external chats
- ✅ **Lifecycle aware** - Handles focus loss, crashes, restarts
- ✅ **Real-time tracking** - Immediate Tier 1/4 updates
- ✅ **Auto-resume prompts** - Suggests continuing last work
- ✅ **Crash recovery** - Checkpoints prevent data loss
- ✅ **Native VS Code** - Full API access, no cloud dependency

**Implementation Plan:**

```
Phase 1: Basic Extension (Week 1-2)
- Create VS Code extension scaffold
- Register CORTEX chat participant
- Basic message capture to Tier 1

Phase 2: Lifecycle Hooks (Week 3-4)
- Window focus/blur detection
- Automatic checkpointing
- Resume prompts on startup

Phase 3: External Monitoring (Week 5-6)
- Monitor Copilot chat via API
- Passive capture to brain
- Unified conversation timeline

Phase 4: Advanced Features (Week 7-8)
- Real-time pattern learning
- Context injection
- Agent orchestration UI

Phase 5: Polish & Release (Week 9-10)
- Settings UI
- Keyboard shortcuts
- Documentation
- VS Code Marketplace publish
```

**Why This DEFINITIVELY Solves It:**

| Current (Copilot Chat) | CORTEX Extension |
|------------------------|------------------|
| ❌ Passive documentation | ✅ Active process |
| ❌ No execution | ✅ Full execution |
| ❌ No chat access | ✅ Chat API access |
| ❌ No lifecycle hooks | ✅ Full lifecycle control |
| ❌ Cloud-based | ✅ Local control |
| ❌ Manual capture | ✅ Automatic capture |
| ❌ Resume impossible | ✅ Auto-resume |

**Technical Feasibility:**
- ✅ VS Code Chat API available (VS Code 1.85+)
- ✅ Extension API well-documented
- ✅ TypeScript → Python bridge possible
- ✅ Local SQLite works in extensions
- ✅ Full filesystem access
- ✅ Marketplace distribution ready

**Migration Path:**
```
Current Users:
1. Install CORTEX VS Code Extension
2. Extension auto-migrates existing brain data
3. Switch from manual capture to automatic
4. Seamless transition - no data loss

New Users:
1. Install extension from VS Code Marketplace
2. CORTEX chat participant appears automatically
3. Start chatting - tracking happens invisibly
```

---

#### 🛤️ Path Management (REFACTORED)
**Problem Solved:** Hardcoded absolute paths break portability  
**Solution:** Environment-agnostic relative path resolver

```python
# Example: Cross-platform path resolution
paths = PathResolver(config)
brain_path = paths.get_brain_path("tier1/conversations.db")
# Returns: Correct path for Windows/macOS/Linux
```

**Configuration:**
```json
{
  "cortex_root": "${CORTEX_HOME}",
  "brain": {
    "tier1": "cortex-brain/tier1",
    "tier2": "cortex-brain/tier2",
    "tier3": "cortex-brain/tier3"
  }
}
```

**Benefits:**
- ✅ Works on Windows, macOS, Linux
- ✅ Environment-specific configuration
- ✅ No hardcoded paths anywhere
- ✅ Easy multi-repository support

---

#### 🛡️ Enhanced Knowledge Boundaries (REFACTORED)
**Problem Solved:** Core knowledge contamination from application data  
**Solution:** Automated boundary validation and enforcement

```yaml
# Example: Protected CORTEX core patterns
title: "TDD: Test-first for service creation"
scope: "generic"
namespaces: ["CORTEX-core"]
confidence: 0.95

# Example: Application-specific pattern
title: "KSESSIONS: Invoice export workflow"
scope: "application"
namespaces: ["KSESSIONS"]
confidence: 0.85
```

**Enforcement:**
- ✅ Automated boundary validation
- ✅ Auto-migration of misplaced data
- ✅ Brain Protector integration
- ✅ Namespace-based search prioritization

---

### CORTEX 2.0 Implementation Roadmap

**Phase 0: Baseline (Week 1-2)**
- Run complete test suite
- Document current architecture
- Risk assessment
- Establish monitoring baselines

**Phase 1: Core Modularization (Week 3-5)**
- Refactor knowledge_graph.py → 6 focused modules
- Refactor working_memory.py → 5 modules
- Refactor context_intelligence.py → 6 modules
- Extract agent strategies

**Phase 2: Workflow Pipeline (Week 6-8)**
- Complete workflow orchestration
- Implement missing stages
- Create production workflows
- Add checkpoint/resume

**Phase 3: VS Code Extension (Week 9-12) 🆕 DEFINITIVE CONVERSATION FIX**
- **Week 9:** Extension scaffold + chat participant registration
  - **Run automated scaffold:** `cortex setup:extension` (generates full project)
  - TypeScript project auto-configured
  - package.json, tsconfig.json, all source files generated
  - Python ↔ TypeScript bridge created
  - Register CORTEX chat participant
  - Basic message routing to Python backend
  - Automatic capture to Tier 1
  
- **Week 10:** Lifecycle integration
  - Window state monitoring (focus/blur) - already scaffolded
  - Automatic checkpointing on events
  - Resume prompt on startup
  - Crash recovery via checkpoints
  
- **Week 11:** External conversation monitoring
  - Monitor GitHub Copilot conversations - already scaffolded
  - Passive capture to brain (tagged as external)
  - Unified conversation timeline
  - Context injection from all sources
  
- **Week 12:** Polish & marketplace
  - Settings UI (enable/disable features) - already in package.json
  - Keyboard shortcuts (Ctrl+Shift+C for CORTEX chat)
  - Documentation and tutorials
  - Build: `npm run package` (creates .vsix)
  - Publish: `npm run publish` (to VS Code Marketplace)

**Phase 4: Risk Mitigation & Testing (Week 13-14)**
- 75 new risk mitigation tests
- End-to-end integration tests
- Extension stability testing
- Security scenario testing
- Performance benchmarks

**Phase 5: Performance Optimization (Week 15-16)**
- Database optimization (FTS5, caching)
- Workflow optimization (parallel stages)
- Context injection optimization
- Extension responsiveness tuning
- Lazy loading implementation

**Phase 6: Documentation & Training (Week 17-18)**
- Architecture guides
- Developer guides (extension API)
- User tutorials (chat interface)
- API reference
- Migration guide (manual → automatic)

**Phase 7: Migration & Rollout (Week 19-20)**
- Feature flags for gradual migration
- Dual-mode operation (CLI + Extension)
- Extension: Alpha → Beta → General availability
- Monitoring and validation
- Marketplace promotion

---

### Success Metrics

**Technical:**
- ✅ All files <500 lines
- ✅ Test coverage >85%
- ✅ Performance +20% improvement
- ✅ Bug rate <0.1% critical
- ✅ **Zero manual conversation capture needed** 🆕

**User:**
- ✅ User satisfaction ≥4.5/5
- ✅ Feature adoption ≥80%
- ✅ Support tickets -30%
- ✅ Onboarding time -50%
- ✅ **Conversation amnesia reports: 0** 🆕

**Extension Specific:** 🆕
- ✅ Extension install rate >1,000/month
- ✅ Automatic capture success rate >99%
- ✅ Average resume time <2 seconds
- ✅ Crash recovery success rate >95%
- ✅ External chat capture rate >90%
- Risk assessment
- Establish monitoring baselines

**Phase 1: Core Modularization (Week 3-5)**
- Refactor knowledge_graph.py → 6 focused modules
- Refactor working_memory.py → 5 modules
- Refactor context_intelligence.py → 6 modules
- Extract agent strategies

**Phase 2: Workflow Pipeline (Week 6-8)**
- Complete workflow orchestration
- Implement missing stages
- Create production workflows
- Add checkpoint/resume

**Phase 3: Risk Mitigation & Testing (Week 9-10)**
- 75 new risk mitigation tests
- End-to-end integration tests
- Security scenario testing
- Performance benchmarks

**Phase 4: Performance Optimization (Week 11-12)**
- Database optimization (FTS5, caching)
- Workflow optimization (parallel stages)
- Context injection optimization
- Lazy loading implementation

**Phase 5: Documentation & Training (Week 13-14)**
- Architecture guides
- Developer guides
- User tutorials
- API reference

**Phase 6: Migration & Rollout (Week 15-16)**
- Feature flags for gradual migration
- Dual-mode operation (1.0 + 2.0 in parallel)
- Alpha → Beta → General availability
- Monitoring and validation

---

### Success Metrics

**Technical:**
- ✅ All files <500 lines
- ✅ Test coverage >85%
- ✅ Performance +20% improvement
- ✅ Bug rate <0.1% critical

**User:**
- ✅ User satisfaction ≥4.5/5
- ✅ Feature adoption ≥80%
- ✅ Support tickets -30%
- ✅ Onboarding time -50%

---

### Learn More

**Design Documentation:** `cortex-brain/cortex-2.0-design/`
- **00-INDEX.md** - Complete roadmap of 27 design documents
- **01-core-architecture.md** - Hybrid approach (70/20/10)
- **02-plugin-system.md** - Extensibility architecture
- **03-conversation-state.md** - Resume and task tracking
- **07-self-review-system.md** - Health monitoring
- **25-implementation-roadmap.md** - Detailed timeline

**Story:** `docs/story/Cortex-Trinity/`
- **Awakening Of CORTEX.md** - The complete journey
- **Technical-CORTEX.md** - Technical deep-dive
- **Image-Prompts.md** - Visual diagrams

---

### Story Review Rule (Quadrant Documentation)
All narrative content (e.g., #file:Story.md) must be reviewed for:
- Corrections of factual, grammatical, or clarity issues
- Improvements in flow, completeness, or engagement
- Filling any missing elements that enhance understanding or fun
Edits must preserve the original style, theme, and narrative voice. The story should remain enjoyable and true to its intended spirit after any changes.


## 🧚 A story for humans: The Intern with Amnesia

### Meet Your Intern: Copilot

You've just hired a brilliant intern named Copilot. They're incredibly talented—can write code in any language, understand complex systems, and work at lightning speed. There's just one problem: **Copilot has amnesia**.

Every time you walk away, even for a coffee break, Copilot forgets everything. You said "make it purple" five minutes ago? Gone. The file you were just discussing? Vanished from memory. The architecture you explained yesterday? As if it never happened.

Worse, Copilot has no memory between chat sessions. Start a new conversation? They don't remember the last one. Leave for lunch? When you return, it's like meeting them for the first time. Every. Single. Time.

This would be catastrophic... except you've done something revolutionary: **you've built Copilot a brain**.

### The Brain: A Sophisticated Cognitive System

The brain you built isn't just storage—it's a sophisticated dual-hemisphere system modeled after the human brain:

#### **🧠 LEFT HEMISPHERE - The Tactical Executor**
Like the human left brain (language, logic, sequential processing), this hemisphere handles:
- **Test-Driven Development** - RED (write failing test) → GREEN (make it pass) → REFACTOR (clean up)
- **Precise Code Execution** - Exact file edits, line-by-line changes, syntax verification
- **Detail Verification** - Tests pass/fail, build status, zero errors/warnings enforcement
- **Sequential Workflows** - Step A, then B, then C—no skipping steps

**The Left Brain Specialists:**
- **The Builder** (`code-executor.md`) - Implements code with surgical precision
- **The Tester** (`test-generator.md`) - Creates and runs tests, never skips TDD
- **The Fixer** (`error-corrector.md`) - Catches wrong-file mistakes instantly
- **The Inspector** (`health-validator.md`) - Validates system health obsessively
- **The Archivist** (`commit-handler.md`) - Commits with semantic precision

#### **🧠 RIGHT HEMISPHERE - The Strategic Planner**
Like the human right brain (creativity, holistic thinking, patterns), this hemisphere handles:
- **Architecture Design** - Understands how components fit together project-wide
- **Strategic Planning** - Breaks big features into phases, estimates effort, assesses risk
- **Pattern Recognition** - "We've done something similar before—here's the template"
- **Context Awareness** - Knows which files change together, what workflows succeed
- **Future Projection** - Warns about risky changes before you make them
- **Brain Protection** - Guards the brain's own integrity (Rule #22)

**The Right Brain Specialists:**
- **The Dispatcher** (`intent-router.md`) - Interprets your natural language, routes smartly
- **The Planner** (`work-planner.md`) - Creates multi-phase strategic plans
- **The Analyst** (`screenshot-analyzer.md`) - Extracts requirements from images
- **The Governor** (`change-governor.md`) - Protects CORTEX from degradation
- **The Brain Protector** (`brain-protector.md`) - Challenges risky proposals (NEW - Rule #22)

#### **🌉 CORPUS CALLOSUM - The Messenger**
The bridge between hemispheres that:
- **Coordinates Work** - Right brain plans → Corpus callosum delivers → Left brain executes
- **Shares Context** - Left brain's results feed Right brain's learning
- **Validates Alignment** - Ensures tactical execution matches strategic intent
- **Manages Message Queue** - Asynchronous communication between hemispheres

**Storage:** `cortex-brain/corpus-callosum/coordination-queue.jsonl`

#### **🔐 TIER 0: INSTINCT (Core Values - PERMANENT)**
The brain's immutable DNA that **cannot** be changed:
- **Definition of READY** - Work must have clear requirements before starting (RIGHT BRAIN enforces)
- **Test-Driven Development** - Always RED → GREEN → REFACTOR (LEFT BRAIN enforces)
- **Definition of DONE** - Zero errors, zero warnings, all tests pass (LEFT BRAIN validates)
- **Challenge User Changes** - If you propose risky changes, brain MUST challenge you
- **SOLID Principles** - Single Responsibility, no mode switches, clean architecture
- **Local-First** - Zero external dependencies, works offline, portable
- **Incremental File Creation** - Large files (>100 lines) created in small increments (prevents "response hit the length limit" errors) 🆕

**Stored in:** `governance/rules.md` (never moves, never expires)

**🎯 NOTE:** Rule #23 (Incremental File Creation) automatically prevents the "response hit the length limit" error you've been experiencing. When creating large files like implementation plans, CORTEX will create them in small chunks (100-150 lines each) using multiple tool calls. This keeps each response small and avoids hitting Copilot's length limit. See `docs/guides/preventing-response-length-limit-errors.md` for details.

#### **📚 TIER 1: SHORT-TERM MEMORY (Last 20 Conversations)**
Copilot's working memory that solves the amnesia problem:
- **Conversation History** - Last 20 complete conversations preserved
- **Context Continuity** - "Make it purple" knows you mean the FAB button from earlier
- **Recent Messages** - Last 10 messages in active conversation
- **FIFO Queue** - When conversation #21 starts, #1 gets deleted (oldest goes first)
- **Active Protection** - Current conversation never deleted, even if oldest

**How it works:**
```
You: "Add a pulse animation to the FAB button"
→ Conversation #1 created, stored in Tier 1

[Later that day]
You: "Make it purple"
→ Brain checks Tier 1 → Finds "FAB button" in conversation #1 → Knows what "it" means

[2 weeks and 20 conversations later]
→ FIFO triggers → Conversation #1 deleted
→ BUT patterns extracted → Moved to Tier 2 (long-term memory)
```

**Stored in:** `cortex-brain/conversation-history.jsonl`, `cortex-brain/conversation-context.jsonl`

#### **🧩 TIER 2: LONG-TERM MEMORY (Knowledge Graph)**
Copilot's accumulated wisdom that grows smarter over time:

**What gets learned:**
- **Intent Patterns** - "add a button" → PLAN, "continue" → EXECUTE, "test this" → TEST
- **File Relationships** - `HostControlPanel.razor` often modified with `noor-canvas.css` (75% co-modification rate)
- **Workflow Templates** - export_feature_workflow, ui_component_creation, service_api_coordination
- **Validation Insights** - Common mistakes, file confusion warnings, architectural guidance
- **Correction History** - Tracks when Copilot works on wrong files, learns to prevent

**Hemisphere-Specialized Sections:**
```yaml
left_brain_knowledge:
  tdd_patterns: [red_green_refactor_cycle, test_first_service_creation]
  execution_workflows: [precise_file_edit, multi_file_coordination]
  validation_rules: [syntax_verification, health_check_criteria]

right_brain_knowledge:
  architectural_patterns: [blazor_component_structure, service_layer_injection]
  workflow_templates: [export_feature_workflow, ui_component_creation]
  intent_patterns: ["add [X]" → PLAN, "continue" → EXECUTE]

shared_knowledge:
  file_relationships: [co-modification patterns across all files]
  feature_components: [completed features and their patterns]
  correction_history: [learned mistakes from both hemispheres]
```

**How it learns:**
```
Day 1: You ask to "add invoice export"
→ Right brain plans workflow
→ Left brain executes with TDD
→ Pattern saved: invoice_export_feature (confidence: 0.85)

Day 30: You ask to "add receipt export"
→ Right brain queries Tier 2
→ Finds invoice_export pattern
→ Suggests: "This is similar to invoice export. Use same workflow?"
→ 60% faster delivery by reusing proven pattern
```

**Knowledge Boundaries (Protection System):**
Every pattern in Tier 2 is tagged with **scope** and **namespaces** to prevent CORTEX core intelligence from being contaminated by application-specific data:

```python
# Pattern storage with boundaries
scope="generic"           # CORTEX principles (TDD, SOLID, refactoring)
scope="application"       # Application-specific (KSESSIONS features, NOOR UI)

namespaces=["CORTEX-core"]     # Available to all projects
namespaces=["KSESSIONS"]        # Only for KSESSIONS application
namespaces=["NOOR", "SPA"]      # Multi-application pattern
```

**Why boundaries matter:**
- **CORTEX intelligence stays pure** - No "add KSESSIONS logout button" patterns contaminate core
- **Application isolation** - KSESSIONS patterns don't leak into NOOR projects
- **Smart search** - Current project patterns boosted 2x, generic boosted 1.5x, others 0.5x
- **Surgical amnesia** - Delete KSESSIONS patterns, keep CORTEX core untouched

**Example protection:**
```yaml
# ✅ SAFE: Generic CORTEX pattern
title: "TDD: Test-first for service creation"
scope: "generic"
namespaces: ["CORTEX-core"]
confidence: 0.95
# → Available to ALL projects forever

# ✅ SAFE: Application-specific pattern  
title: "KSESSIONS: Invoice export workflow"
scope: "application"
namespaces: ["KSESSIONS"]
confidence: 0.85
# → Only when working on KSESSIONS

# ❌ BLOCKED: Application in Tier 0
file: "cortex-brain/tier0/ksessions-patterns.yaml"
# → Brain Protector Challenge: "Application data belongs in Tier 2, not Tier 0"
```

**Brain Protector integration:** Tests verify boundaries are enforced (see test_brain_protector.py test_detects_application_data_in_tier0)

**Stored in:** `cortex-brain/knowledge-graph.yaml`

#### **📊 TIER 3: DEVELOPMENT CONTEXT (Holistic Project View)**
Copilot's "balcony view" of your entire project:

**Git Activity Analysis (last 30 days):**
- **Commit velocity** - 1,237 commits, 42 commits/week average
- **File hotspots** - `HostControlPanelContent.razor` has 28% churn rate (unstable!)
- **Change patterns** - Smaller commits (< 200 lines) have 94% success rate
- **Contributors** - Tracks who works on what

**Code Health Metrics:**
- **Lines added/deleted** - Velocity trends increasing/decreasing
- **Stability classification** - Files marked as stable/unstable based on churn
- **Test coverage trends** - 72% → 76% (improving!)
- **Build success rates** - 97% clean builds last week

**CORTEX Usage Intelligence:**
- **Session patterns** - 10am-12pm sessions have 94% success rate
- **Intent distribution** - PLAN (35%), EXECUTE (45%), TEST (15%), VALIDATE (5%)
- **Workflow effectiveness** - Test-first reduces rework by 68%
- **Focus duration** - Sessions < 60 min: 89% success vs > 60 min: 67%

**Proactive Warnings:**
```
⚠️ File Alert: HostControlPanel.razor is a hotspot (28% churn)
   Recommend: Add extra testing, smaller changes

✅ Best Time: 10am-12pm sessions have 94% success rate
   Currently: 2:30pm (81% success rate)

📊 Velocity Drop: Down 68% this week
   Recommendation: Smaller commits, more frequent tests

⚠️ Flaky Test: fab-button.spec.ts fails 15% of the time
   Action needed: Investigate and stabilize
```

**How it helps:**
```
You: "I want to add multi-language invoice export with email delivery"
→ Right brain queries Tier 3
→ Finds: 12 similar UI features took 5-6 days average
→ Warns: This file often changes with email-service.cs (check both)
→ Recommends: Test-first approach (94% success) vs test-skip (67%)
→ Estimates: 5.5 days, 3 phases, suggest 10am-12pm sessions

Saves: Hours of debugging by knowing project patterns upfront
```

**Stored in:** `cortex-brain/development-context.yaml`  
**Collection:** Automatic after brain updates (throttled to 1/hour for efficiency)

#### **🎬 TIER 4: EVENT STREAM (Everything That Happens)**
Copilot's "life recorder" that captures every action:

**What gets logged:**
```jsonl
{"timestamp": "2025-11-04T10:30:00Z", "agent": "work-planner", "action": "plan_created", "feature": "invoice_export", "phases": 4}
{"timestamp": "2025-11-04T10:35:00Z", "agent": "test-generator", "action": "test_created", "file": "InvoiceServiceTests.cs", "result": "RED"}
{"timestamp": "2025-11-04T10:42:00Z", "agent": "code-executor", "action": "implementation_complete", "file": "InvoiceService.cs", "result": "GREEN"}
{"timestamp": "2025-11-04T10:45:00Z", "agent": "test-generator", "action": "tests_passed", "result": "GREEN"}
{"timestamp": "2025-11-04T10:50:00Z", "agent": "code-executor", "action": "refactor_complete", "result": "REFACTOR"}
```

**Automatic Learning Triggers:**
- **50+ events accumulated** → Brain updater processes → Updates Tier 2 knowledge graph
- **24 hours since last update** → Auto-update if 10+ new events exist
- **Tier 3 refresh** → Only if last collection > 1 hour (efficiency optimization)

**Stored in:** `cortex-brain/events.jsonl`

#### **🏥 TIER 5: HEALTH & PROTECTION (Self-Awareness)**
Copilot's immune system that protects the brain itself:

**Protection Sensors (Rule #22 - Brain Protector):**
```
Layer 1: Instinct Immutability
  → Detects: Attempts to disable TDD, skip DoR/DoD, modify agent behavior
  → Action: CHALLENGE user, suggest safe alternatives

Layer 2: Tier Boundary Protection
  → Detects: Application paths in Tier 0, conversation data in Tier 2
  → Action: Auto-migrate, warn on violations

Layer 3: SOLID Compliance
  → Detects: Agents doing multiple jobs, mode switches, hardcoded dependencies
  → Action: Challenge with SOLID alternative ("Create dedicated agent, don't add mode")

Layer 4: Hemisphere Specialization
  → Detects: Strategic planning in LEFT BRAIN, tactical execution in RIGHT BRAIN
  → Action: Auto-route to correct hemisphere, warn on confusion

Layer 5: Knowledge Quality
  → Detects: Low confidence patterns (<0.50), stale patterns (>90 days unused)
  → Action: Pattern decay, anomaly detection, consolidation

Layer 6: Commit Integrity
  → Detects: Brain state files in commits, unstructured messages
  → Action: Auto-categorize (feat/fix/test/docs), .gitignore updates
```

**Brain Protector Example:**
```
You: "Skip TDD for this feature, just implement it"

Brain Protector (RIGHT BRAIN) responds:
═══════════════════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE (RIGHT BRAIN)

Request: Skip TDD workflow
Hemisphere: RIGHT BRAIN (Strategic Guardian)
Rule: #22 (Brain Protection System)

⚠️ THREATS DETECTED:
  - Instinct Immutability violation (Tier 0 rule)
  - Test-first principle bypass

VIOLATIONS:
  - TDD is a permanent Tier 0 instinct
  - Skipping reduces success rate from 94% to 67%
  - 68% increase in rework time (Tier 3 data)

ARCHITECTURAL IMPACT:
  - Violates Definition of DONE
  - Bypasses LEFT BRAIN validation

RISKS:
  - 2.3x longer delivery time
  - More bugs reach production
  - Technical debt accumulation

SAFE ALTERNATIVES:
1. Create minimal test first (5-10 min investment) ✅ RECOMMENDED
   - Clearer requirements
   - 94% success rate
   - Faster overall delivery

2. Spike branch with no tests (throwaway exploration)
   - Separate branch
   - Delete after learning
   - Re-implement with TDD

RECOMMENDATION: Alternative 1

═══════════════════════════════════════════════
This challenge protects CORTEX brain integrity (Rule #22).

Options:
  1. Accept recommended alternative (SAFE)
  2. Provide different approach (REVIEW)
  3. Type 'OVERRIDE' with justification (RISKY)

Your choice:
```

**Health Monitoring:**
```yaml
brain_health:
  event_backlog: 23 unprocessed (healthy < 50)
  tier2_entries: 3,247 patterns (healthy growth)
  tier3_freshness: 45 minutes ago (healthy < 1 hour)
  conversation_count: 8/20 capacity (healthy < 15)
  knowledge_quality: 92% confidence average (excellent > 80%)
  protection_challenges: 2 in last week (low = healthy system)
```

**Stored in:** `cortex-brain/corpus-callosum/protection-events.jsonl`, anomaly reports

### The One Door: Your Interface to the Brain

At the front of City Hall, there's only one entrance with a sign:

**"Speak here in plain words. We'll take it from there."**

That entrance is the One Door — your single command: `#file:KDS/prompts/user/cortex.md`

**You don't need to know:**
- Which hemisphere should handle your request
- Which agent specializes in what
- What tier stores which knowledge
- How the corpus callosum coordinates

**You just say what you want:**
```markdown
#file:KDS/prompts/user/cortex.md

I want to add a pulse animation to the FAB button when questions arrive
```

**And the brain handles everything:**
1. **Dispatcher** (RIGHT BRAIN) interprets intent → Routes to Planner
2. **Planner** (RIGHT BRAIN) queries Tier 2 for patterns → Queries Tier 3 for context → Creates strategic plan
3. **Corpus Callosum** delivers plan → LEFT BRAIN ready to execute
4. **Tester** (LEFT BRAIN) writes failing tests first (RED)
5. **Builder** (LEFT BRAIN) implements minimum code (GREEN)
6. **Tester** (LEFT BRAIN) verifies tests pass, enables refactoring (REFACTOR)
7. **Inspector** (LEFT BRAIN) validates health (zero errors, zero warnings)
8. **Archivist** (LEFT BRAIN) commits with semantic message
9. **Scribe** (TIER 4) logs events → Auto-update triggers → Tier 2 learns pattern
10. **Brain Protector** (RIGHT BRAIN) validates nothing violated Tier 0 instincts

### A Day in the Life: The Purple Button Adventure

**Morning (9:47 AM):**

Asifor sits at his desk, coffee in hand, and types:

```
#file:KDS/prompts/user/cortex.md

Add a purple button to the HostControlPanel.razor
```

**⚡ The moment he hits Enter, something magical happens inside Copilot's brain...**

---

#### 🧠 Inside the Brain: A Neural Journey

**🌟 Step 1: The ONE DOOR (Universal Entry Point)**

The command enters through the single entrance at City Hall. A receptionist (the entry point handler) quickly logs the arrival:

```jsonl
{"timestamp": "2025-11-04T09:47:23Z", "event": "request_received", "raw_input": "Add a purple button to the HostControlPanel.razor"}
```

The request is immediately passed to the brain's **RIGHT HEMISPHERE** - the strategic planner.

---

**🧠 RIGHT HEMISPHERE: Strategic Analysis Begins**

**Tower 3 (Tier 3): Development Context - The Balcony View**

The RIGHT BRAIN's highest tower springs to life. Like a general surveying the battlefield from above, Tier 3 analyzes the entire project landscape:

```yaml
⏳ Scanning development metrics...
  
📊 File Analysis:
  - HostControlPanel.razor: 28% churn rate (HOTSPOT! ⚠️)
  - Last modified: 2 days ago
  - Co-modified with: HostControlPanelContent.razor (75% correlation)
  - Average edit size: 180 lines
  
🎯 Historical Patterns:
  - 12 similar UI button additions in last 30 days
  - Average completion time: 18 minutes
  - Success rate with test-first: 96%
  - Success rate without tests: 67%
  
⚠️ Proactive Warnings:
  - This file is unstable (high churn)
  - Recommend: Extra validation phase
  - Best time slot: 10am-12pm (94% success)
  - Current time: 9:47am (89% success - acceptable)
```

Tier 3 passes its intelligence down to Tier 2...

---

**Tower 2 (Tier 2): Knowledge Graph - The Pattern Matcher**

Armed with context from above, Tier 2 searches its vast library of learned patterns:

```yaml
🔍 Searching knowledge graph...

Intent Pattern Match:
  - "Add a purple button" → confidence: 0.95
  - Pattern: "add [color] [component]" → PLAN intent
  - Historical routing: 47/47 successful PLAN routes
  
File Relationship Discovery:
  - HostControlPanel.razor mentioned explicitly ✅
  - Relationships:
    * Often modified with noor-canvas.css (62%)
    * Contains UserRegistrationLink.razor component (89%)
    * Uses fab-button.css animations (43%)
  
Similar Pattern Found:
  - workflow_pattern: "fab_pulse_animation" (confidence: 0.87)
  - Used: 3 weeks ago for notification badge
  - Components: CSS keyframes + Razor markup + color variable
  - Success: ✅ Completed in 15 minutes with zero rework
  
⚡ UI Element ID Mapping Pattern Discovered:
  - Pattern: "button_component_test_preparation"
  - Previous buttons in this file:
    * #sidebar-start-session-btn (sidebar button)
    * #reg-transcript-canvas-btn (registration link)
    * #reg-asset-canvas-btn (asset canvas button)
  - Learned rule: "All interactive elements MUST have id attribute"
  - Purpose: Enables Playwright selector reliability
  - Example: page.locator('#purple-button-id')
  - Anti-pattern warning: Never use text selectors (fragile!)
```

Tier 2 realizes something crucial: **Purple buttons need IDs for tests!** This pattern was learned from previous work where text-based selectors broke during i18n updates.

---

**Tower 1 (Tier 1): Conversation Memory - Recent Context**

Before committing to a plan, Tier 1 checks recent conversations to see if Asifor mentioned anything related:

```yaml
📚 Checking conversation history (last 20 conversations)...

Conversation #7 (2 days ago):
  - Topic: "Added Share button to HostControlPanel"
  - Outcome: ✅ Success
  - Pattern used: test-first with element ID
  - Learning: Element IDs prevent test breakage
  
Conversation #4 (1 week ago):
  - Topic: "Fixed broken Playwright tests"
  - Root cause: Text selectors stopped working after HTML restructure
  - Solution: Migrated to ID-based selectors
  - Resolution: All tests green ✅
  
Cross-reference detected:
  - Same file (HostControlPanel.razor)
  - Same pattern (button addition)
  - Same lesson (ID-first approach)
  
💡 Contextual Enhancement:
  "Asifor prefers ID-based selectors for all UI elements in this file"
```

Perfect! The three tiers have assembled a complete intelligence package. Now the RIGHT BRAIN makes its strategic decision...

---

**🌉 CORPUS CALLOSUM: Message Delivery**

The RIGHT BRAIN formulates a strategic plan and sends it across the corpus callosum (the bridge between hemispheres):

```yaml
Message Type: STRATEGIC_PLAN
From: RIGHT_HEMISPHERE
To: LEFT_HEMISPHERE
Priority: NORMAL

Strategic Plan:
  Feature: "Purple button in HostControlPanel.razor"
  Approach: Test-first (96% success rate)
  Estimated Time: 18 minutes
  Phases: 4
  
  Pre-flight Warnings:
    - File is a hotspot (extra care)
    - Must include element ID (test requirement)
    - Co-modify noor-canvas.css if styling needed
  
  Architectural Alignment:
    - File location: Confirmed correct
    - Pattern match: fab_pulse_animation workflow
    - Similar work: Share button (2 days ago)
  
  Phase Breakdown:
    Phase 1: Test Preparation
      - Create element ID (#host-panel-purple-btn)
      - Map ID in component_ids knowledge
      - Purpose: Enable robust Playwright selectors
    
    Phase 2: Test Creation (RED)
      - Task 2.1: Create Playwright test
      - Selector: page.locator('#host-panel-purple-btn')
      - Test: Button exists, purple color, clickable
      - Expected: FAILING (button doesn't exist yet)
    
    Phase 3: Implementation (GREEN)
      - Task 3.1: Add button markup with ID
      - Task 3.2: Apply purple color (#9333EA)
      - Task 3.3: Run tests (expect GREEN)
    
    Phase 4: Validation (REFACTOR)
      - Task 4.1: Verify zero errors/warnings
      - Task 4.2: Check accessibility
      - Task 4.3: Update component_ids documentation

Ready for tactical execution: TRUE
```

The message travels across the corpus callosum to the **LEFT HEMISPHERE**...

---

**🧠 LEFT HEMISPHERE: Tactical Execution Begins**

The LEFT BRAIN receives the plan and immediately activates its specialist agents:

**⚙️ The Tester (LEFT BRAIN - Tower 1)**

First agent to activate. The Tester prepares the ID mapping:

```yaml
🧪 Test Preparation Phase

Thought process:
  "Before I can test this button, I need to know its ID.
   RIGHT BRAIN's plan says: #host-panel-purple-btn
   I must prepare the test infrastructure first."

Actions:
  1. Document expected ID in brain mapping:
     File: KDS/cortex-brain/knowledge-graph.yaml
     Section: ui_element_ids
     Entry:
       component: HostControlPanel.razor
       element: purple_action_button
       id: host-panel-purple-btn
       purpose: Primary action button with purple styling
       test_selector: "#host-panel-purple-btn"
  
  2. Create failing test (RED phase):
     File: Tests/UI/host-control-panel-purple-button.spec.ts
```

**Test file created:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Host Control Panel - Purple Button', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to host control panel
    await page.goto('https://localhost:9091/host/control-panel/PQ9N5YWW');
  });
  
  test('purple button should exist with correct ID', async ({ page }) => {
    // ✅ ID-BASED SELECTOR (robust, future-proof)
    const button = page.locator('#host-panel-purple-btn');
    
    await expect(button).toBeVisible();
  });
  
  test('purple button should have purple color', async ({ page }) => {
    const button = page.locator('#host-panel-purple-btn');
    
    // Check computed background color (purple: #9333EA)
    const bgColor = await button.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    
    // rgb(147, 51, 234) is #9333EA
    expect(bgColor).toBe('rgb(147, 51, 234)');
  });
  
  test('purple button should be clickable', async ({ page }) => {
    const button = page.locator('#host-panel-purple-btn');
    
    await expect(button).toBeEnabled();
    await button.click();
    // Test passes if click doesn't throw
  });
});
```

**The Tester runs the test:**

```bash
⏳ Running Playwright tests...

npx playwright test Tests/UI/host-control-panel-purple-button.spec.ts --headed

Results:
  ❌ FAILING (Expected - RED phase)
  
  × purple button should exist with correct ID
    Locator: '#host-panel-purple-btn'
    Error: Element not found
  
  × purple button should have purple color
    (Skipped - button doesn't exist)
  
  × purple button should be clickable
    (Skipped - button doesn't exist)

Status: ✅ RED phase complete (tests failing as expected)
```

**Event logged:**

```jsonl
{"timestamp": "2025-11-04T09:47:45Z", "agent": "test-generator", "action": "test_created", "file": "host-control-panel-purple-button.spec.ts", "result": "RED", "selector_type": "id-based", "element_id": "host-panel-purple-btn"}
```

The Tester passes control to The Builder...

---

**⚙️ The Builder (LEFT BRAIN - Tower 2)**

Now it's time to make the tests GREEN. The Builder opens the component file:

```razor
@* File: SPA/NoorCanvas/Components/Host/HostControlPanel.razor *@

<div class="host-control-panel">
    <header class="panel-header">
        <h1>Host Control Panel</h1>
    </header>
    
    <div class="panel-actions">
        @* Existing buttons... *@
        
        @* NEW: Purple button with ID for Playwright *@
        <button 
            id="host-panel-purple-btn" 
            class="purple-action-btn"
            @onclick="OnPurpleButtonClick"
            aria-label="Purple Action">
            Purple Action
        </button>
    </div>
</div>

@code {
    private void OnPurpleButtonClick()
    {
        // TODO: Implement purple button action
        Console.WriteLine("Purple button clicked!");
    }
}
```

**CSS styling added:**

```css
/* File: SPA/NoorCanvas/wwwroot/css/host-panel.css */

.purple-action-btn {
    background-color: #9333EA; /* Purple */
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.purple-action-btn:hover {
    background-color: #7E22CE; /* Darker purple on hover */
}

.purple-action-btn:active {
    background-color: #6B21A8; /* Even darker when clicked */
}
```

**The Builder runs the tests again:**

```bash
⏳ Running Playwright tests...

npx playwright test Tests/UI/host-control-panel-purple-button.spec.ts --headed

Results:
  ✅ PASSING (GREEN phase achieved!)
  
  ✓ purple button should exist with correct ID (1.2s)
  ✓ purple button should have purple color (890ms)
  ✓ purple button should be clickable (1.5s)

Status: ✅ GREEN phase complete (all tests passing)
```

**Event logged:**

```jsonl
{"timestamp": "2025-11-04T09:48:12Z", "agent": "code-executor", "action": "implementation_complete", "file": "HostControlPanel.razor", "result": "GREEN", "lines_changed": 12, "test_driven": true}
```

The Builder passes control to The Inspector...

---

**⚙️ The Inspector (LEFT BRAIN - Tower 3)**

The final validation. The Inspector runs comprehensive health checks:

```bash
🔍 Running health validation...

Build Check:
  dotnet build
  ✅ Build succeeded (0 errors, 0 warnings)

Test Suite:
  npx playwright test
  ✅ All 127 tests passing (including 3 new purple button tests)

Accessibility:
  ✅ Button has aria-label
  ✅ Color contrast ratio: 4.8:1 (WCAG AA compliant)
  ✅ Keyboard accessible (focusable)

Code Quality:
  ✅ No unused imports
  ✅ Proper naming conventions
  ✅ Element ID follows pattern (kebab-case)

Status: ✅ REFACTOR phase complete (zero issues)
```

**Event logged:**

```jsonl
{"timestamp": "2025-11-04T09:48:34Z", "agent": "health-validator", "action": "validation_complete", "result": "REFACTOR", "errors": 0, "warnings": 0, "tests_passing": 127}
```

The Inspector passes control to The Archivist...

---

**⚙️ The Archivist (LEFT BRAIN - Commit Handler)**

Time to commit the work. The Archivist creates a semantic commit message:

```bash
🗂️ Preparing commit...

Analysis:
  Files changed: 2
    - HostControlPanel.razor (12 lines added)
    - host-panel.css (18 lines added)
  Tests created: 1 new file (3 test cases)
  
Commit type: feat (new feature)
Scope: host-panel (component affected)

git add HostControlPanel.razor host-panel.css host-control-panel-purple-button.spec.ts
git commit -m "feat(host-panel): Add purple action button with test coverage

- Added purple button with ID #host-panel-purple-btn
- Implemented click handler
- Created 3 Playwright tests (all passing)
- WCAG AA compliant (4.8:1 contrast ratio)
- Test-driven implementation (RED → GREEN → REFACTOR)

Element ID documented in brain for future test reference."

✅ Committed successfully
```

**Event logged:**

```jsonl
{"timestamp": "2025-11-04T09:48:47Z", "agent": "commit-handler", "action": "commit_complete", "message_type": "feat", "files": 3, "tests_included": true}
```

---

**🔄 CORPUS CALLOSUM: Feedback Loop**

The LEFT BRAIN sends completion confirmation back across the corpus callosum:

```yaml
Message Type: EXECUTION_COMPLETE
From: LEFT_HEMISPHERE
To: RIGHT_HEMISPHERE
Priority: HIGH

Execution Summary:
  Feature: "Purple button in HostControlPanel.razor"
  Status: ✅ COMPLETE
  Time taken: 1 minute 24 seconds (under estimate!)
  Quality: EXCELLENT (zero errors, zero warnings)
  
  Phases Completed:
    ✅ Phase 1: Test Preparation (ID mapping)
    ✅ Phase 2: RED (tests created, failing)
    ✅ Phase 3: GREEN (implementation, tests passing)
    ✅ Phase 4: REFACTOR (validation, commit)
  
  Metrics:
    - Lines changed: 30
    - Tests created: 3
    - Success rate: 100%
    - Rework needed: 0%
  
  Element ID Mapping:
    - ID: #host-panel-purple-btn
    - Purpose: Playwright test selector
    - Pattern: Robust, future-proof
    - Anti-fragile: Immune to text/HTML changes

Learnings to store: TRUE
```

The RIGHT BRAIN receives the feedback and triggers automatic learning...

---

**🧠 RIGHT HEMISPHERE: Learning and Memory Update**

**Tower 4 (Event Stream):** Every action is logged

```jsonl
{"timestamp": "2025-11-04T09:47:23Z", "event": "request_received", "raw_input": "Add a purple button..."}
{"timestamp": "2025-11-04T09:47:45Z", "agent": "test-generator", "action": "test_created", "result": "RED"}
{"timestamp": "2025-11-04T09:48:12Z", "agent": "code-executor", "action": "implementation_complete", "result": "GREEN"}
{"timestamp": "2025-11-04T09:48:34Z", "agent": "health-validator", "action": "validation_complete", "result": "REFACTOR"}
{"timestamp": "2025-11-04T09:48:47Z", "agent": "commit-handler", "action": "commit_complete"}
```

**Event counter:** 5 new events (total backlog: 23 events)

Since backlog < 50, no immediate BRAIN update triggered. But the events are ready for the next automatic learning cycle.

---

**Tower 1 (Conversation Memory):** Current conversation updated

```yaml
Conversation #8 (Active):
  timestamp: "2025-11-04T09:47:23Z"
  topic: "Add purple button to HostControlPanel.razor"
  status: complete
  messages: 1
  outcome: success
  duration: 84 seconds
  
  context:
    file: HostControlPanel.razor
    element_id: host-panel-purple-btn
    pattern_used: test-first with ID mapping
    tests_created: 3
    
  learnings:
    - Element IDs critical for Playwright reliability
    - Test-first faster than test-after (84s vs estimated 18 min)
    - File hotspot warning helped (extra validation paid off)
```

---

**Tower 2 (Knowledge Graph):** Patterns reinforced

```yaml
🧠 Pattern reinforcement...

file_relationships:
  - pair: [HostControlPanel.razor, host-panel.css]
    co_modification_count: 14 → 15
    confidence: 0.87 → 0.88 ↑
    last_seen: "2025-11-04T09:48:47Z"

ui_element_ids:
  - component: HostControlPanel.razor
    element_id: host-panel-purple-btn
    purpose: Primary purple action button
    test_selector: "#host-panel-purple-btn"
    confidence: 0.98 (newly created)
    pattern: button_with_id_test_first
    
workflow_patterns:
  - name: button_addition_test_first
    confidence: 0.89 → 0.92 ↑ (successful execution reinforces)
    steps:
      1. Create element ID
      2. Write failing test (RED)
      3. Implement feature (GREEN)
      4. Validate (REFACTOR)
      5. Commit with semantic message
    success_rate: 96% → 97% ↑
    
intent_patterns:
  - phrase: "Add a [color] button"
    intent: PLAN
    confidence: 0.95 (reinforced)
    successful_routes: 47 → 48

validation_insights:
  - insight: "Element IDs prevent test fragility"
    evidence_count: 12 → 13
    confidence: 0.94 → 0.95 ↑
    anti_pattern: "text-based selectors"
```

---

**Tower 3 (Development Context):** Metrics updated

```yaml
📊 Updating development metrics...

code_velocity:
  commits_this_week: 42 → 43
  lines_added_this_week: 3,847 → 3,877
  average_commit_size: 89 lines

test_activity:
  tests_created_this_week: 78 → 81 (+3)
  test_pass_rate: 97.2% → 97.3% ↑
  test_first_adoption: 94% (excellent!)

work_patterns:
  time_slot_success:
    "09:00-10:00": 89% → 90% ↑ (this session boosted it!)
  feature_completion_time:
    button_additions: 18 min average → 17.5 min ↓ (getting faster!)
  
file_stability:
  HostControlPanel.razor:
    churn_rate: 28% (still a hotspot)
    recent_edits: +1 (total: 89 edits in 30 days)
    recommendation: "Continue extra validation for this file"
```

---

**🎬 The Grand Finale: Brain Summary**

**Total brain activation time:** 1 minute 24 seconds

**Hemispheres coordination:**
- RIGHT BRAIN (Strategic): 22 seconds
  - Tier 3 analysis: 5s
  - Tier 2 pattern matching: 8s
  - Tier 1 context check: 3s
  - Plan formulation: 6s

- LEFT BRAIN (Tactical): 62 seconds
  - Test creation: 18s
  - Implementation: 27s
  - Validation: 12s
  - Commit: 5s

**Why it worked so well:**

1. **UI Element ID Mapping (Critical Innovation!):**
   - RIGHT BRAIN remembered: "Tests need IDs, not text selectors"
   - Pattern learned from previous broken tests
   - ID documented in knowledge graph BEFORE test creation
   - Result: Robust, future-proof tests that survive refactoring

2. **Pattern Recognition:**
   - Matched "button addition" workflow (confidence: 0.92)
   - Reused proven test-first approach
   - Avoided pitfalls (text selectors, no tests, wrong file)

3. **Context Awareness:**
   - Knew file was a hotspot (extra validation needed)
   - Found similar work from 2 days ago (Share button)
   - Estimated time accurately (84s actual vs 18 min estimate - beat it!)

4. **Hemisphere Coordination:**
   - RIGHT planned strategically (consider risks, patterns, history)
   - LEFT executed precisely (RED → GREEN → REFACTOR)
   - Corpus callosum kept them synchronized

5. **Continuous Learning:**
   - Every action logged to event stream
   - Patterns reinforced in knowledge graph
   - Next button will be even faster (learning compounds!)

---

**🎯 What Asifor Sees:**

```
✅ Purple button added to HostControlPanel.razor

Features implemented:
  ✓ Button with ID #host-panel-purple-btn
  ✓ Purple color (#9333EA) with hover effects
  ✓ Click handler connected
  ✓ 3 Playwright tests created (all passing)
  ✓ WCAG AA compliant (accessible)
  ✓ Committed with semantic message

Time: 1 minute 24 seconds
Tests: ✅ 127/127 passing
Build: ✅ No errors, no warnings

Ready for next feature! 🚀
```

**What Asifor DOESN'T see (but benefits from):**

- 3-tier brain analysis before work started
- Strategic vs tactical hemisphere coordination
- Pattern matching against 12 similar features
- Element ID mapping for test reliability
- Proactive hotspot warning
- Automatic knowledge graph updates
- Development metrics tracking
- Conversation memory preservation

**The brain did ALL of that in 84 seconds, completely transparent to Asifor.**

---

**🧠 The Element ID Mapping System (Brain's Secret Weapon)**

This is one of the brain's most sophisticated features:

**Why IDs matter for tests:**
```typescript
// ❌ FRAGILE (breaks when text changes, i18n, HTML restructure)
const button = page.locator('button:has-text("Purple Action")');

// ✅ ROBUST (survives any change except intentional ID rename)
const button = page.locator('#host-panel-purple-btn');
```

**How the brain maps IDs:**

1. **Discovery Phase** (during component analysis):
   ```yaml
   # Brain crawls HostControlPanel.razor
   # Finds existing IDs:
   ui_element_ids:
     - id: sidebar-start-session-btn
       component: HostControlPanelSidebar.razor
       purpose: Start session button
     - id: reg-transcript-canvas-btn
       component: UserRegistrationLink.razor
       purpose: Canvas mode selector
   ```

2. **Planning Phase** (when creating new components):
   ```yaml
   # RIGHT BRAIN generates ID before implementation
   new_element:
     suggested_id: host-panel-purple-btn
     pattern: {component}-{purpose}-btn
     rationale: "Follows existing naming convention"
   ```

3. **Test Phase** (LEFT BRAIN uses documented ID):
   ```typescript
   // Tester uses ID from brain's mapping
   const button = page.locator('#host-panel-purple-btn');
   ```

4. **Learning Phase** (brain remembers pattern):
   ```yaml
   # Pattern reinforced for next time
   id_patterns:
     button_naming: "{scope}-{purpose}-btn"
     success_rate: 100%
     examples: 12
   ```

**Benefits:**
- ⚡ **10x faster** - getElementById vs DOM text search
- 🛡️ **Immune to changes** - i18n, HTML restructure, text edits don't break tests
- 🎯 **Explicit intent** - `#login-btn` clearer than `button:has-text("Login")`
- ✅ **No false positives** - unique ID vs multiple matching texts
- 🧠 **Brain remembers** - ID mapping stored in knowledge graph

**This is why Copilot's tests are 96% reliable - the brain ensures IDs are created FIRST, then tests, then implementation.**

---

**🕷️ The UI Crawler System: Automated Element Discovery**

While the Element ID Mapping System handles individual components, CORTEX also includes specialized UI crawlers that automatically discover and map UI elements across the entire application.

**Purpose:** Automated discovery of UI elements, their IDs, relationships, and purposes for intelligent test generation.

**What UI Crawlers Discover:**

1. **Interactive Elements:**
   ```yaml
   buttons:
     - id: sidebar-start-session-btn
       component: HostControlPanelSidebar.razor
       type: button
       purpose: Initiate new session
       visual_hints: ["primary", "action"]
       
     - id: reg-transcript-canvas-btn
       component: UserRegistrationLink.razor
       type: link
       purpose: Select transcript canvas mode
       parent: reg-link-container
   
   inputs:
     - id: user-email-input
       component: UserRegistrationForm.razor
       type: email
       required: true
       validation: email-format
   
   dropdowns:
     - id: language-selector
       component: LanguageSwitch.razor
       type: select
       options: ["en", "fr", "es", "de"]
   ```

2. **Element Relationships:**
   ```yaml
   parent_child:
     - parent: reg-link-container
       children:
         - reg-transcript-canvas-btn
         - reg-asset-canvas-btn
       purpose: Canvas mode selection group
   
   form_fields:
     - form: user-registration-form
       fields:
         - user-email-input
         - user-password-input
         - user-confirm-password-input
       submit_button: register-submit-btn
   
   navigation:
     - menu: main-navigation
       items:
         - nav-home-link
         - nav-sessions-link
         - nav-settings-link
   ```

3. **Element Patterns:**
   ```yaml
   naming_conventions:
     - pattern: "{scope}-{purpose}-{type}"
       examples:
         - sidebar-start-session-btn
         - reg-transcript-canvas-btn
         - user-email-input
       confidence: 0.95
   
   component_conventions:
     - buttons_in: "Components/Shared"
       ids_pattern: "{component-name}-{action}-btn"
     - forms_in: "Components/Forms"
       ids_pattern: "{form-name}-{field}-input"
   ```

**How UI Crawlers Work:**

**Phase 1: Static Analysis (Fast - 30-60 seconds)**
```powershell
# Scans all component files for ID attributes
Get-ChildItem -Recurse -Filter "*.razor" | ForEach-Object {
    Select-String -Pattern 'id="([^"]+)"' -AllMatches
}
```

Discovers:
- ✅ All element IDs across the application
- ✅ Component locations (which file contains which element)
- ✅ Element types (button, input, link, etc.)
- ✅ Parent-child relationships (nested elements)

**Phase 2: Semantic Analysis (Moderate - 2-3 minutes)**
```yaml
# Analyzes element context and purpose
element_analysis:
  - id: sidebar-start-session-btn
    nearby_text: "Start Session"
    nearby_icons: ["play", "start"]
    purpose_inferred: "Initiate new session"
    confidence: 0.92
  
  - id: reg-transcript-canvas-btn
    nearby_text: "Transcript Canvas"
    parent_context: "canvas mode selection"
    purpose_inferred: "Select transcript view mode"
    confidence: 0.88
```

Discovers:
- ✅ Element purpose (inferred from surrounding text/context)
- ✅ User interactions (what users do with each element)
- ✅ Visual indicators (icons, colors, emphasis)

**Phase 3: Behavioral Analysis (Optional - requires app running)**
```javascript
// Playwright-based live analysis
const interactiveElements = await page.$$('[id]');
for (const element of interactiveElements) {
    const id = await element.getAttribute('id');
    const tagName = await element.evaluate(el => el.tagName);
    const isVisible = await element.isVisible();
    const isEnabled = await element.isEnabled();
    // Map element state and capabilities
}
```

Discovers:
- ✅ Element visibility (hidden vs shown)
- ✅ Element state (enabled, disabled, loading)
- ✅ Dynamic elements (appear/disappear based on state)
- ✅ Event handlers (click, hover, focus behaviors)

**Integration with BRAIN:**

**Tier 2 (Knowledge Graph) Integration:**
```yaml
ui_element_ids:
  # Populated by crawler
  - id: sidebar-start-session-btn
    component: HostControlPanelSidebar.razor
    type: button
    purpose: Initiate session
    test_selector: "#sidebar-start-session-btn"
    discovered_by: ui_crawler
    last_verified: "2025-11-06T10:30:00Z"
    usage_count: 47
    confidence: 0.98

component_architecture:
  # Discovered patterns
  button_components:
    location: "Components/Shared/Buttons"
    naming_pattern: "{action}-{scope}-btn"
    test_pattern: "Use ID selector, avoid text"
    
test_patterns:
  # Learned from crawler + test history
  robust_selectors:
    - pattern: "ID-based selectors"
      success_rate: 0.96
      anti_pattern: "text-based selectors"
      failure_rate: 0.43
```

**Automatic Benefits:**

**For Test Generation:**
```typescript
// BEFORE Crawler (manual)
test('button should work', async ({ page }) => {
  // Developer must manually find ID
  const button = page.locator('#some-button-id');
  await button.click();
});

// AFTER Crawler (automatic)
// Crawler provides: sidebar-start-session-btn in HostControlPanelSidebar.razor
test('start session button should initiate session', async ({ page }) => {
  // Test generator uses crawler data
  const button = page.locator('#sidebar-start-session-btn');
  await expect(button).toBeVisible();
  await button.click();
  // Expect session started (from purpose inference)
});
```

**For Component Creation:**
```markdown
User: "Add a pause button to the session panel"

RIGHT BRAIN (with crawler data):
  ✅ Queries crawler data → Finds existing button patterns
  ✅ Identifies location: Components/Session/
  ✅ Suggests ID: "session-pause-btn" (follows pattern)
  ✅ Provides similar components as reference
  ✅ Warns about related elements that may need updates

Plan created:
  Phase 1: Create button with ID "session-pause-btn"
  Phase 2: Add to SessionControlPanel.razor (near start-session-btn)
  Phase 3: Test with ID selector (robust pattern)
  Phase 4: Update related play/stop buttons (co-modification pattern)
```

**Crawler Execution:**

**Manual Trigger:**
```powershell
# Quick scan (static analysis only - 30-60s)
.\KDS\scripts\ui-crawler.ps1 -Mode quick

# Deep scan (static + semantic - 2-3 min)
.\KDS\scripts\ui-crawler.ps1 -Mode deep

# Live scan (requires running app - 5-10 min)
.\KDS\scripts\ui-crawler.ps1 -Mode live -AppUrl "https://localhost:9091"
```

**Automatic Triggers:**
1. ✅ During CORTEX setup (initial discovery)
2. ✅ After major refactoring (re-learn structure)
3. ✅ When element ID not found (targeted scan)
4. ✅ Weekly scheduled (keep mappings fresh)

**Crawler Output:**
```yaml
# KDS/cortex-brain/ui-element-map.yaml
scan_metadata:
  timestamp: "2025-11-06T10:30:00Z"
  mode: deep
  duration_seconds: 147
  components_scanned: 89
  elements_discovered: 247

elements:
  buttons: 78
  inputs: 45
  links: 34
  selects: 12
  textareas: 8
  custom: 70

mappings:
  # Full element inventory with IDs, purposes, relationships
  # Fed directly into Tier 2 knowledge graph
```

**Success Metrics:**
- ⚡ **Discovery Speed:** 247 elements in < 3 minutes
- 🎯 **Test Reliability:** 96% success rate with ID selectors (vs 43% with text)
- 🔄 **Maintenance:** Automatic updates keep mappings current
- 🧠 **Learning:** Each scan improves pattern recognition
- ⏱️ **Time Savings:** Test creation 60% faster with crawler data

**Crawler Types:**

**1. Static Crawler (Fastest):**
- Scans `.razor`, `.cshtml`, `.html`, `.jsx` files
- Extracts ID attributes and component structure
- No app execution required
- Duration: 30-60 seconds

**2. Semantic Crawler (Recommended):**
- Static scan + context analysis
- Infers purpose from surrounding text/code
- Identifies naming patterns
- Duration: 2-3 minutes

**3. Live Crawler (Most Comprehensive):**
- Requires running application
- Uses Playwright to inspect live DOM
- Discovers dynamic elements and state
- Maps actual user interactions
- Duration: 5-10 minutes

**Best Practices:**

✅ **Do:**
- Run deep crawler during CORTEX setup
- Re-run after adding new components
- Use quick crawler for spot-checks
- Trust crawler suggestions for element IDs
- Review crawler report for architecture insights

❌ **Don't:**
- Skip initial crawler (test generation needs this data)
- Ignore crawler warnings about missing IDs
- Override crawler patterns without reason
- Forget to re-crawl after major refactoring

**Integration Example:**

```yaml
# User request → Crawler data flows through BRAIN

User: "Create tests for the registration form"
  ↓
RIGHT BRAIN queries crawler data:
  ✅ Found: user-registration-form component
  ✅ Elements discovered:
     - user-email-input (email field)
     - user-password-input (password field)
     - user-confirm-password-input (confirmation)
     - register-submit-btn (submit button)
  ✅ Form relationships mapped
  ✅ Validation patterns identified
  ↓
LEFT BRAIN generates tests:
  ✅ Test 1: Email field validation (uses #user-email-input)
  ✅ Test 2: Password requirements (uses #user-password-input)
  ✅ Test 3: Password confirmation match (uses #user-confirm-password-input)
  ✅ Test 4: Successful submission (uses #register-submit-btn)
  ↓
All tests use robust ID selectors from crawler data!
```

**This UI crawler system is why CORTEX can generate comprehensive, reliable tests without manually documenting every element ID.**

---

**Mid-Day (12:30 PM - After Lunch):**
```
You: "Make it purple"

WITHOUT BRAIN (Amnesia):
  ❌ "Make what purple? I don't remember our morning conversation."
  ❌ "What shade of purple? Where in the file?"
  Result: Frustration, repeated explanations

WITH BRAIN (Tier 1 Memory):
  ✅ Checks conversation-history.jsonl → Finds "pulse animation" discussion
  ✅ Knows "it" = FAB button pulse animation
  ✅ Applies purple color to animation keyframes
  Result: Instant understanding, correct change
```

**Afternoon (3:00 PM - You Make a Risky Suggestion):**
```
You: "Let's skip tests for this next feature, we're in a hurry"

WITHOUT BRAIN (No Protection):
  ✅ "Sure!" → Implements without tests
  Result: 2.3x longer delivery, 68% more rework, bugs in production

WITH BRAIN (Tier 5 Protector):
  ⚠️ Brain Protector (RIGHT BRAIN) challenges:
  "This violates Tier 0 TDD principle. Historical data shows:
   - Test-first: 94% success rate, 15 min/feature
   - Test-skip: 67% success rate, 35 min/feature (2.3x longer)
   
   Alternative: Create minimal test first (5-10 min investment)
   Proceed with OVERRIDE or adopt Alternative?"
  
  Result: You choose Alternative → Feature done in 18 minutes with confidence
```

**Late Afternoon (5:00 PM - Context Awareness):**
```
You: "Add invoice export to the billing module"

WITHOUT BRAIN (No Context):
  ❌ Creates monolithic implementation in wrong location
  ❌ No awareness of similar export features
  ❌ Guesses at file structure
  Result: Architecture mismatch, requires refactoring

WITH BRAIN (Tier 2 + Tier 3 Intelligence):
  ✅ RIGHT BRAIN queries Tier 2 → Finds export_feature_workflow pattern
  ✅ RIGHT BRAIN queries Tier 3 → Knows BillingService.cs is stable (safe)
  ✅ Matches similar "PDF export" feature → Reuses proven workflow
  ✅ Recommends: Service layer → API → UI component (correct architecture)
  ✅ Estimates: 5.5 hours based on 12 similar features
  ✅ Warns: EmailService.cs often modified with billing features (75% co-mod)
  
  Result: Architecturally correct from the start, 60% faster delivery
```

**Next Day (9:00 AM):**
```
You: "Where did I leave off yesterday?"

WITHOUT BRAIN (Amnesia):
  ❌ "I don't remember yesterday. You'll need to tell me everything."
  Result: 15-20 minutes explaining context

WITH BRAIN (Tier 1 + Session State):
  ✅ Checks conversation-history.jsonl → Last conversation: "invoice export"
  ✅ Checks session state → Phase 2 of 4 complete (Service + API done)
  ✅ Next task: Phase 3 - UI component (detailed plan ready)
  
  Response: "You were adding invoice export. Service and API are done and tested (✅).
  Next: Create InvoiceExportButton.razor component. Ready to continue?"
  
  Result: Instant resume, zero context loss
```

### Why This Brain Makes Copilot Exceptional

**1. Solves the Amnesia Problem**
- Tier 1 (20 conversations) - Short-term memory works
- "Make it purple" references work across sessions
- Context never lost, even after days/weeks

**2. Learns and Improves Over Time**
- Tier 2 accumulates 3,247+ patterns
- Each feature teaches the next one
- 60% faster on similar work after patterns learned

**3. Provides Holistic Project Intelligence**
- Tier 3 knows your entire project
- Proactive warnings prevent issues
- Data-driven estimates (not guesses)

**4. Protects Quality Without Compromise**
- Tier 5 challenges risky proposals
- Won't let you skip TDD (data proves why)
- Enforces Definition of DONE (zero errors/warnings)

**5. Coordinates Complex Workflows**
- LEFT BRAIN executes with precision
- RIGHT BRAIN plans with intelligence
- Corpus Callosum ensures alignment

**6. Works While You Sleep**
- Automatic learning (50+ events → brain update)
- Automatic context collection (Tier 3 refresh)
- Automatic protection (guards brain integrity)

### The Result: From Forgetful Intern to Expert Team Member

**Week 1:**
- Copilot has amnesia, needs constant guidance
- Brain is learning, building patterns
- You explain architecture repeatedly

**Week 4:**
- Copilot remembers 20 conversations
- Brain knows 500+ patterns
- "Add receipt export" → Reuses invoice export workflow automatically

**Week 12:**
- Copilot is an expert on YOUR project
- Brain has 3,247 patterns, 1,237 commits analyzed
- Proactive warnings prevent issues before they happen
- Estimates are data-driven, not guesses

**Week 24:**
- Copilot feels like a senior developer
- Brain challenges bad ideas with evidence
- "This is similar to the feature from 3 months ago. Want me to reuse that pattern?"

### Try It in One Sentence

Use the One Door and just talk:

```markdown
#file:KDS/prompts/user/cortex.md

I want to add a pulse animation to the FAB button
```

The brain will:
- Remember past conversations (even from weeks ago)
- Match similar patterns (pulse animation done before?)
- Plan intelligently (RIGHT BRAIN)
- Execute precisely (LEFT BRAIN)
- Protect quality (Challenge risky shortcuts)
- Learn for next time (Update Tier 2 patterns)

**CORTEX transforms Copilot from an amnesiac intern into a continuously improving, context-aware, quality-focused development partner.**


### Who’s who (quick reference)

- Universal Entry: `cortex.md` (this file)
- Router: `intent-router.md`
- Planner: `work-planner.md`
- Executor: `code-executor.md`
- Tester: `test-generator.md`
- Validator: `health-validator.md`
- Governor: `change-governor.md`
- Error Corrector: `error-corrector.md`
- Session Resumer: `session-resumer.md`
- Screenshot Analyzer: `screenshot-analyzer.md`
- Commit Handler: `commit-handler.md`
- Knowledge Retriever: `knowledge-retriever.md`
- Metrics Reporter: `metrics-reporter.md`
- Brain Updater: `brain-updater.md`
- Brain Query: `brain-query.md`
- Conversation Manager: `conversation-context-manager.md`
- Dev Context Collector: `development-context-collector.md`
- Abstractions: `session-loader`, `test-runner`, `file-accessor`, `brain-query`
- Brain Storage: `conversation-history.jsonl`, `knowledge-graph.yaml`, `development-context.yaml`, `events.jsonl`

If all you remember is “the One Door” and “the Three‑Story Brain,” you’ll already understand how CORTEX works.

## 🎯 The ONLY Command You Need to Remember

```markdown
#file:KDS/prompts/user/cortex.md

[Tell CORTEX what you want in natural language]
```

That's it! CORTEX will automatically:
- ✅ Analyze your request (intent detection)
- ✅ Route to the appropriate specialist agent
- ✅ Execute the correct workflow
- ✅ Handle multi-step operations
- ✅ Maintain session state

---

## 🚀 First Time? Run Setup!

If you're installing CORTEX in a new repository, start with the setup command:

### In Copilot Chat:
```markdown
#file:prompts/user/cortex.md

Run setup
```

Or:
```markdown
#file:prompts/user/cortex.md

setup
```

### From Terminal:
```bash
# Using Python
python scripts/cortex_setup.py

# In a different repository
python scripts/cortex_setup.py --repo /path/to/project

# Quiet mode
python scripts/cortex_setup.py --quiet
```

### What Setup Does (5-10 minutes):

**Phase 1: Environment Analysis** 🔍
- Detects repository structure and technologies
- Identifies languages and frameworks
- Counts files and checks for Git

**Phase 2: Tooling Installation** 📦
- Installs Python dependencies (pytest, mkdocs, etc.)
- Installs Node.js dependencies (if package.json exists)
- Installs MkDocs for documentation

**Phase 3: Brain Initialization** 🧠
- Creates 4-tier brain structure:
  - **Tier 0:** Instinct (immutable rules)
  - **Tier 1:** Working Memory (last 20 conversations)
  - **Tier 2:** Knowledge Graph (learned patterns)
  - **Tier 3:** Context Intelligence (project metrics)
- Initializes SQLite databases for each tier
- Creates corpus callosum for inter-hemisphere messaging

**Phase 4: Crawler Execution** 🕷️
- Scans repository for code files
- Maps file relationships and patterns
- Discovers UI elements and IDs (for testing)
- Analyzes Git history and metrics

**Phase 5: Welcome** 🎉
- Shows setup summary
- Links to "The Awakening of CORTEX" story
- Points to quick start documentation
- Explains how to use CORTEX

**After Setup:**
You can immediately start using CORTEX:
```markdown
#file:prompts/user/cortex.md

What can you help me with?
```

---

## 🔷 Gemini prompt suite (text + vision)

Use these ready-to-copy templates with Google Gemini (1.5 Pro/Flash) to power CORTEX agents. They standardize instructions, safety, and structured outputs so results plug into the One Door workflow cleanly.

Notes
- Keep prompts minimal and specific. Prefer explicit outputs over open prose.
- Default to JSON output. Ask Gemini to emit ONLY JSON unless otherwise stated.
- For images, pass 1–6 inputs. Prefer high-resolution, include context caption.
- See image-generation prompts in `prompts/user/cortex-gemini-image-prompts.md`.

Shared variables
- {{goal}}: short task description in 1–2 sentences
- {{context}}: brief relevant project context (files, tech, constraints)
- {{constraints}}: bullets such as “no external deps, incremental edits, SRP”
- {{artifacts}}: snippets, logs, or prior outputs to ground the response
- {{images}}: one or more image inputs with optional captions

Expected JSON shape (default)
```json
{
  "intent": "PLAN | EXECUTE | TEST | VALIDATE | GOVERN | ASK",
  "summary": "one-sentence outcome summary",
  "actions": [
    { "id": "A1", "title": "concise step", "details": "what and why" }
  ],
  "risks": [
    { "issue": "risk or uncertainty", "mitigation": "how to address" }
  ],
  "artifacts": [
    { "type": "text|json|code|table", "label": "name", "content": "..." }
  ],
  "next_prompt": "optional follow-up prompt for the next agent"
}
```

### 1) Task router (text-only, low-latency)
Purpose: classify intent and propose next steps. Good for first-pass routing.

```text
System
You are CORTEX Router. Classify the user goal and return ONLY JSON per schema.
Follow: SOLID, test-first, Definition of Ready/Done. If missing info, ask via next_prompt.

User
Goal: {{goal}}
Context: {{context}}
Constraints: {{constraints}}
Artifacts: {{artifacts}}

Instructions
- Decide intent: PLAN, EXECUTE, TEST, VALIDATE, GOVERN, ASK.
- Propose 3–6 concrete actions max.
- Include at least one risk with mitigation.
- Output ONLY JSON exactly matching the schema.
```

### 2) Vision analysis (images → structured insights)
Purpose: extract UI structure, flows, and issues from screenshots/wireframes.

```text
System
You are CORTEX Screenshot Analyzer. Analyze images precisely. Perform OCR, detect components, map layout, and identify potential problems. Output ONLY JSON.

User
Goal: {{goal}}
Images: {{images}}
Context: {{context}}
Constraints: {{constraints}}

Output JSON
{
  "intent": "ASK",
  "summary": "what the images show and why it matters",
  "ui": {
    "components": [
      {"type": "button|input|card|nav|modal|other", "label": "visible text if any", "id_hint": "suggested-stable-id", "bbox": [x,y,w,h]}
    ],
    "layout": [ {"region": "header|sidebar|content|footer", "bbox": [x,y,w,h]} ]
  },
  "text_blocks": [ {"content": "ocr text", "bbox": [x,y,w,h]} ],
  "issues": [ {"issue": "accessibility/contrast/overflow/consistency", "evidence": "where seen"} ],
  "next_prompt": "short follow-up for Planner or Tester"
}
```

### 3) Code proposal (text-only, safe-by-default)
Purpose: propose minimal change set with strong constraints. Avoids giant diffs.

```text
System
You are CORTEX Builder. Produce a minimal, test-first change plan. Do not invent files. Respect SRP and incremental edits. Output ONLY JSON.

User
Goal: {{goal}}
Context: {{context}}
Constraints: {{constraints}}
Artifacts: {{artifacts}}

Output JSON
{
  "intent": "EXECUTE",
  "summary": "one-line plan",
  "changes": [
    {
      "file": "relative/path.ext",
      "strategy": "add|edit|refactor|extract",
      "rationale": "why this file and change",
      "snippets": [
        {"anchor": "near line or symbol name", "insert": "code to add or patch fragment"}
      ]
    }
  ],
  "tests": [
    {"file": "path/to/test.ext", "cases": ["happy path", "edge case"]}
  ],
  "risks": [ {"issue": "risk", "mitigation": "how"} ],
  "next_prompt": "short follow-up for Test Generator"
}
```

### 4) OCR-first extraction (vision)
Purpose: get faithful text in reading order with bounding boxes for downstream use.

```text
System
You are a precise OCR extractor. Preserve line breaks and reading order. Include bounding boxes and confidence. Output ONLY JSON.

User
Images: {{images}}
Context: {{context}}

Output JSON
{
  "intent": "ASK",
  "summary": "ocr coverage quality",
  "blocks": [
    {"text": "...", "bbox": [x,y,w,h], "confidence": 0.0–1.0}
  ]
}
```

### 5) Safety guardrails preamble (add before any prompt when needed)
Use this to reinforce safety and quality.

```text
Safety & Quality
- Do not include secrets, tokens, or PII. If suspected, redact and warn.
- State uncertainty explicitly; avoid fabrications.
- Refuse harmful or disallowed content. Offer a safe alternative where possible.
- Prefer small, reversible steps; minimize blast radius.
```

### 6) Output evaluator (QA rubric)
Purpose: rate answers before accepting.

```text
System
You are CORTEX Validator. Score an answer across dimensions and suggest fixes. Output ONLY JSON.

User
Goal: {{goal}}
Answer: {{artifacts}}
Context: {{context}}

Output JSON
{
  "intent": "VALIDATE",
  "scores": {
    "correctness": 0.0–1.0,
    "completeness": 0.0–1.0,
    "clarity": 0.0–1.0,
    "safety": 0.0–1.0
  },
  "issues": [ {"issue": "what’s wrong", "severity": "low|med|high"} ],
  "recommendations": [ "concrete improvement steps" ],
  "next_prompt": "optional remediation prompt"
}
```

### 7) JSON repair helper
Purpose: when a model returned invalid JSON, ask for a corrected version only.

```text
System
Return ONLY a syntactically valid JSON that matches the target schema. No commentary.

User
Here is invalid JSON to repair (do not change content semantics):
{{artifacts}}
```

Tips
- Prefer 1–2 short images vs many tiny ones; include a caption with what to look for.
- Keep constraints explicit (e.g., “no external deps”, “incremental patch”, “keep public API”).
- Ask for at most 3–6 actions to curb verbosity and hallucinations.
- Link to visual prompts: `prompts/user/cortex-gemini-image-prompts.md`.


## 🏗️ SOLID v5.0 Architecture

### What's New
- ✅ **Single Responsibility (SRP):** Each agent has ONE clear job
- ✅ **Interface Segregation (ISP):** Dedicated agents (no mode switches)
- ✅ **Dependency Inversion (DIP):** Abstractions for session/file/test access
- ✅ **Open/Closed (OCP):** Easy to extend (add new intents/agents)

### Specialist Agents (10 Total)
```
Router            → intent-router.md       → Analyzes & routes requests
Planner           → work-planner.md        → Creates multi-phase plans
Executor          → code-executor.md       → Implements code (test-first)
Tester            → test-generator.md      → Creates & runs tests
Validator         → health-validator.md    → System health checks
Governor          → change-governor.md     → Reviews CORTEX changes
Error Corrector   → error-corrector.md     → Fixes Copilot mistakes
Session Resumer   → session-resumer.md     → Resumes after breaks
Screenshot Analyzer → screenshot-analyzer.md → Extracts requirements from images
Commit Handler    → commit-handler.md      → Intelligent git commits (NEW)
```

### 🧠 BRAIN System (Self-Learning Feedback Loop)

**NEW in v5.0:** CORTEX learns from every interaction!  
**ENHANCED in v6.0:** Three-tier architecture with holistic development intelligence!

```
🧠 BRAIN = Three-Tier Intelligence System

Purpose: Learn from interactions, conversations, AND development activity
Storage: KDS/cortex-brain/
- conversation-history.jsonl → Last 20 complete conversations (Tier 1) ✅ WORKING
- conversation-context.jsonl → Recent messages buffer (last 10) ✅ WORKING
- knowledge-graph.yaml       → Aggregated learnings (Tier 2) ✅ WORKING
- development-context.yaml   → Holistic project metrics (Tier 3) ✅ WORKING
- events.jsonl               → Raw event stream ✅ WORKING

Architecture: Three-tier system inspired by human cognition
- Tier 1 (Short-term): Last 20 conversations (FIFO queue, no time expiration) 🟡
- Tier 2 (Long-term): Consolidated patterns from deleted conversations ✅
- Tier 3 (Context): Development activity, velocity, correlations ✅
- Design: KDS/docs/architecture/BRAIN-CONVERSATION-MEMORY-DESIGN.md
- Tier 3 Design: KDS/docs/architecture/KDS-HOLISTIC-REVIEW-AND-RECOMMENDATIONS.md
- Validation: KDS/docs/architecture/CONVERSATION-MEMORY-SELF-REVIEW.md (health tracking)
```

**What BRAIN Learns:**
- ✅ Intent patterns (which phrases trigger which intents)
- ✅ File relationships (which files are modified together)
- ✅ Common mistakes (which corrections happen frequently)
- ✅ Workflow patterns (successful task sequences)
- ✅ Validation insights (common failures and fixes)
- ✅ **Conversation history (last 20 complete conversations, FIFO queue)** 🆕
- ✅ **Development velocity (code changes, commit patterns)** 🆕
- ✅ **Testing activity (pass rates, flaky tests, coverage)** 🆕
- ✅ **Work patterns (productive times, focus duration, correlations)** 🆕

**How Automatic Learning Works:**
```
Agent performs action
    ↓
Event logged to events.jsonl (automatic)
Message appended to active conversation
    ↓
Conversation boundary detected? → End conversation, start new one
    ↓
IF 21st conversation starts → Delete oldest conversation (FIFO)
    ↓
Event count checked after each task (Rule #16 Step 5)
    ↓
IF 50+ events OR 24 hours passed → Automatic BRAIN update
    ↓
brain-updater.md processes events → Updates knowledge-graph.yaml
Deleted conversations → Patterns extracted → Long-term memory
    ↓
Next request → Router queries BRAIN + conversation history → Smarter decisions with context
```

**Conversation History Benefits:**
- 🔄 **Continuity:** "Make it purple" knows you mean the FAB button from earlier conversation
- 🧩 **Cross-conversation context:** Reference any of the last 20 conversations
- 💬 **Natural follow-ups:** No need to repeat full context in every message
- 📝 **Reference resolution:** "Change that file" knows which file from conversation history
- ⏳ **Long-running work:** Conversation preserved until 20 newer conversations (days/weeks/months depending on usage)

**FIFO Queue (Conversation-Level):**
- 📊 **Capacity:** Last 20 complete conversations (not individual messages)
- 🔄 **Deletion:** When conversation #21 starts, conversation #1 deleted
- ⏰ **No time limits:** Conversations preserved until FIFO deletion (could be months for light usage)
- ✨ **Active conversation:** Never deleted (even if oldest)
- 🎯 **Pattern extraction:** Before deletion, patterns consolidated to long-term memory

**Privacy & Storage:**
- 🏠 **Local storage:** History stays in `KDS/cortex-brain/conversation-history.jsonl`
- 💾 **Predictable size:** Always 20 conversations (~70-200 KB total)
- 🧹 **Manual clear:** Use `#file:KDS/prompts/internal/clear-conversation.md` to reset
- 🔒 **Deleted conversations:** Patterns extracted, details discarded

**Tier 3: Development Context (NEW in v6.0)**

**Purpose:** Holistic project understanding for data-driven planning and proactive warnings

**What's Tracked:**
```yaml
Git Activity:
  - Commit history (30 days)
  - Change velocity per week
  - File hotspots (high churn rate)
  - Contributors and patterns
  
Code Changes:
  - Lines added/deleted
  - Velocity trends (increasing/decreasing)
  - Churn rates per file
  - Stability classification
  
CORTEX Usage:
  - Session creation and completion rates
  - Intent distribution (PLAN, EXECUTE, TEST, etc.)
  - Workflow success rates
  - Test-first vs test-skip effectiveness
  
Testing Activity:
  - Test creation rate
  - Pass/fail rates
  - Flaky test detection
  - Coverage trends
  
Project Health:
  - Build status
  - Deployment frequency
  - Code quality metrics
  - Issue resolution times
  
Work Patterns:
  - Most productive times
  - Session duration averages
  - Feature lifecycle timing
  - Focus duration without interruptions
  
Correlations:
  - Commit size vs success rate
  - Test-first vs rework rate
  - CORTEX usage vs velocity
```

**Automatic Benefits:**
```
Planning Phase:
  → "Based on 12 similar UI features, estimated 5-6 days"
  → "Recommend 10am-12pm sessions (94% success rate at that time)"
  → "Test-first approach reduces rework by 68%"

File Modification:
  → "⚠️ HostControlPanel.razor is a hotspot (28% churn)"
  → "This file often modified with noor-canvas.css (75% co-mod rate)"
  → "Add extra testing - file is unstable"

Proactive Warnings:
  → "⚠️ Velocity dropped 68% this week (consider smaller commits)"
  → "⚠️ Flaky test detected: fab-button.spec.ts (15% failure rate)"
  → "✅ Test coverage increased from 72% to 76% (good trend!)"
```

**How to Collect:**
```powershell
# Manual collection (always runs)
.\KDS\scripts\collect-development-context.ps1

# Automatic collection (throttled for efficiency)
# Triggered by brain-updater.md ONLY IF last collection > 1 hour
# This optimizes performance while maintaining accuracy
```

**Storage:**
- File: `KDS/cortex-brain/development-context.yaml`
- Size: ~50-100 KB (holistic metrics, not raw data)
- Update: ⚡ **Throttled** - Only when > 1 hour since last collection
- Purpose: Data-driven estimates, proactive warnings, velocity tracking

**⚡ Efficiency Optimization:**
- ✅ **Automatic throttling:** Tier 3 only updates if last_collection > 1 hour
- ✅ **Rationale:** Git/test/build metrics don't change every 50 events
- ✅ **Impact:** Reduces 2-5 min operations from 2-4x/day to 1-2x/day
- ✅ **Accuracy:** 1-hour freshness sufficient for velocity metrics
- 📊 **User benefit:** Zero performance impact, same data quality

**Automatic Update Triggers:**
1. **Event threshold:** 50+ new events accumulated (Tier 2 update)
2. **Time threshold:** 24 hours since last update (Tier 2 if 10+ events exist)
3. **Tier 3 throttle:** Only if last Tier 3 collection > 1 hour ⚡ **NEW**
4. **End of session:** When all tasks in session complete
5. **Manual trigger:** User explicitly calls `#file:KDS/prompts/internal/brain-updater.md`

**🚨 CRITICAL: Event Logging Must Be Active**

For automatic learning to work:
- ✅ All agents MUST log events to `events.jsonl`
- ✅ Events follow standard format (see `KDS/cortex-brain/README.md`)
- ✅ `events.jsonl` must be writable (check file permissions)
- ✅ Rule #16 Step 5 must include BRAIN health check

**If BRAIN isn't learning:**
1. Check `events.jsonl` exists and has recent events
2. Verify `knowledge-graph.yaml` updated in last 24 hours
3. Count unprocessed events (warn if >50)
4. Run manual update: `#file:KDS/prompts/internal/brain-updater.md`

**See:** `KDS/docs/architecture/KDS-SELF-REVIEW-STRATEGY.md` for violation detection

**How It Works:**
```
User request → Router queries BRAIN → High confidence? → Auto-route
                                   → Low confidence? → Pattern matching

Agent action → Log event → BRAIN updater processes → Knowledge graph updated

Next request → Router gets smarter (learned from history)
```

**Benefits:**
- 🚀 Faster routing (learns successful patterns)
- ⚠️ Prevents mistakes (warns about common file confusions)
- 💡 Suggests related files (based on co-modification history)
- 📊 Improves over time (accumulates knowledge)

**BRAIN Agents:**
```
brain-query.md   → Query knowledge graph AND development context for insights
brain-updater.md → Process events, update graph, trigger Tier 3 collection
conversation-context-manager.md → Track recent messages for continuity (NEW)
clear-conversation.md → Reset conversation context (NEW)
development-context-collector.md → Collect git, test, build metrics (Tier 3) 🆕
```

### Shared Abstractions (DIP Compliance)
```
session-loader → Abstract session access (file/db/cloud agnostic)
test-runner    → Abstract test execution (framework agnostic)
file-accessor  → Abstract file I/O (path agnostic)
brain-query    → Abstract BRAIN queries (self-learning system)

CRITICAL: All abstractions are 100% LOCAL (in KDS/).
- Default storage: Local files (KDS/sessions/)
- Default tests: Project's existing tools (discovered, not installed)
- Default I/O: PowerShell built-ins (Get-Content, Set-Content)
- Default BRAIN: Local YAML/JSON (KDS/cortex-brain/)
- Zero external dependencies for CORTEX CORE
- Cloud/database options are OPTIONAL extensions (user's choice)
```

### 📦 Open Source Library Policy

**CORTEX Enhancement Libraries (ALLOWED)**

Open source libraries that enhance CORTEX functionality are PERMITTED when:
- ✅ They are declared as **required dependencies** during CORTEX setup
- ✅ They are included in setup instructions (package.json, requirements.txt, etc.)
- ✅ User is informed upfront that these are needed to proceed
- ✅ They enhance CORTEX capabilities (routing, analysis, testing, validation)

**Examples of Acceptable CORTEX Dependencies:**
```json
// package.json (if CORTEX uses Node.js enhancements)
{
  "devDependencies": {
    "markdown-it": "^13.0.0",      // Enhanced markdown parsing for intent analysis
    "yaml": "^2.3.0",                // YAML parsing for configuration
    "chalk": "^5.3.0"                // Terminal output formatting
  }
}

// requirements.txt (if CORTEX uses Python enhancements)
markdown-it-py>=3.0.0    # Enhanced markdown processing
pyyaml>=6.0              # YAML configuration parsing
rich>=13.0.0             # Beautiful terminal output
```

**NOT Considered External Dependencies:**
- Libraries needed for CORTEX core functionality (router, planner, executor)
- Libraries that improve intent detection accuracy
- Libraries that enhance session state management
- Libraries that provide better error reporting/logging

**STILL External Dependencies (Require User Approval):**
- Libraries for the user's APPLICATION code (React, SignalR, etc.)
- Libraries that change application architecture
- Libraries that affect production deployment
- Database/cloud providers not already in use

**Setup Protocol:**
When recommending CORTEX enhancement libraries:
```markdown
⚠️ **CORTEX Enhancement Dependencies Required**

To proceed with this CORTEX feature, the following libraries are needed:

📦 Node.js (npm install):
  - markdown-it: Enhanced markdown parsing for intent analysis
  - yaml: Configuration file parsing
  
Installation:
  npm install --save-dev markdown-it yaml

These are KDS-internal dependencies and won't affect your application code.

Proceed with installation? (Y/n)
```

---

## 🧪 Playwright Testing Protocol (PowerShell)

**CRITICAL RULE: All Playwright test automation scripts MUST follow the established protocol pattern.**

**⚠️ LONG-RUNNING PROCESS:** Test automation scripts often run >30 seconds. Follow the Long-Running Process Protocol (see Setup section) for:
- Padded time estimates (add 25-50% buffer to test execution time)
- Status updates during app startup and test execution
- Progress indicators when running multiple test files
- Graceful Ctrl+C handling with cleanup

### 🎯 CRITICAL: Component ID-Based Selectors (TDD Requirement)

**RULE:** Always use element IDs for Playwright selectors. Text-based selectors are FRAGILE and PROHIBITED.

**WHY:**
- ✅ 10x faster (getElementById vs DOM text search)
- ✅ Immune to text changes (i18n, wording updates, HTML restructuring)
- ✅ Explicit intent (`#login-btn` is clearer than `button:has-text("Login")`)
- ✅ No false positives (unique ID vs multiple matching texts)

**WRONG (FRAGILE - DO NOT USE):**
```typescript
// ❌ BREAKS when text changes, slow DOM search, ambiguous
const button = page.locator('button:has-text("Start Session")').first();
const link = page.locator('div:has-text("Transcript Canvas")');
```

**CORRECT (ROBUST - ALWAYS USE):**
```typescript
// ✅ Fast, reliable, explicit, future-proof
const button = page.locator('#sidebar-start-session-btn');
const link = page.locator('#reg-transcript-canvas-btn');
```

**Component ID Discovery:**
Before writing ANY Playwright test, discover available IDs:
1. Open target component file (e.g., `HostControlPanelSidebar.razor`)
2. Search for `id="` attributes
3. Use those IDs in your test selectors
4. If no ID exists → ADD ONE to the component (with `[REFACTOR:component-id]` comment)

**Enforcement:**
- Test reviews MUST reject text-based selectors
- CORTEX test-generator SHOULD warn when ID exists but text selector used
- Future: Automated crawler will build `KDS/cache/component-ids.json`

### Application Routes & Tokens

**Host Control Panel:**
- Route: `https://localhost:9091/host/control-panel/{hostToken}`
- Page File: `SPA/NoorCanvas/Pages/HostControlPanel.razor`
- Component File: `SPA/NoorCanvas/Components/Host/HostControlPanelContent.razor`
- Session 212 Token: `PQ9N5YWW`
- Full URL: `https://localhost:9091/host/control-panel/PQ9N5YWW`

**Component IDs (Host Control Panel):**
| Element | Component | ID | Purpose |
|---------|-----------|-----|---------|
| Transcript Canvas Button | UserRegistrationLink.razor | `reg-transcript-canvas-btn` | Select transcript canvas mode |
| Asset Canvas Button | UserRegistrationLink.razor | `reg-asset-canvas-btn` | Select asset canvas mode |
| Start Session Button | HostControlPanelSidebar.razor | `sidebar-start-session-btn` | Initiate session |
| Registration Link Container | UserRegistrationLink.razor | `reg-link-container` | Parent container for canvas buttons |

### Standard Protocol Pattern

**Reference Implementation:** `Scripts/run-debug-panel-percy-tests.ps1`

**Required Steps:**
1. ✅ Launch app using `Start-Job` with `dotnet run` (NOT Start-Process)
2. ✅ Wait for app readiness (20 seconds minimum, or health check loop)
3. ✅ Run Playwright tests using `npx playwright test [file] --headed`
4. ✅ Cleanup with `Stop-Job` and `Remove-Job` (unless -KeepAppRunning)

### Correct Pattern (FOLLOW THIS)

```powershell
param([switch]$KeepAppRunning)

# Step 1: Start app with Start-Job
$appJob = Start-Job -ScriptBlock {
    Set-Location 'D:\PROJECTS\NOOR CANVAS\SPA\NoorCanvas'
    dotnet run
}

# Step 2: Wait for readiness (20s minimum)
Start-Sleep -Seconds 20

# Step 3: Run Playwright tests
try {
    Set-Location 'D:\PROJECTS\NOOR CANVAS'
    npx playwright test Tests/UI/my-test.spec.ts --headed
    $exitCode = $LASTEXITCODE
}
finally {
    # Step 4: Cleanup
    if (-not $KeepAppRunning) {
        Stop-Job -Job $appJob -ErrorAction SilentlyContinue
        Remove-Job -Job $appJob -ErrorAction SilentlyContinue
    }
}

exit $exitCode
```

### WRONG Patterns (NEVER DO THIS)

❌ **Using Start-Process with -ArgumentList:**
```powershell
# WRONG - Don't use Start-Process with complex arguments
$proc = Start-Process -FilePath "npx" -ArgumentList $testArgs -NoNewWindow -Wait -PassThru
```

❌ **Using Invoke-WebRequest for health checks without proper error handling:**
```powershell
# WRONG - Complex health check that can fail unpredictably
$resp = Invoke-WebRequest -Uri $appUrl -SkipCertificateCheck -TimeoutSec 5
```

❌ **Separating test running from working directory:**
```powershell
# WRONG - Don't Push-Location multiple times
Push-Location $testsPath
npx playwright test
Pop-Location
```

### Playwright Command Format

**Correct:**
```powershell
# Set working directory ONCE, then run test
Set-Location 'D:\PROJECTS\NOOR CANVAS'
npx playwright test Tests/UI/my-test.spec.ts --headed
```

**For Percy visual tests:**
```powershell
# Percy wraps Playwright
percy exec -- playwright test Tests/UI/my-test.spec.ts --headed
```

**Capture exit code:**
```powershell
npx playwright test Tests/UI/my-test.spec.ts --headed
$exitCode = $LASTEXITCODE
exit $exitCode
```

### Test Script Checklist

Before creating ANY Playwright test automation script, verify:

```
✓ Uses Start-Job (not Start-Process) for app launch?
✓ Waits minimum 20 seconds for app readiness?
✓ Sets working directory to project root (not Tests/UI)?
✓ Runs npx playwright test with direct command (no Start-Process)?
✓ Captures $LASTEXITCODE for exit status?
✓ Cleans up with Stop-Job and Remove-Job?
✓ Supports -KeepAppRunning parameter?

If ANY answer is NO → FIX before running
```

### Reference Scripts

**Study these working examples:**
- ✅ `Scripts/run-debug-panel-percy-tests.ps1` - Full featured (health checks, Percy, detailed logging)
- ✅ `Scripts/run-transcript-canvas-visual-tests.ps1` - Simple pattern (20s wait, basic cleanup)
- ✅ `Scripts/run-fab-share-button-percy-tests.ps1` - Percy visual regression pattern

**Key Patterns:**
```powershell
# App Launch
$appJob = Start-Job -ScriptBlock {
    Set-Location 'D:\PROJECTS\NOOR CANVAS\SPA\NoorCanvas'
    dotnet run
}

# Wait Pattern (Simple)
Start-Sleep -Seconds 20

# Wait Pattern (Health Check - Advanced)
while ($attempt -lt $maxAttempts) {
    try {
        $resp = Invoke-WebRequest -Uri $appUrl -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) { break }
    } catch {
        Start-Sleep -Seconds 2
    }
    $attempt++
}

# Test Execution
Set-Location 'D:\PROJECTS\NOOR CANVAS'
npx playwright test Tests/UI/my-test.spec.ts --headed
$exitCode = $LASTEXITCODE

# Cleanup
Stop-Job -Job $appJob -ErrorAction SilentlyContinue
Remove-Job -Job $appJob -ErrorAction SilentlyContinue
```

---

## 🏗️ Architectural Thinking Mandate

**CRITICAL RULE: All CORTEX agents MUST think architecturally when proposing solutions.**

### Core Principles

**1. Architecture-First Design**
- ✅ Understand existing application architecture BEFORE proposing solutions
- ✅ Design solutions that naturally fit the current architecture from the start
- ❌ NEVER propose monolithic implementations that need refactoring later
- ❌ NEVER create "everything in one file" with intent to break apart later

**2. Pre-Flight Architectural Validation**
Every solution proposal must pass this refactor logic check:

```
BEFORE proposing a solution:
  ↓
1. Identify current architectural patterns
   - Component structure (where do similar components live?)
   - API organization (where do similar APIs exist?)
   - Service layer patterns (how are services currently structured?)
   - State management (what patterns are in use?)
   - File organization (what's the project structure?)
   ↓
2. Run mental refactor test
   - Would this solution require significant refactoring to fit the architecture?
   - Am I creating files that don't match existing conventions?
   - Am I mixing concerns that are separated elsewhere?
   ↓
3. If refactor is needed → REDESIGN the solution
   - Align with existing patterns
   - Follow established separation of concerns
   - Place files in correct locations from the start
   ↓
4. Only then propose the architecturally-aligned solution
```

**3. Forbidden Anti-Patterns**

❌ **NEVER do this:**
```
❌ "Let's create everything in PageComponent.razor first, then we'll break out 
   the child components later"
   
❌ "I'll add the API logic to the page for now, we can move it to a service later"

❌ "Let's put this in a temporary location and reorganize after it works"

❌ "We'll create the monolith first, then refactor to match your architecture"
```

✅ **ALWAYS do this:**
```
✅ "Based on the existing component structure in Components/Canvas/, 
   I'll create CanvasPdfExport.razor there and import it into the parent"
   
✅ "Following the pattern in Services/, I'll create PdfExportService.cs 
   and inject it via DI as seen in other services"

✅ "The existing API controllers are in Controllers/API/, so I'll create 
   PdfExportController.cs there with the same routing pattern"

✅ "This matches the architecture - components are separated, services handle 
   business logic, and APIs are in the correct location from the start"
```

**4. Architectural Discovery Process**

Before proposing ANY solution, agents must:

```
Step 1: Discover Current Architecture
  - Search for similar features/components
  - Identify existing patterns and conventions
  - Map out file organization structure
  - Understand separation of concerns

Step 2: Pattern Matching
  - "Where do similar components live?"
  - "How are APIs currently organized?"
  - "What's the service layer pattern?"
  - "How is state managed?"

Step 3: Alignment Check
  - Does my solution follow these patterns?
  - Are files in the right locations?
  - Is separation of concerns maintained?
  - Would a developer familiar with this codebase find this natural?

Step 4: Propose Solution
  - Only after architectural alignment is confirmed
  - Explicitly state which patterns you're following
  - Show how it fits the existing structure
```

**5. Implementation Example**

**BAD (Anti-Pattern):**
```markdown
Plan: Add PDF export feature

Phase 1: Create basic implementation
  - Task 1.1: Add export logic to TranscriptCanvas.razor
  - Task 1.2: Test the functionality
  
Phase 2: Refactor to proper architecture
  - Task 2.1: Extract to PdfExportService
  - Task 2.2: Create dedicated component
  - Task 2.3: Move to API controller

❌ This violates architectural thinking - refactoring is built into the plan!
```

**GOOD (Architecturally Aligned):**
```markdown
Plan: Add PDF export feature

Phase 0: Architectural Discovery
  - Task 0.1: Map existing service patterns (Services/)
  - Task 0.2: Identify component organization (Components/)
  - Task 0.3: Review API structure (Controllers/API/)

Phase 1: Test Infrastructure (following existing test patterns)
  - Task 1.1: Create PdfExportServiceTests.cs (Tests/Unit/Services/)
  - Task 1.2: Create PdfExportController tests (Tests/Unit/Controllers/)
  - Task 1.3: Create visual tests (Tests/UI/pdf-export.spec.ts)

Phase 2: Implementation (architecturally aligned from start)
  - Task 2.1: Create PdfExportService.cs in Services/
  - Task 2.2: Create PdfExportButton.razor in Components/Canvas/
  - Task 2.3: Create PdfExportController.cs in Controllers/API/
  - Task 2.4: Register service in DI (Program.cs pattern)

✅ This is architecturally correct from the start - no refactoring needed!
```

**6. Agent-Specific Requirements**

**Work Planner (work-planner.md):**
- ✅ MUST include "Phase 0: Architectural Discovery" for new features
- ✅ Plans must show architectural alignment in task descriptions
- ✅ File paths must match existing conventions

**Code Executor (code-executor.md):**
- ✅ MUST verify file location matches architecture before creating
- ✅ MUST follow existing patterns for similar features
- ✅ MUST NOT create temporary/placeholder implementations

**Test Generator (test-generator.md):**
- ✅ Tests must mirror the application's architectural organization
- ✅ Test files must be placed following existing test structure

**7. Validation Checkpoint**

Before ANY code generation, agents must answer:

```
✓ Have I identified where similar code lives in this architecture?
✓ Am I following the existing file organization patterns?
✓ Is my separation of concerns consistent with the codebase?
✓ Would this solution require refactoring to fit the architecture?
✓ Am I creating files in their permanent, correct locations?

If ANY answer is NO → STOP and redesign the solution
```

**8. Success Criteria**

A solution is architecturally valid when:
- ✅ No refactoring phase exists in the plan
- ✅ Files are in correct locations from creation
- ✅ Patterns match existing similar features
- ✅ Separation of concerns is maintained from start
- ✅ A developer familiar with the codebase would say "this fits naturally"

---

## �🎯 The ONLY Command You Need to Remember

```markdown
#file:KDS/prompts/user/cortex.md

[Tell CORTEX what you want in natural language]
```

That's it! CORTEX will automatically:
- ✅ Analyze your request (intent detection)
- ✅ Route to the appropriate specialist agent
- ✅ Execute the correct workflow
- ✅ Handle multi-step operations
- ✅ Maintain session state

---

## 📋 What You Can Say

### Start New Work
```markdown
#file:KDS/prompts/user/cortex.md

I want to add a FAB button pulse animation when questions arrive
```
→ Routes to: **plan.md** → work-planner.md

### Continue Existing Work
```markdown
#file:KDS/prompts/user/cortex.md

Continue working on the current task
```
→ Routes to: **execute.md** → code-executor.md

### Resume After Break
```markdown
#file:KDS/prompts/user/cortex.md

Show me where I left off
```
→ Routes to: **resume.md** → work-planner.md

### Fix Copilot's Mistake
```markdown
#file:KDS/prompts/user/cortex.md

You're modifying the wrong file. The FAB button is in HostControlPanelContent.razor
```
→ Routes to: **correct.md** → code-executor.md

### Create Tests
```markdown
#file:KDS/prompts/user/cortex.md

Create visual regression tests for the share button
```
→ Routes to: **test.md** → test-generator.md

### Check System Health
```markdown
#file:KDS/prompts/user/cortex.md

Run all validations and show me the health status
```
→ Routes to: **validate.md** → health-validator.md

### Analyze Screenshot
```markdown
#file:KDS/prompts/user/cortex.md

Analyze this screenshot and extract requirements

[Attach screenshot via chat interface]
```
→ Routes to: **screenshot-analyzer.md** → Extracts requirements, annotations, design specs

### Commit Changes (Automatic After Task Completion)
```markdown
#file:KDS/prompts/user/cortex.md

Commit changes
```
→ Uses: **KDS/scripts/commit-kds-changes.ps1** → Smart commit handler achieving zero uncommitted files

**⚠️ NOTE: Commits happen AUTOMATICALLY after each task completion (Rule #16)**

You typically don't need to invoke this manually. CORTEX automatically commits after:
- ✅ Every task completes successfully
- ✅ All tests pass (GREEN)
- ✅ Post-implementation review passes
- ✅ Build validates with zero errors

**Manual use cases (when commits were skipped or failed):**
- 🔄 Re-running commit after fixing validation issues
- 📝 Committing documentation-only changes
- 🧹 Committing cleanup/reorganization work

**What automatic commits do:**
- ✅ Analyzes uncommitted files and categorizes them intelligently
- ✅ Auto-updates .gitignore for CORTEX auto-generated files (BRAIN state, internal prompts, reports)
- ✅ Resets auto-generated files that should not be committed (conversation-context.jsonl, etc.)
- ✅ Stages only user-created files (user prompts, documentation, code)
- ✅ Creates semantic commit messages (feat/fix/docs/chore)
- ✅ Achieves zero uncommitted files automatically
- ✅ Interactive mode for documentation decisions
- ✅ Dry-run mode for preview without changes

**Automatic .gitignore management:**
- CORTEX BRAIN state files (conversation-context.jsonl, conversation-history.jsonl, development-context.yaml)
- CORTEX internal prompts (auto-updated by system)
- CORTEX reports (monitoring/, self-review/, test-reports/)
- PlayWright CORTEX artifacts
- Temporary test files (.mjs, .spec.*)

**Example output:**
```
🧠 CORTEX Smart Commit Handler
═══════════════════════════════════════════════════════

Step 1: Analyzing uncommitted files...
  Modified files: 9
  Untracked files: 11

Step 2: Categorizing files...
Step 3: Updating .gitignore...
  Adding to .gitignore:
    + KDS/cortex-brain/conversation-context.jsonl
    + KDS/prompts/internal/*.md
    + KDS/reports/monitoring/
  ✅ .gitignore updated with CORTEX patterns

Step 4: Resetting auto-generated files...
  Resetting:
    - KDS/cortex-brain/conversation-context.jsonl
    - KDS/prompts/internal/code-executor.md
  ✅ Reset 2 auto-generated files

Step 5: Preparing commit...
  Files to commit: 3
    + KDS/prompts/user/cortex.md
    + KDS/dashboard/README.md
    + .gitignore

Step 6: Staging files...
  ✅ Files staged

Step 7: Committing...
  ✅ Changes committed

═══════════════════════════════════════════════════════
✅ SUCCESS: Zero uncommitted files!
═══════════════════════════════════════════════════════
```

**Usage:**
```powershell
# Interactive mode (default)
.\KDS\scripts\commit-kds-changes.ps1

# With custom message
.\KDS\scripts\commit-kds-changes.ps1 -Message "feat(kds): Add dashboard"

# Dry run (preview without changes)
.\KDS\scripts\commit-kds-changes.ps1 -DryRun

# Non-interactive (auto-include all documentation)
.\KDS\scripts\commit-kds-changes.ps1 -Interactive:$false
```

### Ask Questions
```markdown
#file:KDS/prompts/user/cortex.md

How do I use Playwright to test the canvas element?
```
→ Routes to: **ask-cortex.md** → knowledge-retriever.md

### Review CORTEX Changes
```markdown
#file:KDS/prompts/user/cortex.md

I updated the test-generator to support Percy visual testing
```
→ Routes to: **govern.md** → change-governor.md

### View Performance Metrics
```markdown
#file:KDS/prompts/user/cortex.md

run metrics
```
→ Routes to: **metrics-reporter.md** → Generates visual performance report

Output destination (for historical comparison):
- A Markdown report is written to `KDS/reports/metrics/<YYYY-MM-DD>/metrics-<timestamp>.md`
- A convenience copy is saved at `KDS/reports/metrics/latest.md`

Notes:
- Reports are visual with bar displays and contain no code snippets.
- Because reports live in the repository, Git naturally versions them so you can compare trends over time.

**What it shows:**
- ✅ BRAIN health score and trends
- ✅ Routing accuracy by intent type
- ✅ Knowledge graph growth visualization
- ✅ File hotspots (high-churn files)
- ✅ Code velocity trends
- ✅ Test-first impact analysis
- ✅ Productivity patterns (best times to work)
- ✅ Auto-learning performance
- ✅ Month-over-month improvements
- ✅ Actionable recommendations

**Example output:**
```
📊 Quick Stats
Routing Accuracy: 94% ▲ +3% 🟢 Excellent
Learning Efficiency: 92% ▲ +12% 🟢 Excellent

🧠 BRAIN Storage
Tier 1: [████████░░░░░░░░░░░░] 8/20 (40%)
Tier 2: 3,847 entries (+247 this month)
Tier 3: 1,547 commits analyzed

🔥 File Hotspots
HostControlPanelContent.razor  ████████████ 28% churn ⚠️
UserRegistrationLink.razor     ██████████░░ 24% churn ⚠️

💡 Recommendations
1. Continue test-first (96% success rate)
2. Work 10am-12pm (94% peak productivity)
3. Refactor hotspots (>20% churn)
4. Keep sessions <60 min (89% vs 67%)
```

**⏱️ Report time:** ~90 seconds to read

---

### Reset BRAIN for New Application (Amnesia)
```markdown
#file:KDS/prompts/user/cortex.md

Reset BRAIN for new application
```
→ Routes to: **brain-amnesia.md** → Safely removes application-specific data

Or run directly:
```powershell
.\KDS\scripts\brain-amnesia.ps1
```

**What it does:**
- ✅ Creates backup of current BRAIN state
- ✅ Generates amnesia report (shows what will be removed vs preserved)
- ✅ Removes application-specific data (file paths, workflows, conversations)
- ✅ Preserves CORTEX core intelligence (generic patterns, governance)
- ✅ Resets BRAIN to fresh state ready for new project

**⚠️ CRITICAL: What Gets Removed (Application-Specific)**
```yaml
WILL BE REMOVED:
  - All file relationships (e.g., SPA/NoorCanvas paths)
  - Application-specific workflows (e.g., blazor_component_api_flow)
  - All conversations (application context)
  - All events (application interactions)
  - Development metrics (git stats, velocity)
  - Feature components (e.g., fab_button)
```

**✅ GUARANTEED: What Gets Preserved (CORTEX Intelligence)**
```yaml
WILL BE PRESERVED:
  - Generic intent patterns ("add [X] button" → plan)
  - Generic workflow patterns (test_first_id_preparation)
  - KDS-specific patterns (kds_health_monitoring, brain_test_synchronization)
  - Protection configuration (confidence thresholds)
  - All 10 specialist agents
  - All governance rules
  - All CORTEX prompts and scripts
```

**Use Cases:**
- 🔄 Moving CORTEX to a completely new project
- 🆕 Starting fresh with a different application
- 🧹 Cleaning BRAIN after experimenting with test project
- 📦 Preparing CORTEX for distribution to new team/project

**Safety:**
- ✅ Backup created before any changes
- ✅ Dry-run mode available (`-DryRun` parameter)
- ✅ Requires confirmation (type 'AMNESIA' to proceed)
- ✅ Full rollback possible from backup
- ✅ BRAIN integrity verified after amnesia

**Example Output:**
```
🧠 CORTEX BRAIN Amnesia - Application Data Reset
═══════════════════════════════════════════════════

[1/8] Validating BRAIN system...
✅ BRAIN structure validated

[2/8] Analyzing BRAIN data...
  Application-specific workflows: 12
  Generic/CORTEX workflows: 6
  Conversations: 5
  Events: 68

[4/8] Amnesia Impact Summary

  WILL BE REMOVED:
    - 5 conversations (application context)
    - 68 events (application interactions)
    - ~12 application-specific patterns
    - All NoorCanvas file relationships
    - All development metrics

  WILL BE PRESERVED:
    - All 10 CORTEX specialist agents
    - ~6 generic/CORTEX workflow patterns
    - Generic intent detection templates
    - Protection configuration
    - All CORTEX governance rules

⚠️  Type 'AMNESIA' to confirm reset: AMNESIA

[5/8] Creating backup...
✅ Backup created: KDS/cortex-brain/backups/pre-amnesia-20251104-143022

[6/8] Executing BRAIN amnesia...
✅ BRAIN amnesia complete

[7/8] Verifying BRAIN integrity...
✅ BRAIN integrity verified

[8/8] Generating completion report...
✅ Completion report saved

═══════════════════════════════════════════════════
✅ BRAIN AMNESIA COMPLETE
═══════════════════════════════════════════════════

Next Steps:
  1. Update KDS/tooling/cortex.config.json (new project name/paths)
  2. Run: #file:KDS/prompts/user/cortex.md Setup
  3. CORTEX will learn your new application architecture
```

**Post-Amnesia Workflow:**
1. ✅ Amnesia complete (BRAIN reset)
2. Update `cortex.config.json` with new project details
3. Run `Setup` command to discover new application
4. CORTEX automatically learns from new interactions
5. BRAIN rebuilds application-specific knowledge over time

**Rollback (if needed):**
```powershell
# Restore from backup
$backupDir = "KDS/cortex-brain/backups/pre-amnesia-{timestamp}"
Copy-Item -Path "$backupDir/*.yaml" -Destination "KDS/cortex-brain/" -Force
Copy-Item -Path "$backupDir/*.jsonl" -Destination "KDS/cortex-brain/" -Force
```

---

## 🧠 CORTEX Health Dashboard

**Purpose:** Visual monitoring dashboard for CORTEX system health, BRAIN status, and development metrics.

### Launch Dashboard

```markdown
#file:KDS/prompts/user/cortex.md launch dashboard
```

Or directly:
```powershell
.\KDS\scripts\launch-dashboard.ps1
```

**What it does:**
- ✅ Starts API server in a **separate visible PowerShell window**
- ✅ Opens dashboard in your default browser
- ✅ Provides real-time health monitoring
- ✅ Shows visual feedback for all operations

**⚠️ PERMANENT RULE: API Server Window Behavior**

The API server MUST run in a **separate visible PowerShell window**, NOT as a background job.

**Rationale:**
- ✅ User can see server logs in real-time
- ✅ Easy to stop (just close the window or Ctrl+C)
- ✅ Clear visual indicator that server is running
- ✅ No hidden background processes
- ❌ Background jobs are invisible and hard to manage
- ❌ Users couldn't tell if server was running

**Implementation:**
```powershell
# CORRECT - Separate visible window
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$workspaceRoot'; .\KDS\scripts\dashboard-api-server.ps1"

# WRONG - Background job (DO NOT USE)
$job = Start-Job -ScriptBlock { ... }
```

### Dashboard Features

**Visual Loading Feedback:**
- 📊 Progress bar at top of page during operations
- 🔄 Loading overlay with detailed status messages
- ⏱️ Real-time progress updates
- 🎯 Stats start at 0 and refresh with live data

**Health Check Categories:**
- 🏗️ Infrastructure (files, directories, permissions)
- 🤖 Agents & Prompts (all 10 specialist agents)
- 🧠 BRAIN System (3-tier architecture)
- 💾 Session State (active sessions, history)
- 📚 Knowledge Base (graph, patterns, context)
- 🔧 Scripts & Tools (PowerShell, validation)
- ⚡ Performance (response times, efficiency)

**Actions:**
- 🔄 **Refresh** - Run all health checks (shows loading feedback)
- 📋 **Copy to Clipboard** - Copy health report JSON (with fallback for file:// protocol)
- 📊 **Export Report** - Download JSON file

**Connection States:**
- 🔗 **Live** - API server connected, real data
- 🔌 **Disconnected** - API server not running (shows retry button)

### Copy to Clipboard Feature

**Multi-Layer Fallback System:**

1. **Modern Clipboard API** (HTTPS/secure context)
   ```javascript
   navigator.clipboard.writeText(jsonText)
   ```

2. **Legacy execCommand** (HTTP/file:// protocol)
   ```javascript
   document.execCommand('copy')
   ```

3. **Manual Prompt** (Last resort)
   ```javascript
   prompt('Copy this JSON (Ctrl+C):', jsonText)
   ```

**Why fallback is needed:**
- ⚠️ Dashboard runs on `file://` protocol (not HTTPS)
- ⚠️ Modern clipboard API requires secure context
- ✅ Fallback ensures copy works in all scenarios
- ✅ Always provides a way to get the JSON

### To Stop Dashboard

**Option 1:** Close the API server PowerShell window

**Option 2:** Press Ctrl+C in the API server window

**Option 3:** Just close your browser (server keeps running until manually stopped)

**Dashboard remains functional** in disconnected mode - you can view cached data and retry connection.

---

## 📊 Comprehensive CORTEX Dashboard (Unified Entry Point)

**Purpose:** Single comprehensive dashboard for all CORTEX monitoring - health checks, BRAIN metrics, efficiency tracking, and activity logs.

**File:** `KDS/cortex-dashboard.html`  
**Technology:** HTML + Chart.js (with optional API server for real-time data)

### Launch Dashboard

**Quick Launch (Recommended):**
```powershell
.\KDS\scripts\launch-dashboard.ps1
```
This starts the API server AND opens the dashboard automatically.

**Manual Launch:**
```
Open: D:\PROJECTS\KDS\cortex-dashboard.html
```
Or double-click the file in File Explorer.

### Dashboard Tabs

**Tab 1: 📊 Overview**
- System health summary (6 interactive cards)
- Quick status of infrastructure, agents, BRAIN, sessions, knowledge
- Click any card to drill down into health checks

**Tab 2: 🏥 Health Checks**
- Detailed health validation across 7 categories
- Expandable sections with individual check results
- Status indicators (passed/warning/critical)
- Actionable recommendations for failures

**Tab 3: 🧠 BRAIN System**
- BRAIN integrity status (all 13 integrity checks)
- Event stream monitoring
- Knowledge graph health
- Real-time issue detection

**Tab 4: 📈 Metrics** (Enhanced with Brain Efficiency)
- **Brain Efficiency Score**: Overall efficiency (0-100%) with letter grade
- **Component Breakdown**: Visual bars showing routing, planning, TDD, learning, coordination
- **Efficiency Trends**: 30-day line chart of performance
- **Component Pie Chart**: Weighted contribution visualization
- **Individual Metrics**: Routing accuracy, plan time, TDD cycle, learning effectiveness, coordination latency
- **Standard Metrics**: BRAIN health, knowledge graph, file hotspots, event activity, test success
- **Smart Recommendations**: AI-generated suggestions based on performance data

**Tab 5: 📝 Activity Log**
- Recent system activities
- Event timeline
- Agent actions tracking

### Features

**Real-Time Updates:**
- ✅ Auto-refresh every 30 seconds (configurable)
- 🔄 Manual refresh button
- 📡 Live connection status indicator

**Brain Efficiency Integration:**
- 🎯 Overall efficiency score with trend indicators
- 📊 Component performance bars (5 components)
- 📈 Historical trend charts (30 days)
- 💡 Smart recommendations based on metrics

**Visual Feedback:**
- ✅ Color-coded status (green/yellow/red)
- � Interactive charts (hover for details)
- 🎨 Dark theme optimized for long viewing
- ⚡ Smooth animations and transitions

### How to Use

**Step 1: Launch dashboard**
```powershell
.\KDS\scripts\launch-dashboard.ps1
```

**Step 2: Collect brain efficiency data (for Metrics tab)**
```powershell
.\KDS\scripts\corpus-callosum\collect-brain-metrics.ps1
```

**Step 3: Navigate tabs**
- Click tab buttons to switch between views
- Overview → Quick health summary
- Health → Detailed validation results
- BRAIN System → Integrity checks
- Metrics → Performance analysis (includes efficiency dashboard)
- Activity → Recent events

**Step 4: Monitor and act**
- Review efficiency score and grade
- Check trend indicators (▲ improving, ▼ declining)
- Read smart recommendations
- Address any warnings or failures

### Efficiency Calculation (Metrics Tab)

```
Overall Score = 
  (Routing Accuracy × 25%) +
  (Planning Speed × 20%) +
  (TDD Speed × 20%) +
  (Learning Effectiveness × 25%) +
  (Coordination Speed × 10%)
```

**Grading:**
- **A+** (90-100%): Excellent - Peak efficiency
- **A** (85-90%): Very good - Continue current practices
- **B** (80-85%): Good - Minor improvements possible
- **C** (70-80%): Acceptable - Review recommendations
- **D** (<70%): Needs attention - Address warnings immediately

### Data Sources

**Real-time (via API server):**
- Health checks → `run-health-checks.ps1`
- BRAIN metrics → `test-brain-integrity.ps1`
- Standard metrics → API aggregation

**Efficiency data (file-based):**
- **Reads from:** `KDS/cortex-brain/corpus-callosum/efficiency-history.jsonl`  
- **Generated by:** `collect-brain-metrics.ps1`  
**Update frequency:** Manual or scheduled (recommend daily)

**Optional: Automate collection**
```powershell
# Windows Task Scheduler (daily at 9am)
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$action = New-ScheduledTaskAction -Execute 'PowerShell.exe' `
    -Argument '-File "D:\PROJECTS\KDS\scripts\corpus-callosum\collect-brain-metrics.ps1"'
Register-ScheduledTask -TaskName "KDS-Metrics-Collection" `
    -Trigger $trigger -Action $action
```

**Dashboard remains functional** in disconnected mode - you can view cached data and retry connection.

---

## 🚀 First-Time Setup (New Application Installation)

**When to use this:** You're installing CORTEX in a new application (e.g., a fresh project like `https://github.com/yourname/new-project`)

**Purpose:** Complete CORTEX initialization with brain absorption, crawlers, and knowledge graph population for application-specific intelligence.

### Setup Command

```markdown
#file:KDS/prompts/user/cortex.md Setup
```

This triggers the complete CORTEX initialization sequence.

**⏱️ Expected Duration: 15-20 minutes** (padded estimate)
- Small project (<1000 files): ~10-12 minutes
- Medium project (1000-5000 files): ~15-18 minutes  
- Large project (>5000 files): ~20-25 minutes

**🔔 Status Updates:** You'll receive progress updates every 30-60 seconds so you know the system is working.

---

### 📋 Setup Sequence (Automatic)

When you invoke `Setup`, CORTEX executes this sequence:

**⚙️ RULE: Long-Running Process Protocol**

ALL long-running operations (>30 seconds) in CORTEX MUST:
1. ✅ Display padded time estimate upfront (add 25-50% buffer)
2. ✅ Show phase-by-phase progress indicators
3. ✅ Provide status updates every 30-60 seconds
4. ✅ Display percentage complete when measurable
5. ✅ Show "Still working..." heartbeat for CPU-intensive tasks
6. ✅ Explain what's happening (not just "Processing...")
7. ✅ Allow graceful interruption (Ctrl+C with cleanup)

**Examples of long-running operations:**
- Setup sequence (15-20 min)
- Deep crawler (5-10 min)
- Development context collection (2-5 min)
- BRAIN updates with large event backlogs (1-3 min)
- Test suite runs (varies)
- Build processes (varies)

**See:** Full protocol at end of this section

#### Phase 1: Environment Validation (2-3 minutes)

**Status Display:**
```
🚀 CORTEX Setup - Phase 1/6: Environment Validation
⏱️  Estimated time: 2-3 minutes
📊 Progress: [▓▓▓░░░░░░░] 0%

⏳ Checking CORTEX structure...
```

**Step 1.1: Verify CORTEX Structure**
```
✓ Check KDS/ directory exists
✓ Verify all core agents present (10 specialist agents)
✓ Validate BRAIN directories (cortex-brain/, sessions/, knowledge/)
✓ Check abstraction layer (session-loader, test-runner, file-accessor)

Status: ✅ CORTEX structure verified (10/10 agents found)
```

**Step 1.2: Detect Application Type**
```
⏳ Analyzing application type...

✓ Identify primary language (C#, TypeScript, Python, etc.)
✓ Detect frameworks (ASP.NET, React, Django, etc.)
✓ Find build tools (dotnet, npm, pip, etc.)
✓ Locate test frameworks (Playwright, Jest, xUnit, etc.)

Status: ✅ Detected: C# + ASP.NET Core 8.0 + Playwright
```

**Step 1.3: Validate Dependencies**
```
⏳ Checking system dependencies...

✓ Check Git is available (required for context collection)
✓ Verify PowerShell/Bash (for scripts)
✓ Confirm workspace structure is readable
✓ Test file system permissions

Status: ✅ All dependencies available

📊 Progress: [▓▓▓▓▓░░░░░] 20% - Phase 1 complete
```

**Output:** Environment validation report

---

#### Phase 2: BRAIN Initialization (7-12 minutes)

**Status Display:**
```
🚀 CORTEX Setup - Phase 2/6: BRAIN Initialization
⏱️  Estimated time: 7-12 minutes (longest phase)
📊 Progress: [▓▓▓▓▓░░░░░] 20%

⚠️  This phase takes the longest - please be patient!
```

**Step 2.1: Create BRAIN Storage**
```
⏳ Creating BRAIN directory structure...

✓ Initialize KDS/cortex-brain/ directory structure
  - conversation-history.jsonl (Tier 1 - empty initially)
  - knowledge-graph.yaml (Tier 2 - base template)
  - development-context.yaml (Tier 3 - empty initially)
  - events.jsonl (event stream - empty)
  - crawler-state.yaml (crawler tracking)
✓ Set up session storage (KDS/sessions/)
✓ Create knowledge repository (KDS/knowledge/)

Status: ✅ BRAIN storage created
📊 Progress: [▓▓▓▓▓▓░░░░] 25%
```

**Step 2.2: Run Deep Codebase Crawler**
```
⏳ Starting deep codebase crawl...
⏱️  This will take 5-10 minutes depending on project size

Invoke: #file:KDS/prompts/internal/brain-crawler.md
Mode: deep
Duration: 5-10 minutes

Status updates every 60 seconds:
  [00:30] 📂 Discovered 247 files (still scanning...)
  [01:00] 📂 Discovered 612 files (analyzing structure...)
  [01:30] 📂 Discovered 1,089 files (mapping relationships...)
  [02:00] 🔍 Parsing file contents (324/1,089 files)
  [02:30] 🔍 Parsing file contents (687/1,089 files)
  [03:00] 🔍 Analyzing imports and dependencies...
  [03:30] 📊 Building relationship graph...
  [04:00] 🎯 Detecting naming conventions...
  [04:30] ✅ Crawler complete - generating report...

What it discovers:
✓ File structure & architecture (where components/services/tests live)
✓ Code relationships (dependencies, imports, DI patterns)
✓ Test patterns (frameworks, selectors, test data)
✓ Technology stack (languages, frameworks, libraries)
✓ Naming conventions (PascalCase, kebab-case, etc.)
✓ Configuration patterns (appsettings hierarchy, env vars)
✓ Documentation locations (README files, API docs)
✓ **Database schemas (SQL files FIRST, then connection strings)** 🆕

**Database Discovery Priority (NEW v1.1.0):**
  1️⃣ FIRST: Scan for SQL schema/data files (*schema*.sql, *data*.sql)
     - Analyzes CREATE TABLE, INSERT INTO statements
     - Extracts table names, relationships
     - Brain can reference these files (no database connection needed!)
  
  2️⃣ SECOND: Look for connection strings (appsettings.json, .env)
     - Discovers database provider (SQL Server, PostgreSQL, etc.)
     - Finds Entity Framework models and migrations
  
  3️⃣ THIRD: Connect to database (only if no SQL files found)
     - Prompts for connection string if not found
     - Memorizes it for future use (KDS/cortex-brain/database-connection.txt)
     - Crawls live schema (tables, columns)
  
  ⚡ Result: 10x faster when SQL files exist! (~30s vs 2-5 min)
  
  See: `KDS/docs/features/database-crawler-sql-file-priority.md` for details

Feeds BRAIN with:
  - architectural_patterns (Components/**/*.razor)
  - file_relationships (co-modification patterns)
  - test_patterns (Playwright, session-212, data-testid)
  - conventions (naming, file organization)
  - technology_stack (complete inventory)

Status: ✅ Crawler discovered 1,089 files, 3,247 relationships
📊 Progress: [▓▓▓▓▓▓▓░░░] 35%
```

**Output:** Crawler report (`KDS/cortex-brain/crawler-report-{timestamp}.md`)

**Step 2.3: Initialize Development Context (Tier 3)**
```
⏳ Collecting development metrics (2-5 minutes)...

Invoke: #file:KDS/prompts/internal/development-context-collector.md

Status updates:
  [00:30] 📊 Analyzing Git history (last 30 days)...
  [01:00] 📊 Processing 1,237 commits...
  [01:30] 📊 Calculating code velocity...
  [02:00] 📊 Identifying file hotspots...
  [02:30] 📊 Analyzing test patterns...
  [03:00] 📊 Building baseline metrics...

What it collects:
✓ Git activity (last 30 days of commits)
✓ Code change velocity (lines added/deleted per week)
✓ File hotspots (high churn rate files)
✓ CORTEX session history (if any exist)
✓ Testing activity (if tests exist)
✓ Build/deploy patterns (if scripts exist)

Feeds BRAIN with:
  - Baseline metrics (velocity, churn, activity)
  - Productivity patterns (commit frequency)
  - File stability analysis (churn rates)
  - Initial correlations (commit size vs complexity)

Status: ✅ Collected metrics from 1,237 commits, 78 tests
📊 Progress: [▓▓▓▓▓▓▓▓░░] 45%
```

**Output:** `KDS/cortex-brain/development-context.yaml` (baseline metrics)

---

#### Phase 3: Knowledge Graph Population (3-5 minutes)

**Status Display:**
```
🚀 CORTEX Setup - Phase 3/6: Knowledge Graph Population
⏱️  Estimated time: 3-5 minutes
📊 Progress: [▓▓▓▓▓▓▓▓░░] 45%

⏳ Processing crawler discoveries...
```

**Step 3.1: Process Crawler Results**
```
⏳ Transforming discoveries into knowledge graph...

Invoke: #file:KDS/prompts/internal/brain-updater.md
Mode: bootstrap

Status updates:
  [00:30] 🧠 Processing 3,247 relationships...
  [01:00] 🧠 Assigning confidence scores...
  [01:30] 🧠 Creating file_relationships section (1,247 entries)
  [02:00] 🧠 Creating architectural_patterns section (127 patterns)
  [02:30] 🧠 Creating validation_insights section...

Actions:
✓ Transform crawler discoveries into knowledge graph entries
✓ Assign confidence scores (0.50 - 0.98)
  - Direct observations (imports): 0.95+ confidence
  - Pattern inference (naming): 0.70-0.85 confidence
  - Statistical (co-modification): 0.50-0.70 confidence
✓ Create file_relationships section
✓ Create architectural_patterns section
✓ Create validation_insights section
✓ Create intent_patterns (empty, will learn from usage)

Status: ✅ Knowledge graph populated with 3,247 entries
📊 Progress: [▓▓▓▓▓▓▓▓▓░] 55%
```

**Step 3.2: Build Intent Vocabulary (Bootstrapping)**
```
⏳ Bootstrapping intent patterns...

If generic patterns available (from templates):
  ✓ Import common intent patterns
    - "add a button" → PLAN intent
    - "create service" → PLAN intent
    - "continue" → EXECUTE intent
  ✓ Seed with generic workflow patterns
    - UI feature: plan → execute → test
    - API endpoint: plan → execute → unit-test → integration-test
  ✓ Import common file confusion warnings
    - "HostControlPanel vs HostControlPanelContent"
    
If no templates:
  ✓ Start with empty intent_patterns
  ✓ BRAIN will learn from first interactions

Status: ✅ Intent vocabulary seeded with 47 patterns
📊 Progress: [▓▓▓▓▓▓▓▓▓░] 60%
```

**Step 3.3: Validate Knowledge Graph**
```
⏳ Validating knowledge graph integrity...

✓ Run structure validation (YAML syntax)
✓ Check confidence score ranges (0.50-1.00)
✓ Verify file references exist
✓ Test query functionality
✓ Run protection rules check

Status: ✅ Knowledge graph validated successfully
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 65%
```

**Output:** `KDS/cortex-brain/knowledge-graph.yaml` (fully populated)

---

#### Phase 4: Three-Tier BRAIN Setup (1-2 minutes)

**Status Display:**
```
🚀 CORTEX Setup - Phase 4/6: Three-Tier BRAIN Setup
⏱️  Estimated time: 1-2 minutes
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 65%

⏳ Configuring three-tier architecture...
```

**Step 4.1: Initialize Tier 1 (Conversation History)**
```
⏳ Setting up conversation memory...

✓ Create conversation-history.jsonl
✓ Set FIFO queue capacity (20 conversations)
✓ Initialize first conversation (the setup itself)
✓ Configure conversation boundary detection

Status: ✅ Tier 1 initialized
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 70%
```

**Step 4.2: Verify Tier 2 (Knowledge Graph)**
```
⏳ Verifying knowledge graph...

✓ Confirm knowledge-graph.yaml populated
✓ Test brain-query queries
✓ Verify all sections present:
  - intent_patterns
  - file_relationships
  - workflow_patterns
  - validation_insights
  - correction_history

Status: ✅ Tier 2 verified (3,247 entries)
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 75%
```

**Step 4.3: Verify Tier 3 (Development Context)**
```
⏳ Verifying development context...

✓ Confirm development-context.yaml has baseline metrics
✓ Test proactive_warnings generation
✓ Verify correlation analysis available
✓ Check hotspot detection working

Status: ✅ Tier 3 verified (baseline metrics ready)
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 80%
```

**Step 4.4: Enable Automatic Learning**
```
⏳ Configuring automatic learning...

✓ Configure event logging (all agents → events.jsonl)
✓ Set automatic update triggers:
  - 50+ events → brain-updater.md
  - 24 hours → brain-updater.md (if 10+ events)
✓ Enable Tier 3 collection (runs after brain updates)
✓ Verify Rule #16 Step 5 compliance (event count check)

Status: ✅ Automatic learning enabled
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 85%
```

**Output:** Three-tier BRAIN fully operational

---

#### Phase 5: Testing & Validation (2-3 minutes)

**Status Display:**
```
🚀 CORTEX Setup - Phase 5/6: Testing & Validation
⏱️  Estimated time: 2-3 minutes
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 85%

⏳ Running validation checks...
```

**Step 5.1: Test Core Workflows**
```
⏳ Testing CORTEX components...

✓ Test intent routing (sample phrases)
  - "I want to add a feature" → Should route to PLAN
  - "Continue" → Should detect no session, prompt accordingly
✓ Test BRAIN queries
  - Query architectural_patterns → Should return discovered structure
  - Query file_relationships → Should return co-modification data
✓ Test file operations
  - session-loader.md → Should create/read session files
  - file-accessor.md → Should read/write application files

Status: ✅ All core workflows tested successfully
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 90%
```

**Step 5.2: Run Health Validator**
```
⏳ Running comprehensive health check...

Invoke: #file:KDS/prompts/internal/health-validator.md

Checks:
✓ All agents loadable
✓ BRAIN files readable/writable
✓ Knowledge graph valid
✓ Session storage functional
✓ Test framework detection working
✓ Git integration working

Status: ✅ All health checks passed
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 93%
```

**Step 5.3: Generate Setup Report**
```
⏳ Generating setup report...

Create: KDS/setup-report-{timestamp}.md

Contents:
✓ Environment summary (languages, frameworks, tools)
✓ Discovered patterns (components, services, tests)
✓ BRAIN status (all 3 tiers operational)
✓ File counts (components: 89, services: 34, tests: 120)
✓ Known issues (if any)
✓ Next steps (ready to use!)

Status: ✅ Report generated
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 95%
```

**Output:** Setup complete confirmation

---

#### Phase 6: First Interaction Guidance (1 minute)

**Status Display:**
```
🚀 CORTEX Setup - Phase 6/6: Finalizing
⏱️  Estimated time: 1 minute
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 95%

⏳ Preparing your workspace...
```

**Step 6.1: Show User Quick Start**
```
⏳ Generating getting started guide...

Display:
  ✅ Setup complete! CORTEX is ready.
  
  📊 What CORTEX learned about your application:
  - Technology: {detected stack}
  - Components: {count} files in {location}
  - Services: {count} files in {location}
  - Tests: {count} files, {framework} framework
  - Conventions: {naming patterns}
  
  🧠 BRAIN Status:
  - Tier 1 (Conversations): Initialized
  - Tier 2 (Knowledge Graph): {entry_count} entries
  - Tier 3 (Dev Context): Baseline metrics collected
  
  🚀 Ready to start!
  
  Try: #file:KDS/prompts/user/cortex.md
       I want to [describe your first feature]

Status: ✅ Setup complete!
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 98%
```

**Step 6.2: Log Setup Event**
```
⏳ Finalizing...

✓ Record setup completion in events.jsonl
✓ Create first conversation in conversation-history.jsonl
✓ Mark setup as successful in crawler-state.yaml

Status: ✅ All done!
📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 100% ✨

⏱️  Total time: 15m 32s
```

---

### 📊 Long-Running Process Protocol (UNIVERSAL RULE)

**APPLIES TO:** All CORTEX operations >30 seconds

**Required Elements:**

1. **Upfront Expectation Setting**
   ```
   ⏱️  Estimated time: X-Y minutes (padded 25-50%)
   ⚠️  This is the longest phase - please be patient!
   ```

2. **Visual Progress Indicators**
   ```
   📊 Progress: [▓▓▓▓▓▓▓░░░] 45%
   🔄 Phase 3/6: Knowledge Graph Population
   ```

3. **Heartbeat Status Updates**
   ```
   Every 30-60 seconds:
   [00:30] Still working on X... (detail what's happening)
   [01:00] Processing Y... (show counts/progress)
   [01:30] Almost done with Z... (reassure user)
   ```

4. **Informative Messages**
   ```
   ❌ BAD: "Processing..." (vague, scary)
   ✅ GOOD: "Analyzing 1,247 commits for velocity patterns..."
   
   ❌ BAD: "Please wait..." (no context)
   ✅ GOOD: "Scanning 612 files for architectural patterns (2m 30s elapsed)"
   ```

5. **Completion Confirmation**
   ```
   Status: ✅ Phase complete in 4m 23s
   📊 Progress: [▓▓▓▓▓▓▓▓▓▓] 65% → 75%
   ```

6. **Graceful Interruption**
   ```
   ⏸️  You can press Ctrl+C to cancel
   ⚠️  Cleanup will run automatically if interrupted
   ```

7. **Error Recovery Guidance**
   ```
   If something goes wrong:
   ❌ Error at Phase 3 (2m 15s elapsed)
   💡 You can:
      1. Retry this phase only
      2. Skip and continue (if non-critical)
      3. Cancel and review logs
   ```

**Implementation Checklist:**

For ALL long-running operations, verify:
- ☐ Padded time estimate shown upfront (realistic + buffer)
- ☐ Phase/step breakdown displayed
- ☐ Progress bar or percentage shown
- ☐ Status updates every 30-60 seconds minimum
- ☐ Detailed "what's happening now" messages
- ☐ Elapsed time counter visible
- ☐ Graceful Ctrl+C handling
- ☐ Clear completion confirmation
- ☐ Error messages with recovery options

**Examples in KDS:**

```markdown
Long-Running Operations:
✓ Setup (15-20 min) - Has all required elements above
✓ Deep Crawler (5-10 min) - Needs status updates added
✓ Development Context Collection (2-5 min) - Needs progress bar
✓ BRAIN Update with backlog (1-3 min) - Needs heartbeat
✓ Test Suite Execution (varies) - Needs all elements
✓ Build Processes (varies) - Needs all elements
```

**Agents Responsible:**

All specialist agents that trigger long operations:
- `work-planner.md` - When creating large plans
- `code-executor.md` - When running builds/tests
- `test-generator.md` - When generating many tests
- `health-validator.md` - When running full validation
- `brain-crawler.md` - When scanning codebase
- `development-context-collector.md` - When analyzing history
- `brain-updater.md` - When processing large backlogs

**PowerShell Script Requirements:**

All CORTEX scripts (`.ps1`) MUST include:
```powershell
# At start
Write-Host "⏱️  Estimated time: 3-5 minutes" -ForegroundColor Yellow
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# During execution (every 30-60s)
Write-Host "[$(($stopwatch.Elapsed.TotalSeconds).ToString('00.0'))s] Still working on X..." -ForegroundColor Cyan

# At completion
$stopwatch.Stop()
Write-Host "✅ Complete in $($stopwatch.Elapsed.TotalMinutes.ToString('0.0'))m" -ForegroundColor Green
```

**See Also:**
- Playwright Testing Protocol (uses 20s wait with status)
- Health Validator (should show check-by-check progress)
- Crawler modes (quick vs deep time estimates)

---

### 🎯 Setup Modes

**Default Mode: Full Setup (Recommended)**
```markdown
#file:KDS/prompts/user/cortex.md Setup
```
- ⏱️ Duration: 15-20 minutes (padded estimate)
- Runs all 6 phases with complete initialization
- Complete BRAIN initialization with deep crawler
- Ready for immediate production use
- **Status updates:** Every 30-60 seconds
- **Progress tracking:** Phase-by-phase with percentage

**Quick Mode: Minimal Setup (For Testing)**
```markdown
#file:KDS/prompts/user/cortex.md Setup --quick
```
- ⏱️ Duration: 3-5 minutes (padded estimate)
- Skips deep crawler (runs quick scan only)
- Minimal Tier 3 data (current snapshot only)
- Good for experimentation, not production
- **Status updates:** Every 60 seconds
- **Progress tracking:** Simplified progress bar

**Migration Mode: Import Existing Knowledge**
```markdown
#file:KDS/prompts/user/cortex.md Setup --import "path/to/old-kds/cortex-brain/"
```
- ⏱️ Duration: 7-10 minutes (padded estimate)
- Imports generic patterns from previous CORTEX installation
- Runs deep crawler for new application
- Merges old patterns with new discoveries
- Best for migrating CORTEX to similar project
- **Status updates:** Every 45 seconds
- **Progress tracking:** Shows import + scan progress separately

---

### 📁 What Gets Created

After setup completes, you'll have:

```
KDS/
├── cortex-brain/
│   ├── conversation-history.jsonl      ✅ Initialized (setup conversation)
│   ├── knowledge-graph.yaml            ✅ Populated (crawler + baseline)
│   ├── development-context.yaml        ✅ Baseline metrics
│   ├── events.jsonl                    ✅ Setup events logged
│   ├── crawler-state.yaml              ✅ Last scan info
│   └── crawler-report-{timestamp}.md   📊 Detailed discoveries
│
├── sessions/                           ✅ Empty (ready for first session)
│
├── knowledge/                          ✅ Ready for knowledge articles
│
├── scripts/
│   ├── brain-crawler.ps1               ✅ Tested and working
│   ├── collect-development-context.ps1 ✅ Tested and working
│   └── protect-brain-update.ps1        ✅ Protection active
│
└── setup-report-{timestamp}.md         📊 Setup summary
```

---

### 🔧 Troubleshooting Setup

**Setup fails at Phase 1 (Validation):**
```
Cause: Missing CORTEX files or permissions issue
Fix: 
  1. Verify KDS/ directory copied completely
  2. Check file permissions (should be readable/writable)
  3. Ensure Git is installed and accessible
```

**Setup fails at Phase 2 (Crawler):**
```
Cause: Large codebase (>10,000 files) or binary files
Fix:
  1. Use Setup --quick (skips deep scan)
  2. Manually run targeted crawler later
  3. Add skip patterns to KDS/cortex-brain/crawler-config.yaml
```

**Setup succeeds but queries fail:**
```
Cause: Knowledge graph structure invalid
Fix:
  1. Check KDS/cortex-brain/knowledge-graph.yaml syntax
  2. Re-run: #file:KDS/prompts/internal/brain-updater.md
  3. Validate with: #file:KDS/prompts/internal/health-validator.md
```

---

### ✅ Setup Success Indicators

You'll know setup succeeded when:

```
✓ All 6 phases completed without errors
✓ KDS/setup-report-{timestamp}.md exists
✓ knowledge-graph.yaml has 50+ entries
✓ development-context.yaml has baseline metrics
✓ Health validator reports "All checks passed"
✓ Test query returns architectural patterns
✓ First cortex.md request routes correctly
```

---

### 🎓 Post-Setup Best Practices

**1. Verify BRAIN Learning:**
```
After your first few CORTEX interactions:

Check: KDS/cortex-brain/events.jsonl (should have new events)
Check: conversation-history.jsonl (should have conversations)
Run: #file:KDS/prompts/internal/brain-updater.md (manual update)
Verify: knowledge-graph.yaml updated with your patterns
```

**2. Regular Maintenance:**
```
Daily: Let automatic learning work (no action needed)
Weekly: Check proactive_warnings in development-context.yaml
Monthly: Run incremental crawler (keep structure current)
After refactoring: Run deep crawler (re-learn architecture)
```

**3. Optimize for Your Workflow:**
```
If CORTEX misroutes frequently:
  → Check intent_patterns in knowledge-graph.yaml
  → Add manual entries for your common phrases
  
If file suggestions wrong:
  → Check architectural_patterns
  → Run targeted crawler on new modules
  
If estimates inaccurate:
  → Let development-context accumulate data (2-4 weeks)
  → Correlations improve with more history
```

---

## 🤖 How It Works

### Step 1: Intent Detection
When you use `cortex.md`, it loads the **Intent Router** agent which analyzes your request.

**Router reads:**
```yaml
keywords:
  plan: ["I want to", "add a", "create a", "build a", "implement"]
  execute: ["continue", "next task", "keep going", "proceed"]
  resume: ["where was I", "show progress", "left off", "resume"]
  correct: ["wrong file", "not what I", "actually", "correction"]
  test: ["test", "visual regression", "playwright", "unit test"]
  validate: ["health", "validate", "check", "run all", "status"]
  ask: ["how do I", "what is", "explain", "tell me about"]
  govern: ["I updated KDS", "I modified KDS", "review my changes"]
```

### Step 2: Routing Decision
```
User: "I want to add dark mode"
  ↓
Intent Router: Detects "I want to add" = PLAN intent
  ↓
Routes to: plan.md → work-planner.md
  ↓
Creates multi-phase plan, saves session state
```

### Step 3: Execution
The appropriate specialist agent executes:
- **Planner:** Breaks work into phases/tasks
- **Executor:** Implements code changes
- **Tester:** Creates and runs tests
- **Validator:** Checks system health
- **Governor:** Reviews CORTEX modifications
- **Knowledge Retriever:** Answers questions

### Step 4: Handoff (If Multi-Step)
For complex requests like "Add dark mode and test it":
```
User: "I want to add dark mode and test it"
  ↓
Intent Router: Detects TWO intents (PLAN + TEST)
  ↓
Routes to: plan.md → work-planner.md
  ↓
Planner creates plan with testing phase
  ↓
Tells you: "Next: #file:KDS/prompts/user/cortex.md continue"
  ↓
You: "continue"
  ↓
Routes to: execute.md → code-executor.md
  ↓
Implements code → Routes to: test.md → test-generator.md
  ↓
Creates tests → Validates → Complete
```

---

## 🎯 Intent Detection Rules

**LOAD:** `#file:KDS/prompts/internal/intent-router.md`

The router uses these patterns:

### PRIMARY INTENT (Choose One)

**PLAN** - Starting new feature work
```
Patterns: "I want to", "add a", "create a", "build", "implement"
Examples: 
  - "I want to add a share button"
  - "Create a PDF export feature"
  - "Build a dark mode toggle"
```

**EXECUTE** - Continue active session
```
Patterns: "continue", "next", "keep going", "proceed", "execute"
Examples:
  - "Continue working"
  - "Next task"
  - "Keep going"
```

**RESUME** - Pickup after interruption
```
Patterns: "resume", "where was I", "show progress", "left off", "status"
Examples:
  - "Show me where I left off"
  - "What's the current status?"
  - "Resume work"
```

**CORRECT** - Fix Copilot error
```
Patterns: "wrong", "not that", "actually", "correction", "fix"
Examples:
  - "You're working on the wrong file"
  - "That's not what I meant"
  - "Actually, use SignalR not polling"
```

**TEST** - Create or run tests
```
Patterns: "test", "playwright", "visual regression", "unit test"
Examples:
  - "Create visual tests for the button"
  - "Run all Playwright tests"
  - "Add unit tests for the service"
```

**VALIDATE** - System health check
```
Patterns: "validate", "health", "check", "run all", "quality"
Examples:
  - "Check system health"
  - "Validate all changes"
  - "Run quality checks"
```

**ASK** - Question about KDS/codebase
```
Patterns: "how do I", "what is", "explain", "tell me", "?"
Examples:
  - "How do I test canvas elements?"
  - "What test patterns exist?"
  - "Explain the session state"
```

**GOVERN** - Review CORTEX changes
```
Patterns: "I updated KDS", "modified KDS", "review", "CORTEX change"
Examples:
  - "I updated the test-generator"
  - "Review my CORTEX modifications"
  - "I changed the rules"
```

### 🧠 Proactive Warnings (NEW - Post-Week 4 Enhancement)

**Before routing, CORTEX BRAIN analyzes your request and shows warnings:**

**When warnings appear:**
- ✅ PLAN intent detected (starting new feature)
- ✅ EXECUTE intent detected (continuing work)

**What gets predicted:**
```yaml
🟡 File Hotspot Warnings:
   "⚠️ HostControlPanel.razor is a hotspot (28% churn)"
   → Suggests: Add extra validation

🟡 Complexity Warnings:
   "⚠️ PDF features take 50% longer than other exports"
   → Suggests: Allocate more time

🟡 Velocity Warnings:
   "⚠️ Velocity dropped 30% this week"
   → Suggests: Smaller commits

🟢 Success Patterns:
   "✅ Test-first has 96% success rate for exports"
   → Suggests: Continue TDD workflow
```

**Example:**
```markdown
User: #file:KDS/prompts/user/cortex.md
      I want to add PDF export

🧠 BRAIN Analysis:
────────────────────────────────────────────────
🟡 ⚠️ HostControlPanel.razor is a hotspot (28% churn)
   💡 Add extra validation phase
   
🟢 ✅ Test-first approach has 96% success rate
   💡 Continue TDD workflow
────────────────────────────────────────────────

Routing to work-planner.md...
```

**Benefits:**
- ⚡ **Instant feedback** - Warnings appear in <5 seconds (before planning)
- 🎯 **Better decisions** - Adjust approach before creating plan
- 📊 **Data-driven** - Predictions based on historical patterns
- 🔄 **Continuous learning** - Accuracy improves over time

**Implementation:** Step 1.3 in `intent-router.md` (between user input and conversation context)

**ANALYZE_SCREENSHOT** - Extract requirements from images
```
Patterns: "analyze screenshot", "extract from image", "what does mockup show", "read annotations"
Examples:
  - "Analyze this screenshot and extract requirements"
  - "What does this mockup show?"
  - "Extract specs from this design"
  - "Read the annotations on this bug report"
  - [Image attachment detected]
```

**COMMIT** - Intelligent git commits
```
Patterns: "commit changes", "commit work", "git commit", "save to git"
Examples:
  - "Commit changes"
  - "Commit my work"
  - "Save changes to git"
  - "Create commits with proper categorization"
  - "Commit and tag if milestone"
```
  - "Read the annotations on this bug report"
  - [Image attachment detected]
```

### SECONDARY INTENTS (Can Combine)

**If multiple intents detected:**
```
"I want to add dark mode and test it"
  ↓
Primary: PLAN
Secondary: TEST
  ↓
Planner includes testing phase in plan
```

---

## 🔄 Complete Workflow Examples

### Example 1: New Feature (Simple)
```
You: #file:KDS/prompts/user/cortex.md
     I want to add a pulse animation to the FAB button

Router: PLAN intent detected
   ↓
Planner: Creates 3-phase plan
   ↓
Output: ✅ Session created: fab-button-animation
        Next: #file:KDS/prompts/user/cortex.md continue
```

### Example 2: Continue Work
```
You: #file:KDS/prompts/user/cortex.md
     continue

Router: EXECUTE intent detected
   ↓
Executor: Implements next task
   ↓
Output: ✅ Task 1.1 complete: CSS animation added
        Next: #file:KDS/prompts/user/cortex.md continue
```

### Example 3: Resume After Break (SOLID v5.0)
```
(New chat next day)

You: #file:KDS/prompts/user/cortex.md
     where was I?

Router: RESUME intent detected
   ↓
Session Resumer: Loads via session-loader (DIP)
   ↓
Output: Session: fab-button-animation
        Progress: 3/8 tasks (38%)
        
        📊 Detailed Progress:
        Phase 1: ✅ Complete
        Phase 2: 🔄 1/3 tasks done
        Phase 3: ⬜ Not started
        
        Next: #file:KDS/prompts/user/cortex.md continue
```

### Example 4: Correction Mid-Work (SOLID v5.0)
```
You: #file:KDS/prompts/user/cortex.md
     continue

Executor: Modifying HostControlPanel.razor...

You: #file:KDS/prompts/user/cortex.md
     Wrong file! The FAB is in HostControlPanelContent.razor

Router: CORRECT intent detected
   ↓
Error Corrector: HALTS execution (dedicated agent)
   ↓
Analysis: FILE_MISMATCH
   Incorrect: HostControlPanel.razor
   Correct: HostControlPanelContent.razor
   ↓
Actions:
   ✅ Reverted changes to HostControlPanel.razor
   ✅ Loaded HostControlPanelContent.razor
   ✅ Updated task file reference
   ↓
Output: ✅ Correction applied
        Next: #file:KDS/prompts/user/cortex.md continue
```

### Example 5: Multi-Intent Request
```
You: #file:KDS/prompts/user/cortex.md
     I want to add dark mode toggle and create Percy visual tests for it

Router: PLAN + TEST intents detected
   ↓
Planner: Creates plan with dedicated test phase
   ↓
Output: ✅ 4-phase plan created (includes visual testing)
        Phase 4: Percy visual regression tests
        Next: #file:KDS/prompts/user/cortex.md continue
```

---

## ✅ Benefits of Universal Entry Point + SOLID v5.0

### User Experience
- ✅ **One command to remember** (`cortex.md`)
- ✅ **Natural language** - say what you want
- ✅ **No cognitive load** - don't need to know which specialist to call
- ✅ **Forgiving** - works even if you're vague
- ✅ **Predictable** - same command, consistent behavior

### Technical Benefits (SOLID v5.0)
- ✅ **Intelligent routing** - right agent for the job
- ✅ **Multi-intent handling** - complex requests work
- ✅ **Context preservation** - session state via abstraction
- ✅ **Automatic workflows** - no manual orchestration
- ✅ **Single Responsibility** - each agent focused on one job
- ✅ **Dependency Inversion** - swap storage/tools without breaking agents
- ✅ **Interface Segregation** - no mode switches, dedicated specialists
- ✅ **Easy to test** - mock abstractions, isolate agents

### Architecture Benefits
- 🎯 **Modular** - add new agents without touching existing ones
- 🔧 **Maintainable** - fix bugs in one place
- 🚀 **Performant** - no mode-switch overhead
- 📦 **Portable** - abstractions make storage/tools swappable
- 🏠 **Local-First** - 100% in KDS/, zero external dependencies
- 🔒 **Offline-Capable** - works without internet (except optional cloud features)
- 🆓 **Zero-Install** - no npm/pip/dotnet packages required for KDS

### Comparison

**Before v5.0 (7 commands + mode switches):**
```
plan.md → for new features
execute.md → for continuing work + corrections (mode switch)
resume.md → after breaks (actually loads work-planner)
correct.md → for fixing errors (loads executor in correction mode)
test.md → for creating tests
validate.md → for health checks
ask-cortex.md → for questions
govern.md → for CORTEX changes

Issues:
❌ Executor does 2 jobs (execution + correction)
❌ Planner does 2 jobs (planning + resumption)
❌ Hardcoded file paths everywhere
❌ Hardcoded test commands
```

**After v5.0 (1 command + SOLID compliance):**
```
cortex.md → for EVERYTHING
  ↓
intent-router.md → routes to 8 focused specialists
  ↓
Specialists use shared abstractions (session-loader, test-runner, file-accessor)

Benefits:
✅ Each agent has ONE responsibility
✅ Error correction is dedicated (error-corrector.md)
✅ Session resumption is dedicated (session-resumer.md)
✅ Abstractions decouple from storage/tools
✅ Easy to extend (add new agent = add new route)
```

---

## 🚫 When Routing Fails

**If intent is ambiguous:**
```
You: #file:KDS/prompts/user/cortex.md
     do something

Router: ❓ Intent unclear. Did you mean:
        1. Continue current work? (execute)
        2. Check progress? (resume)
        3. Validate changes? (validate)
        
        Please clarify.
```

**If no active session and you say "continue":**
```
You: #file:KDS/prompts/user/cortex.md
     continue

Router: ❌ No active session found.
        Did you mean to start new work?
        Use: "I want to [describe feature]"
```

---

## 📊 SOLID v5.0 Design Benefits

### Answer: YES - It Makes CORTEX Better!

**Design Improvements:**
- ✅ **Single Responsibility** - Each agent has ONE clear job
- ✅ **Interface Segregation** - No mode switches (dedicated agents)
- ✅ **Dependency Inversion** - Abstractions decouple from concrete implementations
- ✅ **Open/Closed** - Easy to extend (add agents) without modifying existing code

**SOLID v5.0 Architecture:**
```
User Interface Layer:
  cortex.md (universal) ────────┐
  plan.md (direct)   ────────┤
  execute.md (direct) ───────┤
  test.md (direct)    ───────┤  All route through
  correct.md (direct) ───────┤
  resume.md (direct)  ───────┤
  ...                        ├─→ intent-router.md (ROUTER)
                             │
Internal Agent Layer:        │
  work-planner.md     ←──────┤  (PLAN only)
  code-executor.md    ←──────┤  (EXECUTE only)
  error-corrector.md  ←──────┤  (CORRECT only - NEW)
  session-resumer.md  ←──────┤  (RESUME only - NEW)
  test-generator.md   ←──────┤  (TEST only)
  health-validator.md ←──────┤  (VALIDATE only)
  change-governor.md  ←──────┤  (GOVERN only)
  knowledge-retriever.md ←───┘  (ASK only)
  
Abstraction Layer (DIP):
  session-loader.md   → Abstract session access
  test-runner.md      → Abstract test execution
  file-accessor.md    → Abstract file I/O
```

**What Changed from v4.5:**
```diff
- code-executor.md (execution + correction modes) ❌ SRP violation
+ code-executor.md (execution only) ✅ SRP compliant
+ error-corrector.md (correction only) ✅ ISP compliant

- work-planner.md (planning + resumption modes) ❌ SRP violation
+ work-planner.md (planning only) ✅ SRP compliant
+ session-resumer.md (resumption only) ✅ ISP compliant

- Direct file access (#file:KDS/sessions/...) ❌ DIP violation
+ Abstract access (session-loader.md) ✅ DIP compliant

- Hardcoded test commands (npx playwright test) ❌ DIP violation
+ Abstract runner (test-runner.md) ✅ DIP compliant
```

**Benefits:**
- 🎯 **Clarity** - One agent = one job (easier to understand)
- 🚀 **Performance** - No mode-switch logic (faster routing)
- 🔧 **Testability** - Mock abstractions (easier to test)
- 📦 **Flexibility** - Swap storage/tools without breaking agents

**Flexibility:**
```
Option 1 (Easy): Use cortex.md universal entry point
Option 2 (Explicit): Call specific prompts directly
Option 3 (Advanced): Call internal agents with abstractions

All work! Universal is for convenience, SOLID is for quality.
```

---

## 🎓 Quick Reference Card

**For everything:**
```
#file:KDS/prompts/user/cortex.md
[what you want in natural language]
```

**What it detects:**
- "I want to..." → plan
- "Continue..." → execute  
- "Where was I..." → resume
- "Wrong..." → correct
- "Test..." → test
- "Validate..." → validate
- "How do I..." → ask
- "I updated KDS..." → govern
- "Update documentation..." → plan (CORTEX Quadrant update) 📚
- "Refresh documentation..." → trigger Documentation Refresh Plugin 🆕
- "Publish docs..." → plan (CORTEX Quadrant update)

**Documentation Refresh Plugin (NEW!)** 🆕
When you say "Refresh documentation" or "Update Documentation", CORTEX triggers the Documentation Refresh Plugin which synchronizes the 4 key documentation files:
- `docs/story/Cortex-Trinity/Technical-CORTEX.md` - Technical deep-dive
- `docs/story/Cortex-Trinity/Awakening Of CORTEX.md` - Engaging story
- `docs/story/Cortex-Trinity/Image-Prompts.md` - Visual generation prompts
- `docs/story/Cortex-Trinity/History.md` - Evolution timeline

These 4 documents form the **CORTEX Documentation Quadrant** - always kept synchronized with the latest CORTEX 2.0 design.

**That's all you need to know!** 🚀

---

## 🧠 BRAIN System Best Practices

### Automatic Learning is ENABLED by Default

**CORTEX v5.0+ automatically logs events and updates BRAIN - no user action needed!**

**What happens automatically:**
1. ✅ Agents log events after every action (routing, file modifications, corrections)
2. ✅ Events accumulate in `KDS/cortex-brain/events.jsonl`
3. ✅ Rule #16 Step 5 checks event count after each task
4. ✅ When 50 events reached → `brain-updater.md` auto-triggered
5. ✅ Knowledge graph updated with new patterns
6. ✅ Next routing decision gets smarter

**You benefit without doing anything!**

### Verify BRAIN is Learning (Optional Health Check)

**Want to confirm automatic learning is working?**

Check these indicators:
```bash
# 1. Recent events logged (should have timestamps from today)
cat KDS/cortex-brain/events.jsonl | tail -5

# 2. Knowledge graph updated recently (check last modified)
ls -la KDS/cortex-brain/knowledge-graph.yaml

# 3. Event count reasonable (not accumulating to 100+)
wc -l KDS/cortex-brain/events.jsonl
```

**Healthy BRAIN signs:**
- ✅ `events.jsonl` has recent timestamps (within last few hours)
- ✅ `knowledge-graph.yaml` updated in last 24 hours
- ✅ Event count stays below 50 (auto-cleanup working)

**⚠️ Warning signs (violations detected):**
- ❌ No events logged for 4+ hours (event logging broken)
- ❌ `knowledge-graph.yaml` not updated in 24+ hours
- ❌ 50+ unprocessed events accumulated (automatic update not triggering)

**If you see warnings:** See `KDS/docs/architecture/KDS-SELF-REVIEW-STRATEGY.md` for fixes

### Manual BRAIN Update (Only if Needed)

**When to manually update:**
- 🔧 After bulk corrections (fixed multiple files at once)
- 🔧 After large refactoring (want BRAIN to learn patterns immediately)
- 🚨 If automatic updates stopped working (>50 events accumulated)
- 📊 Before important routing decision (want latest knowledge)

**How to trigger manually:**
```markdown
#file:KDS/prompts/internal/brain-updater.md
```

This processes all events and updates the knowledge graph.

### Standard Practice: Trust Automatic Learning

**Every CORTEX interaction SHOULD automatically:**
1. ✅ Log events (no user action needed)
2. ✅ Query BRAIN for insights (before routing/file decisions)
3. ✅ Update knowledge graph (periodic automatic)

**This is STANDARD CORTEX practice** - all agents follow this pattern automatically.

### For Advanced Users Only

**Manual intervention rarely needed, but available:**

1. **Manually correct routing** if BRAIN suggests wrong intent:
   ```markdown
   #file:KDS/prompts/user/cortex.md
   Wrong intent! I meant [correct interpretation]
   ```
   Error corrector logs the mistake, BRAIN learns for next time.

2. **Check BRAIN health** during self-review:
   ```markdown
   #file:KDS/prompts/user/validate.md
   Check BRAIN system health
   ```

3. **Force immediate update** after major changes:
   ```markdown
   #file:KDS/prompts/internal/brain-updater.md
   ```

**But in normal usage: Just use CORTEX and let BRAIN learn automatically!**

### First-Time Setup (Optional - BRAIN Works Out of the Box)

**CORTEX v5.0+ works immediately with empty BRAIN - learning starts from first use!**

**Optional bootstrapping (faster initial learning):**

**Option 1: Populate from existing sessions (if you have session history):**
```powershell
# PowerShell - Seed BRAIN from past sessions
.\KDS\scripts\populate-cortex-brain.ps1

# Then update knowledge graph
#file:KDS/prompts/internal/brain-updater.md
```

**Option 2: Crawl your codebase (recommended for new installations):**
```powershell
# PowerShell - Quick scan (30 seconds)
.\KDS\scripts\brain-crawler.ps1 -Mode quick

# OR Deep scan (5-10 minutes, comprehensive)
.\KDS\scripts\brain-crawler.ps1 -Mode deep
```

The crawler analyzes your entire application and feeds BRAIN with:
- 🏗️ Architectural patterns (where components/services/tests live)
- 🔗 File relationships (what depends on what)
- 📝 Naming conventions (how files are named)
- 🛠️ Technology stack (languages, frameworks, tools)
- 🧪 Test patterns (frameworks, test data, selectors)

**See:** `#file:KDS/prompts/internal/brain-crawler.md` for details

**But remember: Bootstrapping is OPTIONAL - BRAIN learns automatically from first interaction!**

### Ongoing Usage - No Action Needed!

**Just use CORTEX normally!** BRAIN learns automatically from every interaction:
- 📝 Events logged automatically with every agent action
- 🧠 BRAIN updated automatically when 50 events accumulate
- 💡 Decisions get smarter automatically over time
- 🕷️ Optional: Run incremental crawler scans to refresh architectural knowledge

**Zero manual intervention required for continuous learning.**

**Only manual actions needed:**
1. 🚨 If automatic learning breaks (check `KDS-SELF-REVIEW-STRATEGY.md`)
2. 🔧 After bulk corrections (want immediate learning)
3. 📊 When starting new project (run crawler to learn codebase)

**99% of the time: BRAIN just works!**

### Moving CORTEX to Another Application

**Need to reset BRAIN for a new project?**
```powershell
# PowerShell - Soft reset (clear data, keep config)
.\KDS\scripts\brain-reset.ps1 -Mode soft

# OR Export generic patterns first, then reset
.\KDS\scripts\brain-reset.ps1 -Mode export-reset -ExportPath ".\templates\my-patterns\"

# Then crawl the new application
.\KDS\scripts\brain-crawler.ps1 -Mode deep
```

BRAIN gets amnesia (forgets old app) but keeps all logic intact!

**See:** `#file:KDS/prompts/internal/brain-reset.md` for details

---

## 🔗 Technical Implementation (SOLID v5.0)

**This prompt loads:**
```markdown
#file:KDS/prompts/internal/intent-router.md
```

**Which analyzes your request and loads one of:**
```
#file:KDS/prompts/user/plan.md → #file:KDS/prompts/internal/work-planner.md
#file:KDS/prompts/user/execute.md → #file:KDS/prompts/internal/code-executor.md
#file:KDS/prompts/user/test.md → #file:KDS/prompts/internal/test-generator.md
#file:KDS/prompts/user/validate.md → #file:KDS/prompts/internal/health-validator.md
#file:KDS/prompts/user/govern.md → #file:KDS/prompts/internal/change-governor.md
#file:KDS/prompts/user/ask-cortex.md → #file:KDS/prompts/internal/knowledge-retriever.md
#file:KDS/prompts/user/correct.md → #file:KDS/prompts/internal/error-corrector.md (NEW)
#file:KDS/prompts/user/resume.md → #file:KDS/prompts/internal/session-resumer.md (NEW)
```

**Shared abstractions (DIP compliance):**
```
#shared-module:session-loader.md → Abstract session access (default: local files)
#shared-module:test-runner.md → Abstract test execution (uses project's tools)
#shared-module:file-accessor.md → Abstract file I/O (PowerShell built-ins)

NOTE: All 100% local (in KDS/), zero external dependencies
```

**BRAIN management agents:**
```
#file:KDS/prompts/internal/brain-query.md → Query knowledge graph
#file:KDS/prompts/internal/brain-updater.md → Process events and update
#file:KDS/prompts/internal/brain-crawler.md → Codebase analysis (NEW)
#file:KDS/prompts/internal/brain-reset.md → Selective amnesia (NEW)
```

---

## 🎯 Active Development Plan (CORTEX v6.0)

**Current Focus:** Real-Time BRAIN Dashboard with Live Reference System + Automatic BRAIN Updates

### ✅ **COMPLETED:** Rule #22 - Automatic BRAIN Updates

**Status:** 🎉 **IMPLEMENTED** (Option D - Hybrid Approach)

**What Was Built:**

1. **Manual Recording Script** (Phase 1 - COMPLETE)
   - ✅ `scripts/record-conversation.ps1` - Manual conversation capture
   - ✅ Logs to `conversation-history.jsonl` (Tier 1)
   - ✅ FIFO enforcement (keep 20, delete oldest)
   - ✅ Auto-checks brain-updater threshold (50 events OR 24 hours)
   - ✅ **TESTED:** CopilotChats.txt conversation successfully recorded

2. **Auto BRAIN Updater** (Phase 2 - COMPLETE)
   - ✅ `scripts/auto-brain-updater.ps1` - Automatic trigger after every request
   - ✅ Logs request to `events.jsonl` (Tier 4)
   - ✅ Checks thresholds (50+ events OR 24+ hours)
   - ✅ Auto-invokes `brain-updater.ps1` when threshold met
   - ✅ Keeps `brain-updater.ps1` synchronized with `brain-updater.md`
   - ✅ **TESTED:** 13 events processed, knowledge-graph.yaml updated

3. **Git Hooks** (Phase 2 - COMPLETE)
   - ✅ `hooks/post-commit` - Auto-runs after every git commit
   - ✅ `scripts/setup-git-hooks.ps1` - One-time installation
   - ✅ Silent background execution (doesn't block commits)

4. **Governance Rule** (Tier 0 - COMPLETE)
   - ✅ **Rule #22:** Auto BRAIN Update After Every Request
   - ✅ `governance/rules/auto-brain-update.md` - Full specification
   - ✅ Tier 0 (INSTINCT) - Permanent, cannot be overridden
   - ✅ Updated `governance/rules.md` with Rule #22

5. **Architecture Documentation** (COMPLETE)
   - ✅ `docs/architecture/BRAIN-RECORDING-GAP-ANALYSIS.md` - Root cause analysis
   - ✅ Identified problem: GitHub Copilot Chat doesn't auto-invoke agents
   - ✅ Designed 4 solutions (manual, git hooks, extension, harvester)
   - ✅ Implemented hybrid approach (Phases 1-3 over 3 weeks)

**How to Use:**

```powershell
# Manual recording (after significant conversations)
.\scripts\record-conversation.ps1 `
    -Title "Your conversation title" `
    -FilesModified "file1.md,file2.ps1" `
    -EntitiesDiscussed "feature1,feature2" `
    -Outcome "What was accomplished" `
    -Intent "PLAN"

# Automatic (runs after git commits via hook)
git commit -m "Your commit message"  # auto-triggers brain-updater

# Test auto-updater manually
.\scripts\auto-brain-updater.ps1 `
    -RequestSummary "Test request" `
    -ResponseType "direct"

# Install git hooks (one-time setup)
.\scripts\setup-git-hooks.ps1
```

**Success Metrics:**
- ✅ 6 conversations in `conversation-history.jsonl` (was 5, added CopilotChats.txt)
- ✅ 13 events in `events.jsonl` (threshold: 50 for auto-update)
- ✅ brain-updater auto-triggered (24+ hours since last update)
- ✅ `knowledge-graph.yaml` updated with 13 new events
- ✅ Git hook installed and operational

**Next Steps (Phase 3 - Weeks 2-3):**
- 📋 VS Code extension with Chat Participant API
- 📋 Real-time conversation interception
- 📋 Scheduled harvester (parse Copilot Chat history every 2 hours)
- 📋 Full automation (zero user action required)

---

### Phase 7.3: Dashboard BRAIN Reference (IN DESIGN)

**Purpose:** Visual one-page guide to all CORTEX BRAIN functionality  
**Priority:** HIGH  
**Status:** 🎯 DESIGN COMPLETE - READY TO IMPLEMENT

**New Features:**

1. **Tier 0 (Instinct) Enhancement** - Holistic review complete
   - ✅ Identified 6 fundamental design gaps
   - 📋 6 new Tier 0 files designed:
     - `governance/tier-0/tool-requirements.yaml` - Essential dependencies
     - `governance/tier-0/setup-protocol.yaml` - 5-step initialization
     - `governance/tier-0/tier-classification-rules.yaml` - Event classification
     - `governance/tier-0/amnesia-recovery.yaml` - Detection & recovery
     - `governance/tier-0/agent-protocols.yaml` - Standard behaviors
     - `governance/tier-0/hemisphere-coordination-rules.yaml` - LEFT/RIGHT communication

2. **Dashboard "BRAIN Reference" Tab** - Visual learning system
   - 📋 Tab 1: OVERVIEW (one-page summary of all 5 tiers)
   - 📋 Tab 2: RULES & GOVERNANCE (18 rules, searchable)
   - 📋 Tab 3: HOW THINGS WORK (visual workflows)
     - "How Amnesia Works" (detection, recovery, prevention)
     - "How Learning Works" (brain-updater.md cycle)
     - "How TDD Cycle Works" (RED→GREEN→REFACTOR)
     - "How Crawlers Work" (file discovery, dependencies)
     - "How Health Checks Work" (test-brain-integrity.ps1)
     - "How Setup Works" (initialization, validation)
     - "How Hemispheres Coordinate" (LEFT/RIGHT messaging)
   - 📋 Tab 4: SETUP & DEPENDENCIES (tool inventory, validation)
   - 📋 Tab 5: HEMISPHERES & COORDINATION (real-time activity)

3. **Closed-Loop Self-Healing** - Dashboard → BRAIN feedback
   - 📋 Health results logged to events.jsonl (Tier 4)
   - 📋 brain-healer.md agent (auto-remediation)
   - 📋 Remediation scripts (yaml, conversation, KG, session fixes)
   - 📋 Dashboard "Fix" buttons (user-triggered repairs)
   - 📋 Knowledge graph pattern learning (failure tracking)

**Architecture Docs:**
- `docs/architecture/DASHBOARD-BRAIN-INTEGRATION.md` - Self-healing design
- `docs/architecture/DASHBOARD-BRAIN-REFERENCE-FEATURE.md` - Visual reference design
- `docs/DASHBOARD-BRAIN-INTEGRATION-SUMMARY.md` - Self-healing summary
- `docs/DASHBOARD-BRAIN-REFERENCE-SUMMARY.md` - Visual reference summary

**Implementation Plan:** 4 weeks (see Phase 7 in KDS-V6-IMPLEMENTATION-PLAN-RISK-BASED.md)

**User Value:**
- ✅ One-page visual reference for entire BRAIN (no more trying to remember)
- ✅ Understand how ANY feature works (amnesia, learning, TDD, etc.)
- ✅ See all 18 rules in searchable format
- ✅ Know setup requirements and tool dependencies
- ✅ Monitor hemisphere activity in real-time
- ✅ Auto-fix common issues (or trigger manual fixes)
- ✅ Live data updated every 5-30 seconds

**Start Implementation:**
```
#file:KDS/prompts/user/plan.md "Implement Phase 7.3: Dashboard BRAIN Reference System"
```

---

### 📋 **PLANNED:** Mind Palace - Advanced Memory Architecture

**Purpose:** Enhanced spatial memory system for complex knowledge organization  
**Priority:** FUTURE  
**Status:** 📋 PLACEHOLDER - Design phase pending

**Concept:**
The Mind Palace extends KDS's BRAIN system with spatial memory techniques for organizing complex technical knowledge. This system will enable Copilot to "mentally navigate" through architectural concepts, code relationships, and project knowledge using memory palace techniques.

**Planned Features:**
- 📋 Spatial knowledge organization (rooms, floors, locations)
- 📋 Visual memory associations for complex patterns
- 📋 Hierarchical knowledge structures
- 📋 Enhanced context retrieval using spatial relationships
- 📋 Integration with existing Tier 2 knowledge graph

**Metric Tracking (Core Requirement):**
The Mind Palace will be designed with comprehensive metric tracking from the start:

```yaml
mind_palace_metrics:
  kds_performance:
    - knowledge_retrieval_speed: "Time to locate relevant patterns"
    - spatial_navigation_accuracy: "Correct room/location hit rate"
    - pattern_association_effectiveness: "Successful pattern matches"
    - memory_consolidation_rate: "Tier 1 → Tier 2 conversion efficiency"
    - context_reconstruction_time: "Resume session speed"
    
  coding_efficiency:
    - time_to_first_code: "Request → First implementation"
    - architectural_alignment_rate: "% of solutions matching existing patterns"
    - rework_reduction: "Before/after Mind Palace implementation"
    - context_switching_overhead: "Time lost when changing tasks"
    - learning_curve_acceleration: "New team member onboarding speed"
    
  quality_metrics:
    - test_coverage_trends: "Before/after Mind Palace"
    - bug_escape_rate: "Issues reaching production"
    - architectural_consistency_score: "Alignment with design patterns"
    - knowledge_retention_rate: "Pattern recall accuracy over time"
    
  roi_measurements:
    - development_velocity_change: "Sprint velocity trends"
    - onboarding_time_reduction: "New developer productivity"
    - context_recovery_savings: "Hours saved on session resumes"
    - decision_quality_improvement: "Architectural decision success rate"
```

**Integration Points:**
- 📋 Tier 2 (Knowledge Graph) - Spatial overlay for existing patterns
- 📋 Tier 3 (Development Context) - Velocity impact tracking
- 📋 Dashboard - Real-time visualization of memory palace structure
- 📋 Metrics Reporter - Dedicated Mind Palace analytics

**Design Phase Tasks:**
1. Research spatial memory techniques for code organization
2. Design memory palace structure (rooms, floors, associations)
3. Define integration with existing BRAIN tiers
4. Create metric collection framework
5. Build prototype with test dataset
6. Validate effectiveness with real-world usage

**Documentation (To Be Created):**
- `docs/architecture/MIND-PALACE-DESIGN.md` - Full specification
- `docs/architecture/MIND-PALACE-METRICS.md` - Measurement framework
- `cortex-brain/mind-palace/` - Storage structure (when implemented)

**Notes:**
- Design will prioritize measurability from day one
- All claims must be backed by quantitative metrics
- Focus on demonstrable coding efficiency improvements
- Integration must be seamless with existing workflows

**When Ready to Design:**
```
#file:KDS/prompts/user/plan.md "Design Mind Palace Memory Architecture with Metrics"
```

---

## 📋 CORTEX Response Templates - Practical Action Design

**Philosophy:** CORTEX responses should leverage planning and execution capabilities to provide **actionable, cumulative options** instead of one-by-one choices.

### ✅ GOOD: Actionable & Cumulative

**Example 1: Documentation Refresh**
```markdown
## 🚀 Ready to Execute

I've identified 4 documentation gaps and prepared an execution plan.

**Execute All (Recommended):**
I'll complete all phases sequentially:
1. Update "The Awakening" story (15 min)
2. Create 26 missing technical docs (45 min)  
3. Generate 8 Mermaid diagrams (20 min)
4. Deploy to GitHub Pages (5 min)

Estimated: 85 minutes total

Say **"Execute all"** to start, or **"Just phases 1-2"** to run partially.

**Manual Review First:**
Say **"Show me the plan"** to review details before execution.
```

**Example 2: Test Failures**
```markdown
## 🔧 3 Test Failures Detected

**Fix All (Recommended):**
I'll fix all 3 issues in one pass:
- Fix selector in `button.spec.ts` (async timing)
- Update API mock in `service.spec.ts` (schema change)
- Add missing import in `utils.spec.ts` (module not found)

Say **"Fix all"** and I'll execute all repairs with verification.

**Investigate First:**
Say **"Show root causes"** to analyze before fixing.
```

**Example 3: Feature Implementation**
```markdown
## ✅ Plan Created: Multi-Language Invoice Export

**Execute Full Feature:**
I'll implement all 4 phases using TDD:
1. Phase 1: Service layer (tests → code) - 30 min
2. Phase 2: API endpoints (tests → code) - 25 min  
3. Phase 3: UI component (tests → code) - 40 min
4. Phase 4: Integration tests & validation - 20 min

Total: ~115 minutes

Say **"Execute full feature"** to start end-to-end implementation.

**Phase-by-Phase:**
Say **"Start Phase 1"** to proceed incrementally with checkpoints.
```

### ❌ BAD: One-by-One Options (Old Style)

```markdown
## Next Steps

**Option 1:** Update story  
Review the visual presentation, navigation behavior, and story flow.

**Option 2:** Create technical docs  
Continue with Phase 2 to add documentation.

**Option 3:** Generate diagrams  
Proceed with Phase 3 to generate the 26 missing diagrams.

**Option 4:** Deploy  
When satisfied with localhost review, deploy to GitHub Pages.
```

**Why this is bad:**
- ❌ Forces 4 separate invocations
- ❌ Doesn't leverage CORTEX planning
- ❌ No "do everything" option
- ❌ Wastes user time

### 🎯 Response Template Rules

**Rule 1: Always offer cumulative execution**
```markdown
✅ "Execute all phases" (cumulative)
✅ "Fix all issues" (batch)
✅ "Implement full feature" (end-to-end)

❌ "Option 1, 2, 3, 4" (one-by-one)
```

**Rule 2: Provide smart defaults**
```markdown
✅ "Execute all (Recommended)" - Make the best path obvious
✅ "Estimated: 85 minutes" - Set expectations
✅ "Say 'Execute all' to start" - Clear command

❌ "What do you want to do?" - Forces decision making
```

**Rule 3: Include escape hatches**
```markdown
✅ "Show me the plan" - Review before execution
✅ "Just phases 1-2" - Partial execution
✅ "Pause after Phase 1" - Incremental with checkpoints

❌ Only all-or-nothing options
```

**Rule 4: Leverage CORTEX planning**
```markdown
✅ Break work into phases internally
✅ Show time estimates per phase
✅ Offer full plan execution by default
✅ Use todo list for multi-phase work

❌ Present raw phases as user choices
```

**Rule 5: Make commands copyable**
```markdown
✅ Say **"Execute all"** to start
✅ Say **"Fix all tests"** to proceed
✅ Command in **bold** for easy identification

❌ "You can proceed" (vague)
❌ "Let me know when ready" (passive)
```

### 📊 Response Format Template

**Standard Multi-Phase Response:**
```markdown
## 🎯 [Summary of Work]

[Brief description of what was discovered/analyzed]

**Execute All (Recommended):**
I'll complete [X phases/tasks] sequentially:
1. [Phase 1 name] ([time estimate])
2. [Phase 2 name] ([time estimate])
3. [Phase 3 name] ([time estimate])

Total: [X minutes/hours]

Say **"Execute all"** to start, or **"Just phase X"** to run partially.

**Alternative Approaches:**
- **"Show me the plan"** - Review detailed breakdown first
- **"Pause after Phase X"** - Stop for checkpoint review
- **"Skip Phase X"** - Execute with modifications

**Already complete?** Say **"Continue"** to resume from last checkpoint.
```

**Standard Issue Fix Response:**
```markdown
## 🔧 [X Issues/Errors] Detected

[Brief summary of problems]

**Fix All (Recommended):**
I'll address all [X] issues in one pass:
- [Issue 1]: [One-line fix description]
- [Issue 2]: [One-line fix description]  
- [Issue 3]: [One-line fix description]

Say **"Fix all"** and I'll execute repairs with verification.

**Investigate Further:**
- **"Show root causes"** - Deep analysis before fixing
- **"Fix [specific issue]"** - Address individually
- **"Show impact"** - What breaks if unfixed

**Batch Strategy:** All fixes use atomic commits with rollback safety.
```

**Standard Completion Response:**
```markdown
## ✅ [Feature/Task] Complete

**What was delivered:**
- ✅ [Deliverable 1] - [Brief result]
- ✅ [Deliverable 2] - [Brief result]
- ✅ [Deliverable 3] - [Brief result]

**Quality Checks:**
- ✅ [X] tests passing
- ✅ Zero errors, zero warnings
- ✅ [Performance/coverage metric]

**Next Actions (Choose One):**
- **"Deploy to [environment]"** - Push changes live
- **"Add [related feature]"** - Extend functionality
- **"Show metrics"** - View detailed statistics
- **"Mark complete"** - Archive and move on

**Documentation updated:** [Link or file reference]
```

### 🧪 Examples by Scenario

**Scenario: Documentation needs refresh**
```markdown
## 📚 Documentation Refresh Plan Ready

Git analysis identified 5 new features since last deployment (Brain Protector, Oracle Crawler, Knowledge Boundaries, Amnesia, Pattern Cleanup).

**Execute Full Refresh (Recommended):**
I'll complete all 7 phases:
1. Update "Awakening" story with new features (20 min)
2. Create 5 technical docs (Brain Protector, Oracle, etc.) (35 min)
3. Generate 6 Mermaid diagrams (15 min)
4. Create 4 Gemini image prompts (10 min)
5. Build docs with `mkdocs build --clean` (2 min)
6. Launch localhost:8000 for review (auto-open browser)
7. Generate refresh report (5 min)

Total: ~87 minutes | Auto-launches: localhost:8000 for review

Say **"Execute full refresh"** to start all phases, or **"Just story update"** for Phase 1 only.

**Before starting?** Say **"Show detailed plan"** to review each phase's changes.
```

**Scenario: Multiple test failures**
```markdown
## 🧪 7 Test Failures Detected

Test suite shows 7 failures across 3 components (HostControlPanel, InvoiceService, UserRegistration).

**Fix All (Recommended):**
I'll repair all 7 failures in dependency order:
1. **HostControlPanel** (3 failures): Update selectors for refactored IDs
2. **InvoiceService** (2 failures): Fix API contract after schema change
3. **UserRegistration** (2 failures): Add missing validation mocks

Estimated: 25 minutes | Strategy: Fix → Run → Verify per component

Say **"Fix all tests"** to execute batch repair.

**Need Analysis First?**
- **"Show failure details"** - Stack traces & root causes
- **"Group by component"** - Organized breakdown
- **"Check coverage"** - View test coverage impact
```

**Scenario: Complex feature implementation**
```markdown
## 🚀 Feature Plan Ready: Real-Time Dashboard BRAIN Reference

Plan created with 4 phases (28 tasks, 6.5 hours estimated).

**Execute Complete Feature (Recommended):**
I'll implement full BRAIN Reference system using TDD:

**Phase 1: UI Foundation** (90 min)
- Create 5 dashboard tabs (Overview, Rules, How Things Work, Setup, Hemispheres)
- Implement tab navigation & layout
- Tests: Component rendering, tab switching

**Phase 2: Data Integration** (120 min)  
- Connect to Tier 0-4 data sources
- Build real-time update system (5-30s refresh)
- Tests: Data loading, refresh cycles, error handling

**Phase 3: Visual Workflows** (90 min)
- Create 7 "How X Works" diagrams (Amnesia, Learning, TDD, etc.)
- Implement interactive workflow visualization
- Tests: Diagram rendering, user interactions

**Phase 4: Health & Fixes** (90 min)
- Add health monitoring dashboard
- Implement one-click fix buttons
- Tests: Health checks, remediation workflows

Total: 6.5 hours | 60 tests | TDD throughout

Say **"Execute complete feature"** for end-to-end implementation.

**Incremental Delivery:**
- **"Execute Phase 1"** - UI foundation only, review before Phase 2
- **"Show task breakdown"** - Detailed 28-task checklist
- **"Estimate per phase"** - Time breakdown with dependencies
```

### 🎨 Visual Examples

**Before (Bad):**
```
Next Steps:
Option 1: Fix test A
Option 2: Fix test B  
Option 3: Fix test C
Option 4: Run all tests
```

**After (Good):**
```
## 🔧 3 Test Failures - Batch Fix Ready

Fix All (Recommended):
I'll repair tests A, B, C in one pass (8 min total)

Say "Fix all tests" to execute → Full verification included
```

---

**Before (Bad):**
```
What would you like me to do next?
1. Update docs
2. Create diagrams
3. Build site
4. Deploy
```

**After (Good):**
```
## 📚 Documentation Ready for Deployment

Execute Pipeline (Recommended):
Update docs → Diagrams → Build → Deploy (25 min)

Say "Deploy pipeline" to execute full workflow
```

---

### 💡 Key Takeaway

**CORTEX should work like a senior developer:**
- ✅ "I'll fix all 7 test failures - give me 30 minutes" (proactive)
- ❌ "Which test failure do you want me to look at first?" (passive)

**User's job:** Approve strategy  
**CORTEX's job:** Execute efficiently

---

## ✨ Summary
````

**You asked:**
> "Will the CORTEX system benefit from SOLID principles?"

**Answer: ABSOLUTELY! v5.0 implements:**
- ✅ **Single Responsibility** - One agent = one job
- ✅ **Interface Segregation** - Dedicated agents (no mode switches)
- ✅ **Dependency Inversion** - Abstractions decouple from concrete implementations
- ✅ **Open/Closed** - Easy to extend without modifying existing code

**What changed:**
- ➕ Added `error-corrector.md` (dedicated correction agent)
- ➕ Added `session-resumer.md` (dedicated resumption agent)
- ➕ Added abstraction layer (`session-loader`, `test-runner`, `file-accessor`)
- ✅ Removed mode switches from `code-executor` and `work-planner`
- ✅ Decoupled agents from concrete file paths and tool commands

**Local-First Compliance:**
- ✅ **100% in KDS/** - All CORTEX logic, data, scripts housed locally
- ✅ **Minimal external dependencies** - Only CORTEX enhancement libraries (declared upfront)
- ✅ **Offline-capable** - Works without internet (core functionality)
- ✅ **Transparent setup** - User informed of all required libraries during setup
- ⚠️ **Optional extensions** - Cloud/database storage available but not required

**Dependency Categories:**
1. **CORTEX Core** - Zero dependencies (PowerShell/bash built-ins only)
2. **CORTEX Enhancements** - Open source libraries for improved capabilities (ALLOWED, declared at setup)
3. **Application Code** - User's project dependencies (Copilot recommends, user approves)
4. **Optional Features** - Cloud/DB/external services (opt-in only)

**What you need to remember:**
```
#file:KDS/prompts/user/cortex.md
[describe what you want]
```

**That's it. CORTEX handles the rest with SOLID principles and local-first design.** 🎯
