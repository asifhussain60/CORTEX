# CORTEX Documentation Generation

This diagram traces the enterprise documentation generation pipeline.

**Discovery Engine** scans Git history, YAML configs, and codebase for features and capabilities.

**Diagrams** generates 14+ Mermaid diagrams illustrating architecture and workflows.

**DALL-E Prompts** creates AI image generation prompts for visual documentation.

**Narratives** writes explanatory text (1:1 with prompts) for each diagram.

**Story** compiles "The Awakening of CORTEX" narrative weaving technical concepts into an engaging story.

**Executive Summary** generates high-level overview with all discovered features.

**MkDocs Site** builds static documentation website with navigation and search.

This pipeline generates comprehensive documentation from a single command, keeping docs in sync with code.