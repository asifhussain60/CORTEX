INCREMENTAL_PLAN_GENERATION: Response Length Limit Prevention

Real incident (2025-11-18):
- User: "Create a complete migration yaml plan"
- Copilot generates 500+ line comprehensive YAML plan
- Response hits length limit: "Sorry, the response hit the length limit. Please rephrase your prompt."
- Plan truncated mid-content, unusable
- User frustrated by incomplete deliverable

Why This Happens:
- GitHub Copilot Chat has ~8K token response limit
- Comprehensive YAML plans easily exceed this (15-25K tokens typical)
- Single-response generation forces truncation
- No way to continue from truncation point

Incremental Generation Benefits:
1. **No Truncation**: Each response stays under limit
2. **Progressive Disclosure**: User sees plan build in real-time
3. **Review Opportunity**: Can adjust direction between phases
4. **File-Based**: Plan persists in file, not ephemeral chat
5. **Resumable**: Can pause and continue later

Implementation Pattern:

```python
# WRONG: Single response generation
def generate_comprehensive_plan():
    plan = {
        'phase_1': {...},  # 200 lines
        'phase_2': {...},  # 200 lines
        'phase_3': {...},  # 200 lines
        'phase_4': {...}   # 200 lines
    }
    return yaml.dump(plan)  # ❌ 800 lines exceeds limit

# CORRECT: Incremental file writing
def generate_plan_incrementally():
    # Response 1: Structure
    create_plan_file_with_metadata()
    return "✅ Plan file created: migration-plan.yaml"
    
    # Response 2: Phase 1
    append_phase_to_file(phase=1, details={...})
    return "✅ Phase 1 added (3-4 hours, 15 tasks)"
    
    # Response 3: Phase 2
    append_phase_to_file(phase=2, details={...})
    return "✅ Phase 2 added (4-5 hours, 20 tasks)"
    
    # Response 4: Remaining phases
    append_remaining_phases_to_file()
    return "✅ All phases complete. Plan ready for execution."
```

User Experience:

✅ GOOD (Incremental):
User: "Create migration plan"
Copilot: "✅ Created migration-plan.yaml with structure. Adding Phase 1..."
[writes to file]
Copilot: "✅ Phase 1 complete (15 tasks). Adding Phase 2..."
[writes to file]
Copilot: "✅ Phase 2 complete (20 tasks). Adding remaining phases..."
[writes to file]
Copilot: "✅ Migration plan complete. 4 phases, 70 tasks, 13-15 hours estimated."

❌ BAD (Single response):
User: "Create migration plan"
Copilot: [generates 800-line YAML in response]
Copilot: "Sorry, the response hit the length limit. Please rephrase your prompt."
User: "Ugh, now I have to ask again?"

Chat Response Format:
- Show progress: "✅ Phase 1/4 added"
- Show summary: "15 tasks, 3-4 hours"
- Reference file: "See migration-plan.yaml for full details"
- No full YAML dump in chat (file is source of truth)

File-Based Planning Advantages:
- Persistent artifact (survives chat closure)
- Git-trackable (version control)
- Resumable (open file anytime)
- Shareable (commit to repo)
- No token limit concerns

This makes CORTEX planning system robust and professional.
