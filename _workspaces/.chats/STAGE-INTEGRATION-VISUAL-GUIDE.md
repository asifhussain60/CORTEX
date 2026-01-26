# 🔗 Complete Workflow Visualization

## Master Orchestrator: 4-Stage Execution Pipeline

```
USER INPUT: coordinate_operation(operation="IMPLEMENT", context={...})
    ║
    ╚═══════════════════════════════════════════════════════════════╗
        GOVERNANCE VALIDATION                                      ║
        ├─ Validate CORE-017, CORE-019 policies                   ║
        ├─ Increment turn counter                                 ║
        └─ Check authorization                                    ║
        │                                                          ║
        ↓                                                          ║
        ╔═══════════════════════════════════════════════════════╗  ║
        ║ STAGE 1: INTERACTION ORCHESTRATOR (Comprehension)    ║  ║
        ╠═══════════════════════════════════════════════════════╣  ║
        ║ Call: InteractionOrchestrator.execute_turn_with_     ║  ║
        ║       challenge(user_input, context, turn_number)    ║  ║
        ║                                                       ║  ║
        ║ Returns:                                             ║  ║
        ║ ├─ challenges: []  # Challenge-driven options       ║  ║
        ║ ├─ user_choice: str                                 ║  ║
        ║ └─ raw_result: {...}                                ║  ║
        ║                                                       ║  ║
        ║ Logs: AC-FR-WIRING-001-STAGE-1                       ║  ║
        ║ Non-blocking: Yes (logs error, continues)            ║  ║
        ╚═══════════════════════════════════════════════════════╝  ║
        │                                                          ║
        ↓                                                          ║
        ╔═══════════════════════════════════════════════════════╗  ║
        ║ STAGE 2: INTENT ROUTER (Verification)               ║  ║
        ╠═══════════════════════════════════════════════════════╣  ║
        ║ Call: IntentRouter.verify_intent(                    ║  ║
        ║       operation, context, stage1_result)            ║  ║
        ║                                                       ║  ║
        ║ Returns:                                             ║  ║
        ║ ├─ classified_intent: str    # Verified intent      ║  ║
        ║ ├─ confidence: float         # 0.0-1.0 score        ║  ║
        ║ └─ metadata: {...}           # Intent context       ║  ║
        ║                                                       ║  ║
        ║ Logs: AC-FR-WIRING-002-STAGE-2                       ║  ║
        ║ Non-blocking: Yes (logs error, continues)            ║  ║
        ╚═══════════════════════════════════════════════════════╝  ║
        │                                                          ║
        ↓                                                          ║
        ╔═══════════════════════════════════════════════════════╗  ║
        ║ STAGE 3: KNOWLEDGE SYNTHESIS (Instruction Gen)      ║  ║
        ╠═══════════════════════════════════════════════════════╣  ║
        ║ Call: KnowledgeSynthesisEngine.synthesize_for_      ║  ║
        ║       intent(classified_intent, context)            ║  ║
        ║                                                       ║  ║
        ║ Returns:                                             ║  ║
        ║ ├─ synthesized_instructions: str                    ║  ║
        ║ ├─ instruction_sources: [{layer, domain, ...}]     ║  ║
        ║ └─ synthesis_confidence: float                       ║  ║
        ║                                                       ║  ║
        ║ Logs: AC-HYBRID-KNOWLEDGE-005                        ║  ║
        ║ Non-blocking: Yes (logs error, continues)            ║  ║
        ╚═══════════════════════════════════════════════════════╝  ║
        │                                                          ║
        ↓                                                          ║
        ╔═══════════════════════════════════════════════════════╗  ║
        ║ STAGE 4+: DOMAIN ORCHESTRATION (Execution)          ║  ║
        ╠═══════════════════════════════════════════════════════╣  ║
        ║ For each target_domain:                              ║  ║
        ║   ├─ Get domain orchestrator                         ║  ║
        ║   ├─ Pass classified_intent + synthesized_instr.    ║  ║
        ║   ├─ Execute operation                               ║  ║
        ║   └─ Collect result                                  ║  ║
        ║                                                       ║  ║
        ║ Aggregate all results                                ║  ║
        ║                                                       ║  ║
        ║ Logs: AC-AR-006-01                                   ║  ║
        ╚═══════════════════════════════════════════════════════╝  ║
        │                                                          ║
        ↓                                                          ║
        FINAL COORDINATION RESULT:                                ║
        {                                                         ║
            "operation": "IMPLEMENT",                             ║
            "classified_intent": "IMPLEMENT",        # Stage 2    ║
            "stage1_comprehension": {...},           # Stage 1    ║
            "stage2_intent": {...},                  # Stage 2    ║
            "synthesized_instructions": "...",       # Stage 3    ║
            "results": {...},                        # Stage 4+   ║
            "timestamp": "...",                                   ║
            "turn_number": 1                                      ║
        }                                                         ║
        │                                                          ║
        ↓                                                          ║
    ════════════════════════════════════════════════════════════════╝
    RETURN Ok(coordination_result)
```

