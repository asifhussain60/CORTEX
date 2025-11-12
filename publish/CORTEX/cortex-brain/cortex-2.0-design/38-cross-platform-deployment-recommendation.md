# CORTEX 2.0: Cross-Platform & Repository-Agnostic Deployment Strategy

**Document:** 38-cross-platform-deployment-recommendation.md  
**Version:** 1.0  
**Created:** 2025-11-09  
**Status:** Recommendation  
**Priority:** CRITICAL  

**Purpose:** Define the optimal deployment strategy for CORTEX 2.0 that works across:
- Multiple platforms (Windows, macOS, Linux)
- Various repository folder structures
- Different team configurations (solo, small team, enterprise)

---

## 🎯 Executive Summary

### Current State Analysis

**CORTEX 2.0 is well-designed but has deployment limitations:**

✅ **Strengths:**
- Excellent modular architecture (97% token reduction)
- Robust cross-platform detection (Mac/Windows/Linux)
- Strong brain architecture (Tier 0-3)
- Comprehensive agent system (10 specialists)

⚠️ **Limitations:**
- **Assumes CORTEX lives in target repo** (hardcoded paths to `cortex-brain/`, `prompts/`, `src/`)
- **Not portable** - can't be used in arbitrary projects without copying entire structure
- **File reference syntax barriers** - `#file:prompts/user/cortex.md` is verbose
- **No standard GitHub Copilot integration** - missing `.github/copilot-instructions.md`

### Recommended Solution: **Hybrid Deployment Model**

Deploy CORTEX in **3 distinct modes** to support different use cases:

1. **Mode 1: Standalone CORTEX Repository** (Current - Dev/Testing)
2. **Mode 2: Embedded CORTEX** (Deploy in target repo - Team Projects)
3. **Mode 3: External CORTEX Service** (Separate repo + API - Enterprise)

---

## 🏗️ Deployment Architecture

### Mode 1: Standalone CORTEX Repository

**Use Case:** CORTEX development, testing, and prototyping

**Structure:**
```
CORTEX/
├── .github/
│   ├── copilot-instructions.md        # Auto-loaded context
│   └── prompts/
│       ├── CORTEX.prompt.md           # /CORTEX command
│       ├── story.prompt.md            # /story command
│       ├── setup.prompt.md            # /setup command
│       └── agents.prompt.md           # /agents command
├── cortex-brain/                      # Brain storage
├── src/                               # CORTEX implementation
├── prompts/                           # Detailed prompts
└── scripts/                           # Automation

```

**Entry Points:**
- Automatic: `.github/copilot-instructions.md` (always loaded)
- On-demand: `/CORTEX` or `/story` or `/setup`
- Legacy: `#file:prompts/user/cortex.md` (still supported)

**Pros:**
- ✅ Full CORTEX capabilities
- ✅ Easy development and testing
- ✅ Complete brain history
- ✅ All agents available

**Cons:**
- ⚠️ Only works within CORTEX repo
- ⚠️ Not usable in other projects

---

### Mode 2: Embedded CORTEX (NEW - RECOMMENDED)

**Use Case:** Team projects that want CORTEX cognitive capabilities

**Structure:**
```
MyProject/                             # Your actual project
├── .github/
│   ├── copilot-instructions.md        # CORTEX baseline context
│   └── prompts/
│       ├── CORTEX.prompt.md           # Entry point
│       └── continue.prompt.md         # Resume conversations
├── .cortex/                           # Embedded CORTEX (NEW)
│   ├── brain/                         # Project-specific brain
│   │   ├── tier1/                     # Conversations for THIS project
│   │   ├── tier2/                     # Patterns for THIS project
│   │   └── tier3/                     # Metrics for THIS project
│   ├── config.json                    # CORTEX configuration
│   └── plugins/                       # Project-specific plugins
├── src/                               # Your project code
├── tests/                             # Your project tests
└── package.json                       # Your project config
```

**Installation:**
```bash
# Install CORTEX in your project
npx create-cortex-brain

# Or with Python
pip install cortex-ai
python -m cortex.init
```

**Entry Points:**
- Automatic: `.github/copilot-instructions.md` (baseline)
- On-demand: `/CORTEX` (full capabilities)
- Quick: `/continue` (resume work)

**Pros:**
- ✅ Works in ANY repository
- ✅ Project-specific brain (isolated memory)
- ✅ Simple installation (npm/pip)
- ✅ Team-shareable via Git
- ✅ No external dependencies

**Cons:**
- ⚠️ Limited to embedded capabilities
- ⚠️ Each project has separate brain
- ⚠️ Requires installation per repo

---

