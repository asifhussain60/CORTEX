# CORTEX Upgrade System - Fix Analysis

**Date:** 2025-11-23  
**Issue:** Upgrade script fails to handle branch-based development and git merges  
**Status:** ✅ ANALYSIS COMPLETE

---

## 🔍 Problems Identified

### 1. Git Merge Strategy (CRITICAL)
**Location:** `upgrade_orchestrator.py` - Missing git integration  
**Problem:**
- Script uses download/extract method only
- No git pull support when remote is configured
- Merge failures with unrelated histories not handled

**Impact:** Users with git remote configured cannot upgrade

**Fix Required:**
- Add git-aware upgrade path
- Detect if CORTEX is git repository
- Use `git pull --rebase` or `git merge --strategy-option=theirs` for clean merges

### 2. Version Comparison Logic
**Location:** `version_detector.py` (assumed - not read yet)  
**Problem:**
- Compares version numbers numerically (5.3.1 > 5.3.0)
- Doesn't account for branch-based development
- No semantic versioning comparison

**Impact:** False "already up to date" messages when development branch has newer features

**Fix Required:**
- Add branch awareness to version detection
- Compare commit timestamps when on same branch
- Show "branch: CORTEX-3.0" in version info

### 3. Missing Pre-Flight Validation
**Location:** `github_fetcher.py` + `upgrade_orchestrator.py`  
**Problem:**
- No validation of downloaded content
- Doesn't verify VERSION file in extracted package
- No integrity checks beyond checksums

**Impact:** Could install broken/incomplete packages

**Fix Required:**
- Validate VERSION file exists in extracted package
- Check for required directories (.github/prompts/, cortex-brain/, etc.)
- Verify critical files present before proceeding

### 4. Selective File Checkout Broken
**Location:** User's attempted manual fix  
**Problem:**
- `git checkout cortex-upstream/CORTEX-3.0 -- path` failed
- Files not found in expected paths
- No fallback strategy

**Impact:** Manual upgrade attempts fail

**Fix Required:**
- Add file existence check before git checkout
- Use git ls-tree to find actual file paths
- Provide helpful error messages

### 5. No Rollback for Failed Merges
**Location:** `upgrade_orchestrator.py`  
**Problem:**
- Backup created, but rollback only triggered on exceptions
- Failed git merge leaves repo in unstable state
- User must manually reset

**Impact:** System left in broken state after failed upgrade

**Fix Required:**
- Detect failed git operations
- Auto-rollback on merge conflicts
- Provide clear recovery instructions

---

## ✅ Recommended Solutions

### Solution 1: Git-Aware Upgrade Path (PRIORITY 1)

**Add to `upgrade_orchestrator.py`:**

```python
def _is_git_repository(self) -> bool:
    """Check if CORTEX is a git repository."""
    return (self.cortex_path / ".git").exists()

def _has_git_remote(self, remote_name: str = "cortex-upstream") -> bool:
    """Check if git remote is configured."""
    if not self._is_git_repository():
        return False
    
    import subprocess
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        cwd=self.cortex_path,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def _git_upgrade(self, branch: str = "CORTEX-3.0") -> bool:
    """Upgrade using git pull (preferred method)."""
    import subprocess
    
    print(f"🔄 Using git-based upgrade (faster, cleaner)")
    
    # Fetch latest
    print(f"   Fetching from upstream...")
    result = subprocess.run(
        ["git", "fetch", "cortex-upstream"],
        cwd=self.cortex_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Git fetch failed: {result.stderr}")
        return False
    
    # Check if there are updates
    result = subprocess.run(
        ["git", "log", "--oneline", f"HEAD..cortex-upstream/{branch}"],
        cwd=self.cortex_path,
        capture_output=True,
        text=True
    )
    
    commits_behind = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    
    if commits_behind == 0:
        print(f"✅ Already up to date with upstream")
        return True
    
    print(f"   Found {commits_behind} new commits")
    
    # Merge with conflict resolution
    print(f"   Merging updates...")
    result = subprocess.run(
        ["git", "merge", f"cortex-upstream/{branch}", "--strategy-option=theirs", "--no-edit"],
        cwd=self.cortex_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        # Try rebase as fallback
        print(f"   Merge failed, trying rebase...")
        result = subprocess.run(
            ["git", "rebase", f"cortex-upstream/{branch}"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Git operations failed")
            print(f"   Error: {result.stderr}")
            # Reset to clean state
            subprocess.run(["git", "merge", "--abort"], cwd=self.cortex_path)
            subprocess.run(["git", "rebase", "--abort"], cwd=self.cortex_path)
            return False
    
    print(f"✅ Git upgrade complete")
    return True

def upgrade(self, version: Optional[str] = None, dry_run: bool = False, skip_backup: bool = False) -> bool:
    """Perform complete CORTEX upgrade with git-aware strategy."""
    
    # ... existing code ...
    
    # Step 3: Choose upgrade method
    print(f"\n[3/8] Choosing Upgrade Method")
    
    if self._is_git_repository() and self._has_git_remote():
        print(f"   Detected git repository with upstream remote")
        
        if not dry_run:
            success = self._git_upgrade()
            if not success:
                print(f"   Git upgrade failed, falling back to download method")
                # Fall through to download method
            else:
                # Skip to validation steps
                # ... existing validation code ...
                return True
    
    # Download method (original code)
    print(f"   Using download method")
    # ... rest of existing code ...
```

