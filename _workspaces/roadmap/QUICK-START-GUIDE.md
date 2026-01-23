# CORTEX Roadmap - Quick Start Guide
**Date:** January 24, 2026  
**Purpose:** Get started using the roadmap quickly  
**Target Audience:** All team members

---

## 🚀 5-Minute Quick Start

### For Your Daily Work

1. **At 9:00 AM**: Open `standup_template` section in roadmap
   - Update: "Yesterday: what I accomplished"
   - Plan: "Today: what I'll do"
   - Log: "Blockers: what's preventing progress"

2. **Throughout Day**: Track metrics
   - Token usage: Real-time in dashboard
   - Tests passing: Check CI/CD pipeline
   - Phase progress: Mark what you completed

3. **At 4:45 PM**: End-of-day standup
   - Same template as morning
   - Update phase completion percentage
   - Log any issues discovered

### For Your Phase Work

1. **Phase Kickoff**: Reference `phase_planning_and_execution_templates`
   - Review objectives and success criteria
   - Understand architecture and design
   - Confirm test strategy and timeline

2. **During Phase**: Follow daily operations in `operational_runbooks`
   - Morning: Start of day checklist
   - Hourly: Health check
   - Evening: End of day standup
   - Weekly: Retrospective

3. **Phase Completion**: Use `phase_completion_checklist`
   - Verify all acceptance criteria met
   - Confirm test pass rate (target: 100%)
   - Get code reviews (2+ reviewers required)
   - Verify governance compliance

### For Problem Solving

**If tests are failing:**
→ See `operational_runbooks` → `incident_response` → `build_failure_response`

**If you're blocked:**
→ Log in standup → Reference `phase_blockers_and_escalation` → Follow escalation path

**If you need architecture context:**
→ See `architecture_decision_records` → Find relevant ADR → Read rationale

**If you're unsure about a decision:**
→ Check `quick_reference` → Architecture patterns section

---

## 📍 Where to Find Everything

### By Task

| Task | Where to Look |
|------|---------------|
| Daily standup | `active_work_management` → `daily_standup_template` |
| Weekly retrospective | `active_work_management` → `weekly_retrospective_template` |
| Production incident | `operational_runbooks` → `incident_response` |
| Deployment | `operational_runbooks` → `deployment_procedures` |
| New phase kickoff | `phase_planning_and_execution_templates` → `new_phase_kickoff` |
| Architecture decision | `architecture_decision_records` |
| Risk escalation | `risk_management` → `contingency_execution` |
| Quality target | `quality_assurance_and_testing_strategy` → `test_coverage_goals` |
| Important dates | `quick_reference` → `important_dates` |
| Team structure | `resource_allocation_tracking` → `current_allocation` |

### By Role

**Project Manager**
- Dashboard: `quick_reference` → `key_dashboards`
- Status: `executive_summary` + real-time metrics
- Updates: `strategic_planning_and_prioritization`
- Risks: `risk_management`

**Engineer**
- Daily work: `operational_runbooks` → `daily_operations`
- Phase work: `phase_planning_and_execution_templates`
- Questions: `architecture_decision_records`
- Issues: `operational_runbooks` → `incident_response`

**Architect**
- Decisions: `architecture_decision_records`
- Guidance: `strategic_planning`
- Patterns: `operational_runbooks` → search "pattern"
- Constraints: `blocked_phases`

**Operations Team**
- Procedures: `operational_runbooks` (all sections)
- Handoff: `transition_to_operations`
- Dashboards: `quick_reference` → `key_dashboards`
- Escalation: `operational_runbooks` → `incident_response` → `escalation`

---

## 📊 Most Important Sections

### 🔴 Critical (Read First)
1. `executive_summary` - Current status
2. `quick_reference` - Everything at a glance
3. `operational_runbooks` → `incident_response` - For emergencies
4. `architecture_decision_records` - Why we made choices

