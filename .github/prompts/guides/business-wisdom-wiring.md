# Business Wisdom Wiring Guide

**Date:** 2026-02-13  
**Author:** Asif Hussain  
**Phase:** CORE Rule Enhancement (Book Reference Integration)  
**Status:** ✅ Stage 1 Complete, Stages 2-3 Ready for Team Implementation

---

## 📖 What Changed

All 33 CORE governance rules in `cortex_brain/tier0/governance/core-rules.yaml` now include **`book_reference`** fields linking each rule to famous business/tech books.

### Example Structure (BEFORE → AFTER)

**BEFORE:**
```yaml
- rule_id: CORE-008
  principle: "Red-Green-Refactor Discipline"
  category: code_quality
  severity: blocked
```

**AFTER:**
```yaml
- rule_id: CORE-008
  principle: "Red-Green-Refactor Discipline"
  book_reference: "Test-Driven Development: By Example by Kent Beck"
  category: code_quality
  severity: blocked
```

---

## ✅ Stage 1: YAML Enhancement (COMPLETE)

**What:** Added `book_reference` metadata to 33 CORE rules  
**Files Changed:** `cortex_brain/tier0/governance/core-rules.yaml`  
**Commits:**
- `feat(governance): Add book references to CORE rules (batch 1/4)` (29000c076)
- `feat(governance): Add book reference to CORE-020` (3344fc2b9)
- `feat(governance): Add book references to CORE rules (batch 2/2)` (0fb89b5e3)

**Book Mappings (21 Unique Titles):**

| CORE Rule | Book Reference |
|-----------|----------------|
| CORE-001, 002, 004, 005, 006, 030 | Good to Great by Jim Collins |
| CORE-008 | Test-Driven Development: By Example by Kent Beck |
| CORE-011 | Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin |
| CORE-012 | The Pragmatic Programmer by Andrew Hunt & David Thomas |
| CORE-013 | Effective Python by Brett Slatkin |
| CORE-017 | Domain-Driven Design by Eric Evans |
| CORE-018 | Continuous Delivery by Jez Humble & David Farley |
| CORE-019 | Accelerate: The Science of Lean Software and DevOps by Nicole Forsgren, Jez Humble, Gene Kim |
| CORE-020 | Extreme Programming Explained by Kent Beck |
| CORE-024 | Infrastructure as Code by Kief Morris |
| CORE-025, 028 | The Pragmatic Programmer by Andrew Hunt & David Thomas |
| CORE-026 | Site Reliability Engineering by Google (Betsy Beyer et al.) |
| CORE-027 | The Art of Monitoring by James Turnbull |
| CORE-029 | The DevOps Handbook by Gene Kim, Jez Humble, Patrick Debois, John Willis |
| CORE-032 | Good to Great by Jim Collins |
| CORE-034 | Measure What Matters by John Doerr |
| CORE-035 | The Phoenix Project by Gene Kim |
| CORE-038 | The Checklist Manifesto by Atul Gawande |
| CORE-039 | The Lean Startup by Eric Ries |
| CORE-040 | Building Evolutionary Architectures by Neal Ford, Rebecca Parsons, Patrick Kua |
| CORE-041 | Designing Data-Intensive Applications by Martin Kleppmann |
| CORE-042 | The Goal by Eliyahu Goldratt |
| AC-PERMANENT-FIX-006 | Lean Software Development by Mary & Tom Poppendieck |

---

## ⚪ Stage 2: Orchestrator Display Templates (TEAM TODO)

**Goal:** Make book references visible in VS Code Copilot Chat during DoR (Definition of Ready) displays.

### Key Files to Update

#### 1. **GovernanceRuleLoader** (`cortex/tools/cortex_brain_integration.py`)

**Current:** Loads rules from YAML  
**Enhancement:** Expose `book_reference` field when retrieving rules

```python
# Example usage (already works):
def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
    """Get a single rule by ID."""
    self._load_rules()
    rule = self._rules_cache.get(rule_id)
    # rule now contains book_reference field ✅
    return rule
```

#### 2. **EnforcementOrchestrator** (`cortex/orchestrators/core/enforcement_orchestrator.py`)

**Lines:** 1017-1060 (`validate_intent_classification`)  
**Enhancement:** Extract book references when displaying governance violations

