# User-Configurable Document Tracking Design

**Feature:** Hybrid Document Architecture  
**Created:** January 4, 2026  
**Status:** ✅ DESIGN COMPLETE  
**SKULL Rules:** `GIT_ISOLATION_ENFORCEMENT`, `USER_DOCUMENT_SELECTIVE_TRACKING`

---

## 🎯 Problem Statement

**User Need:**
- Track planning documents in git for team collaboration
- Share reports, analyses, and documentation
- Keep CORTEX brain and core isolated

**Current Limitation:**
- ALL CORTEX content in `CORTEX/` or `cortex-brain/`
- .gitignore blocks everything (no selective tracking)
- Users can't share plans without manual copying

**Conflict:**
- User wants: Track some documents
- SKULL rule: Never commit brain state or core code
- Solution: Two-tier architecture with whitelist/blacklist

---

## 🏗️ Solution: Hybrid Architecture

### Directory Structure

```
user-repo/
│
├── .cortex/                          # User-controlled (selective tracking)
│   ├── config.json                   # User preferences (trackable)
│   │
│   ├── planning/                     # Plans (trackable if enabled)
│   │   ├── active/
│   │   │   ├── 01-feature-x.md
│   │   │   └── 02-feature-y.md
│   │   └── completed/
│   │       └── 2026-01-01-feature-z.md
│   │
│   ├── reports/                      # Reports (trackable if enabled)
│   │   ├── analysis-report.md
│   │   └── performance-report.md
│   │
│   ├── docs/                         # User docs (trackable if enabled)
│   │   └── architecture.md
│   │
│   └── sessions/                     # Session logs (NEVER trackable)
│       └── .gitignore               # Always excluded
│
├── CORTEX/                           # Brain + Core (ALWAYS excluded)
│   ├── cortex-brain/
│   │   ├── tier0/                   # Governance (NEVER trackable)
│   │   ├── tier1/                   # Working memory (NEVER trackable)
│   │   ├── tier2/                   # Knowledge graph (NEVER trackable)
│   │   ├── tier3/                   # Dev context (NEVER trackable)
│   │   └── conversation-context.jsonl
│   │
│   ├── src/                         # Core code (NEVER trackable)
│   ├── tests/                       # Tests (NEVER trackable)
│   └── manifests/                   # Orchestrators (NEVER trackable)
│
└── .gitignore                        # Auto-managed by CORTEX
```

### Configuration Schema

**File:** `.cortex/config.json`

```json
{
  "$schema": "https://cortex.ai/schemas/config-v5.json",
  "version": "5.0",
  "created": "2026-01-04T10:00:00Z",
  "updated": "2026-01-04T10:00:00Z",
  
  "user_preferences": {
    "document_tracking": {
      "enabled": false,
      "mode": "whitelist",
      
      "whitelist": {
        "planning": {
          "enabled": false,
          "patterns": [
            ".cortex/planning/**/*.md",
            ".cortex/planning/**/*.yaml"
          ],
          "exclude_active": false,
          "exclude_private": true
        },
        "reports": {
          "enabled": false,
          "patterns": [
            ".cortex/reports/**/*.md",
            ".cortex/reports/**/*.html"
          ]
        },
        "documentation": {
          "enabled": false,
          "patterns": [
            ".cortex/docs/**/*.md"
          ]
        }
      }
    },
    
    "sharing": {
      "team_plans": false,
      "public_docs": false,
      "sanitize_before_commit": true
    }
  },
  
  "brain_protection": {
    "enforce_isolation": true,
    "strict_mode": true,
    
    "never_track": [
      "CORTEX/**",
      "cortex-brain/**",
      ".cortex/config.json",
      ".cortex/sessions/**",
      ".cortex/.secrets/**",
      "*.cortex-session.*",
      "*.cortex-state.*"
    ],
    
    "validation": {
      "pre_commit_scan": true,
      "block_on_violation": true,
      "alert_user": true
    }
  },
  
  "safety": {
    "backup_before_migration": true,
    "rollback_enabled": true,
    "audit_log": ".cortex/.audit.log"
  }
}
```

