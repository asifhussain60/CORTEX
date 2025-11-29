"""Debug why test files aren't found."""
from pathlib import Path
from src.validation.test_coverage_validator import TestCoverageValidator

project_root = Path(__file__).parent
validator = TestCoverageValidator(project_root)

# Test each feature
features = [
    ("SetupEPMOrchestrator", "orchestrator"),
    ("ADOWorkItemOrchestrator", "orchestrator")
]

for name, ftype in features:
    print(f"\n{'='*60}")
    print(f"Searching for: {name}")
    print('='*60)
    
    # Strip Impl suffix if needed
    base_name = name[:-4] if name.endswith("Impl") else name
    print(f"Base name: {base_name}")
    
    # Convert to snake case
    snake_name = validator._snake_case(base_name)
    print(f"Snake case: {snake_name}")
    
    # Expected test file name
    test_name = f"test_{snake_name}.py"
    print(f"Expected test filename: {test_name}")
    
    # Search paths
    search_paths = [
        validator.tests_root / "orchestrators",
        validator.tests_root / "operations" / "modules",
        validator.tests_root / "workflows",
        validator.tests_root / "operations"
    ]
    
    print(f"\nSearch paths:")
    for path in search_paths:
        print(f"  {path.relative_to(project_root)} (exists: {path.exists()})")
    
    # Search recursively
    print(f"\nSearching for {test_name} recursively...")
    found_files = []
    for search_path in search_paths:
        if not search_path.exists():
            continue
        for test_file in search_path.rglob(test_name):
            found_files.append(test_file)
            print(f"  ✓ Found: {test_file.relative_to(project_root)}")
    
    if not found_files:
        print(f"  ✗ No files found")
        
        # List what IS in tests/orchestrators
        orchestrators_dir = validator.tests_root / "orchestrators"
        if orchestrators_dir.exists():
            print(f"\nFiles in {orchestrators_dir.relative_to(project_root)}:")
            for f in sorted(orchestrators_dir.glob("*.py")):
                print(f"  - {f.name}")
