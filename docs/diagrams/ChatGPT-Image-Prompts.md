# CORTEX Mermaid Diagrams: ChatGPT Image Generation Prompts

**Purpose:** ChatGPT image generation prompts for all 15 CORTEX Mermaid diagrams  
**Generated:** November 16, 2025  
**Version:** CORTEX 2.1  
**Author:** Asif Hussain

---

## 📋 Overview

This document contains detailed image generation prompts for ChatGPT (DALL-E 3) to create
professional visualizations of all CORTEX architecture diagrams originally designed in Mermaid.

Each prompt includes:
- **Narrative context** explaining what the diagram represents
- **Visual specifications** detailing layout, colors, and elements
- **Margin requirements** ensuring proper spacing (top, bottom, left, right)
- **Spelling accuracy** instructions for all technical terms

---

## 🎨 Global Style Guide

**All diagrams should follow these conventions:**

### Color Palette
- **Tier 0 (Instinct)**: Deep Purple `#6B46C1` - Immutable governance
- **Tier 1 (Memory)**: Bright Blue `#3B82F6` - Active conversations
- **Tier 2 (Knowledge)**: Emerald Green `#10B981` - Learned patterns
- **Tier 3 (Context)**: Warm Orange `#F59E0B` - Development metrics
- **LEFT Brain**: Cool tones (blues, greens) - Tactical execution
- **RIGHT Brain**: Warm tones (oranges, reds) - Strategic planning
- **Connections**: Gray `#6B7280` with directional arrows

### Typography
- **Headers**: Bold, sans-serif (Arial, Helvetica)
- **Labels**: Regular weight, clear and readable
- **Code/Technical**: Monospace font (Consolas, Monaco)
- **Minimum font size**: 14pt for readability

### Layout Requirements
- **Margins**: Minimum 10% space on all sides (top, bottom, left, right)
- **Spacing**: Clear separation between elements
- **Alignment**: Consistent and grid-based
- **Aspect ratios**: 16:9 for landscape, 9:16 for portrait, 1:1 for square

### Spelling Accuracy
All technical terms must be spelled correctly, including:
- CORTEX (all caps)
- GitHub Copilot
- TDD (Test-Driven Development)
- Definition of Ready (DoR)
- Definition of Done (DoD)
- SQLite, YAML, JSON
- PowerShell, Python
- Tier 0, Tier 1, Tier 2, Tier 3 (capitalized)

---

## 🔧 How to Use These Prompts

1. **Copy the full prompt** (including narrative and specifications)
2. **Paste into ChatGPT** (GPT-4 with DALL-E 3)
3. **Review generated image** for accuracy
4. **Request refinements** if needed ("Add more spacing", "Make text larger")
5. **Download high-resolution** version (1920x1080 minimum)
6. **Save to** `docs/diagrams/generated/` with appropriate filename

**Recommended ChatGPT prompt prefix:**
```
Create a professional technical diagram with the following specifications.
Ensure all text is spelled correctly and there are clear margins on all sides
(top, bottom, left, right - minimum 10% space). Use clean, modern design
suitable for technical documentation.

[Paste specific diagram prompt below]
```

---

## 📊 Diagram 01: CORTEX 4-Tier Memory Architecture

**Source:** `01-tier-architecture.mmd`

### Narrative Context

CORTEX implements a four-tier cognitive architecture inspired by the human brain. Tier 0 (Instinct) contains immutable governance rules that cannot be bypassed. Tier 1 (Working Memory) stores the last 20 conversations in a FIFO queue for short-term context. Tier 2 (Knowledge Graph) learns patterns from past work and stores workflow templates. Tier 3 (Context Intelligence) analyzes git history, file stability, and development metrics. Each tier builds upon the previous, creating a sophisticated memory system that transforms GitHub Copilot from an amnesiac intern into an experienced team member.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX 4-Tier Memory Architecture".

