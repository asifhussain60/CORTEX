# Documentation Sitemap Generator

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Standards:** glassmorphism-design-standards-v2.md

## 🎯 Purpose

Automatically generates a comprehensive, glassmorphism-styled sitemap for CORTEX documentation that:
- Scans all documentation directories
- Extracts page titles and descriptions
- Generates a fully responsive HTML sitemap
- Follows glassmorphism design standards v2
- Uses FontAwesome icons (no emojis)
- Provides mobile-first responsive design

## 📋 Features

✅ **Automatic Discovery** - Scans docs directory structure  
✅ **Metadata Extraction** - Pulls titles and descriptions from HTML meta tags  
✅ **Glassmorphism Design** - Modern blur effects and transparency  
✅ **FontAwesome Icons** - Professional icon system  
✅ **Mobile Responsive** - 320px to 1920px+ support  
✅ **Touch-Friendly** - 44px+ tap targets  
✅ **Back to Top** - Smooth scroll navigation  
✅ **Hover Effects** - Interactive page links

## 🚀 Usage

### Basic Usage

```bash
# From CORTEX root
python cortex-toolkit/documentation/generate_sitemap.py
```

### With Custom Docs Path

```bash
python cortex-toolkit/documentation/generate_sitemap.py /path/to/docs
```

### Output

- **File:** `docs/sitemap.html`
- **Size:** ~52KB
- **Format:** Standalone HTML with embedded CSS

## 📊 Sitemap Structure

The generator organizes documentation into sections:

| Section | Icon | Description |
|---------|------|-------------|
| **Features** | `fa-star` | Core capabilities and features |
| **Orchestrators** | `fa-network-wired` | 8 intelligent workflow orchestrators |
| **Governance** | `fa-shield-alt` | SKULL rules and brain protection |
| **Knowledge Library** | `fa-book-open` | Technical knowledge and patterns |
| **Sharpen The Saw** | `fa-tools` | Security and quality practices |
| **The Awakening** | `fa-book-reader` | CORTEX origin story |
| **4.0 Vision** | `fa-rocket` | Future roadmap and plans |

## 🎨 Design Standards

Follows `glassmorphism-design-standards-v2.md`:

- ✅ FontAwesome icons instead of emojis
- ✅ Glassmorphism blur effects (`backdrop-filter: blur(10px)`)
- ✅ Mobile-first responsive design
- ✅ Touch-friendly 44px+ tap targets
- ✅ Smooth transitions and animations
- ✅ Accessible color contrast (WCAG 2.1 AA)
- ✅ Semantic HTML structure

## 📱 Mobile Breakpoints

| Breakpoint | Width | Adjustments |
|------------|-------|-------------|
| **Desktop** | 1200px+ | Full layout |
| **Tablet** | 768-1199px | Stacked sections |
| **Mobile** | 480-767px | Compact layout |
| **Small** | 320-479px | Minimal UI, hide descriptions |

## 🔧 How It Works

### 1. Directory Scanning
```python
docs/
├── features/
│   ├── index.html
│   └── planning-system.html
├── orchestrators/
│   └── ...
└── knowledge/
    └── ...
```

### 2. Metadata Extraction
- Extracts `<title>` tags
- Parses `<meta name="description">` content
- Calculates relative URLs

### 3. HTML Generation
- Creates glassmorphism-styled sections
- Adds FontAwesome icons
- Implements responsive CSS
- Includes back-to-top button

## 📦 Output Example

```html
<div class="sitemap-section">
    <div class="sitemap-section-header">
        <div class="sitemap-section-icon">
            <i class="fas fa-star"></i>
        </div>
        <div class="sitemap-section-info">
            <h3>Features</h3>
            <p>Core capabilities and features</p>
        </div>
    </div>
    <div class="sitemap-pages">
        <a href="features/planning-system.html">
            <div class="sitemap-page-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="sitemap-page-info">
                <h4>Planning System</h4>
                <p>Autonomous planning with 4-folder structure</p>
            </div>
        </a>
    </div>
</div>
```

## 🔄 Regeneration

Run the generator whenever:
- New documentation pages are added
- Page titles or descriptions change
- Documentation structure is reorganized

**Recommended:** Add to CI/CD pipeline for automatic updates.

## 🛠️ Customization

### Add New Sections

Edit the `sections` dictionary in `generate_sitemap.py`:

```python
sections = {
    'new-section': {
        'title': 'New Section',
        'icon': 'fa-custom-icon',
        'description': 'Section description'
    }
}
```

### Modify Styling

The generated HTML includes embedded CSS. To customize:
1. Edit the styles in the `generate_html()` method
2. Regenerate the sitemap

## 📚 Dependencies

- **Python 3.7+**
- **Standard Library** - No external packages required

## ✅ Success Criteria

After running the tool:

1. ✅ `docs/sitemap.html` exists
2. ✅ File size ~50KB
3. ✅ All sections discovered
4. ✅ Page counts match expected numbers
5. ✅ Sitemap loads without errors
6. ✅ Mobile responsive at all breakpoints
7. ✅ FontAwesome icons display correctly

## 🐛 Troubleshooting

### No Pages Found

**Symptom:** "Found 0 sections with 0 total pages"

**Solution:**
```bash
# Check docs path
ls docs/features/
ls docs/orchestrators/

# Run with explicit path
python cortex-toolkit/documentation/generate_sitemap.py D:/PROJECTS/CORTEX/docs
```

### Missing Icons

**Symptom:** Icons don't display

**Solution:**
- Ensure FontAwesome CDN is accessible
- Check browser console for 404 errors
- Verify `main.css` is loading

### Broken Links

**Symptom:** Links return 404

**Solution:**
- Verify file paths are correct
- Check relative path calculation
- Ensure docs structure matches expectations

## 🔗 Related Tools

| Tool | Purpose |
|------|---------|
| `generate_docs_from_code.py` | Generate API documentation |
| `generate_quick_reference.py` | Create quick reference guides |
| `regenerate_prompts.py` | Update AI prompt files |

## 📖 See Also

- `glassmorphism-design-standards-v2.md` - Design standards reference
- `TOOLS-INVENTORY.md` - Complete toolkit catalog
- `docs/sitemap.html` - Generated output

---

**Next Steps:** View the generated sitemap at `http://localhost:8000/sitemap.html`
