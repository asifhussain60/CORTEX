# KDS Configuration Loader

**Purpose:** Load application-specific configuration from `kds.config.json` and make variables available to all prompts.

**Version:** 1.0.0  
**Type:** Core Module (Shared)  
**Usage:** Include in all prompts that need application-specific settings

---

## 📋 Configuration Variables

After loading this module, the following variables are available:

### Application Variables

- `{{APP_NAME}}` - Application name (e.g., "KDS", "NoorCanvas", "MyProject")
- `{{APP_FRAMEWORK}}` - Frontend/backend framework (e.g., "Blazor", "React", "Vue")
- `{{APP_LANGUAGE}}` - Primary programming language (e.g., ".NET 8.0", "TypeScript", "Python")
- `{{APP_ROOT}}` - Absolute path to project root (e.g., "D:\\PROJECTS\\KDS")
- `{{BUILD_CMD}}` - Build command (e.g., "dotnet build", "npm run build")
- `{{RUN_CMD}}` - Run/start command (e.g., "dotnet run", "npm run dev")

### Testing Variables

- `{{TEST_FRAMEWORK}}` - Test framework name (e.g., "Playwright", "Cypress", "Jest")
- `{{TEST_CONFIG_PATH}}` - Path to test configuration file (e.g., "playwright.config.cjs")
- `{{TEST_ORCHESTRATION_PATTERN}}` - Orchestration pattern identifier
- `{{TEST_ORCHESTRATION_SCRIPT}}` - Script path for test orchestration
- `{{TEST_HEALTH_URL}}` - Health check URL for test environment
- `{{TEST_HEALTH_TIMEOUT}}` - Health check timeout in seconds
- `{{TEST_CMD}}` - Test execution command (e.g., "npx playwright test")
- `{{TEST_HEADLESS}}` - Default headless mode (true/false)

### Database Variables

- `{{DB_PROVIDER}}` - Database provider (e.g., "SQL Server", "PostgreSQL", "MongoDB")
- `{{DB_CONNECTION_KEY}}` - Connection string key/env variable name
- `{{DB_TEST_SESSION_ID}}` - Test session ID for development
- `{{DB_TEST_HOST_TOKEN}}` - Test host token for development

### Governance Variables

- `{{GOV_AUTO_CHAIN_TASKS}}` - Auto-chain tasks within phases (true/false)
- `{{GOV_AUTO_CHAIN_PHASES}}` - Auto-chain phases (E2E mode) (true/false)
- `{{GOV_REQUIRE_BUILD}}` - Require build validation (true/false)
- `{{GOV_REQUIRE_GIT}}` - Require git validation (true/false)
- `{{GOV_TEST_QUALITY_THRESHOLD}}` - Test quality score threshold (0-100)

---

## 🔧 How to Use in Prompts

### Step 1: Include This Module

Add this line at the top of your prompt (after the header):

```markdown
<!-- INCLUDE: core/config-loader.md -->
```

### Step 2: Use Variables

Replace hard-coded values with config variables:

**BEFORE (Hard-coded):**
```markdown
Set-Location "D:\PROJECTS\NOOR CANVAS\SPA\NoorCanvas"
dotnet build
npx playwright test --config=config/testing/playwright.config.cjs
```

**AFTER (Config-driven):**
```markdown
Set-Location "{{APP_ROOT}}"
{{BUILD_CMD}}
{{TEST_CMD}} --config={{TEST_CONFIG_PATH}}
```

### Step 3: Conditional Logic

Use variables for conditional behavior:

```markdown
{{#GOV_REQUIRE_BUILD}}
## Build Validation Required

Run build command:
{{BUILD_CMD}}

Check exit code. HALT if errors detected.
{{/GOV_REQUIRE_BUILD}}
```

---

## 📖 Configuration Loading Process

### Automatic Loading (Recommended)

When a prompt includes this module, KDS automatically:

1. ✅ Reads `kds.config.json` from project root
2. ✅ Parses JSON structure
3. ✅ Maps config fields to template variables
4. ✅ Makes variables available to prompt
5. ✅ Validates required fields are present

### Manual Loading (Advanced)

For custom scenarios:

