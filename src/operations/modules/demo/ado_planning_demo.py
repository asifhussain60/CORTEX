"""
ADO Planning Demo Script

Interactive demonstration of ADO work item planning with git history integration.
Shows complete workflow: create work item → git enrichment → template generation → result display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime


class ADOPlanningDemo:
    """
    Interactive demonstration of ADO work item planning.
    
    Shows Phase 1 git history integration features:
    - Quality scoring (0-100%)
    - High-risk file detection
    - SME identification
    - Related commits and contributors
    """
    
    def __init__(self, cortex_root: Path):
        """
        Initialize ADO planning demo.
        
        Args:
            cortex_root: Path to CORTEX repository root
        """
        self.cortex_root = cortex_root
        self.logger = logging.getLogger(__name__)
        
    def run_demo(self) -> Dict[str, Any]:
        """
        Run complete ADO planning demonstration.
        
        Returns:
            Demo results with examples and explanations
        """
        self.logger.info("Starting ADO planning demonstration")
        
        return {
            'success': True,
            'demo_sections': [
                self._section_introduction(),
                self._section_before_phase1(),
                self._section_after_phase1(),
                self._section_quality_scoring(),
                self._section_high_risk_detection(),
                self._section_sme_identification(),
                self._section_try_it_yourself()
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _section_introduction(self) -> Dict[str, Any]:
        """Introduction to ADO planning with git integration"""
        return {
            'title': '📋 ADO Work Item Planning Demo',
            'content': """
## Welcome to ADO Planning with Git History Integration!

This demo shows how CORTEX automatically enriches Azure DevOps work items with:
- **Quality scoring** based on git history depth
- **High-risk file detection** from churn patterns
- **SME identification** from contributor analysis
- **Related context** from recent commits

**Duration:** 5-7 minutes  
**Interactive:** Yes - you'll create a real work item at the end!
""",
            'type': 'introduction'
        }
    
    def _section_before_phase1(self) -> Dict[str, Any]:
        """Show work item BEFORE git integration"""
        return {
            'title': '❌ Before Phase 1 (No Git Integration)',
            'content': """
## Traditional Work Item Creation

When you created a work item before Phase 1, you got basic structure only:

```markdown
# User Story: Fix authentication bug

**Work Item ID:** UserStory-20251127143022  
**Priority:** Medium  
**Status:** Active

## Description
Bug in authentication system causing login failures

## Acceptance Criteria
1. [ ] Must pass all tests
2. [ ] Bug must be fixed
3. [ ] Documentation updated

## Related Work Items
None

## Tags
bug, authentication
```

**Problems:**
- ❌ No git history context
- ❌ No awareness of file risk levels
- ❌ No SME guidance for assignment
- ❌ No related commit visibility
- ❌ Generic acceptance criteria
- ❌ Missing critical context for developers
""",
            'type': 'before_example'
        }
    
    def _section_after_phase1(self) -> Dict[str, Any]:
        """Show work item AFTER git integration"""
        return {
            'title': '✅ After Phase 1 (Git Integration Active)',
            'content': """
## Enhanced Work Item with Git Context

Same work item with Phase 1 git history integration:

```markdown
# User Story: Fix authentication bug

**Work Item ID:** UserStory-20251127143022  
**Priority:** Medium  
**Status:** Active

## Description
Bug in `src/auth/login.py` causing login failures for OAuth users

## Acceptance Criteria
1. [ ] ⚠️ Review high-risk files: src/auth/login.py, src/auth/oauth.py
2. [ ] Must pass all existing authentication tests
3. [ ] Add specific tests for OAuth edge cases
4. [ ] Security review required (recent vulnerability fixes)
5. [ ] Bug must be fixed without breaking session management

---

## Git History Context

**Quality Score:** 85.5% (Good)

**⚠️ High-Risk Files Detected:**
- `src/auth/login.py` - Requires extra attention
  - **Churn:** 18 commits in last 6 months (threshold: 15)
  - **Hotfixes:** 4 emergency fixes (threshold: 3)
  - **Recent Security Fix:** 12 days ago

- `src/auth/oauth.py` - Moderate risk
  - **Churn:** 12 commits in last 6 months
  - **Complexity:** High coupling with login module

**💡 Subject Matter Expert Suggestions:**
- **John Doe** (top contributor to authentication module)
  - 42 commits to `src/auth/login.py`
  - Author of recent security fixes
  - Recommended for code review assignment

**Contributors to Related Files:**
- John Doe (42 commits) - Primary maintainer
- Jane Smith (28 commits) - Security specialist
- Bob Wilson (15 commits) - OAuth integration
- Alice Johnson (8 commits) - Testing
- Charlie Brown (5 commits) - Documentation

**Related Commits:**
- `abc123` (2024-11-15): Fix critical authentication vulnerability in OAuth flow
- `def456` (2024-11-10): Refactor session management for better security
- `ghi789` (2024-11-05): Add comprehensive unit tests for auth edge cases
- `jkl012` (2024-10-28): Implement rate limiting for login attempts
- `mno345` (2024-10-20): Update authentication documentation and examples
```

