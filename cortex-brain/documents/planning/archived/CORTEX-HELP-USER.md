# CORTEX User Help - Quick Reference

**Version:** 2.1  
**Last Updated:** 2025-11-22  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🚀 Quick Start

Just tell CORTEX what you need in natural language:

```
"show me a demo"
"setup environment"
"onboard this application"
"plan a new feature"
"resume authentication work"
```

No slash commands needed! CORTEX understands natural language.

---

## 📋 User Operations

| Operation | Natural Language | What It Does | Status |
|-----------|------------------|--------------|--------|
| **Demo** | "demo", "show me what cortex can do" | Interactive walkthrough of CORTEX capabilities | ✅ Ready |
| **Setup** | "setup", "configure cortex" | Configure development environment (Mac/Windows/Linux) | ✅ Ready |
| **Onboard App** | "onboard this application", "analyze my codebase" | Deploy CORTEX to your application with intelligent analysis | ✅ Ready |
| **Plan Feature** | "plan a feature", "let's plan authentication" | Interactive feature planning with DoR validation | ✅ Ready |
| **Enhance Existing** | "enhance the dashboard", "improve authentication" | Discover existing code and plan enhancements | ✅ Ready |
| **Maintain** | "maintain", "cleanup", "optimize cortex" | Workspace cleanup and system optimization | ✅ Ready |
| **Resume Conversation** | "resume authentication", "continue our dark mode work" | Resume previous conversation with full context | ✅ Ready |
| **Status** | "status", "where are we" | Show current implementation status | ✅ Ready |
| **Help** | "help", "what can cortex do" | Show this help message | ✅ Ready |

---

## 🎬 Demo Operation

**Purpose:** Interactive walkthrough of CORTEX capabilities

**Profiles:**
- **Quick** (2 min) - Essential commands only
- **Standard** (3-4 min) - Core capabilities (DEFAULT)
- **Comprehensive** (5-6 min) - Full walkthrough
- **Developer** (8-10 min) - Development workflow deep-dive

**Usage:**
```
"demo"                    # Standard profile
"show me a quick demo"    # Quick profile
"comprehensive demo"      # Full walkthrough
```

**What You'll See:**
- ✅ Help system with natural language commands
- ✅ Story transformation with narrator voice
- ✅ DoD/DoR workflow integration
- ✅ Token optimization (97.2% reduction)
- ✅ Code review capabilities
- ✅ Conversation memory system

---

## ⚙️ Setup Operation

**Purpose:** Configure CORTEX development environment

**Profiles:**
- **Minimal** - Core functionality only
- **Standard** - Recommended for most users (DEFAULT)
- **Full** - Everything enabled

**Usage:**
```
"setup"                       # Standard setup
"setup environment"           # Standard setup
"minimal setup"               # Core only
"full setup"                  # Everything enabled
```

**What It Does:**
1. ✅ Validates project structure
2. ✅ Detects platform (Mac/Windows/Linux)
3. ✅ Configures virtual environment
4. ✅ Installs Python dependencies
5. ✅ Initializes brain tiers (0, 1, 2, 3)
6. ✅ Runs validation tests
7. ✅ Generates setup report

**Requirements:**
- Python 3.10+
- Git (optional but recommended)
- 500MB disk space

---

## 📦 Onboard Application Operation

**Purpose:** Deploy CORTEX to your application with intelligent analysis

**Profiles:**
- **Quick** - Essential setup only (no questions)
- **Standard** - Full analysis with smart questions (DEFAULT)
- **Comprehensive** - Deep analysis with recommendations

**Usage:**
```
"onboard this application"                # Standard profile
"analyze my codebase"                     # Standard profile
"quick onboard"                           # Skip questions
"comprehensive application onboarding"    # Deep analysis
```

**What It Does:**
1. ✅ Copies CORTEX entry points to `.github/`
2. ✅ Installs required tooling
3. ✅ Initializes brain databases
4. ✅ Crawls and indexes codebase
5. ✅ Analyzes tech stack and dependencies
6. ✅ Generates architecture documentation
7. ✅ Asks intelligent questions:
   - "I see React but no test files - shall I help set up Jest?"
   - "You have ESLint but not on pre-commit - want hooks?"
   - "No TypeScript detected - would you like type safety migration?"

**Smart Questions:**
- Only asks what's relevant to YOUR codebase
- Detects missing best practices
- Suggests improvements based on industry standards
- Can implement recommendations with tests

---

## 🎯 Feature Planning Operation

**Purpose:** Interactive feature planning with zero ambiguity

**Usage:**
```
"plan a feature"                    # Standard planning
"plan authentication system"        # Plan specific feature
"let's plan a new API"             # Interactive planning
```

**Planning Process:**
1. **DoR Validation** - Definition of Ready with zero ambiguity
2. **Clarifying Questions** - CORTEX asks targeted questions:
   - What EXACTLY does this feature do?
   - Who are the SPECIFIC users?
   - What EXACT systems/APIs/databases?
   - What are MEASURABLE constraints?
   - How do we MEASURE success?
3. **Security Review** - OWASP Top 10 checklist
4. **Plan Generation** - Phase breakdown with milestones
5. **Approval** - Review plan before implementation

**Output:**
- Planning file: `cortex-brain/documents/planning/features/PLAN-[date]-[feature].md`
- Structured phases (Foundation → Core → Validation)
- Risk analysis
- Security considerations
- Task generation
- Acceptance criteria

