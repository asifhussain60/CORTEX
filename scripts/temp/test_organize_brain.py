"""Test script to organize existing brain documents."""
from src.workflows.document_organizer import organize_brain_documents
from pathlib import Path

# Dry run first
print("=" * 60)
print("DRY RUN - Preview document organization")
print("=" * 60)

result = organize_brain_documents(Path('cortex-brain'), dry_run=True)

print(f"\nDocuments to organize: {len(result['results']['success'])}")
print(f"Failed: {len(result['results']['failed'])}")
print(f"Skipped: {len(result['results']['skipped'])}")

print("\nSample operations (first 15):")
for op in result['results']['success'][:15]:
    print(f"  - {op}")

print("\n" + "=" * 60)
print("Statistics after organization:")
print("=" * 60)
for category, count in result['statistics']['categories'].items():
    print(f"  {category}: {count} documents")
print(f"\nTotal: {result['statistics']['total_documents']} documents")
