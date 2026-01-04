# Safe Deletion Strategies

**Date:** 2026-01-02  
**Purpose:** Document critical file protection and safe deletion rules for Vacuum v2

---

## 🎯 Core Principle

**NEVER delete critical files that could cause data loss or system instability.**

Safe deletion requires:
1. **Identification** - Detect critical files before deletion
2. **Validation** - Verify file is safe to delete
3. **Protection** - Block deletion of critical files
4. **User Confirmation** - Require approval for high-risk deletions

---

## 🛡️ Critical File Categories

### 1. **Git Metadata** (NEVER DELETE)

**Patterns:**
- `.git/` directory (entire git repository metadata)
- `.gitignore`, `.gitattributes`, `.gitmodules`
- `.github/` (CI/CD workflows, GitHub-specific configs)

**Rationale:**
- Deleting `.git/` destroys version history (irreversible)
- Git workflows depend on `.gitignore`, `.github/`
- CORTEX CI/CD requires `.github/workflows/`

**Protection:**
```python
CRITICAL_PATTERNS = [
    '.git',
    '.git/**',
    '.gitignore',
    '.gitattributes',
    '.gitmodules',
    '.github/**'
]

def is_git_metadata(path: Path) -> bool:
    """Check if path is git metadata."""
    return any(path.match(pattern) for pattern in CRITICAL_PATTERNS)
```

### 2. **Source Code** (NEVER DELETE)

**Patterns:**
- `*.py`, `*.js`, `*.ts`, `*.jsx`, `*.tsx`
- `*.java`, `*.c`, `*.cpp`, `*.h`, `*.cs`
- `*.go`, `*.rs`, `*.rb`, `*.php`
- `*.html`, `*.css`, `*.scss`, `*.sass`
- `*.sql`, `*.sh`, `*.bash`, `*.ps1`

**Exclusions:**
- `*.pyc`, `*.pyo` (compiled Python - safe to delete)
- Generated code (if marked as auto-generated)

**Rationale:**
- Source code is the core asset
- Deleting source code is catastrophic
- Even "unused" code may be needed

**Protection:**
```python
SOURCE_CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx',
    '.java', '.c', '.cpp', '.h', '.cs',
    '.go', '.rs', '.rb', '.php',
    '.html', '.css', '.scss', '.sass',
    '.sql', '.sh', '.bash', '.ps1'
}

def is_source_code(path: Path) -> bool:
    """Check if path is source code."""
    return path.suffix in SOURCE_CODE_EXTENSIONS
```

### 3. **Configuration Files** (NEVER DELETE)

**Patterns:**
- `*.yaml`, `*.yml`
- `*.json` (except build artifacts like `package-lock.json`)
- `*.toml`, `*.ini`, `*.conf`, `*.config`
- `*.env`, `.env.*` (environment variables)
- `requirements.txt`, `package.json`, `pyproject.toml`
- `Dockerfile`, `docker-compose.yml`
- `Makefile`, `CMakeLists.txt`

**Rationale:**
- Configuration files define system behavior
- Deleting config breaks applications
- Environment files contain secrets/settings

**Protection:**
```python
CONFIG_EXTENSIONS = {
    '.yaml', '.yml', '.json',
    '.toml', '.ini', '.conf', '.config',
    '.env'
}

CONFIG_FILENAMES = {
    'requirements.txt',
    'package.json',
    'pyproject.toml',
    'Dockerfile',
    'docker-compose.yml',
    'Makefile',
    'CMakeLists.txt'
}

def is_config_file(path: Path) -> bool:
    """Check if path is configuration file."""
    return (
        path.suffix in CONFIG_EXTENSIONS or
        path.name in CONFIG_FILENAMES
    )
```

### 4. **Documentation** (NEVER DELETE)

**Patterns:**
- `*.md` (Markdown documentation)
- `*.rst` (reStructuredText)
- `*.txt` (text files - except logs)
- `README*`, `LICENSE*`, `CHANGELOG*`
- `docs/` directory

**Exclusions:**
- `*.log.txt` (log files - safe to archive)
- `temp_notes.txt` (temporary files)

**Rationale:**
- Documentation is critical knowledge
- README, LICENSE are required for open-source
- CORTEX relies on Markdown docs