**Example:**
```
You: "plan authentication system"

CORTEX: 
✅ Created planning file: PLAN-2025-11-22-authentication.md

📋 Definition of Ready Checklist:
☐ Requirements documented (zero ambiguity)
☐ Dependencies identified & validated
☐ Technical design approach agreed
☐ Test strategy defined
☐ Acceptance criteria measurable
☐ Security review complete
☐ User approval on scope

📬 Clarifying Questions (Must answer ALL):
1. **Feature Scope** - What EXACTLY does authentication do?
2. **Users** - Who are the SPECIFIC users?
...
```

---

## 🔄 Resume Conversation Operation

**Purpose:** Resume previous conversation with full context restoration

**Usage:**
```
"resume authentication"                # Resume by topic
"continue our dark mode work"         # Resume by description
"resume conversation conv-20251122"   # Resume by ID
```

**What It Does:**
1. ✅ Searches past conversations for related discussions
2. ✅ Scores them for relevance (keywords, files, intent, recency)
3. ✅ Restores planning documents if they exist
4. ✅ Injects context automatically
5. ✅ Shows context summary so you know what Copilot "remembered"

**Context Display:**
```
📋 Context from Previous Conversations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 Conversation 1: JWT authentication implementation
   Relevance: 0.87 (High)
   Time: 2 days ago
   Files: auth.py, tokens.py
   Intent: IMPLEMENT

Quality Indicators:
- Total Conversations: 1
- Average Relevance: 0.87
- Token Usage: 324 / 500

✅ Context quality: High
```

---

## 🧹 Maintain Operation

**Purpose:** Comprehensive maintenance combining cleanup, optimization, and health checks

**Profiles:**
- **Quick** - Cleanup and basic health check
- **Standard** - Cleanup, optimization, and health validation (DEFAULT)
- **Comprehensive** - Full maintenance with auto-optimization

**Usage:**
```
"maintain"                    # Standard maintenance
"cleanup"                     # Standard maintenance
"optimize cortex"             # Standard maintenance
"comprehensive maintenance"   # Full maintenance
```

**What It Does:**
1. **Cleanup:**
   - ✅ Remove temporary files
   - ✅ Clear Python cache
   - ✅ Remove old logs (30+ days)
   - ✅ Vacuum SQLite databases

2. **Optimization:**
   - ✅ Validate Tier 0 governance
   - ✅ Check tier health
   - ✅ Profile performance
   - ✅ Audit configuration

3. **Health Check:**
   - ✅ Test coverage analysis
   - ✅ Module status review
   - ✅ Generate health report

**Output:**
- Cleanup report: Files removed, space saved
- Optimization plan: Recommendations for improvements
- Health report: System diagnostics

---

## 💬 Conversation Memory System

**Purpose:** Track and restore conversation context across sessions

**How It Works:**
- Automatically captures conversations in Tier 1 memory
- Searches and scores past conversations for relevance
- Auto-injects context when relevant (score > 0.50)
- Context displayed at START of Copilot responses

**Commands:**
```
"show context"                    # View what Copilot remembers
"forget about authentication"     # Remove specific conversations
"forget the old API design"       # Remove by topic
"clear all context"               # Remove ALL memory (fresh start)
"clear memory"                    # Alias for clear all
```

**Context Quality:**
| Score | Quality | Meaning |
|-------|---------|---------|
| 0.80+ | 🟢 High | Same topic, files, intent - very relevant |
| 0.50-0.79 | 🟡 Medium | Related concepts |
| 0.20-0.49 | 🟠 Low | Tangentially related |
| <0.20 | 🔴 Very Low | Not useful |

**What Affects Relevance:**
- Keyword overlap (30%)
- File overlap (25%)
- Entity overlap - classes, functions (20%)
- Recency - newer scores higher (15%)
- Intent match - PLAN/IMPLEMENT/FIX/etc. (10%)

---

## 🎓 Best Practices

### Feature Planning
1. ✅ Answer ALL clarifying questions (no vague terms)
2. ✅ Review DoR checklist before approval
3. ✅ Run security review for HIGH/CRITICAL features
4. ✅ Validate dependencies exist before proceeding

### Conversation Memory
1. ✅ Capture important decisions naturally (auto-stored)
2. ✅ Clean up outdated context monthly
3. ✅ Use `show context` to review what's remembered
4. ✅ Resume conversations across sessions seamlessly

### Application Onboarding
1. ✅ Run standard profile for best experience
2. ✅ Answer smart questions to get tailored recommendations
3. ✅ Review generated documentation before deployment
4. ✅ Let CORTEX implement recommendations with tests

---

## 🆘 Troubleshooting

### Operation Fails
```
Check CORTEX installation: "cortex status"
Validate brain structure: "cortex setup"
Try quick profile: "quick demo"
```

### Copilot Doesn't Recognize CORTEX
```
Ensure .github/prompts/CORTEX.prompt.md exists
Restart VS Code
Try: "help" to see available commands
```

### Memory Not Working
```
Check conversation tracking: "show context"
Validate Tier 1 database: "cortex setup"
Clear and restart: "clear memory" then resume
```

---

## 📚 Additional Resources

**Documentation:**
- Story: `.github/prompts/shared/story.md`
- Setup Guide: `.github/prompts/shared/setup-guide.md`
- Technical Docs: `.github/prompts/shared/technical-reference.md`
- Tracking Guide: `.github/prompts/shared/tracking-guide.md`

**Support:**
- GitHub: https://github.com/asifhussain60/CORTEX
- Issues: Report via GitHub Issues

---

**Version:** 2.1  
**Last Updated:** 2025-11-22
