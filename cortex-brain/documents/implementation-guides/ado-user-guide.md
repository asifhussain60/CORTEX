# CORTEX ADO Integration - User Guide

**Author:** Asif Hussain  
**Version:** 1.0  
**Date:** November 26, 2025

---

## 🎯 What is ADO Integration?

CORTEX now provides seamless Azure DevOps (ADO) integration, allowing you to:
- Create structured work items (user stories, features) directly from chat
- Track implementation progress with automatic file and decision tracking
- Generate ADO-formatted summaries for direct copy-paste into ADO work items
- Run code reviews with ADO-ready reports

**Key Benefit:** No more manual work item documentation. CORTEX tracks everything and generates professional summaries automatically.

---

## 🚀 Quick Start

### Example 1: Create a User Story

**You say:**
```
plan ado story
```

**CORTEX responds:**
```
📋 Creating User Story

Please provide:
1. Title: What feature or capability?
2. Description: As a [user], I want [feature], so that [benefit]
3. Acceptance Criteria (optional): What must be done?
4. Priority: High/Medium/Low/Very Low
```

**You provide:**
```
Title: User login with email and password
Description: As a registered user, I want to log in with my email and password so that I can access my account securely.
Criteria:
- Login form accepts email and password
- Invalid credentials show error message
- Successful login redirects to dashboard
Priority: High
```

**CORTEX creates:**
- Work item file in `cortex-brain/documents/planning/ado/active/UserStory-20251126143025-user-login.md`
- Opens file in VS Code for review
- Provides work item ID: `UserStory-20251126143025`

**During Implementation:**

As you work, update the work item file:
- Add files created to "Files Changed > Created" section
- Add files modified to "Files Changed > Modified" section
- Add tests to "Files Changed > Tests" section
- Document technical decisions
- Check off acceptance criteria as you complete them

### Example 2: Generate Work Summary

**After completing your work, you say:**
```
generate ado summary UserStory-20251126143025
```

**CORTEX generates:**
- Complete summary with all tracked information
- ADO-formatted markdown ready for copy-paste
- Saves to `cortex-brain/documents/summaries/ado/SUMMARY-UserStory-20251126143025-[timestamp].md`
- Opens summary file in VS Code

**Summary includes:**
```markdown
# Summary of Work Completed

## User Story: User Login with Email and Password
**Work Item ID:** UserStory-20251126143025
**Status:** Completed
**Priority:** High

---

## Files Changed

### Created (3 files)
- `src/auth/LoginComponent.tsx` - Login UI component
- `src/services/AuthService.ts` - Authentication service
- `tests/auth/LoginComponent.test.tsx` - Component tests

### Modified (2 files)
- `src/routes/AppRoutes.tsx` - Added login route
- `src/App.tsx` - Updated navigation

### Tests (1 file)
- `tests/auth/LoginComponent.test.tsx` - 12 tests, 100% coverage

**Total:** 3 created, 2 modified, 1 test file

---

## Implementation Details

...
```

**Copy-Paste to ADO:**
1. Select content from "Summary of Work Completed" to end
2. Copy (Cmd+C / Ctrl+C)
3. Open your ADO work item
4. Paste into Description or add as Comment
5. Update work item status to Done/Resolved

---

## 📚 Natural Language Commands

### User Story Commands

| You Say | CORTEX Does |
|---------|-------------|
| `plan ado story` | Creates new user story with interactive template |
| `create ado story` | Same as above |
| `new user story` | Same as above |

### Feature Commands

| You Say | CORTEX Does |
|---------|-------------|
| `plan ado feature` | Creates new feature with story linking |
| `create ado feature` | Same as above |
| `new ado feature` | Same as above |

### Summary Commands

| You Say | CORTEX Does |
|---------|-------------|
| `generate ado summary [ID]` | Generates copy-paste ready summary for work item |
| `create work summary [ID]` | Same as above |
| `ado work summary [ID]` | Same as above |
| `complete ado work [ID]` | Same as above |

