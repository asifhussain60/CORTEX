# Database Crawler - SQL File Priority Enhancement

**Date:** 2025-11-04  
**Version:** 1.1.0  
**Status:** ✅ Implemented

---

## 🎯 Enhancement Summary

The database crawler now prioritizes discovering SQL schema and data files **BEFORE** attempting database connections. This makes it easier and faster for the brain to understand database structure without needing live database access.

---

## 📋 Discovery Priority (New Workflow)

### Priority 1: SQL Schema/Data Files (Fastest, Easiest) ⚡

**Scans for:**
- `*schema*.sql` - Schema/DDL files
- `*ddl*.sql` - Data Definition Language
- `*create*.sql` - CREATE TABLE statements
- `*structure*.sql` - Database structure
- `*data*.sql` - Data/DML files
- `*dml*.sql` - Data Manipulation Language
- `*insert*.sql` - INSERT statements
- `*seed*.sql` - Seed data

**What it extracts:**
- ✅ File type (schema/data/mixed)
- ✅ Statement counts (CREATE TABLE, INSERT, etc.)
- ✅ Referenced table names
- ✅ File size and line counts
- ✅ DDL vs DML distribution

**Benefits:**
- ✅ **No database connection needed** - Works offline
- ✅ **Fast** - File scanning vs database queries
- ✅ **Safe** - No credentials, no network access
- ✅ **Version controlled** - SQL files in Git = history
- ✅ **Brain-friendly** - Easy to reference in prompts

### Priority 2: Configuration Discovery

**Scans for:**
- Connection strings (appsettings.json, web.config, .env)
- Database provider detection
- Entity models and DbContext files
- Migration files

### Priority 3: Live Database Connection (Only if Needed)

**Triggers connection only if:**
- ❌ No SQL schema files found **AND**
- ✅ Connection string available

**OR**

- ✅ Explicitly requested via `-ConnectAndCrawl` flag

**If no connection string:**
- Prompts user to provide one
- Memorizes it to `KDS/kds-brain/database-connection.txt`
- Reuses for future crawls

---

## 🔍 SQL File Analysis

### Schema File Example

**File:** `database/schema.sql`

```sql
CREATE TABLE Users (
    Id INT PRIMARY KEY,
    Username NVARCHAR(50),
    Email NVARCHAR(100)
);

CREATE TABLE Sessions (
    Id INT PRIMARY KEY,
    UserId INT FOREIGN KEY REFERENCES Users(Id),
    StartTime DATETIME
);

CREATE INDEX IX_Users_Email ON Users(Email);
```

**Extracted Info:**
```json
{
  "file": "database/schema.sql",
  "type": "schema",
  "statement_counts": {
    "create_table": 2,
    "create_index": 1,
    "insert": 0
  },
  "tables_referenced": ["Users", "Sessions"],
  "file_size_kb": 2.5,
  "estimated_lines": 45
}
```

### Data File Example

**File:** `database/seed-data.sql`

```sql
INSERT INTO Users (Id, Username, Email) VALUES
(1, 'admin', 'admin@example.com'),
(2, 'user1', 'user1@example.com');

INSERT INTO Sessions (Id, UserId, StartTime) VALUES
(101, 1, '2025-11-04 10:00:00'),
(102, 2, '2025-11-04 11:00:00');
```

**Extracted Info:**
```json
{
  "file": "database/seed-data.sql",
  "type": "data",
  "statement_counts": {
    "create_table": 0,
    "insert": 2
  },
  "tables_referenced": ["Users", "Sessions"],
  "file_size_kb": 1.2,
  "estimated_lines": 12
}
```

---

## 💡 Brain Benefits

### Before Enhancement

```
User: "What tables are in the database?"
Brain: "I need a connection string to connect to the database."
User: "Here's the connection string..."
Brain: *Connects, queries INFORMATION_SCHEMA, takes 2-5 min*
Brain: "Found: Users, Sessions, Products..."
```

### After Enhancement

```
User: "What tables are in the database?"
Brain: *Checks SQL files (30 seconds)*
Brain: "Found 2 schema files with these tables:
  - schema.sql: Users, Sessions, Products, Orders
  - migrations/001_add_reviews.sql: Reviews
  
  Total: 5 tables referenced across all SQL files"
```

**Much faster, no credentials needed!**

---

## 🎯 Usage Examples

### Example 1: Project with SQL Files (Most Common)

```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp"
```