### Mode 3: External CORTEX Service (FUTURE)

**Use Case:** Enterprise teams, multiple projects, shared brain

**Architecture:**
```
CORTEX-Server/                         # Separate repo/service
├── src/                               # CORTEX core
├── cortex-brain/                      # Shared brain across projects
└── api/                               # REST API

MyProject1/                            # Client project 1
├── .github/
│   └── copilot-instructions.md        # Calls CORTEX API
└── .cortexrc                          # API endpoint config

MyProject2/                            # Client project 2
├── .github/
│   └── copilot-instructions.md        # Calls CORTEX API
└── .cortexrc                          # API endpoint config
```

**Installation:**
```bash
# In your project
npm install @cortex/client
cortex connect https://cortex-api.yourcompany.com
```

**Entry Points:**
- API calls from `.github/copilot-instructions.md`
- Shared brain across all projects
- Centralized pattern learning

**Pros:**
- ✅ Single brain for entire organization
- ✅ Cross-project pattern sharing
- ✅ Centralized management
- ✅ Minimal per-project setup

**Cons:**
- ⚠️ Requires infrastructure
- ⚠️ Network dependency
- ⚠️ More complex setup
- ⚠️ Security/privacy considerations

---

## 🎯 Recommended Implementation: Mode 2 (Embedded)

### Why Mode 2?

**Balance of Portability + Power:**
- Works in ANY repository (no folder structure assumptions)
- Cross-platform (Windows, macOS, Linux)
- Team-friendly (commit to Git, everyone gets it)
- Simple installation (one command)
- Isolated brains (project-specific memory)

### Implementation Steps

#### Step 1: Create Portable CORTEX Core

**File:** `.cortex/cortex-core.py` (or `.cortex/cortex-core.ts`)

```python
"""
Portable CORTEX Core - Works in any repository

Features:
- Auto-detects project structure (no assumptions)
- Creates brain in .cortex/ folder
- Platform-agnostic (Windows, macOS, Linux)
- Minimal dependencies
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

class PortableCortex:
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or self._detect_repo_root()
        self.cortex_dir = self.repo_root / ".cortex"
        self.brain_dir = self.cortex_dir / "brain"
        self.config_file = self.cortex_dir / "config.json"
        
    def _detect_repo_root(self) -> Path:
        """Detect repository root (works with any structure)"""
        current = Path.cwd()
        
        # Look for .git folder
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        # Fallback to current directory
        return Path.cwd()
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize CORTEX in current repository"""
        # Create .cortex structure
        self.cortex_dir.mkdir(exist_ok=True)
        (self.brain_dir / "tier1").mkdir(parents=True, exist_ok=True)
        (self.brain_dir / "tier2").mkdir(parents=True, exist_ok=True)
        (self.brain_dir / "tier3").mkdir(parents=True, exist_ok=True)
        
        # Create default config
        config = {
            "version": "2.0",
            "repo_root": str(self.repo_root),
            "brain_path": str(self.brain_dir),
            "platform": sys.platform,
            "created": "2025-11-09"
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "cortex_dir": str(self.cortex_dir)}
```

#### Step 2: Create Installation Script

**File:** `scripts/install-cortex-embedded.sh`

```bash
#!/bin/bash
# Install CORTEX in any repository

set -e

echo "🧠 Installing CORTEX in current repository..."

# Detect repository root
if [ -d ".git" ]; then
    REPO_ROOT="$(pwd)"
else
    echo "❌ Not a Git repository"
    exit 1
fi

# Create .cortex structure
mkdir -p .cortex/brain/{tier1,tier2,tier3}
mkdir -p .github/prompts

# Download CORTEX core (from GitHub release or NPM)
curl -sL https://github.com/asifhussain60/CORTEX/releases/latest/download/cortex-core.py \
    -o .cortex/cortex-core.py

# Create entry point prompt
cat > .github/prompts/CORTEX.prompt.md << 'EOF'
# CORTEX - Your Cognitive Development Partner

You are using CORTEX, an AI cognitive enhancement system that provides:
- Memory across conversations (Tier 1)
- Pattern learning (Tier 2)
- Project intelligence (Tier 3)

## How to Use

Just describe what you need in natural language:
- "Add user authentication"
- "Continue from where we left off"
- "Test the new feature"
- "Make it purple" (references earlier context)

CORTEX will route your request to specialist agents and handle the rest.

## Project-Specific Context

[Auto-generated from .cortex/brain/]

## Available Commands

- `/continue` - Resume your last conversation
- `/patterns` - Show learned patterns
- `/metrics` - Project health metrics
- `/plan [feature]` - Create implementation plan
EOF

# Create baseline instructions
cat > .github/copilot-instructions.md << 'EOF'
# Project Development Instructions

This repository uses CORTEX for cognitive development assistance.

## CORTEX Capabilities

- **Memory:** Remembers last 20 conversations across sessions
- **Learning:** Accumulates patterns from every interaction
- **Intelligence:** Understands your project structure and conventions

## How CORTEX Works

When you ask for help, CORTEX:
1. Checks Tier 1 (recent conversations) for context
2. Consults Tier 2 (learned patterns) for best practices
3. Analyzes Tier 3 (project metrics) for optimal approach
4. Routes to specialist agent (planner, executor, tester, etc.)

## Usage

Use `/CORTEX` for full capabilities, or just ask naturally.
CORTEX runs in the background and provides context automatically.
EOF

# Initialize brain
python3 .cortex/cortex-core.py init

echo "✅ CORTEX installed successfully!"
echo ""
echo "Next steps:"
echo "  1. Commit .cortex/ and .github/ to your repo"
echo "  2. Team members get CORTEX automatically on clone"
echo "  3. Use /CORTEX in GitHub Copilot Chat"
```

