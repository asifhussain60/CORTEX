# src.plugins.doc_refresh_plugin

Documentation Refresh Plugin

Automatically refreshes the 6 synchronized documentation files based on CORTEX 2.0 design:
- docs/story/CORTEX-STORY/Technical-CORTEX.md
- docs/story/CORTEX-STORY/Awakening Of CORTEX.md
- docs/story/CORTEX-STORY/Image-Prompts.md (TECHNICAL DIAGRAMS ONLY - no cartoons)
- docs/story/CORTEX-STORY/History.md
- docs/story/CORTEX-STORY/Ancient-Rules.md (The Rule Book - governance rules)
- docs/story/CORTEX-STORY/CORTEX-FEATURES.md (Simple feature list for humans)

Triggered by: 'Update Documentation' or 'Refresh documentation' commands at entry point

NOTE: Image-Prompts.md generates SYSTEM DIAGRAMS (flowcharts, sequence diagrams, 
architecture diagrams) that reveal CORTEX design - NOT cartoon characters or story 
illustrations. For story illustrations, see prompts/user/cortex-gemini-image-prompts.md

CRITICAL RULES (ABSOLUTE PROHIBITIONS):
1. **NEVER CREATE NEW FILES** - Only update existing documentation files
2. **FORBIDDEN:** Creating Quick Read, Summary, or variant versions
3. **FORBIDDEN:** Creating new files in docs/story/CORTEX-STORY/
4. If a file doesn't exist, FAIL with error - do not create it
5. If content exceeds target length, TRIM existing file - do not create alternatives

READ TIME ENFORCEMENT:
- "Awakening Of CORTEX.md" target: 60-75 minutes (epic full story)
- If Quick Read needed: UPDATE existing file to 15-20 min, don't create variant
- Plugin should TRIM content, not spawn new files
- Validate read time after updates, enforce constraints

PROGRESSIVE RECAP RULES (for multi-part stories):
1. Each PART should start with a quick, funny recap of previous parts
2. Part 2 recaps Part 1 (medium compression, ~150 tokens)
3. Part 3 recaps Part 2 + Part 1 (progressive compression: Part 1 high-level ~80 tokens, Part 2 medium ~120 tokens)
4. Recaps get progressively more compressed as you go back in time
5. Maintains humor, key milestones, and narrative flow
6. Insert recaps RIGHT AFTER the '# PART X:' heading, BEFORE the first interlude
7. Style: casual, funny, single-paragraph format like Lab Notebook

Example Pattern:
  # PART 2: THE EVOLUTION TO 2.0
  
  *[Quick funny recap of Part 1 achievements]*
  
  ## Interlude: The Whiteboard Archaeology
  
  # PART 3: THE EXTENSION ERA
  
  *[Quick funny recap of Part 2 (detailed) + Part 1 (high-level)]*
  
  ## Interlude: The Invoice That Haunts Him
