# AST-Powered Copilot Instructions Enhancement Plan

**Plan ID:** AST-COPILOT-INSTRUCTIONS-v1.0  
**Created:** December 11, 2025  
**Author:** Asif Hussain  
**Status:** Awaiting Approval

---

## 🎯 Overview

Enhance CORTEX setup system to use **AST-based code analysis** for generating domain-specific copilot-instructions.md files. When existing instructions exist, intelligently merge CORTEX capabilities while preserving 100% of user customizations.

---

## 📋 Current State vs Desired State

### Current Behavior
- ✅ Detects existing `.github/copilot-instructions.md` via filesystem check
- ✅ Returns early if file exists (no overwrite without `force=True`)
- ✅ Generates CORTEX-enhanced template with project metadata
- ❌ No domain-specific pattern detection
- ❌ No intelligent merge capability
- ❌ All-or-nothing approach (replace vs skip)

### Desired Behavior
- ✅ AST-based code pattern detection (architecture, auth, API style, data access)
- ✅ Domain-specific instructions tailored to actual codebase
- ✅ Intelligent merge preserving all user customizations
- ✅ CORTEX capability injection without content loss
- ✅ Upgrade path for existing CORTEX instructions

---

## 🔬 AST Analysis Strategy

### Supported Languages

| Language | AST Library | Detection Focus |
|----------|-------------|-----------------|
| **Python** | `ast` (stdlib) | Classes, decorators, imports |
| **TypeScript/JS** | `esprima` or regex | Exports, interfaces, React patterns |
| **C#** | Regex-based | Attributes, namespaces, LINQ |
| **Java** | Regex-based | Annotations, interfaces |

### Pattern Categories

1. **Architecture Patterns**
   - Repository Pattern: `class UserRepository(BaseRepository)`
   - Service Layer: `class *Service` classes
   - CQRS: Command/Query separation
   - Factory Pattern: `class *Factory`

2. **Authentication & Security**
   - JWT: `import jwt`, `@jwt_required`, `JwtBearer`
   - OAuth: `oauth2`, `OAuthHandler`
   - Session-based: `session.get`, `SessionMiddleware`
   - Role-based: `@roles_required`, `[Authorize(Roles=`

3. **API Patterns**
   - REST: `@app.route`, `@RestController`, `app.get/post`
   - GraphQL: `graphql`, `@Query`, `@Mutation`
   - gRPC: `grpc`, `.proto` files
   - WebSockets: `WebSocket`, `socket.io`

4. **Data Access**
   - ORMs: `SQLAlchemy`, `Entity Framework`, `Hibernate`, `Mongoose`
   - Query builders: `knex`, `LINQ`
   - Raw SQL: `cursor.execute`, `SqlCommand`

5. **Testing Conventions**
   - Test naming: `test_*`, `Test*`, `*Test`, `*.spec.ts`
   - Fixtures: `@pytest.fixture`, `beforeEach`, `[SetUp]`
   - Mocking: `unittest.mock`, `jest.mock`, `Moq`
   - Factories: `factory_boy`, `faker`

6. **Framework-Specific**
   - React: Functional components, hooks (`useState`, `useEffect`)
   - Vue: Composition API, Options API
   - Django: Middleware, signals, management commands
   - ASP.NET: Middleware, dependency injection, filters

### Targeted Scanning (Performance Optimized)

**Files to Scan:**
- Entry points: `main.py`, `app.py`, `index.ts`, `Program.cs`, `Application.java`
- Base classes: `*base*.py`, `*repository*.py`, `*service*.py`
- Config files: `settings.py`, `config.ts`, `appsettings.json`
- API routes: `routes.py`, `controllers/*`, `api/*`

**Files to Skip:**
- Test files (unless analyzing test patterns)
- Migrations (`migrations/`, `alembic/versions/`)
- Generated code (`*_pb2.py`, `*.g.cs`)
- Dependencies (`node_modules/`, `venv/`, `vendor/`)

**Performance Target:** 5-10 seconds for targeted AST scan

---

## 🔄 Intelligent Merge Strategy

### Three Merge Scenarios

#### Scenario A: No Existing File
**Action:** Generate new CORTEX-enhanced template with detected patterns

**Output:**
```markdown
# GitHub Copilot Instructions for {project_name}

## 🎯 Entry Point
**Primary prompt:** `.github/prompts/CORTEX.prompt.md`

## 🧠 CORTEX Integration
- Planning System 2.0
- TDD Mastery
- View Discovery

## Development Guidelines
### Architecture
- Repository Pattern (detected)
- Service Layer (detected)

### API Development
- REST with OpenAPI (detected)
- JWT authentication (detected)

### Database
- SQLAlchemy async ORM (detected)
```