**Benefits:**
- ✅ Rich git history context included
- ✅ High-risk files automatically flagged
- ✅ SME suggested for assignment (John Doe)
- ✅ Related commits provide context
- ✅ Informed acceptance criteria (security review, OAuth tests)
- ✅ Contributors visible for collaboration
- ✅ Quality score shows git history health
""",
            'type': 'after_example'
        }
    
    def _section_quality_scoring(self) -> Dict[str, Any]:
        """Explain quality scoring system"""
        return {
            'title': '📊 Quality Scoring Explained',
            'content': """
## Git History Quality Score (0-100%)

The quality score indicates the depth and quality of git history for related files.

### Score Ranges

**90-100% (Excellent)** 🟢
- Deep git history (50+ commits)
- Active contributors (5+ people)
- Recent activity (commits within 30 days)
- Comprehensive documentation
- Strong test coverage evident

**70-89% (Good)** 🟡
- Solid history (20-49 commits)
- Multiple contributors (3-4 people)
- Regular activity (commits within 90 days)
- Decent documentation
- Some test coverage

**50-69% (Adequate)** 🟠
- Basic history (10-19 commits)
- Few contributors (1-2 people)
- Occasional activity (commits within 180 days)
- Minimal documentation
- Limited tests

**< 50% (Weak)** 🔴
- Sparse history (< 10 commits)
- Single contributor
- Stale (no commits in 180+ days)
- No documentation
- No tests

### What It Means

**High Score (70-100%):**
- Well-maintained files with active community
- Good context available for changes
- Lower risk of unexpected issues
- Strong knowledge base

**Low Score (< 50%):**
- Newer files or legacy code
- Limited context for changes
- Higher risk of hidden dependencies
- Consider pairing with experienced developer

### Example Calculation

For `src/auth/login.py`:
- Recent commits: 18 in 6 months (30 points)
- Contributors: 5 people (25 points)
- Recent activity: 12 days ago (20 points)
- Security scans: Pass (10 points)
- **Total: 85% (Good)**
""",
            'type': 'explanation'
        }
    
    def _section_high_risk_detection(self) -> Dict[str, Any]:
        """Explain high-risk file detection"""
        return {
            'title': '⚠️ High-Risk File Detection',
            'content': """
## How CORTEX Identifies High-Risk Files

High-risk files require extra attention during development. CORTEX automatically flags them based on:

### Detection Criteria

**1. High Churn (> 15 commits in 6 months)**
- File changes frequently
- Indicates complexity or instability
- Higher chance of merge conflicts
- May need refactoring

**2. Hotfix Pattern (> 3 emergency fixes)**
- Multiple urgent fixes applied
- Suggests underlying design issues
- May have hidden edge cases
- Consider comprehensive refactor

**3. Recent Security Fix (< 30 days)**
- Security vulnerability recently patched
- Requires security review for changes
- Test security scenarios thoroughly
- Consult security team

**4. High Complexity**
- Large file size (> 500 lines)
- Many dependencies
- Complex logic patterns
- Difficult to test

### What Happens When Flagged

When a file is flagged as high-risk:

1. **Auto-Added to Acceptance Criteria:**
   ```markdown
   1. [ ] ⚠️ Review high-risk files: src/auth/login.py
   ```

2. **Detailed Warning in Git Context:**
   ```markdown
   **⚠️ High-Risk Files Detected:**
   - `src/auth/login.py` - Requires extra attention
     - **Churn:** 18 commits in last 6 months (threshold: 15)
     - **Hotfixes:** 4 emergency fixes (threshold: 3)
     - **Recent Security Fix:** 12 days ago
   ```

3. **Recommended Actions:**
   - Assign to experienced developer (SME suggestion provided)
   - Require code review from 2+ people
   - Add comprehensive test coverage
   - Consider pair programming
   - Document changes thoroughly

### Example: Authentication Module

```python
# src/auth/login.py - HIGH RISK
# Churn: 18 commits (6 months)
# Hotfixes: 4 emergency patches
# Last security fix: 12 days ago
# Complexity: High (OAuth, session, tokens)

def authenticate_user(username, password):
    # Complex authentication logic
    # Multiple failure points
    # Security-critical code
    pass
```

**Risk Factors:**
- ✅ High churn detected (18 > 15)
- ✅ Hotfix pattern detected (4 > 3)
- ✅ Recent security fix (12 days < 30)
- ✅ Security-critical function

**Recommendation:** Treat as high-risk, require security review
""",
            'type': 'explanation'
        }
    
    def _section_sme_identification(self) -> Dict[str, Any]:
        """Explain SME identification"""
        return {
            'title': '💡 SME Identification System',
            'content': """
