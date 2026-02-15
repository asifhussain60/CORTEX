# CORTEX GitPages Documentation

**HTTP-based documentation site hosted via GitHub Pages**

---

## 🌐 Architecture: HTTP Protocol (Not File://)

This documentation site is designed for **HTTP hosting** (GitHub Pages, local server), NOT for file:// protocol access. The site uses:

- **Relative URLs** for navigation (not file:// paths)
- **CORS-safe assets** (CSS, JS, images served via HTTP)
- **Dynamic content loading** (requires HTTP server)
- **Modern web APIs** (Service Workers, Fetch API)

---

## 🚀 Quick Start (Local Development)

### macOS/Linux

```bash
cd _workspaces/gitpages-docs
./serve-docs.sh
```

### Windows

```cmd
cd _workspaces\gitpages-docs
serve-docs.bat
```

**Server:** http://localhost:8080  
**Auto-browser:** Opens automatically after startup

---

## 📁 Directory Structure

```
_workspaces/gitpages-docs/
├── index.html              # Entry landing page (glassmorphism v4.0)
├── serve-docs.sh           # macOS/Linux HTTP server launcher
├── serve-docs.bat          # Windows HTTP server launcher
├── assets/
│   ├── css/
│   │   ├── main.css                    # Global styles
│   │   ├── index-multipanel.css        # Entry page layout
│   │   ├── generated-classes.css       # Auto-generated utilities
│   │   └── intentional-classes.css     # Custom components
│   ├── images/
│   │   ├── CORTEX-logo-*.png          # Brand assets
│   │   └── Awakening-200.png          # Hero image
│   └── js/
│       └── index.js                    # Entry page interactions
└── README.md               # This file
```

---

## 🎨 Theme: Glassmorphism v4.0

**Colors:**
- **Primary (Cyan):** #00d4ff
- **Secondary (Purple):** #7b61ff
- **Background:** Dark gradient (#0a0a0a → #1a1a1a)
- **Glass Effect:** rgba(255, 255, 255, 0.05) with 10px blur

**Layout Patterns:**
- Multi-column card grids (no long empty rows)
- Responsive breakpoints (1200px, 768px, 480px)
- Touch-optimized targets (44px minimum)
- Mobile-first CSS

---

## 🏗️ Content Generation Pipeline

**Two-Agent Pattern:**

1. **cortex-documentation-architect.md** (.github/agents/core/)
   - Extracts content from cortex-registry
   - Applies Diátaxis framework (Tutorial/How-To/Reference/Explanation)
   - Generates role narratives (Business/Product/Engineering)
   - Outputs: content.json

2. **cortex-gitpages-builder.md** (.github/agents/core/)
   - Loads content.json
   - Applies glassmorphism templates
   - Generates 3 role landing pages + 15 child pages
   - Embeds D3.js visualizations
   - Optimizes assets (minify CSS/JS)
   - Outputs: docs/ (GitHub Pages ready)

---

## 🌍 GitHub Pages Deployment

**Branch:** `CORTEX`  
**Path:** `/_workspaces/gitpages-docs/`  
**URL:** https://asifhussain60.github.io/CORTEX/

### Deployment Steps

1. **Build site** (via cortex-gitpages-builder agent)
2. **Commit changes** to `_workspaces/gitpages-docs/`
3. **Push to origin/CORTEX**
4. **GitHub Actions** auto-deploys to GitHub Pages

### GitHub Pages Settings

```yaml
# Settings → Pages
Source: Deploy from a branch
Branch: CORTEX
Folder: /_workspaces/gitpages-docs
```

---

## 🔧 Local Server Features

**serve-docs.sh / serve-docs.bat:**

✅ **Auto-kill** existing server on port 8080  
✅ **Python 3 check** (http.server module)  
✅ **HTTP server** on localhost:8080  
✅ **Auto-browser** launch  
✅ **Ctrl+C handler** for graceful shutdown

**Performance:**
- Static file serving (~1ms response)
- No build step required (pre-built HTML)
- Hot-reload not needed (refresh browser)

---

## 📊 Content Architecture

### Entry Landing (index.html)

- **Hero Section:** CORTEX branding + tagline
- **Feature Showcase:** 24 orchestrators, 15+ MCP tools, 4-tier governance
- **Stats Panel:** Real-time metrics (tests passing, coverage, uptime)
- **Role Gateway:** 3 persona cards (Business/Product/Engineering)

### Role Landing Pages (To Be Generated)

- **Business Leaders:** business/index.html
- **Product Owners:** product/index.html  
- **Software Engineers:** engineering/index.html

Each role page includes:
- Sidebar navigation (5 child pages)
- Multi-column content area
- Role-specific guidance
- D3.js visualizations

### Child Pages (5 per role = 15 total)

**Business:**
- Strategy alignment, ROI tracking, Risk management, Compliance, Team productivity

**Product:**
- Feature planning, Roadmap tracking, Quality gates, User stories, Release management

**Engineering:**
- TDD workflow, MCP tools, Orchestrators, Testing, CI/CD

---

## 🛡️ Security & Performance

**Headers (via GitHub Pages):**
```
Content-Security-Policy: default-src 'self'; script-src 'self' cdnjs.cloudflare.com
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

**Performance Optimizations:**
- Resource preloading (fonts, hero image)
- Lazy loading (below-the-fold images)
- Minified CSS/JS (production)
- GZIP compression (GitHub Pages automatic)
- CDN delivery (Fastly via GitHub Pages)

**Accessibility:**
- ARIA landmarks
- Semantic HTML5
- Keyboard navigation
- Screen reader tested
- WCAG 2.1 AA compliant

---

## 🔗 Cross-Platform Compatibility

| Platform | Launcher | Python | Browser |
|----------|----------|--------|---------|
| macOS | serve-docs.sh | python3 | Safari/Chrome |
| Linux | serve-docs.sh | python3 | Firefox/Chrome |
| Windows | serve-docs.bat | python | Edge/Chrome |

**Tested Browsers:**
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+

---

## 📚 Related Documentation

- `.github/agents/core/cortex-documentation-architect.md` - Content generation agent
- `.github/agents/core/cortex-gitpages-builder.md` - HTML generation agent
- `cortex-registry/_cortex-docs/` - Source content
- `.github/prompts/cortex-doc.prompt.md` - Documentation standards

---

## 🚨 Important Notes

**DO NOT:**
- ❌ Open index.html via file:// protocol (breaks navigation)
- ❌ Modify index.html directly (regenerate via cortex-gitpages-builder)
- ❌ Use absolute file paths (use relative URLs)
- ❌ Commit node_modules or build artifacts

**DO:**
- ✅ Use HTTP server for local development
- ✅ Test on multiple browsers before deploying
- ✅ Run link checker before pushing
- ✅ Validate HTML5 (nu validator)
- ✅ Check mobile responsiveness (viewport meta tag)

---

**Last Updated:** 2026-02-15  
**Maintainer:** Asif Hussain  
**Authority:** cortex-gitpages-builder.md v1.0
