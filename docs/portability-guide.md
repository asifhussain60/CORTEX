# KDS Portability Guide

**Version:** 1.0.0  
**Date:** 2025-11-04  
**Purpose:** Complete instructions for porting KDS to a new application in 5 minutes

---

## 📋 What is KDS Portability?

KDS (Knowledge-Driven System) is designed to be **application-agnostic**. This means:

- ✅ **Zero hard-coded paths** - All project paths are in `kds.config.json`
- ✅ **Framework-agnostic** - Works with Blazor, React, Vue, Angular, Next.js, and more
- ✅ **Database-agnostic** - Supports SQL Server, PostgreSQL, MySQL, MongoDB, SQLite
- ✅ **Test framework flexible** - Works with Playwright, Cypress, Jest, Selenium, Vitest
- ✅ **5-minute setup** - Copy folder, update config, operational

---

## 🚀 Quick Start (5-Minute Setup)

### Step 1: Copy KDS Folder (30 seconds)

**From existing project:**
```bash
# Linux/Mac
cp -r /path/to/old-project/KDS /path/to/new-project/KDS

# Windows PowerShell
Copy-Item -Path "D:\OLD_PROJECT\KDS" -Destination "D:\NEW_PROJECT\KDS" -Recurse
```

**Or clone from repository:**
```bash
git clone https://github.com/yourorg/kds.git /path/to/new-project/KDS
```

### Step 2: Update kds.config.json (3 minutes)

Open `KDS/kds.config.json` and update these fields:

```json
{
  "application": {
    "name": "YOUR_PROJECT_NAME",
    "framework": "YOUR_FRAMEWORK",
    "language": "YOUR_LANGUAGE",
    "rootPath": "/absolute/path/to/your/project",
    "buildCommand": "YOUR_BUILD_COMMAND",
    "runCommand": "YOUR_RUN_COMMAND"
  },
  "testing": {
    "framework": "YOUR_TEST_FRAMEWORK",
    "configPath": "path/to/test/config",
    "testCommand": "YOUR_TEST_COMMAND",
    "healthCheckUrl": "http://localhost:YOUR_PORT"
  }
}
```

### Step 3: Validate Setup (1 minute)

Run validation:
```markdown
#file:KDS/prompts/internal/health-validator.md
```

### Step 4: Start Using KDS (30 seconds)

Create your first feature:
```markdown
#file:KDS/prompts/user/kds.md

I want to add [describe your feature]
```

**Total Time: 5 minutes** ✅

---

## 📚 Detailed Configuration Guide

### Application Section

#### Required Fields

**name** (string)
- **Purpose:** Identifies your application
- **Example:** `"MyAwesomeApp"`, `"E-Commerce Platform"`, `"KDS"`
- **Used in:** Reports, logs, dashboard titles

**framework** (string)
- **Purpose:** Frontend/backend framework identifier
- **Examples:**
  - Frontend: `"Blazor"`, `"React"`, `"Vue"`, `"Angular"`, `"Next.js"`, `"Vite"`
  - Backend: `".NET"`, `"Node.js"`, `"Django"`, `"Spring Boot"`
  - Multi: `"React + Node.js"`, `"Blazor + .NET"`
- **Used in:** Architecture detection, workflow optimization

**language** (string)
- **Purpose:** Primary programming language and version
- **Examples:**
  - `".NET 8.0"`, `"TypeScript 5.0"`, `"Python 3.11"`, `"Java 17"`
- **Used in:** Code generation patterns, syntax validation

**rootPath** (string)
- **Purpose:** Absolute path to project root directory
- **Examples:**
  - Windows: `"D:\\PROJECTS\\MyApp"`
  - Linux/Mac: `"/home/user/projects/myapp"`
- **Used in:** All file operations, path resolution
- **CRITICAL:** Must be absolute path (not relative)

#### Optional Fields

**buildCommand** (string, default: empty)
- **Purpose:** Command to build the application
- **Examples:**
  - .NET: `"dotnet build"`
  - Node.js: `"npm run build"`
  - Python: `"python setup.py build"`
  - No build: `""` (empty string)
- **Used in:** Pre-execution validation, quality gates

**runCommand** (string, default: empty)
- **Purpose:** Command to start/run the application
- **Examples:**
  - .NET: `"dotnet run"`
  - Node.js: `"npm run dev"` or `"npm start"`
  - Python: `"python manage.py runserver"`
  - Prompt system: `""` (empty string)
- **Used in:** Test orchestration, development workflow

---

### Testing Section

#### Framework Support

**Playwright** (Recommended)
```json
{
  "testing": {
    "framework": "Playwright",
    "configPath": "playwright.config.ts",
    "testCommand": "npx playwright test",
    "healthCheckUrl": "http://localhost:3000"
  }
}
```

