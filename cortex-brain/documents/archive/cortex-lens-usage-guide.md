# CORTEX Lens Usage Guide

**Component:** Legacy Specification Generator  
**Version:** 3.0.0 (OpenAPI Generation)  
**Path Policy:** Fully Parameterized - No Hardcoded Paths

---

## 🎯 Purpose

CORTEX Lens capabilities are **path-agnostic tools** that work with any user-specified directory. All outputs are written to the location the user provides via command-line arguments.

---

## 📁 Path Architecture

### ✅ Correct: User-Specified Paths

**Pattern:**
```bash
python <cortex_tool> <input_file> <output_directory>
```

**Examples:**
```bash
# Output to Platform.Classic repository
python legacy_spec_generator.py \
  "C:\Code\MyApp\Services\MyAPI.cs" \
  "C:\Projects\Platform.Classic\specs\myapi"

# Output to separate documentation repository
python legacy_spec_generator.py \
  "C:\Code\MyApp\Services\MyAPI.cs" \
  "C:\Docs\api-specs\myapi"

# Output to temporary directory for review
python legacy_spec_generator.py \
  "C:\Code\MyApp\Services\MyAPI.cs" \
  "C:\Temp\review\myapi"

# Output to network share
python legacy_spec_generator.py \
  "C:\Code\MyApp\Services\MyAPI.cs" \
  "\\Server\Share\specs\myapi"
```

### ❌ Incorrect: Hardcoded Paths

**Never do this in CORTEX tools:**
```python
# WRONG - Hardcoded path
output_dir = Path("C:\\PROJECTS\\Platform.Classic\\cortex\\ra-api-specs")

# WRONG - Assumed repository structure
output_dir = Path.cwd() / "Platform.Classic" / "specs"

# WRONG - Environment-specific path
output_dir = Path(os.getenv("PROJECT_ROOT")) / "specs"
```

**Always do this:**
```python
# CORRECT - Accept path as parameter
def __init__(self, legacy_file: Path, output_dir: Path):
    self.legacy_file = legacy_file
    self.output_dir = output_dir  # User-provided, not hardcoded
```

---

## 🛠️ CORTEX Lens Generator

### Command Line Interface

**Syntax:**
```bash
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py \
  <legacy_file> \
  <output_directory>
```

**Parameters:**
- `<legacy_file>` - Absolute path to legacy C# file to analyze
- `<output_directory>` - Absolute path where specs will be generated

**No defaults, no assumptions about directory structure.**

---

### Generated Outputs

All files written to `<output_directory>`:

1. **business-spec.md** - PM/BA specification with user stories
2. **traceability-matrix.md** - Line-by-line legacy→modern mapping
3. **openapi.yaml** - OpenAPI 3.0 specification (YAML format)
4. **openapi.json** - OpenAPI 3.0 specification (JSON format)

**Output Structure:**
```
<output_directory>/
├── business-spec.md
├── traceability-matrix.md
├── openapi.yaml
└── openapi.json
```

---

## 📊 Usage Examples

### Example 1: Platform.Classic Documentation

```bash
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py \
  "C:\PROJECTS\Platform.Classic\Segment4\HETransactions\XGenerateFundingInvoice.cs" \
  "C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\xgeneratefundinginvoice"
```

**Result:**
```
C:\PROJECTS\Platform.Classic\cortex\ra-api-specs\specifications\xgeneratefundinginvoice\
├── business-spec.md
├── traceability-matrix.md
├── openapi.yaml
└── openapi.json
```

---

### Example 2: Separate Documentation Repository

```bash
python C:\PROJECTS\CORTEX\src\operations\modules\generators\legacy_spec_generator.py \
  "C:\Code\HealthEquity\Libs\HEInteraction\Services\Updaters\Updater_CreateRAFundingInvoices.cs" \
  "C:\Docs\HealthEquity\API-Specs\updater-createrafundinginvoices"
```

**Result:**
```
C:\Docs\HealthEquity\API-Specs\updater-createrafundinginvoices\
├── business-spec.md
├── traceability-matrix.md
├── openapi.yaml
└── openapi.json
```

---

### Example 3: Multiple Repositories

