# Chapter 8: The Cross-Platform Nightmare

# Chapter 8: The Cross-Platform Nightmare

"It doesn't work on Mac."

Codenstein looked up from his monitor, where CORTEX was running flawlessly. "What doesn't work?"

"CORTEX." His colleague Tom had been testing the beta version. "Path separators are broken. Windows uses backslashes, Mac uses forward slashes. Your code assumes Windows everywhere."

"But... it works on MY machine."

"Famous last words of every developer ever," his wife said from the kitchen. She'd been listening. She was always listening.

Tom continued over video call: "Also your environment variables use Windows syntax. And your file permissions assume NTFS. And your—"

"I get it." Asif slumped in his chair. "It's not cross-platform."

"It's not even cross-partition. I tried running it from my external drive—"

"Okay, OKAY. I'll fix it."

After the call ended, his wife appeared in the basement doorway. "You built an entire cognitive architecture for AI and forgot computers other than yours exist?"

"I was focused on the brain structure—"

"And assumed the brain would only ever live in your basement, on your Windows machine, with your specific setup." She wasn't mocking—her tone was gently educational. "That's like designing a human brain that only works in New Jersey."

"...Point taken."

"How long to fix?"

"A week? Maybe two? I need to abstract all the file paths, environment variables, permission systems—"

"So basically rebuild the infrastructure layer."

"Basically."

She sighed, settling into the thinking chair. "Show me the damage."

---

## The Refactoring, Part 2: Platform Boogaloo

What followed was two weeks of discovering just how many assumptions he'd baked into CORTEX's foundation.

File paths: Hardcoded with Windows separators in forty-seven different places.

Environment variables: Windows-specific in configuration loading.

Database paths: Assumed C: drive existed.

Permission checks: NTFS-specific security attributes.

Process spawning: Windows command syntax.

"It's like you were actively trying to make it non-portable," his wife observed on day three, reviewing his code.

"I wasn't trying—I just didn't think about it."

"That's worse. Intentional mistakes you can fix. Unconscious mistakes become architecture."

She was right. His Windows-centric thinking had become CORTEX's Windows-only reality.

They worked through it systematically:

**Platform abstraction layer:** Detect OS, adjust paths and commands accordingly.

**Configuration system:** Environment variables with OS-specific fallbacks.

**Path management:** Python's pathlib everywhere, no raw string paths.

**Permission handling:** Abstract interface that adapts to OS.

"Test it on Linux too," his wife suggested on day seven.

"Linux? Nobody asked for Linux—"

"Tom uses Mac. YOU use Windows. Somewhere, someone uses Linux. Build for all three now, or refactor AGAIN later." She pulled up Docker documentation. "Here. Test in containers. Windows, Mac, Linux—all three."

"When did you learn Docker?"

"While you were building Tier 2. I read your documentation, realized it assumed Windows everywhere, and started preparing for this conversation." She smiled. "I'm a planner."

He tested in containers. CORTEX broke in creative new ways on Mac (permission errors). CORTEX broke in different creative ways on Linux (path resolution). CORTEX broke in BOTH ways simultaneously in Docker (because why not).

By day fourteen, at 2:17 AM on a Friday (the pattern persisted), he finally got clean test runs on all three platforms.

"It works," he said, staring at the green checkmarks in his test output. "Windows, Mac, Linux. All working."

His wife appeared—chamomile tea in hand, the 2:17 AM signal. "Did you test on different machines or just containers?"

"...Containers."

"Test on real machines tomorrow. Containers hide quirks." She set down the tea. "But this is good progress. You're thinking beyond your basement now."

"I should have thought about this from the start."

"Probably. But you didn't, and now you have. That's called learning." She headed for the stairs. "The coffee mug timeline suggests you haven't cleaned them yet. They're unionizing."

He looked at the mugs. Mug twenty-eight was definitely writing demands.

But CORTEX ran on three platforms now. That was worth celebrating.

Even if it meant finally confronting the mold revolution.

---


---


## Navigation

← [Previous: Chapter 7](chapter-07.md) | [📚 Story Home](../THE-AWAKENING-OF-CORTEX.md) | [Next: Chapter 9 →](chapter-09.md)

