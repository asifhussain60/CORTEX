# CORTEX Documentation Server

Quick-start scripts to run the MkDocs documentation server locally.

## Quick Start

### 🪟 Windows
```bash
docs\serve-docs.bat
```

### 🍎 Mac / 🐧 Linux
```bash
chmod +x docs/serve-docs.sh
./docs/serve-docs.sh
```

## What It Does

The serve scripts automatically:

1. **Kill existing server** — Stop any previous instance running on port 8000
2. **Check dependencies** — Verify mkdocs is installed, install if needed
3. **Start server** — Launch MkDocs development server
4. **Open browser** — Navigate to http://127.0.0.1:8000/
5. **Stream logs** — Display server output in terminal

## Features

### Windows (`serve-docs.bat`)
- ✅ Automatically kills processes on port 8000
- ✅ Detects virtual environment or system Python
- ✅ Installs dependencies if missing
- ✅ Opens browser automatically
- ✅ Colored output with progress steps
- ✅ Shows full error messages

### Mac/Linux (`serve-docs.sh`)
- ✅ Kills existing processes on port 8000
- ✅ Auto-detects Python 3 or virtual environment
- ✅ Installs dependencies if missing
- ✅ Opens browser automatically (with fallback for headless)
- ✅ Colored output with status indicators
- ✅ Works on macOS (Intel & Apple Silicon) and Linux

## Troubleshooting

### Port 8000 Already in Use

**Windows:**
```batch
netstat -aon | findstr ":8000"
taskkill /F /PID <PID>
```

**Mac/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

Then re-run the script.

### Python Not Found

**Make sure you have Python 3.8+ installed:**

- **Windows:** Download from https://python.org
- **Mac:** `brew install python3`
- **Linux:** `apt-get install python3` (Debian/Ubuntu) or equivalent

### mkdocs Module Not Found

The scripts automatically try to install dependencies. If that fails:

```bash
pip install mkdocs mkdocs-material
```

### Browser Won't Open

The documentation will still be available at:
```
http://127.0.0.1:8000/
```

Just open this URL manually in your browser.

## Manual Start (Without Scripts)

If you prefer to start the server manually:

```bash
# Activate virtual environment (optional)
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install dependencies (first time only)
pip install mkdocs mkdocs-material

# Run the server
mkdocs serve --dev-addr 127.0.0.1:8000
```

Then open http://127.0.0.1:8000/ in your browser.

## File Structure

```
docs/
├── serve-docs.bat          # Windows launcher (batch script)
├── serve-docs.sh           # Mac/Linux launcher (bash script)
├── SERVE-DOCS-README.md    # This file
├── mkdocs.yml              # MkDocs configuration
├── 00-README.md            # Documentation index
├── 01-cortex-brain/        # Documentation sections
├── 02-orchestrators/
├── ... (more sections)
└── _build/                 # Generated site (after running server)
```

## Documentation Structure

Once the server is running, you can navigate to:

- **Home:** http://127.0.0.1:8000/ or http://127.0.0.1:8000/INDEX/
- **Orchestrators:** http://127.0.0.1:8000/02-orchestrators/
- **Architecture:** http://127.0.0.1:8000/04-architecture/
- **Getting Started:** http://127.0.0.1:8000/03-getting-started/
- **API Reference:** http://127.0.0.1:8000/06-api-reference/

See the navigation sidebar for complete documentation structure.

## For Developers

### Editing Documentation

1. Start the server: `./serve-docs.sh` (Mac/Linux) or `docs\serve-docs.bat` (Windows)
2. Edit markdown files in the `docs/` folder
3. Reload browser to see changes (usually automatic)
4. Commit changes to git when ready

### Building Static Site

To build a static HTML site (for deployment):

```bash
mkdocs build
```

This creates a `_build/site/` directory with all HTML files.

## Technical Details

### Windows Batch Script (`serve-docs.bat`)

- Language: Batch (CMD.exe)
- Requirements: Windows 7+, Python 3.8+
- Port: 8000
- Browser: Default Windows browser
- Features:
  - Process enumeration using `netstat` and `taskkill`
  - Virtual environment detection
  - Dependency auto-installation
  - Error handling with exit codes

### Bash Script (`serve-docs.sh`)

- Language: Bash 3.2+
- Requirements: macOS 10.9+ or Linux with bash
- Port: 8000
- Browser: 
  - macOS: `open` command
  - Linux: `xdg-open` or `gnome-open`
  - Fallback: Manual URL
- Features:
  - Process enumeration using `lsof`
  - Python 3 auto-detection
  - Virtual environment detection
  - Cross-platform compatibility
  - Colored output
  - Graceful browser fallback

## Performance

- **First run:** ~5-10 seconds (may install dependencies)
- **Subsequent runs:** ~3-5 seconds
- **Server startup:** Usually ready within 2-3 seconds
- **Live reload:** Automatic when files change

## Compatibility

| Platform | Python | Status | Notes |
|----------|--------|--------|-------|
| Windows 10/11 | 3.8+ | ✅ Full | Uses batch script |
| macOS 10.9+ | 3.8+ | ✅ Full | Intel & Apple Silicon |
| macOS 10.9+ (ARM) | 3.9+ | ✅ Full | M1/M2/M3 Macs |
| Ubuntu 18.04+ | 3.8+ | ✅ Full | Uses bash script |
| Debian 10+ | 3.8+ | ✅ Full | Uses bash script |
| CentOS 7+ | 3.8+ | ✅ Full | Uses bash script |
| WSL (Windows) | 3.8+ | ✅ Full | Bash script works |

## Support

For issues with the documentation server:

1. Check [Troubleshooting](#troubleshooting) section above
2. Verify Python 3.8+ is installed: `python --version`
3. Verify mkdocs is installed: `pip list | grep mkdocs`
4. Check port 8000 is available: `netstat -an | grep 8000`
5. Review script output for specific error messages

---

**Version:** 1.0  
**Updated:** 2026-01-22  
**Status:** Production Ready  