### Code Review Commands

| You Say | CORTEX Does |
|---------|-------------|
| `code review [PR URL]` | Analyzes PR and generates ADO-formatted review |
| `review pr [PR URL]` | Same as above |
| `pull request review [PR URL]` | Same as above |

---

## 📋 Work Item Template Structure

When CORTEX creates a work item, it uses this template:

```markdown
# UserStory: [Title]

**Work Item ID:** UserStory-20251126143025
**Type:** User Story
**Priority:** High
**Created:** 2025-11-26 14:30:25
**Status:** Active

---

## Description
As a registered user, I want to log in with my email and password 
so that I can access my account securely.

---

## Acceptance Criteria
1. [ ] Login form accepts email and password
2. [ ] Invalid credentials show error message
3. [ ] Successful login redirects to dashboard
4. [ ] Session persists for 30 minutes

---

## Implementation Notes
[Add notes as you implement]

---

## Files Changed

### Created
- file1.tsx
- file2.ts

### Modified
- existing_file.tsx

### Tests
- test_file.test.tsx

---

## Technical Decisions
- Decision 1: Used JWT for session management (more secure than cookies)
- Decision 2: Implemented rate limiting (prevent brute force attacks)

---

## Related Work Items
[Link related stories/features here]

---

## Tags
`authentication`, `security`, `login`
```

---

## 🎯 Workflow Examples

### Complete Feature Development Workflow

**Day 1: Planning**
```
You: plan ado feature

CORTEX: [Asks for feature details]

You: 
Title: User Authentication System
Description: Complete authentication with login, registration, password reset
Related Stories: 
- User login (will create next)
- User registration (will create next)
Priority: High
Duration: 2 weeks

CORTEX: ✅ Feature created: Feature-20251126150000
```

**Day 1: Create First Story**
```
You: plan ado story

CORTEX: [Asks for story details]

You:
Title: User Login
Description: As a user, I want to log in...
Related Feature: Feature-20251126150000
Priority: High

CORTEX: ✅ Story created: UserStory-20251126150500
```

**Days 2-3: Implementation**

*Update work item file as you work:*
- Add files created/modified
- Document decisions
- Check off criteria

**Day 3: Completion**
```
You: generate ado summary UserStory-20251126150500

CORTEX: ✅ Summary generated and ready for copy-paste
```

*Copy summary to ADO and mark story Done*

**Week 2: Feature Complete**
```
You: generate ado summary Feature-20251126150000

CORTEX: ✅ Feature summary with all stories and metrics
```

---

## 💡 Pro Tips

### 1. Update Work Items Regularly

✅ **Good Practice:**
```
Every time you create/modify a file, immediately update the work item:
- Add to Files Changed section
- Note why you made the change
```

❌ **Bad Practice:**
```
Wait until end to update work item (you'll forget details)
```

### 2. Document Technical Decisions

✅ **Good:**
```
Technical Decisions:
- Used Redux Toolkit instead of Context API: Better performance for large state
- Implemented JWT refresh tokens: Improve UX with persistent sessions
- Added rate limiting to login: Prevent brute force attacks (OWASP recommendation)
```

❌ **Bad:**
```
Technical Decisions:
- Various implementation choices
```

### 3. Check Off Acceptance Criteria

✅ **As you complete each criterion:**
```
## Acceptance Criteria
1. [x] Login form accepts email and password ← Change [ ] to [x]
2. [x] Invalid credentials show error message
3. [ ] Successful login redirects to dashboard ← Still working on this
```

### 4. Use Work Item IDs in Commit Messages

```bash
git commit -m "UserStory-20251126150500: Implement login form validation"
```

This creates traceability from code → commit → work item.

---

## 🔧 Advanced Features

### Custom Priorities

When creating work items, you can use:
- `Very High` - Urgent/blocking
- `High` - Important, do soon
- `Medium` - Standard priority (default)
- `Low` - Nice to have
- `Very Low` - Backlog item

