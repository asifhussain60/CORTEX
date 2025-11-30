# Conversation Captures

**Purpose:** Temporary storage for manually captured conversations from GitHub Copilot Chat.

## Workflow

1. **CORTEX creates empty file** - When Smart Hint appears, CORTEX auto-creates placeholder file here
2. **You paste conversation** - Copy full conversation from Copilot Chat, paste into the file
3. **CORTEX imports** - Say "import conversation" and CORTEX processes it into the brain
4. **File archived** - After import, file moves to `conversation-vault/` with metadata

## Folder Structure

```
conversation-captures/          # Temporary captures (manual paste)
├── README.md                   # This file
├── YYYY-MM-DD-topic.md        # Pending import (empty → pasted → imported)
└── ...

conversation-vault/            # Archived captures (after import)
├── YYYY/
│   └── MM/
│       └── DD-topic.md       # Processed with quality score & metadata
└── index.json                # Searchable index
```

## File Naming Convention

- Format: `YYYY-MM-DD-topic-description.md`
- Example: `2025-11-13-authentication-implementation.md`
- Keep descriptions concise (3-5 words)
- Use hyphens (not spaces or underscores)

## Next Steps

After pasting conversation:
1. **Import:** Say "import conversation" or "process conversation"
2. **CORTEX will:**
   - Analyze quality score
   - Extract semantic elements
   - Link to active session
   - Move to vault with metadata
   - Update index

---

*This folder is for temporary storage only. Imported conversations move to `conversation-vault/`.*
