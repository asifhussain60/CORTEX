# Module Guides Index

**Location:** `.github/prompts/modules/`  
**Purpose:** Comprehensive guides for all CORTEX features and workflows

---

## Core Features

### Planning & Development
- **[planning-orchestrator-guide.md](planning-orchestrator-guide.md)** - Planning System 2.0 with Vision API, DoR/DoD validation
- **[tdd-mastery-guide.md](tdd-mastery-guide.md)** - TDD workflow with auto-debug and refactoring
- **[hands-on-tutorial-guide.md](hands-on-tutorial-guide.md)** - Interactive 15-30 min CORTEX learning program

### System Management
- **[system-alignment-guide.md](system-alignment-guide.md)** - System alignment checks and integration scoring (admin)
- **[upgrade-guide.md](upgrade-guide.md)** - Universal upgrade system with brain preservation
- **[architecture-intelligence-guide.md](architecture-intelligence-guide.md)** - Architecture health trends and debt forecasting

### User Interface
- **[dashboard-launcher-guide.md](dashboard-launcher-guide.md)** - HTTP server, auto-browser, smart ports (NEW in v3.7.1)
- **[quick-start-guide.md](quick-start-guide.md)** - Getting started with CORTEX
- **[setup-epm-guide.md](setup-epm-guide.md)** - Environment setup for Mac/Windows/Linux

---

## Response System

### Templates & Formatting
- **[response-format.md](response-format.md)** - Mandatory 5-part response structure
- **[template-guide.md](template-guide.md)** - Response template system overview
- **[template-triggers.md](template-triggers.md)** - Auto-selection rules for templates

### Routing & Operations
- **[operations-routing-guide.md](operations-routing-guide.md)** - Operation registration and routing
- **[user-profile-system-guide.md](user-profile-system-guide.md)** - User profile management

---

## Advanced Features

### Development Tools
- **[timeframe-estimation-guide.md](timeframe-estimation-guide.md)** - Timeframe estimation for tasks

---

## Usage

**In Documentation:**
```markdown
**Guide:** `.github/prompts/modules/planning-orchestrator-guide.md`
```

**In Code:**
```python
# Reference in comments
# See: .github/prompts/modules/tdd-mastery-guide.md
```

**For Users:**
```
# Natural language
"Show me the planning guide"
"How do I use TDD Mastery?"
```

---

## Validation

**Check all guides exist:**
```bash
python scripts/validate_module_guides.py
```

**Expected output:**
```
[OK] 14/14 guides found
```

---

## Contributing

**Adding New Guide:**
1. Create `feature-name-guide.md` in this directory
2. Follow existing format (Overview, Features, Usage, Troubleshooting)
3. Reference in documentation files
4. Run validation: `python scripts/validate_module_guides.py`

**Guide Format:**
- Title with version and status
- Overview section
- Features with examples
- Troubleshooting section
- Related guides
- Changelog

---

## Statistics

**Total Guides:** 14  
**Coverage:** 100% of major features  
**Average Length:** 200-400 lines  
**Format:** Markdown with code examples

---

**Last Updated:** 2025-12-05  
**Version:** 3.7.1
