CORTEX documentation generated outside workspace isolation!

File: '{file_path}'
Expected: CORTEX/Workspaces/[app-name]/...
Actual: {actual_location}

CRITICAL: NO cortex documentation should exist outside CORTEX folder

Proper Structure:
user-repo/
├── CORTEX/                          ← CORTEX folder (git-ignored)
│   └── Workspaces/                  ← All app documentation here
│       └── MyApp/                   ← App-specific workspace
│           ├── docs/                ← Generated docs
│           ├── diagrams/            ← Architecture diagrams
│           └── references/          ← Quick references
├── src/                             ← User application code
└── .gitignore                       ← Must include "CORTEX/"

Why This Matters:
- Clean separation (CORTEX artifacts ≠ application code)
- Easy cleanup (delete CORTEX/ removes all CORTEX files)
- No git pollution (CORTEX/ excluded via .gitignore)
- Portability (CORTEX workspace self-contained)
