from src.orchestrators.tdd_orchestrator import TDDOrchestrator, TDDWorkRequest, TDDPhase
from pathlib import Path
import tempfile

tmpdir = Path(tempfile.mkdtemp())
orch = TDDOrchestrator(tmpdir)

# Create a work request with "email validation" keyword
req = TDDWorkRequest(
    feature_name="Data Validation",
    test_file_path="tests/test_validator.py",
    implementation_file_path="src/validator.py",
    requirements=["Validate email format"]
)

# Get chunks and execute GREEN chunk
chunks = orch.break_into_chunks(req.__dict__)
green_chunk = [c for c in chunks if c.chunk_type == 'method' and c.metadata.get('phase') == TDDPhase.GREEN.value][0]

print(f'Executing GREEN chunk: {green_chunk.description}')
result = orch.execute_chunk(green_chunk)
print(f'Success: {result["success"]}')

# Now search for the pattern
print(f'\nSearching for patterns with "email validation"...')
patterns = orch.tier2.search_patterns(query="email validation", limit=5)
print(f'Patterns found: {len(patterns)}')
for i, p in enumerate(patterns):
    print(f'{i}: {p["title"]} - type={p.get("pattern_type")}')

# Try more general searches
print(f'\nSearching for "email"...')
patterns2 = orch.tier2.search_patterns(query="email", limit=5)
print(f'Patterns found: {len(patterns2)}')

print(f'\nSearching for "Data Validation"...')
patterns3 = orch.tier2.search_patterns(query="Data Validation", limit=5)
print(f'Patterns found: {len(patterns3)}')

# Check what was actually stored
print(f'\nChecking all implementation patterns...')
all_patterns = orch.tier2.get_patterns_by_type('implementation', limit=10)
print(f'Total implementation patterns: {len(all_patterns)}')
for p in all_patterns:
    print(f'  - {p["title"]}')