**Output:**
```
🗄️  Database Crawler Started

[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)...
  📄 Scanning for *schema*.sql, *data*.sql, *ddl*.sql, *dml*.sql...
  Found 3 schema files, 2 data files
  
  📋 Analyzing schema: database-schema.sql
    ✓ Type: schema, Tables: 12, Size: 45.3 KB
  📋 Analyzing schema: migrations/001_initial.sql
    ✓ Type: mixed, Tables: 15, Size: 23.7 KB
  
  ✅ Found SQL files! Brain can reference these instead of connecting to database.
  📊 Total unique tables referenced: 18
  
[2/6] Discovering database configuration files...
  Found 2 configuration files
  
[6/6] Skipping database connection (SQL files found - brain can use those!)
  ✅ Brain has 3 schema files and 2 data files

════════════════════════════════════
SQL Schema Files: 3
SQL Data Files: 2
Connection strings: 2
Providers: SQL Server
Entities: 15
Duration: 8s
════════════════════════════════════
```

### Example 2: No SQL Files, Has Connection String

```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp"
```

**Output:**
```
[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)...
  Found 0 schema files, 0 data files
  ⚠️  No SQL schema/data files found. Will attempt database connection if configured.

[2/6] Discovering database configuration files...
  Found connection string in appsettings.json
  
[6/6] No SQL files found - attempting database connection...
  Attempting connection to: MyDatabase
  ✅ Successfully crawled: MyDatabase (42 tables found)
```

### Example 3: No SQL Files, No Connection String

```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp"
```

**Output:**
```
[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)...
  Found 0 schema files, 0 data files
  
[6/6] No SQL files found - attempting database connection...
  ⚠️  No connection strings found. Please provide connection string.
  💡 You can:
     1. Add to appsettings.json (ConnectionStrings section)
     2. Add to .env file (DATABASE_URL=...)
     3. Provide manually when prompted
     
  Enter connection string (or press Enter to skip): Server=localhost;Database=MyDB;...
  
  💾 Memorizing connection string for future use...
  ✅ Connection string saved to: KDS\kds-brain\database-connection.txt
  
  Attempting connection to: MyDB
  ✅ Successfully crawled: MyDB (42 tables found)
```

### Example 4: Force Database Connection (Even with SQL Files)

```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\MyApp" -ConnectAndCrawl
```

**Output:**
```
[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)...
  Found 3 schema files, 2 data files
  
[6/6] Connecting to databases (explicit request via -ConnectAndCrawl)...
  ⚠️  Live database crawling is EXPERIMENTAL
  Attempting connection to: MyDatabase
  ✅ Successfully crawled: MyDatabase (42 tables found)
  
  (Brain now has BOTH SQL files AND live schema)
```

---

## 🧠 Brain Integration

### What Brain Learns

**From SQL Schema Files:**
```yaml
database_knowledge:
  sql_files:
    schema:
      - file: "database/schema.sql"
        tables: ["Users", "Sessions", "Products"]
        ddl_statements: 25
        indexes: 8
        
    data:
      - file: "database/seed-data.sql"
        tables: ["Users", "Products"]
        insert_count: 150
        
  discovered_tables:
    - Users
    - Sessions
    - Products
    - Orders
    - Reviews
    
  table_relationships:
    Sessions:
      foreign_keys: ["UserId -> Users.Id"]
    Orders:
      foreign_keys: ["UserId -> Users.Id", "ProductId -> Products.Id"]
```

### Brain Query Examples

```markdown
#file:KDS/prompts/internal/brain-query.md

Query: "What database tables exist?"

Brain: "Found 18 tables across 3 SQL schema files:
  - database/schema.sql: Users, Sessions, Products, Orders (12 tables)
  - migrations/001_initial.sql: Reviews, Comments (3 tables)
  - migrations/002_audit.sql: AuditLog (1 table)
  
  All tables: Users, Sessions, Products, Orders, Reviews, Comments, 
              AuditLog, Categories, Tags, UserProfiles, Settings, etc."
```

```markdown
Query: "Which file has the Users table schema?"

Brain: "The Users table schema is in:
  - database/schema.sql (CREATE TABLE Users with 8 columns)
  
  Referenced in data files:
  - database/seed-data.sql (150 INSERT statements)"
```

---

## ✅ Benefits Summary

### For Users
- ✅ **Faster** - 30 seconds vs 2-5 minutes for database connection
- ✅ **Easier** - No connection string needed
- ✅ **Safer** - No credentials exposed
- ✅ **Offline** - Works without database access

### For Brain
- ✅ **Better references** - File paths instead of "live database"
- ✅ **Version history** - SQL files in Git = timeline
- ✅ **Complete context** - Sees CREATE statements, not just column lists
- ✅ **Relationship aware** - Sees FOREIGN KEY definitions

