---
title: Knowledge Graph Import Guide
date: 2025-11-25
author: CORTEX Documentation Generator
---

# Knowledge Graph Import Guide

## Knowledge Graph Import/Export

CORTEX's Tier 2 Knowledge Graph stores learned patterns and relationships.

### Brain Implants System

**Export Brain Patterns**
```
export brain
```

Creates timestamped YAML file containing:
- Learned patterns (workflows, tech stacks)
- Pattern confidence scores (0.0-1.0)
- Metadata (source, version, namespaces)
- Integrity signature

**Import Brain Patterns**
```
import brain
```

Imports shared patterns with intelligent conflict resolution:
- **Auto**: Keep higher confidence (recommended)
- **Overwrite**: Import wins
- **Preserve**: Local wins

### What Gets Shared

**Exported**:
- Workflow templates from successful implementations
- Technology stack patterns
- Problem-solution pairs
- Architecture decisions

**Not Exported**:
- Conversation history (Tier 1 - private)
- Machine-specific configurations
- Database connections
- Credentials

### Use Cases

**Team Knowledge Sharing**
1. Senior developer exports patterns
2. Team members import with "auto" strategy
3. Team benefits from shared learnings

**Backup & Restore**
1. Export before major changes
2. Keep timestamped backups
3. Restore if needed

**Cross-Project Transfer**
1. Export patterns from completed project
2. Import into new project
3. Apply learned patterns immediately

## Related Documentation

- [Brain Export Guide](https://github.com/asifhussain60/CORTEX/blob/CORTEX-3.0/.github/prompts/modules/brain-export-guide.md)
- [Brain Import Guide](https://github.com/asifhussain60/CORTEX/blob/CORTEX-3.0/.github/prompts/modules/brain-import-guide.md)
- [Architecture: Tier System](architecture/tier-system.md)