```powershell
# PowerShell script to load config
$configPath = Join-Path $PSScriptRoot "..\..\kds.config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Access values
$appRoot = $config.application.rootPath
$buildCmd = $config.application.buildCommand
```

---

## 🚨 Error Handling

### Missing Configuration File

**Error:** `kds.config.json not found`

**Solution:**
1. Create `kds.config.json` in project root
2. Copy template from `KDS/templates/kds.config.template.json`
3. Update all fields with project-specific values
4. Run: `#file:KDS/prompts/internal/health-validator.md` to verify

### Invalid JSON

**Error:** `Failed to parse kds.config.json`

**Solution:**
1. Validate JSON syntax: https://jsonlint.com/
2. Check for trailing commas (not allowed in JSON)
3. Ensure all strings are quoted
4. Verify nested structure matches schema

### Missing Required Fields

**Error:** `Required field 'application.rootPath' not found`

**Solution:**
1. Review configuration schema
2. Add missing required fields
3. Use template as reference
4. Run validation

---

## 📋 Configuration Schema

### Required Fields

**application:**
- `name` (string) - Application name
- `framework` (string) - Framework identifier
- `language` (string) - Programming language/version
- `rootPath` (string) - Absolute path to project root

**governance:**
- `autoChainTasks` (boolean) - Enable task auto-chaining
- `autoChainPhases` (boolean) - Enable phase auto-chaining (E2E mode)
- `testQualityThreshold` (number) - Test quality minimum score (0-100)

### Optional Fields

**application:**
- `buildCommand` (string) - Build command (default: empty)
- `runCommand` (string) - Run command (default: empty)

**testing:**
- All fields optional (default to empty/null)

**database:**
- All fields optional (default to empty/null)

**governance:**
- `requireBuildValidation` (boolean, default: true)
- `requireGitValidation` (boolean, default: true)

---

## 🔍 Validation

### Validate Configuration

To check if your configuration is valid:

```markdown
#file:KDS/prompts/internal/health-validator.md
```

The health validator will:
- ✅ Check `kds.config.json` exists
- ✅ Validate JSON syntax
- ✅ Verify required fields present
- ✅ Test that paths exist
- ✅ Verify commands are executable
- ✅ Check health URL is accessible (if configured)

### Example Output

```markdown
## ✅ Configuration Validation | Status: HEALTHY

**File:** kds.config.json found ✅
**JSON:** Valid syntax ✅
**Required Fields:** All present ✅

**Path Validation:**
- application.rootPath: D:\PROJECTS\KDS ✅ (exists)

**Command Validation:**
- buildCommand: Skipped (no build required) ✅
- runCommand: Skipped (prompt system) ✅

**Test Configuration:**
- framework: None (not configured) ℹ️
- healthCheckUrl: Not configured ℹ️

**Database Configuration:**
- provider: None (not configured) ℹ️

**Governance:**
- autoChainTasks: true ✅
- autoChainPhases: false ✅
- testQualityThreshold: 70 ✅

**Overall:** Configuration is valid for current use case
```

---

## 🎯 Portability Benefits

### Before Config-Loader

**Problem:** Hard-coded paths in 50+ places across prompts

**Impact:**
- ❌ KDS only works for one specific project
- ❌ Porting to new project requires editing 50+ files
- ❌ Easy to miss hard-coded values
- ❌ High risk of breaking changes

### After Config-Loader

**Solution:** Single config file + template variables

**Impact:**
- ✅ KDS works with ANY project
- ✅ Porting requires editing 1 file (kds.config.json)
- ✅ Zero hard-coded values in prompts
- ✅ 5-minute setup time

### Porting Workflow

1. **Copy KDS folder** to new project
2. **Update kds.config.json** (5 minutes)
3. **Run validation** (`health-validator.md`)
4. **Start working** - KDS fully operational

---

## 📚 See Also

- [docs/portability-guide.md](../../docs/portability-guide.md) - Complete portability instructions
- [kds.config.json](../../kds.config.json) - Current configuration file
- [prompts/internal/health-validator.md](../internal/health-validator.md) - Configuration validation

---

**Module Version:** 1.0.0  
**Last Updated:** 2025-11-04  
**Maintained By:** KDS Core Team
