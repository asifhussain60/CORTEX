# CORTEX Documentation Security

## Security Headers Configuration

### Local Development (Python http.server)

**Console Warnings Expected:**
```
⚠️ Content Security Policy directive 'frame-ancestors' is ignored when delivered via a <meta> element
⚠️ X-Frame-Options may only be set via an HTTP header
```

**Why:** Python's `http.server` doesn't support custom HTTP headers. These warnings are **safe to ignore** during local development.

**To Fix (Optional):**
Use a development server that supports headers:
```bash
# Option 1: http-server (npm)
npm install -g http-server
http-server cortex-docs/ -p 8000 --cors

# Option 2: Live Server (VS Code extension)
# Install: "Live Server" by Ritwick Dey
# Right-click index.html → "Open with Live Server"
```

---

### Production Deployment

**Security headers are properly configured via HTTP headers:**

#### Nginx (Recommended)
See: `deployment/nginx.conf` and `deployment/nginx.prod.conf`

Headers configured:
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Referrer-Policy: strict-origin-when-cross-origin
- ✅ Content-Security-Policy (with frame-ancestors)
- ✅ Strict-Transport-Security (HSTS)
- ✅ Permissions-Policy

#### Apache/GitHub Pages
See: `cortex-docs/.htaccess`

**GitHub Pages Note:** 
- Some headers may be overridden by GitHub's infrastructure
- frame-ancestors works via .htaccess if GitHub allows mod_headers
- Consider using Cloudflare or similar CDN for full header control

---

### Security Standards Compliance

**OWASP Top 10:**
- ✅ A1: Injection (CSP prevents inline script attacks)
- ✅ A2: Broken Authentication (N/A - static site)
- ✅ A5: Broken Access Control (X-Frame-Options prevents clickjacking)
- ✅ A6: Security Misconfiguration (Headers properly set)
- ✅ A7: XSS (X-XSS-Protection + CSP)

**NIST Cybersecurity Framework:**
- ✅ PR.AC-5: Network integrity (HTTPS enforcement)
- ✅ PR.DS-5: Data protection (CSP, HSTS)
- ✅ DE.CM-1: Detection (Security headers logged)

---

### Verification

**Test headers in production:**
```bash
curl -I https://your-domain.com | grep -i "x-frame\|content-security\|x-content-type"
```

**Online tools:**
- https://securityheaders.com
- https://observatory.mozilla.org

**Expected Score:** A+ with all headers properly configured

---

### Files Modified

| File | Purpose |
|------|---------|
| `cortex-docs/index.html` | Removed invalid meta tags (frame-ancestors, X-Frame-Options) |
| `deployment/nginx.conf` | Added security headers for dev/staging |
| `deployment/nginx.prod.conf` | Enhanced security headers for production |
| `cortex-docs/.htaccess` | Apache/GitHub Pages security headers |

---

### Troubleshooting

**Issue:** Console warnings in local dev
**Solution:** Ignore (Python http.server limitation) or use http-server/Live Server

**Issue:** Headers not working on GitHub Pages
**Solution:** Use Cloudflare or Netlify with custom header rules

**Issue:** CSP blocks legitimate resources
**Solution:** Update CSP in nginx.conf/nginx.prod.conf to whitelist domains
