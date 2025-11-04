# Mock Test Project

**Purpose:** Minimal project structure for testing KDS setup and independence.

**Type:** .NET 8.0 + React (simulated)

**Structure:**
```
mock-project/
├── .git/                    # Simulated git repository
├── src/
│   ├── MyApp/              # .NET backend
│   │   ├── Controllers/
│   │   ├── Services/
│   │   └── MyApp.csproj
│   └── frontend/           # React frontend
│       ├── src/
│       │   └── components/
│       └── package.json
├── tests/
│   ├── Unit/
│   └── UI/
└── KDS/                    # KDS will be installed here
```

**Usage:**
This mock project is used to validate:
- ✅ KDS setup wizard can detect project type
- ✅ Dynamic path resolution works correctly
- ✅ No hard-coded paths break on different locations
- ✅ Configuration templates generate properly
- ✅ BRAIN initializes with clean state

**Notes:**
- No actual build required (minimal files)
- Git repository simulated (no real commits needed)
- Represents typical enterprise project structure
- Used for automated testing of KDS independence

**Created:** November 4, 2025  
**Part of:** KDS Independence Project - Phase 0.2
