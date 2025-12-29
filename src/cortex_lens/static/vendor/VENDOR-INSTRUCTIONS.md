# CORTEX Lens v3.0 - Vendor Library Instructions

**Purpose:** Instructions for vendoring D3.js, Three.js, and Chart.js (zero CDN dependencies)

**Libraries to Vendor:**
1. D3.js v7.8.5 (~250KB minified)
2. Three.js r150 (~600KB minified)
3. Chart.js v4.4.0 (~200KB minified)

**Total Size:** ~1.05MB (acceptable for local dashboard)

---

## 📦 Vendoring Steps

### Option A: Manual Download (Recommended)

```powershell
# Create vendor directory
New-Item -Path "src\cortex_lens\static\vendor" -ItemType Directory -Force

# Download D3.js v7.8.5
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js" -OutFile "src\cortex_lens\static\vendor\d3.min.js"

# Download Three.js r150
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.min.js" -OutFile "src\cortex_lens\static\vendor\three.min.js"

# Download OrbitControls for Three.js
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/three@0.150.0/examples/js/controls/OrbitControls.js" -OutFile "src\cortex_lens\static\vendor\OrbitControls.js"

# Download Chart.js v4.4.0
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" -OutFile "src\cortex_lens\static\vendor\chart.umd.min.js"

# Verify downloads
Get-ChildItem "src\cortex_lens\static\vendor" | Select-Object Name, Length
```

### Option B: npm Install + Copy (Alternative)

```powershell
# Install via npm (temporary)
npm install d3@7.8.5 three@0.150.0 chart.js@4.4.0

# Copy to vendor directory
Copy-Item "node_modules\d3\dist\d3.min.js" -Destination "src\cortex_lens\static\vendor\"
Copy-Item "node_modules\three\build\three.min.js" -Destination "src\cortex_lens\static\vendor\"
Copy-Item "node_modules\three\examples\js\controls\OrbitControls.js" -Destination "src\cortex_lens\static\vendor\"
Copy-Item "node_modules\chart.js\dist\chart.umd.min.js" -Destination "src\cortex_lens\static\vendor\"

# Clean up node_modules
Remove-Item -Recurse -Force "node_modules"
Remove-Item "package.json", "package-lock.json"
```

---

## ✅ Verification

After vendoring, verify file sizes:

```powershell
Get-ChildItem "src\cortex_lens\static\vendor\*.js" | ForEach-Object {
    [PSCustomObject]@{
        File = $_.Name
        Size = "{0:N2} KB" -f ($_.Length / 1KB)
    }
}
```

**Expected Output:**
```
File                  Size
----                  ----
d3.min.js             245.32 KB
three.min.js          591.48 KB
OrbitControls.js      19.87 KB
chart.umd.min.js      198.65 KB
```

---

## 📝 Usage in Templates

### D3.js Import

```html
<script src="{{ url_for('static', filename='vendor/d3.min.js') }}"></script>
<script>
  // D3 is now available globally
  const svg = d3.select('body').append('svg');
</script>
```

### Three.js Import

```html
<script src="{{ url_for('static', filename='vendor/three.min.js') }}"></script>
<script src="{{ url_for('static', filename='vendor/OrbitControls.js') }}"></script>
<script>
  // THREE is now available globally
  const scene = new THREE.Scene();
</script>
```

### Chart.js Import

```html
<script src="{{ url_for('static', filename='vendor/chart.umd.min.js') }}"></script>
<script>
  // Chart is now available globally
  const ctx = document.getElementById('myChart').getContext('2d');
  const chart = new Chart(ctx, { ... });
</script>
```

---

## 🔒 Benefits of Vendoring

1. **Zero External Dependencies:** No CDN reliance
2. **Offline Operation:** Works without internet
3. **Version Control:** Exact versions tracked in git
4. **Performance:** No DNS lookups or SSL handshakes
5. **Security:** No third-party script injection risk

---

## 🚀 Next Steps

After vendoring, execute:

```powershell
# Verify vendor files
Test-Path "src\cortex_lens\static\vendor\d3.min.js"
Test-Path "src\cortex_lens\static\vendor\three.min.js"
Test-Path "src\cortex_lens\static\vendor\chart.umd.min.js"

# If all return True, proceed to D3.js template creation
```

**Status:** Manual step required - execute vendoring commands above