---

## 🛡️ Whitelist/Blacklist Enforcement

### Protection Layers

#### Layer 1: Configuration Validation

```python
class DocumentTrackingConfig:
    """Validates and enforces document tracking configuration."""
    
    PROTECTED_PATTERNS = [
        "CORTEX/**",
        "cortex-brain/**",
        "src/**",
        "tests/**",
        ".cortex/config.json",
        ".cortex/sessions/**",
        "*.cortex-session.*"
    ]
    
    SAFE_USER_PATTERNS = [
        ".cortex/planning/**/*.md",
        ".cortex/reports/**/*.md",
        ".cortex/docs/**/*.md"
    ]
    
    def validate_whitelist(self, patterns: List[str]) -> ValidationResult:
        """Ensure user whitelist doesn't include protected patterns."""
        violations = []
        
        for pattern in patterns:
            if self._matches_protected(pattern):
                violations.append({
                    "pattern": pattern,
                    "reason": "Matches protected CORTEX brain/core pattern",
                    "severity": "CRITICAL"
                })
        
        if violations:
            return ValidationResult(
                valid=False,
                violations=violations,
                message="Configuration violates GIT_ISOLATION_ENFORCEMENT"
            )
        
        return ValidationResult(valid=True)
    
    def _matches_protected(self, user_pattern: str) -> bool:
        """Check if user pattern overlaps with protected patterns."""
        import fnmatch
        
        for protected in self.PROTECTED_PATTERNS:
            # Check both directions
            if fnmatch.fnmatch(user_pattern, protected):
                return True
            if fnmatch.fnmatch(protected, user_pattern):
                return True
        
        return False
```

#### Layer 2: Pre-Commit Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
# CORTEX Brain Protection Hook

echo "🛡️  CORTEX: Validating staged files..."

# Get all staged files
staged_files=$(git diff --cached --name-only)

# Protected patterns (NEVER allow)
protected_patterns=(
    "CORTEX/"
    "cortex-brain/"
    ".cortex/config.json"
    ".cortex/sessions/"
    "*.cortex-session.*"
)

# Check each staged file
violations=()
for file in $staged_files; do
    for pattern in "${protected_patterns[@]}"; do
        if [[ $file == $pattern* ]]; then
            violations+=("$file")
        fi
    done
done