---

## Data Flowing Through Stages

```
Stage 1 Output                    Stage 2 Input
┌──────────────────┐              ┌──────────────────┐
│ challenges: []   │──────────┐   │ operation: str   │
│ user_choice: str │──────────┼──→│ context: dict    │
│ raw_result: {}   │──────────┘   │ stage1_result: {}│
└──────────────────┘              └──────────────────┘
                                        │
                                        ↓
                                  Stage 2 Output
                                  ┌──────────────────┐
                                  │ classified_intent│──┐
                                  │ confidence: float│  │
                                  │ metadata: dict   │  │
                                  └──────────────────┘  │
                                                        │
        Stage 3 Input ◄──────────────────────────────┘
        ┌──────────────────┐
        │ intent_type: str │
        │ context: dict    │
        └──────────────────┘
               │
               ↓
        Stage 3 Output
        ┌──────────────────────────┐
        │ synthesized_instructions │
        │ instruction_sources: []  │
        │ synthesis_confidence     │
        └──────────────────────────┘
               │
               ↓
        Stage 4+ Input (enhanced)
        ┌──────────────────────────┐
        │ classified_intent: str   │
        │ synthesized_instr.: str  │
        │ context: dict            │
        └──────────────────────────┘
```

---

## Audit Trail: What Gets Logged

```
AC-AR-006-01 COORDINATION completion logs:

{
    "ac_id": "AC-AR-006-01",
    "operation": "COORDINATION",
    
    ┌─── GOVERNANCE ──────────────────┐
    │ turn_number: 1                  │
    │ governance_enforced: true       │
    └─────────────────────────────────┘
    
    ┌─── STAGE 1 METRICS ─────────────┐
    │ stage1_enabled: true            │
    │ stage1_challenges_generated: 3  │
    │ stage1_user_choice: "Opt 2"     │
    └─────────────────────────────────┘
    
    ┌─── STAGE 2 METRICS ─────────────┐
    │ stage2_enabled: true            │
    │ stage2_classified_intent: "IMP" │
    │ stage2_intent_confidence: 0.98  │
    │ stage2_intent_matched: true     │
    └─────────────────────────────────┘
    
    ┌─── STAGE 3 METRICS ─────────────┐
    │ instructions_synthesized: true  │
    │ instruction_sources_count: 2    │
    └─────────────────────────────────┘
    
    ┌─── STAGE 4+ METRICS ────────────┐
    │ orchestrators_involved: 2       │
    │ successful: 2                   │
    │ failed: 0                       │
    └─────────────────────────────────┘
}
```

---

## Error Handling: Non-Blocking Stages

```
If Stage 1 fails:
    ├─ Log AC-FR-WIRING-001-STAGE-1 error
    ├─ Set stage1_challenges = []
    ├─ Set stage1_user_choice = None
    └─ Continue to Stage 2 ✓

If Stage 2 fails:
    ├─ Log AC-FR-WIRING-002-STAGE-2 error
    ├─ Keep classified_intent = operation (original)
    ├─ Set intent_confidence = 1.0
    └─ Continue to Stage 3 ✓

If Stage 3 fails:
    ├─ Log AC-HYBRID-KNOWLEDGE-005 error
    ├─ Set synthesized_instructions = None
    ├─ Set instruction_sources = []
    └─ Continue to Stage 4+ ✓

If Stage 4+ fails:
    ├─ Log domain-specific errors
    ├─ Populate errors dict
    └─ Return Err(...) ✗

All stages are independent - no cascading failures!
```

---

## Quick Integration Check

```
✅ coordinate_operation() execution checklist:

┌─ Governance ────────────────┐
│ ✓ Validate policies          │
│ ✓ Increment turn counter     │
└──────────────────────────────┘

┌─ Stage 1 ──────────────────┐
│ ✓ Call InteractionOrch.      │
│ ✓ Generate challenges        │
│ ✓ Capture user choice        │
│ ✓ Log comprehension          │
└──────────────────────────────┘

┌─ Stage 2 ──────────────────┐
│ ✓ Call IntentRouter          │
│ ✓ Classify intent            │
│ ✓ Compute confidence         │
│ ✓ Log verification           │
└──────────────────────────────┘

┌─ Stage 3 ──────────────────┐
│ ✓ Call SynthesisEngine       │
│ ✓ Generate instructions      │
│ ✓ Get sources                │
│ ✓ Log synthesis              │
└──────────────────────────────┘

┌─ Stage 4+ ─────────────────┐
│ ✓ Delegate to orchestrators  │
│ ✓ Aggregate results          │
│ ✓ Atomic transaction         │
│ ✓ Log completion             │
└──────────────────────────────┘
```

---

**All 4 stages now wired, integrated, and flowing through a single atomic Master Orchestrator coordination workflow!**
