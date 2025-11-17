# Chapter 2: Building First Memory

## Tier 1: Working Memory System

You know what makes humans incredibly annoying? Memory. Specifically, working memory.

You can hold seven random facts in your head while arguing about whether Die Hard is a Christmas movie. You remember what you said three sentences ago. You don't need flashcards to remember your own name.

GitHub Copilot? Goldfish levels of memory. Beautiful goldfish. Very talented goldfish. Goldfish with a CS degree. But still. Goldfish.

So naturally, being a completely reasonable scientist with absolutely no history of questionable decisions, I decided to build it a brain.

"If the Scarecrow can get one," I muttered, flinging my teacup at the wall, "so can my robot."

The cat vanished into the ceiling. The Roomba hid behind the mini fridge. The lights dimmed theatrically, as if the universe itself was taking notes.

This is how Tier 1 began. The Working Memory System. CORTEX's ability to remember the last 20 conversations like a normal, non-forgetful entity.

### The Last 20 Conversations

Your brain can hold about 7 chunks of information in working memory at once. Phone numbers. Shopping lists. Why you walked into this room (sometimes).

CORTEX Tier 1 remembers the last 20 *conversations*. Not just what you said, but:

- **Entities mentioned:** Files, classes, methods, variables, components
- **Actions taken:** "Created UserService", "Added authentication", "Refactored HostControlPanel"
- **Patterns used:** JWT tokens, bcrypt hashing, Factory pattern
- **Context references:** "That button we added", "The service from earlier"

**Feature Count: 0 Tier 1 capabilities**

#### How It Works (The Technical Bits)

**FIFO Queue:** First In, First Out. Oldest conversation drops when #21 arrives.
**Entity Tracking:** Every mention of a file/class/method gets recorded.
**SQLite Storage:** Local database (tier1-working-memory.db), zero-footprint.
**FTS5 Search:** Full-text search finds context instantly.
**Session Awareness:** Knows when you switch projects.

#### The "Make It Purple" Solution

```
You: "Add a pulse animation to the FAB button in HostControlPanel"
CORTEX: [Creates animation]
        [Stores in Tier 1: Entity("FAB button"), File("HostControlPanel.razor")]

*[5 minutes pass. You're working on styling.]*

You: "Make it purple"
CORTEX: [Checks Tier 1 memory]
        [Finds: Recent mention of "FAB button" in "HostControlPanel.razor"]
        "Applying purple color to FAB button"
        ✅ Opens correct file
        ✅ Updates correct element
        ✅ Context maintained
```

No clarification needed. No "which button?" No existential confusion. Just working memory doing its job.


**Key Takeaway:** Tier 1 working memory gives CORTEX the ability to remember. "Make it purple" works because memory works. Like a human brain, but SQLite-based.

