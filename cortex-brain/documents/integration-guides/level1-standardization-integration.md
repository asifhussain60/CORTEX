# Level 1 View Standardization - Integration Guide

**Version:** 1.0.0  
**Date:** January 5, 2026  
**Author:** Asif Hussain  
**Target:** CORTEX 5.0 Enhanced Version

---

## 📋 Overview

This guide documents the Level 1 View Standardization Orchestrator for integration into CORTEX 5.0 Enhanced. The orchestrator automatically standardizes all Level 1 documentation views based on complexity analysis and visual design principles.

---

## 🎯 What This Orchestrator Does

### Core Functionality

1. **Complexity Analysis** (0-100 scale)
   - Content volume: Word count, section count (0-30 points)
   - Structural depth: HTML nesting levels (0-25 points)
   - Data types: Tables, lists, code blocks, diagrams (0-45 points)

2. **Visual Treatment Decision**
   - High complexity (≥70): Hero-card-grid + diagrams + 3-color palette
   - Medium complexity (40-69): Tetris/card-grid + 2-color palette
   - Low complexity (<40): Simple tiles + 1-color palette

3. **Content Regeneration**
   - Converts bullet lists → card grids
   - Applies glassmorphism 7-color palette
   - Adds hero sections with CORTEX robot
   - Implements tetris-style metadata pills
   - Ensures visual-first design

4. **State Management**
   - Git checkpoints before changes
   - Tracks complexity scores per page
   - Records visual treatments applied
   - Enables rollback on errors

---

## 📁 File Structure

```
CORTEX/
├── scripts/
│   └── orchestrators/
│       └── level1_standardization_orchestrator.py  # Main orchestrator
│
├── cortex-brain/
│   ├── manifests/
│   │   └── orchestrators/
│   │       └── level1-standardization-orchestrator.yaml  # Manifest
│   ├── cache/
│   │   └── html-standardization-state.json  # State tracking
│   └── documents/
│       └── integration-guides/
│           └── level1-standardization-integration.md  # This file
│
└── docs/
    ├── architecture/index.html      # Target pages
    ├── features/index.html
    ├── getting-started/index.html
    ├── knowledge/index.html
    ├── learning-paths/index.html
    ├── lens/index.html
    ├── orchestrators/index.html     # Reference pattern
    ├── security/index.html
    ├── story/index.html
    ├── sts/index.html
    ├── token-optimization/index.html
    └── toolkit-manager/index.html
```

---

## 🔧 Installation Steps

### Step 1: Verify Dependencies

```bash
# Check Python environment
python --version  # Require 3.10+

# Verify required packages
pip list | grep -E "beautifulsoup4|PyYAML"

# Install if missing
pip install beautifulsoup4 pyyaml
```

### Step 2: Copy Files to Target Machine

```bash
# Copy orchestrator script
scp scripts/orchestrators/level1_standardization_orchestrator.py \
    target-machine:/path/to/CORTEX/scripts/orchestrators/

# Copy manifest
scp cortex-brain/manifests/orchestrators/level1-standardization-orchestrator.yaml \
    target-machine:/path/to/CORTEX/cortex-brain/manifests/orchestrators/

# Copy this integration guide
scp cortex-brain/documents/integration-guides/level1-standardization-integration.md \
    target-machine:/path/to/CORTEX/cortex-brain/documents/integration-guides/
```

### Step 3: Verify CSS Infrastructure

Ensure these CSS files exist with required classes:

**docs/assets/css/variables.css** must contain:
```css
/* 7-Color Glassmorphism Palette */
.glass-panel-purple { /* ... */ }
.glass-panel-emerald { /* ... */ }
.glass-panel-amber { /* ... */ }
.glass-panel-cyan { /* ... */ }
.glass-panel-teal { /* ... */ }
.glass-panel-indigo { /* ... */ }
.glass-panel-pink { /* ... */ }

/* Tetris-style card stats */
.card-stats-tetris { /* ... */ }
.card-stats-tetris span { /* ... */ }
.card-stats-tetris span:first-child { /* ... */ }
.card-stats-tetris span:last-child { /* ... */ }
```

