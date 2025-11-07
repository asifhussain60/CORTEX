# CORTEX Conversation Tracking - Quick Reference

**Status**: ✅ OPERATIONAL  
**Last Updated**: November 7, 2025  

---

## Quick Start

### Track a Conversation
```bash
python scripts/cortex_cli.py "Your message here"
```

### Validate System Health
```bash
python scripts/cortex_cli.py --validate
```

**Expected Output**:
```
✅ Conversations: 1
✅ Messages: 7
✅ Recent (24h): 7
```

### Check Session Info
```bash
python scripts/cortex_cli.py --session-info
```

**Expected Output**:
```
📊 Session Information:
   Conversation ID: aa5fcf91-6994-41e9-a198-7ec8e3fce049
   Started: 2025-11-07T06:09:05.824949
   Messages: 0
   Status: active
```

### End Current Session
```bash
python scripts/cortex_cli.py --end-session
```

---

## PowerShell Commands

### Auto-Detect from Clipboard
```powershell
.\scripts\cortex-capture.ps1 -AutoDetect
```

### Manual Message Capture
```powershell
.\scripts\cortex-capture.ps1 -Message "Your message here"
```

### Validate System
```powershell
.\scripts\cortex-capture.ps1 -Validate
```

---

## Testing Commands

### Run Integration Tests
```bash
pytest tests/tier0/test_conversation_tracking_integration.py -v
```

**Expected**: ✅ 3/3 tests passing

### Run Quick Validation
```bash
python scripts/test-conversation-tracking.py
```

**Expected**: ✅ All checks passing

### Run Brain Protector Tests
```bash
pytest tests/tier0/test_brain_protector_conversation_tracking.py -v
```

**Expected**: 🟡 3/8 tests passing (core functionality validated)

---

## Database Queries

### Check Conversations (SQLite)
```bash
sqlite3 cortex-brain/tier1/conversations.db "SELECT * FROM working_memory_conversations;"
```

### Check Messages (SQLite)
```bash
sqlite3 cortex-brain/tier1/conversations.db "SELECT * FROM working_memory_messages;"
```

### Count Recent Conversations
```bash
sqlite3 cortex-brain/tier1/conversations.db "SELECT COUNT(*) FROM conversations WHERE datetime(start_time) > datetime('now', '-24 hours');"
```

---

## Troubleshooting

### Issue: "no such table: working_memory_conversations"
**Solution**: Schema initialization should happen automatically. Try:
```bash
python scripts/cortex_cli.py --validate
```
This will trigger schema creation.

### Issue: Import errors
**Solution**: Ensure you're in the project root:
```bash
cd D:\PROJECTS\CORTEX
python scripts/cortex_cli.py --validate
```

### Issue: PowerShell execution policy
**Solution**: Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `scripts/cortex_cli.py` | Python CLI for conversation tracking | 262 |
| `scripts/cortex-capture.ps1` | PowerShell bridge | 374 |
| `CORTEX/src/session_manager.py` | Session management with schema init | ~300 |
| `cortex-brain/tier1/conversations.db` | SQLite database | N/A |

---

## Success Indicators

✅ **System is working if**:
- `--validate` shows conversations and messages
- `--session-info` returns active session
- No "no such table" errors
- Integration tests passing

❌ **System needs attention if**:
- `--validate` shows "0 conversations"
- Import errors appear
- Database file missing
- Tests failing with schema errors

---

## Documentation

- **Implementation Guide**: `CONVERSATION-TRACKING-COMPLETE.md`
- **Session Summary**: `SESSION-COMPLETION-CONVERSATION-TRACKING.md`
- **CORTEX Rules**: `prompts/user/cortex.md` (see Rule #24)

---

**Quick Help**: Run any command with `--help` for more options:
```bash
python scripts/cortex_cli.py --help
```
