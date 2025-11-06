#!/usr/bin/env python3
"""
Generate realistic test data for sql.js performance benchmarking.

Creates a SQLite database with:
- 1000 conversations (simulating KDS conversation history)
- 3000 patterns (simulating extracted knowledge)
- Realistic data sizes and structures

Used in Phase -1 to validate sql.js performance assumptions.
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DB_PATH = Path(__file__).parent / "test-cortex-brain.db"
NUM_CONVERSATIONS = 1000
NUM_PATTERNS = 3000
START_DATE = datetime(2024, 1, 1)

# Sample data for realism
SAMPLE_PROMPTS = [
    "Help me implement user authentication",
    "Review this code for bugs",
    "Create a REST API endpoint",
    "Optimize database queries",
    "Fix the failing tests",
    "Add error handling",
    "Implement caching strategy",
    "Design a data model",
    "Debug performance issues",
    "Write unit tests",
]

SAMPLE_RESPONSES = [
    "I'll help you implement authentication using JWT tokens...",
    "Here's a comprehensive review of your code...",
    "Let's create a REST API with proper error handling...",
    "I've analyzed the queries and found several optimization opportunities...",
    "The tests are failing because of a race condition...",
    "Let's add proper error handling with custom exceptions...",
    "I recommend implementing Redis caching for frequently accessed data...",
    "Here's a normalized data model that supports your requirements...",
    "The performance issue is caused by N+1 queries...",
    "I'll write comprehensive unit tests with mocks...",
]

SAMPLE_PATTERNS = [
    "User prefers TypeScript over JavaScript",
    "Always includes error handling in API endpoints",
    "Follows REST naming conventions",
    "Uses dependency injection for testability",
    "Prefers async/await over callbacks",
    "Writes tests before implementation (TDD)",
    "Documents public APIs with JSDoc",
    "Uses environment variables for configuration",
    "Implements proper logging with structured output",
    "Follows SOLID principles",
]

SAMPLE_CONTEXTS = [
    "authentication system",
    "REST API development",
    "database optimization",
    "test-driven development",
    "error handling patterns",
    "caching strategies",
    "data modeling",
    "performance tuning",
    "code review process",
    "unit testing best practices",
]


def create_schema(conn: sqlite3.Connection) -> None:
    """Create CORTEX schema (Tier 1 + Tier 2)."""
    
    # Tier 1: Working Memory (last 50 conversations)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            tokens_used INTEGER,
            model TEXT,
            metadata TEXT
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
        ON conversations(timestamp DESC)
    """)
    
    # Tier 2: Long-Term Knowledge (patterns with FTS5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            context TEXT,
            confidence REAL DEFAULT 1.0,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            occurrence_count INTEGER DEFAULT 1,
            decay_factor REAL DEFAULT 0.95
        )
    """)
    
    # FTS5 virtual table for full-text search
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
            pattern,
            context,
            content=patterns,
            content_rowid=id
        )
    """)
    
    # Triggers to keep FTS5 in sync
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
            INSERT INTO patterns_fts(rowid, pattern, context)
            VALUES (new.id, new.pattern, new.context);
        END
    """)
    
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
            INSERT INTO patterns_fts(patterns_fts, rowid, pattern, context)
            VALUES ('delete', old.id, old.pattern, old.context);
        END
    """)
    
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
            INSERT INTO patterns_fts(patterns_fts, rowid, pattern, context)
            VALUES ('delete', old.id, old.pattern, old.context);
            INSERT INTO patterns_fts(rowid, pattern, context)
            VALUES (new.id, new.pattern, new.context);
        END
    """)
    
    conn.commit()


def generate_conversations(conn: sqlite3.Connection) -> None:
    """Generate realistic conversation data."""
    
    print(f"Generating {NUM_CONVERSATIONS} conversations...")
    
    conversations = []
    for i in range(NUM_CONVERSATIONS):
        timestamp = START_DATE + timedelta(hours=i)
        prompt = random.choice(SAMPLE_PROMPTS)
        response = random.choice(SAMPLE_RESPONSES) + f" (conversation {i+1})"
        tokens_used = random.randint(500, 4000)
        model = random.choice(["gpt-4", "gpt-3.5-turbo", "claude-3-opus"])
        
        metadata = json.dumps({
            "session_id": f"session-{i // 10}",
            "file_context": random.choice([
                "src/auth.ts",
                "src/api/users.ts",
                "src/models/user.ts",
                "tests/unit/auth.test.ts",
                "src/utils/validation.ts",
            ]),
            "branch": random.choice(["main", "feature/auth", "bugfix/tests"]),
        })
        
        conversations.append((
            timestamp.isoformat(),
            prompt,
            response,
            tokens_used,
            model,
            metadata,
        ))
    
    conn.executemany(
        """
        INSERT INTO conversations (timestamp, prompt, response, tokens_used, model, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        conversations,
    )
    
    conn.commit()
    print(f"✅ Created {NUM_CONVERSATIONS} conversations")


