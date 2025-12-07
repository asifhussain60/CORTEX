from src.orchestrators.tdd_orchestrator import TDDOrchestrator, TDDWorkRequest, TDDPhase
from pathlib import Path
import tempfile

tmpdir = Path(tempfile.mkdtemp())
orch = TDDOrchestrator(tmpdir)
req = TDDWorkRequest('Test', 'test.py', 'impl.py', ['requirement'])
chunks = orch.break_into_chunks(req.__dict__)

print(f'Total chunks: {len(chunks)}')
for i, c in enumerate(chunks):
    print(f'{i}: type={c.chunk_type}, phase={c.metadata.get("phase")}, desc={c.description[:60]}')

# Find TEST chunk (actual RED phase, not skeleton)
test_chunks = [c for c in chunks if c.chunk_type == 'test' and c.metadata.get('phase') == TDDPhase.RED.value]
print(f'\nTEST chunks (type=test, phase=red): {len(test_chunks)}')
if test_chunks:
    print(f'Executing TEST chunk (index {chunks.index(test_chunks[0])})...')
    result = orch.execute_chunk(test_chunks[0])
    print(f'Result: {result["success"]}')

    
    # Check tier1
    print(f'\nChecking Tier 1...')
    tier1_data = orch.tier1.get_recent_test_intents(limit=5)
    print(f'Test intents found: {len(tier1_data)}')
    for intent in tier1_data:
        print(f'  - {intent["feature_name"]}: {intent["requirement"]}')