### 🟡 Important (Read This Week)
5. `phase_planning_and_execution_templates` - Phase execution
6. `resource_allocation_tracking` - Who does what
7. `risk_management` - Known risks and mitigations
8. `strategic_planning_and_prioritization` - Where we're going

### 🟢 Reference (Use as Needed)
9. `operational_runbooks` - Daily procedures
10. `quality_assurance_and_testing_strategy` - Quality targets
11. `knowledge_and_documentation_management` - Docs location
12. `continuous_monitoring_and_metrics` - Metrics collection

---

## 🎯 Common Scenarios

### Scenario: I'm starting a new phase tomorrow
**Steps:**
1. Read `phase_planning_and_execution_templates` → `new_phase_kickoff_template`
2. Review related `architecture_decision_records` for context
3. Check `resource_allocation_tracking` for your team
4. Review `quality_assurance_and_testing_strategy` → `test_coverage_goals`
5. Set up daily standup using `daily_standup_template`

### Scenario: Production incident happened
**Steps:**
1. See `operational_runbooks` → `incident_response` → `production_incident_response`
2. Page on-call engineer (1 minute)
3. Create incident ticket with timestamp
4. Start incident war room call
5. Follow SLA target: <15 minutes from detection to stabilization
6. After resolved: document root cause, update risk register

### Scenario: Tests are failing
**Steps:**
1. Identify which tests are failing (CI/CD dashboard)
2. See `operational_runbooks` → `incident_response` → `build_failure_response`
3. Notify committer who broke it
4. Either fix in next commit or revert previous
5. SLA: <10 minutes from failure to fix/revert
6. If revert reverts: escalate to architect

### Scenario: Phase is falling behind schedule
**Steps:**
1. See `phase_planning_and_execution_templates` → `phase_mid_point_review`
2. Assess actual progress vs plan
3. If <50% done at midpoint: activate contingency
4. Options: add resources, reduce scope, improve communication
5. See `risk_management` → `contingency_execution`
6. Escalate if impact on critical path

### Scenario: I need architecture context
**Steps:**
1. See `architecture_decision_records`
2. Search for relevant decision (ADR-001 through ADR-004+)
3. Read: context, alternatives, rationale, consequences
4. If still unclear: ask architect during architecture review

### Scenario: I don't understand a decision
**Steps:**
1. Check `architecture_decision_records` for context
2. Check `quick_reference` → `architectural_patterns` for patterns
3. If pattern, see relevant consolidation example (CONS-001-011)
4. Ask in architecture review or code review

---

## 📈 Key Metrics You Should Track

### Daily
- ✅ Token usage (should match daily budget)
- ✅ Test pass rate (should be 100%)
- ✅ Commits to main (should be steady)

### Weekly
- ✅ Phase progress % (should be 20%+ of estimate)
- ✅ Velocity (hours/phase, should be consistent)
- ✅ Code quality (coverage, docstrings)
- ✅ Blockers (should be 0-1 at any time)

### Monthly
- ✅ Consolidation pattern efficiency (target: 40%+ savings)
- ✅ Test coverage (target: >95% new code)
- ✅ Breaking changes (target: 0)
- ✅ Governance compliance (target: 100%)

---

## 🚨 When to Escalate

### Escalate to Tech Lead
- Build is broken (within 10 minutes)
- Tests failing (within 1 hour)
- Phase falling behind (at mid-point review)

### Escalate to Architect
- Design decision needed
- Governance rule conflict
- Major scope change

### Escalate to Steering Committee
- Risk probability >60%
- Phase will impact other phases
- Resource constraint preventing delivery
- Token budget exceeded

---

## 🎓 Learning Paths

### If You're New to CORTEX

**Week 1:**
1. Read `executive_summary` (20 min)
2. Read `quick_reference` (10 min)
3. Read `architecture_decision_records` (30 min)
4. Attend knowledge transfer session: "Project Overview"