---

#### Scenario B: Generic Existing File
**Action:** Merge CORTEX sections + detected patterns while preserving user content

**Before:**
```markdown
# Project Instructions

## Custom Workflows
- Use feature branches
- Squash merges only

## Team Guidelines
- Code review required
```

**After:**
```markdown
# Project Instructions

## 🎯 Entry Point
**Primary prompt:** `.github/prompts/CORTEX.prompt.md`

## Custom Workflows
- Use feature branches
- Squash merges only

## Team Guidelines
- Code review required

## 🧠 CORTEX Integration
- Planning System 2.0
- TDD Mastery

## Development Guidelines
### 🧠 CORTEX-Detected Patterns
- Repository Pattern
- JWT authentication
- SQLAlchemy async ORM
```

---

#### Scenario C: Existing CORTEX File
**Action:** Update CORTEX sections + refresh detected patterns

**Before:**
```markdown
# GitHub Copilot Instructions

## 🎯 Entry Point (v3.2.1)

## 🧠 CORTEX Integration
- Planning System 2.0

## Custom Notes
- Use async/await everywhere
```

**After:**
```markdown
# GitHub Copilot Instructions

## 🎯 Entry Point (v3.8.1)

## 🧠 CORTEX Integration
- Planning System 2.0
- TDD Mastery (NEW)
- Progress Monitoring (NEW)

## Custom Notes
- Use async/await everywhere

## Development Guidelines
### 🧠 CORTEX-Detected Patterns (Refreshed)
- Repository Pattern
- JWT authentication
```

---

## 📐 Implementation Plan

### Phase 1: Code Pattern Detector (NEW)
**File:** `src/operations/modules/setup/code_pattern_detector.py` (~400 lines)

**Functions:**
```python
@dataclass
class DomainPatterns:
    architecture: List[str]
    auth_method: Optional[str]
    api_style: Optional[str]
    data_access: Optional[str]
    testing_patterns: List[str]
    framework_specifics: Dict[str, str]
    custom_conventions: List[str]

def detect_patterns(project_root: Path, language: str) -> DomainPatterns:
    """Detect code patterns via AST analysis."""

def detect_python_patterns(root: Path) -> DomainPatterns:
    """Python-specific AST pattern detection."""

def detect_typescript_patterns(root: Path) -> DomainPatterns:
    """TypeScript-specific pattern detection (regex fallback)."""

def detect_csharp_patterns(root: Path) -> DomainPatterns:
    """C#-specific pattern detection (regex-based)."""

def detect_java_patterns(root: Path) -> DomainPatterns:
    """Java-specific pattern detection (regex-based)."""
```

**AST Analysis Targets:**
- **Python:** Use `ast.parse()` to detect classes, decorators, base classes, imports
- **TypeScript:** Use regex for `export`, `interface`, `React.FC`, hooks
- **C#:** Use regex for `[Attribute]`, namespaces, interfaces
- **Java:** Use regex for `@Annotation`, `implements`, `extends`

**Fallback:** If AST parsing fails, use regex for basic pattern detection

---

### Phase 2: Merge Engine (NEW)
**File:** `src/operations/modules/setup/copilot_instructions_merger.py` (~300 lines)

**Functions:**
```python
@dataclass
class MergeResult:
    content: str
    action: str  # "created", "merged", "updated"
    user_sections_preserved: int
    cortex_sections_updated: int
    patterns_injected: int

def merge_with_existing(
    existing_path: Path,
    detection: ProjectDetection,
    domain_patterns: DomainPatterns
) -> MergeResult:
    """Merge CORTEX enhancements while preserving user content."""

def parse_markdown_sections(content: str) -> Dict[str, str]:
    """Parse markdown into sections by headers."""

def is_cortex_managed_section(header: str) -> bool:
    """Check if section is CORTEX-managed (safe to update)."""

def generate_cortex_sections(
    detection: ProjectDetection,
    domain_patterns: DomainPatterns
) -> Dict[str, str]:
    """Generate CORTEX sections with detected patterns."""

def render_markdown(sections: Dict[str, str]) -> str:
    """Render sections back to markdown."""
```

**Section Classification:**
- **CORTEX-Managed:** `## 🧠 CORTEX Integration`, `## 🎯 Entry Point`
- **User-Owned:** Any custom headers, `## Custom Notes`, `## Team Guidelines`
- **Hybrid:** `## Development Guidelines` (merge patterns as subsection)