# Block commit if violations found
if [ ${#violations[@]} -gt 0 ]; then
    echo ""
    echo "❌ CORTEX BRAIN PROTECTION VIOLATION"
    echo ""
    echo "The following protected files were staged:"
    for violation in "${violations[@]}"; do
        echo "  - $violation"
    done
    echo ""
    echo "SKULL Rule: GIT_ISOLATION_ENFORCEMENT"
    echo "CORTEX brain and core files must NEVER be committed."
    echo ""
    echo "To fix:"
    echo "  git reset HEAD <file>  # Unstage protected files"
    echo ""
    exit 1
fi

echo "✅ No brain protection violations"
exit 0
```

#### Layer 3: Runtime Validation

```python
class GitSafetyValidator:
    """Runtime validation before git operations."""
    
    def validate_staging_area(self) -> ValidationResult:
        """Check git staging area for protected files."""
        
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True
        )
        
        staged_files = result.stdout.strip().split('\n')
        
        violations = []
        for file in staged_files:
            if self._is_protected(file):
                violations.append({
                    "file": file,
                    "reason": "Protected CORTEX file",
                    "severity": "CRITICAL"
                })
        
        if violations:
            self._alert_user(violations)
            self._auto_unstage(violations)
            
            return ValidationResult(
                valid=False,
                violations=violations,
                message="Protected files auto-unstaged"
            )
        
        return ValidationResult(valid=True)
    
    def _is_protected(self, file_path: str) -> bool:
        """Check if file matches protected patterns."""
        protected = [
            "CORTEX/",
            "cortex-brain/",
            ".cortex/config.json",
            ".cortex/sessions/"
        ]
        
        return any(file_path.startswith(p) for p in protected)
    
    def _auto_unstage(self, violations: List[Dict]):
        """Automatically unstage protected files."""
        for violation in violations:
            subprocess.run(
                ["git", "reset", "HEAD", violation["file"]],
                capture_output=True
            )
```

---

## 🔄 Migration Strategy

### Phase 1: Create .cortex/ Structure

```python
class CortexDirectoryMigration:
    """Migrate user documents to .cortex/ folder."""
    
    def migrate(self, repo_path: Path):
        """Execute migration with rollback safety."""
        
        # 1. Backup existing structure
        backup_path = self._create_backup(repo_path)
        
        try:
            # 2. Create .cortex/ structure
            self._create_dotcortex_structure(repo_path)
            
            # 3. Migrate user-trackable documents
            self._migrate_planning_docs(repo_path)
            self._migrate_reports(repo_path)
            
            # 4. Update .gitignore
            self._update_gitignore(repo_path)
            
            # 5. Create config.json
            self._create_config(repo_path)
            
            # 6. Validate migration
            self._validate_brain_protection(repo_path)
            
            print("✅ Migration complete!")
            print(f"   Backup: {backup_path}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print(f"   Rolling back to: {backup_path}")
            self._rollback(repo_path, backup_path)
            raise
    
    def _create_dotcortex_structure(self, repo_path: Path):
        """Create .cortex/ folder structure."""
        dotcortex = repo_path / ".cortex"
        
        folders = [
            "planning/active",
            "planning/completed",
            "reports",
            "docs",
            "sessions"
        ]
        
        for folder in folders:
            (dotcortex / folder).mkdir(parents=True, exist_ok=True)
        
        # Create sessions/.gitignore (NEVER track sessions)
        sessions_gitignore = dotcortex / "sessions" / ".gitignore"
        sessions_gitignore.write_text("*\n!.gitignore\n")
    
    def _migrate_planning_docs(self, repo_path: Path):
        """Move user-created plans to .cortex/planning/."""
        
        source = repo_path / "cortex-brain" / "documents" / "planning" / "active"
        target = repo_path / ".cortex" / "planning" / "active"
        
        if not source.exists():
            return
        
        # Only migrate user-created plans (not CORTEX internals)
        user_plans = self._identify_user_plans(source)
        
        for plan_file in user_plans:
            shutil.copy2(plan_file, target / plan_file.name)
            print(f"  Migrated: {plan_file.name}")
```

### Phase 2: Update .gitignore

**Enhanced .gitignore Logic:**

```python
def generate_gitignore(self, config: Dict) -> str:
    """Generate .gitignore with selective tracking."""
    
    lines = [
        "",
        "# ============================================",
        "# CORTEX AI Assistant (Auto-Generated)",
        "# ============================================",
        "",
        "# CORTEX Brain & Core (NEVER track)",
        "CORTEX/",
        "CORTEX/**",
        "cortex-brain/",
        "",
        "# CORTEX Sessions & Config (NEVER track)",
        ".cortex/config.json",
        ".cortex/sessions/",
        ".cortex/.secrets/",
        "*.cortex-session.*",
        "*.cortex-state.*",
        ""
    ]
    
    # Add user whitelist (if enabled)
    if config.get("user_preferences", {}).get("document_tracking", {}).get("enabled"):
        lines.extend([
            "# User-Trackable Documents (Whitelisted)",
            "# These are ALLOWED to be tracked if enabled:",
            "# - .cortex/planning/**/*.md",
            "# - .cortex/reports/**/*.md",
            "# - .cortex/docs/**/*.md",
            "",
            "# To enable, set document_tracking.enabled = true",
            "# in .cortex/config.json",
            ""
        ])
    else:
        lines.extend([
            "# User Documents (Currently NOT tracked)",
            ".cortex/planning/",
            ".cortex/reports/",
            ".cortex/docs/",
            ""
        ])
    
    return "\n".join(lines)
```

---

## 🎮 User Interface

### Interactive Setup

```bash
$ cortex config tracking

🎯 CORTEX Document Tracking Configuration

Current Status: DISABLED

Would you like to track planning documents in git? (y/n): y

⚠️  WARNING: Brain Protection Active
✅ Safe to track: .cortex/planning/**/*.md
❌ Never tracked: CORTEX/, cortex-brain/, .cortex/config.json

Select what to track:
  [x] Planning documents (.cortex/planning/**/*.md)
  [ ] Reports (.cortex/reports/**/*.md)
  [ ] Documentation (.cortex/docs/**/*.md)

Enable tracking for active plans? (y/n): n
Enable tracking for completed plans? (y/n): y

✅ Configuration Updated!

Next steps:
  1. Review .gitignore changes
  2. Stage trackable documents: git add .cortex/planning/completed/
  3. Commit: git commit -m "Add completed CORTEX plans"

🛡️ Brain Protection: ACTIVE
   Protected files will be auto-rejected if staged.
```

### CLI Commands

```bash
# Enable document tracking
cortex config tracking --enable

# Disable document tracking
cortex config tracking --disable

# View current configuration
cortex config tracking --status

# Validate configuration
cortex config tracking --validate

# Test what would be tracked
cortex config tracking --dry-run

# Migrate to .cortex/ structure
cortex migrate dotcortex --backup
```

---

## ✅ Safety Guarantees

### 1. Configuration Validation
- ✅ User whitelist cannot overlap protected patterns
- ✅ Schema validation on config load
- ✅ Error messages explain violations

### 2. Git Hook Protection
- ✅ Pre-commit hook blocks protected files
- ✅ Automatic unstaging of violations
- ✅ Clear error messages

### 3. Runtime Validation
- ✅ Check staging area before operations
- ✅ Alert user to violations
- ✅ Auto-fix when possible

### 4. Audit Trail
- ✅ Log all tracking config changes
- ✅ Record migration events
- ✅ Track validation failures

### 5. Rollback Safety
- ✅ Backup before migration
- ✅ Rollback command available
- ✅ State preservation

---

## 📊 Example Configurations

### Configuration 1: Team Collaboration (Planning)

```json
{
  "user_preferences": {
    "document_tracking": {
      "enabled": true,
      "whitelist": {
        "planning": {
          "enabled": true,
          "exclude_active": false,
          "exclude_private": true
        }
      }
    }
  }
}
```

**Result:** Team can track and share planning documents

### Configuration 2: Documentation Only

```json
{
  "user_preferences": {
    "document_tracking": {
      "enabled": true,
      "whitelist": {
        "documentation": {
          "enabled": true
        }
      }
    }
  }
}
```

**Result:** Only documentation tracked, plans stay local

### Configuration 3: Maximum Isolation (Default)

```json
{
  "user_preferences": {
    "document_tracking": {
      "enabled": false
    }
  }
}
```

**Result:** Nothing tracked, full brain protection

---

## 🎯 Implementation Checklist

- [ ] Create `.cortex/` directory structure
- [ ] Implement `DocumentTrackingConfig` class
- [ ] Build migration utility
- [ ] Update `.gitignore` generation logic
- [ ] Create pre-commit git hook
- [ ] Build `GitSafetyValidator`
- [ ] Implement `cortex config tracking` command
- [ ] Add configuration schema validation
- [ ] Write tests for all protection layers
- [ ] Update deployment plan with migration
- [ ] Document user workflows
- [ ] Create video tutorial

---

**Status:** ✅ DESIGN COMPLETE - Ready for Implementation  
**SKULL Rules:** `GIT_ISOLATION_ENFORCEMENT` (preserved), `USER_DOCUMENT_SELECTIVE_TRACKING` (new)  
**Author:** CORTEX AI Assistant  
**Copyright © 2026 Asif Hussain. All rights reserved.**