NARRATIVE: CORTEX implements a four-tier cognitive architecture inspired by the human brain. Tier 0 (Instinct) contains immutable governance rules that cannot be bypassed. Tier 1 (Working Memory) stores the last 20 conversations in a FIFO queue for short-term context. Tier 2 (Knowledge Graph) learns patterns from past work and stores workflow templates. Tier 3 (Context Intelligence) analyzes git history, file stability, and development metrics. Each tier builds upon the previous, creating a sophisticated memory system that transforms GitHub Copilot from an amnesiac intern into an experienced team member.

VISUAL DESIGN:
- Primary focus: Vertical stack of four distinct colored layers with upward arrows showing data flow
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Tier 0 (purple): TDD, Definition of Ready/Done, Brain Protection
- Tier 1 (blue): Conversation history, FIFO queue, 18ms performance
- Tier 2 (green): Intent patterns, file relationships, 92ms performance
- Tier 3 (orange): Git analysis, code health, 156ms performance
- Arrows showing enforcement and data flow between tiers

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Vertical stack of four distinct colored layers with upward arrows showing data flow with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 02: CORTEX Dual-Hemisphere Agent System

**Source:** `02-agent-system.mmd`

### Narrative Context

CORTEX uses ten specialist agents divided between two hemispheres, like the human brain. The RIGHT hemisphere (Strategic Planning) contains the Intent Router, Work Planner, Screenshot Analyzer, Change Governor, and Brain Protector - agents that think strategically and protect architectural integrity. The LEFT hemisphere (Tactical Execution) contains the Code Executor, Test Generator, Error Corrector, Health Validator, and Commit Handler - agents that execute work with precision. The Corpus Callosum coordinates communication between hemispheres, ensuring tactical execution aligns with strategic intent.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Dual-Hemisphere Agent System".

NARRATIVE: CORTEX uses ten specialist agents divided between two hemispheres, like the human brain. The RIGHT hemisphere (Strategic Planning) contains the Intent Router, Work Planner, Screenshot Analyzer, Change Governor, and Brain Protector - agents that think strategically and protect architectural integrity. The LEFT hemisphere (Tactical Execution) contains the Code Executor, Test Generator, Error Corrector, Health Validator, and Commit Handler - agents that execute work with precision. The Corpus Callosum coordinates communication between hemispheres, ensuring tactical execution aligns with strategic intent.

VISUAL DESIGN:
- Primary focus: Two brain hemispheres side by side with agents positioned inside and connected by central bridge
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- RIGHT brain (warm colors): Intent Router, Work Planner, Screenshot Analyzer, Change Governor, Brain Protector
- LEFT brain (cool colors): Code Executor, Test Generator, Error Corrector, Health Validator, Commit Handler
- Corpus Callosum bridge in center with message queue
- Coordination arrows between hemispheres
- Color coding: LEFT=blue, RIGHT=orange

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Two brain hemispheres side by side with agents positioned inside and connected by central bridge with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 03: CORTEX Test-Driven Development Workflow

**Source:** `03-tdd-workflow.mmd`

### Narrative Context

CORTEX enforces Test-Driven Development through a strict RED-GREEN-REFACTOR cycle. In the RED phase, the Test Generator creates comprehensive test suites that initially fail. In the GREEN phase, the Code Executor implements minimal code to make tests pass. In the REFACTOR phase, code is cleaned up and improved while ensuring tests still pass. Finally, the Health Validator checks Definition of Done: zero errors, zero warnings, all tests passing. This disciplined approach ensures high code quality and prevents technical debt.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Test-Driven Development Workflow".

NARRATIVE: CORTEX enforces Test-Driven Development through a strict RED-GREEN-REFACTOR cycle. In the RED phase, the Test Generator creates comprehensive test suites that initially fail. In the GREEN phase, the Code Executor implements minimal code to make tests pass. In the REFACTOR phase, code is cleaned up and improved while ensuring tests still pass. Finally, the Health Validator checks Definition of Done: zero errors, zero warnings, all tests passing. This disciplined approach ensures high code quality and prevents technical debt.

