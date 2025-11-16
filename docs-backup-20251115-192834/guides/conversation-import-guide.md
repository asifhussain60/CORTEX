# CORTEX 3.0 - Conversation Import Guide

**Purpose:** Import GitHub Copilot Chat conversations to CORTEX memory for long-term learning.

**Version:** 1.0 (Milestone 1)  
**Status:** ✅ PRODUCTION READY  
**Tests:** 19/19 passing

---

## 🚀 Quick Start (3 Steps)

### Step 1: See Smart Hint

When CORTEX detects a high-quality conversation, you'll see:

```
> ### 💡 CORTEX Learning Opportunity
> 
> **This conversation has exceptional strategic value:**
> - Multi-phase planning, design decisions
> 
> **Quality Score: 12/10 (EXCELLENT)**
> 
> 📁 **Ready to capture:**  
> → [Open: cortex-brain/conversation-captures/2025-11-13-your-topic.md]
> 
> *Copy conversation, paste into file, then say "import conversation"*
```

**Click the link** to open the capture file.

### Step 2: Paste Conversation

1. In Copilot Chat: **Export** → **Copy All**
2. Paste into the capture file
3. **Save** (Ctrl+S)

### Step 3: Import

Say in Copilot Chat:

```
import conversation
```

Done! CORTEX stores it in memory and archives to vault.

---

## 📊 Quality Levels

| Level | Score | Import? |
|-------|-------|---------|
| **EXCELLENT** | 10+ | ✅ Always |
| **GOOD** | 6-9 | ✅ Usually |
| **FAIR** | 3-5 | 🤔 Optional |
| **LOW** | 0-2 | ⏭️ Skip |

**What makes EXCELLENT?**
- Multi-phase planning (3 pts/phase)
- Challenge/Accept flow (3 pts)
- Design decisions (2 pts)
- Architectural discussion (2 pts)

---

## 💡 Example

**EXCELLENT Conversation (Score: 12):**

```
User: Plan the authentication system

CORTEX:
🎯 Understanding: You want to design authentication

⚠️ Challenge: ✓ Accept - Security is critical

💬 Response: Recommend multi-phase approach:

Phase 1: Core Auth (JWT tokens)
Phase 2: Route Protection  
Phase 3: Testing

🔍 Next Steps:
   1. Implement Phase 1
   2. Add guards
   3. Test thoroughly
```

This has: ✅ Phases ✅ Challenge/Accept ✅ Architecture ✅ Next Steps = **EXCELLENT**

---

## 🔍 Where Are My Conversations?

**During capture:**  
`cortex-brain/conversation-captures/[date]-[topic].md`

**After import:**  
`cortex-brain/conversation-vault/[date]-[topic].md`

**Metadata:**  
`cortex-brain/conversation-vault/metadata/[conv-id].json`

---

## 🆘 Troubleshooting

**Q: Smart Hint not appearing?**  
A: Only shown for GOOD+ conversations. Quick fixes won't trigger it.

**Q: Can I import manually?**  
A: Yes! Create file in `conversation-captures/`, paste conversation, say "import conversation".

**Q: How do I find old conversations?**  
A: Check the vault: `cortex-brain/conversation-vault/` - all conversations with metadata.

**Q: Can I delete imported conversations?**  
A: Files in vault are safe to delete. Database entries persist until FIFO eviction (20 limit).

---

## 🎯 Best Practices

✅ **DO import:**
- Feature planning sessions
- Architecture discussions
- Problem-solving with multiple approaches
- Multi-phase implementations

❌ **DON'T import:**
- Quick syntax fixes
- Simple questions
- Error messages only
- Repetitive tasks

---

## 📈 Next Steps

**Learn more:**
- `.github/prompts/shared/tracking-guide.md` - Full conversation tracking
- `cortex-brain/CORTEX-3.0-DUAL-CHANNEL-MEMORY-DESIGN.md` - Architecture

**Get help:**
Say "help import" or "conversation import guide" in Copilot Chat

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025  
**Version:** Milestone 1 Complete
