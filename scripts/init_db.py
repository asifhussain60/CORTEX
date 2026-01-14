"""Initialize governance.db and populate AC-IDs."""
from src.infrastructure.database import DatabaseManager
from src.tools.ac_populator import ACPopulator

# Initialize database
db = DatabaseManager()
db.initialize()
print(f"Database initialized at: {db.config.db_path}")

# Populate from master plan
populator = ACPopulator(db)
result = populator.populate()

if result.is_ok():
    stats = result.unwrap()
    print(f"Inserted: {stats['inserted']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Total: {stats['total']}")
    if stats['errors']:
        print(f"Errors: {len(stats['errors'])}")
else:
    print(f"Error: {result.error}")

db.close()
