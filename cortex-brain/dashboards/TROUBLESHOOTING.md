# Dashboard Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** 2025-12-04  
**Author:** Asif Hussain

---

## Common Issues

### 1. Dashboard Shows 404 Error (Most Common)

**Symptoms:**
- Browser shows "Error response - Error code: 404 - File not found"
- Server logs show: `"GET /ui/index.html HTTP/1.1" 404`
- HTTP server is running without errors

**Root Cause:**
Python HTTP server serves files relative to the **working directory**, not the script location. If you start the server from the wrong directory, all paths will return 404.

**Solution:**

```powershell
# 1. Kill any existing servers
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Navigate to the dashboards directory (CRITICAL)
cd d:\PROJECTS\CORTEX\cortex-brain\dashboards

# 3. Start server from correct location
python -m http.server 8090
```

**Verification:**
- Server logs should show `200` status codes: `"GET /ui/index.html HTTP/1.1" 200`
- Check current directory with `pwd` or `Get-Location` - should show `.../cortex-brain/dashboards`

---

### 2. Port Already in Use

**Symptoms:**
- Error: `OSError: [Errno 98] Address already in use` (Linux)
- Error: `OSError: [WinError 10048] Only one usage of each socket address` (Windows)

**Solution:**

```powershell
# Find process using port 8090
netstat -ano | Select-String ':8090' | Select-String 'LISTENING'

# Kill the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force

# Or kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Alternative:** Use a different port:
```bash
python -m http.server 8091
```

---

### 3. Data Not Loading / Empty Dashboard

**Symptoms:**
- Dashboard loads but shows no data
- Browser console errors: `Failed to load resource: /mock/health-data.json`

**Causes:**
1. **Missing data files** - Check `cortex-brain/dashboards/mock/` exists
2. **Wrong source parameter** - URL should include `?source=mock`
3. **CORS issues** - Must use HTTP server, not `file://` protocol

**Solution:**

```powershell
# 1. Verify mock data exists
Get-ChildItem d:\PROJECTS\CORTEX\cortex-brain\dashboards\mock\*.json

# Should show 7 files:
# - health-data.json
# - tech-stack.json
# - security.json
# - architecture.json
# - code-organization.json
# - team-metrics.json
# - vendors.json

# 2. Use correct URL with source parameter
http://localhost:8090/ui/index.html?source=mock
```

---

### 4. JavaScript Module Errors

**Symptoms:**
- Console error: `Failed to resolve module specifier`
- Console error: `Unexpected token '<'` in JavaScript file

**Causes:**
- Trying to load ES6 modules from `file://` protocol
- Missing `type="module"` in script tags
- Incorrect relative paths in imports

**Solution:**
- Always use HTTP server (never open HTML directly)
- Check script tags have `type="module"`
- Verify import paths are relative to served directory

---

### 5. Browser Cache Issues

**Symptoms:**
- Changes to JavaScript/CSS don't appear
- Dashboard shows old data
- Mixed behavior (some updates work, others don't)

**Solution:**

1. **Hard refresh:**
   - Chrome/Edge: `Ctrl+Shift+R` or `Ctrl+F5`
   - Firefox: `Ctrl+Shift+R`
   - Safari: `Cmd+Shift+R`

2. **Clear cache:**
   - Chrome: `Ctrl+Shift+Delete` → Clear browsing data
   - Or use Incognito/Private window

3. **Disable cache during development:**
   - Open DevTools (F12)
   - Network tab → Check "Disable cache"

---

## Quick Diagnostic Checklist

When dashboard doesn't work, check in this order:

- [ ] **Server running?** → Check terminal for "Serving HTTP on..."
- [ ] **Correct directory?** → Should be `cortex-brain/dashboards`, verify with `pwd`
- [ ] **Port available?** → Check for port conflicts with `netstat`
- [ ] **Correct URL?** → Should include `/ui/index.html?source=mock`
- [ ] **Data files exist?** → Check `mock/` directory has 7 JSON files
- [ ] **Browser console clean?** → Press F12, check for errors
- [ ] **HTTP (not file://)?** → URL must start with `http://localhost`

---

## Debug Tools

### Check Server Status
```powershell
# Check if Python HTTP server is running
Get-Process python -ErrorAction SilentlyContinue

# Check what's listening on port 8090
netstat -ano | Select-String ':8090'
```

### Verify File Structure
```powershell
# List dashboard files
Get-ChildItem d:\PROJECTS\CORTEX\cortex-brain\dashboards -Recurse -File | Select-Object FullName

# Check mock data exists
Get-ChildItem d:\PROJECTS\CORTEX\cortex-brain\dashboards\mock\*.json | Select-Object Name, Length
```

### Test Data Loading
```bash
# Test if data endpoint is accessible
curl http://localhost:8090/mock/health-data.json

# Should return JSON data, not 404
```

---

## Prevention Best Practices

1. **Always start server from dashboards directory:**
   ```bash
   cd cortex-brain/dashboards
   python -m http.server 8090
   ```

2. **Use explicit paths:**
   ```bash
   cd d:\PROJECTS\CORTEX\cortex-brain\dashboards
   ```

3. **Verify before opening browser:**
   - Check server logs show "Serving HTTP on..."
   - Verify `pwd` shows correct directory
   - Test with curl or simple file first

4. **Document working setup:**
   - Note which port works
   - Save working directory path
   - Keep troubleshooting log

---

## Getting Help

If issues persist:

1. **Check server logs** - Terminal output shows all requests and errors
2. **Check browser console** - F12 → Console tab for JavaScript errors
3. **Check network tab** - F12 → Network tab for failed requests
4. **Check file permissions** - Ensure files are readable
5. **Try different port** - May be firewall/antivirus blocking
6. **Try different browser** - Isolate browser-specific issues

---

## Known Issues

### Windows Defender / Antivirus
Some antivirus software blocks Python HTTP server. If dashboard won't load:
- Add Python to antivirus exceptions
- Temporarily disable firewall for testing
- Check Windows Security → Firewall logs

### Corporate Networks
Corporate proxies/firewalls may block localhost connections:
- Try `127.0.0.1` instead of `localhost`
- Check if specific ports are blocked
- Use `0.0.0.0` as server address if accessing from network

### WSL Issues
If running in WSL:
- Use Windows Python, not WSL Python
- Access via `localhost`, not WSL IP
- Check WSL network configuration

---

**Last Updated:** 2025-12-04  
**Maintainer:** Asif Hussain  
**Related:** README.md, QUICK-FIX-GUIDE.md