---

### Phase 3: Enhanced Setup Utility (MODIFIED)
**File:** `src/operations/modules/setup/master_setup_utility.py` (+150 lines)

**Changes:**
```python
def generate_copilot_instructions(
    project_root: Path,
    project_name: str,
    detection: ProjectDetection,
    force: bool = False,
    enable_code_analysis: bool = True  # NEW PARAMETER
) -> Dict[str, Any]:
    """Generate or merge copilot-instructions.md with code pattern detection."""
    
    instructions_path = project_root / ".github" / "copilot-instructions.md"
    
    # NEW: Detect code patterns via AST
    domain_patterns = None
    if enable_code_analysis:
        from src.operations.modules.setup.code_pattern_detector import detect_patterns
        domain_patterns = detect_patterns(project_root, detection.language)
        logger.info(f"✓ Detected {len(domain_patterns)} domain patterns")
    
    # NEW: Handle existing files with merge
    if instructions_path.exists():
        if not force:
            # Merge mode (preserve user content)
            from src.operations.modules.setup.copilot_instructions_merger import merge_with_existing
            result = merge_with_existing(
                instructions_path,
                detection,
                domain_patterns
            )
            logger.info(f"✓ Merged: {result.user_sections_preserved} user sections preserved")
            return {
                "success": True,
                "action": result.action,
                "patterns_detected": result.patterns_injected
            }
        else:
            # Force mode: backup and replace
            backup_path = instructions_path.with_suffix('.md.backup')
            shutil.copy(instructions_path, backup_path)
            logger.info(f"⚠️  Backed up existing file to {backup_path}")
    
    # Generate new CORTEX-enhanced template
    content = render_enhanced_template(
        project_name,
        detection,
        domain_patterns  # NEW: Inject detected patterns
    )
    
    instructions_path.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "action": "created",
        "patterns_detected": len(domain_patterns) if domain_patterns else 0
    }
```

---

## 🎭 User Experience Examples

### Example 1: New Repository (FastAPI + SQLAlchemy)

**Command:** `setup copilot instructions`

**Output:**
```
🔍 Analyzing codebase...
   ✓ Detected: Python 3.11 with FastAPI
   ✓ Found: Repository Pattern (5 repositories detected)
   ✓ Found: JWT authentication with refresh tokens
   ✓ Found: SQLAlchemy async ORM
   ✓ Found: pytest with factory_boy
   ⏱️  Analysis completed in 7.2 seconds

📝 Generated .github/copilot-instructions.md
   • Project metadata: Python, FastAPI, pytest
   • CORTEX Integration: Planning System 2.0, TDD Mastery
   • Domain patterns: 4 patterns detected
   • File size: 342 lines (~1,200 tokens)

✅ Ready! GitHub Copilot now has domain-specific context.
```

---

### Example 2: Existing Generic Instructions

**Command:** `setup copilot instructions`

**Output:**
```
⚠️  Existing .github/copilot-instructions.md detected

🔍 Analyzing content...
   • Type: Generic boilerplate (no CORTEX enhancements)
   • User sections: 2 (Custom Workflows, Team Guidelines)

🔍 Analyzing codebase...
   ✓ Detected: Repository Pattern
   ✓ Detected: JWT authentication
   ✓ Detected: SQLAlchemy async ORM
   ⏱️  Analysis completed in 6.8 seconds

🔄 Merging enhancements...
   ✓ Preserved: Custom Workflows section (user content)
   ✓ Preserved: Team Guidelines section (user content)
   ✓ Added: 🧠 CORTEX Integration section
   ✓ Enhanced: Development Guidelines with detected patterns
   ✓ Added: 🎯 Entry Point section

📝 Updated .github/copilot-instructions.md
   • User content: 100% preserved (2 sections)
   • CORTEX sections: 3 added
   • Domain patterns: 3 injected
   • Before: 120 lines → After: 380 lines

✅ Enhanced! User customizations preserved + CORTEX capabilities added.
```

---

### Example 3: Update Existing CORTEX Instructions

**Command:** `setup copilot instructions --force`