### Solution 2: Enhanced Version Detection

**Add to `version_detector.py`:**

```python
def get_upgrade_info(self) -> Dict:
    """Get upgrade information with git awareness."""
    info = {
        "current_version": self.get_current_version(),
        "latest_version": self.get_latest_version(),
        "deployment_type": self.get_deployment_type(),
        "upgrade_available": False,
        "git_repository": False,
        "git_remote": None,
        "commits_behind": 0
    }
    
    # Check if git repository
    if (self.cortex_path / ".git").exists():
        info["git_repository"] = True
        
        # Check for upstream remote
        import subprocess
        result = subprocess.run(
            ["git", "remote", "get-url", "cortex-upstream"],
            cwd=self.cortex_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            info["git_remote"] = result.stdout.strip()
            
            # Count commits behind
            result = subprocess.run(
                ["git", "log", "--oneline", "HEAD..cortex-upstream/CORTEX-3.0"],
                cwd=self.cortex_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                commits = result.stdout.strip().split('\n')
                info["commits_behind"] = len(commits)
                info["upgrade_available"] = True
    
    # Version comparison (existing logic)
    if not info["upgrade_available"]:
        info["upgrade_available"] = self._compare_versions(
            info["current_version"],
            info["latest_version"]
        ) < 0
    
    return info
```

### Solution 3: Pre-Flight Validation

**Add to `github_fetcher.py`:**

```python
def validate_extracted_package(self, extracted_path: Path) -> Dict[str, bool]:
    """
    Validate extracted CORTEX package has required structure.
    
    Args:
        extracted_path: Path to extracted CORTEX directory
        
    Returns:
        Dictionary of validation results
    """
    print(f"🔍 Validating extracted package...")
    
    required_files = [
        "VERSION",
        ".github/prompts/CORTEX.prompt.md",
        "cortex-brain/response-templates.yaml",
        "cortex-brain/capabilities.yaml",
        "scripts/cortex-upgrade.py"
    ]
    
    required_dirs = [
        ".github/prompts",
        "cortex-brain",
        "scripts",
        "src"
    ]
    
    results = {}
    
    # Check files
    for file_path in required_files:
        full_path = extracted_path / file_path
        results[f"file:{file_path}"] = full_path.exists()
        status = "✅" if results[f"file:{file_path}"] else "❌"
        print(f"   {status} {file_path}")
    
    # Check directories
    for dir_path in required_dirs:
        full_path = extracted_path / dir_path
        results[f"dir:{dir_path}"] = full_path.exists() and full_path.is_dir()
        status = "✅" if results[f"dir:{dir_path}"] else "❌"
        print(f"   {status} {dir_path}/")
    
    all_valid = all(results.values())
    print(f"\n{'✅' if all_valid else '❌'} Package validation: {'PASSED' if all_valid else 'FAILED'}")
    
    return results
```

---

## 📋 Implementation Plan

### Phase 1: Git-Aware Upgrade (60 min)
1. ✅ Add git detection methods to `upgrade_orchestrator.py`
2. ✅ Implement `_git_upgrade()` method
3. ✅ Add merge conflict handling
4. ✅ Update main `upgrade()` flow to prefer git method

### Phase 2: Enhanced Version Detection (30 min)
1. ✅ Add git awareness to `version_detector.py`
2. ✅ Implement commit-based comparison
3. ✅ Update version display format

### Phase 3: Validation Enhancement (30 min)
1. ✅ Add package validation to `github_fetcher.py`
2. ✅ Integrate validation into upgrade flow
3. ✅ Add helpful error messages

### Phase 4: Testing (45 min)
1. Test git-based upgrade path
2. Test download-based upgrade path
3. Test rollback scenarios
4. Verify brain data preservation

---

## 🎯 Expected Outcomes

**Before Fix:**
- ❌ Git merge fails with unrelated histories
- ❌ Version comparison shows false "up to date"
- ❌ No validation of downloaded packages
- ❌ Manual upgrade attempts fail

**After Fix:**
- ✅ Git-aware upgrade (preferred method)
- ✅ Smart version detection with commit awareness
- ✅ Package validation before installation
- ✅ Clean rollback on failures
- ✅ Better error messages and recovery instructions

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
