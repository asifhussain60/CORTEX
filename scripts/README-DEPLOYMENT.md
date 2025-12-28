# GitHub Pages Deployment Guide

**Quick Reference:** Deploy your localhost:8000 site to GitHub Pages

---

## 🚀 One-Command Deployment

```bash
./scripts/deploy_to_ghpages.sh
```

That's it! Your site will be live at:
- **Story Viewer:** https://asifhussain60.github.io/CORTEX/story/viewer.html
- **Main Site:** https://asifhussain60.github.io/CORTEX/

---

## 📋 What This Script Does

1. **Switches to gh-pages branch** (creates if doesn't exist)
2. **Cleans existing files** (keeps .git directory)
3. **Copies docs/ directory** to branch root
4. **Creates .nojekyll file** (prevents Jekyll processing)
5. **Commits changes** (bypasses pre-commit hooks)
6. **Force-pushes to origin/gh-pages**
7. **Returns to your original branch**

---

## ⚡ When to Use

- After making changes to `docs/` directory
- When you've tested locally on `http://localhost:8000`
- To publish story viewer updates
- To deploy documentation changes

---

## 🔍 Pre-Deployment Checklist

✅ Test locally first:
```bash
python3 scripts/serve_docs.py 8000
# Visit http://localhost:8000/story/viewer.html
```

✅ Commit your changes to CORTEX-4.0:
```bash
git add docs/
git commit -m "Update story viewer"
git push origin CORTEX-4.0
```

✅ Then deploy:
```bash
./scripts/deploy_to_ghpages.sh
```

---

## 📊 Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Script execution | ~10 seconds | You'll see output |
| GitHub processing | 30-60 seconds | Check Actions tab |
| CDN propagation | 1-2 minutes | Changes go live |
| **Total** | **~3 minutes** | Fully deployed |

---

## 🔗 Verify Deployment

1. **Check Actions:** https://github.com/asifhussain60/CORTEX/actions
2. **View Deployments:** https://github.com/asifhussain60/CORTEX/deployments
3. **Test Live Site:** https://asifhussain60.github.io/CORTEX/story/viewer.html

**Force refresh in browser:**
- Chrome/Firefox: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Safari: `Cmd+Option+R`

---

## 🛠️ Troubleshooting

### "Not a git repository"
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
./scripts/deploy_to_ghpages.sh
```

### "Failed to push"
Check your git credentials:
```bash
git config --list | grep credential
git push origin gh-pages --force  # Try manually
```

### "No changes to deploy"
This means gh-pages already has your latest docs/:
```bash
# Make a change first, then deploy
echo "update" >> docs/.deployment-trigger
./scripts/deploy_to_ghpages.sh
```

### Changes not visible on live site
1. Wait 3 minutes for full propagation
2. Hard refresh browser (Cmd+Shift+R)
3. Check browser DevTools Network tab for 304 (cached) responses
4. Try incognito/private window

---

## 📝 Recent Deployments

**Latest:** 2025-12-28
- ✅ Story viewer responsive CSS
- ✅ Mobile burger menu (z-index: 1003)
- ✅ Sticky breadcrumb navigation
- ✅ Full-width images on mobile
- ✅ 201 files, 48K+ lines deployed

---

## 🎯 Related Scripts

| Script | Purpose |
|--------|---------|
| `serve_docs.py` | Local development server (port 8000) |
| `deploy_to_ghpages.sh` | Deploy to GitHub Pages |
| `launch_docs.sh` | Launch local docs with browser |

---

## 📚 Additional Resources

- **GitHub Pages Docs:** https://docs.github.com/en/pages
- **Custom Domains:** https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- **GitHub Actions:** https://docs.github.com/en/actions

---

**Last Updated:** 2025-12-28  
**Maintainer:** Asif Hussain
