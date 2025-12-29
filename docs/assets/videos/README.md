# CORTEX Video Assets

This folder contains video tutorials and demonstrations for CORTEX documentation.

## Videos

### Setup Tutorial
- **File:** `cortex-setup-tutorial.mp4`
- **Duration:** 10:45
- **Resolution:** 1920x1080 (Full HD)
- **Format:** MP4 (H.264)
- **Purpose:** Complete CORTEX setup walkthrough from installation to first TDD workflow
- **Integrated in:** `docs/getting-started/index.html`

## Usage

Videos are embedded in the documentation site using HTML5 `<video>` tags:

```html
<video controls poster="../assets/images/CORTEX-logo.png">
    <source src="../assets/videos/cortex-setup-tutorial.mp4" type="video/mp4">
    Your browser doesn't support video playback.
</video>
```

## File Size Guidelines

- Keep videos under 50MB for optimal loading
- Use H.264 codec for broad compatibility
- Include captions (SRT format) in same directory
- Use CORTEX logo as poster image

## Generation

Videos are generated using the prompts in:
`cortex-brain/documents/templates/gemini-video-tutorial-prompt.md`