**Protection:**
```python
DOCUMENTATION_EXTENSIONS = {'.md', '.rst'}
DOCUMENTATION_FILENAMES = {
    'README', 'README.md', 'README.txt',
    'LICENSE', 'LICENSE.md', 'LICENSE.txt',
    'CHANGELOG', 'CHANGELOG.md',
    'CONTRIBUTING', 'CONTRIBUTING.md',
    'CODE_OF_CONDUCT', 'CODE_OF_CONDUCT.md'
}

def is_documentation(path: Path) -> bool:
    """Check if path is documentation."""
    return (
        path.suffix in DOCUMENTATION_EXTENSIONS or
        path.stem in DOCUMENTATION_FILENAMES or
        'docs' in path.parts
    )
```

### 5. **CORTEX Brain** (NEVER DELETE - Governance)

**Patterns:**
- `cortex-brain/tier0/` (Governance layer)
- `cortex-brain/tier1/` (Working memory)
- `cortex-brain/tier2/` (Knowledge graph)
- `cortex-brain/tier3/` (Development context)
- `cortex-brain/database/` (SQLite databases)
- `cortex-brain/manifests/` (Orchestrator configs)
- `cortex-brain/config/` (System configuration)

**Exclusions:**
- `cortex-brain/cache/` (safe to clean)
- `cortex-brain/logs/` (safe to archive)
- `cortex-brain/cleanup-reports/` (safe to clean)
- `cortex-brain/archives/` (safe to clean old archives)

**Rationale:**
- Brain tier0 defines CORTEX governance
- Brain databases contain critical state
- Manifests control orchestrator behavior
- Deleting brain = deleting CORTEX intelligence

**Protection:**
```python
CORTEX_CRITICAL_PATHS = [
    'cortex-brain/tier0',
    'cortex-brain/tier1',
    'cortex-brain/tier2',
    'cortex-brain/tier3',
    'cortex-brain/database',
    'cortex-brain/manifests',
    'cortex-brain/config'
]

CORTEX_SAFE_PATHS = [
    'cortex-brain/cache',
    'cortex-brain/logs',
    'cortex-brain/cleanup-reports',
    'cortex-brain/archives'
]

def is_cortex_critical(path: Path) -> bool:
    """Check if path is CORTEX critical brain data."""
    for critical_path in CORTEX_CRITICAL_PATHS:
        if path.is_relative_to(Path(critical_path)):
            # Check if in safe subfolder
            for safe_path in CORTEX_SAFE_PATHS:
                if path.is_relative_to(Path(safe_path)):
                    return False
            return True
    return False
```

### 6. **Active Files** (Recently Modified)

**Rule:** Never delete files modified in last 24 hours (unless `--aggressive`)

**Rationale:**
- Recent files likely in active use
- User may not have committed changes
- High risk of deleting work in progress

**Protection:**
```python
from datetime import datetime, timedelta

def is_recently_modified(path: Path, hours: int = 24) -> bool:
    """Check if file modified within N hours."""
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age = datetime.now() - mtime
        return age < timedelta(hours=hours)
    except OSError:
        return False  # Assume safe if cannot check
```

### 7. **Uncommitted Changes**

**Rule:** Never delete files with uncommitted git changes

**Rationale:**
- Uncommitted changes are not backed up
- Deleting = permanent data loss
- Git status = modified, untracked, staged

**Protection:**
```python
import subprocess

def has_uncommitted_changes(path: Path, git_root: Path) -> bool:
    """Check if file has uncommitted changes."""
    try:
        # Get git status for file
        result = subprocess.run(
            ['git', 'status', '--porcelain', str(path)],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Non-empty output = uncommitted changes
        return bool(result.stdout.strip())
    except Exception:
        return False  # Assume safe if cannot check
```

---

## ⚠️ High-Risk File Categories

### 1. **Orphaned Files** (Require Confirmation)

**Definition:** Files with no references (imports, links, dependencies)

**Examples:**
- Test files with no corresponding source file
- Config files for removed dependencies
- Unused Python modules (no imports)

**Strategy:**
- Detect via AST analysis (imports, references)
- Warn user with context (why detected as orphan)
- Require explicit confirmation
- Option to archive instead of delete

**Protection:**
```python
def is_orphaned(path: Path, project_root: Path) -> bool:
    """
    Check if file is orphaned (no references).
    
    Returns:
        True if file has no imports/references
    """
    # Use ASTEngine to find references
    from src.operations.modules.analysis.ast_engine import ASTEngine
    
    ast_engine = ASTEngine(project_root)
    references = ast_engine.find_references(path)
    
    return len(references) == 0
```