**docs/assets/css/main.css** must contain:
```css
/* Glass card displays */
.glass-card-display { /* ... */ }
.glass-card-clickable { /* ... */ }
.card-variant-primary { /* ... */ }
.card-variant-info { /* ... */ }
.card-variant-success { /* ... */ }
.card-variant-warning { /* ... */ }

/* Card descriptions with min-height */
.glass-card-clickable:has(.card-stats-tetris) .card-description {
    min-height: 120px;
}
```

### Step 4: Test Installation

```bash
cd /path/to/CORTEX

# Test dry-run mode (no changes)
python scripts/orchestrators/level1_standardization_orchestrator.py --dry-run

# Expected output:
# ======================================================================
# 🎨 CORTEX Level 1 View Standardization Orchestrator
# ======================================================================
# 
# 📁 Workspace: /path/to/CORTEX
# 📄 Pages to process: 12
# 🧪 Dry run: True
```

---

## 🚀 Usage Instructions

### Basic Usage

```bash
# Change to CORTEX workspace
cd /path/to/CORTEX

# Standardize all Level 1 pages
python scripts/orchestrators/level1_standardization_orchestrator.py

# Preview changes without modifying files
python scripts/orchestrators/level1_standardization_orchestrator.py --dry-run

# Standardize specific page
python scripts/orchestrators/level1_standardization_orchestrator.py --page architecture

# Specify different workspace
python scripts/orchestrators/level1_standardization_orchestrator.py --workspace /custom/path
```

### Advanced Usage

```bash
# Preview single page
python scripts/orchestrators/level1_standardization_orchestrator.py \
    --page orchestrators --dry-run

# Batch standardization with error logging
python scripts/orchestrators/level1_standardization_orchestrator.py \
    2>&1 | tee standardization.log

# Check state after standardization
cat cortex-brain/cache/html-standardization-state.json | python -m json.tool
```

---

## 📊 Understanding Complexity Scores

### Scoring System

| Component | Weight | Calculation |
|-----------|--------|-------------|
| **Content Volume** | 0-30 | `(word_count / 50) + (section_count * 2)` |
| **Structural Depth** | 0-25 | `max_nesting_depth * 3` |
| **Data Types** | 0-45 | `tables*10 + lists*3 + code*5 + images*7` |
| **Total** | 0-100 | Sum of above |

### Visual Treatment Thresholds

| Score Range | Treatment | Layout | Colors | Features |
|-------------|-----------|--------|--------|----------|
| 70-100 | High Visual | hero-card-grid | 3-color | Icons + Diagrams |
| 40-69 | Medium Visual | tetris/card-grid | 2-color | Icons only |
| 0-39 | Simple Visual | tiles | 1-color | Icons only |

### Example Scores

```
orchestrators/index.html:
- Content: 25 (500 words, 3 sections)
- Structure: 18 (6 levels deep)
- Data: 30 (0 tables, 10 lists, 0 code, 0 images)
- Total: 73 → High Visual Treatment

getting-started/index.html:
- Content: 12 (250 words, 1 section)
- Structure: 9 (3 levels deep)
- Data: 15 (0 tables, 5 lists, 0 code, 0 images)
- Total: 36 → Simple Visual Treatment
```

---

## 🎨 Visual Design Patterns

### 7-Color Glassmorphism Palette

The orchestrator rotates through these colors for section backgrounds:

1. **glass-panel-purple** (primary)
2. **glass-panel-emerald** (success/growth)
3. **glass-panel-amber** (warning/emphasis)
4. **glass-panel-cyan** (info/technology)
5. **glass-panel-teal** (harmony/balance)
6. **glass-panel-indigo** (depth/sophistication)
7. **glass-panel-pink** (creativity/innovation)

**Application:**
- Sections rotate through colors deterministically
- Each page gets 1-3 colors based on complexity
- Colors have soft gradients with glass blur effects

### Layout Patterns

**1. Hero Section** (all pages)
```html
<div class="hero-section-wrapper">
    <div class="hero-robot-container">
        <a href="../index.html">
            <img src="../assets/images/CORTEX-logo-200.png" 
                 class="hero-robot-head" />
        </a>
    </div>
    <div class="hero-divider-line"></div>
</div>

<section class="glass-card-display hero-introduction">
    <div class="card-header-centered">
        <i class="card-icon-primary fas fa-icon"></i>
        <h2>Page Title</h2>
    </div>
    <p class="hero-description">Description...</p>
</section>
```

