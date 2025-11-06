# Building Custom sql.js with FTS5

**Purpose:** Create sql.js WebAssembly build with FTS5 (Full-Text Search 5) support  
**Why:** Standard npm package doesn't include FTS5 extension  
**When:** One-time build, reuse across team  
**Time:** ~4 hours first time, ~30 minutes for rebuilds

---

## Prerequisites

### 1. Emscripten SDK

Download and install Emscripten:

```powershell
# Clone emsdk
cd D:\PROJECTS\KDS
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk

# Install latest
.\emsdk.bat install latest

# Activate
.\emsdk.bat activate latest

# Verify
.\emsdk_env.bat
emcc --version
```

**Expected output:**
```
emcc (Emscripten gcc/clang-like replacement + linker emulating GNU ld) 4.0.19
```

---

## Build Process

### Option A: Automated Build Script (Recommended)

We've created a PowerShell script that handles everything:

```powershell
cd D:\PROJECTS\KDS\sql.js
.\build-fts5.ps1
```

**Output:**
```
🔨 Building Custom sql.js with FTS5 Support
============================================================
✅ Emscripten environment configured
✅ Emscripten version: emcc 4.0.19

📦 Compiling SQLite with FTS5...
Compiling sqlite3.c...
✅ sqlite3.o compiled
Compiling extension-functions.c...
✅ extension-functions.o compiled

🔗 Linking to WebAssembly...
✅ Linked successfully

📦 Creating final build...
✅ dist/sql-wasm.js created (45 KB)
✅ dist/sql-wasm.wasm created (756 KB)

📊 Build Summary:
JavaScript: 44.88 KB
WebAssembly: 755.75 KB
FTS5 Enabled: ✅ YES

✅ Custom sql.js with FTS5 built successfully!
```

### Option B: Manual Build

If you need to customize further:

#### 1. Clone sql.js

```powershell
cd D:\PROJECTS\KDS
git clone https://github.com/sql-js/sql.js.git
cd sql.js
```

#### 2. Enable FTS5 in Makefile

Edit `Makefile`, find `SQLITE_COMPILATION_FLAGS` and add:

```makefile
SQLITE_COMPILATION_FLAGS = \
	-Oz \
	-DSQLITE_OMIT_LOAD_EXTENSION \
	-DSQLITE_DISABLE_LFS \
	-DSQLITE_ENABLE_FTS3 \
	-DSQLITE_ENABLE_FTS3_PARENTHESIS \
	-DSQLITE_ENABLE_FTS5 \              # ← ADD THIS LINE
	-DSQLITE_THREADSAFE=0 \
	-DSQLITE_ENABLE_NORMALIZE
```

#### 3. Download SQLite Amalgamation

```powershell
Invoke-WebRequest -Uri "https://sqlite.org/2025/sqlite-amalgamation-3490100.zip" `
    -OutFile "sqlite-amalgamation.zip"
Expand-Archive -Path "sqlite-amalgamation.zip" -Force
```

#### 4. Compile SQLite

```powershell
# Set up Emscripten environment
..\emsdk\emsdk_env.bat

# Create output directory
mkdir out, dist -Force

# Compile sqlite3.c
emcc -Oz `
    -DSQLITE_OMIT_LOAD_EXTENSION `
    -DSQLITE_DISABLE_LFS `
    -DSQLITE_ENABLE_FTS3 `
    -DSQLITE_ENABLE_FTS3_PARENTHESIS `
    -DSQLITE_ENABLE_FTS5 `
    -DSQLITE_THREADSAFE=0 `
    -DSQLITE_ENABLE_NORMALIZE `
    -c sqlite-amalgamation-3490100/sqlite3.c `
    -o out/sqlite3.o
```

#### 5. Download and Compile Extension Functions

```powershell
# Download
Invoke-WebRequest -Uri "https://www.sqlite.org/contrib/download/extension-functions.c?get=25" `
    -OutFile "extension-functions.c"

# Compile
emcc -Oz `
    -I sqlite-amalgamation-3490100 `
    -DSQLITE_OMIT_LOAD_EXTENSION `
    -DSQLITE_DISABLE_LFS `
    -DSQLITE_ENABLE_FTS3 `
    -DSQLITE_ENABLE_FTS3_PARENTHESIS `
    -DSQLITE_ENABLE_FTS5 `
    -DSQLITE_THREADSAFE=0 `
    -DSQLITE_ENABLE_NORMALIZE `
    -c extension-functions.c `
    -o out/extension-functions.o
```

#### 6. Link to WASM

```powershell
emcc `
    -s RESERVED_FUNCTION_POINTERS=64 `
    -s ALLOW_TABLE_GROWTH=1 `
    -s EXPORTED_FUNCTIONS=@src/exported_functions.json `
    -s EXPORTED_RUNTIME_METHODS=@src/exported_runtime_methods.json `
    -s SINGLE_FILE=0 `
    -s NODEJS_CATCH_EXIT=0 `
    -s NODEJS_CATCH_REJECTION=0 `
    -s STACK_SIZE=5MB `
    -s WASM=1 `
    -s ALLOW_MEMORY_GROWTH=1 `
    -Oz `
    -flto `
    --closure 1 `
    out/sqlite3.o out/extension-functions.o `
    --pre-js src/api.js `
    -o out/tmp-raw.js
