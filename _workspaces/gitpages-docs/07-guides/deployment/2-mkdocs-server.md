# MkDocs Development Server

> Auto-generated from cortex-doc.prompt.md on 2026-01-21

## Quick Launch

**Option 1: External Terminal (Recommended)**
```powershell
./scripts/launch-mkdocs.ps1
```

**Option 2: VS Code Terminal**
```bash
mkdocs serve
```

---

## What is MkDocs?

MkDocs generates a **static documentation website** from your Markdown files. It provides:
- 📖 Professional, searchable site (Material Design theme)
- 🔍 Full-text search across all docs
- 📱 Mobile-responsive layout
- 🌙 Dark mode support
- ⚡ Zero-database deployment

---

## Launch Methods

### Option 1: Detached External Terminal (Recommended for Development)

Launches MkDocs in a **separate PowerShell window** that stays open while you continue work in VS Code.

#### Why Use This?
✅ **Non-blocking** – Server runs independently  
✅ **Persistent** – Stays live while you edit docs  
✅ **Live preview** – Changes visible instantly in browser  
✅ **Clean workflow** – Separate terminal from code editing  

#### How to Use
```powershell
# From VS Code terminal (or any terminal)
./scripts/launch-mkdocs.ps1
```

#### What Happens
1. New PowerShell window opens
2. MkDocs builds documentation
3. Server starts at `http://127.0.0.1:8000`
4. You can continue working in VS Code
5. Press **Ctrl+C** in the MkDocs window to stop

#### Output Example
```
INFO    -  Building documentation in '.'
INFO    -  Cleaning site directory
INFO    -  The site is ready at http://127.0.0.1:8000
```

---

### Option 2: VS Code Terminal (Direct)

Runs MkDocs directly in the VS Code terminal.

#### How to Use
```bash
mkdocs serve
```

#### Trade-offs
⚠️ **Blocks terminal** – You can't run other commands while server is active  
✅ **Simpler** – Everything in one window  
✅ **Direct output** – See all logs inline  

#### To Continue Working
You must open a **new terminal** in VS Code (Ctrl+Shift+`) and keep the MkDocs window active in the first terminal.

---

### Option 3: Manual External Terminal

Open PowerShell manually and start MkDocs.

```powershell
# In external PowerShell window
cd d:\PROJECTS\CORTEX
mkdocs serve
```

---

## Configuration

MkDocs reads configuration from `mkdocs.yml`:

```yaml
site_name: CORTEX Documentation
docs_dir: docs              # Source markdown files
site_dir: site              # Generated HTML output
theme:
  name: material            # Material Design theme
  palette:
    - scheme: default       # Light mode
    - scheme: slate         # Dark mode
```

See `mkdocs.yml` for full configuration.

---

## Common Tasks

### View Documentation
```
Open browser: http://127.0.0.1:8000
```

### Edit a Document
```
1. Edit a .md file in docs/
2. Save the file
3. Browser auto-refreshes (live reload)
```

### Build Static Site (No Server)
```bash
mkdocs build
```
Generates `site/` folder with 64+ HTML files (6.94 MB).

### Deploy to GitHub Pages
```bash
mkdocs gh-deploy
```
Deploys `site/` to `gh-pages` branch.

### Stop the Server
```
Press Ctrl+C in the MkDocs terminal
```

---

## Navigation Structure

The documentation is organized into **7 categories**:

1. **Getting Started** – Installation, quick start, first orchestrator
2. **Architecture** – System design, components, patterns
3. **API Reference** – REST, MCP, CLI endpoints
4. **How-To Guides** – Deployment, integration, operations
5. **Reference** – Glossary, FAQ, known issues, compliance
6. **Tutorials** – Hands-on examples
7. **Contributing** – Development, testing, PR process

See `docs/INDEX.md` for complete navigation.

---

## Troubleshooting

### "mkdocs not found"
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
```powershell
# Use different port
mkdocs serve --dev-addr 127.0.0.1:8001
```

### "Changes not showing"
```
1. Verify file saved
2. Check browser cache (Ctrl+Shift+R to hard refresh)
3. Check MkDocs terminal for errors
```

### "Build errors with missing files"
This is expected – some files are archived in `docs/_archive/`. Check the build output; it will list excluded files.

---

## Live Reload

MkDocs includes **live reload** by default:
- ✅ Edit markdown file
- ✅ Save
- ✅ Browser auto-refreshes in ~1 second

If you need to disable live reload:
```bash
mkdocs serve --no-livereload
```

---

## Performance Notes

- **Build time:** ~2-3 seconds (64 HTML files)
- **Site size:** 6.94 MB (very lightweight)
- **Memory:** ~50-100 MB while serving
- **CPU:** Minimal (Python HTTP server)

---

## Next Steps

1. **Launch server** – `./scripts/launch-mkdocs.ps1`
2. **Open browser** – `http://127.0.0.1:8000`
3. **Browse docs** – Start with [INDEX](../INDEX.md)
4. **Edit docs** – Make changes, see them live
5. **Build static** – `mkdocs build` when ready to deploy

---

**See Also:**
- [Development Setup](./2-development-setup.md) – Local environment
- [INDEX](../INDEX.md) – Documentation navigation
- [mkdocs.yml](../../mkdocs.yml) – Configuration
