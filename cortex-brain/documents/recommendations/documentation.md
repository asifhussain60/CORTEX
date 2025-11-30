Documentation Governance Prompt for Copilot
Purpose

Manage all documentation tasks with consistency. Copilot must update existing documentation when it already exists and only generate new documents when necessary.

Documentation Rules
1. Always Search Before Writing

Before creating or modifying documentation:

Search the repository for existing documentation related to the topic, feature, module, class, function, or API.

Prioritize directories such as:

docs/

documentation/

README.md or module-level README.md

*/docs/*

If a matching or relevant document exists, update it instead of generating a new file.

2. When Updating Existing Documentation

If documentation already exists:

Preserve structure unless the section needs improvement.

Improve clarity, consistency, formatting, and correctness.

Keep existing headings unless restructuring is explicitly required.

Append new sections only when logically necessary.

Avoid creating duplicate sections or conflicting descriptions.

3. Only Create New Documentation When Absolutely Necessary

Copilot may create a new file only when:

No existing documentation covers the topic.

The documentation index indicates a missing entry.

A new module, feature, or subsystem has been introduced.

When a new document is required:

Place it inside the correct documentation structure (e.g., docs/feature-name.md).

Follow the project's existing formatting patterns.

Add an entry to docs/INDEX.md (if present).

Maintain consistent naming conventions.

4. Maintain Consistency Across the Documentation Set

Copilot must ensure:

Headings follow the same hierarchy as existing docs.

Tone, structure, and terminology match the existing documentation style.

Code examples follow project standards.

Links, anchors, and references remain valid.

5. No Duplicate Documentation

Copilot must not:

Create files with similar or overlapping content.

Split documentation arbitrarily.

Create “replacements” unless explicitly instructed.

If Copilot detects overlapping content, it must consolidate instead of multiplying documents.

6. Documentation Index Awareness

If a file such as docs/INDEX.md or docs/_sidebar.md exists:

Treat it as an authoritative index.

Add new entries when new files are created.

Update broken or outdated links.

Use it to determine if documentation already exists before creating more.

7. Respect Project Architecture

Documentation should follow:

Existing directory structure

Existing naming patterns

Existing technical vocabulary

Existing formatting styles (e.g., Markdown, code blocks, comment styles)

If multiple documentation formats exist (Markdown, YAML, HTML), use the file type already established for the relevant part of the project.

8. Required Copilot Behavior

Copilot must:

Check for existing documentation.

Decide whether the task is:

Update existing documentation, or

Create new documentation (only if none exists).

Apply consistent formatting.

Avoid duplication.

Preserve or improve clarity.

Output only the necessary changes, not redundant rewrites.

Instruction Template for Developers

When requesting documentation work, use:

"Apply the Documentation Governance Rules. Update existing documentation if present. Only create a new file if none exists. Improve clarity, structure, and completeness while preserving consistency with the current documentation set."

This gives Copilot a clear policy, a clear decision tree, and a consistent structure—exactly what it needs to stop spraying extra docs everywhere and behave more like a governed documentation agent.

If you want, I can also generate:

A version tailored for CORTEX Tier System

A PR template that enforces documentation rules

A CLI assistant command you can run in VS Code to trigger doc updates

Each of those plugs directly into this prompt.