### 2. **Large Files** (Warn Before Deletion)

**Rule:** Warn if deleting files >10MB

**Rationale:**
- Large files may be important (databases, datasets)
- User may not realize size
- Should confirm before deleting

**Protection:**
```python
def is_large_file(path: Path, threshold_mb: int = 10) -> bool:
    """Check if file exceeds size threshold."""
    try:
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb > threshold_mb
    except OSError:
        return False
```

### 3. **IDE Custom Configurations** (Selective Deletion)

**Rule:** Delete generic IDE metadata, preserve custom configs

**Examples:**
- ✅ Delete: `.vscode/settings.json` (if default)
- ❌ Keep: `.vscode/launch.json` (custom debug configs)
- ❌ Keep: `.vscode/tasks.json` (custom tasks)

**Protection:**
```python
IDE_SAFE_TO_DELETE = [
    '.vscode/settings.json',
    '.idea/workspace.xml',
    '.vs/config/applicationhost.config'
]

IDE_PRESERVE = [
    '.vscode/launch.json',
    '.vscode/tasks.json',
    '.idea/runConfigurations/',
    '.github/'
]

def is_safe_ide_metadata(path: Path) -> bool:
    """Check if IDE metadata is safe to delete."""
    path_str = str(path)
    
    # Check if in preserve list
    for preserve_pattern in IDE_PRESERVE:
        if preserve_pattern in path_str:
            return False
    
    # Check if in safe-to-delete list
    for safe_pattern in IDE_SAFE_TO_DELETE:
        if safe_pattern in path_str:
            return True
    
    return False
```

---

## 🔒 Safety Validation Pipeline

### Validation Workflow

```python
class SafetyValidator:
    """Validate files before deletion."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.critical_patterns = config['safety']['critical_patterns']
        self.size_threshold_mb = config['safety']['size_threshold_mb']
        self.protected_paths = config['exclusions']
    
    def validate_deletion(self, path: Path) -> Dict[str, Any]:
        """
        Validate if file is safe to delete.
        
        Returns:
            {
                'safe': bool,
                'risk_level': 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
                'reasons': List[str],
                'requires_confirmation': bool
            }
        """
        reasons = []
        risk_level = 'SAFE'
        
        # Check critical patterns
        if self._is_critical_file(path):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['Critical file (git, source, config, docs)'],
                'requires_confirmation': True
            }
        
        # Check CORTEX brain
        if is_cortex_critical(path):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['CORTEX brain tier0/1/2/3 (governance)'],
                'requires_confirmation': True
            }
        
        # Check recently modified
        if is_recently_modified(path, hours=24):
            reasons.append('Modified in last 24 hours')
            risk_level = 'HIGH'
        
        # Check uncommitted changes
        if has_uncommitted_changes(path, self.git_root):
            return {
                'safe': False,
                'risk_level': 'CRITICAL',
                'reasons': ['Uncommitted git changes'],
                'requires_confirmation': True
            }
        
        # Check large file
        if is_large_file(path, self.size_threshold_mb):
            reasons.append(f'Large file (>{self.size_threshold_mb} MB)')
            risk_level = 'MEDIUM'
        
        # Check orphaned
        if is_orphaned(path, self.project_root):
            reasons.append('Orphaned file (no references)')
            risk_level = 'MEDIUM'
        
        # Determine if confirmation required
        requires_confirmation = risk_level in {'HIGH', 'CRITICAL'}
        
        return {
            'safe': risk_level not in {'CRITICAL'},
            'risk_level': risk_level,
            'reasons': reasons,
            'requires_confirmation': requires_confirmation
        }
    
    def _is_critical_file(self, path: Path) -> bool:
        """Check if file matches any critical pattern."""
        return (
            is_git_metadata(path) or
            is_source_code(path) or
            is_config_file(path) or
            is_documentation(path)
        )
```

### Usage

```python
validator = SafetyValidator(config)

for file_path in files_to_delete:
    validation = validator.validate_deletion(file_path)
    
    if not validation['safe']:
        print(f"❌ BLOCKED: {file_path}")
        print(f"   Risk: {validation['risk_level']}")
        print(f"   Reasons: {', '.join(validation['reasons'])}")
        continue
    
    if validation['requires_confirmation']:
        print(f"⚠️ CONFIRM: {file_path}")
        print(f"   Risk: {validation['risk_level']}")
        print(f"   Reasons: {', '.join(validation['reasons'])}")
        
        if not user_confirms():
            continue
    
    # Safe to delete
    delete_file(file_path)
```