```

#### 7. Wrap and Finalize

```powershell
# Combine shell wrapper
$pre = Get-Content "src/shell-pre.js" -Raw
$raw = Get-Content "out/tmp-raw.js" -Raw
$post = Get-Content "src/shell-post.js" -Raw

# Fix WASM filename reference
$raw = $raw -replace 'tmp-raw\.wasm', 'sql-wasm.wasm'

# Write final JS
($pre + $raw + $post) | Set-Content "dist/sql-wasm.js"

# Copy WASM
Copy-Item "out/tmp-raw.wasm" "dist/sql-wasm.wasm" -Force
```

---

## Testing

### Quick FTS5 Test

```javascript
const initSqlJs = require('sql.js');
const SQL = await initSqlJs({
    locateFile: (file) => `./dist/${file}`
});

const db = new SQL.Database();

// Try to create FTS5 table
db.run(`
    CREATE VIRTUAL TABLE test_fts USING fts5(content, tags)
`);

console.log('✅ FTS5 is working!');
```

### Full Benchmark

```powershell
# Copy to CORTEX
Copy-Item dist/sql-wasm.* ../CORTEX/node_modules/sql.js/dist/ -Force

# Run benchmarks
cd ../CORTEX
npm run benchmark
```

**Expected results:**
- Tier 1: <1ms (target: <50ms) ✅
- Tier 2 FTS5: <1ms (target: <100ms) ✅
- All tests passing ✅

---

## Deployment

### For Development (CORTEX tests)

```powershell
Copy-Item D:\PROJECTS\KDS\sql.js\dist\sql-wasm.* `
    D:\PROJECTS\KDS\CORTEX\node_modules\sql.js\dist\ -Force
```

### For Dashboard (Production)

```powershell
# Copy to dashboard public folder
Copy-Item D:\PROJECTS\KDS\sql.js\dist\sql-wasm.* `
    D:\PROJECTS\CORTEX\dashboard\public\ -Force
```

Dashboard code:
```typescript
// dashboard/src/lib/db.ts
import initSqlJs from 'sql.js';

const SQL = await initSqlJs({
    locateFile: (file) => `/sql-wasm.wasm`  // Load from public/
});
```

---

## Version Control

### Option 1: Commit WASM to Git (Recommended)

```powershell
# Add to git
git add sql.js/dist/sql-wasm.*
git commit -m "build: Custom sql.js with FTS5 support"
```

**Pros:**
- Team doesn't need to rebuild
- Consistent builds across team
- Fast setup for new developers

**Cons:**
- 756 KB WASM file in git (acceptable)

### Option 2: Git LFS (If repo size is a concern)

```powershell
git lfs track "*.wasm"
git add .gitattributes
git add sql.js/dist/sql-wasm.wasm
git commit -m "build: Custom sql.js with FTS5 (LFS)"
```

### Option 3: Build Server (Advanced)

- GitHub Actions workflow to build on push
- Upload as artifact
- Download in CI/CD pipeline

---

## Maintenance

### When to Rebuild

1. **SQLite version update** - New SQLite release with bug fixes/features
2. **Emscripten update** - New Emscripten with better optimization
3. **Additional extensions** - Need other SQLite extensions (JSON1, etc.)

### How to Rebuild

```powershell
# Update SQLite version in build script
$SQLITE_VERSION = "3500000"  # Update this

# Clean previous build
Remove-Item out, dist -Recurse -Force

# Rebuild
.\build-fts5.ps1

# Test
cd ..\CORTEX
npm run benchmark

# If passing, commit
git add sql.js/dist/
git commit -m "build: Rebuild sql.js with SQLite $SQLITE_VERSION"
```

---

## Troubleshooting

### Error: "make: command not found"

Use the PowerShell build script instead of Makefile:
```powershell
.\build-fts5.ps1
```

### Error: "emcc: command not found"

Emscripten not activated:
```powershell
cd ..\emsdk
.\emsdk_env.bat
cd ..\sql.js
.\build-fts5.ps1
```

### Error: "no such module: fts5"

FTS5 not enabled in build. Check `Makefile` has `-DSQLITE_ENABLE_FTS5`.

### WASM file too large (>1MB)

Normal for FTS5 build. Optimization flags already applied:
- `-Oz` (size optimization)
- `-flto` (link-time optimization)
- `--closure 1` (Closure Compiler)

756 KB is expected and acceptable.

### Build takes 20+ minutes first time

Normal - Emscripten is compiling system libraries (cached for future builds).
Subsequent builds: ~2-3 minutes.

---

## Performance Validation

After building, verify performance meets targets:

```powershell
cd ..\CORTEX
npm run benchmark
```

**Expected results:**
```
Tier 1 (Working Memory):
  p50: ~0.5ms  (target: <50ms)  ✅
  p95: ~2ms    (target: <75ms)  ✅

Tier 2 (FTS5 Search):
  p50: ~0.3ms  (target: <100ms) ✅
  p95: ~1ms    (target: <150ms) ✅

DECISION: ✅ PROCEED WITH SQL.JS
```

---

## References

- **sql.js repository:** https://github.com/sql-js/sql.js
- **Emscripten docs:** https://emscripten.org/docs/getting_started/downloads.html
- **SQLite FTS5:** https://www.sqlite.org/fts5.html
- **SQLite downloads:** https://www.sqlite.org/download.html

---

**Created:** 2025-11-06  
**Last Updated:** 2025-11-06  
**Build Script:** `sql.js/build-fts5.ps1`  
**Output:** `sql.js/dist/sql-wasm.{js,wasm}`

