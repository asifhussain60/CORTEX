# Direct Import Mode - Quick User Guide

## 🎯 What Is Direct Import?

**Before (Template Mode):**
```bash
1. /CORTEX capture conversation          # Creates empty template
2. Copy conversation from Copilot Chat
3. Paste into template file
4. Save file
5. /CORTEX import [capture_id]           # Finally imports
```

**After (Direct Import Mode):**
```bash
1. Save conversation to a file
2. /CORTEX capture conversation file:conversation.txt   # Done! ✅
```

---

## 🚀 Quick Start

### Single File Import

```bash
/CORTEX capture conversation file:my_conversation.txt
```

**Expected Output:**
```
🧠 Direct Import Completed! 

✅ Batch Import Summary
- Total Files: 1
- Successful: 1
- Failed: 0

📊 Import Details:
✅ `my_conversation.txt`
   - Conversation ID: `conv_20251117_123045_a1b2c3`
   - Messages: 4
   - Entities: 3

🔗 Context Continuity NOW ACTIVE
All imported conversations are now in CORTEX working memory!

🎉 No template files created - Direct import mode!
```

### Multiple Files (Batch)

```bash
/CORTEX capture conversation file:conv1.txt file:conv2.txt file:conv3.txt
```

**Result:** All 3 files imported in one command!

---

## 📝 File Format

Your conversation file should use this format:

```
You: Can you help me with authentication?

Copilot: Sure! Here's how authentication works in your system:
1. User submits credentials
2. AuthService validates
3. JWT token is generated

You: What about password hashing?

Copilot: The system uses bcrypt for password hashing with 10 rounds.
This protects passwords even if the database is compromised.
```

**Key Points:**
- Use `You:` for your messages
- Use `Copilot:` for Copilot responses
- Empty lines between exchanges are okay
- Code blocks and formatting are preserved
- File names, class names, functions are auto-extracted

---

## 🛠️ Use Cases

### Use Case 1: Importing Old Conversations

You have conversations saved in text files from previous work sessions:

```bash
# Import all conversations from a directory
/CORTEX capture conversation file:~/old-conversations/auth-discussion.txt file:~/old-conversations/api-design.txt
```

### Use Case 2: Sharing Conversations with Team

A teammate shares a conversation file with you:

```bash
# Import their conversation directly
/CORTEX capture conversation file:teammate-solution.txt
```

### Use Case 3: Bulk Import from Backup

You have a backup folder with multiple conversation files:

```bash
# Import entire backup (list all files)
/CORTEX capture conversation file:backup/conv1.txt file:backup/conv2.txt file:backup/conv3.txt
```

---

## ⚠️ Common Issues & Solutions

### Issue: "File not found"

**Solution:** Check your file path
```bash
# Use absolute path
/CORTEX capture conversation file:/Users/you/conversations/conv.txt

# Or workspace-relative path
/CORTEX capture conversation file:conversations/conv.txt
```

### Issue: "No valid conversation messages found"

**Solution:** Check your file format
- Must use `You:` and `Copilot:` labels
- Each label must be followed by message content
- Empty files won't work

### Issue: Some files succeed, others fail

**This is okay!** Direct import allows partial success:

```
🧠 Direct Import Completed! 

✅ Batch Import Summary
- Total Files: 3
- Successful: 2
- Failed: 1

📊 Import Details:
✅ `conv1.txt` - Success
✅ `conv2.txt` - Success
❌ `conv3.txt` - Error: File not found
```

---

## 🔄 Backward Compatibility

**Template mode still works!** If you prefer the old workflow:

```bash
# Old way (still works)
/CORTEX capture conversation           # Creates template
# (paste conversation into file)
/CORTEX import [capture_id]            # Import from template
```

**Direct import is optional** - use whichever method you prefer!

---

## 💡 Tips & Tricks

### Tip 1: Save Conversations as You Go

Instead of copying from Copilot Chat after the fact, save interesting conversations to files as you work:

```bash
# During your work session
cat > auth-discussion.txt
You: How does authentication work?
Copilot: [paste response here]
^D

# Later, import all at once
/CORTEX capture conversation file:auth-discussion.txt file:api-design.txt
```

### Tip 2: Use Descriptive File Names

```bash
# Good names (self-documenting)
authentication-implementation.txt
bug-fix-null-reference.txt
api-redesign-discussion.txt

# Bad names (unclear)
conv1.txt
temp.txt
new.txt
```

### Tip 3: Combine with Git

```bash
# Track conversations in version control
mkdir conversations/
git add conversations/*.txt
git commit -m "Save CORTEX conversations"

# Import from git-tracked folder
/CORTEX capture conversation file:conversations/*.txt
```

---

## 📊 What Gets Extracted

CORTEX automatically extracts:

| Entity Type | Example | How It's Used |
|-------------|---------|---------------|
| **Files** | `AuthService.cs` | Tracks which files you discussed |
| **Classes** | `class UserController` | Links to codebase architecture |
| **Functions** | `def authenticate()` | Remembers method discussions |
| **Concepts** | "authentication", "JWT" | Semantic search in future |

This extracted data powers CORTEX's context continuity!

---

## 🎉 Benefits

**Speed:**
- 🚀 One command vs 5-step workflow
- ⚡ Batch import multiple files at once
- ✅ No manual copy/paste required

**Flexibility:**
- 📁 Import from anywhere on your filesystem
- 🔄 Partial success allowed (some files can fail)
- 💾 Keep conversation files for backup/sharing

**Compatibility:**
- ✅ Old template mode still works
- 🔄 No breaking changes
- 📦 Choose the method that fits your workflow

---

## ❓ FAQ

**Q: Can I use relative paths?**  
A: Yes! Both absolute and workspace-relative paths work.

**Q: What if a file doesn't exist?**  
A: That file will fail, but other files in the batch will still import.

**Q: Can I import the same file twice?**  
A: Yes, but CORTEX will create duplicate conversations. Use unique files for best results.

**Q: What file formats are supported?**  
A: Plain text (`.txt`), Markdown (`.md`), or any UTF-8 encoded file with `You:`/`Copilot:` format.

**Q: Can I mix template mode and direct import?**  
A: Yes! Use whichever method fits the situation.

**Q: Do I need to run any setup command?**  
A: No! Direct import mode is ready to use immediately after implementation.

---

## 📚 Learn More

- **Technical Details:** See `DIRECT-IMPORT-IMPLEMENTATION-SUMMARY.md`
- **Planning Document:** See `CONVERSATION-CAPTURE-DIRECT-MODE-ENHANCEMENT.md`
- **Original Conversation Capture:** See CORTEX documentation for template mode usage

---

**Created:** 2025-11-17  
**Version:** 1.0  
**Status:** Ready to Use ✅