**Week 2:**
5. Read relevant `phase_planning_and_execution_templates`
6. Attend knowledge transfer session: "Architecture Deep Dive"
7. Start your first phase with buddy/mentor

**Week 3:**
8. Participate in weekly retrospective
9. Complete first phase or subphase
10. Attend knowledge transfer session: "Implementation Walkthrough"

### If You're Joining Operations Team

**Pre-Handoff (1 week before):**
1. Read `operational_runbooks` (all sections) - 2 hours
2. Review `transition_to_operations` checklist
3. Attend knowledge transfer session: "Deployment and Operations"

**Handoff Period (1 week):**
4. Operations runbooks review with implementation lead
5. Monitoring dashboards walkthrough
6. Alert rule review and testing
7. Incident response procedure drill
8. Escalation path verification

**After Handoff:**
9. Monitor 24/7 for first week (with implementation team backup)
10. Execute daily operations procedures
11. Weekly health check routine
12. Monthly archive and cleanup

---

## 🔧 Tools & Files You'll Need

### Essential Files
- `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/cortex-roadmap.yaml` - This roadmap
- `monitoring/cortex-phase-dashboard.yaml` - Metrics dashboard
- `roadmap/risk_tracking.yaml` - Risk register
- `roadmap/phase_progress.yaml` - Phase tracking

### Daily Work Files
- `roadmap/standup_notes_YYYY-MM-DD.md` - Daily standup notes
- `roadmap/phase_execution_plan.md` - Phase timeline (created per phase)
- `tests/` directory - Where to add tests
- `.github/workflows/` - CI/CD pipeline

### Important Dashboards
- CI/CD pipeline: Check test status before merging
- Metrics dashboard: Real-time progress and metrics
- Risk register: Known risks and mitigation status
- Monitoring: Post-deployment metrics

---

## ✅ Checklist for Getting Started

- [ ] Read `executive_summary` (understand current status)
- [ ] Review `quick_reference` (bookmark key locations)
- [ ] Read `architecture_decision_records` (understand why decisions made)
- [ ] Set up `daily_standup_template` (start using tomorrow)
- [ ] Join daily standup (9:00 AM daily)
- [ ] Set up alerts for critical dashboards
- [ ] Review relevant `phase_planning_templates` (before your phase starts)
- [ ] Attend knowledge transfer sessions (schedule with team lead)
- [ ] Ask questions (no dumb questions, this is complex!)

---

## 🤔 Frequently Asked Questions

**Q: How often should I update the roadmap?**
A: Daily standup notes, weekly phase tracking, monthly lessons learned. See `continuous_improvement_cycle`.

**Q: What if I find something wrong in the roadmap?**
A: Update it! This is a living document. Note the change date and reason.

**Q: How do I request a change to the plan?**
A: Bring to weekly retrospective or architecture review. See `strategic_planning` for prioritization.

**Q: What if I disagree with a decision?**
A: See `architecture_decision_records` for the rationale. If still disagree, discuss in architecture review.

**Q: How do I know what to work on?**
A: Check `strategic_planning_and_prioritization` for current priorities and current phase assignment.

**Q: What's the token budget for my phase?**
A: Check `quick_reference` → `token_budget_tracking` for allocation. See `active_work_management` for daily tracking.

**Q: How much time should a phase take?**
A: See the phase specification and historical data (CONS-001-011 for consolidation pattern, WIRE-001-012 for orchestrator wiring).

---

## 📞 Emergency Contacts

See `quick_reference` → `emergency_contacts` for who to call in emergencies.

---

## 🎉 You're Ready!

You now have everything you need to contribute effectively to CORTEX. 

**Next Steps:**
1. Bookmark this quick start guide
2. Attend knowledge transfer session matching your role
3. Reach out to your team lead with any questions
4. Attend tomorrow's standup at 9:00 AM
5. Start contributing! 🚀

Good luck! 💪