VISUAL DESIGN:
- Primary focus: Three-phase workflow with color transitions: red to green to blue, ending with validation
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Phase 1 RED: Test Generator creates failing tests
- Phase 2 GREEN: Code Executor makes tests pass with minimal code
- Phase 3 REFACTOR: Clean up code while keeping tests green
- Validation: Health Validator enforces Definition of Done
- Sequential flow with decision points and success criteria

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Three-phase workflow with color transitions: red to green to blue, ending with validation with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 04: CORTEX Intent Detection and Routing

**Source:** `04-intent-routing.mmd`

### Narrative Context

When users make natural language requests, the Intent Router parses keywords, extracts entities (files, components), and searches Tier 2 for matching patterns. It calculates a confidence score from 0.0 to 1.0. If confidence exceeds 0.7, the request is routed to the appropriate specialist agent. If below 0.7, CORTEX asks clarifying questions. Intent types include PLAN (work planning), EXECUTE (code implementation), TEST (test generation), FIX (bug correction), VALIDATE (system health), ANALYZE (screenshot analysis), PROTECT (brain protection), and CONTINUE (resume session).

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Intent Detection and Routing".

NARRATIVE: When users make natural language requests, the Intent Router parses keywords, extracts entities (files, components), and searches Tier 2 for matching patterns. It calculates a confidence score from 0.0 to 1.0. If confidence exceeds 0.7, the request is routed to the appropriate specialist agent. If below 0.7, CORTEX asks clarifying questions. Intent types include PLAN (work planning), EXECUTE (code implementation), TEST (test generation), FIX (bug correction), VALIDATE (system health), ANALYZE (screenshot analysis), PROTECT (brain protection), and CONTINUE (resume session).

VISUAL DESIGN:
- Primary focus: Decision tree showing request parsing, pattern matching, and routing to eight different agents
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- User natural language input at top
- Intent Router parsing and entity extraction
- Confidence scoring with 0.7 threshold
- Eight intent types with trigger words
- Clarification loop for low confidence
- Color-coded agents by type

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Decision tree showing request parsing, pattern matching, and routing to eight different agents with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 05: CORTEX Multi-Agent Coordination Pattern

**Source:** `05-agent-coordination.mmd`

### Narrative Context

For complex features, multiple CORTEX agents coordinate through the Corpus Callosum. The Work Planner creates a strategic multi-phase plan and sends it via the message queue. The Code Executor receives tasks and implements with TDD. The Test Generator creates comprehensive test suites. The Error Corrector fixes issues using correction history from Tier 2. The Health Validator ensures Definition of Done is met. Finally, results are stored in Tier 1 and patterns are extracted to Tier 2 for future learning. This coordinated approach ensures consistent, high-quality delivery.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Multi-Agent Coordination Pattern".

NARRATIVE: For complex features, multiple CORTEX agents coordinate through the Corpus Callosum. The Work Planner creates a strategic multi-phase plan and sends it via the message queue. The Code Executor receives tasks and implements with TDD. The Test Generator creates comprehensive test suites. The Error Corrector fixes issues using correction history from Tier 2. The Health Validator ensures Definition of Done is met. Finally, results are stored in Tier 1 and patterns are extracted to Tier 2 for future learning. This coordinated approach ensures consistent, high-quality delivery.

VISUAL DESIGN:
- Primary focus: Sequence diagram showing message passing between agents over time
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Work Planner creates strategic plan
- Corpus Callosum message queue coordination
- Code Executor implements with TDD
- Test Generator creates test suites
- Health Validator checks quality
- Knowledge graph update at end
- Vertical timeline with horizontal messages

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Sequence diagram showing message passing between agents over time with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 06: CORTEX Conversation Memory Flow

**Source:** `06-conversation-memory.mmd`

### Narrative Context

CORTEX solves GitHub Copilot's amnesia problem through a sophisticated memory capture and storage system. Conversations are captured via PowerShell scripts, Python CLI, or ambient daemon. They're stored in Tier 1's SQLite database with entity tracking (files, classes, methods). A FIFO queue maintains the 20 most recent conversations, automatically archiving older ones. Entities are indexed for fast retrieval, enabling context-aware responses like understanding 'Make it purple' refers to a button mentioned earlier. This transforms Copilot from forgetting everything to remembering your last 20 work sessions.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Conversation Memory Flow".