**Output:**
```
⚠️  Existing CORTEX-enhanced instructions detected

🔍 Checking for updates...
   • Current version: 3.2.1
   • Latest version: 3.8.1
   • New capabilities: 2 (Progress Monitoring, ADO Operations)

🔍 Re-analyzing codebase...
   ✓ Detected: Repository Pattern (unchanged)
   ✓ Detected: JWT authentication (unchanged)
   ✓ Detected: Event-driven architecture (NEW PATTERN)
   ⏱️  Analysis completed in 5.9 seconds

🔄 Updating CORTEX sections...
   ✓ Updated: Entry Point (v3.2.1 → v3.8.1)
   ✓ Updated: CORTEX Integration (added 2 new capabilities)
   ✓ Preserved: All user sections (0 changes)
   ✓ Refreshed: Domain patterns (detected 1 new pattern)

📝 Updated .github/copilot-instructions.md
   • Version: 3.2.1 → 3.8.1
   • New capabilities: 2
   • New patterns: 1
   • User content: 100% preserved

✅ Up to date! Latest CORTEX capabilities + refreshed patterns.
```

---

## 📊 Impact Analysis

### Files to Create
1. `src/operations/modules/setup/code_pattern_detector.py` (~400 lines)
2. `src/operations/modules/setup/copilot_instructions_merger.py` (~300 lines)

### Files to Modify
1. `src/operations/modules/setup/master_setup_utility.py` (+150 lines)

### Benefits
- ✅ **Domain Intelligence:** Instructions tailored to actual codebase patterns
- ✅ **Non-Destructive:** 100% preservation of user customizations
- ✅ **Auto-Learning:** Detects new patterns as code evolves
- ✅ **CORTEX Upgrade Path:** Safe updates without content loss
- ✅ **Better AI Assistance:** Copilot understands repo-specific conventions

### Performance
- AST scanning: 5-10 seconds (targeted files only)
- Merge operation: <1 second
- Total setup time: 10-15 seconds (vs 3-5 seconds currently)
- **Tradeoff:** Acceptable for domain intelligence gain

### Token Budget
- Pattern detection: ~50 tokens per pattern
- Enhanced instructions: ~300-500 lines (~1,200-2,000 tokens)
- GitHub Copilot limit: 4,000 tokens ✅ (under budget)

---

## 🔍 Implementation Steps

1. **Phase 1:** Implement `code_pattern_detector.py`
   - Start with Python AST support
   - Add TypeScript/JS regex detection
   - Add C#/Java regex detection
   - Add fallback for unsupported languages

2. **Phase 2:** Implement `copilot_instructions_merger.py`
   - Markdown section parser
   - Section classification (CORTEX vs user)
   - Intelligent merge logic
   - Conflict resolution

3. **Phase 3:** Integrate into `master_setup_utility.py`
   - Add `enable_code_analysis` parameter
   - Call pattern detector
   - Call merger for existing files
   - Inject patterns into template

4. **Phase 4:** Testing
   - Test Scenario A: New repository (various languages)
   - Test Scenario B: Generic existing instructions
   - Test Scenario C: CORTEX existing instructions
   - Test edge cases: Empty file, corrupted file, permission errors

5. **Phase 5:** Documentation
   - Update SETUP-GUIDE.md
   - Create implementation guide
   - Add user guide for merge scenarios

6. **Phase 6:** Deployment
   - Add to CORTEX 3.9.0 release
   - Update changelog
   - Announce feature

---

## ✅ Acceptance Criteria

- [ ] AST pattern detection works for Python (ast library)
- [ ] Regex pattern detection works for TypeScript, C#, Java
- [ ] Detects at least 4 pattern categories (architecture, auth, API, data access)
- [ ] Merge preserves 100% of user customizations
- [ ] CORTEX sections can be updated without data loss
- [ ] Performance: AST scan completes in <10 seconds
- [ ] Token budget: Generated instructions stay under 2,000 tokens
- [ ] All 3 scenarios tested: New, Generic, CORTEX files
- [ ] Documentation updated in SETUP-GUIDE.md
- [ ] User feedback mechanism for pattern accuracy

---

## 🚀 Next Steps

1. **Approve Plan** - Confirm AST-based approach aligns with vision
2. **Implement Phase 1** - Build `code_pattern_detector.py` with Python AST
3. **Implement Phase 2** - Build `copilot_instructions_merger.py`
4. **Integrate Phase 3** - Modify `master_setup_utility.py`
5. **Test Scenarios** - Validate all 3 merge scenarios
6. **Document** - Update SETUP-GUIDE.md
7. **Deploy** - Add to CORTEX 3.9.0 release

---

**Created:** December 11, 2025  
**Author:** Asif Hussain  
**Status:** ⏳ Awaiting Approval  
**Target Release:** CORTEX 3.9.0