**Suggested Enhancement:**
```python
def _format_governance_rule_with_book(self, rule_id: str) -> str:
    """Format governance rule with book reference for display."""
    from cortex.tools.cortex_brain_integration import GovernanceRuleLoader
    
    loader = GovernanceRuleLoader()
    rule = loader.get_rule_by_id(rule_id)
    
    if not rule:
        return rule_id
    
    principle = rule.get("principle", "")
    book_ref = rule.get("book_reference", "")
    
    if book_ref:
        return f"**{principle}** → {rule_id} ({book_ref})"
    return f"**{principle}** → {rule_id}"

# Usage in validation messages:
for rule_id in governance_rules:
    formatted = self._format_governance_rule_with_book(rule_id)
    # Display: **Red-Green-Refactor Discipline** → CORE-008 (Test-Driven Development by Kent Beck)
```

#### 3. **Intent Classification Display** (Location TBD - needs discovery)

**Search Pattern:**
```bash
# Find where DoR displays business principles:
grep -r "business_principles" --include="*.py" cortex/
grep -r "to_markdown" --include="*.py" cortex/orchestrators/
```

**Expected Location:** File that generates markdown for Copilot Chat DoR displays

**Enhancement Pattern:**
```python
def format_dor_display(self, intent_reflection: Dict[str, Any]) -> str:
    """Format DoR display with business wisdom."""
    governance_rules = intent_reflection.get("governance_rules", [])
    
    # Load book references for each rule
    loader = GovernanceRuleLoader()
    enriched_rules = []
    
    for rule_id in governance_rules:
        rule = loader.get_rule_by_id(rule_id)
        if rule:
            principle = rule.get("principle", "")
            book_ref = rule.get("book_reference", "")
            enriched_rules.append(
                f"**{principle}** → {rule_id} ({book_ref})"
            )
    
    # Format as markdown panel
    markdown = "### 📚 Business Wisdom\n\n"
    for enriched in enriched_rules[:5]:  # Max 5 rules
        markdown += f"- {enriched}\n"
    
    return markdown
```

---

## ⚪ Stage 3: Response Format Standards (TEAM TODO)

**Goal:** Document markdown panel templates for consistent business wisdom display.

### File to Create/Update

**Location:** `.github/prompts/response-format-standards.md`

**Template to Add:**

````markdown
## Business Wisdom Panel Template

When displaying governance rules (CORE-XXX) in Copilot Chat, enrich with book references:

### Standard Format

```
### 📚 Business Wisdom (Governance Context)

- **Red-Green-Refactor Discipline** → CORE-008 (Test-Driven Development by Kent Beck)
- **Principle of Least Knowledge** → CORE-011 (Clean Code by Robert C. Martin)
- **Executable Documentation** → CORE-012 (The Pragmatic Programmer by Hunt & Thomas)
```

### Usage Guidelines

1. **Max 5 principles** per display (avoid overwhelming user)
2. **Bold principle names** for visual hierarchy
3. **Arrow notation (→)** for principle-to-rule mapping
4. **Parenthetical book reference** for authority/credibility
5. **Order by severity** (P0 → P1 → P2) or **alphabetical** by principle

### Example in DoR Display

```
# 🧠 CORTEX
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---

### ✅ Definition of Ready (DoR)

| Field | Value |
|-------|-------|
| **Intent** | IMPLEMENT |
| **Handler** | TDDOrchestrator |
| **Confidence** | 0.92 |
| **Scope** | MODULE |

### 📚 Business Wisdom

- **Red-Green-Refactor Discipline** → CORE-008 (Test-Driven Development by Kent Beck)
- **Principle of Least Knowledge** → CORE-011 (Clean Code by Robert C. Martin)
- **Executable Documentation** → CORE-012 (The Pragmatic Programmer by Hunt & Thomas)

**Proceed?** (yes/no/clarify)
```
````

---

## 🔧 How Team Members Use This

### For Developers Pulling This Work

**1. Pull latest from `origin/CORTEX`:**
```bash
git pull origin CORTEX
```

**2. Verify YAML changes:**
```bash
# Check that book_reference fields exist
grep -A 1 "book_reference" cortex_brain/tier0/governance/core-rules.yaml | head -20
```

**Expected Output:**
```yaml
book_reference: "Good to Great by Jim Collins"
--
book_reference: "Good to Great by Jim Collins"
--
book_reference: "Good to Great by Jim Collins"
```

**3. Test governance rule loading:**
```python
# In Python shell or test:
from cortex.tools.cortex_brain_integration import GovernanceRuleLoader

loader = GovernanceRuleLoader()
rule = loader.get_rule_by_id("CORE-008")

print(rule.get("principle"))         # "Red-Green-Refactor Discipline"
print(rule.get("book_reference"))    # "Test-Driven Development: By Example by Kent Beck"
```