### Tags for Organization

Add tags to work items for easy filtering:
```
Tags: `authentication`, `security`, `frontend`, `api`
```

### Linking Work Items

Reference other work items:
```
Related Work Items:
- Feature-20251126150000 (parent feature)
- Bug-20251125120000 (blocked by this fix)
```

---

## 📊 Summary Contents

Every ADO summary includes:

1. **Header** - Title, ID, status, priority
2. **Files Changed** - Created, modified, tested (with counts)
3. **Implementation Details** - What you built, how it works
4. **Technical Decisions** - Architecture choices and rationale
5. **Acceptance Criteria Validation** - ✅ for completed items
6. **Copy-Paste Instructions** - How to use the summary in ADO

---

## 🎓 Training Scenario

**Scenario:** You need to add a "Remember Me" checkbox to the login page.

**Step 1: Create Story**
```
You: plan ado story

You: 
Title: Remember Me functionality on login
Description: As a user, I want a "Remember Me" checkbox so my session persists for 7 days
Criteria:
- Checkbox appears on login form
- Checked = 7-day session, unchecked = 30-min session
- Preference saved in secure cookie
Priority: Medium
Tags: authentication, ux-improvement

CORTEX: ✅ Story created: UserStory-20251126160000
```

**Step 2: Implement**

*Make your code changes, then update work item file:*
```markdown
## Files Changed

### Created
- None

### Modified
- `src/auth/LoginForm.tsx` - Added Remember Me checkbox
- `src/services/AuthService.ts` - Updated session logic for 7-day persistence
- `src/auth/LoginForm.css` - Styled checkbox

### Tests
- `tests/auth/LoginForm.test.tsx` - Added 3 new tests for Remember Me behavior

## Technical Decisions
- Used secure, HttpOnly cookie for Remember Me token (prevent XSS)
- Implemented separate refresh token for long sessions (security best practice)
- Token rotation every 24 hours (balance security and UX)
```

**Step 3: Generate Summary**
```
You: generate ado summary UserStory-20251126160000

CORTEX: ✅ Summary generated with all details
```

**Step 4: Paste to ADO**

*Copy summary, paste to ADO work item, mark Done*

**Done!** 🎉

---

## 🆘 Troubleshooting

### Problem: "Work item ID required"

**Solution:** When generating summaries, always provide the work item ID:
```
generate ado summary UserStory-20251126160000
```

### Problem: Summary has incomplete information

**Solution:** Check work item file - did you fill in all sections?
- Files Changed (created, modified, tests)
- Implementation Notes
- Technical Decisions
- Acceptance Criteria (check them off!)

### Problem: Can't find work item file

**Solution:** Files are saved in:
```
cortex-brain/documents/planning/ado/active/[WorkItemID].md
```

Use VS Code file explorer or say "where is UserStory-20251126160000"

### Problem: Want to edit work item after creation

**Solution:** Just open the file in VS Code and edit directly:
1. Navigate to `cortex-brain/documents/planning/ado/active/`
2. Find your work item file
3. Edit any section
4. Save (Cmd+S / Ctrl+S)

---

## 📞 Need Help?

**Say to CORTEX:**
- `help with ado integration` - This guide
- `ado example` - See example workflow
- `where is my work item [ID]` - Find work item file
- `ado troubleshooting` - Common issues and solutions

---

## ✅ Quick Reference Card

| Task | Command | Output |
|------|---------|--------|
| Create story | `plan ado story` | Interactive story creation |
| Create feature | `plan ado feature` | Interactive feature creation |
| Generate summary | `generate ado summary [ID]` | Copy-paste ready summary |
| Code review | `code review [PR URL]` | ADO-formatted review report |
| Find work item | Check `cortex-brain/documents/planning/ado/active/` | Markdown file |
| Get help | `help with ado integration` | This guide |

---

**Version:** 1.0  
**Last Updated:** November 26, 2025  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
