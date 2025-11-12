# Command Discovery - Quick Summary

**Problem:** Users will forget commands as CORTEX grows (7 → 20+)

**Solution:** 5-Layer Discovery System (Zero memorization required!)

---

## 🎯 The 5 Layers

### 1️⃣ Natural Language (PRIMARY) - 60%+ usage
```
User: "I want to plan a feature"
CORTEX: "Starting planning... 💡 Tip: You can also use /plan-feature"
```
**✅ Zero memorization needed**

### 2️⃣ Intelligent `/help` (DISCOVERY) - 25% usage
```
User: /help

CORTEX: 📋 MOST RELEVANT (based on your current work):
  • /plan-feature - You're viewing a design doc
  • /run-tests - Last used 2 hours ago
  
🔍 /help search <keyword> | /help all | /help <command>
```
**✅ Context-aware suggestions**

### 3️⃣ Proactive Suggestions (LEARNING) - 10% usage
```
*User opens architecture file*

CORTEX: 💡 Tip: Try /architect for collaborative design
        [Dismiss] [Use it] [Stop tips]
```
**✅ Learns when to suggest**

### 4️⃣ Visual Aids (REFERENCE) - 5% usage
```
Sidebar widget with:
- Searchable command list
- Favorite commands
- Click to use
- Daily tips
```
**✅ Always-available reference**

### 5️⃣ Autocomplete (SPEED) - Power users
```
User types: /pla

Suggests:
  • /plan-feature ⭐ (most popular)
  • /setup - Platform setup
```
**✅ Faster for pros**

---

## 🎨 Design Principles

1. **Progressive Disclosure** - Reveal as needed
2. **Contextual Relevance** - Suggest based on work
3. **Non-Intrusive** - Helpful, not annoying
4. **Educational** - Learn through usage
5. **Empowering** - Multiple paths to success

---

## 📊 Expected Results

| Metric | Target |
|--------|--------|
| Command discovery | >90% within 1 week |
| Command adoption | >70% after discovery |
| Natural language usage | >60% preference |
| Time to find command | <30 seconds |
| User satisfaction | >4.5/5 |

---

## 🚀 Implementation (3 Phases)

**Phase 1 (Week 1) - HIGH PRIORITY:**
- ✅ Intelligent `/help` command
- ✅ Natural language → command suggestions
- ✅ Basic usage tracking

**Phase 2 (Week 2) - MEDIUM PRIORITY:**
- ✅ Context-aware suggestions
- ✅ Proactive education
- ✅ Personalized help

**Phase 3 (Week 3) - LOW PRIORITY:**
- ✅ Visual command palette
- ✅ Status bar integration
- ✅ Onboarding tour

---

## 💡 Key Innovation

**Users NEVER need to memorize commands!**

They can:
1. Talk naturally (CORTEX understands)
2. Ask for help (context-aware)
3. Receive suggestions (at right time)
4. Browse visually (quick reference)
5. Autocomplete (if they want speed)

**Choose your style - all work perfectly!** 🎯

---

## 📚 Full Design

See: `docs/design/CORTEX-COMMAND-DISCOVERY-SYSTEM.md`

---

*Problem solved: As commands grow, users discover them naturally!*