**4. Implement Stage 2 (orchestrator display):**
- See "Stage 2: Orchestrator Display Templates" above
- Target files: `enforcement_orchestrator.py`, DoR display logic
- Estimated effort: 4 hours

**5. Document Stage 3 (response format standards):**
- Create/update `.github/prompts/response-format-standards.md`
- Add business wisdom panel template
- Estimated effort: 1 hour

---

## 📊 Verification Checklist

### Stage 1 (Complete) ✅
- [x] All 33 CORE rules have `book_reference` field
- [x] 21 unique book titles referenced
- [x] YAML formatting preserved (no governance check failures)
- [x] Changes committed to `origin/CORTEX`
- [x] Git history clean (4 commits)

### Stage 2 (Pending) ⚪
- [ ] `EnforcementOrchestrator` displays book references in violations
- [ ] DoR markdown includes business wisdom panel
- [ ] Governance rule display enriched with books
- [ ] Maximum 5 principles displayed (avoid clutter)
- [ ] Tests added for book reference display

### Stage 3 (Pending) ⚪
- [ ] Response format standards documented
- [ ] Markdown panel template created
- [ ] Usage guidelines written
- [ ] Example DoR displays updated

---

## 🎯 Expected User Experience (After Stage 2-3)

### BEFORE (Current)
```
### ✅ Definition of Ready (DoR)

Governance Rules: CORE-008, CORE-011, CORE-012
```

### AFTER (Target)
```
### ✅ Definition of Ready (DoR)

### 📚 Business Wisdom

- **Red-Green-Refactor Discipline** → CORE-008 (Test-Driven Development by Kent Beck)
- **Principle of Least Knowledge** → CORE-011 (Clean Code by Robert C. Martin)
- **Executable Documentation** → CORE-012 (The Pragmatic Programmer by Hunt & Thomas)
```

**Impact:** Users see WHY rules exist (business wisdom context) instead of just WHAT rules apply (IDs).

---

## 🔗 Related Files

### Modified
- `cortex_brain/tier0/governance/core-rules.yaml` (1814 lines, 33 rules enhanced)

### To Implement (Stage 2)
- `cortex/tools/cortex_brain_integration.py` (GovernanceRuleLoader)
- `cortex/orchestrators/core/enforcement_orchestrator.py` (Line 1017+)
- **Location TBD:** DoR markdown display logic (needs discovery)

### To Create (Stage 3)
- `.github/prompts/response-format-standards.md` (business wisdom panel template)

---

## 🎓 Learning Value

**For Users:**
- **Authority:** Book references lend credibility to rules
- **Learning Path:** Users can read referenced books for deeper understanding
- **Context:** Principles (flywheel effect, hedgehog concept) are more memorable than rule IDs

**For Team:**
- **Metadata Extension Pattern:** Shows how to add rich metadata to governance rules
- **Display Layer Separation:** YAML data → orchestrator logic → markdown formatting
- **Tier 0 Immutability:** Book references don't change rule behavior, only enhance display

---

## 🚀 Next Actions

### Immediate (Stage 2 - 4 hours)
1. **Discover DoR display location** (grep for `to_markdown`, `business_principles`)
2. **Update `EnforcementOrchestrator`** to format rules with books
3. **Test in Copilot Chat** (/implement command should show enriched DoR)
4. **Add unit tests** (e.g., `test_book_reference_display.py`)
5. **Commit changes** to CORTEX branch

### Follow-up (Stage 3 - 1 hour)
1. **Create response format standards doc** (markdown panel template)
2. **Add usage examples** (before/after screenshots in doc comments)
3. **Update copilot-instructions.md** (reference business wisdom display)

### Optional (Future Enhancement)
1. **Interactive Book Browser:** MCP tool to list all books + CORE rules
2. **Reading List Generator:** Create prioritized reading list based on user's common violations
3. **Principle Search:** Find CORE rules by business principle keyword

---

## 📞 Questions?

**Contact:** Asif Hussain  
**Branch:** `CORTEX` (origin/CORTEX)  
**Commits:** 29000c076, 3344fc2b9, 0fb89b5e3  
**Related Enhancement:** Phase 38.0 (Business Wisdom Integration)

---

**Status:** Stage 1 ✅ COMPLETE | Stages 2-3 ⚪ READY FOR TEAM
