"""Fix corrupted cortex_review_log table schema"""
import sqlite3
from pathlib import Path
import sys

cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.config import config

db_path = config.brain_path / "tier3" / "context.db"
print(f"Fixing database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop incorrect table
print("Dropping incorrect cortex_review_log table...")
cursor.execute("DROP TABLE IF EXISTS cortex_review_log")

# Create correct table
print("Creating correct cortex_review_log table...")
cursor.execute("""
    CREATE TABLE cortex_review_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_timestamp TIMESTAMP NOT NULL,
        review_type TEXT NOT NULL,
        features_reviewed INTEGER NOT NULL DEFAULT 0,
        new_features_found INTEGER NOT NULL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("CREATE INDEX idx_review_timestamp ON cortex_review_log(review_timestamp DESC)")

conn.commit()
conn.close()

print("✅ Fixed cortex_review_log table schema")
