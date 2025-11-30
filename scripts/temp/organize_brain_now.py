"""Organize existing brain documents for real."""
from src.workflows.document_organizer import organize_brain_documents
from pathlib import Path

print("=" * 60)
print("ORGANIZING BRAIN DOCUMENTS")
print("=" * 60)

result = organize_brain_documents(Path('cortex-brain'), dry_run=False)

print(f"\nDocuments organized: {len(result['results']['success'])}")
print(f"Failed: {len(result['results']['failed'])}")
print(f"Skipped: {len(result['results']['skipped'])}")

print("\n" + "=" * 60)
print("Final Statistics:")
print("=" * 60)
for category, count in result['statistics']['categories'].items():
    if count > 0:
        print(f"  {category}: {count} documents")
print(f"\nTotal: {result['statistics']['total_documents']} documents")

print("\n✅ Organization complete!")
print(f"📁 Indexes updated for all categories")