```bash
# Team A: Output to their docs repo
python legacy_spec_generator.py \
  "C:\TeamA\Services\API.cs" \
  "C:\TeamA-Docs\specs\api"

# Team B: Output to their project folder
python legacy_spec_generator.py \
  "C:\TeamB\Services\API.cs" \
  "C:\TeamB\Project\documentation\api-specs"

# Team C: Output to shared network location
python legacy_spec_generator.py \
  "C:\TeamC\Services\API.cs" \
  "\\CompanyShare\Documentation\TeamC\api"
```

---

## 🔧 Integration Patterns

### CI/CD Pipeline

```yaml
# Azure DevOps Pipeline Example
steps:
- task: PythonScript@0
  inputs:
    scriptSource: 'filePath'
    scriptPath: '$(CORTEX_PATH)/src/operations/modules/generators/legacy_spec_generator.py'
    arguments: '$(SourceFile) $(Pipeline.Workspace)/specs/$(APIName)'
```

### Batch Processing

```powershell
# PowerShell script to process multiple APIs
$apis = @(
    @{File="C:\Code\API1.cs"; Output="C:\Specs\api1"}
    @{File="C:\Code\API2.cs"; Output="C:\Specs\api2"}
    @{File="C:\Code\API3.cs"; Output="C:\Specs\api3"}
)

foreach ($api in $apis) {
    python C:\CORTEX\src\operations\modules\generators\legacy_spec_generator.py `
        $api.File `
        $api.Output
}
```

### Programmatic Usage

```python
from pathlib import Path
from cortex.generators import LegacySpecGenerator

# User specifies paths
input_file = Path("C:/MyProject/Services/MyAPI.cs")
output_dir = Path("C:/MyDocs/specs/myapi")

# No hardcoded paths in CORTEX tool
generator = LegacySpecGenerator(input_file, output_dir)
generator.analyze()
generator.generate_all()
```

---

## ✅ Design Principles

### 1. Path Agnosticism
- **Never assume** repository structure
- **Never hardcode** output locations
- **Always accept** paths as parameters
- **Always use** absolute paths for clarity

### 2. Repository Separation
- **CORTEX repo** = Tools, generators, utilities
- **User repos** = Inputs (source code) and outputs (documentation)
- **No coupling** between CORTEX and user directory structures

### 3. Flexibility
- **Any source** - Local, network, cloud storage
- **Any destination** - Project folder, docs repo, temp directory
- **Any structure** - Flat, nested, arbitrary organization

### 4. Portability
- **Works anywhere** - Developer machines, CI/CD servers, containers
- **No environment variables** - All paths explicit
- **No configuration files** - Pure command-line arguments

---

## 🚨 Common Mistakes

### Mistake 1: Assuming Platform.Classic Exists

```python
# WRONG
output_dir = Path("C:/PROJECTS/Platform.Classic/cortex/ra-api-specs")

# CORRECT
output_dir = Path(sys.argv[2])  # User provides path
```

### Mistake 2: Relative Paths

```python
# WRONG - Depends on current working directory
output_dir = Path("../specs/api")

# CORRECT - Absolute paths always
output_dir = Path("C:/MyProject/specs/api")
```

### Mistake 3: Hardcoded Separators

```python
# WRONG - Windows-specific
output_file = output_dir + "\\" + "spec.md"

# CORRECT - Cross-platform
output_file = output_dir / "spec.md"
```

---

## 📝 Tool Checklist

Before adding any new CORTEX Lens capability:

- [ ] Tool accepts `input_file` and `output_dir` as parameters
- [ ] No hardcoded paths in implementation
- [ ] All outputs written to `output_dir`
- [ ] Command-line interface documents path requirements
- [ ] Example usage shows different output locations
- [ ] Works with absolute paths
- [ ] No assumptions about repository structure

---

## 🎯 Summary

**CORTEX Philosophy:**
> "Build tools, not assumptions. Accept paths, don't dictate them."

**Key Takeaway:**
Every CORTEX Lens capability must work with **any** user-specified path. The tool lives in CORTEX repository, but outputs go wherever the user wants.

**Verification:**
If you can run the tool with 5 different output directories without changing code, it's correctly designed.

---

**Version:** 3.0.0  
**Status:** Production Ready  
**Path Policy:** Fully Parameterized
