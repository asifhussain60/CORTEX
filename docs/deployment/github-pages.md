# Hosting MkDocs on GitHub Pages

## Overview

GitHub Pages is a free static site hosting service that works perfectly with MkDocs. Your documentation site will be hosted at `https://[username].github.io/[repo-name]/`.

For this repository: `https://asifhussain60.github.io/CORTEX/`

---

## Prerequisites

- ✅ GitHub repository (already exists: `asifhussain60/CORTEX`)
- ✅ MkDocs installed and working locally
- ✅ Documentation in `docs/` folder
- ✅ `mkdocs.yml` configuration file

---

## Deployment Methods

### Method 1: Manual Deployment (Recommended for First Time)

**Step 1: Build your documentation**
```powershell
# From repository root
mkdocs build --clean
```

This creates a `site/` folder with all HTML files.

**Step 2: Deploy to GitHub Pages**
```powershell
mkdocs gh-deploy
```

This command:
- Builds the documentation
- Creates/updates a `gh-pages` branch
- Pushes the site to GitHub
- Your site goes live at `https://asifhussain60.github.io/CORTEX/`

**Step 3: Enable GitHub Pages (First time only)**
1. Go to your GitHub repository: `https://github.com/asifhussain60/CORTEX`
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**, select:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
5. Click **Save**
6. Wait 1-2 minutes for deployment

---

### Method 2: Automated GitHub Actions (Best for Teams)

Create a GitHub Actions workflow that automatically deploys when you push to the main branch.

**Step 1: Create workflow file**

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy MkDocs

on:
  push:
    branches:
      - cortex-migration  # or 'main' depending on your default branch
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch all history for proper git info

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.x

      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install mkdocs-mermaid2-plugin

      - name: Build and deploy
        run: mkdocs gh-deploy --force
```

**Step 2: Commit and push**
```powershell
git add .github/workflows/deploy-docs.yml
git commit -m "ci: Add automated MkDocs deployment"
git push
```

**Step 3: Verify deployment**
- Go to **Actions** tab in GitHub
- Watch the workflow run
- Once complete, visit `https://asifhussain60.github.io/CORTEX/`

---

## Configuration Updates

### Update `mkdocs.yml` for GitHub Pages

Make sure your `mkdocs.yml` has the correct site URL:

```yaml
site_name: CORTEX Documentation
site_url: https://asifhussain60.github.io/CORTEX/
repo_url: https://github.com/asifhussain60/CORTEX
```

If deploying to a custom domain, change `site_url` accordingly.

---

## Custom Domain (Optional)

If you own a custom domain (e.g., `docs.cortex.ai`):

**Step 1: Configure DNS**

Add these DNS records at your domain registrar:

```
Type: CNAME
Name: docs (or subdomain of your choice)
Value: asifhussain60.github.io
```

**Step 2: Configure GitHub Pages**

1. Go to **Settings → Pages**
2. Under **Custom domain**, enter: `docs.cortex.ai`
3. Check **Enforce HTTPS**

**Step 3: Update `mkdocs.yml`**

```yaml
site_url: https://docs.cortex.ai/
```

**Step 4: Create CNAME file**

Create `docs/CNAME` with your domain:
```
docs.cortex.ai
```

---

## Troubleshooting

### Site not updating?

**Clear browser cache:**
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

**Force rebuild:**
```powershell
mkdocs gh-deploy --force
```

### 404 errors on page refresh?

This happens with single-page apps. GitHub Pages doesn't support this by default. Use these solutions:

1. **Use hash-based URLs** (not recommended for docs)
2. **404.html redirect** - Create `docs/404.html`:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <meta http-equiv="refresh" content="0;url=/">
   </head>
   </html>
   ```

### CSS/JS not loading?

Check `site_url` in `mkdocs.yml` - it must match your actual URL:
```yaml
site_url: https://asifhussain60.github.io/CORTEX/
```

### Build fails in GitHub Actions?

**Check Python version:**
```yaml
python-version: 3.x  # Use 3.x, not specific version
```

**Install all required plugins:**
```yaml
- name: Install dependencies
  run: |
    pip install mkdocs-material
    pip install mkdocs-mermaid2-plugin
    # Add any other plugins from your mkdocs.yml
```

---

## What Your GitHub Pages Site Looks Like

Once deployed, your site structure will be:

```
https://asifhussain60.github.io/CORTEX/
│
├── index.html (Homepage - from docs/index.md)
├── story/
│   └── the-awakening-of-cortex.html
├── getting-started/
│   ├── quick-start.html
│   ├── installation.html
│   └── configuration.html
├── architecture/
│   ├── overview.html
│   ├── three-tier-brain.html
│   └── ...
├── api/
│   └── ...
└── assets/
    ├── stylesheets/
    │   └── extra.css (your custom styles)
    ├── javascripts/
    └── images/
```

---

## Workflow Best Practices

### Local Development
```powershell
# Preview locally (auto-reload on changes)
mkdocs serve

# Open browser to http://127.0.0.1:8000/
```

### Making Changes
```powershell
# 1. Edit documentation in docs/
# 2. Preview locally
mkdocs serve

# 3. When satisfied, commit and push
git add docs/
git commit -m "docs: Update documentation"
git push

# 4. Deploy to GitHub Pages
mkdocs gh-deploy

# Or let GitHub Actions do it automatically
```

---

## Monitoring Your Site

### GitHub Pages Dashboard

Go to **Settings → Pages** to see:
- ✅ Site status (published/building/failed)
- 🔗 Live URL
- 📊 Visitor statistics (if enabled)
- 🔒 HTTPS enforcement status

### GitHub Actions Logs

Go to **Actions** tab to see:
- Build history
- Deployment logs
- Error messages
- Build duration

---

## Site Performance

GitHub Pages provides:
- ✅ **Free hosting** (unlimited public repositories)
- ✅ **CDN distribution** (fast worldwide)
- ✅ **HTTPS by default** (secure connections)
- ✅ **100GB monthly bandwidth** (soft limit)
- ✅ **1GB site size limit** (more than enough for docs)

---

## Next Steps

### After First Deployment

1. **Test all links** - Click through every page
2. **Check mobile view** - Responsive design validation
3. **Verify search works** - Try searching for content
4. **Test navigation** - Ensure sidebar/tabs work
5. **Share the URL** - Send to team/users

### Regular Maintenance

- 📝 Keep documentation updated with code changes
- 🔄 Redeploy after major updates: `mkdocs gh-deploy`
- 📊 Monitor GitHub Actions for build failures
- 🔗 Check for broken links periodically

---

## Additional Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions for MkDocs](https://github.com/marketplace/actions/deploy-mkdocs)

---

## Quick Reference Commands

```powershell
# Preview locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy

# Force redeploy
mkdocs gh-deploy --force

# Clean build
mkdocs build --clean
```

Your documentation is now live and accessible to the world! 🚀