**2. Card Grid** (medium/high complexity)
```html
<section class="glass-card-display glass-panel-purple">
    <h2 class="section-title">
        <i class="fas fa-icon"></i>
        Section Title
    </h2>
    
    <div class="masonry-grid">
        <a href="#" class="glass-card-clickable card-variant-primary">
            <div class="card-header-centered">
                <i class="card-icon-primary fas fa-cube"></i>
                <h3 class="card-title">Card Title</h3>
            </div>
            <p class="card-description">Description...</p>
            
            <!-- Tetris-style metadata -->
            <div class="card-stats card-stats-tetris">
                <span class="stat-primary">
                    <i class="fas fa-icon"></i> Label
                </span>
            </div>
        </a>
    </div>
</section>
```

**3. Simple Tiles** (low complexity)
```html
<section class="glass-card-display glass-panel-emerald">
    <div class="tiles-grid">
        <div class="tile">
            <i class="fas fa-icon"></i>
            <h3>Title</h3>
            <p>Description</p>
        </div>
    </div>
</section>
```

---

## 🔄 State Management

### State File Structure

**Location:** `cortex-brain/cache/html-standardization-state.json`

```json
{
  "version": "2.0",
  "last_updated": "2026-01-05T15:30:00Z",
  "pages": {
    "docs/architecture/index.html": {
      "last_modified": "2026-01-05T15:25:00Z",
      "git_checkpoint": "checkpoint-level1-architecture-20260105-152500",
      "complexity_score": 65,
      "visual_treatment": "card-grid",
      "color_palette": ["glass-panel-purple", "glass-panel-emerald"],
      "status": "standardized",
      "approved_tag": ""
    }
  },
  "global_state": {
    "total_pages_processed": 12,
    "css_registry_version": "2.0",
    "approved_panel_library_version": "1.1.0"
  }
}
```

### Git Checkpoint Tags

Format: `checkpoint-level1-{page_name}-{timestamp}`

Example:
```bash
# Created automatically before modifications
git tag checkpoint-level1-architecture-20260105-152500

# List all checkpoints
git tag | grep checkpoint-level1

# Rollback to checkpoint
git checkout checkpoint-level1-architecture-20260105-152500 -- docs/architecture/index.html
```

---

## 🧪 Testing & Validation

### Pre-Deployment Testing

```bash
# 1. Dry-run on all pages
python scripts/orchestrators/level1_standardization_orchestrator.py --dry-run

# 2. Test single page with real changes
python scripts/orchestrators/level1_standardization_orchestrator.py \
    --page architecture

# 3. Verify in browser
python -m http.server 8000 --directory docs
# Open: http://localhost:8000/architecture/index.html

# 4. Check git diff
git diff docs/architecture/index.html

# 5. Rollback if needed
git checkout HEAD -- docs/architecture/index.html
```

### Validation Checklist

- [ ] All 12 Level 1 pages processed successfully
- [ ] Each page has hero section with robot head
- [ ] Sections use glassmorphism color palette
- [ ] Cards have tetris-style metadata pills
- [ ] No inline styles present
- [ ] All CSS classes exist in registry
- [ ] Git checkpoints created
- [ ] State file updated correctly
- [ ] Pages render correctly in browser
- [ ] Mobile responsive layouts work

---

## 🔗 Integration with CORTEX 5.0

### Master Orchestrator Integration

Add to `src/main.py` routing:

```python
# Level 1 View Standardization patterns
LEVEL1_PATTERNS = [
    r'^standardize\s+level\s*1',
    r'^standardize\s+views',
    r'^apply\s+approved\s+pattern',
    r'^regenerate\s+level\s*1'
]

def route_request(user_input: str):
    if any(re.search(pattern, user_input, re.I) for pattern in LEVEL1_PATTERNS):
        return invoke_level1_standardization(user_input)
```

### Invocation Function

```python
def invoke_level1_standardization(request: str):
    """Invoke Level 1 standardization orchestrator"""
    
    import subprocess
    
    # Parse request for specific page
    page_match = re.search(r'(?:page|view)\s+(\w+)', request, re.I)
    
    cmd = ['python', 'scripts/orchestrators/level1_standardization_orchestrator.py']
    
    if page_match:
        cmd.extend(['--page', page_match.group(1)])
        
    # Check for dry-run
    if 'preview' in request.lower() or 'dry-run' in request.lower():
        cmd.append('--dry-run')
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        'success': result.returncode == 0,
        'output': result.stdout,
        'errors': result.stderr
    }
```