NARRATIVE: CORTEX solves GitHub Copilot's amnesia problem through a sophisticated memory capture and storage system. Conversations are captured via PowerShell scripts, Python CLI, or ambient daemon. They're stored in Tier 1's SQLite database with entity tracking (files, classes, methods). A FIFO queue maintains the 20 most recent conversations, automatically archiving older ones. Entities are indexed for fast retrieval, enabling context-aware responses like understanding 'Make it purple' refers to a button mentioned earlier. This transforms Copilot from forgetting everything to remembering your last 20 work sessions.

VISUAL DESIGN:
- Primary focus: Data flow from conversation capture to storage to retrieval with FIFO queue management
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Three capture methods: PowerShell, Python CLI, Ambient Daemon
- Tier 1 SQLite storage with entity extraction
- FIFO queue (20 conversations max)
- Archive process for old conversations
- Entity indexing for fast search
- Context retrieval for future requests

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Data flow from conversation capture to storage to retrieval with FIFO queue management with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 07: CORTEX Brain Protection System (Rule #22)

**Source:** `07-brain-protection.mmd`

### Narrative Context

CORTEX protects its own intelligence through six protection layers enforced by the Brain Protector agent. Layer 1 (Instinct Immutability) prevents bypassing core rules. Layer 2 (Critical Path Protection) guards core files from modification. Layer 3 (Application Separation) keeps user application code out of CORTEX core. Layer 4 (Brain State Protection) prevents committing conversation history to git. Layer 5 (Namespace Isolation) enforces scope boundaries. Layer 6 (Architectural Integrity) maintains design principles. When risky changes are detected, the Brain Protector challenges the user and suggests safer alternatives.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Brain Protection System (Rule #22)".

NARRATIVE: CORTEX protects its own intelligence through six protection layers enforced by the Brain Protector agent. Layer 1 (Instinct Immutability) prevents bypassing core rules. Layer 2 (Critical Path Protection) guards core files from modification. Layer 3 (Application Separation) keeps user application code out of CORTEX core. Layer 4 (Brain State Protection) prevents committing conversation history to git. Layer 5 (Namespace Isolation) enforces scope boundaries. Layer 6 (Architectural Integrity) maintains design principles. When risky changes are detected, the Brain Protector challenges the user and suggests safer alternatives.

VISUAL DESIGN:
- Primary focus: Shield with six concentric protection layers surrounding CORTEX brain core
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Center: CORTEX brain core (Tiers 0-3)
- Layer 1: Instinct Immutability
- Layer 2: Critical Path Protection
- Layer 3: Application Separation
- Layer 4: Brain State Protection
- Layer 5: Namespace Isolation
- Layer 6: Architectural Integrity
- Brain Protector agent as guardian

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Shield with six concentric protection layers surrounding CORTEX brain core with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 08: CORTEX Knowledge Graph and Pattern Learning

**Source:** `08-knowledge-graph.mmd`

### Narrative Context

CORTEX learns from every interaction through Tier 2's knowledge graph. Intent patterns are stored with confidence scores, enabling better routing over time. File relationships track co-modification patterns (when AuthService.cs changes, tests usually change too). Workflow templates capture successful approaches for reuse. Validation insights store correction history to prevent repeated mistakes. Patterns decay 5% every 30 days if unused, keeping the knowledge graph fresh. When similar work is requested, CORTEX suggests proven patterns, dramatically reducing implementation time.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Knowledge Graph and Pattern Learning".

NARRATIVE: CORTEX learns from every interaction through Tier 2's knowledge graph. Intent patterns are stored with confidence scores, enabling better routing over time. File relationships track co-modification patterns (when AuthService.cs changes, tests usually change too). Workflow templates capture successful approaches for reuse. Validation insights store correction history to prevent repeated mistakes. Patterns decay 5% every 30 days if unused, keeping the knowledge graph fresh. When similar work is requested, CORTEX suggests proven patterns, dramatically reducing implementation time.

VISUAL DESIGN:
- Primary focus: Network graph showing nodes (patterns, files, workflows) connected by relationships with confidence scores
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Intent patterns with confidence scores
- File relationship graph with co-modification strength
- Workflow templates with success rates
- Validation insights and correction history
- Pattern decay mechanism (5% per 30 days)
- FTS5 full-text search capability
- Namespace isolation (cortex vs application)

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Network graph showing nodes (patterns, files, workflows) connected by relationships with confidence scores with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 09: CORTEX Context Intelligence and Analytics

**Source:** `09-context-intelligence.mmd`

### Narrative Context

Tier 3 provides holistic development context through git analysis and session analytics. Git analysis tracks commit velocity (42 commits/week average), identifies file hotspots (files changed frequently), and classifies file stability (stable, unstable, volatile). Code health metrics track test coverage, build success rates, and error counts. Session analytics discover productivity patterns (your 10am-12pm sessions have 94% success rate). These insights enable proactive warnings: 'HostControlPanel.razor is a hotspot with 28% churn rate - add extra testing before changes.'

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Context Intelligence and Analytics".

NARRATIVE: Tier 3 provides holistic development context through git analysis and session analytics. Git analysis tracks commit velocity (42 commits/week average), identifies file hotspots (files changed frequently), and classifies file stability (stable, unstable, volatile). Code health metrics track test coverage, build success rates, and error counts. Session analytics discover productivity patterns (your 10am-12pm sessions have 94% success rate). These insights enable proactive warnings: 'HostControlPanel.razor is a hotspot with 28% churn rate - add extra testing before changes.'

VISUAL DESIGN:
- Primary focus: Dashboard with multiple metric panels showing git stats, file stability, and productivity analytics
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Git commit velocity chart (last 30 days)
- File hotspot identification with churn rates
- File stability classification (stable/unstable/volatile)
- Code health scorecard (coverage, build success)
- Session productivity patterns by time of day
- Proactive warning system
- Performance: 156ms average analysis time

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Dashboard with multiple metric panels showing git stats, file stability, and productivity analytics with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 10: CORTEX Interactive Feature Planning

**Source:** `10-feature-planning.mmd`

### Narrative Context

When users say 'plan a feature', CORTEX activates the Work Planner agent for interactive planning. The planner assesses confidence based on detail provided: high confidence (80-100%) proceeds directly to planning, medium (50-79%) asks 1-2 questions, low (<50%) asks detailed clarifying questions. Questions cover authentication methods, user types, integrations, and security constraints. The planner then generates a multi-phase roadmap with tasks, dependencies, risks, and acceptance criteria. Plans are stored in Tier 1 for execution and Tier 2 for future pattern learning.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Interactive Feature Planning".

NARRATIVE: When users say 'plan a feature', CORTEX activates the Work Planner agent for interactive planning. The planner assesses confidence based on detail provided: high confidence (80-100%) proceeds directly to planning, medium (50-79%) asks 1-2 questions, low (<50%) asks detailed clarifying questions. Questions cover authentication methods, user types, integrations, and security constraints. The planner then generates a multi-phase roadmap with tasks, dependencies, risks, and acceptance criteria. Plans are stored in Tier 1 for execution and Tier 2 for future pattern learning.

VISUAL DESIGN:
- Primary focus: Flowchart showing confidence assessment, question asking, and plan generation phases
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Intent detection: PLAN with confidence score
- Three confidence levels (high, medium, low)
- Clarifying questions section with 4 categories
- Multi-phase plan generation (Phases 1-4)
- Plan metadata: dependencies, risks, criteria
- Execution ready state with storage
- Color-coded phases

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Flowchart showing confidence assessment, question asking, and plan generation phases with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 11: CORTEX Performance Benchmarks

**Source:** `11-performance-benchmarks.mmd`

### Narrative Context

CORTEX consistently exceeds all performance targets. Tier 1 conversation storage averages 12ms (target: <30ms), recent query 18ms (target: <50ms), and search 45ms (target: <100ms). Tier 2 pattern search averages 92ms (target: <150ms) with FTS5 full-text search. Tier 3 git analysis completes in 156ms (target: <200ms). Intent routing takes 45ms (target: <100ms). Brain protection checks complete in 89ms (target: <150ms). These metrics demonstrate that CORTEX adds intelligence without sacrificing speed.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Performance Benchmarks".

NARRATIVE: CORTEX consistently exceeds all performance targets. Tier 1 conversation storage averages 12ms (target: <30ms), recent query 18ms (target: <50ms), and search 45ms (target: <100ms). Tier 2 pattern search averages 92ms (target: <150ms) with FTS5 full-text search. Tier 3 git analysis completes in 156ms (target: <200ms). Intent routing takes 45ms (target: <100ms). Brain protection checks complete in 89ms (target: <150ms). These metrics demonstrate that CORTEX adds intelligence without sacrificing speed.

VISUAL DESIGN:
- Primary focus: Bar chart comparing target vs actual performance for all operations, all bars showing green (under target)
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Tier 1 operations: Store (12ms), Query (18ms), Search (45ms)
- Tier 2 operations: Pattern search (92ms), Store (56ms)
- Tier 3 operations: Git analysis (156ms), File stability (67ms)
- Agent operations: Intent routing (45ms), Brain protection (89ms)
- All actuals below targets (green indicators)
- Performance margin percentages shown

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Bar chart comparing target vs actual performance for all operations, all bars showing green (under target) with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 12: CORTEX Token Optimization Results

**Source:** `12-token-optimization.mmd`

### Narrative Context

CORTEX achieved 97.2% input token reduction through modular architecture. The original monolithic prompt was 74,047 tokens. By splitting into focused modules (story, setup, technical, agents, tracking), average input dropped to 2,078 tokens. This translates to 93.4% cost reduction using GitHub Copilot's pricing model. Projected annual savings: $8,636 for 1,000 requests/month. Additional benefits include 97% faster parsing (2-3s to 80ms), easier maintenance (200-400 lines per module vs 8,701 monolithic), and better user experience with targeted documentation.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Token Optimization Results".

NARRATIVE: CORTEX achieved 97.2% input token reduction through modular architecture. The original monolithic prompt was 74,047 tokens. By splitting into focused modules (story, setup, technical, agents, tracking), average input dropped to 2,078 tokens. This translates to 93.4% cost reduction using GitHub Copilot's pricing model. Projected annual savings: $8,636 for 1,000 requests/month. Additional benefits include 97% faster parsing (2-3s to 80ms), easier maintenance (200-400 lines per module vs 8,701 monolithic), and better user experience with targeted documentation.

VISUAL DESIGN:
- Primary focus: Before/after comparison showing dramatic reduction in tokens, cost, and parsing time
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- Before: 74,047 tokens (monolithic prompt)
- After: 2,078 tokens average (modular)
- 97.2% input token reduction
- 93.4% cost reduction ($8,636/year savings)
- 97% faster parsing (2-3s to 80ms)
- Modular structure: 6 focused documents
- Side-by-side visual comparison

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Before/after comparison showing dramatic reduction in tokens, cost, and parsing time with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 13: CORTEX Zero-Footprint Plugin Architecture

**Source:** `13-plugin-system.mmd`

### Narrative Context

CORTEX plugins extend functionality without adding external dependencies. Each plugin inherits from BasePlugin and implements initialize(), execute(), and cleanup() methods. Plugins register natural language patterns with the command registry. When users make requests, the Intent Router checks plugin patterns alongside core intents. Plugins access CORTEX brain tiers (Tier 2 for patterns, Tier 3 for context) but never require external APIs or tools. Example plugins include Recommendation API (code quality analysis), Code Review, Cleanup, and Documentation Refresh - all using only CORTEX brain intelligence.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Zero-Footprint Plugin Architecture".

NARRATIVE: CORTEX plugins extend functionality without adding external dependencies. Each plugin inherits from BasePlugin and implements initialize(), execute(), and cleanup() methods. Plugins register natural language patterns with the command registry. When users make requests, the Intent Router checks plugin patterns alongside core intents. Plugins access CORTEX brain tiers (Tier 2 for patterns, Tier 3 for context) but never require external APIs or tools. Example plugins include Recommendation API (code quality analysis), Code Review, Cleanup, and Documentation Refresh - all using only CORTEX brain intelligence.

VISUAL DESIGN:
- Primary focus: Hub-and-spoke diagram with CORTEX core at center and plugins around edge showing inheritance
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- CORTEX Core (center): BasePlugin, Plugin Registry, Command Registry
- Active plugins (surrounding): Recommendation API, Code Review, Cleanup, etc.
- Inheritance arrows (dashed) from plugins to core
- Command registration flow (solid arrows)
- Natural Language Router at top
- Zero external dependencies callout
- Interface methods: initialize(), execute(), cleanup()

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Hub-and-spoke diagram with CORTEX core at center and plugins around edge showing inheritance with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 14: CORTEX Complete Data Flow (End-to-End)

**Source:** `14-data-flow-complete.mmd`

### Narrative Context

This diagram shows the complete journey from user request to feature completion. User says 'Add purple button to dashboard'. Tier 1 checks recent conversations and loads context (DashboardPanel.razor). Intent Router parses keywords and routes to Code Executor. Tier 2 searches for similar patterns and loads the button_creation workflow. Code Executor follows TDD: write failing test, implement button, tests pass, refactor code. Health Validator checks Definition of Done. Commit Handler creates semantic commit. Results are stored back to Tier 1, patterns updated in Tier 2, and analytics recorded in Tier 3. This complete loop demonstrates how all components work together.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "CORTEX Complete Data Flow (End-to-End)".

NARRATIVE: This diagram shows the complete journey from user request to feature completion. User says 'Add purple button to dashboard'. Tier 1 checks recent conversations and loads context (DashboardPanel.razor). Intent Router parses keywords and routes to Code Executor. Tier 2 searches for similar patterns and loads the button_creation workflow. Code Executor follows TDD: write failing test, implement button, tests pass, refactor code. Health Validator checks Definition of Done. Commit Handler creates semantic commit. Results are stored back to Tier 1, patterns updated in Tier 2, and analytics recorded in Tier 3. This complete loop demonstrates how all components work together.

VISUAL DESIGN:
- Primary focus: Sequential flow diagram showing all tiers and agents in complete request lifecycle
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- User request at top: 'Add purple button'
- Tier 1 context check with entity tracking
- Intent routing with confidence scoring
- Tier 2 pattern search and workflow loading
- Code Executor TDD workflow (RED-GREEN-REFACTOR)
- Health Validator checking Definition of Done
- Commit Handler with semantic message
- Storage back to all three tiers
- Complete loop showing learning

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Sequential flow diagram showing all tiers and agents in complete request lifecycle with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📊 Diagram 15: Before CORTEX vs After CORTEX

**Source:** `15-before-vs-after.mmd`

### Narrative Context

This comparison shows the dramatic difference CORTEX makes. BEFORE: Copilot alone forgets context between sessions ('Make it purple' - 'What should I make purple?'), repeats mistakes, has no pattern recognition, no learning, and no proactive guidance. AFTER: CORTEX remembers last 20 conversations, understands 'it' references, learns from corrections, suggests proven patterns, identifies file hotspots proactively, and gets smarter with every interaction. The transformation is like upgrading from a brilliant amnesiac intern to an experienced senior developer who remembers your entire project history.

### Image Generation Prompt for ChatGPT

```
Create a professional technical diagram titled "Before CORTEX vs After CORTEX".

NARRATIVE: This comparison shows the dramatic difference CORTEX makes. BEFORE: Copilot alone forgets context between sessions ('Make it purple' - 'What should I make purple?'), repeats mistakes, has no pattern recognition, no learning, and no proactive guidance. AFTER: CORTEX remembers last 20 conversations, understands 'it' references, learns from corrections, suggests proven patterns, identifies file hotspots proactively, and gets smarter with every interaction. The transformation is like upgrading from a brilliant amnesiac intern to an experienced senior developer who remembers your entire project history.

VISUAL DESIGN:
- Primary focus: Side-by-side comparison with sad/frustrated left side and happy/productive right side
- Style: Clean, modern, technical illustration
- Aspect ratio: 16:9 landscape (or adjust based on content)

KEY ELEMENTS TO INCLUDE:
- LEFT (Before): Copilot alone, forgetting, confused, repetitive
- RIGHT (After): Copilot + CORTEX, remembering, learning, guiding
- Specific examples of problems solved
- Memory timeline showing retention
- Pattern learning visualization
- Proactive warning examples
- Visual contrast: frustrated vs productive developer

COLOR SCHEME (use exact hex codes):
- Purple #6B46C1 for Tier 0/Instinct elements
- Blue #3B82F6 for Tier 1/Memory/LEFT brain elements
- Green #10B981 for Tier 2/Knowledge elements
- Orange #F59E0B for Tier 3/Context/RIGHT brain elements
- Gray #6B7280 for connections and arrows

TYPOGRAPHY:
- Title: Bold, 24pt, centered at top
- Section headers: Bold, 18pt
- Labels: Regular, 14pt minimum
- Technical terms: Monospace where appropriate

CRITICAL REQUIREMENTS:
1. **MARGINS**: Leave 10% empty space on all four sides (top, bottom, left, right)
2. **SPELLING**: Use correct spelling for all terms:
   - CORTEX (all caps)
   - GitHub Copilot
   - TDD, DoR, DoD
   - SQLite, YAML, JSON
   - Tier 0, Tier 1, Tier 2, Tier 3
3. **READABILITY**: All text must be clearly readable at 50% zoom
4. **ALIGNMENT**: Use grid-based layout with consistent spacing
5. **CONNECTIONS**: Show clear directional arrows with labels

OUTPUT SPECIFICATIONS:
- Resolution: 1920x1080 minimum (or proportional)
- Format: PNG with transparent or white background
- Quality: High-resolution suitable for documentation

Generate a professional, polished diagram suitable for technical documentation.
```

### Expected Output

The image should clearly show Side-by-side comparison with sad/frustrated left side and happy/productive right side with proper margins on all sides,
correctly spelled technical terms, and professional visual design matching the
CORTEX style guide.

---

## 📝 Prompt Refinement Tips

If the generated image needs adjustments, use these follow-up prompts:

**For spacing issues:**
- "Increase margins on all sides to 15%"
- "Add more spacing between elements"
- "Make the layout less cramped"

**For text issues:**
- "Increase all font sizes by 20%"
- "Make labels more readable"
- "Use bolder text for headers"
- "Fix spelling of [specific term]"

**For color issues:**
- "Use exact hex color #3B82F6 for blue elements"
- "Make the color contrast stronger"
- "Ensure colors match the specified palette"

**For layout issues:**
- "Align elements in a grid pattern"
- "Stack vertically instead of horizontally"
- "Center the main content"
- "Balance the left and right sides"

---

## 📁 File Organization

**Save generated images to:**
```
docs/diagrams/generated/
├── 01-tier-architecture.png
├── 02-agent-system.png
├── 03-tdd-workflow.png
├── 04-intent-routing.png
├── 05-agent-coordination.png
├── 06-conversation-memory.png
├── 07-brain-protection.png
├── 08-knowledge-graph.png
├── 09-context-intelligence.png
├── 10-feature-planning.png
├── 11-performance-benchmarks.png
├── 12-token-optimization.png
├── 13-plugin-system.png
├── 14-data-flow-complete.png
└── 15-before-vs-after.png
```

**Naming convention:**
- Use same number prefix as .mmd file
- Descriptive name matching diagram purpose
- PNG format (transparent background preferred)

---

## 🔗 Related Documentation

- **Mermaid Sources**: `docs/diagrams/mermaid/*.mmd`
- **Style Guide**: `docs/diagrams/STYLE-GUIDE.md`
- **Narratives**: `docs/diagrams/narratives/*.md`
- **CORTEX Story**: `docs/awakening-of-cortex.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

*These prompts are optimized for ChatGPT with DALL-E 3. For other AI image generators (Midjourney, Stable Diffusion), adjust prompt syntax accordingly.*