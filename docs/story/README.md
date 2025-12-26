# The Awakening of CORTEX - Story Viewer

Interactive story viewer for "The Awakening of CORTEX: A Tech Comedy in 12 Chapters"

## Structure

```
story/
├── viewer.html              # Main story viewer page (entry point)
├── story-viewer.js          # JavaScript for chapter loading and navigation
├── Prologue/                # Prologue chapter
│   └── PROLOGUE.txt
├── Chapter-01/ through Chapter-12/  # Story chapters
│   └── CHAPTER-XX.txt
└── illustrations/
    └── images/
        ├── essentials/      # Core chapter illustrations
        └── valuable/        # Additional chapter illustrations
```

## Features

- **Interactive Navigation**: Left sidebar with all chapters
- **Contextual Images**: Images embedded within narrative text
- **Responsive Design**: Mobile-friendly layout
- **Glassmorphism Theme**: Consistent with CORTEX documentation
- **Chapter Progress**: Previous/Next navigation at bottom

## Git Pages URL

When published, access via:
- Production: `https://asifhussain60.github.io/CORTEX/story/viewer.html`
- Direct link from main site: "The Awakening of CORTEX" button

## Local Testing

Open `viewer.html` directly in browser:
```bash
open docs/story/viewer.html
```

Or use a local server:
```bash
cd docs/story
python3 -m http.server 8000
# Visit: http://localhost:8000/viewer.html
```

## File Paths

All paths are relative to `viewer.html` location:
- Chapter files: `Chapter-XX/CHAPTER-XX.txt`
- Images: `illustrations/images/essentials/` and `valuable/`
- Assets: `../assets/` (CORTEX logo, CSS)

## Chapter Configuration

Chapters configured in `story-viewer.js` with:
- Chapter metadata (title, word count, type)
- Image associations (linked by chapter number in filename)
- Navigation flow (previous/next)

## Author

Asif Hussain | Copyright © 2025 Asif Hussain. All rights reserved.
