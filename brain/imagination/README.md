# Tier 4: Imagination

**Purpose:** Creative idea tracking, implementation plans, and question deduplication.

## 📂 Contents

- \ideas-stashed.yaml\ - Future enhancements and implementation plans
- \questions-answered.yaml\ - Deduplication cache
- \semantic-links.yaml\ - Idea relationships

## 💡 Use Cases

### Implementation Plans
All implementation plans (like KDS-V6-HOLISTIC-PLAN.md) should be:
1. **Structured in:** \ideas-stashed.yaml\ (core idea + status)
2. **Detailed in:** \docs/*.md\ (full documentation)
3. **Linked via:** \semantic-links.yaml\ (idea → doc mapping)

**Example:**
\\\yaml
ideas:
  kds-v6-brain-redesign:
    status: in-progress
    priority: high
    created: 2025-11-04
    description: Brain-inspired 6-tier structure
    documentation: docs/KDS-V6-HOLISTIC-PLAN.md
    related_ideas:
      - brain-flush-mechanism
      - extensible-sharpener
\\\

### Question Deduplication
- Avoid answering same question twice
- Track which questions have been answered
- Link to knowledge base articles

### Idea Stashing
- Capture ideas for later (\stash idea: ...\)
- Track idea evolution (status: idea → planned → in-progress → implemented)

## 📖 See Also

- knowledge-retriever.md - Queries this tier
- docs/ - Detailed documentation linked from ideas
