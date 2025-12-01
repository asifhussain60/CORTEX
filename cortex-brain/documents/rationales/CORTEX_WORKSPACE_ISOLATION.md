CORTEX_WORKSPACE_ISOLATION: Repository Organization Standard

Real incident (2025-11-17):
- User: "onboarding app creates docs in repo root, not CORTEX folder"
- Published onboarding generates: user-repo/docs/onboarding.md
- CORTEX artifacts polluting user's application repository
- Cleanup difficult (which docs are CORTEX vs application?)
- .gitignore cannot exclude selectively

Why Workspace Isolation Critical:

1. Repository Cleanliness:
   - User repo = user's application code only
   - CORTEX artifacts = temporary scaffolding
   - Clear boundary prevents confusion
   Example: docs/ could be user's actual docs or CORTEX-generated

2. Easy Cleanup:
   - Delete CORTEX/ → all CORTEX artifacts gone
   - No hunting for scattered CORTEX files
   - Uninstall = single folder removal
   Example: rm -rf CORTEX/ vs finding 47 scattered files

3. Git Isolation:
   - Add "CORTEX/" to .gitignore once
   - No CORTEX artifacts ever committed to user repo
   - No accidental commits of temporary scaffolding
   Example: CORTEX workspace excluded, user code included

4. Portability:
   - CORTEX workspace self-contained
   - Can backup/restore entire CORTEX state
   - Can sync across machines if desired
   Example: Copy CORTEX/ to new machine = full context restored

5. Multi-Application Support:
   - CORTEX can work with multiple applications
   - Each app gets isolated workspace
   - No cross-contamination of artifacts
   Example: CORTEX/Workspaces/AppA/, CORTEX/Workspaces/AppB/

Proper Workspace Structure:

```
user-application-repo/
├── CORTEX/                          ← Git-ignored CORTEX folder
│   ├── .cortex-metadata.json        ← Workspace metadata
│   └── Workspaces/                  ← All application workspaces
│       ├── MyApp/                   ← Application-specific workspace
│       │   ├── docs/                ← Generated documentation
│       │   │   ├── onboarding.md
│       │   │   ├── architecture-overview.md
│       │   │   └── quick-reference.md
│       │   ├── diagrams/            ← Architecture diagrams
│       │   │   ├── component-diagram.mmd
│       │   │   ├── data-flow.mmd
│       │   │   └── images/          ← Rendered images
│       │   ├── references/          ← Quick references
│       │   │   └── api-quick-ref.md
│       │   └── analysis/            ← Code analysis reports
│       │       └── complexity-report.json
│       └── AnotherApp/              ← Another application
│           └── docs/
│               └── onboarding.md
├── src/                             ← User's actual application code
│   └── MyApp/
├── tests/                           ← User's tests
├── README.md                        ← User's README
└── .gitignore                       ← Must include "CORTEX/"
```

Implementation Changes Required:

1. PageGenerator (src/epm/modules/page_generator.py):
   Before:
   ```python
   self.output_path = root_path / "docs"
   ```
   
   After:
   ```python
   app_name = context.get('app_name', 'UnknownApp')
   self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "docs"
   ```

2. DiagramGenerator (src/epm/modules/diagram_generator.py):
   Before:
   ```python
   self.output_path = root_path / "docs"
   ```
   
   After:
   ```python
   app_name = context.get('app_name', 'UnknownApp')
   self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
   ```

3. ImagePromptGenerator (src/epm/modules/image_prompt_generator.py):
   Before:
   ```python
   self.output_dir = Path(output_dir)  # Typically docs/diagrams
   ```
   
   After:
   ```python
   app_name = context.get('app_name', 'UnknownApp')
   self.output_dir = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
   ```

4. Onboarding Orchestrator Context:
   Add app_name to session context:
   ```python
   session_context = {
       "app_name": self._detect_app_name(root_path),  # From solution file, csproj, package.json
       "profile": profile.value,
       "project_root": self.project_root,
       ...
   }
   ```

5. .gitignore Creation:
   Onboarding MUST create/update user repo's .gitignore:
   ```gitignore
   # CORTEX AI Assistant (local workspace, not committed)
   CORTEX/
   ```

Benefits:
- Clean separation: CORTEX ≠ Application
- Easy uninstall: Delete CORTEX/ folder
- No git pollution: Single .gitignore entry
- Multi-app support: Isolated workspaces
- Portable: Self-contained CORTEX state

Enforcement:
- Brain Protector blocks operations writing outside CORTEX/
- Integration tests verify output paths
- Onboarding validates workspace structure
- Design sync validates isolation maintained

Exception: Shared CORTEX Installation
If user wants to share CORTEX across projects (not per-repo):
- Install CORTEX once (e.g., ~/CORTEX/)
- Each repo references shared CORTEX
- Workspaces still isolated: ~/CORTEX/Workspaces/[app-name]/
- This is advanced configuration (document separately)
