# Platform Switch Plugin

**Version:** 1.0.0  
**Type:** Pre-Execution Plugin  
**Author:** CORTEX Team

## Overview

The Platform Switch Plugin automates the process of switching between development platforms (macOS, Windows, Linux) for CORTEX 2.0. It handles environment configuration, dependency installation, and validation to ensure seamless cross-platform development.

## Features

### Automated Workflow
1. **Git Pull** - Downloads latest code from repository
2. **Environment Configuration** - Sets up platform-specific paths and settings
3. **Dependency Verification** - Installs missing Python packages
4. **Brain Tests** - Runs comprehensive test suite
5. **Tooling Verification** - Validates required development tools

### Supported Platforms
- ✅ macOS (Darwin) - zsh shell, Unix paths
- ✅ Windows - PowerShell, Windows paths
- ✅ Linux - bash shell, Unix paths

## Usage

### Basic Commands

Simply mention your platform switch in natural language:

```
"switched to mac"
"working on mac"
"using mac"

"switched to windows"
"working on windows"
"using windows"

"switched to linux"
"working on linux"
"using linux"
```

### What Happens

When you trigger the plugin, it automatically:

1. **Pulls Latest Code**
   - Detects current Git branch
   - Pulls latest changes from origin
   - Reports number of files changed

2. **Configures Environment**
   - Detects Python installation
   - Verifies/creates virtual environment
   - Sets platform-specific paths
   - Configures path separators

3. **Installs Dependencies**
   - Checks for required packages:
     - pytest, pytest-cov
     - PyYAML
     - numpy, scikit-learn
     - watchdog
     - mkdocs, mkdocs-material
     - black, flake8, mypy
   - Installs any missing packages

4. **Runs Brain Tests**
   - Executes core CORTEX tests:
     - Tier 0: Brain Protection (22 tests)
     - Tier 1: Working Memory (22 tests)
     - Tier 2: Knowledge Graph (25 tests)
     - Tier 3: Context Intelligence (13 tests)
   - Reports pass/fail status

5. **Verifies Tooling**
   - Git availability
   - Python version
   - Platform-specific tools (brew, PowerShell, etc.)

## Output Example

```
🔄 Platform Switch: Configuring for macOS
   Current platform: macOS

📥 Step 1: Pulling latest code from Git...
   Branch: CORTEX-2.0
   ✅ Git pull successful
   Files changed: 454

⚙️  Step 2: Configuring macOS environment...
   Python: Python 3.9.6
   ✅ Virtual environment found: /Users/asif/PROJECTS/CORTEX/.venv
   ✅ Environment configured for macOS

📦 Step 3: Verifying dependencies...
   ✅ pytest: 8.4.2
   ✅ PyYAML: 6.0.3
   ✅ numpy: 1.26.4
   ... (all packages checked)

🧪 Step 4: Running brain tests...
   Running: pytest tests/tier0/ tests/tier1/ tests/tier2/ tests/tier3/
   ✅ All tests passed!
   Tests: 82 passed

🔧 Step 5: Verifying tooling...
   ✅ git: git version 2.39.0
   ✅ python: Python 3.9.6
   ✅ brew: Homebrew 4.0.0

============================================================
🔄 Platform Switch Summary: macOS
============================================================

✅ Git Pull: SUCCESS
   Files changed: 454
✅ Environment Configuration: SUCCESS
✅ Dependency Verification: SUCCESS
✅ Brain Tests: SUCCESS
   Passed: 82, Failed: 0
✅ Tooling Verification: SUCCESS

============================================================
✅ macOS environment is ready!
   All systems operational for CORTEX 2.0
============================================================
```

## Platform-Specific Configuration

### macOS Configuration
- **Path Separator:** `/`
- **Python Command:** `python3`
- **Shell:** `zsh`
- **Line Endings:** LF (`\n`)
- **Home Variable:** `$HOME`
- **Virtual Environment:** `.venv/bin/python`