**Cypress**
```json
{
  "testing": {
    "framework": "Cypress",
    "configPath": "cypress.config.ts",
    "testCommand": "npx cypress run",
    "healthCheckUrl": "http://localhost:3000"
  }
}
```

**Jest** (Unit tests)
```json
{
  "testing": {
    "framework": "Jest",
    "configPath": "jest.config.js",
    "testCommand": "npm test",
    "healthCheckUrl": ""
  }
}
```

**Selenium**
```json
{
  "testing": {
    "framework": "Selenium",
    "configPath": "selenium.config.json",
    "testCommand": "python -m pytest tests/",
    "healthCheckUrl": "http://localhost:8000"
  }
}
```

**No Testing** (Not recommended)
```json
{
  "testing": {
    "framework": "None",
    "configPath": "",
    "testCommand": "",
    "healthCheckUrl": ""
  }
}
```

#### Test Configuration Fields

**framework** (string, default: "None")
- Test framework identifier
- See examples above

**configPath** (string, default: "")
- Path to test configuration file (relative to rootPath)
- Examples: `"playwright.config.ts"`, `"cypress.config.js"`

**orchestrationPattern** (string, default: "")
- Identifier for orchestration approach
- Examples: `"v3.0-direct-dotnet"`, `"npm-scripts"`, `"custom"`

**orchestrationScript** (string, default: "")
- Path to custom orchestration script
- Examples: `"Scripts/run-tests.ps1"`, `"scripts/test.sh"`

**healthCheckUrl** (string, default: "")
- URL to check if application is running
- Examples: `"http://localhost:3000"`, `"https://localhost:9091"`

**healthCheckTimeout** (number, default: 30)
- Timeout in seconds for health check
- Range: 10-120 seconds recommended

**testCommand** (string, default: "")
- Command to execute tests
- Examples: `"npx playwright test"`, `"npm test"`, `"pytest"`

**headlessDefault** (boolean, default: false)
- Run tests in headless mode by default
- `true` = headless (CI/CD), `false` = headed (development)

---

### Database Section

#### Provider Support

**SQL Server**
```json
{
  "database": {
    "provider": "SQL Server",
    "connectionStringKey": "DefaultConnection",
    "testSessionId": 212,
    "testHostToken": "PQ9N5YWW"
  }
}
```

**PostgreSQL**
```json
{
  "database": {
    "provider": "PostgreSQL",
    "connectionStringKey": "DATABASE_URL",
    "testSessionId": 1,
    "testHostToken": "test-token-123"
  }
}
```

**MongoDB**
```json
{
  "database": {
    "provider": "MongoDB",
    "connectionStringKey": "MONGO_URI",
    "testSessionId": null,
    "testHostToken": ""
  }
}
```

**No Database**
```json
{
  "database": {
    "provider": "None",
    "connectionStringKey": "",
    "testSessionId": null,
    "testHostToken": ""
  }
}
```

#### Database Configuration Fields

**provider** (string, default: "None")
- Database system identifier
- Examples: `"SQL Server"`, `"PostgreSQL"`, `"MySQL"`, `"MongoDB"`, `"SQLite"`

**connectionStringKey** (string, default: "")
- Environment variable or config key for connection string
- Examples: `"DefaultConnection"`, `"DATABASE_URL"`, `"MONGO_URI"`

**testSessionId** (number/null, default: null)
- Test session ID for development/testing
- Used in test data seeding

**testHostToken** (string, default: "")
- Test host authentication token
- Used in test scenarios requiring authentication

---

### Governance Section

**autoChainTasks** (boolean, default: true)
- Automatically continue to next task within a phase
- `true` = Auto-continue with 5-second countdown
- `false` = Manual approval for each task

**autoChainPhases** (boolean, default: false)
- Automatically continue to next phase (E2E mode)
- `true` = E2E mode (auto-continue all phases)
- `false` = Manual approval after each phase (recommended)

**requireBuildValidation** (boolean, default: true)
- Run build command after each task/phase
- `true` = HALT if build fails
- `false` = Skip build validation

**requireGitValidation** (boolean, default: true)
- Check git status before/after operations
- `true` = Warn on uncommitted changes
- `false` = Skip git checks

**testQualityThreshold** (number, default: 70)
- Minimum test quality score (0-100)
- Range: 0-100
- Recommended: 70+ for production, 50+ for prototypes

---

## 🔧 Framework-Specific Examples

### Blazor + ASP.NET Core

