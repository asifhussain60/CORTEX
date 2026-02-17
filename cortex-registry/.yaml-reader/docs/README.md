# CORTEX Registry YAML Reader

## Overview

A **fully offline, self-contained YAML viewer** designed specifically to run from the `file://` protocol with **zero HTTP dependencies**. This single-page application (SPA) provides a modern glassmorphism UI for loading, exploring, and visualizing YAML files entirely within your browser.

## Key Features

### 🎯 Offline-First Design
- **No HTTP/CDN dependencies** - all libraries vendored locally
- Works perfectly with `file://` protocol
- All processing happens in-browser (no uploads, no servers)
- Zero network requests after initial load

### 📂 File Loading
- **File System Access API** with fallback to `<input type="file">`
- Drag & drop support for multiple YAML files
- Multi-file management with explorer panel
- Recent files tracking (stored in `localStorage`)

### 🎨 Multiple Views
1. **Tree View** - Collapsible hierarchical structure with syntax highlighting
2. **Cards View** - Smart cards for structured data with copy buttons
3. **Graph View** - D3.js force-directed graph for dependencies/relationships
4. **Raw View** - Syntax-highlighted raw YAML with copy functionality

### 🔍 Smart Features
- Global search across loaded content (press `/` to focus)
- Parse error handling with friendly messages
- Graceful clipboard access (works within `file://` limitations)
- Toast notifications for user feedback
- Keyboard shortcuts (Escape, /)

### 📊 Graph Visualization
Automatically detects and visualizes graph structures from YAML:
- `id`/`name` + `dependencies`/`depends_on` relationships
- `steps`/`transitions` flows
- `inputs`/`outputs`/`routes` connections
- Interactive zoom/pan with D3.js

## File Structure

```
cortex-registry/
├── index.html              # Main SPA (self-contained HTML/CSS/JS)
├── vendor/
│   ├── js-yaml.min.js     # YAML parser (v4.1.0)
│   └── d3.min.js          # Graph visualization (v7.8.5)
├── index.html.backup      # Previous version (knowledge hub)
└── README-YAML-READER.md  # This file
```

## Usage

### Opening the Reader

**Method 1: Double-click**
```bash
# Simply double-click index.html in your file manager
# It will open in your default browser using file:// protocol
```

**Method 2: Command Line**
```bash
# macOS
open cortex-registry/index.html

# Linux
xdg-open cortex-registry/index.html

# Windows
start cortex-registry/index.html
```

**Method 3: Direct File URL**
```
file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/index.html
```

### Loading YAML Files

1. **Click "Open File(s)"** button in the header
2. **Drag & drop** YAML files anywhere on the page
3. **Multi-select** to load multiple files at once

### Navigation

- **Explorer Panel**: Switch between "Loaded" and "Recent" tabs
- **View Tabs**: Toggle between Tree/Cards/Graph/Raw views
- **Search**: Press `/` to focus search, `Esc` to clear
- **File Management**: Click `✕` to close individual files, or "Clear All" button

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search box |
| `Esc` | Clear search and blur |

## Browser Compatibility

### Tested Browsers
- ✅ Chrome/Edge (Chromium) 90+
- ✅ Firefox 88+
- ✅ Safari 14+

### Known Limitations (file:// Protocol)

1. **Clipboard Access**: Requires user gesture; fallback uses `document.execCommand('copy')`
2. **localStorage**: May have reduced storage limits in some browsers
3. **File System Access API**: Not available in all browsers (gracefully falls back to `<input type="file">`)

### Graceful Degradation

The app is designed with fallbacks:
- Modern Clipboard API → `document.execCommand` → Toast warning
- File System Access API → Traditional file input
- Always shows clear error messages for browser limitations

## Architecture Details

### No HTTP/Fetch Calls

❌ **What we DON'T do:**
```javascript
// NO fetch() for relative paths (blocked by file:// protocol)
fetch('./data.yaml')  // ❌ Will fail

// NO CDN scripts
<script src="https://cdn.jsdelivr.net/...">  // ❌ Not used
```

✅ **What we DO:**
```javascript
// File API for reading local files
const reader = new FileReader();
reader.readAsText(file);  // ✅ Works in file://

// Local vendor scripts
<script src="./vendor/js-yaml.min.js">  // ✅ Relative paths work
```

### Embedded Dependencies

All JavaScript is either:
1. **Embedded inline** in `<script>` tags
2. **Vendored locally** in `./vendor/` folder

No build step required - just open the HTML file!

### Data Flow

```
User Selects File
    ↓
FileReader API reads file.text()
    ↓
js-yaml parses content
    ↓
Render to selected view (Tree/Cards/Graph/Raw)
    ↓
All state kept in memory
    ↓
Recent files metadata stored in localStorage
```

## Design System

### Glassmorphism Theme
- **Primary**: `#00d4ff` (Cyan)
- **Secondary**: `#7b61ff` (Purple)
- **Success**: `#10b981` (Emerald)
- **Warning**: `#f59e0b` (Amber)
- **Danger**: `#ef4444` (Red)

### Typography
- Main: Segoe UI, Roboto, Helvetica Neue
- Mono: Courier New, Courier

## Development Notes

### Why Self-Contained?

This design choice ensures:
1. **Zero dependencies on HTTP servers** (works offline)
2. **No CORS issues** (no cross-origin requests)
3. **Portable** (copy folder anywhere)
4. **Fast** (no network latency)
5. **Secure** (files never leave your machine)

### Updating Vendor Libraries

To update vendored libraries:

```bash
cd cortex-registry/vendor

# Update js-yaml
curl -sL https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js -o js-yaml.min.js

# Update D3.js
curl -sL https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js -o d3.min.js
```

## Troubleshooting

### Issue: "Clipboard access denied"
**Cause**: Browser security restrictions under `file://`
**Solution**: Click the copy button again (requires user gesture)

### Issue: Graph view shows "No Graph Structure Detected"
**Cause**: YAML doesn't contain recognizable relationship fields
**Solution**: Add fields like `id`, `dependencies`, `depends_on`, etc.

### Issue: Files not loading
**Cause**: Browser blocks file access
**Solution**: Try a different browser or use method 2 (command line open)

### Issue: Styles not loading
**Cause**: CSS is embedded, this shouldn't happen
**Solution**: Check browser console for errors

## Phase Context

This YAML Reader was created as part of **Phase 104: Registry Intelligence Consolidation** to replace the static knowledge hub with a dynamic, offline-capable YAML exploration tool.

### Original Requirement
> Update the YAML Reader SPA design so it runs strictly from the file protocol (file://) with no local server and no HTTP fetches

### Design Constraints Met
✅ Loads YAML only via File API (no fetch)
✅ All dependencies vendored locally
✅ Single self-contained index.html
✅ Explorer panel with Loaded/Recent tabs
✅ Modern glassmorphism UI with Tree/Cards/Graph/Raw views
✅ Explicit browser limitation warnings
✅ Graceful fallbacks for restricted APIs

## License

Part of the CORTEX project. See main repository for license details.

## Support

For issues or questions, refer to the main CORTEX documentation or file an issue in the repository.