### Windows Configuration
- **Path Separator:** `\`
- **Python Command:** `python`
- **Shell:** `powershell`
- **Line Endings:** CRLF (`\r\n`)
- **Home Variable:** `%USERPROFILE%`
- **Virtual Environment:** `.venv\Scripts\python.exe`

### Linux Configuration
- **Path Separator:** `/`
- **Python Command:** `python3`
- **Shell:** `bash`
- **Line Endings:** LF (`\n`)
- **Home Variable:** `$HOME`
- **Virtual Environment:** `.venv/bin/python`

## Requirements

### All Platforms
- Git 2.0+
- Python 3.9+
- Virtual environment support
- Internet connection (for pip installs)

### Platform-Specific
- **macOS:** Homebrew (optional but recommended)
- **Windows:** PowerShell 5.0+
- **Linux:** bash shell

## Error Handling

The plugin gracefully handles common errors:

### Git Errors
- Not a git repository → Reports error, suggests `git init`
- Network issues → Timeout after 2 minutes, reports error
- Merge conflicts → Reports error, suggests manual resolution

### Environment Errors
- Python not found → Tests multiple Python commands
- Virtual environment missing → Creates new venv automatically
- Permission issues → Reports error with details

### Dependency Errors
- Package installation fails → Reports specific package and error
- Network timeout → Retries with pip default behavior
- Version conflicts → Reports incompatible packages

### Test Errors
- Test failures → Reports number failed, shows output
- Import errors → Indicates missing dependencies
- Timeout → Aborts after 5 minutes

## Integration

### With CORTEX Entry Point

The plugin integrates with CORTEX's routing system:

```python
# Automatically triggered by cortex.md
if "switched to mac" in user_request:
    result = platform_switch_plugin.execute(user_request)
```

### With Other Plugins

Can be chained with other plugins:

```python
# After platform switch, run cleanup
platform_switch_plugin.execute("switched to mac")
cleanup_plugin.execute("cleanup old files")
```

## Testing

Run plugin tests:

```bash
pytest tests/plugins/test_platform_switch_plugin.py -v
```

### Test Coverage
- ✅ Platform detection
- ✅ Configuration generation
- ✅ Trigger detection
- ✅ Git operations
- ✅ Environment setup
- ✅ Dependency checks
- ✅ Test execution
- ✅ Tool verification
- ✅ Summary generation

## Configuration

The plugin uses project structure detection. No additional configuration needed.

### Optional: Custom Requirements

Edit `requirements.txt` to add custom dependencies:

```txt
# Your custom packages
my-package>=1.0.0
```

The plugin will automatically install them.

## Troubleshooting

### "Virtual environment not found"
**Solution:** Plugin will create it automatically. Ensure Python is accessible.

### "Tests failed with import errors"
**Solution:** Run dependency verification step again. May need to reinstall packages.

### "Git pull failed"
**Solution:** Check network connection and repository access. May need to authenticate.

### "Platform not detected correctly"
**Solution:** Plugin auto-detects from `sys.platform`. If issues, file a bug report.

## Performance

Typical execution times:

- **Git Pull:** 5-30 seconds (depends on changes)
- **Environment Config:** 1-5 seconds
- **Dependency Check:** 5-15 seconds (longer if installing)
- **Brain Tests:** 1-2 seconds (82 tests)
- **Tool Verification:** 1-2 seconds

**Total:** ~15-60 seconds for complete workflow

## Maintenance

### Adding New Dependencies

1. Add to `requirements.txt`
2. Plugin will detect and install automatically
3. No code changes needed

### Adding New Tests

1. Add tests to appropriate tier directory
2. Plugin automatically includes all tier tests
3. Update test count in documentation

### Platform-Specific Features

To add platform-specific behavior:

```python
if config.platform == Platform.MAC:
    # macOS-specific logic
elif config.platform == Platform.WINDOWS:
    # Windows-specific logic
```

## Security

- ✅ No credentials stored
- ✅ Executes only in CORTEX project directory
- ✅ Validates all paths before access
- ✅ Subprocess calls with timeout protection
- ✅ No shell injection vulnerabilities

## Changelog

### Version 1.0.0 (2025-11-09)
- ✅ Initial release
- ✅ Support for macOS, Windows, Linux
- ✅ Automated git pull
- ✅ Environment configuration
- ✅ Dependency installation
- ✅ Brain test execution
- ✅ Tooling verification
- ✅ Comprehensive test suite
- ✅ Error handling and reporting

## Future Enhancements

Planned features:

- [ ] Docker container setup
- [ ] Cloud development environment support (Codespaces, GitPod)
- [ ] Automatic branch switching based on platform
- [ ] Platform-specific optimization settings
- [ ] Performance benchmarking across platforms
- [ ] Automated CI/CD configuration

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review test output for specific errors
3. Check CORTEX logs in `logs/` directory
4. File issue with platform details and error messages

## License

Part of CORTEX 2.0 - All rights reserved.

---

**Last Updated:** November 9, 2025  
**Maintained By:** CORTEX Team
