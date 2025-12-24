SKULL-005: Transformation Verification

Real incident (2025-11-10):
- refresh_cortex_story operation executed
- Module apply_narrator_voice_module.py claims "transformation complete"
- Returns success=True with "Narrator voice transformation complete"
- BUT: Line 123 does `context['transformed_story'] = story_content` (pass-through!)
- File hash unchanged after operation
- git diff shows NO changes
- User discovers operation is fake

Impact:
- User trust degradation (claims success but does nothing)
- Status inflation (operations marked READY when incomplete)
- Integration failures (downstream operations expect real data)

SKULL-005 prevents this by:
1. Detecting transformation + success claims in output
2. Requiring file hash comparison test
3. Blocking completion without measurable changes
4. Forcing honest status reporting (PARTIAL vs READY)

Implementation:
- Add @verify_transformation decorator to operation modules
- Integration tests MUST check before/after file state
- CI fails if transformation claims success but git diff empty
- Status documents distinguish architecture vs implementation
