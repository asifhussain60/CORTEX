# Tier 1 Auto-Recording Quick Reference
**Version:** 7.0  
**Status:** ✅ Production Ready  
**Created:** 2025-11-05

---

## 🎯 Purpose

Automatic conversation tracking for Tier 1 (BRAIN Working Memory) using a three-layer system that eliminates manual recording burden and ensures comprehensive conversation capture.

---

## 🏗️ Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Copilot Chat Export (PRIMARY)                │
│  📁 .github/workflows/CopilotChats.txt                 │
│  🔄 Auto-imports via post-commit hook                  │
│  🎯 Zero-effort tracking                               │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: Session Recording (ACTIVE WORK)              │
│  📁 sessions/*.json                                    │
│  🔄 Auto-records via auto-brain-updater.ps1           │
│  🎯 Captures planned work sessions                    │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: Manual Fallback (EDGE CASES)                 │
│  📁 record-conversation.ps1                            │
│  🔄 Manual invocation                                  │
│  🎯 Important conversations missed by Layer 1 & 2      │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Quick Start

### Check Tier 1 Health
```powershell
.\scripts\monitor-tier1-health.ps1
```

**Expected Output:**
```
📊 Tier 1 Utilization Report
================================
Total Conversations: 14 / 20 (FIFO capacity: 70%)
Auto-recorded: 10
Manual-recorded: 4
Auto-Recording Rate: 71.4%
✅ HEALTHY
```

### View Conversations
```powershell
Get-Content kds-brain\conversation-history.jsonl | ConvertFrom-Json | Format-Table conversation_id, title, source
```

### Generate Weekly Report
```powershell
.\scripts\tier1-health-report.ps1
# Output: reports/monitoring/tier1-health-report.md
```

---

## 📋 Layer 1: Copilot Chat Export

### How It Works
1. **GitHub Copilot** exports chats to `.github/workflows/CopilotChats.txt` (automatic)
2. **Git post-commit hook** detects changes to CopilotChats.txt
3. **import-copilot-chats.ps1** parses and imports to `conversation-history.jsonl`

### Manual Import
```powershell
.\scripts\import-copilot-chats.ps1
```

### Dry Run (Preview)
```powershell
.\scripts\import-copilot-chats.ps1 -DryRun
```

### Custom Path
```powershell
.\scripts\import-copilot-chats.ps1 -CopilotChatsPath "path\to\chats.txt"
```

---

## 📋 Layer 2: Session Recording

### How It Works
1. **work-planner.md** creates session files in `sessions/`
2. **auto-brain-updater.ps1** checks for completed sessions (active=false)
3. **record-session-conversation.ps1** converts session to conversation format

### Manual Session Recording
```powershell
.\scripts\record-session-conversation.ps1 -SessionFile "sessions\my-session.json"
```

### Force Recording (Active Session)
```powershell
.\scripts\record-session-conversation.ps1 -SessionFile "sessions\my-session.json" -Force
```

---

## 📋 Layer 3: Manual Recording

### Basic Usage
```powershell
.\scripts\record-conversation.ps1 `
    -Title "My Conversation" `
    -Outcome "Completed feature X"
```

### Full Parameters
```powershell
.\scripts\record-conversation.ps1 `
    -Title "Dashboard BRAIN Integration" `
    -FilesModified "dashboard.html,kds-brain/knowledge-graph.yaml" `
    -EntitiesDiscussed "dashboard,brain-reference,visual-design" `
    -Outcome "Created visual BRAIN reference system" `
    -Intent "PLAN" `
    -SessionId "session-123"
```

**Parameters:**
- **Title** (required): Brief conversation title
- **FilesModified** (optional): Comma-separated file list
- **EntitiesDiscussed** (optional): Comma-separated entities
- **Outcome** (required): Summary of results
- **Intent** (optional): PLAN, EXECUTE, TEST, VALIDATE, LEARN, CORRECT, UPDATE
- **SessionId** (optional): Link to existing session

---

## 📊 Monitoring & Tracking

### Real-Time Health Check
```powershell
.\scripts\monitor-tier1-health.ps1
```

**Metrics Tracked:**
- Total conversations (14/20 FIFO capacity)
- Auto-recorded vs manual (target: >80% auto)
- Utilization rate (target: >50%)
- Average messages per conversation
- FIFO capacity (target: 30-70%)

### Weekly Report
```powershell
.\scripts\tier1-health-report.ps1
```

**Report Includes:**
- Recording source breakdown (Copilot, Session, Manual)
- Intent distribution (PLAN, EXECUTE, TEST, etc.)
- Top entities discussed
- Top files modified
- Daily trend analysis
- Recommendations

### Monthly Report
```powershell
.\scripts\tier1-health-report.ps1 -Days 30
```

### Metrics in Development Context
Check `kds-brain/development-context.yaml`:
```yaml
tier1_metrics:
  total_conversations: 14
  auto_recorded: 10
  manual_recorded: 4
  utilization_rate: 71.4
  fifo_capacity: 70.0
  avg_message_count: 3.5
  last_updated: "2025-11-05T12:00:00Z"
  status: healthy
```

---

## 🔧 Troubleshooting

### Issue: Auto-Recording Rate < 50%

**Diagnosis:**
```powershell
.\scripts\monitor-tier1-health.ps1
```

**Solutions:**

1. **Check Copilot Chat Export** (Layer 1)
   ```powershell
   Test-Path ".github\workflows\CopilotChats.txt"
   .\scripts\import-copilot-chats.ps1 -DryRun
   ```

2. **Check Session Recording** (Layer 2)
   ```powershell
   Get-ChildItem sessions\*.json
   .\scripts\record-session-conversation.ps1 -SessionFile "sessions\latest.json"
   ```

3. **Use Manual Recording** (Layer 3)
   ```powershell
   .\scripts\record-conversation.ps1 -Title "Important Conv" -Outcome "Result"
   ```

### Issue: FIFO Queue Full (20/20)

**Symptom:** Oldest conversations being deleted

**Solution:** This is normal FIFO behavior. Increase capacity if needed:
1. Edit `scripts/record-conversation.ps1`
2. Change `$maxConversations = 20` to higher value
3. Update monitoring scripts with new threshold

### Issue: Duplicate Conversations

**Diagnosis:**
```powershell
Get-Content kds-brain\conversation-history.jsonl | ConvertFrom-Json | 
    Group-Object conversation_id | Where-Object Count -gt 1
```

**Solution:** Import scripts check for duplicates automatically. If found, manually remove from JSONL file.

---

## 🧪 Testing

### Run All Tests
```powershell
.\tests\test-tier1-tracking.ps1
```

**Tests Covered:**
- ✅ Layer 3: Manual recording
- ✅ Layer 2: Session recording
- ✅ Layer 1: Copilot Chat import
- ✅ Monitoring: Health checks

**Expected:** 13/13 tests pass

### Verify Data Quality
```powershell
# Check conversation structure
$convs = Get-Content kds-brain\conversation-history.jsonl | ConvertFrom-Json
$convs | Select-Object conversation_id, title, source, message_count

# Check sources
$convs | Group-Object source

# Check intents
$convs | Group-Object intent
```

---

## 📁 File Reference

| File | Purpose | Layer |
|------|---------|-------|
| `scripts/import-copilot-chats.ps1` | Import Copilot Chat exports | Layer 1 |
| `scripts/record-session-conversation.ps1` | Record completed sessions | Layer 2 |
| `scripts/record-conversation.ps1` | Manual conversation recording | Layer 3 |
| `scripts/monitor-tier1-health.ps1` | Real-time health monitoring | Tracking |
| `scripts/tier1-health-report.ps1` | Weekly/monthly reports | Tracking |
| `scripts/auto-brain-updater.ps1` | Enhanced with session recording | Integration |
| `hooks/post-commit` | Auto-triggers Layer 1 & 2 | Integration |
| `tests/test-tier1-tracking.ps1` | Validation suite | Testing |
| `kds-brain/conversation-history.jsonl` | FIFO queue (20 conversations) | Data |
| `kds-brain/conversation-context.jsonl` | Last 10 messages buffer | Data |

---

## 🎯 Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Auto-Recording Rate | >80% | 71.4% | ⚠️ Good |
| FIFO Utilization | 30-70% | 70% | ✅ Optimal |
| Total Conversations | 10+ | 14 | ✅ Healthy |
| Manual Rate | <20% | 28.6% | ⚠️ Acceptable |

---

## 🚀 Next Steps

1. **Monitor Weekly**
   ```powershell
   .\scripts\tier1-health-report.ps1
   ```

2. **Review Trends**
   - Check `reports/monitoring/tier1-health-report.md`
   - Identify patterns in entities/files
   - Adjust Layer 1 parser if Copilot format changes

3. **Continuous Improvement**
   - Increase auto-recording rate to >80%
   - Ensure FIFO rotation working (20 conversation limit)
   - Review conversation quality (entities, outcomes)

---

**Last Updated:** 2025-11-05  
**Version:** 7.0  
**Status:** ✅ All 13 tests passing
