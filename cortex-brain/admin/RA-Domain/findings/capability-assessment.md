# CORTEX AST Capability Assessment

**Purpose:** Document current AST scanning capabilities and gaps for C#/.NET analysis  
**Status:** 🟡 ASSESSMENT REQUIRED  
**Created:** December 11, 2025

---

## 🎯 Assessment Questions

### 1. Current AST Capabilities

**Question:** Does CORTEX have existing AST scanning for C#/.NET?

**Investigation Steps:**
- [ ] Search for C# parser implementations in `src/orchestrators/`
- [ ] Check for Roslyn integration in dependencies
- [ ] Review `requirements.txt` for .NET parsing libraries
- [ ] Search for AST-related modules in codebase

**Expected Findings:**
- Existing Python AST scanner (likely)
- C#/.NET support: TBD
- Gap assessment required

---

### 2. Required Capabilities for RA Domain

**Minimum Requirements:**
1. Parse C# syntax (classes, methods, properties)
2. Extract type information (inheritance, generics)
3. Analyze attributes (Entity Framework, WebAPI, etc.)
4. Parse XML (.csproj files for dependencies)
5. Map relationships between types

**Nice-to-Have:**
1. Semantic analysis (method call graphs)
2. Control flow analysis
3. Data flow analysis
4. Symbol resolution across projects

---

### 3. Technology Options

#### Option A: Roslyn (Microsoft.CodeAnalysis)
**Pros:**
- Official Microsoft compiler platform
- Full semantic analysis
- Supports all C# versions
- Rich API for syntax/semantic queries

**Cons:**
- .NET runtime required
- Complex integration from Python
- Requires .NET interop (pythonnet, subprocess, or REST API)

**Feasibility:** HIGH (if .NET available on machine)

---

#### Option B: Tree-sitter (C# Grammar)
**Pros:**
- Pure syntax parsing (no .NET required)
- Python bindings available (`py-tree-sitter`)
- Fast and lightweight
- Supports multiple languages

**Cons:**
- Syntax only (no semantic analysis)
- No type resolution
- Limited attribute parsing

**Feasibility:** MEDIUM (good for basic parsing)

---

#### Option C: External CLI Tools + JSON Output
**Pros:**
- Leverage existing tools (dotnet list package, etc.)
- No parser development needed
- JSON output easy to consume

**Cons:**
- Limited to what tools provide
- No custom queries
- Requires .NET SDK installed

**Feasibility:** HIGH (quick start, limited depth)

---

#### Option D: Hybrid Approach
**Strategy:**
1. Use Tree-sitter for syntax parsing
2. Use dotnet CLI for dependency extraction
3. Use grep/regex for attribute extraction
4. Build custom relationship mapper

**Pros:**
- No .NET interop complexity
- Achieves 80% of requirements
- Python-native implementation

**Cons:**
- Less accurate than Roslyn
- Manual relationship mapping
- Limited semantic analysis

**Feasibility:** HIGH (recommended starting point)

---

## 🔍 Investigation Tasks

### Task 1: Check CORTEX Existing AST Infrastructure
```powershell
# Search for existing AST implementations
cd C:\PROJECTS\CORTEX
Select-String -Path src\**\*.py -Pattern "ast\.|AST|parse_tree|syntax_tree"

# Check for existing code analyzers
Get-ChildItem -Path src\orchestrators -Recurse -Filter *analyzer*.py
Get-ChildItem -Path src\orchestrators -Recurse -Filter *parser*.py
```

**Expected Output:** List of existing AST-related modules

---

### Task 2: Check Python Environment for Parsing Libraries
```powershell
# Check installed packages
pip list | Select-String "tree-sitter|roslyn|pythonnet"

# Check requirements.txt
Get-Content requirements.txt | Select-String "tree-sitter|roslyn|pythonnet"
```

**Expected Output:** Current parser dependencies (if any)

---

### Task 3: Verify .NET Availability (for Roslyn option)
```powershell
# Check if .NET SDK installed
dotnet --version

# Check if .NET runtime available
dotnet --list-runtimes
```

**Expected Output:** .NET version (if installed)

---

### Task 4: Test Basic C# Parsing (Tree-sitter)
```python
# Sample Python script to test tree-sitter C# parsing
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp

# Build parser
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser()
parser.set_language(CS_LANGUAGE)

# Test on sample C# code
code = b"""
public class ReimbursementAccount
{
    public int Id { get; set; }
    public string AccountNumber { get; set; }
}
"""

tree = parser.parse(code)
print(tree.root_node.sexp())
```

**Expected Output:** S-expression AST of C# class

---

## 📊 Gap Analysis Template

| Capability | Required | Current Status | Gap | Solution |
|------------|----------|----------------|-----|----------|
| Parse C# syntax | ✅ YES | ⏳ TBD | ⏳ TBD | Tree-sitter or Roslyn |
| Extract classes | ✅ YES | ⏳ TBD | ⏳ TBD | AST traversal |
| Extract properties | ✅ YES | ⏳ TBD | ⏳ TBD | AST traversal |
| Parse attributes | ✅ YES | ⏳ TBD | ⏳ TBD | Attribute syntax parsing |
| Type resolution | 🟡 NICE | ⏳ TBD | ⏳ TBD | Roslyn (full) or Manual (partial) |
| Parse .csproj (XML) | ✅ YES | ⏳ TBD | ⏳ TBD | Python xml.etree |
| Relationship mapping | ✅ YES | ⏳ TBD | ⏳ TBD | Custom graph builder |
| Method call graphs | 🟡 NICE | ⏳ TBD | ⏳ TBD | Roslyn or manual |

**Legend:**
- ✅ YES = Required for RA domain analysis
- 🟡 NICE = Nice to have, not critical
- ⏳ TBD = To be determined after investigation

---

## 🚀 Recommended Path Forward

### Phase 1: Rapid Assessment (30 mins)
1. Run investigation tasks above
2. Fill out gap analysis table
3. Choose technology stack (recommend Hybrid Approach)

### Phase 2: Proof of Concept (2 hours)
1. Install chosen parser (tree-sitter-c-sharp recommended)
2. Parse 5 sample files from RA domain
3. Extract basic entities and properties
4. Validate accuracy vs manual inspection

### Phase 3: Full Implementation (4-6 hours)
1. Build C# AST scanner orchestrator
2. Implement all test scenarios from `test-scenarios.md`
3. Generate analysis reports
4. Document findings and limitations

---

## 📝 Notes Section

**Investigation Date:** _________________  
**Investigator:** _________________

**Findings:**
- [ ] Existing AST capabilities: _________________
- [ ] Chosen technology: _________________
- [ ] Gaps identified: _________________
- [ ] Estimated effort: _________________

**Blockers:**
- None expected for read-only analysis
- May need .NET SDK if Roslyn chosen

---

**Next:** Complete investigation tasks and update this document with findings.

