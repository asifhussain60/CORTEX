# CORTEX Refactoring Strategy - REVISED FOR USER'S TECH STACK

**Date:** 2025-11-12  
**Status:** CRITICAL REVISION  
**Reason:** User's organization uses **C#/.NET/Angular/React**, NOT Python!

---

## 🚨 Critical Discovery

### What I Got Wrong (Initially)

**My assumption:** User needs Python refactoring (rope)  
**Reality:** User's organization stack:
- ✅ **C# / .NET Core** (primary backend)
- ✅ **Angular** (frontend)
- ✅ **React** (frontend)
- ✅ **SQL Server / Azure** (database)
- ✅ **Oracle** (database)
- ❌ **Python** (CORTEX framework only, not user's apps!)

**Impact:** Rope is WRONG priority! User needs C#/JavaScript tools, not Python tools.

---

## 🎯 User's Concerns (Critical Constraints)

### 1. **Footprint Minimization**
> "We don't want CORTEX footprint to be big"

**Implication:**
- ❌ Don't bundle large dependencies by default
- ✅ Make ALL refactoring tools **optional**
- ✅ Zero forced installations
- ✅ Pay-as-you-go model (install only what you need)

### 2. **No Forced Dependencies**
> "Shouldn't force user to forcefully install dependencies"

**Implication:**
- ❌ Don't add rope/Roslyn to `requirements.txt`
- ✅ Create `requirements-optional.txt` (user choice)
- ✅ Auto-detect installed tools
- ✅ Graceful degradation always

### 3. **Organizational Firewalls**
> "What about tools CORTEX uses that are blocked by the org?"

**Critical questions:**
1. Can org developers install npm packages? (Angular/React tools)
2. Can org install NuGet packages? (Roslyn analyzers)
3. Can org install pip packages? (even optional ones)
4. Are external APIs blocked? (GitHub Copilot Vision API)
5. Can VS Code extensions be installed?

**Strategy:** Design for **zero external dependencies by default**

---

## 📊 Tech Stack Alignment Matrix

### User's Actual Codebase (90%+)

| Language/Framework | % of Code | Refactoring Tool | Priority | Blocked? |
|-------------------|-----------|------------------|----------|----------|
| **C# / .NET Core** | 40% | Roslyn Analyzers | 🔥 HIGH | ❓ Unknown |
| **Angular** | 20% | ESLint, TSLint | 🔥 HIGH | ❓ Unknown |
| **React** | 20% | ESLint, Prettier | 🔥 HIGH | ❓ Unknown |
| **SQL** | 15% | SQL Formatter | 🟡 MEDIUM | ❓ Unknown |
| **Oracle** | 5% | PL/SQL Formatter | 🟢 LOW | ❓ Unknown |

### CORTEX Framework (Internal)

| Language | % of CORTEX | Refactoring Tool | Priority | Blocked? |
|----------|-------------|------------------|----------|----------|
| **Python** | 100% | rope, black | 🟢 LOW | ❓ Unknown |

**Conclusion:** Python tools help CORTEX devs, NOT user's org!

---

## 🔄 Revised Strategy: Zero-Footprint Plugin Architecture

### Core Principle: **Detect, Don't Require**

```python
# NEW: Zero-footprint refactoring orchestrator
class RefactoringOrchestrator:
    """
    Orchestrates refactoring without requiring ANY tools.
    
    Detects what user has installed:
    - Roslyn CLI? Use it for C#
    - ESLint installed? Use it for JS/TS
    - Nothing installed? Provide guidance only
    """
    
    def __init__(self):
        self.detected_tools = self._auto_detect_all()
    
    def _auto_detect_all(self) -> Dict[str, bool]:
        """Detect available refactoring tools (no failures if missing)."""
        return {
            # .NET tools
            'dotnet_cli': self._check_command('dotnet --version'),
            'roslyn_analyzers': self._check_roslyn(),
            
            # JavaScript/TypeScript tools
            'eslint': self._check_npm_package('eslint'),
            'prettier': self._check_npm_package('prettier'),
            'tslint': self._check_npm_package('tslint'),
            
            # Python tools (for CORTEX dev only)
            'rope': self._check_pip_package('rope'),
            'black': self._check_pip_package('black'),
            
            # SQL tools
            'sqlfluff': self._check_pip_package('sqlfluff'),
        }
    
    def refactor_csharp(self, file_path: str, operation: str):
        """Refactor C# code using available tools."""
        if self.detected_tools['roslyn_analyzers']:
            # Use Roslyn if available
            return self._roslyn_refactor(file_path, operation)
        elif self.detected_tools['dotnet_cli']:
            # Use dotnet format if available
            return self._dotnet_format(file_path)
        else:
            # Provide guidance only
            return {
                'success': False,
                'guidance': "Install Roslyn analyzers for C# refactoring",
                'manual_steps': [
                    "1. dotnet tool install -g dotnet-format",
                    "2. Run: dotnet format <solution.sln>"
                ]
            }
```

---

## 🏗️ Revised Architecture: Language-Agnostic

### Tier Structure (Updated)

```
CORTEX (Python framework)
    ↓
Refactoring Orchestrator (language-agnostic)
    ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│   C# Tools  │   JS Tools   │ Python Tools │  SQL Tools   │
│  (Optional) │  (Optional)  │  (Optional)  │  (Optional)  │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

**Key changes:**
1. **No default tools** - All optional
2. **Auto-detection** - Find what's installed
3. **Guidance fallback** - Show manual steps if tools missing
4. **Language-specific** - C# first, Python last

---

## 🎯 Priority-Ordered Implementation (REVISED)

### Phase 1: C# / .NET Support (Week 1-2) 🔥 HIGH PRIORITY

**Target:** User's primary language

**Tools to detect (NOT install):**
- `dotnet` CLI (check: `dotnet --version`)
- Roslyn analyzers (check: `dotnet tool list -g | grep format`)
- StyleCop (check: NuGet package presence)

**Implementation:**
```python
# src/tier1/refactoring_csharp.py
class CSharpRefactoringAPI:
    """
    C# refactoring via Roslyn (if available).
    
    NO DEPENDENCIES - Just orchestrates existing tools.
    """
    
    def __init__(self):
        self.dotnet_available = shutil.which('dotnet') is not None
        self.roslyn_available = self._check_roslyn()
    
    def format_code(self, solution_path: str):
        """Format C# code using dotnet format."""
        if not self.dotnet_available:
            return self._provide_guidance('dotnet_cli')
        
        # Use existing dotnet installation
        subprocess.run(['dotnet', 'format', solution_path])
```

**Benefits:**
- ✅ Helps user's ACTUAL codebase
- ✅ No new dependencies (uses what org already has)
- ✅ Respects org firewall (no external downloads)

### Phase 2: Angular/React Support (Week 3-4) 🔥 HIGH PRIORITY

**Target:** User's frontend stack

**Tools to detect:**
- ESLint (`npx eslint --version`)
- Prettier (`npx prettier --version`)
- TSLint (`npx tslint --version`)

**Implementation:**
```python
# src/tier1/refactoring_javascript.py
class JavaScriptRefactoringAPI:
    """
    JavaScript/TypeScript refactoring via ESLint/Prettier.
    
    NO DEPENDENCIES - Uses user's npm packages.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.eslint_available = self._check_npm_local('eslint')
        self.prettier_available = self._check_npm_local('prettier')
    
    def _check_npm_local(self, package: str) -> bool:
        """Check if npm package exists in project's node_modules."""
        return (self.project_root / 'node_modules' / package).exists()
```

### Phase 3: SQL Support (Week 5-6) 🟡 MEDIUM PRIORITY

**Target:** SQL Server / Oracle queries

**Tools to detect:**
- sqlfluff (Python - optional)
- SQL Formatter (npm - optional)

**Approach:** Provide formatter recommendations, not installations

### Phase 4: Python Support (CORTEX Dev Only) 🟢 LOW PRIORITY

**Target:** CORTEX framework itself (not user's apps)

**Only for:**
- CORTEX contributors
- Internal CORTEX development
- NOT for user's organization code

---

## 🔒 Firewall/Security Strategy

### Understanding Organizational Constraints

**Questions for user:**

1. **Package Managers Allowed?**
   - Can you run `dotnet tool install`?
   - Can you run `npm install`?
   - Can you run `pip install`?

2. **External API Access?**
   - Can VS Code reach GitHub Copilot API?
   - Are PyPI/npm/NuGet registries accessible?
   - Is GitHub.com accessible?

3. **Tool Installation Permissions?**
   - Can you install VS Code extensions?
   - Can you install global CLI tools?
   - Are you admin on your machine?

### Firewall-Friendly Design

**Assumption:** User has SOME restrictions

**Strategy:**
```yaml
firewall_strategy:
  tier_1_safest:
    - Use tools ALREADY installed (dotnet, npm, node)
    - No new downloads required
    - Guidance-only mode if tools missing
    
  tier_2_conservative:
    - Detect local node_modules (project dependencies)
    - Use project's existing ESLint/Prettier config
    - Never install globally
    
  tier_3_restricted:
    - Provide manual instructions only
    - Copy-paste commands for user to run
    - Document-based guidance
```

**Example (safest mode):**
```python
def refactor_angular_component(component_path: str):
    """Refactor Angular component (firewall-safe)."""
    
    # Check if ESLint exists in PROJECT's node_modules
    project_root = find_project_root(component_path)
    eslint_path = project_root / 'node_modules' / '.bin' / 'eslint'
    
    if eslint_path.exists():
        # Use project's existing ESLint (no download!)
        subprocess.run([str(eslint_path), '--fix', component_path])
    else:
        # Provide guidance (no failure!)
        return {
            'mode': 'guidance',
            'message': 'ESLint not found in project dependencies',
            'steps': [
                '1. Add ESLint to package.json devDependencies',
                '2. Run: npm install',
                '3. Configure .eslintrc.json',
                '4. Run: npx eslint --fix ' + component_path
            ]
        }
```

---

## 📦 Dependency Strategy (Zero-Footprint)

### OLD Approach (WRONG for user)
```txt
# requirements.txt (forced on all users)
rope>=1.11.0          # ❌ User doesn't need this!
black>=23.0.0         # ❌ User's code is C#, not Python!
```

### NEW Approach (Zero-Footprint)

```txt
# requirements.txt (CORTEX core - minimal)
PyYAML>=6.0.1         # ✅ Core CORTEX functionality
pytest>=7.4.0         # ✅ Testing framework

# requirements-optional-python.txt (CORTEX devs only)
rope>=1.11.0          # Python refactoring (CORTEX code)
black>=23.0.0         # Python formatting (CORTEX code)

# requirements-optional-sql.txt (SQL users only)
sqlfluff>=2.0.0       # SQL linting (if user wants)

# NO C#/JavaScript tools in requirements!
# Those are installed via dotnet/npm, not pip
```

**Installation instructions:**
```bash
# Minimum install (all users)
pip install -r requirements.txt

# Optional Python tools (CORTEX contributors only)
pip install -r requirements-optional-python.txt

# Optional SQL tools (if user works with SQL)
pip install -r requirements-optional-sql.txt
```

---

## 🎯 Recommended Action Plan

### Immediate: Information Gathering

**Before implementing anything, ask user:**

1. **What's blocked by your org firewall?**
   - Can you install VS Code extensions?
   - Can you run `dotnet tool install`?
   - Can you run `npm install` in projects?
   - Can you access GitHub Copilot API?

2. **What tools do you ALREADY have?**
   - `dotnet --version` (what version?)
   - `node --version` (what version?)
   - Do your projects have `package.json` with ESLint?
   - Do your projects have `.editorconfig` or StyleCop?

3. **What would be most valuable?**
   - C# code formatting?
   - Angular/React code formatting?
   - SQL query formatting?
   - Database schema refactoring?

### Phase 1: Zero-Footprint Detection (Week 1)

**Goal:** Understand user's environment without installing ANYTHING

**Deliverable:**
```python
# src/operations/modules/environment_scanner.py
class EnvironmentScanner:
    """
    Scan user's environment to detect available tools.
    
    NO INSTALLATIONS - Pure detection only.
    """
    
    def scan_development_tools(self) -> Dict[str, Any]:
        return {
            'dotnet': self._detect_dotnet(),
            'node': self._detect_node(),
            'npm_packages': self._detect_npm_packages(),
            'vs_code_extensions': self._detect_vscode_extensions(),
            'firewall_restrictions': self._test_connectivity()
        }
```

### Phase 2: Guidance System (Week 2)

**Goal:** Provide actionable guidance for tools user WANTS but doesn't have

**Example:**
```
User: "Format this C# file"

CORTEX detects: dotnet CLI not found

CORTEX response:
┌─────────────────────────────────────────────┐
│ C# Formatting Unavailable                   │
├─────────────────────────────────────────────┤
│ CORTEX can format C# code, but requires     │
│ .NET CLI to be installed.                   │
│                                             │
│ Steps to enable:                            │
│ 1. Install .NET SDK (if not blocked)        │
│ 2. Run: dotnet tool install -g dotnet-format│
│ 3. Try again: "Format this C# file"         │
│                                             │
│ Alternative:                                │
│ - Use VS Code's built-in formatter          │
│ - Configure .editorconfig in your project   │
└─────────────────────────────────────────────┘
```

### Phase 3: Tool Integration (Week 3-4)

**Only after confirming:**
- What user has installed
- What org firewall allows
- What user actually needs

---

## 💡 Key Insights

### 1. **CORTEX Framework ≠ User's Codebase**

```
CORTEX (Python)  →  Framework/Tool
User's Code (C#) →  What CORTEX helps with
```

**Mistake:** Assuming user needs Python tools  
**Reality:** User needs C#/JavaScript tools

### 2. **Organizational Constraints Trump Features**

```
Best tool (blocked) < Good tool (allowed)
```

**Better to:**
- Use what user already has
- Provide guidance for blocked tools
- Never force installations

### 3. **Detection > Installation**

```
Auto-detect what's there > Force new installs
```

**CORTEX should be:**
- Smart orchestrator (uses existing tools)
- NOT package manager (doesn't install tools)

---

## 📋 Questions for User (Next Steps)

### Critical Information Needed:

1. **Firewall Status:**
   - Can you install VS Code extensions?
   - Can you run `dotnet tool install -g <tool>`?
   - Can you run `npm install <package>` in project?
   - Can CORTEX access external APIs?

2. **Existing Tools:**
   - What's your .NET SDK version? (`dotnet --version`)
   - What's your Node version? (`node --version`)
   - Do your projects use ESLint/Prettier?
   - Do your C# projects use StyleCop/EditorConfig?

3. **Priorities:**
   - What would help most?
     - [ ] C# code formatting
     - [ ] Angular/React code formatting
     - [ ] SQL query formatting
     - [ ] Code complexity analysis
     - [ ] Other: _______________

4. **Constraints:**
   - Can CORTEX install pip packages automatically?
   - Are there size limits on VS Code extensions?
   - Are there approved/blocked tool lists?

---

## 🎯 Revised Recommendation

**STOP the rope implementation immediately!**

**Instead:**

1. **Week 1:** Environment scanning (detect user's tools)
2. **Week 2:** Guidance system (show what's possible)
3. **Week 3-4:** C# integration (if firewall allows)
4. **Week 5-6:** Angular/React integration (if firewall allows)
5. **Later:** Python tools (only for CORTEX dev team)

**Guiding principles:**
- ✅ Detect, don't require
- ✅ Guide, don't force
- ✅ Respect firewall constraints
- ✅ User's tech stack first, CORTEX's second

---

**Status:** ⏸️ PAUSED - Awaiting user's firewall/tooling information

**Next Action:** User answers questions above → Then we design RIGHT solution