### CORTEX.prompt.md Integration

Add to intent routing table:

```markdown
| Pattern (Regex) | Route To | Type |
|-----------------|----------|------|
| `^(standardize level 1\|standardize views\|apply approved pattern)` | **Level 1 Standardization** | 🛡️ AUTONOMOUS |
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "File not found" errors**
```bash
# Verify workspace structure
ls -la docs/*/index.html

# Check working directory
pwd  # Should be CORTEX root
```

**2. "BeautifulSoup not found"**
```bash
# Install missing dependency
pip install beautifulsoup4
```

**3. Git checkpoint creation fails**
```bash
# Check git repository status
git status

# Ensure you're in a git repo
git rev-parse --git-dir
```

**4. Complexity scores seem wrong**
```bash
# Run with verbose output
python scripts/orchestrators/level1_standardization_orchestrator.py \
    --page architecture --dry-run 2>&1 | tee debug.log

# Check actual HTML content
wc -w docs/architecture/index.html
```

**5. CSS classes not found**
```bash
# Verify CSS files exist
ls -la docs/assets/css/variables.css
ls -la docs/assets/css/main.css

# Check for required classes
grep -n "glass-panel-purple" docs/assets/css/variables.css
grep -n "card-stats-tetris" docs/assets/css/variables.css
```

---

## 📈 Performance Considerations

### Processing Time

| Pages | Time (dry-run) | Time (real) |
|-------|----------------|-------------|
| 1 | ~0.5s | ~1.5s |
| 12 | ~6s | ~18s |

### Memory Usage

- Peak memory: ~150MB (all 12 pages)
- BeautifulSoup parsing: ~10MB per page
- State file: <50KB

### Optimization Tips

```bash
# Process in parallel (advanced)
for page in architecture features getting-started; do
    python scripts/orchestrators/level1_standardization_orchestrator.py \
        --page $page &
done
wait

# Monitor resource usage
time python scripts/orchestrators/level1_standardization_orchestrator.py
```

---

## 🔐 Security Considerations

### Git Safety

- Always creates checkpoints before modifications
- Enables instant rollback on errors
- Preserves original content in git history

### File Permissions

```bash
# Ensure orchestrator is executable
chmod +x scripts/orchestrators/level1_standardization_orchestrator.py

# Verify write permissions
ls -la docs/*/index.html
```

### Backup Strategy

```bash
# Before running on production
git branch backup-before-standardization
git checkout backup-before-standardization
cp -r docs docs.backup

# After running
git diff HEAD backup-before-standardization
```

---

## 📚 Additional Resources

### Related Files

- `scripts/migrate_inline_styles.py` - Inline style removal
- `scripts/cleanup_level1_themes.py` - Theme cleanup
- `scripts/standardize_level1_views.py` - Original standardizer
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/response-templates-v4.yaml` - Response templates

### Documentation

- `.github/prompts/cortex-docs.prompt.md` - HTML modification rules
- `.github/prompts/CORTEX.prompt.md` - Master orchestrator routing
- `cortex-brain/manifests/orchestrators/level1-standardization-orchestrator.yaml` - Full manifest

### Support

For issues or questions:
1. Check this integration guide
2. Review manifest file
3. Inspect state file
4. Check git checkpoints
5. Run with --dry-run first

---

## ✅ Post-Integration Checklist

After deploying to target machine:

- [ ] All dependencies installed
- [ ] Files copied to correct locations
- [ ] CSS infrastructure verified
- [ ] Test run completed (--dry-run)
- [ ] Single page test successful
- [ ] Full batch test successful
- [ ] State file generated correctly
- [ ] Git checkpoints created
- [ ] Browser validation passed
- [ ] Master orchestrator routing added
- [ ] CORTEX.prompt.md updated
- [ ] Documentation reviewed by team

---

**Document Version:** 1.0.0  
**Last Updated:** January 5, 2026  
**Author:** Asif Hussain  
**Copyright:** © 2026 Asif Hussain. All rights reserved.