#### Step 3: Create GitHub Copilot Integration

**File:** `.github/copilot-instructions.md`

```markdown
# CORTEX-Enabled Repository

This repository uses CORTEX cognitive assistance.

## Project Type

[Auto-detected: TypeScript/React/Node.js]

## CORTEX Status

- Tier 1 (Memory): 15/20 conversations stored
- Tier 2 (Patterns): 247 patterns learned
- Tier 3 (Metrics): 89% test coverage, 12 hotspots

## Development Context

CORTEX has learned that this project:
- Uses React 18 with TypeScript
- Prefers functional components with hooks
- Has 89% test coverage (pytest)
- Uses Material-UI for components
- Follows feature-based folder structure

## Common Patterns

1. **New Feature:** Test-first development (94% success rate)
2. **Bug Fix:** Reproduce via test, then fix (87% success rate)
3. **Refactoring:** Run tests before+after (100% success rate)

## Quick Commands

- Use `/CORTEX` for full entry point
- Use `/continue` to resume work
- Use `/patterns` to see what CORTEX learned

CORTEX provides automatic context - just describe what you need.
```

**File:** `.github/prompts/CORTEX.prompt.md`

```markdown
# CORTEX Universal Entry Point

[Include full cortex.md content here, but with project-specific paths]

This is an embedded CORTEX instance running in YOUR project.

Brain location: `.cortex/brain/`
Config: `.cortex/config.json`

All features work exactly like standalone CORTEX, but isolated to this project.

[Rest of cortex.md content...]
```

#### Step 4: Cross-Platform Compatibility

**Key Requirements:**

1. **Path Resolution:**
   ```python
   # Always use Path objects (cross-platform)
   from pathlib import Path
   
   brain_path = Path(".cortex") / "brain"  # Works on Windows/Mac/Linux
   ```

2. **Platform Detection:**
   ```python
   import sys
   
   if sys.platform == "darwin":
       # macOS-specific
   elif sys.platform.startswith("win"):
       # Windows-specific
   elif sys.platform.startswith("linux"):
       # Linux-specific
   ```

3. **No Hardcoded Paths:**
   ```python
   # ❌ BAD
   brain_path = "/Users/asif/PROJECTS/CORTEX/cortex-brain"
   
   # ✅ GOOD
   brain_path = self.repo_root / ".cortex" / "brain"
   ```

---

## 📊 Comparison Matrix

| Feature | Mode 1: Standalone | Mode 2: Embedded | Mode 3: Service |
|---------|-------------------|------------------|-----------------|
| **Portability** | ❌ Single repo only | ✅ Any repo | ✅ Any repo |
| **Installation** | N/A (is CORTEX) | ⚡ One command | ⚡ One command |
| **Cross-Platform** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Team Sharing** | ❌ N/A | ✅ Via Git | ✅ Via API |
| **Brain Isolation** | N/A | ✅ Per-project | ⚠️ Shared |
| **Setup Complexity** | N/A | ⭐ Low | ⭐⭐⭐ High |
| **Maintenance** | N/A | ⭐ Low | ⭐⭐⭐ High |
| **Infrastructure** | None | None | ⚠️ Server required |
| **Use Case** | CORTEX dev | Projects | Enterprise |

---

## 🎯 Final Recommendation

### Implement Mode 2 (Embedded) NOW