```json
{
  "application": {
    "name": "NoorCanvas",
    "framework": "Blazor",
    "language": ".NET 8.0",
    "rootPath": "D:\\PROJECTS\\NOOR CANVAS",
    "buildCommand": "dotnet build SPA/NoorCanvas/NoorCanvas.csproj",
    "runCommand": "dotnet run --project SPA/NoorCanvas/NoorCanvas.csproj"
  },
  "testing": {
    "framework": "Playwright",
    "configPath": "config/testing/playwright.config.cjs",
    "orchestrationPattern": "v3.0-direct-dotnet",
    "orchestrationScript": "Scripts/Start-NoorCanvasForTests.ps1",
    "healthCheckUrl": "https://localhost:9091",
    "healthCheckTimeout": 30,
    "testCommand": "npx playwright test",
    "headlessDefault": false
  },
  "database": {
    "provider": "SQL Server",
    "connectionStringKey": "DefaultConnection",
    "testSessionId": 212,
    "testHostToken": "PQ9N5YWW"
  }
}
```

### React + TypeScript + Vite

```json
{
  "application": {
    "name": "MyReactApp",
    "framework": "React + Vite",
    "language": "TypeScript 5.0",
    "rootPath": "/home/user/projects/react-app",
    "buildCommand": "npm run build",
    "runCommand": "npm run dev"
  },
  "testing": {
    "framework": "Playwright",
    "configPath": "playwright.config.ts",
    "orchestrationPattern": "npm-scripts",
    "orchestrationScript": "npm test",
    "healthCheckUrl": "http://localhost:5173",
    "healthCheckTimeout": 30,
    "testCommand": "npx playwright test",
    "headlessDefault": false
  },
  "database": {
    "provider": "PostgreSQL",
    "connectionStringKey": "DATABASE_URL",
    "testSessionId": 1,
    "testHostToken": ""
  }
}
```

### Vue + Node.js + Express

```json
{
  "application": {
    "name": "VueExpressApp",
    "framework": "Vue + Node.js",
    "language": "TypeScript 5.0",
    "rootPath": "/Users/dev/projects/vue-app",
    "buildCommand": "npm run build",
    "runCommand": "npm run serve"
  },
  "testing": {
    "framework": "Cypress",
    "configPath": "cypress.config.ts",
    "orchestrationPattern": "custom",
    "orchestrationScript": "scripts/run-tests.sh",
    "healthCheckUrl": "http://localhost:8080",
    "healthCheckTimeout": 30,
    "testCommand": "npx cypress run",
    "headlessDefault": true
  },
  "database": {
    "provider": "MongoDB",
    "connectionStringKey": "MONGO_URI",
    "testSessionId": null,
    "testHostToken": ""
  }
}
```

### Python + Django

```json
{
  "application": {
    "name": "DjangoProject",
    "framework": "Django",
    "language": "Python 3.11",
    "rootPath": "/home/user/django-project",
    "buildCommand": "python manage.py collectstatic --noinput",
    "runCommand": "python manage.py runserver"
  },
  "testing": {
    "framework": "Selenium",
    "configPath": "selenium.config.json",
    "orchestrationPattern": "pytest",
    "orchestrationScript": "scripts/run-selenium-tests.sh",
    "healthCheckUrl": "http://localhost:8000",
    "healthCheckTimeout": 30,
    "testCommand": "python -m pytest tests/selenium/",
    "headlessDefault": true
  },
  "database": {
    "provider": "PostgreSQL",
    "connectionStringKey": "DATABASE_URL",
    "testSessionId": 1,
    "testHostToken": "test-user-token"
  }
}
```

---

## ✅ Post-Setup Validation

### Run Health Check

```markdown
#file:KDS/prompts/internal/health-validator.md
```

### Expected Output

```markdown
## ✅ Configuration Validation | Status: HEALTHY

**File:** kds.config.json found ✅
**JSON:** Valid syntax ✅
**Required Fields:** All present ✅

**Path Validation:**
- application.rootPath: /path/to/project ✅ (exists)

**Command Validation:**
- buildCommand: npm run build ✅ (executable)
- runCommand: npm run dev ✅ (executable)

**Test Configuration:**
- framework: Playwright ✅
- configPath: playwright.config.ts ✅ (exists)
- healthCheckUrl: http://localhost:3000 ⚠️ (not accessible - app not running)
- testCommand: npx playwright test ✅ (executable)

**Database Configuration:**
- provider: PostgreSQL ✅
- connectionStringKey: DATABASE_URL ✅

**Governance:**
- autoChainTasks: true ✅
- autoChainPhases: false ✅
- testQualityThreshold: 70 ✅

**Overall:** Configuration is valid ✅
**Next:** Start using KDS with `#file:KDS/prompts/user/kds.md`
```

---

## 🚨 Troubleshooting

### Common Issues

#### Issue: "kds.config.json not found"

**Cause:** File missing or in wrong location

**Solution:**
```bash
# Check if file exists
ls KDS/kds.config.json