## Subject Matter Expert (SME) Identification

CORTEX automatically identifies the best person to work on or review your changes.

### How It Works

**1. Contributor Analysis**
```bash
git shortlog -sn -- src/auth/login.py
```
Extracts:
- Commit counts per contributor
- File ownership patterns
- Recent activity

**2. Ranking Algorithm**
- **Primary factor:** Commit count to specific files
- **Secondary factor:** Recent activity (recency bonus)
- **Tertiary factor:** Related file expertise

**3. SME Suggestion**
Top contributor becomes SME suggestion:
```markdown
**💡 Subject Matter Expert Suggestions:**
- **John Doe** (top contributor to authentication module)
  - 42 commits to `src/auth/login.py`
  - Author of recent security fixes
  - Recommended for code review assignment
```

### Benefits

**For Work Assignment:**
- Auto-suggests best person for `assigned_to` field
- Reduces assignment decision time
- Improves code quality (expert handles complex areas)

**For Code Review:**
- Identifies who should review PR
- Ensures knowledgeable reviewer
- Faster review cycles

**For Knowledge Transfer:**
- New team members know who to ask
- Documentation of expertise
- Prevents knowledge silos

### Example: Authentication Module

**Contributors (from git history):**
1. John Doe - 42 commits (48%)
2. Jane Smith - 28 commits (32%)
3. Bob Wilson - 15 commits (17%)
4. Alice Johnson - 3 commits (3%)

**Analysis:**
- **Primary SME:** John Doe (clear majority, 48%)
- **Backup SME:** Jane Smith (significant contributor, 32%)
- **Specialized:** Bob Wilson (OAuth focus based on commit messages)

**Recommendation:**
- **Assign to:** John Doe (primary maintainer)
- **Review by:** Jane Smith (security expertise)
- **Consult:** Bob Wilson (if OAuth-related)

### Auto-Population (Future Phase)

Phase 2 will auto-populate `assigned_to` field:
```yaml
work_item:
  assigned_to: "John Doe"  # Auto-suggested from git history
  reviewers:
    - "Jane Smith"         # Security review
    - "Bob Wilson"         # OAuth expertise
```
""",
            'type': 'explanation'
        }
    
    def _section_try_it_yourself(self) -> Dict[str, Any]:
        """Interactive section for user to try"""
        return {
            'title': '🚀 Try It Yourself!',
            'content': """
## Create Your Own ADO Work Item

Ready to see git history integration in action?

### Step 1: Choose Work Item Type

Say one of:
- `create user story` - For feature work
- `create bug` - For defect fixes
- `create task` - For standalone work
- `create feature` - For large initiatives

### Step 2: Describe Work Item

Include file references in backticks for git context:

**Example 1: Bug Fix**
```
Fix authentication bug in `src/auth/login.py` where OAuth users 
cannot log in after session timeout.
```

**Example 2: Feature**
```
Add password reset functionality to `src/auth/password.py` with 
email verification and rate limiting.
```

**Example 3: Refactoring**
```
Refactor `src/orchestrators/ado_work_item_orchestrator.py` to 
improve git context enrichment performance.
```

### Step 3: Review Generated Work Item

You'll see:
- ✅ Quality score for git history
- ✅ High-risk file warnings (if applicable)
- ✅ SME suggestions for assignment
- ✅ Related commits and contributors
- ✅ Enhanced acceptance criteria

### Quick Commands

**Full ADO Workflow:**
```
plan ado
```

**Just Demo ADO:**
```
demo ado planning
```

**Show Phase 1 Report:**
```
show file cortex-brain/documents/reports/ADO-GIT-HISTORY-INTEGRATION-PHASE-1-COMPLETE.md
```

**Run Integration Tests:**
```
pytest tests/orchestrators/test_ado_git_integration.py -v
```

### What's Next?

**Phase 2 (Coming Soon):**
- YAML file generation for machine-readable format
- Resume capability with `resume ado [work-item-id]`
- Status tracking (active/completed/blocked)

**Phase 3 (Planned):**
- Interactive clarification with multi-round conversation
- Letter-based choice system (1a, 2c, 3b)
- Challenge-and-clarify prompts

**Phase 4 (Planned):**
- Automated DoR/DoD validation
- Quality scoring for requirements
- Approval workflow with quality gates

---

**Ready to try?** Say `plan ado` to create your first git-enhanced work item!
""",
            'type': 'interactive'
        }


def run_ado_planning_demo(cortex_root: Path) -> Dict[str, Any]:
    """
    Quick function to run ADO planning demonstration.
    
    Args:
        cortex_root: Path to CORTEX repository
        
    Returns:
        Demo results dictionary
    """
    demo = ADOPlanningDemo(cortex_root)
    return demo.run_demo()
