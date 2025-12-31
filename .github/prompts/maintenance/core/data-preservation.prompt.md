# ⛔ DATA PRESERVATION RULES

**Before ANY cleanup/deletion operation, verify:**

- [ ] `cortex-brain/lessons-learned.yaml` preserved
- [ ] `cortex-brain/knowledge-graph.yaml` preserved
- [ ] `cortex-brain/tier1/*.md` preserved
- [ ] `cortex-brain/tier2/*.yaml` preserved
- [ ] User-added documents in `cortex-brain/documents/` preserved
- [ ] `cortex-brain/user-dictionary.yaml` preserved
- [ ] All `.db` files in `tier1/`, `tier2/`, `tier3/` preserved
- [ ] `copilot_instructions` in plan files preserved during regeneration
- [ ] `metadata.notes` and `metadata.tags` in plans preserved
- [ ] `named_templates` in `response-templates-v4.yaml` preserved

---

## Critical Data Locations (NEVER DELETE)

```
cortex-brain/
├── tier1/*.db              # Conversations, working memory
├── tier2/*.db              # Knowledge graph, learned patterns  
├── tier3/*.db              # Development context, metrics
├── lessons-learned.yaml    # Accumulated learnings
├── knowledge-graph.yaml    # Relationship mappings
├── user-dictionary.yaml    # Custom terminology
├── documents/              # User-created content
└── response-templates-v4.yaml (named_templates section)
```

---

## References

- Data Preservation: `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md`
- Brain Protection: `cortex-brain/brain-protection-rules.yaml`
- Upgrade Preservation: UPGRADE_BRAIN_PRESERVATION instinct
