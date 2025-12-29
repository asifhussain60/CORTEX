# 🚀 GitHub Pages Deployment Guide

**Quick Command:** `./scripts/publish`

---

## 📋 Simple Publishing

Just run this from the CORTEX root directory:

```bash
./scripts/publish
```

The script will:
1. ✅ Check for uncommitted changes
2. 🔄 Deploy docs to `gh-pages` branch
3. 🚀 Push to GitHub
4. 🌐 Your site goes live!

---

## 🌐 Your Live URLs

After deployment, your documentation will be available at:

- **Main Site:** https://asifhussain60.github.io/CORTEX/
- **Story Viewer:** https://asifhussain60.github.io/CORTEX/story/viewer.html
- **Knowledge Base:** https://asifhussain60.github.io/CORTEX/knowledge/

---

## 🎯 Alternative Methods

### Method 1: Direct Script (No Checks)
```bash
./scripts/deploy_to_ghpages.sh
```

### Method 2: Manual Deployment
```bash
# 1. Ensure all changes are committed
git add -A
git commit -m "Update documentation"
git push origin CORTEX-4.0

# 2. Deploy
./scripts/publish
```

---

## 📝 What Gets Published?

Everything in the `docs/` folder:
- ✅ `docs/index.html` → Homepage
- ✅ `docs/knowledge/` → Knowledge base
- ✅ `docs/story/` → Story viewer
- ✅ `docs/assets/` → CSS, images, etc.

---

## ⚡ Quick Tips

1. **Before Publishing:**
   - Commit your changes to CORTEX-4.0 branch
   - Test locally if needed: `python -m http.server 8000` from `docs/`

2. **After Publishing:**
   - Wait 1-2 minutes for GitHub to build
   - Clear browser cache if changes don't appear

3. **Troubleshooting:**
   - If site doesn't update: Check GitHub Actions tab in your repo
   - If pages are broken: Check file paths are relative (not absolute)

---

## 🔧 Technical Details

- **Source Branch:** CORTEX-4.0
- **Deploy Branch:** gh-pages
- **Deploy Directory:** docs/
- **Site URL:** https://asifhussain60.github.io/CORTEX/

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX
