# Mind Palace Brain - Quick Reference

**🎯 One-Page Cheat Sheet for Mind Palace Tier 4**

---

## ⚡ Quick Commands

### Initialize Mind Palace in Brain
```bash
python scripts/init-mind-palace-brain.py
```

### Check Progress
```sql
SELECT * FROM tier4_mind_palace_progress;
```

### Mark Chapter Complete
```sql
UPDATE tier4_mind_palace_chapters
SET status = 'complete', 
    has_story = 1, has_cartoon_prompt = 1, 
    has_diagram_prompt = 1, has_technical_docs = 1,
    completed_at = datetime('now')
WHERE chapter_id = 'ch-002-four-tier-mind';
```

### Add Metaphor Mapping
```sql
INSERT INTO tier4_metaphor_mappings (
    mapping_id, chapter_id, story_character, 
    technical_component, file_location, component_type, is_validated
) VALUES (
    'map-ch002-001', 'ch-002-four-tier-mind', 
    'The Three-Story Brain Tower', 'CORTEX 4-Tier Architecture',
    'cortex-brain/schema.sql', 'architecture', 1
);
```

---

## 📊 Key Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `tier4_mind_palace_chapters` | Chapter tracking | chapter_number, title, status |
| `tier4_metaphor_mappings` | Story→Tech mapping | story_character, technical_component |
| `tier4_image_prompts` | Image generation | prompt_type, is_generated |
| `tier4_chapter_references` | Dependencies | from_chapter_id, to_chapter_id |
| `tier4_mind_palace_progress` | Overall stats | completed_chapters, total_chapters |

---

## 🔍 Essential Queries

### Progress Overview
```sql
SELECT 
    completed_chapters || '/' || total_chapters as progress,
    ROUND(completed_chapters * 100.0 / total_chapters, 1) || '%' as pct
FROM tier4_mind_palace_progress;
```

### Incomplete Chapters
```sql
SELECT chapter_number, title, status
FROM tier4_mind_palace_chapters
WHERE status != 'complete'
ORDER BY chapter_number;
```

### All Metaphors
```sql
SELECT c.chapter_number, m.story_character, m.technical_component
FROM tier4_metaphor_mappings m
JOIN tier4_mind_palace_chapters c ON m.chapter_id = c.chapter_id
ORDER BY c.chapter_number;
```

---

## 📝 Chapter Workflow

1. **Create Chapter** (using template)
2. **Write Content** (Story + Images + Technical)
3. **Update Brain** (Mark sections complete)
4. **Add Metaphors** (Map story to code)
5. **Track Images** (Record prompts, mark generated)
6. **Mark Complete** (Update status)

---

## 🎯 Chapter Status Values

- `draft` - Work in progress
- `review` - Ready for review
- `complete` - All sections done
- `published` - Released to users

---

## 📖 Documentation

- **Full Guide:** `docs/Mind-Palace/BRAIN-INTEGRATION.md`
- **Summary:** `docs/Mind-Palace/INTEGRATION-SUMMARY.md`
- **Template:** `templates/mind-palace-chapter-template.md`
- **Schema:** `cortex-brain/schema.sql` (Tier 4 section)

---

## 🚀 Reading Paths

```sql
-- Get beginner path
SELECT beginner_path FROM tier4_mind_palace_progress;

-- Get developer path
SELECT developer_path FROM tier4_mind_palace_progress;
```

---

**Version:** 1.0 | **Updated:** 2025-11-06 | **Status:** ✅ Active
