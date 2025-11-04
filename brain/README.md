# KDS Brain Structure (v6.0)

**Inspired by human brain architecture** - Multi-tier intelligence system.

## 📁 Folder Structure

\\\
brain/
├── instinct/              # Tier 0: Permanent core rules (never reset)
├── working-memory/        # Tier 1: Last 20 conversations (FIFO)
├── long-term/             # Tier 2: Consolidated patterns
├── context-awareness/     # Tier 3: Project metrics & intelligence
├── imagination/           # Tier 4: Ideas & questions
├── housekeeping/          # Tier 5: Automatic maintenance
├── sharpener/             # Testing framework
├── event-stream/          # Activity log
├── health/                # Diagnostics
└── archived/              # Historical data
\\\

## 🧠 Brain Region Mapping

| Brain Region | Biological Function | KDS Folder | Purpose |
|--------------|---------------------|------------|---------|
| **Brainstem** | Automatic responses | \instinct/\ | Core rules, never change |
| **Hippocampus** | Short-term memory | \working-memory/\ | Recent 20 conversations |
| **Cortex** | Long-term learning | \long-term/\ | Consolidated patterns |
| **Prefrontal Cortex** | Context & planning | \context-awareness/\ | Project metrics |
| **Creative Centers** | Imagination | \imagination/\ | Ideas & questions |
| **Cerebellum** | Automatic maintenance | \housekeeping/\ | Background cleanup |

## 📖 Migration from v5.0

This structure replaces the flat \kds-brain/\ folder with a hierarchical, brain-inspired organization.

**Old (v5.0):**
\\\
kds-brain/
├── conversation-history.jsonl
├── knowledge-graph.yaml
├── development-context.yaml
└── events.jsonl
\\\

**New (v6.0):**
- \conversation-history.jsonl\ → Split into \working-memory/recent-conversations/*.jsonl\
- \knowledge-graph.yaml\ → Split into \long-term/*.yaml\ (specialized files)
- \development-context.yaml\ → Split into \context-awareness/*.yaml\
- \vents.jsonl\ → Moved to \vent-stream/events.jsonl\

See: \KDS/docs/KDS-V6-MIGRATION-GUIDE.md\ for complete migration instructions.
