---
title: Pattern Router (Trie)
---

The Pattern Router maps user intents to orchestrators using a Trie:

- O(1) style matching for known patterns
- Avoids slow “scan everything” routing
- Enables consistent, testable behavior

It’s routing as a data structure, not as a pile of if-statements.