### For Projects
- ✅ **Portable** - SQL files travel with code
- ✅ **Documented** - Schema is self-documenting
- ✅ **Reproducible** - Anyone can run SQL files
- ✅ **Reviewable** - Schema changes in pull requests

---

## 📝 Recommended Practices

### 1. Create SQL Schema Files

Even if your project uses Entity Framework migrations, create readable SQL files:

```
/database
  /schema
    - schema.sql          (Main schema - CREATE TABLE statements)
    - indexes.sql         (All indexes)
    - constraints.sql     (Foreign keys, constraints)
    - views.sql           (Views and stored procedures)
  /data
    - seed-data.sql       (Development seed data)
    - test-data.sql       (Test fixtures)
```

### 2. Keep SQL Files Updated

When schema changes:
- ✅ Update the SQL file
- ✅ Commit with migration
- ✅ Re-run crawler: `.\database-crawler.ps1 -WorkspaceRoot .`

### 3. Name Files Clearly

Good names:
- ✅ `database-schema.sql`
- ✅ `01-schema-initial.sql`
- ✅ `seed-data-users.sql`

Bad names:
- ❌ `temp.sql`
- ❌ `new.sql`
- ❌ `backup-copy-2.sql`

### 4. Version Control

Add to `.gitignore` (if needed):
```
# Exclude personal local database configs
appsettings.local.json
database-connection.txt

# Include schema files
!database/schema/*.sql
!database/data/*.sql
```

---

## 🔄 Migration Guide

### If You Have EF Migrations Only

Extract schema to SQL:

```powershell
# Generate SQL from migrations
dotnet ef migrations script --output database/schema.sql

# Clean up the file (remove migration metadata if needed)
```

### If You Have Database But No SQL Files

Export schema:

```sql
-- SQL Server: Generate CREATE scripts via SSMS
Right-click Database → Tasks → Generate Scripts → Select tables

-- Or use sqlcmd
sqlcmd -S localhost -d MyDB -Q "SELECT * FROM INFORMATION_SCHEMA.TABLES" -o schema-export.sql
```

Save as `database/schema.sql` and commit.

---

## 🎓 Technical Details

### SQL File Parsing Logic

**Type Detection:**
```
IF (DDL > 0 AND DML == 0) → type = "schema"
IF (DML > 0 AND DDL == 0) → type = "data"
IF (DDL > 0 AND DML > 0)  → type = "mixed"
```

**Table Extraction:**
- Regex: `\b(?:FROM|INTO|TABLE|UPDATE|JOIN)\s+(?:\[?(\w+)\]?\.)?(?:\[?(\w+)\]?)`
- Filters SQL keywords (SELECT, WHERE, etc.)
- Captures schema.table or just table

**Statement Counting:**
- Case-insensitive regex matches
- CREATE TABLE, ALTER TABLE, DROP TABLE
- INSERT INTO, UPDATE SET, DELETE FROM
- CREATE INDEX, CREATE VIEW, CREATE PROCEDURE

---

## 📊 Performance

**Typical Performance:**
- SQL file scan: **5-30 seconds** (depending on file count)
- Config discovery: **10-30 seconds**
- Live DB connection: **1-5 minutes** (if needed)

**Total:**
- With SQL files: **15-60 seconds** ⚡
- Without SQL files: **2-6 minutes**

**Speedup:** ~10x faster when SQL files exist!

---

## 🚀 Future Enhancements

Potential additions:
- [ ] Generate ER diagrams from SQL files
- [ ] Detect schema drift (SQL files vs live DB)
- [ ] Auto-update SQL files from migrations
- [ ] Support for NoSQL schema files (MongoDB, Cassandra)
- [ ] Cross-reference with Entity Framework models

---

## ✅ Testing Checklist

Before committing changes:
- ✅ Test with SQL files present
- ✅ Test with no SQL files, connection string present
- ✅ Test with no SQL files, no connection string (prompt flow)
- ✅ Test with `-ConnectAndCrawl` flag
- ✅ Verify JSON output includes `sql_schema_files` and `sql_data_files`
- ✅ Verify Brain can query SQL file locations

---

## 📚 Related Documentation

- **Main Crawler:** `KDS/prompts/internal/brain-crawler.md`
- **Database Crawler Script:** `KDS/scripts/crawlers/database-crawler.ps1`
- **Brain Query Agent:** `KDS/prompts/internal/brain-query.md`
- **Setup Guide:** `KDS/prompts/user/kds.md` (Setup section)

---

## 🎯 Summary

**Before:** Database crawler required connection strings and live database access (slow, complex, risky)

**After:** Database crawler prioritizes SQL files (fast, simple, safe), only connects to database if necessary

**Result:** 10x faster discovery, works offline, brain has better context! 🚀