# If missing, create from template
cp KDS/templates/kds.config.template.json KDS/kds.config.json
```

#### Issue: "Path does not exist: /path/to/project"

**Cause:** `application.rootPath` is incorrect

**Solution:**
1. Get absolute path to your project:
   ```bash
   # Linux/Mac
   pwd
   
   # Windows PowerShell
   (Get-Location).Path
   ```
2. Update `application.rootPath` in config
3. Re-run validation

#### Issue: "Command not found: npm run build"

**Cause:** Build command is incorrect or npm not in PATH

**Solution:**
1. Test command manually:
   ```bash
   npm run build
   ```
2. If fails, check:
   - Is npm installed? (`npm --version`)
   - Is command correct in package.json?
   - Are you in the right directory?
3. Update `application.buildCommand` in config

#### Issue: "Health check failed"

**Cause:** Application not running or wrong URL

**Solution:**
1. Start your application manually
2. Verify health check URL in browser
3. Update `testing.healthCheckUrl` if needed
4. Re-run validation

---

## 📊 Migration Checklist

Use this checklist when porting KDS to a new project:

- [ ] Copy KDS folder to new project
- [ ] Open `kds.config.json`
- [ ] Update `application.name`
- [ ] Update `application.framework`
- [ ] Update `application.language`
- [ ] Update `application.rootPath` (absolute path)
- [ ] Update `application.buildCommand`
- [ ] Update `application.runCommand`
- [ ] Update `testing.framework` (if applicable)
- [ ] Update `testing.configPath` (if applicable)
- [ ] Update `testing.testCommand` (if applicable)
- [ ] Update `testing.healthCheckUrl` (if applicable)
- [ ] Update `database.provider` (if applicable)
- [ ] Update `database.connectionStringKey` (if applicable)
- [ ] Review governance settings
- [ ] Run validation: `#file:KDS/prompts/internal/health-validator.md`
- [ ] Verify all checks pass
- [ ] Test with first feature: `#file:KDS/prompts/user/kds.md`

**Total Time: ~5 minutes** ✅

---

## 🎯 Benefits of Portability

### Before Portability (v2.x)

**Problem:**
- Hard-coded paths in 50+ prompt files
- Framework-specific logic scattered everywhere
- Porting required editing dozens of files
- Easy to miss hard-coded values
- High risk of breaking changes
- 10+ hours to port to new project

### After Portability (v6.0+)

**Solution:**
- Single config file (`kds.config.json`)
- All prompts use template variables
- Porting requires editing 1 file
- Validation catches missing values
- Zero risk of broken prompts
- **5 minutes to port to new project** ✅

### Real-World Impact

**Scenario:** You want to use KDS for a new React project

**v2.x (Hard-coded):**
1. Copy KDS folder
2. Search for "NoorCanvas" in all files → 50+ matches
3. Replace with "MyReactApp"
4. Search for "D:\\PROJECTS" → 30+ matches
5. Replace with new path
6. Search for "dotnet" → 20+ matches
7. Replace with "npm"
8. Test extensively, fix broken logic
9. **Total time: 10+ hours** ❌

**v6.0+ (Config-driven):**
1. Copy KDS folder
2. Edit `kds.config.json` (15 fields)
3. Run validation
4. Start working
5. **Total time: 5 minutes** ✅

---

## 📚 Next Steps

### After Successful Setup

1. **Learn the basics:**
   - Read: `KDS/README.md`
   - Try: `#file:KDS/prompts/user/kds.md I want to add a hello world feature`

2. **Understand the architecture:**
   - Read: `KDS/docs/KDS-V6-EXECUTIVE-SUMMARY.md`
   - Review: `KDS/docs/KDS-V6-QUICK-START.md`

3. **Explore advanced features:**
   - Brain system: `KDS/docs/architecture/BRAIN-CONVERSATION-MEMORY-DESIGN.md`
   - Test-driven development: `KDS/TDD-QUICK-REFERENCE.md`
   - Dashboard: `KDS/dashboard/README.md`

4. **Customize to your workflow:**
   - Edit templates: `KDS/templates/`
   - Adjust governance: `kds.config.json` → `governance` section
   - Configure testing: `kds.config.json` → `testing` section

---

## 🤝 Support & Contribution

### Getting Help

- **Documentation:** `KDS/docs/`
- **Quick reference:** `KDS/KDS-CHEATSHEET.md`
- **Issues:** Check existing documentation first

### Contributing

If you've ported KDS to a new framework:
1. Share your `kds.config.json` as an example
2. Document any framework-specific challenges
3. Submit framework-specific template examples

---

**Guide Version:** 1.0.0  
**Last Updated:** 2025-11-04  
**Maintained By:** KDS Core Team

**Ready to port KDS to ANY application in 5 minutes!** 🚀