def generate_patterns(conn: sqlite3.Connection) -> None:
    """Generate realistic pattern data."""
    
    print(f"Generating {NUM_PATTERNS} patterns...")
    
    patterns = []
    for i in range(NUM_PATTERNS):
        pattern = random.choice(SAMPLE_PATTERNS) + f" (variant {i % 100})"
        context = random.choice(SAMPLE_CONTEXTS)
        confidence = random.uniform(0.6, 1.0)
        first_seen = START_DATE + timedelta(hours=random.randint(0, NUM_CONVERSATIONS))
        last_seen = first_seen + timedelta(hours=random.randint(1, 100))
        occurrence_count = random.randint(1, 50)
        decay_factor = 0.95
        
        patterns.append((
            pattern,
            context,
            confidence,
            first_seen.isoformat(),
            last_seen.isoformat(),
            occurrence_count,
            decay_factor,
        ))
    
    conn.executemany(
        """
        INSERT INTO patterns (pattern, context, confidence, first_seen, last_seen, occurrence_count, decay_factor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        patterns,
    )
    
    conn.commit()
    print(f"✅ Created {NUM_PATTERNS} patterns")


def generate_statistics(conn: sqlite3.Connection) -> None:
    """Print database statistics."""
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    # Total conversations
    cursor = conn.execute("SELECT COUNT(*) FROM conversations")
    count = cursor.fetchone()[0]
    print(f"Total conversations: {count:,}")
    
    # Total patterns
    cursor = conn.execute("SELECT COUNT(*) FROM patterns")
    count = cursor.fetchone()[0]
    print(f"Total patterns: {count:,}")
    
    # Database size
    db_size_kb = DB_PATH.stat().st_size / 1024
    print(f"Database size: {db_size_kb:.2f} KB")
    
    # Sample query timings (rough estimate in Python)
    import time
    
    # Tier 1 query (last 50 conversations)
    start = time.perf_counter()
    cursor = conn.execute(
        "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT 50"
    )
    results = cursor.fetchall()
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\nTier 1 query (last 50): {elapsed_ms:.2f}ms ({len(results)} rows)")
    
    # Tier 2 FTS5 search
    start = time.perf_counter()
    cursor = conn.execute(
        "SELECT * FROM patterns_fts WHERE patterns_fts MATCH 'authentication' LIMIT 20"
    )
    results = cursor.fetchall()
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"Tier 2 FTS5 search: {elapsed_ms:.2f}ms ({len(results)} rows)")
    
    print("\n⚠️  Note: These are Python SQLite timings.")
    print("   sql.js (WebAssembly) will be 10-20x slower.")
    print("   Run benchmark-sql-js.spec.ts for actual browser performance.")
    print("=" * 50)


def main():
    """Generate test database for sql.js benchmarking."""
    
    print("🧪 CORTEX Phase -1: Test Data Generator")
    print("=" * 50)
    
    # Remove existing database
    if DB_PATH.exists():
        print(f"Removing existing database: {DB_PATH}")
        DB_PATH.unlink()
    
    # Create new database
    print(f"Creating database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    # Enable WAL mode (Write-Ahead Logging) - CORTEX default
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    
    try:
        # Create schema
        create_schema(conn)
        
        # Generate data
        generate_conversations(conn)
        generate_patterns(conn)
        
        # Print statistics
        generate_statistics(conn)
        
        print(f"\n✅ Test database created successfully!")
        print(f"📁 Location: {DB_PATH}")
        print(f"\n🚀 Next step: Run benchmark-sql-js.spec.ts")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
