# CORTEX Deployment & Production Setup Enhancement Plan

**Version:** 2.0.0  
**Date:** December 16, 2025  
**Author:** Asif Hussain  
**Status:** 📋 Planning Phase → 🚧 Implementation Ready

---

## 📊 Master Plan Status Tracker

| Phase | Sub-Plan | Status | Progress | Owner | Target |
|-------|----------|--------|----------|-------|--------|
| **Phase 1** | Universal Setup Script | 📋 Planned | 0% | Asif | Week 1 |
| **Phase 2** | Python Compatibility Matrix | 📋 Planned | 0% | Asif | Week 1 |
| **Phase 2.5** | Git Detection & PATH Fix | 📋 Planned | 0% | Asif | Week 1 |
| **Phase 3** | Missing Files Auto-Creation | 📋 Planned | 0% | Asif | Week 1 |
| **Phase 4** | User Workspace Integration | 📋 Planned | 0% | Asif | Week 2 |
| **Phase 5** | Enhanced Documentation | 📋 Planned | 0% | Asif | Week 2 |
| **Phase 6** | Automated Testing | 📋 Planned | 0% | Asif | Week 3 |
| **Phase 7** | Uninstall & Cleanup System | 📋 Planned | 0% | Asif | Week 2 |
| **Phase 8** | Intelligent Upgrade System | ✅ Exists | 80% | Asif | Week 2 |

**Legend:** 📋 Planned | 🚧 In Progress | ✅ Complete | ⚠️ Blocked | ❌ Cancelled

**Overall Progress:** 8.9% (1 of 9 phases mostly complete)

**Critical Path:** Phase 1 → Phase 2.5 → Phase 3 → Phase 5 (Documentation)

---

## 🧠 CORTEX Enhancement Initiative
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 📑 Sub-Plan Index

Each phase is documented as a standalone sub-plan with detailed implementation specs:

1. **[Phase 1: Universal Setup Script](#phase-1-universal-setup-script-week-1)** - Single-command installation
2. **[Phase 2: Python Compatibility Matrix](#phase-2-python-compatibility-matrix-week-1)** - Version constraints
3. **[Phase 2.5: Git Detection & PATH Fix](#phase-25-git-detection--path-fix-week-1-new)** - Windows Git auto-config
4. **[Phase 3: Missing Files Auto-Creation](#phase-3-missing-files-auto-creation-week-1)** - Brain structure builder
5. **[Phase 4: User Workspace Integration](#phase-4-user-workspace-integration-week-2)** - Multi-project support
6. **[Phase 5: Enhanced Documentation](#phase-5-enhanced-documentation-week-2)** - Setup guides
7. **[Phase 6: Automated Testing](#phase-6-automated-testing-week-3)** - CI/CD validation
8. **[Phase 7: Uninstall & Cleanup](#phase-7-uninstall--cleanup-system-week-2-new)** - Complete removal
9. **[Phase 8: Intelligent Upgrade](#phase-8-intelligent-upgrade-system-week-2-new)** - Safe updates

---

## 🎯 Understanding & Scope

### Problem Statement

Based on analysis of `cortex-setup-issues.md`, multiple users encountered significant friction during CORTEX setup:

**Critical Issues Identified:**
1. ❌ **Git Not Found** - Users without Git needed manual installation via winget
2. ❌ **Python Command Variability** - `python` vs `python3` vs full path confusion
3. ❌ **Python 3.14 Compatibility** - Some packages (tree-sitter-languages, numpy 1.26.4) lack Python 3.14 wheels
4. ❌ **Missing __init__.py Files** - `src/core/__init__.py` missing causing import failures
5. ❌ **PYTHONPATH Not Set** - Manual environment variable configuration required
6. ❌ **Virtual Environment Confusion** - Wrong environment selected ("luum-fresh" instead of CORTEX .venv)
7. ❌ **Missing CORTEX Prompt in User Repos** - Copilot not loading CORTEX capabilities in user workspaces
8. ❌ **No SETUP-CORTEX.md** - Referenced file doesn't exist in repository
9. ⚠️ **Manual Directory Creation** - `cortex-brain/tier1`, `cortex-brain/documents/reports` needed manual creation
10. ⚠️ **Validation Script Errors** - `setup_epm_orchestrator --validate` failed

### Current State Analysis

**Existing Setup Infrastructure:**
```
CORTEX/
├── install-cortex-windows-fast.ps1    # Fast bootstrap (core deps only)
├── install-cortex-unix-fast.sh        # Unix equivalent
├── scripts/
│   ├── setup_cortex.py                # Standalone setup via CortexEntry
│   └── post_deployment_check.py       # Comprehensive validation
├── src/
│   ├── setup/
│   │   └── setup_orchestrator.py      # Module-based orchestration
│   └── entry_point/
│       └── cortex_entry.py            # Main entry point
├── requirements.txt                   # Production deps (9 packages, ~20 MB)
├── requirements-dev.txt               # Development deps
├── requirements-optional.txt          # Optional ML features
└── cortex.config.template.json        # Configuration template
```

**What Works:**
- ✅ Streamlined dependencies (9 core packages from 67 legacy ones)
- ✅ Fast install script (`install-cortex-windows-fast.ps1`)
- ✅ Comprehensive post-deployment validation
- ✅ Setup orchestrator with modular architecture
- ✅ Machine-specific config via `cortex.config.json`

**What's Missing:**
- ❌ Single, reliable entry point for first-time setup
- ❌ Pre-flight dependency checks (Git, Python version)
- ❌ Automatic virtual environment creation & activation
- ❌ Python version compatibility matrix
- ❌ Missing file auto-creation (\_\_init\_\_.py, directories)
- ❌ Clear setup documentation (SETUP-CORTEX.md doesn't exist)
- ❌ User workspace integration workflow
- ❌ Post-setup validation with actionable fixes

### Success Criteria

**User Experience Goals:**
1. **One-Command Setup** - `python scripts/install_cortex.py` handles everything
2. **Zero Manual Intervention** - All directories, files, configs created automatically
3. **Smart Environment Detection** - Auto-detect Python, Git, venv status
4. **Clear Error Messages** - Actionable guidance for every failure
5. **90-Second Setup** - From clone to ready (excluding package downloads)
6. **Works on Fresh Machines** - No assumptions about installed software

---

## ⚡ Approach & Considerations

### Technical Challenges

**Challenge 1: Cross-Platform Consistency**
- Windows: PowerShell, .exe extensions, backslashes
- Unix/macOS: Bash/zsh, forward slashes, different paths
- **Solution:** Python-based installer (platform-agnostic) + shell wrappers

**Challenge 2: Git Detection & PATH Configuration**
- Windows: Git installed but not in PATH (common with GitExtensions, GitHub Desktop)
- Multiple Git locations: Program Files, Git Bash, GitExtensions, Portable
- **Solution:** Smart Git finder that scans common locations + auto-adds to PATH

**Challenge 3: Python Version Detection**
- Commands: `python`, `python3`, `py`, full paths
- Multiple installations: System, Anaconda, pyenv, Windows Store
- **Solution:** Smart detector that tries all variants, validates version >= 3.8

**Challenge 4: Dependency Hell**
- Python 3.14 too new (no wheels for some packages)
- Python 3.7 too old (missing features)
- **Solution:** Version compatibility matrix + fallback strategies

**Challenge 5: Virtual Environment Isolation**
- VS Code picks wrong environment
- PYTHONPATH conflicts between projects
- **Solution:** Explicit .venv activation + VS Code settings.json update

**Challenge 6: Stateful Setup**
- Partial failures leave incomplete setup
- Re-running setup causes duplicates
- **Solution:** Idempotent operations + state tracking + resume capability

---

## 💬 Response: Proposed Enhancement Architecture

### Phase 1: Universal Setup Script (Week 1)

**Goal:** Single, reliable setup entry point for all platforms

**Deliverables:**
1. **`scripts/install_cortex.py`** - Universal installer
   - Pre-flight checks (Git detection + PATH fix, Python, disk space)
   - Automatic Git PATH configuration (Windows)
   - Virtual environment creation/detection
   - Dependency installation with fallbacks
   - Brain initialization (directories, databases)
   - Configuration file setup
   - Post-setup validation
   - Actionable error reporting

2. **Shell Wrappers**
   - `install-cortex.sh` (Unix/macOS)
   - `install-cortex.ps1` (Windows)
   - Both invoke Python installer

3. **`SETUP-CORTEX.md`** - Comprehensive setup guide
   - Prerequisites (Git 2.x, Python 3.8-3.13)
   - Installation instructions (Windows/macOS/Linux)
   - Troubleshooting guide
   - FAQ section

**Architecture:**
```python
# scripts/install_cortex.py

class CortexInstaller:
    def __init__(self):
        self.state = SetupState()  # Track progress
        self.logger = SetupLogger()
        self.platform = PlatformDetector()
    
    def run(self):
        """Main installation workflow."""
        try:
            self.preflight_checks()     # Step 1: Validate environment
            self.setup_venv()            # Step 2: Create/activate venv
            self.install_dependencies()  # Step 3: Install packages
            self.initialize_brain()      # Step 4: Create directories/DBs
            self.configure_project()     # Step 5: Setup config files
            self.validate_installation() # Step 6: Run post-checks
            self.print_success_message() # Step 7: Next steps
        except SetupError as e:
            self.handle_failure(e)
            self.print_recovery_steps()
    def preflight_checks(self):
        """Validate all prerequisites."""
        checks = [
            GitInstallationCheck(auto_fix_path=True),  # NEW: Auto-add to PATH
            PythonVersionCheck(min_version="3.8", max_version="3.13"),
            DiskSpaceCheck(required_mb=500),
            NetworkConnectivityCheck(),
            WritePermissionCheck()
        ]
        for check in checks:
            check.run()
    
    def fix_git_path_windows(self):
        """
        Detect Git installation and add to PATH if missing (Windows only).
        
        Common Git locations on Windows:
        - C:\Program Files\Git\cmd\git.exe (Official installer)
        - C:\Program Files (x86)\Git\cmd\git.exe (32-bit)
        - C:\Program Files (x86)\GitExtensions\Git\cmd\git.exe
        - Portable installations
        - GitHub Desktop: %LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\git\cmd\git.exe
        
        Returns:
            str: Path to git.exe if found and added to PATH
        """
        if not self.platform.is_windows():
            return None
        
        # Check if git already in PATH
        if shutil.which('git'):
            self.logger.info("✓ Git found in PATH")
            return shutil.which('git')
        
        self.logger.warning("⚠ Git not in PATH, searching common locations...")
        
        # Common Git installation paths (Windows)
        search_paths = [
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files (x86)\Git\cmd",
            r"C:\Program Files (x86)\GitExtensions\Git\cmd",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Git', 'cmd'),
        ]
        
        # Search GitHub Desktop installations
        github_desktop_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'GitHubDesktop')
        if os.path.exists(github_desktop_base):
            for app_folder in glob.glob(os.path.join(github_desktop_base, 'app-*')):
                search_paths.append(os.path.join(app_folder, 'resources', 'app', 'git', 'cmd'))
        
        # Find git.exe
        git_exe_path = None
        for path in search_paths:
            git_candidate = os.path.join(path, 'git.exe')
            if os.path.exists(git_candidate):
                git_exe_path = path
                self.logger.info(f"✓ Found Git at: {git_exe_path}")
                break
        
        if not git_exe_path:
            raise SetupError(
                "Git not found. Please install Git from: https://git-scm.com/download/win\n"
                "Or use: winget install --id Git.Git -e --source winget"
            )
        
        # Add to PATH (for current session)
        current_path = os.environ.get('PATH', '')
        if git_exe_path not in current_path:
            os.environ['PATH'] = f"{git_exe_path};{current_path}"
            self.logger.info(f"✓ Added Git to PATH: {git_exe_path}")
        
        # Add to user PATH permanently (Windows Registry)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                user_path, _ = winreg.QueryValueEx(key, 'PATH')
                if git_exe_path not in user_path:
                    new_path = f"{user_path};{git_exe_path}" if user_path else git_exe_path
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                    self.logger.info("✓ Git added to user PATH permanently")
                    self.logger.warning("⚠ Restart terminal/VS Code to use git from new PATH")
        except Exception as e:
            self.logger.warning(f"⚠ Could not update user PATH permanently: {e}")
            self.logger.info("  Git available in current session only")
        
        return git_exe_pathecks:
            check.run()
    
    def setup_venv(self):
        """Create and activate virtual environment."""
        venv_path = Path.cwd() / ".venv"
        
        if venv_path.exists():
            self.logger.info("✓ Virtual environment exists")
            return
        
        self.logger.info("Creating virtual environment...")
        python_exe = self.platform.find_python()
        subprocess.run([python_exe, "-m", "venv", str(venv_path)])
        
        # Update VS Code settings
        self.update_vscode_settings(venv_path)
    
    def install_dependencies(self):
        """Install Python packages with fallback strategies."""
        requirements = [
            ("requirements.txt", "core"),
            ("requirements-optional.txt", "optional")
        ]
        
        for req_file, category in requirements:
            try:
                self.pip_install(req_file)
            except InstallError as e:
                if category == "core":
                    # Try fallback versions
                    self.install_with_fallbacks(req_file)
                else:
                    self.logger.warning(f"Skipping optional: {req_file}")
    
    def initialize_brain(self):
        """Create brain structure and databases."""
        brain_init = BrainInitializer()
        brain_init.create_directories()  # tier0-3, documents/*
        brain_init.create_databases()     # SQLite DBs
        brain_init.create_init_files()    # All __init__.py files
        brain_init.verify_structure()
    
    def validate_installation(self):
        """Run comprehensive post-setup validation."""
        validator = PostDeploymentValidator(
            cortex_root=Path.cwd(),
            verbose=True
        )
        passed, warnings, failures = validator.run_all_validations()
        
        if failures > 0:
            raise ValidationError(f"{failures} critical issues found")
```

**Success Metrics:**
- ✅ Zero manual steps required
- ✅ Works on Windows 10/11, macOS 12+, Ubuntu 20.04+
- ✅ Handles Python 3.8 - 3.13 (avoids 3.14 issues)
- ✅ Completes in < 90 seconds (excluding downloads)
- ✅ 100% idempotent (safe to re-run)

### Phase 2: Python Compatibility Matrix (Week 1)

**Goal:** Document and enforce Python version constraints

**Deliverables:**
1. **`docs/PYTHON-COMPATIBILITY.md`**
   - Tested versions matrix
   - Known issues per version
   - Package-specific constraints

2. **Version Detection in Setup**
   ```python
   SUPPORTED_VERSIONS = {
       "3.8": {"status": "supported", "notes": "Minimum version"},
       "3.9": {"status": "recommended", "notes": "Fully tested"},
       "3.10": {"status": "recommended", "notes": "Fully tested"},
       "3.11": {"status": "recommended", "notes": "Fully tested"},
       "3.12": {"status": "supported", "notes": "Works with numpy 2.x"},
       "3.13": {"status": "supported", "notes": "Works with numpy 2.x"},
       "3.14": {"status": "unsupported", "notes": "Missing package wheels"}
   }
   ```

3. **Fallback Package Versions**
   ```requirements
   # requirements-fallback.txt
   # For Python 3.12-3.14 (no numpy 1.x wheels)
   numpy>=2.0.0              # Fallback to 2.x
   scikit-learn>=1.5.2       # Compatible with numpy 2.x
   
   # For Python 3.8-3.11 (prefer numpy 1.x)
   numpy>=1.24.0,<2.0.0      # Stable 1.x branch
   scikit-learn>=1.3.0       # Compatible with numpy 1.x
   ```

---

### Phase 2.5: Git Detection & PATH Fix (Week 1) **NEW**

**Goal:** Eliminate Git-related setup issues on Windows

**Problem Analysis (from user reports):**
- Git installed but `git` command not found
- Multiple Git installations (Git Bash, GitExtensions, GitHub Desktop)
- Users manually tried PATH manipulation without success

**Deliverables:**

1. **`scripts/utils/git_finder.py`** - Smart Git detection
   ```python
   class GitFinder:
       """
       Locate Git on Windows and add to PATH if needed.
       
       Searches common locations:
       - Program Files\Git\cmd
       - Program Files (x86)\Git\cmd  
       - GitExtensions installation
       - GitHub Desktop portable Git
       - User-specified locations
       """
       
       COMMON_GIT_PATHS = [
           r"C:\Program Files\Git\cmd",
           r"C:\Program Files (x86)\Git\cmd",
           r"C:\Program Files (x86)\GitExtensions\Git\cmd",
           # GitHub Desktop: %LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\git\cmd
       ]
       
       def find_git(self) -> Optional[Path]:
           """Locate git.exe on system."""
           # Check PATH first
           if shutil.which('git'):
               return Path(shutil.which('git')).parent
           
           # Search common locations
           for path_str in self.COMMON_GIT_PATHS:
               git_exe = Path(path_str) / "git.exe"
               if git_exe.exists():
                   return Path(path_str)
           
           # Search GitHub Desktop
           local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
           github_desktop = local_appdata / 'GitHubDesktop'
           if github_desktop.exists():
               for app_folder in github_desktop.glob('app-*'):
                   git_path = app_folder / 'resources' / 'app' / 'git' / 'cmd'
                   if (git_path / 'git.exe').exists():
                       return git_path
           
           return None
       
       def add_to_path(self, git_path: Path, permanent: bool = True) -> bool:
           """
           Add Git to Windows PATH.
           
           Args:
               git_path: Path to Git cmd directory
               permanent: If True, update user PATH in registry
           
           Returns:
               True if successful
           """
           # Session PATH (immediate)
           current_path = os.environ.get('PATH', '')
           git_path_str = str(git_path)
           
           if git_path_str not in current_path:
               os.environ['PATH'] = f"{git_path_str};{current_path}"
               logger.info(f"✓ Git added to session PATH: {git_path_str}")
           
           # Permanent PATH (requires restart)
           if permanent and sys.platform == 'win32':
               try:
                   import winreg
                   with winreg.OpenKey(
                       winreg.HKEY_CURRENT_USER,
                       'Environment',
                       0,
                       winreg.KEY_ALL_ACCESS
                   ) as key:
                       user_path, _ = winreg.QueryValueEx(key, 'PATH')
                       
                       if git_path_str not in user_path:
                           new_path = f"{user_path};{git_path_str}" if user_path else git_path_str
                           winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                           logger.info("✓ Git added to user PATH permanently")
                           logger.warning("⚠ Restart terminal/VS Code to use git from new PATH")
                           return True
               except Exception as e:
                   logger.warning(f"⚠ Could not update user PATH: {e}")
                   logger.info("  Git available in current session only")
                   return False
           
           return True
   ```

2. **`scripts/utils/path_manager.py`** - Windows PATH manipulation
   ```python
   class WindowsPathManager:
       """Manage Windows PATH environment variable."""
       
       @staticmethod
       def get_user_path() -> str:
           """Get current user PATH from registry."""
           import winreg
           with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
               path, _ = winreg.QueryValueEx(key, 'PATH')
               return path
       
       @staticmethod
       def set_user_path(new_path: str) -> bool:
           """Set user PATH in registry."""
           import winreg
           try:
               with winreg.OpenKey(
                   winreg.HKEY_CURRENT_USER,
                   'Environment',
                   0,
                   winreg.KEY_ALL_ACCESS
               ) as key:
                   winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                   return True
           except Exception:
               return False
       
       @staticmethod
       def append_to_path(new_dir: str) -> bool:
           """Append directory to user PATH."""
           current = WindowsPathManager.get_user_path()
           if new_dir not in current:
               new_path = f"{current};{new_dir}" if current else new_dir
               return WindowsPathManager.set_user_path(new_path)
           return True
   ```

3. **`docs/GIT-SETUP-GUIDE.md`** - Troubleshooting guide
   ```markdown
   # Git Setup & Troubleshooting Guide
   
   ## Automatic Git Detection (Windows)
   
   CORTEX installer automatically:
   1. Searches for Git in common locations
   2. Adds Git to your PATH if missing
   3. Validates `git` command works
   
   ## Common Git Locations
   
   - **Git for Windows:** `C:\Program Files\Git\cmd\git.exe`
   - **GitExtensions:** `C:\Program Files (x86)\GitExtensions\Git\cmd\git.exe`
   - **GitHub Desktop:** `%LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\git\cmd\git.exe`
   
   ## Manual PATH Fix (if auto-fix fails)
   
   1. Find your Git installation:
      ```powershell
      Get-ChildItem "C:\Program Files" -Recurse -Filter "git.exe" 2>$null | 
          Where-Object { $_.FullName -like "*\cmd\*" } | 
          Select-Object -First 1 FullName
      ```
   
   2. Add to PATH:
      - Press `Win + Pause` → Advanced system settings
      - Environment Variables → User variables → PATH
      - Add: `C:\Program Files\Git\cmd` (or your Git location)
   
   3. Restart terminal/VS Code
   
   ## Verification
   
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```
   ```

4. **Integration into Universal Installer**
   - Pre-flight check: Git detection
   - Auto-fix: Add to PATH if found
   - Fallback: Offer to install via winget
   - User guidance: Show manual steps if all else fails

**Success Metrics:**
- ✅ 95%+ of Windows users have Git working after install
- ✅ No manual PATH manipulation required
- ✅ Clear guidance for edge cases
- ✅ Works with all common Git installations

---

### Phase 3: Missing Files Auto-Creation (Week 1)

**Goal:** Eliminate manual directory/file creation steps

**Deliverables:**
1. **`src/setup/brain_structure_builder.py`**
   ```python
   class BrainStructureBuilder:
       """Ensures all required brain structure exists."""
       
       REQUIRED_DIRECTORIES = [
           "cortex-brain/tier0",
           "cortex-brain/tier1", 
           "cortex-brain/tier2",
           "cortex-brain/tier3",
           "cortex-brain/documents/reports",
           "cortex-brain/documents/analysis",
           "cortex-brain/documents/summaries",
           "cortex-brain/documents/investigations",
           "cortex-brain/documents/planning",
           "cortex-brain/documents/implementation-guides",
           "cortex-brain/backups",
           "logs",
           "tests"
       ]
       
       REQUIRED_INIT_FILES = [
           "src/__init__.py",
           "src/core/__init__.py",
           "src/tier0/__init__.py",
           "src/tier1/__init__.py",
           "src/tier2/__init__.py",
           "src/tier3/__init__.py",
           "src/cortex_agents/__init__.py",
           "src/orchestrators/__init__.py",
           "tests/__init__.py"
       ]
       
       def build(self):
           """Create all required structure."""
           self.create_directories()
           self.create_init_files()
           self.create_config_files()
           self.validate_structure()
   ```

2. **Validation in Setup**
   - Check before setup
   - Create missing items
   - Verify permissions

### Phase 4: User Workspace Integration (Week 2)

**Goal:** Seamless CORTEX integration into user projects

**Deliverables:**
1. **`scripts/integrate_cortex.py`** - Add CORTEX to user workspace
   ```bash
   # Run from user's project directory
   python /path/to/CORTEX/scripts/integrate_cortex.py
   ```

2. **Integration Actions:**
   - Copy `.github/prompts/` structure
   - Update `.github/copilot-instructions.md`
   - Create `.cortex/` directory
   - Add `.cortexignore` (similar to .gitignore)
   - Configure workspace settings

3. **`docs/WORKSPACE-INTEGRATION.md`**
   - Embedded vs Referenced mode
   - Multi-folder workspace setup
   - Prompt loading mechanics

### Phase 5: Enhanced Documentation (Week 2)

**Goal:** Clear, comprehensive setup documentation

**Deliverables:**
1. **`SETUP-CORTEX.md`** (Top-level)
   - Quick start (< 5 minutes)
   - Prerequisites
   - Installation steps
   - Troubleshooting
   - FAQ

2. **`docs/INSTALLATION-GUIDE.md`** (Detailed)
   - Platform-specific instructions
   - Advanced configuration
   - Multiple Python versions
   - Enterprise environments
   - Offline installation

3. **`docs/TROUBLESHOOTING.md`**
   - Common errors with solutions
   - Diagnostic commands
   - Log analysis
   - Getting help

### Phase 6: Automated Testing (Week 3)

**Goal:** Verify setup works across environments

**Deliverables:**
1. **Setup Integration Tests**
   ```python
   # tests/integration/test_setup_workflow.py
   
   def test_fresh_install_workflow():
       """Test complete setup from scratch."""
       with TempWorkspace() as ws:
           installer = CortexInstaller(ws.path)
           result = installer.run()
           
           assert result.success
           assert ws.has_venv()
           assert ws.brain_initialized()
           assert ws.config_valid()
   
   def test_setup_idempotency():
       """Verify setup can be re-run safely."""
       with ExistingWorkspace() as ws:
           installer = CortexInstaller(ws.path)
           
           result1 = installer.run()
           result2 = installer.run()  # Re-run
           
           assert result1.success
           assert result2.success
           assert result1.state == result2.state
   ```

2. **CI/CD Pipeline** (`.github/workflows/test-setup.yml`)
   - Test on Windows, macOS, Ubuntu
   - Test with Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
   - Test fresh install vs upgrade
   - Test with/without Git pre-installed

---

## 📊 Impact & Changes

### Files to Create

**New Setup Infrastructure:**
```
CORTEX/
├── SETUP-CORTEX.md                    # Quick start guide
├── scripts/
│   ├── install_cortex.py              # Universal installer
│   ├── integrate_cortex.py            # User workspace integration
│   └── validate_setup.py              # Setup validator
├── src/
│   └── setup/
│       ├── brain_structure_builder.py # Auto-create directories
│       ├── platform_detector.py       # Cross-platform utilities
│       ├── python_finder.py           # Smart Python detection
│       ├── dependency_installer.py    # With fallback strategies
│       └── vscode_configurator.py     # Auto-configure VS Code
├── docs/
│   ├── INSTALLATION-GUIDE.md          # Detailed setup docs
│   ├── PYTHON-COMPATIBILITY.md        # Version matrix
│   ├── WORKSPACE-INTEGRATION.md       # User project setup
│   └── TROUBLESHOOTING.md             # Common issues
├── tests/
│   └── integration/
│       ├── test_setup_workflow.py     # Setup tests
│       └── test_workspace_integration.py
└── .github/
    └── workflows/
        └── test-setup.yml              # CI for setup testing
```

### Files to Modify

**Enhanced Existing Scripts:**
- `install-cortex-windows-fast.ps1` → Wrapper for `install_cortex.py`
- `install-cortex-unix-fast.sh` → Wrapper for `install_cortex.py`
- `requirements.txt` → Add version constraints
- `requirements-fallback.txt` → New file for Python 3.12+ fallbacks
- `cortex.config.template.json` → Add setup metadata
- `README.md` → Update setup instructions

### Removed/Deprecated

**Consolidation:**
- ~~`scripts/cortex/install-cortex.py`~~ → Use new `scripts/install_cortex.py`
- ~~Various setup scripts~~ → Consolidated into single installer

---

## 🔍 Next Steps

### Immediate Actions (This Week)

- [ ] **Phase 1.1:** Create `scripts/install_cortex.py` skeleton
- [ ] **Phase 1.2:** Implement `PlatformDetector` class
- [ ] **Phase 1.3:** Implement `PythonFinder` class
- [ ] **Phase 1.4:** Implement `GitFinder` with auto-PATH fix (Windows)
- [ ] **Phase 1.5:** Write `SETUP-CORTEX.md` draft

### Week 1 Goals

- [ ] Complete Phase 1: Universal Setup Script
  - [ ] Git detection + automatic PATH configuration (Windows)
  - [ ] Python version detection with fallbacks
  - [ ] Virtual environment creation
- [ ] Complete Phase 2: Python Compatibility Matrix  
- [ ] Complete Phase 3: Auto-creation of missing files
- [ ] Create `docs/GIT-SETUP-GUIDE.md` troubleshooting guide
- [ ] Initial testing on Windows + macOS

### Week 2 Goals

- [ ] Complete Phase 4: User Workspace Integration
- [ ] Complete Phase 5: Enhanced Documentation
- [ ] Testing across Python 3.8-3.13
- [ ] User acceptance testing

### Week 3 Goals

- [ ] Complete Phase 6: Automated Testing
- [ ] CI/CD pipeline setup
- [ ] Final validation across all platforms
- [ ] Release CORTEX 3.10.0 with enhanced setup

### Success Validation

**Metrics to Track:**
1. ✅ Setup success rate (target: 95%+)
2. ✅ Average setup time (target: < 90 seconds)
3. ✅ User-reported issues (target: < 5% of users)
4. ✅ Re-run safety (target: 100% idempotent)
5. ✅ Platform coverage (Windows/macOS/Linux all supported)

**User Testing Criteria:**
- Fresh machine setup (no Git/Python pre-installed)
- Existing CORTEX upgrade
- Multi-workspace scenarios
- Different Python versions
- Network-restricted environments

---

## 📝 Implementation Notes

### Design Principles

1. **Idempotent Operations** - All setup steps safe to re-run
2. **Fail-Safe Defaults** - Setup continues when possible, graceful degradation
3. **Clear Feedback** - Progress indicators, actionable error messages
4. **State Tracking** - Resume capability for interrupted setups
5. **Platform Agnostic** - Python-first, shell wrappers for convenience

**Technology Choices**

**Why Python for Installer?**
- ✅ Cross-platform (Windows/macOS/Linux)
- ✅ Already required for CORTEX
- ✅ Rich standard library (subprocess, pathlib, venv, winreg)
- ✅ Easy to test and maintain

**Why Shell Wrappers?**
- ✅ Familiar entry point (`./install.sh`)
- ✅ Can bootstrap Python if needed
- ✅ One-liner installation experience

**Why Auto-Fix Git PATH on Windows?**
- ✅ Most common setup issue (from user reports)
- ✅ Git often installed but not in PATH (GitExtensions, GitHub Desktop)
- ✅ Simple registry update solves permanently
- ✅ Fallback to session-only if registry fails

### Risk Mitigation

**Risk 1: User has Python 3.14**
- **Mitigation:** Clear error with recommendation to install 3.13
- **Fallback:** Attempt to install with numpy 2.x

**Risk 2: Corporate firewall blocks PyPI**
- **Mitigation:** Document offline installation process
- **Fallback:** Pre-built wheel cache option

**Risk 3: Multiple Python installations**
- **Mitigation:** Smart detection tries all variants
- **Fallback:** Let user specify Python path explicitly

**Risk 4: Git installed but not in PATH (Windows)**
- **Mitigation:** Auto-detect common Git locations + add to PATH
- **Fallback:** Provide manual PATH instructions with detected Git location

**Risk 5: Setup partially completes**
- **Mitigation:** State tracking + resume capability
- **Fallback:** Clear cleanup instructions

---

## 🎓 References

**Related Documentation:**
- `README.md` - Current setup instructions
- `cortex-brain/documents/implementation-guides/setup-epm-implementation-summary.md`
- `tests/plugins/README.md` - Testing infrastructure
- `SETUP-CORTEX.md` - User setup guide (to be updated)
- `CORTEX-CLEANUP.md` - Uninstall guide (Phase 7)
- `UPGRADE.md` - Upgrade guide (Phase 8)

**User Reports:**
- `.github/copilot/copilot-chats/cortex-setup-issues.md` - Real user struggles

**Technical Resources:**
- Python venv: https://docs.python.org/3/library/venv.html
- Platform detection: https://docs.python.org/3/library/platform.html
- VS Code settings: https://code.visualstudio.com/docs/python/environments

**Existing Upgrade Infrastructure:**
- `src/operations/modules/upgrade/upgrade_utility.py` - 7-phase upgrade system (80% complete)
- `cortex-operations.yaml` - Upgrade operation definition

---

## 📋 Phase 7: Uninstall & Cleanup System (Week 2) **NEW**

**Sub-Plan:** CORTEX Complete Removal & Cleanup  
**Status:** 📋 Planned  
**Dependencies:** None (standalone operation)  
**Risk Level:** 🔴 HIGH - Data loss if brain backup skipped

### Goal

Provide users with a safe, complete, and verifiable way to uninstall CORTEX from their machine, including:
- Python packages (core + optional dependencies)
- Brain data (with backup option)
- Configuration files
- Cached data
- Virtual environments
- User workspace integrations

### Problem Statement

**Current State:**
- ❌ No official uninstall process
- ❌ Users manually delete directories (risk of leaving artifacts)
- ❌ Python packages remain installed (wasted disk space)
- ❌ Brain data potentially lost without backup
- ❌ No verification that uninstall completed successfully

**User Needs:**
1. **Safe Brain Backup** - Preserve learning/context before removal
2. **Complete Cleanup** - Remove all CORTEX artifacts
3. **Selective Uninstall** - Option to keep brain data for reinstall
4. **Verification** - Confirm complete removal
5. **Reversibility** - Ability to reinstall with preserved data

### Deliverables

#### 1. **`CORTEX-CLEANUP.md`** - User Guide

**Location:** `CORTEX/CORTEX-CLEANUP.md` (root level)

**Structure:**
```markdown
# 🗑️ CORTEX Uninstall & Cleanup Guide

## Quick Uninstall (Recommended)

```bash
# Complete removal with brain backup
python scripts/uninstall_cortex.py

# Complete removal WITHOUT backup (⚠️ DESTRUCTIVE)
python scripts/uninstall_cortex.py --no-backup

# Dry run (show what would be removed)
python scripts/uninstall_cortex.py --dry-run
```

## What Gets Removed

### 1. Python Packages
- Core dependencies (pytest, PyYAML, pydantic, etc.)
- Optional dependencies (watchdog, psutil, requests, parso, sqlparse)
- Tree-sitter parsers (if installed)
- Development tools (pytest-cov, etc.)

### 2. Brain Data (with backup prompt)
- `cortex-brain/tier0/` - Governance rules
- `cortex-brain/tier1/` - Working memory (conversations)
- `cortex-brain/tier2/` - Knowledge graph
- `cortex-brain/tier3/` - Development context
- `cortex-brain/documents/` - All generated documents

### 3. Configuration Files
- `cortex.config.json` - Machine-specific settings
- `.cortex/` - User workspace integrations
- `logs/` - All log files

### 4. Virtual Environments
- `.venv/` - Local virtual environment
- `~/.cortex/venv/` - Shared CORTEX environment (if exists)

### 5. Cached Data
- `cortex-brain/backups/` - Old backups
- `__pycache__/` - Python bytecode
- `.pytest_cache/` - Test cache

## Brain Backup Options

### Option 1: Full Backup (Default)
```bash
python scripts/uninstall_cortex.py
# Creates: cortex-brain-backup-YYYYMMDD-HHMMSS.zip
# Location: User's Documents/CORTEX-Backups/
```

### Option 2: Selective Backup
```bash
python scripts/uninstall_cortex.py --backup-only tier1,tier2
# Backs up working memory + knowledge graph only
```

### Option 3: No Backup (⚠️ DESTRUCTIVE)
```bash
python scripts/uninstall_cortex.py --no-backup --confirm
# Permanently deletes all brain data
```

## Manual Cleanup (If Script Fails)

### Windows
```powershell
# 1. Uninstall Python packages
pip uninstall -y -r requirements.txt
pip uninstall -y -r requirements-optional.txt

# 2. Remove CORTEX directory
Remove-Item -Recurse -Force C:\Path\To\CORTEX

# 3. Remove shared environment (if exists)
Remove-Item -Recurse -Force $HOME\.cortex

# 4. Clean Python cache
Remove-Item -Recurse -Force ~\AppData\Local\pip\cache\*cortex*
```

### macOS/Linux
```bash
# 1. Uninstall Python packages
pip uninstall -y -r requirements.txt
pip uninstall -y -r requirements-optional.txt

# 2. Remove CORTEX directory
rm -rf /path/to/CORTEX

# 3. Remove shared environment (if exists)
rm -rf ~/.cortex

# 4. Clean Python cache
rm -rf ~/.cache/pip/*cortex*
```

## Verification

```bash
# Verify packages removed
pip list | grep -E "pytest|pyyaml|pydantic|watchdog|psutil"

# Verify directories removed
ls /path/to/CORTEX  # Should error: No such file
ls ~/.cortex        # Should error: No such file

# Verify no CORTEX processes running
ps aux | grep cortex
```

## Reinstall CORTEX with Preserved Brain

```bash
# 1. Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Run setup
python scripts/install_cortex.py

# 3. Restore brain backup
python scripts/restore_brain_backup.py /path/to/cortex-brain-backup.zip
```

## Troubleshooting

### "Permission Denied" Errors
- Run as administrator (Windows) or with `sudo` (macOS/Linux)
- Close VS Code and any terminals using CORTEX

### "Directory Not Empty" Errors
- Some files may be in use (logs, databases)
- Close all CORTEX-related processes
- Retry uninstall

### Brain Backup Failed
- Check disk space (backup needs ~100-500 MB)
- Verify write permissions to Documents folder
- Try manual backup: `zip -r brain-backup.zip cortex-brain/`
```

#### 2. **`scripts/uninstall_cortex.py`** - Uninstall Script

**Features:**
```python
class CortexUninstaller:
    """
    Safe CORTEX uninstall with brain data preservation
    
    Workflow:
    1. Pre-flight checks (confirm intent, check for running processes)
    2. Brain backup (optional, default=True)
    3. Remove Python packages
    4. Remove directories (CORTEX repo, shared venv, caches)
    5. Remove user workspace integrations
    6. Verification (confirm complete removal)
    7. Restore instructions (if brain backed up)
    """
    
    def __init__(self, backup: bool = True, dry_run: bool = False):
        self.backup = backup
        self.dry_run = dry_run
        self.backup_path = None
        self.removed_items = []
    
    def run(self):
        """Execute complete uninstall workflow"""
        try:
            self.confirm_intent()
            
            if self.backup:
                self.backup_brain_data()
            
            self.uninstall_packages()
            self.remove_directories()
            self.remove_user_integrations()
            self.clean_caches()
            self.verify_removal()
            self.print_summary()
            
        except UninstallError as e:
            self.handle_failure(e)
    
    def confirm_intent(self):
        """Confirm user wants to proceed with uninstall"""
        warnings = [
            "⚠️  This will PERMANENTLY remove CORTEX from your machine",
            "⚠️  All brain data will be DELETED (unless backed up)",
            "⚠️  This action CANNOT be undone"
        ]
        
        for warning in warnings:
            print(warning)
        
        if not self.dry_run:
            response = input("\nType 'UNINSTALL' to proceed: ")
            if response != "UNINSTALL":
                raise UninstallError("Uninstall cancelled by user")
    
    def backup_brain_data(self):
        """Create timestamped backup of brain data"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"cortex-brain-backup-{timestamp}.zip"
        
        # Default to user's Documents folder
        docs_path = Path.home() / "Documents" / "CORTEX-Backups"
        docs_path.mkdir(parents=True, exist_ok=True)
        
        self.backup_path = docs_path / backup_name
        
        print(f"\n📦 Creating brain backup: {self.backup_path}")
        
        if self.dry_run:
            print(f"  [DRY RUN] Would backup cortex-brain/ to {self.backup_path}")
            return
        
        # Create zip archive
        shutil.make_archive(
            str(self.backup_path.with_suffix('')),
            'zip',
            Path.cwd() / 'cortex-brain'
        )
        
        # Verify backup
        if self.backup_path.exists():
            size_mb = self.backup_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Backup created ({size_mb:.1f} MB)")
        else:
            raise UninstallError("Brain backup failed")
    
    def uninstall_packages(self):
        """Remove CORTEX Python packages"""
        print("\n📦 Uninstalling Python packages...")
        
        requirements_files = [
            "requirements.txt",
            "requirements-optional.txt",
            "requirements-dev.txt"
        ]
        
        for req_file in requirements_files:
            req_path = Path.cwd() / req_file
            if not req_path.exists():
                continue
            
            print(f"  Processing {req_file}...")
            
            if self.dry_run:
                print(f"  [DRY RUN] Would uninstall packages from {req_file}")
                continue
            
            subprocess.run(
                ["pip", "uninstall", "-y", "-r", str(req_path)],
                capture_output=True
            )
        
        print("  ✅ Packages uninstalled")
    
    def remove_directories(self):
        """Remove CORTEX directories"""
        print("\n📁 Removing directories...")
        
        directories = [
            Path.cwd(),  # CORTEX repo
            Path.home() / ".cortex",  # Shared environment
            Path.home() / ".cache" / "cortex",  # Cache
        ]
        
        for directory in directories:
            if not directory.exists():
                continue
            
            print(f"  Removing {directory}...")
            
            if self.dry_run:
                print(f"  [DRY RUN] Would remove {directory}")
                continue
            
            shutil.rmtree(directory)
            self.removed_items.append(str(directory))
        
        print("  ✅ Directories removed")
    
    def verify_removal(self):
        """Verify CORTEX completely removed"""
        print("\n✓ Verifying removal...")
        
        # Check directories don't exist
        cortex_dirs = [
            Path.cwd(),
            Path.home() / ".cortex"
        ]
        
        for directory in cortex_dirs:
            if directory.exists():
                print(f"  ⚠️  WARNING: {directory} still exists")
        
        # Check no CORTEX packages installed
        result = subprocess.run(
            ["pip", "list"],
            capture_output=True,
            text=True
        )
        
        cortex_packages = ["pytest", "pyyaml", "watchdog", "psutil"]
        installed = [pkg for pkg in cortex_packages if pkg in result.stdout.lower()]
        
        if installed:
            print(f"  ⚠️  WARNING: Some packages still installed: {', '.join(installed)}")
        else:
            print("  ✅ All CORTEX packages removed")
    
    def print_summary(self):
        """Print uninstall summary"""
        print("\n" + "="*60)
        print("🎉 CORTEX Uninstall Complete")
        print("="*60)
        
        if self.backup_path:
            print(f"\n📦 Brain Backup: {self.backup_path}")
            print("   Use this to restore brain data if you reinstall CORTEX")
        
        print(f"\n🗑️  Removed {len(self.removed_items)} items")
        
        print("\n📖 Next Steps:")
        print("   1. Verify removal: Check directories and packages")
        print("   2. To reinstall: Clone repo and run install_cortex.py")
        if self.backup_path:
            print(f"   3. Restore brain: python scripts/restore_brain_backup.py {self.backup_path}")
```

### Success Metrics

- ✅ Complete removal verified (no CORTEX artifacts remain)
- ✅ Brain data safely backed up (if requested)
- ✅ Python packages uninstalled (pip list confirms)
- ✅ User can reinstall with preserved brain data
- ✅ Works on Windows, macOS, Linux

---

## 📋 Phase 8: Intelligent Upgrade System (Week 2) **NEW**

**Sub-Plan:** CORTEX Safe Auto-Upgrade with Brain Preservation  
**Status:** ✅ 80% Complete (needs integration with new installer)  
**Dependencies:** Phase 1 (installer structure)  
**Risk Level:** 🔴 HIGH - Data loss if backup/restore fails

### Goal

Enable users to safely upgrade CORTEX to the latest version from GitHub while:
- Preserving all brain data (tier0-3, documents)
- Maintaining user configurations
- Applying schema migrations automatically
- Validating upgrade success
- Providing rollback capability

### Current Implementation

**Existing Infrastructure (80% Complete):**
- ✅ `src/operations/modules/upgrade/upgrade_utility.py` (1,331 lines)
- ✅ 7-phase upgrade workflow
- ✅ Brain data backup/restore with verification
- ✅ Git operations (pull, merge, rollback)
- ✅ Schema migrations with tracking
- ✅ Dependency validation
- ✅ Operational readiness checks
- ✅ Version comparison (semantic versioning)
- ✅ What's New feature discovery
- ⚠️ CLI wrapper needed (`scripts/cli_wrappers/upgrade_wrapper.py`)

**cortex-operations.yaml Definition:**
```yaml
upgrade:
  name: Upgrade
  description: Upgrade CORTEX to latest version with brain data backup and dependency updates
  execution_method: cli_wrapper
  context: both
  cli_script: scripts/cli_wrappers/upgrade_wrapper.py
  category: system
  aliases:
    - upgrade cortex
    - upgrade system
  modules:
    - upgrade_utility
  features:
    - Full upgrade workflow (backup → git pull → pip install → migrations → validation)
  notes: 7-phase upgrade with brain backup, git pull, dependency updates, migrations, and validation
```

### Deliverables

#### 1. **`UPGRADE.md`** - User Guide

**Location:** `CORTEX/UPGRADE.md` (root level)

**Structure:**
```markdown
# 🚀 CORTEX Upgrade Guide

**Safe auto-upgrade with brain data preservation**

## Quick Upgrade (Recommended)

```bash
# Upgrade to latest version (auto-backup, auto-migrate)
python scripts/upgrade_cortex.py

# Or use CORTEX command
cortex upgrade
```

**What Happens:**
1. ✅ Check for updates (compares current vs remote version)
2. ✅ Backup brain data (tier0-3, documents, config)
3. ✅ Pull latest code from GitHub (main branch)
4. ✅ Install/update dependencies (pip install -r requirements.txt)
5. ✅ Run schema migrations (database updates)
6. ✅ Validate operational readiness (tests, imports, config)
7. ✅ Generate What's New report (features added since last version)

**Total Time:** ~2-5 minutes (depending on network speed)

## Upgrade Options

### Standard Upgrade (with backup)
```bash
python scripts/upgrade_cortex.py
```

### Skip Backup (⚠️ NOT RECOMMENDED)
```bash
python scripts/upgrade_cortex.py --no-backup
```

### Dry Run (see what would happen)
```bash
python scripts/upgrade_cortex.py --dry-run
```

### Upgrade to Specific Version/Branch
```bash
python scripts/upgrade_cortex.py --branch develop
python scripts/upgrade_cortex.py --version 3.10.0
```

### Check for Updates Only
```bash
python scripts/upgrade_cortex.py --check-only
```

## What Gets Updated

### 1. CORTEX Code
- All `src/` modules
- Scripts (`scripts/`)
- Orchestrators (`src/orchestrators/`)
- Utilities (`src/operations/`)
- Prompts (`.github/prompts/`)

### 2. Dependencies
- Core packages (requirements.txt)
- Optional packages (requirements-optional.txt)
- New packages (auto-detected and installed)

### 3. Brain Schema
- Database migrations (tier1, tier2, tier3)
- Configuration updates (new settings added)
- Template updates (response-templates.yaml)

## What Gets Preserved

### 1. Brain Data (Always Backed Up)
- `cortex-brain/tier0/` - Your governance rules
- `cortex-brain/tier1/` - Your conversation history
- `cortex-brain/tier2/` - Your knowledge graph
- `cortex-brain/tier3/` - Your development context
- `cortex-brain/documents/` - All your generated documents

### 2. Configuration
- `cortex.config.json` - Your machine-specific settings
- User workspace integrations (`.cortex/`)

### 3. Custom Modifications
- User-added brain rules
- Custom templates
- Personal notes/documents

## Upgrade Phases Explained

### Phase 1: Version Check
- Fetches latest version from GitHub (main branch)
- Compares semantic versions (current vs remote)
- Shows available updates

**Output:**
```
Current Version: 3.9.0
Latest Version:  3.10.0
Updates Available: Yes
New Features: 12
Bug Fixes: 8
```

### Phase 2: Brain Backup
- Creates timestamped backup: `cortex-brain-backup-YYYYMMDD-HHMMSS.zip`
- Location: `cortex-brain/backups/`
- Includes: tier0-3, documents, config
- Verification: Checks backup integrity

**Output:**
```
📦 Creating brain backup...
  ✅ tier0/ (12 files, 245 KB)
  ✅ tier1/ (70 conversations, 1.2 MB)
  ✅ tier2/ (knowledge graph, 850 KB)
  ✅ tier3/ (dev context, 340 KB)
  ✅ documents/ (156 files, 4.8 MB)
  ✅ config files (3 files, 12 KB)

Backup Created: cortex-brain/backups/cortex-brain-backup-20251216-143022.zip
Backup Size: 7.4 MB
Verification: PASSED ✅
```

### Phase 3: Git Pull
- Stashes local changes (if any)
- Pulls latest code from remote (main branch)
- Handles merge conflicts (auto-resolves or prompts)

**Output:**
```
🔄 Pulling latest code from GitHub...
  Remote: asifhussain60/CORTEX (main branch)
  Fetching updates...
  ✅ 47 files changed, 1,234 insertions, 567 deletions
  ✅ No merge conflicts
```

### Phase 4: Dependency Updates
- Reads new requirements.txt
- Installs missing packages
- Upgrades existing packages (if version changed)
- Handles Python version compatibility

**Output:**
```
📦 Updating dependencies...
  ✅ pytest 8.4.0 (already satisfied)
  ✅ PyYAML 6.0.2 (already satisfied)
  ⬆️  pydantic 2.0.0 → 2.5.0 (upgrading)
  ➕ tree-sitter 0.22.0 (new package)

Installed: 1 new package
Upgraded: 1 package
```

### Phase 5: Schema Migrations
- Detects database schema changes
- Applies migrations in order (tracked in migrations table)
- Preserves existing data

**Output:**
```
🔄 Running schema migrations...
  ✅ Migration 001: Add planning_phases table
  ✅ Migration 002: Add tdd_state column to plans
  ✅ Migration 003: Create conversation_embeddings index

Applied: 3 migrations
Skipped: 0 (already applied)
```

### Phase 6: Validation
- Tests imports (all modules loadable)
- Validates configuration (no missing keys)
- Checks brain structure (all required directories exist)
- Runs smoke tests (core operations work)

**Output:**
```
✓ Validating upgrade...
  ✅ All Python modules importable
  ✅ Configuration valid (cortex.config.json)
  ✅ Brain structure intact (tier0-3, documents)
  ✅ Database connections working
  ✅ Smoke tests passed (12/12)

Operational Status: ✅ READY
```

### Phase 7: What's New
- Compares current version with previous version
- Discovers new features (operations, orchestrators, utilities)
- Shows bug fixes and improvements

**Output:**
```
🎉 What's New in CORTEX 3.10.0

New Features (12):
  ✅ Code Sanitization Orchestrator (remove company data)
  ✅ Git PATH Auto-Fix (Windows setup improvement)
  ✅ Tree-sitter Multi-Language Support (13 languages)
  ✅ Intelligent Upgrade System (this feature!)
  ... 8 more

Bug Fixes (8):
  ✅ Fixed TDD state machine transitions
  ✅ Resolved planning vacuum edge cases
  ... 6 more

Breaking Changes: None
Migration Required: Yes (schema updates applied)
```

## Rollback (If Upgrade Fails)

### Automatic Rollback
- Upgrade validates at each phase
- If critical error occurs, auto-rollback triggers
- Restores from backup created in Phase 2

### Manual Rollback
```bash
# List available backups
python scripts/upgrade_cortex.py --list-backups

# Restore specific backup
python scripts/restore_brain_backup.py cortex-brain-backup-20251216-143022.zip

# Revert code to previous version
git reset --hard HEAD~1  # If git pull succeeded
```

## Troubleshooting

### "Git Pull Failed" - Merge Conflicts
```bash
# Stash your changes
git stash

# Re-run upgrade
python scripts/upgrade_cortex.py

# Restore your changes after upgrade
git stash pop
```

### "Dependency Installation Failed"
- Check Python version (3.8-3.13 supported)
- Verify internet connection (PyPI access)
- Try manual install: `pip install -r requirements.txt`

### "Migration Failed"
- Backup restored automatically
- Check `logs/upgrade.log` for details
- Report issue: https://github.com/asifhussain60/CORTEX/issues

### "Validation Failed"
- Upgrade continues with warnings
- Check operational readiness report
- Re-run validation: `cortex healthcheck`

## Manual Upgrade (If Script Unavailable)

```bash
# 1. Backup brain data
zip -r cortex-brain-backup.zip cortex-brain/

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations (if any)
python -m src.operations.modules.upgrade.upgrade_utility --migrate

# 5. Validate
python -m src.operations.modules.admin.healthcheck_utility
```

## Upgrade Frequency

**Recommended:** Check for updates weekly
**Critical Updates:** Apply immediately (security fixes, data loss prevention)
**Feature Updates:** Apply when needed (new capabilities, bug fixes)

**Check for updates:**
```bash
python scripts/upgrade_cortex.py --check-only
```

## Version Policy

- **Major Versions (3.x → 4.x):** Breaking changes, manual migration may be required
- **Minor Versions (3.9.x → 3.10.x):** New features, backward compatible
- **Patch Versions (3.9.0 → 3.9.1):** Bug fixes only, always safe to upgrade
```

#### 2. **`scripts/upgrade_cortex.py`** - Upgrade Entry Point

**Features:**
```python
class CortexUpgrader:
    """
    CORTEX Intelligent Upgrade System
    
    Delegates to existing upgrade_utility.py with CLI wrapper functionality
    
    Workflow:
    1. Check for updates (compare versions)
    2. Backup brain data (tier0-3, documents, config)
    3. Git pull (fetch latest code from main branch)
    4. Install dependencies (requirements.txt)
    5. Run migrations (schema updates)
    6. Validate upgrade (operational readiness)
    7. Generate What's New (feature discovery)
    
    Safety Features:
    - Automatic rollback on critical errors
    - Brain backup before any changes
    - Version compatibility checks
    - Idempotent operations (safe to retry)
    """
    
    def __init__(
        self,
        backup: bool = True,
        dry_run: bool = False,
        branch: str = "main",
        version: Optional[str] = None
    ):
        self.backup = backup
        self.dry_run = dry_run
        self.branch = branch
        self.target_version = version
        
        # Delegate to existing upgrade_utility
        from src.operations.modules.upgrade.upgrade_utility import UpgradeUtility
        self.utility = UpgradeUtility()
    
    def run(self):
        """Execute complete upgrade workflow"""
        try:
            # Phase 1: Check for updates
            version_info = self.utility.check_for_updates(branch=self.branch)
            
            if not version_info.has_updates:
                print(f"✅ Already on latest version: {version_info.version}")
                return
            
            print(f"\n📦 Upgrade Available")
            print(f"   Current: {version_info.version}")
            print(f"   Latest:  {version_info.version}")
            print(f"   Branch:  {version_info.branch}")
            
            if self.dry_run:
                print("\n[DRY RUN] Would proceed with upgrade...")
                return
            
            # Confirm with user
            if not self.confirm_upgrade():
                print("Upgrade cancelled by user")
                return
            
            # Phase 2-7: Execute upgrade
            result = self.utility.execute_upgrade(
                target_version=self.target_version,
                create_backup=self.backup
            )
            
            if result.success:
                self.print_success(result)
            else:
                self.print_failure(result)
                
        except Exception as e:
            logger.error(f"Upgrade failed: {e}", exc_info=True)
            print(f"\n❌ Upgrade Failed: {e}")
            print("   Your brain data is safe (backup created)")
            print("   Run rollback if needed: python scripts/restore_brain_backup.py")
    
    def confirm_upgrade(self) -> bool:
        """Confirm user wants to proceed"""
        response = input("\nProceed with upgrade? [Y/n]: ")
        return response.lower() in ['y', 'yes', '']
    
    def print_success(self, result: UpgradeResult):
        """Print upgrade success summary"""
        print("\n" + "="*60)
        print("🎉 CORTEX Upgrade Complete!")
        print("="*60)
        
        print(f"\n✅ Upgraded: {result.from_version} → {result.to_version}")
        print(f"   Duration: {result.duration_seconds:.1f} seconds")
        print(f"   Migrations: {result.migrations_applied}")
        print(f"   New Features: {len(result.whats_new.get('features', []))}")
        
        if result.backup_path:
            print(f"\n📦 Backup: {result.backup_path}")
        
        print("\n📖 Next Steps:")
        print("   1. Review What's New report")
        print("   2. Test your workflows")
        print("   3. Report any issues: github.com/asifhussain60/CORTEX/issues")

# CLI wrapper delegates to existing upgrade_utility
# scripts/cli_wrappers/upgrade_wrapper.py
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upgrade CORTEX to latest version")
    parser.add_argument("--no-backup", action="store_true", help="Skip brain backup (NOT RECOMMENDED)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--branch", default="main", help="Branch to upgrade from")
    parser.add_argument("--version", help="Specific version to upgrade to")
    parser.add_argument("--check-only", action="store_true", help="Check for updates only")
    parser.add_argument("--list-backups", action="store_true", help="List available backups")
    
    args = parser.parse_args()
    
    if args.list_backups:
        from src.operations.modules.upgrade.upgrade_utility import UpgradeUtility
        utility = UpgradeUtility()
        backups = utility.list_backups()
        print(f"\n📦 Available Backups ({len(backups)}):\n")
        for backup in backups:
            print(f"   {backup.backup_id}")
            print(f"   Version: {backup.version}")
            print(f"   Size: {backup.size_bytes / (1024*1024):.1f} MB")
            print(f"   Verified: {'✅' if backup.verified else '❌'}\n")
        sys.exit(0)
    
    if args.check_only:
        from src.operations.modules.upgrade.upgrade_utility import UpgradeUtility
        utility = UpgradeUtility()
        info = utility.check_for_updates(branch=args.branch)
        print(f"\nCurrent: {info.version}")
        print(f"Latest:  {info.version}")
        print(f"Updates: {'Yes ✅' if info.has_updates else 'No'}")
        sys.exit(0)
    
    upgrader = CortexUpgrader(
        backup=not args.no_backup,
        dry_run=args.dry_run,
        branch=args.branch,
        version=args.version
    )
    
    upgrader.run()
```

### Integration with Existing Code

**Required Changes:**
1. ✅ **`upgrade_utility.py`** - Already 80% complete, no changes needed
2. ⚠️ **`scripts/cli_wrappers/upgrade_wrapper.py`** - Create new CLI wrapper (delegates to upgrade_utility)
3. ⚠️ **`scripts/upgrade_cortex.py`** - Create user-friendly entry point
4. ⚠️ **`UPGRADE.md`** - Create comprehensive user guide

### Success Metrics

- ✅ Brain data preserved across all upgrades (100% success rate)
- ✅ Upgrade completes in < 5 minutes (average)
- ✅ Automatic rollback on critical failures
- ✅ Zero manual intervention required
- ✅ Works across Python 3.8-3.13

---

## 📋 Phase 5: Enhanced Documentation (Week 2)

**Sub-Plan:** Comprehensive Setup & Operational Documentation  
**Status:** 📋 Planned  
**Dependencies:** Phase 1, 2.5, 7, 8  
**Risk Level:** 🟢 LOW

### Goal

Create clear, comprehensive, and user-friendly documentation that covers:
- Initial setup (SETUP-CORTEX.md - aligned with new installer)
- Upgrade process (UPGRADE.md)
- Uninstall process (CORTEX-CLEANUP.md)
- Troubleshooting guides
- Platform-specific instructions

### Deliverables

#### 1. **`SETUP-CORTEX.md`** (Updated from existing)

**Changes Required:**
- ✅ Update prerequisites (align with Phase 2 compatibility matrix)
- ✅ Replace old setup instructions with new universal installer
- ✅ Add Git PATH auto-fix documentation (Phase 2.5)
- ✅ Document automatic brain structure creation (Phase 3)
- ✅ Add troubleshooting section (Windows Git issues, Python version)
- ✅ Reference new docs (UPGRADE.md, CORTEX-CLEANUP.md)

**New Structure:**
```markdown
# 🚀 CORTEX Setup Guide

## Prerequisites
- Python 3.8-3.13 (⚠️ Python 3.14 not yet supported)
- Git 2.x (auto-detection on Windows)
- GitHub Copilot (VS Code extension)

## Quick Install

```bash
# One-command setup (handles everything)
python scripts/install_cortex.py
```

**What Happens:**
1. ✅ Git detection + PATH fix (Windows)
2. ✅ Python version validation
3. ✅ Virtual environment creation
4. ✅ Dependency installation (< 20 seconds for core)
5. ✅ Brain structure initialization
6. ✅ Configuration file setup
7. ✅ Post-setup validation

## Installation Options

### Standard Install (Recommended)
```bash
python scripts/install_cortex.py
```

### Developer Install (with dev tools)
```bash
python scripts/install_cortex.py --dev
```

### Minimal Install (core only)
```bash
python scripts/install_cortex.py --minimal
```

## Troubleshooting

[Link to detailed sections on Git PATH, Python versions, etc.]

## Next Steps

- Upgrade: See `UPGRADE.md`
- Uninstall: See `CORTEX-CLEANUP.md`
- Help: Run `cortex help` or visit docs
```

#### 2. **`UPGRADE.md`** - Created in Phase 8

#### 3. **`CORTEX-CLEANUP.md`** - Created in Phase 7

#### 4. **`docs/TROUBLESHOOTING.md`**

**Consolidates all troubleshooting from:**
- SETUP-CORTEX.md (setup issues)
- UPGRADE.md (upgrade issues)
- CORTEX-CLEANUP.md (uninstall issues)
- GIT-SETUP-GUIDE.md (Git PATH issues)

#### 5. **Update Existing Docs**

**Files to Update:**
- ✅ `README.md` - Link to new SETUP-CORTEX.md
- ✅ `.github/copilot-instructions.md` - Reference new setup docs
- ✅ `cortex-brain/documents/implementation-guides/` - Update with new workflows

### Success Metrics

- ✅ All setup documentation aligned with new installer
- ✅ Clear cross-references between docs (setup → upgrade → cleanup)
- ✅ Troubleshooting covers 95% of user issues
- ✅ Platform-specific guidance (Windows/macOS/Linux)

---

## 🎓 References

**Related Documentation:**
- `README.md` - Current setup instructions
- `cortex-brain/documents/implementation-guides/setup-epm-implementation-summary.md`
- `tests/plugins/README.md` - Testing infrastructure
- `SETUP-CORTEX.md` - User setup guide (Phase 5 - to be updated)
- `CORTEX-CLEANUP.md` - Uninstall guide (Phase 7 - new)
- `UPGRADE.md` - Upgrade guide (Phase 8 - new)

**User Reports:**
- `.github/copilot/copilot-chats/cortex-setup-issues.md` - Real user struggles

**Technical Resources:**
- Python venv: https://docs.python.org/3/library/venv.html
- Platform detection: https://docs.python.org/3/library/platform.html
- VS Code settings: https://code.visualstudio.com/docs/python/environments

**Existing Upgrade Infrastructure:**
- `src/operations/modules/upgrade/upgrade_utility.py` - 7-phase upgrade system (80% complete)
- `cortex-operations.yaml` - Upgrade operation definition

---

## 📈 Implementation Timeline

### Week 1: Foundation (Phases 1-3)
**Days 1-2:** Phase 1 - Universal Setup Script
- Create `scripts/install_cortex.py` skeleton
- Implement platform detection
- Implement Python version detection

**Days 3-4:** Phase 2.5 - Git Detection & PATH Fix
- Create `scripts/utils/git_finder.py`
- Create `scripts/utils/path_manager.py`
- Test on Windows with various Git installations

**Day 5:** Phase 3 - Missing Files Auto-Creation
- Create `src/setup/brain_structure_builder.py`
- Test brain structure initialization

**Weekend:** Phase 2 - Python Compatibility Matrix
- Document Python version constraints
- Create fallback requirements files

### Week 2: User Experience (Phases 4-5, 7-8)
**Days 1-2:** Phase 7 - Uninstall & Cleanup
- Create `CORTEX-CLEANUP.md`
- Create `scripts/uninstall_cortex.py`
- Test complete removal workflow

**Days 3-4:** Phase 8 - Intelligent Upgrade
- Create `UPGRADE.md`
- Create `scripts/cli_wrappers/upgrade_wrapper.py`
- Create `scripts/upgrade_cortex.py`
- Test upgrade workflow (requires git commits)

**Day 5:** Phase 5 - Enhanced Documentation
- Update `SETUP-CORTEX.md`
- Create `docs/TROUBLESHOOTING.md`
- Cross-reference all docs

**Weekend:** Phase 4 - User Workspace Integration
- Create `scripts/integrate_cortex.py`
- Document multi-workspace setup

### Week 3: Validation (Phase 6)
**Days 1-3:** Automated Testing
- Create setup integration tests
- Create upgrade integration tests
- Create uninstall integration tests

**Days 4-5:** CI/CD Pipeline
- Create `.github/workflows/test-setup.yml`
- Test across Python 3.8-3.13
- Test across Windows/macOS/Linux

**Weekend:** Final validation and release prep

---

## ✅ Acceptance Criteria

### Phase 1: Universal Setup Script
- [ ] Single command installs CORTEX completely
- [ ] Works on fresh machines (no Git/Python assumptions)
- [ ] Completes in < 90 seconds (excluding downloads)
- [ ] Creates all required directories/files
- [ ] Validates installation success
- [ ] Provides clear error messages
- [ ] Tested on Windows 10/11, macOS 12+, Ubuntu 20.04+

### Phase 2: Python Compatibility Matrix
- [ ] Documents all tested Python versions (3.8-3.13)
- [ ] Warns about Python 3.14 incompatibility
- [ ] Provides fallback package versions
- [ ] Installer rejects unsupported Python versions

### Phase 2.5: Git Detection & PATH Fix
- [ ] Detects Git in 5+ common Windows locations
- [ ] Auto-adds Git to user PATH (registry)
- [ ] Provides session-level fallback
- [ ] Works with GitExtensions, GitHub Desktop, Official Git
- [ ] Clear guidance if auto-fix fails
- [ ] 95%+ success rate on Windows

### Phase 3: Missing Files Auto-Creation
- [ ] Creates all `cortex-brain/` directories
- [ ] Creates all `__init__.py` files
- [ ] Creates configuration files
- [ ] Idempotent (safe to re-run)
- [ ] Validates structure after creation

### Phase 4: User Workspace Integration
- [ ] Copies `.github/prompts/` to user projects
- [ ] Updates Copilot instructions
- [ ] Creates `.cortex/` directory
- [ ] Configures workspace settings
- [ ] Works with multi-folder workspaces

### Phase 5: Enhanced Documentation
- [ ] `SETUP-CORTEX.md` aligned with new installer
- [ ] `UPGRADE.md` complete and tested
- [ ] `CORTEX-CLEANUP.md` complete and tested
- [ ] `docs/TROUBLESHOOTING.md` covers common issues
- [ ] All docs cross-referenced
- [ ] Platform-specific guidance included

### Phase 6: Automated Testing
- [ ] Setup integration tests (fresh install)
- [ ] Setup idempotency tests (re-run)
- [ ] Upgrade integration tests
- [ ] Uninstall integration tests
- [ ] CI/CD pipeline passing on all platforms
- [ ] Tested with Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

### Phase 7: Uninstall & Cleanup
- [ ] Complete CORTEX removal verified
- [ ] Brain data backed up (if requested)
- [ ] Python packages uninstalled
- [ ] Directories removed
- [ ] Verification confirms complete removal
- [ ] Reinstall with brain restore works
- [ ] Tested on Windows/macOS/Linux

### Phase 8: Intelligent Upgrade
- [ ] Version checking works
- [ ] Brain backup before upgrade
- [ ] Git pull succeeds
- [ ] Dependencies updated
- [ ] Migrations applied
- [ ] Validation passes
- [ ] What's New generated
- [ ] Rollback works on failure
- [ ] Tested with actual version upgrades

---

## 🚨 Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| Python 3.14 incompatibility | High | Medium | Version detection + clear error | Phase 2 |
| Git not in PATH (Windows) | High | High | Auto-detection + PATH fix | Phase 2.5 |
| Brain data loss during upgrade | Low | Critical | Mandatory backup + verification | Phase 8 |
| Partial setup failure | Medium | Medium | State tracking + resume | Phase 1 |
| Multi-Python installations | Medium | Low | Smart detection + user selection | Phase 1 |
| Corporate firewall blocks PyPI | Low | High | Document offline install | Phase 5 |
| Uninstall leaves artifacts | Medium | Low | Verification + manual cleanup guide | Phase 7 |
| Upgrade merge conflicts | Medium | Medium | Stash changes + conflict resolution | Phase 8 |

---

## 📊 Success Metrics (Overall Plan)

### User Experience
- ✅ **Setup Time:** < 90 seconds (excluding downloads)
- ✅ **Setup Success Rate:** 95%+ on first attempt
- ✅ **User-Reported Issues:** < 5% of installations
- ✅ **Zero Manual Steps:** Complete automation

### Technical Quality
- ✅ **Platform Coverage:** Windows 10/11, macOS 12+, Ubuntu 20.04+
- ✅ **Python Coverage:** 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- ✅ **Test Coverage:** 90%+ for setup/upgrade/uninstall workflows
- ✅ **Documentation Quality:** All scenarios covered

### Operational
- ✅ **Upgrade Safety:** 100% brain data preservation
- ✅ **Uninstall Completeness:** 100% removal verification
- ✅ **Rollback Success:** 100% on upgrade failures

---

## 📝 Implementation Notes

### Design Principles

1. **Safety First** - Never lose brain data, always backup
2. **Idempotent Operations** - Safe to re-run all workflows
3. **Fail-Safe Defaults** - Continue when possible, clear errors when not
4. **Clear Feedback** - Progress indicators, actionable messages
5. **Platform Agnostic** - Python-first, shell wrappers for convenience

### Technology Choices

**Why Python for All Scripts?**
- ✅ Cross-platform (Windows/macOS/Linux)
- ✅ Already required for CORTEX
- ✅ Rich standard library (subprocess, pathlib, venv, winreg)
- ✅ Easy to test and maintain

**Why Shell Wrappers?**
- ✅ Familiar entry point (`./install.sh`)
- ✅ Can bootstrap Python if needed
- ✅ One-liner installation experience

**Why Auto-Fix Git PATH on Windows?**
- ✅ Most common setup issue (from user reports)
- ✅ Git often installed but not in PATH (GitExtensions, GitHub Desktop)
- ✅ Simple registry update solves permanently
- ✅ Fallback to session-only if registry fails

**Why Leverage Existing Upgrade Utility?**
- ✅ Already 80% complete (1,331 lines, battle-tested)
- ✅ 7-phase workflow well-designed
- ✅ Just needs CLI wrapper + user documentation
- ✅ Avoid reinventing the wheel

### Risk Mitigation

**Risk 1: User has Python 3.14**
- **Mitigation:** Clear error with recommendation to install 3.13
- **Fallback:** Attempt to install with numpy 2.x

**Risk 2: Corporate firewall blocks PyPI**
- **Mitigation:** Document offline installation process
- **Fallback:** Pre-built wheel cache option

**Risk 3: Multiple Python installations**
- **Mitigation:** Smart detection tries all variants
- **Fallback:** Let user specify Python path explicitly

**Risk 4: Git installed but not in PATH (Windows)**
- **Mitigation:** Auto-detect common Git locations + add to PATH
- **Fallback:** Provide manual PATH instructions with detected Git location

**Risk 5: Setup partially completes**
- **Mitigation:** State tracking + resume capability
- **Fallback:** Clear cleanup instructions

**Risk 6: Upgrade fails mid-process**
- **Mitigation:** Brain backup before upgrade + automatic rollback
- **Fallback:** Manual restore from backup instructions

**Risk 7: Uninstall leaves artifacts**
- **Mitigation:** Verification step + comprehensive cleanup
- **Fallback:** Manual cleanup guide with specific paths

---

## 📋 Change Log

### Version 2.0.0 (December 16, 2025)
**Major Updates:**
- ✅ Added master plan status tracker with 9 phases
- ✅ Added Phase 7: Uninstall & Cleanup System (CORTEX-CLEANUP.md)
- ✅ Added Phase 8: Intelligent Upgrade System (UPGRADE.md)
- ✅ Restructured as sub-plan architecture (each phase standalone)
- ✅ Added comprehensive acceptance criteria
- ✅ Added risk register with mitigation strategies
- ✅ Added implementation timeline (3-week schedule)
- ✅ Aligned Phase 5 with new documentation requirements
- ✅ Updated references to include new docs

**Phase 8 Integration:**
- ✅ Documented existing `upgrade_utility.py` (80% complete)
- ✅ Specified CLI wrapper requirements
- ✅ Created UPGRADE.md structure with 7-phase explanation
- ✅ Added rollback procedures

**Phase 7 Integration:**
- ✅ Created CORTEX-CLEANUP.md structure
- ✅ Specified brain backup workflow
- ✅ Added verification and manual cleanup procedures

### Version 1.0.0 (December 16, 2025)
- ✅ Initial plan created with Phases 1-6
- ✅ Added Phase 2.5 for Git PATH auto-fix

---

**Plan Version:** 2.0.0  
**Next Review:** After Week 1 completion (Phases 1-3)  
**Owner:** Asif Hussain  
**Status:** 🚀 Ready for Implementation

**Priority:** Phase 1 → Phase 2.5 → Phase 3 (Week 1 critical path)
