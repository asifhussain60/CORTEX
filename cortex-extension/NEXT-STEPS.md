# CORTEX Extension - Next Steps Guide

**Date:** 2025-11-08  
**Phase:** 3.1 → 3.2 Transition  
**Status:** Scaffold Complete, Ready for Testing

---

## 🎯 Immediate Next Steps

### 1. Install Dependencies (5 minutes)

```powershell
cd cortex-extension
npm install
```

**Expected Output:**
```
added 234 packages in 45s
```

### 2. Compile TypeScript (2 minutes)

```powershell
npm run compile
```

**Expected Output:**
```
> cortex@1.0.0 compile
> tsc -p ./
```

**Note:** TypeScript errors will be fixed during compilation as dependencies are resolved.

### 3. Test Extension in Development Host (10 minutes)

**Option A: VS Code UI**
1. Open `cortex-extension` folder in VS Code
2. Press F5 (or Run → Start Debugging)
3. A new VS Code window opens (Extension Development Host)
4. In the new window, open any workspace
5. Open VS Code Chat (Ctrl+Alt+I)
6. Type `@cortex` - it should appear in suggestions
7. Try: `@cortex hello` - should get response

**Option B: Command Line**
```powershell
code cortex-extension
# Then press F5 in VS Code
```

### 4. Verify Python Bridge (5 minutes)

**In Extension Development Host terminal:**
```powershell
# Check if Python bridge started
# Look for console message: "CORTEX Bridge Server started on port 5555"
```

**Test manually:**
```powershell
# In a separate terminal
Invoke-RestMethod -Uri "http://localhost:5555/health" -Method GET
# Should return: {"status": "healthy"}
```

### 5. Test Core Features (15 minutes)

**Test Checklist:**
- [ ] Extension activates (see "CORTEX is now active!" notification)
- [ ] @cortex appears in chat participants
- [ ] Type `@cortex hello` - gets response
- [ ] Type `@cortex /resume` - attempts to resume
- [ ] Type `@cortex /checkpoint` - creates checkpoint
- [ ] Type `@cortex /history` - shows history (empty if first run)
- [ ] Open Token Dashboard (View → CORTEX → Token Dashboard)
- [ ] Dashboard shows metrics (placeholder data initially)
- [ ] Click "Optimize Tokens" button - shows success message
- [ ] Click "Clear Cache" button - shows success message
- [ ] Close/reopen VS Code - resume prompt appears (if configured)

---

## 🐛 Troubleshooting

### Extension won't activate

**Symptom:** No "CORTEX is now active!" message

**Solutions:**
1. Check Output panel (View → Output → select "CORTEX")
2. Verify Python is in PATH: `python --version`
3. Set `cortex.pythonPath` in settings if auto-detection fails
4. Check `cortex.cortexRoot` points to CORTEX installation

### Python bridge fails to start

**Symptom:** Error "Python bridge server failed to start within timeout"

**Solutions:**
1. Verify Python dependencies installed: `pip install -r requirements.txt`
2. Check port 5555 not in use: `netstat -ano | findstr :5555`
3. Run bridge manually to see errors:
   ```powershell
   cd cortex-extension\src\python
   python bridge.py --port 5555
   ```
4. Check CORTEX_ROOT environment variable set

### @cortex not appearing in chat

**Symptom:** Chat participant not registered

**Solutions:**
1. Check extension activated successfully
2. Restart Extension Development Host (Ctrl+Shift+F5)
3. Check VS Code version: Must be ≥1.85.0
4. Try: Developer → Reload Window

### Token dashboard blank

**Symptom:** Dashboard shows no metrics

**Solutions:**
1. Check Python bridge running (port 5555)
2. Open browser console: Help → Toggle Developer Tools
3. Check for CORS errors
4. Click "Refresh" button manually
5. Verify `cortex.tokenDashboard.refreshInterval` setting

### TypeScript compilation errors

**Symptom:** `npm run compile` fails

**Solutions:**
1. Delete `node_modules` folder
2. Delete `package-lock.json`
3. Run `npm install` again
4. Run `npm run compile`
5. Check TypeScript version: `npx tsc --version` (should be 5.3.0)

---

## 📋 Testing Checklist

### Phase 3.2: Chat Participant Registration (15 unit + 5 integration tests)

**Unit Tests to Write:**

1. **BrainBridge Tests (5 tests)**
   - [ ] Test Python process spawning
   - [ ] Test server health check
   - [ ] Test message capture API call
   - [ ] Test conversation retrieval
   - [ ] Test token metrics retrieval

2. **ChatParticipant Tests (5 tests)**
   - [ ] Test message handling
   - [ ] Test command routing (/resume, /checkpoint, /history, /optimize)
   - [ ] Test conversation capture
   - [ ] Test error handling
   - [ ] Test streaming responses

3. **TokenDashboard Tests (5 tests)**
   - [ ] Test webview creation
   - [ ] Test metrics update
   - [ ] Test action buttons (optimize, clear cache, refresh)
   - [ ] Test auto-refresh interval
   - [ ] Test webview message passing

**Integration Tests to Write (5 tests):**

1. [ ] **Full activation flow** - Extension activates → Bridge starts → Chat participant registers
2. [ ] **End-to-end message capture** - User sends message → Captured to Tier 1 → Retrievable
3. [ ] **Resume workflow** - Create conversation → Close → Reopen → Resume
4. [ ] **Token dashboard workflow** - View metrics → Optimize → Verify reduction
5. [ ] **Lifecycle workflow** - Focus → Blur → Checkpoint created

---

## 🎯 Success Criteria (Before Moving to Phase 3.3)

- [ ] All npm dependencies installed
- [ ] TypeScript compiles without errors
- [ ] Extension runs in development host
- [ ] Python bridge starts successfully
- [ ] @cortex chat participant works
- [ ] All 4 commands work (/resume, /checkpoint, /history, /optimize)
- [ ] Token dashboard displays metrics
- [ ] Lifecycle hooks trigger on focus/blur
- [ ] 15 unit tests written and passing
- [ ] 5 integration tests written and passing

---

## 📊 Estimated Timeline

| Task | Estimated Time | Status |
|------|----------------|--------|
| Install dependencies | 5 min | 📋 Pending |
| Compile TypeScript | 2 min | 📋 Pending |
| Test in dev host | 10 min | 📋 Pending |
| Verify Python bridge | 5 min | 📋 Pending |
| Test core features | 15 min | 📋 Pending |
| Write unit tests | 4 hours | 📋 Pending |
| Write integration tests | 2 hours | 📋 Pending |
| Debug and refine | 2 hours | 📋 Pending |
| **Total** | **~8 hours** | 📋 Pending |

---

## 🚀 After Testing Complete

Once all tests pass and features work:

1. Update `IMPLEMENTATION-STATUS-CHECKLIST.md`
   - Mark Phase 3.1 tests complete
   - Update Phase 3 progress: 40% → 55%

2. Create `PHASE-3.2-COMPLETE.md` summary

3. Begin Phase 3.3: Token Dashboard Integration
   - Connect to real token metrics (Phase 1.5)
   - Implement ML optimization UI
   - Add cache explosion warnings

---

**Current Status:** ✅ Phase 3.1 Complete (Scaffold)  
**Next Session:** Install → Compile → Test → Write Tests  
**Estimated Completion:** ~8-12 hours from now

---

**Author:** Asif Hussain  
**Date:** 2025-11-08