**Why:**
1. ✅ Works in **any repository** (no folder structure assumptions)
2. ✅ **Cross-platform** (Windows, macOS, Linux) 
3. ✅ **Simple installation** (one script, one command)
4. ✅ **Team-friendly** (commit to Git, everyone gets it)
5. ✅ **Uses GitHub Copilot standards** (`.github/copilot-instructions.md` + `.github/prompts/`)
6. ✅ **Solves original problem:** Simple entry point (`/CORTEX` instead of long file path)

**Implementation Path:**

### Phase 1: Create Portable Core (Week 1)
- [ ] Extract core CORTEX logic to standalone module
- [ ] Make path resolution dynamic (no hardcoded paths)
- [ ] Create `.cortex/` initialization script
- [ ] Test on Windows, macOS, Linux

### Phase 2: GitHub Copilot Integration (Week 1)
- [ ] Create `.github/copilot-instructions.md` template
- [ ] Create `.github/prompts/CORTEX.prompt.md` template
- [ ] Test `/CORTEX` command in Copilot Chat
- [ ] Verify auto-loading of copilot-instructions.md

### Phase 3: Installation Automation (Week 2)
- [ ] Create `install-cortex-embedded.sh` script
- [ ] Create `install-cortex-embedded.ps1` (Windows)
- [ ] Add to NPM as `npx create-cortex-brain`
- [ ] Add to PyPI as `pip install cortex-ai; cortex init`

### Phase 4: Documentation & Testing (Week 2)
- [ ] Update README.md with embedded mode instructions
- [ ] Create tutorial: "Using CORTEX in Your Project"
- [ ] Test in 3+ different repo structures
- [ ] Test on Windows, macOS, Linux

### Phase 5: Migration Path (Week 3)
- [ ] Add to existing CORTEX repo (eating own dog food)
- [ ] Deprecate hardcoded paths gracefully
- [ ] Provide migration guide for existing users
- [ ] Support both modes during transition

---

## 🚀 Quick Win: Implement in Current Repo

**You can do this RIGHT NOW in 10 minutes:**

1. **Create `.github/copilot-instructions.md`:**
   ```markdown
   # CORTEX Repository
   
   This is the CORTEX cognitive framework project.
   
   Use `/CORTEX` for full entry point.
   
   [Brief project description]
   ```

2. **Create `.github/prompts/CORTEX.prompt.md`:**
   ```markdown
   [Copy prompts/user/cortex.md content here]
   ```

3. **Enable prompt files in VS Code:**
   - Open Command Palette (Cmd+Shift+P)
   - Search "Open Workspace Settings (JSON)"
   - Add: `"chat.promptFiles": true`

4. **Test:**
   - Open Copilot Chat
   - Type `/CORTEX`
   - Should load full entry point!

**Result:** Simple `/CORTEX` command instead of `#file:prompts/user/cortex.md`

---

## 📋 Success Criteria

**Mode 2 (Embedded) is successful when:**

- ✅ Can install CORTEX in **any Git repository** with one command
- ✅ Works on **Windows, macOS, and Linux** without modification
- ✅ Entry point is simple: `/CORTEX` (not long file path)
- ✅ Team members get CORTEX automatically on `git clone`
- ✅ Project-specific brain (isolated from other projects)
- ✅ Zero external dependencies (no servers, no APIs)
- ✅ Follows GitHub Copilot conventions (`.github/` structure)

---

## 🔮 Future: Mode 3 (Service)

After Mode 2 is stable, consider Mode 3 for enterprise:

**Benefits:**
- Shared brain across ALL projects in organization
- Cross-project pattern learning
- Centralized management
- Team-wide knowledge accumulation

**Implementation:**
- CORTEX server with REST API
- Client libraries (npm, pip)
- Authentication and authorization
- Cloud deployment (AWS, Azure, GCP)

**Timeline:** 3-6 months after Mode 2 launch

---

## 📚 Related Documents

- **23-modular-entry-point.md:** Original modular architecture
- **31-human-readable-documentation-system.md:** Documentation strategy
- **37-documentation-architecture.md:** Single source of truth
- **prompts/user/cortex.md:** Current entry point

---

## ✅ Decision

**RECOMMEND: Implement Mode 2 (Embedded CORTEX)**

**Rationale:**
- Solves portability problem (works in any repo)
- Solves cross-platform problem (Windows/Mac/Linux)
- Solves entry point problem (`/CORTEX` vs long path)
- Solves team collaboration (commit to Git)
- Follows GitHub standards (`.github/` conventions)
- Simple installation (one command)
- Zero infrastructure required

**Next Steps:**
1. Get approval for Mode 2 approach
2. Start Phase 1 (Portable Core)
3. Quick win: Implement in CORTEX repo first
4. Iterate based on feedback

---

*Last Updated: 2025-11-09 | Status: Recommendation*
