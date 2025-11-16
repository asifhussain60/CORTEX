# CORTEX Command Discovery System

**Version:** 1.0  
**Status:** 🎯 DESIGN PHASE  
**Related:** CORTEX 2.1 Enhancement  
**Author:** Asif Hussain  
**Date:** November 9, 2025

---

## 📋 Problem Statement

**Challenge:** As CORTEX commands grow (currently 7, projected 20+), users struggle to:
1. ❌ Remember all available commands
2. ❌ Know which command to use for their task
3. ❌ Discover new commands as they're added
4. ❌ Learn command syntax without consulting docs

**Impact:**
- Reduced feature adoption (users don't know features exist)
- Increased support burden (users asking "how do I...?")
- Friction in workflow (searching docs instead of working)
- Missed opportunities for collaboration (not using interactive planning)

---

## 🎯 Design Goals

1. **Zero Memory Required** - Users shouldn't need to memorize commands
2. **Contextual Relevance** - Show commands relevant to current work
3. **Progressive Discovery** - Learn commands through natural usage
4. **Non-Intrusive** - Help available but not annoying
5. **Scalable** - Works with 7 commands or 70 commands

---

## 🏗️ Architecture Overview

### Multi-Layer Discovery System

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Natural Language (PRIMARY)                │
│  User describes intent → CORTEX suggests command    │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Intelligent /help (DISCOVERY)             │
│  Context-aware command suggestions                  │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Proactive Suggestions (LEARNING)          │
│  Smart tips based on context and usage              │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Layer 4: Visual Aids (REFERENCE)                   │
│  Quick reference panels, autocomplete, widgets      │
└─────────────────────────────────────────────────────┘
```

---

## 💡 Solution 1: Intelligent `/help` Command

### Basic Usage

**Simple help:**
```
User: /help

CORTEX: 🎯 CORTEX Commands

📋 MOST RELEVANT (based on your current work):
  • /CORTEX, let's plan a feature
    You're viewing: CORTEX-2.1-QUICK-REFERENCE.md
    
  • /CORTEX, run tests
    Last used: 2 hours ago
    
💬 FREQUENTLY USED:
  • /setup - Environment configuration (used 15 times)
  • /resume - Continue previous work (used 8 times)

🔍 More: /help all | /help search <keyword> | /help <command>
```

### Advanced Usage

**Show all commands:**
```
User: /help all

CORTEX: 🎯 All CORTEX Commands (7 available)

🏗️  PLANNING & DESIGN:
  • /CORTEX, let's plan a feature ⭐⭐⭐
    Interactive feature planning with guided questions
    Example: "/CORTEX, let's plan a feature - add authentication"
    
  • /CORTEX, architect a solution ⭐⭐
    Collaborative architecture design
    Example: "/CORTEX, architect a solution for microservices"

♻️  REFACTORING & MAINTENANCE:
  • /CORTEX, refactor this module
    Interactive refactoring with clarifications
    
🧪 TESTING & VALIDATION:
  • /CORTEX, run tests
    Execute test suite
    
  • /CORTEX, run brain protection
    Validate brain protection rules

📚 DOCUMENTATION:
  • /CORTEX, generate documentation
    Auto-generate project documentation
    
  • /CORTEX, refresh cortex story
    Update CORTEX story documentation

⚙️  SETUP & ENVIRONMENT:
  • /setup (aliases: /env, /configure)
    Setup/configure current platform
    
  • /resume
    Resume previous conversation
    
  • /status
    Show current work status

⭐ = Popularity (⭐⭐⭐ = Most used)
```

**Search commands:**
```
User: /help search plan

CORTEX: 🔍 Found 3 commands matching "plan":

1. /CORTEX, let's plan a feature ⭐⭐⭐
   Interactive feature planning with guided questions
   
2. /setup
   Includes: platform planning and configuration
   
3. /CORTEX, architect a solution
   Related: includes planning phase for architecture

💡 Tip: Try natural language: "I want to plan a feature"
```

**Get help for specific command:**
```
User: /help /plan-feature

CORTEX: 📖 Command: /CORTEX, let's plan a feature

✨ What it does:
  Interactive feature planning where CORTEX asks clarifying 
  questions to understand your requirements before creating 
  an implementation plan.

🎯 When to use:
  - Complex features with unclear requirements
  - When you want to collaborate on planning
  - Before starting major implementations

💬 Usage:
  Command: /CORTEX, let's plan a feature - <description>
  Natural: "let's plan", "plan feature", "I want to plan"

📝 Example:
  /CORTEX, let's plan a feature - add JWT authentication
  
  CORTEX will ask 3-5 questions like:
  - What auth strategy?
  - Keep existing user schema?
  - Add refresh token support?

🔗 Learn more: docs/design/CORTEX-2.1-INTERACTIVE-PLANNING.md
```

---

## 💡 Solution 2: Natural Language Intent Detection

### Enhanced Intent Router

**Location:** `src/cortex_agents/corpus_callosum/intent_router.py`

**New capability: Command suggestion**

```python
class IntentRouter:
    def detect_intent_and_suggest_command(self, user_input: str):
        """
        Detects intent and suggests equivalent command.
        Educates user about command shortcuts.
        """
        intent = self.detect_intent(user_input)
        command = self.map_intent_to_command(intent)
        
        if command and not user_input.startswith('/'):
            # User used natural language - educate them
            return {
                'intent': intent,
                'command_equivalent': command,
                'show_suggestion': True,
                'message': f"💡 Tip: You can also use: {command}"
            }
        
        return {'intent': intent, 'command_equivalent': command}
```

**User Experience:**

```
User: "I want to plan how to add authentication"

CORTEX: "I understand you want to plan a feature! 🎯
        
        💡 Quick tip: You can also use this command:
           /CORTEX, let's plan a feature - add authentication
        
        Starting interactive planning now...
        
        [Don't show tips] [Learn more about commands]"
```

**Progressive Learning:**
- First time: Show tip with full explanation
- 2nd-3rd time: Show shorter tip
- 4+ times: No tip (user has learned)
- User can disable tips: "Don't show tips"

---

## 💡 Solution 3: Context-Aware Suggestions

### Smart Context Detection

**Location:** `src/cortex_agents/right_brain/context_analyzer.py`

```python
class ContextAnalyzer:
    def suggest_relevant_commands(self, context: Dict) -> List[CommandSuggestion]:
        """
        Analyzes current context and suggests relevant commands.
        
        Context includes:
        - Current file/directory
        - Recent git activity
        - Time since last command
        - Current task status
        """
        suggestions = []
        
        # File-based suggestions
        if context['current_file'].endswith('test.py'):
            suggestions.append({
                'command': '/CORTEX, run tests',
                'reason': 'You\'re editing a test file',
                'confidence': 0.9
            })
        
        # Architecture docs → suggest architect command
        if 'architecture' in context['current_file'].lower():
            suggestions.append({
                'command': '/CORTEX, architect a solution',
                'reason': 'You\'re viewing architecture documentation',
                'confidence': 0.85
            })
        
        # Design docs → suggest planning
        if 'design' in context['current_file'].lower():
            suggestions.append({
                'command': '/CORTEX, let\'s plan a feature',
                'reason': 'You\'re in design phase',
                'confidence': 0.8
            })
        
        # Time-based suggestions
        if context['hours_since_last_activity'] > 24:
            suggestions.append({
                'command': '/resume',
                'reason': 'Continue where you left off yesterday',
                'confidence': 0.75
            })
        
        # Recent changes → suggest tests
        if context['uncommitted_changes'] > 10:
            suggestions.append({
                'command': '/CORTEX, run tests',
                'reason': 'You have uncommitted changes',
                'confidence': 0.7
            })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
```

**User Experience:**

```
User: *opens file: src/auth/authentication.py*

CORTEX: 💡 Context Suggestion
        
        I notice you're working on authentication code.
        Relevant commands:
        
        1. /CORTEX, let's plan a feature - add auth features
        2. /CORTEX, refactor this module - refactor auth code
        3. /CORTEX, run tests - test auth changes
        
        [Dismiss] [Use command 1] [Stop suggestions]
```

---

## 💡 Solution 4: Proactive Command Education

### Smart Onboarding

**First-time user experience:**

```
CORTEX: 👋 Welcome to CORTEX 2.1!

        I'm your AI development partner with memory and planning abilities.
        
        🎯 You can talk to me naturally:
           "Add a purple button to the dashboard"
           "Let's plan how to add authentication"
        
        ⚡ Or use quick commands:
           /help - Discover all commands
           /setup - Configure environment
           /resume - Continue previous work
        
        💡 I'll suggest relevant commands as you work.
        
        Ready to start? Try: "show me the CORTEX story"
        
        [Take interactive tour] [Skip to work] [Settings]
```

**Milestone-based education:**

```
User: *completes first successful task*

CORTEX: ✅ Task complete! Great work!

        💡 Learning Moment:
        Did you know? Next time you can use:
        /resume - to continue this work later
        
        I'll remember our conversation history, so you can
        always pick up where we left off!
        
        [Try it now] [Remind me later] [Learn more]
```

---

## 💡 Solution 5: Visual Command Reference

### Quick Reference Panel (VS Code Extension)

**Sidebar widget:**

```
┌──────────────────────────────────────┐
│ 🎯 CORTEX Quick Commands            │
├──────────────────────────────────────┤
│ 🔍 Search: [________________] 🔎    │
├──────────────────────────────────────┤
│ 📋 FAVORITES (drag to reorder)      │
│  ⭐ /plan-feature                    │
│  ⭐ /run-tests                       │
│  ⭐ /setup                           │
│     [+ Add favorite]                 │
├──────────────────────────────────────┤
│ 📚 ALL COMMANDS (7)                  │
│  └─ 🏗️  Planning & Design (2)       │
│     • /plan-feature                  │
│     • /architect                     │
│  └─ 🧪 Testing & Validation (2)     │
│     • /run-tests                     │
│     • /brain-protect                 │
│  └─ 📚 Documentation (2)            │
│     • /generate-docs                 │
│     • /refresh-story                 │
│  └─ ⚙️  Setup (3)                    │
│     • /setup                         │
│     • /resume                        │
│     • /status                        │
├──────────────────────────────────────┤
│ 💡 Tip of the day                   │
│ Use natural language! Just tell     │
│ CORTEX what you want.               │
│ [Next tip] [Disable]                │
└──────────────────────────────────────┘
```

**Features:**
- ✅ Searchable command list
- ✅ Favorites for quick access
- ✅ Collapsible categories
- ✅ Click to insert command
- ✅ Daily tips
- ✅ Usage statistics

### Status Bar Integration

**Bottom-right status bar:**

```
🎯 CORTEX | 💬 Last: /plan-feature (2h ago) | ⚡ /help
```

Click:
- `🎯 CORTEX` → Open quick command palette
- `💬 Last...` → Repeat last command
- `⚡ /help` → Show help

---

## 🧠 Tier 2 Knowledge Enhancement

### Track Command Usage Patterns

**Location:** `cortex-brain/knowledge-graph.yaml`

```yaml
command_usage_analytics:
  user_preferences:
    favorite_commands:
      - command: "/CORTEX, let's plan a feature"
        usage_count: 23
        last_used: "2025-11-09T14:30:00Z"
        average_frequency: "2-3 times per week"
        
      - command: "/CORTEX, run tests"
        usage_count: 45
        last_used: "2025-11-09T16:15:00Z"
        average_frequency: "daily"
    
    command_discovery:
      - command: "/CORTEX, architect a solution"
        discovered_via: "natural_language"
        learned: "2025-11-08"
        uses_since_discovery: 3
        
      - command: "/CORTEX, refactor this module"
        discovered_via: "/help search refactor"
        learned: "2025-11-07"
        uses_since_discovery: 0  # Never used after discovery
    
    learning_patterns:
      - "user prefers natural language over commands"
        confidence: 0.87
        
      - "user forgets /resume command (needs reminders)"
        confidence: 0.92
        
      - "user discovered 5/7 commands through natural language"
        confidence: 1.0
  
  command_effectiveness:
    most_discovered_via:
      natural_language: 65%
      help_command: 25%
      proactive_suggestions: 10%
    
    adoption_rate:
      discovered_and_used: 71%  # 5/7 commands used after discovery
      discovered_not_used: 29%  # 2/7 never used after learning
```

### Personalized Help

**Use Tier 2 data to personalize suggestions:**

```python
def generate_personalized_help(user_history: Dict) -> str:
    """
    Generates help tailored to user's usage patterns.
    """
    if user_history['prefers_natural_language']:
        return """
        💬 You prefer natural language! Here's how I understand you:
        
        "Let's plan" → /CORTEX, let's plan a feature
        "Run tests" → /CORTEX, run tests
        "Setup environment" → /setup
        
        Keep talking naturally - I'll understand! 🎯
        """
    
    if user_history['forgets_resume']:
        return """
        💡 Reminder: Use /resume to continue previous work
        
        You haven't used this in 2 weeks, but it's super helpful
        for picking up where you left off!
        """
    
    # Suggest underused commands
    unused = user_history['discovered_but_unused']
    if unused:
        return f"""
        🤔 You discovered {unused[0]['command']} but haven't tried it yet.
        
        It's great for: {unused[0]['use_case']}
        Want to try it now?
        """
```

---

## 🎯 Implementation Phases

### Phase 1: Core Discovery (Week 1) - HIGH PRIORITY

**Tasks:**
1. ✅ Build intelligent `/help` command
   - Basic help with categories
   - `/help all` for full list
   - `/help search <keyword>` for searching
   - `/help <command>` for details

2. ✅ Enhance intent router
   - Command suggestion after natural language
   - Progressive learning (reduce tips over time)
   - User preference for tip frequency

3. ✅ Basic usage tracking
   - Track command usage in Tier 2
   - Count frequency
   - Record discovery method

**Deliverables:**
- `src/cortex_agents/corpus_callosum/help_agent.py`
- Enhanced `src/cortex_agents/corpus_callosum/intent_router.py`
- Tier 2 schema updates
- Unit tests

### Phase 2: Context-Aware Help (Week 2) - MEDIUM PRIORITY

**Tasks:**
1. ✅ Context analyzer
   - File-based suggestions
   - Time-based suggestions
   - Git activity analysis

2. ✅ Proactive suggestions
   - Show relevant commands based on context
   - Non-intrusive notifications
   - Dismissible with user preference

3. ✅ Personalized help
   - Use Tier 2 data for personalization
   - Suggest underused commands
   - Remind about forgotten features

**Deliverables:**
- `src/cortex_agents/right_brain/context_analyzer.py`
- Proactive suggestion system
- Personalized help generator
- Integration tests

### Phase 3: Visual Aids (Week 3) - LOW PRIORITY

**Tasks:**
1. ✅ Quick reference sidebar (VS Code extension)
   - Searchable command list
   - Favorites
   - Categories
   - Click to use

2. ✅ Status bar integration
   - Show last command
   - Quick command palette
   - Usage stats

3. ✅ Onboarding tour
   - First-time user experience
   - Interactive tutorial
   - Milestone-based education

**Deliverables:**
- VS Code extension updates
- Onboarding tour implementation
- User documentation

### Phase 4: Analytics & Optimization (Week 4) - ONGOING

**Tasks:**
1. ✅ Usage analytics
   - Track discovery methods
   - Measure adoption rates
   - Identify unused commands

2. ✅ A/B testing
   - Test different suggestion styles
   - Optimize tip frequency
   - Measure effectiveness

3. ✅ Continuous improvement
   - Refine based on data
   - Add new discovery methods
   - Improve suggestions

**Deliverables:**
- Analytics dashboard
- A/B testing framework
- Optimization reports

---

## 📊 Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Command discovery rate** | >90% | Users discover commands within 1 week |
| **Command adoption rate** | >70% | Discovered commands are actually used |
| **Help usage reduction** | -50% | Less need for `/help` over time |
| **Natural language preference** | >60% | Users choose NL over commands |
| **Time to find command** | <30 sec | From need to execution |
| **User satisfaction** | >4.5/5 | Survey rating for discoverability |

### Qualitative Metrics

- ✅ Users feel commands are "easy to find"
- ✅ Users don't feel overwhelmed by suggestions
- ✅ Users discover features organically
- ✅ Users prefer CORTEX over documentation search
- ✅ Reduced support questions about "how do I...?"

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/corpus_callosum/test_help_agent.py

def test_basic_help():
    """Test basic /help output"""
    pass

def test_help_search():
    """Test /help search functionality"""
    pass

def test_command_categorization():
    """Test commands are properly categorized"""
    pass

def test_context_aware_suggestions():
    """Test suggestions based on context"""
    pass
```

### Integration Tests

```python
# tests/integration/test_command_discovery.py

def test_natural_language_to_command():
    """Test NL intent detection suggests command"""
    pass

def test_progressive_learning():
    """Test tips reduce over time"""
    pass

def test_personalized_help():
    """Test help adapts to user history"""
    pass
```

### User Testing

**Scenarios:**
1. First-time user: Can they discover 5/7 commands in 30 minutes?
2. Return user: Do they remember commands or rely on help?
3. Power user: Are suggestions helpful or annoying?

---

## 🔒 Brain Protection

**New rules for command discovery:**

```yaml
# cortex-brain/brain-protection-rules.yaml

command_discovery:
  help_system:
    - rule: "Must provide /help command at all times"
      severity: "critical"
      
    - rule: "Help output must be readable (max 50 lines)"
      severity: "error"
      
    - rule: "Search must return results in <1 second"
      severity: "warning"
  
  suggestions:
    - rule: "Never show more than 1 suggestion per interaction"
      severity: "error"
      reason: "Prevents overwhelming user"
      
    - rule: "Respect user preference to disable suggestions"
      severity: "critical"
      
    - rule: "Suggestions must be dismissible"
      severity: "critical"
  
  privacy:
    - rule: "Command usage tracking is opt-in"
      severity: "critical"
      
    - rule: "User can delete usage history anytime"
      severity: "critical"
```

---

## 📚 Documentation Updates

### User Documentation

1. **New file:** `docs/guides/COMMAND-DISCOVERY-GUIDE.md`
   - How to find commands
   - Using /help effectively
   - Understanding suggestions
   - Customizing preferences

2. **Update:** `README.md`
   - Add "How to Find Commands" section
   - Highlight /help command

3. **Update:** `.github/prompts/CORTEX.prompt.md`
   - Mention command discovery system
   - Link to discovery guide

### Developer Documentation

1. **New file:** `docs/development/ADDING-NEW-COMMANDS.md`
   - How to register commands
   - How to add help text
   - How to categorize commands
   - How to add natural language equivalents

---

## 🎨 UX Principles

### Design Philosophy

1. **Progressive Disclosure**
   - Don't overwhelm with all commands at once
   - Reveal commands as user needs them
   - Start with natural language, teach commands later

2. **Contextual Relevance**
   - Only suggest commands that make sense now
   - Use current work context
   - Learn user's patterns

3. **Non-Intrusive**
   - Suggestions are helpful, not annoying
   - Easy to dismiss
   - User can disable completely

4. **Educational**
   - Teach through usage
   - Show command equivalents
   - Explain why commands are useful

5. **Empowering**
   - User feels in control
   - Multiple ways to accomplish tasks
   - No "wrong" way to use CORTEX

---

## 🚀 Rollout Strategy

### Phase 1: Silent Launch (Week 1)
- ✅ Deploy `/help` command
- ✅ No announcements yet
- ✅ Gather baseline metrics

### Phase 2: Soft Launch (Week 2)
- ✅ Enable context suggestions
- ✅ Limited to 10 beta users
- ✅ Gather feedback

### Phase 3: Public Launch (Week 3)
- ✅ Full rollout to all users
- ✅ Announcement: "Discover CORTEX commands easily!"
- ✅ Tutorial/onboarding

### Phase 4: Optimization (Ongoing)
- ✅ Monitor usage data
- ✅ Refine suggestions
- ✅ A/B test improvements

---

## 🔮 Future Enhancements (Post-Launch)

### Potential Features

1. **Voice Commands**
   - "Hey CORTEX, help me plan"
   - Voice-activated command palette

2. **Command Aliases (User-Defined)**
   - User: "I want to call '/plan-feature' as '/p'"
   - CORTEX: "Got it! '/p' now maps to '/plan-feature'"

3. **Command Macros**
   - Chain multiple commands
   - Example: "/morning-routine" = "/resume + /status + /run-tests"

4. **AI-Generated Commands**
   - User: "I need a command that does X"
   - CORTEX: "Let me create that for you..."

5. **Social Learning**
   - "Users like you also use: /command"
   - Team-wide command sharing

---

## 📖 Example User Journeys

### Journey 1: First-Time User

```
Day 1 - First interaction:
  User: "Add a button"
  CORTEX: ✅ Done! 
          💡 Tip: You can also use natural language anytime.
          Try: "Let's plan a new feature"

Day 2 - Discovery:
  User: "Let's plan a new feature"
  CORTEX: Great! I understand you want to plan.
          💡 Quick tip: You can also use: /CORTEX, let's plan a feature
          Starting planning now...
          
  [User learns command exists but still prefers NL]

Day 3 - Exploration:
  User: "/help"
  CORTEX: [Shows relevant commands based on recent work]
  
  [User browses and bookmarks favorites]

Day 7 - Proficiency:
  User: "/plan" [uses shortcut]
  CORTEX: Starting interactive planning... 🚀
  
  [User has adopted commands, uses mix of NL and shortcuts]
```

### Journey 2: Power User

```
Week 1:
  User: "/help all"
  CORTEX: [Shows all 7 commands]
  [User reads and bookmarks 3 favorites]

Week 2:
  User: *editing test file*
  CORTEX: 💡 Suggestion: /run-tests
  User: [Clicks suggestion - saves time]

Week 3:
  User: "/help search refactor"
  CORTEX: Found: /refactor-module
  User: [Discovers new feature]

Month 2:
  [User has created custom aliases]
  [Uses command palette daily]
  [Rarely needs /help anymore]
```

---

## ✅ Acceptance Criteria

**Must have (Phase 1):**
- ✅ `/help` command with categories
- ✅ `/help search <keyword>` works
- ✅ `/help <command>` shows details
- ✅ Natural language suggests command equivalents
- ✅ Command usage tracked in Tier 2

**Should have (Phase 2):**
- ✅ Context-aware suggestions
- ✅ Personalized help based on history
- ✅ Proactive command education
- ✅ User can disable suggestions

**Nice to have (Phase 3):**
- ✅ Visual command palette
- ✅ Status bar integration
- ✅ Onboarding tour
- ✅ Usage analytics dashboard

---

## 🏁 Conclusion

This command discovery system ensures users never need to memorize commands. Through intelligent help, natural language understanding, context awareness, and proactive suggestions, users will discover and adopt CORTEX commands organically.

**Key Innovations:**
- ✅ Multi-layer discovery (NL → Help → Suggestions → Visual)
- ✅ Context-aware relevance
- ✅ Progressive learning
- ✅ Non-intrusive education
- ✅ Personalization through Tier 2 memory

**Expected Impact:**
- 90%+ command discovery rate
- 70%+ command adoption rate
- 50% reduction in help usage over time
- Higher user satisfaction and productivity

**Next Steps:**
1. Review and approve design
2. Prioritize Phase 1 implementation
3. Begin development (Week 1)

---

*Design Document Version: 1.0*  
*Last Updated: November 9, 2025*  
*Status: Ready for Implementation Review*