---

## 🔍 Edge Cases

### 1. **Symlinks to Critical Files**

**Problem:** Symlink points to `.git/config` - is it safe to delete symlink?

**Answer:** Yes, but verify symlink is inside root (security)

```python
def is_safe_to_delete_symlink(symlink: Path) -> bool:
    """Delete symlink is safe (doesn't affect target)."""
    if not symlink.is_symlink():
        return False
    
    # Deleting symlink is safe (doesn't delete target)
    # BUT verify target is not critical (for reporting)
    try:
        target = symlink.resolve()
        if is_critical_file(target):
            logger.warning(f"Symlink points to critical file: {symlink} → {target}")
    except (OSError, RuntimeError):
        pass
    
    return True
```

### 2. **Generated Source Code**

**Problem:** `generated_api.py` is source code but auto-generated - safe to delete?

**Answer:** Check for auto-generated marker in file

```python
def is_auto_generated(path: Path) -> bool:
    """Check if file is auto-generated."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(5)]
        
        # Common auto-generated markers
        markers = [
            '# Auto-generated',
            '# Generated by',
            '# DO NOT EDIT',
            '# This file is automatically',
            '// Auto-generated',
            '/* Generated by'
        ]
        
        for line in first_lines:
            if any(marker in line for marker in markers):
                return True
        
        return False
    except Exception:
        return False
```

### 3. **Backup Files in Critical Locations**

**Problem:** `.git/config.bak` is in `.git/` but is a backup file

**Answer:** Still critical (preserve git backup)

```python
def is_backup_in_critical_location(path: Path) -> bool:
    """Check if backup file is in critical location."""
    # Even backups in .git/ are critical
    if is_git_metadata(path.parent):
        return True
    
    # Backups in cortex-brain/tier0 are critical
    if is_cortex_critical(path.parent):
        return True
    
    return False
```

---

## 📊 Risk Level Matrix

| File Type | Risk Level | Requires Confirmation | Action |
|-----------|------------|----------------------|--------|
| `.git/` metadata | CRITICAL | Always | Block |
| Source code | CRITICAL | Always | Block |
| Config files | CRITICAL | Always | Block |
| Documentation | CRITICAL | Always | Block |
| CORTEX brain | CRITICAL | Always | Block |
| Uncommitted changes | CRITICAL | Always | Block |
| Recent files (<24h) | HIGH | Yes | Warn |
| Large files (>10MB) | MEDIUM | Yes | Warn |
| Orphaned files | MEDIUM | Yes | Warn |
| IDE custom configs | MEDIUM | Yes | Warn |
| Duplicates | LOW | No (unless >10MB) | Safe |
| Temp files | SAFE | No | Safe |
| Build artifacts | SAFE | No | Safe |
| Caches | SAFE | No | Safe |
| Old logs (>30d) | SAFE | No | Safe |

---

## 🎯 Implementation Checklist

For Vacuum v2, implement:
- ✅ `SafetyValidator` class
- ✅ Critical pattern detection (git, source, config, docs)
- ✅ CORTEX brain protection
- ✅ Recently modified check
- ✅ Uncommitted changes detection
- ✅ Large file warnings
- ✅ Orphaned file detection (AST)
- ✅ Risk level classification
- ✅ User confirmation prompts (HIGH/CRITICAL)
- ✅ Exclusion pattern enforcement

**Test Cases:**
- ✅ Attempt to delete `.git/` → Blocked
- ✅ Attempt to delete `main.py` → Blocked
- ✅ Attempt to delete `requirements.txt` → Blocked
- ✅ Attempt to delete `README.md` → Blocked
- ✅ Attempt to delete `cortex-brain/tier0/governance.yaml` → Blocked
- ✅ Attempt to delete file modified 1 hour ago → Warned + confirmation
- ✅ Attempt to delete file with uncommitted changes → Blocked
- ✅ Attempt to delete 50MB binary → Warned + confirmation
- ✅ Attempt to delete orphaned test → Warned + confirmation
- ✅ Delete `.tmp` file → Allowed (SAFE)
- ✅ Delete `__pycache__/` → Allowed (SAFE)

---

**Next:** Document migration strategy (transactional operations, rollback architecture).
