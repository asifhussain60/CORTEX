# Database Discovery Workflow - Quick Reference

**Version:** 1.1.0  
**Updated:** 2025-11-04

---

## 🎯 Priority Order (Fastest → Slowest)

```
1. SQL Files (30 seconds)        ← FASTEST, TRY FIRST ✅
   ↓ If not found...
   
2. Connection Strings (1 min)    ← FALLBACK
   ↓ If not found...
   
3. Prompt User (manual input)    ← ASK USER
   ↓ Then...
   
4. Database Connection (2-5 min) ← SLOWEST, LAST RESORT
```

---

## 📁 SQL File Patterns Scanned

### Schema Files (DDL)
- `*schema*.sql` - Main schema files
- `*ddl*.sql` - Data Definition Language
- `*create*.sql` - CREATE statements
- `*structure*.sql` - Database structure

### Data Files (DML)
- `*data*.sql` - Data files
- `*dml*.sql` - Data Manipulation Language
- `*insert*.sql` - INSERT statements
- `*seed*.sql` - Seed data

---

## ✅ Recommended Project Structure

```
/database
  /schema
    schema.sql          ← Main DDL (CREATE TABLE, etc.)
    indexes.sql         ← All indexes
    constraints.sql     ← Foreign keys
    views.sql           ← Views, stored procedures
    
  /data
    seed-data.sql       ← Development data
    test-data.sql       ← Test fixtures
```

---

## 🚀 Quick Commands

### Scan for SQL Files Only
```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot .
```
*Auto-skips database connection if SQL files found*

### Force Database Connection
```powershell
.\KDS\scripts\crawlers\database-crawler.ps1 -WorkspaceRoot . -ConnectAndCrawl
```
*Connects even if SQL files exist*

---

## 🧠 What Brain Learns

### From SQL Files
```yaml
database_knowledge:
  sql_files:
    schema: ["database/schema.sql"]
    data: ["database/seed-data.sql"]
  tables: ["Users", "Sessions", "Products"]
  table_sources:
    Users: "database/schema.sql (line 15)"
    Sessions: "database/schema.sql (line 42)"
```

### Brain Can Answer
- "What database tables exist?" → Lists from SQL files
- "Where is the Users table defined?" → Points to SQL file
- "What's the schema for Products?" → Shows CREATE TABLE from file

---

## ⚡ Performance

| Method | Time | Requirements |
|--------|------|--------------|
| SQL Files | 30 seconds | Just SQL files in project |
| Connection String | 1-2 min | appsettings.json or .env |
| Manual Input | User prompt | User provides connection string |
| Live Database | 2-5 min | Database accessible, credentials |

**Speedup:** 10x faster with SQL files! 🚀

---

## 💡 Pro Tips

1. **Keep SQL files updated** - When schema changes, update the SQL file
2. **Name clearly** - Use descriptive names like `database-schema.sql`
3. **Commit to Git** - SQL files = version controlled schema
4. **Generate from migrations** - `dotnet ef migrations script --output schema.sql`
5. **One-time export** - Export from database once, commit, reuse forever

---

## 🔍 What Gets Analyzed

For each SQL file:
- ✅ File type (schema/data/mixed)
- ✅ Statement counts (CREATE, INSERT, etc.)
- ✅ Table names referenced
- ✅ File size and line count
- ✅ DDL vs DML distribution

---

## 📚 Related Docs

- **Full Details:** `KDS/docs/features/database-crawler-sql-file-priority.md`
- **Main Crawler:** `KDS/prompts/internal/brain-crawler.md`
- **Setup Guide:** `KDS/prompts/user/kds.md` (Phase 2.2)
- **Script:** `KDS/scripts/crawlers/database-crawler.ps1`

---

## 🎓 Example Output

```
🗄️  Database Crawler Started

[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)...
  Found 2 schema files, 1 data files
  
  📋 Analyzing schema: database/schema.sql
    ✓ Type: schema, Tables: 12, Size: 45.3 KB
    
  ✅ Found SQL files! Brain can reference these.
  📊 Total unique tables: 12

[6/6] Skipping database connection (SQL files found!)
  ✅ Brain has 2 schema files and 1 data file

════════════════════════════════════
SQL Schema Files: 2
SQL Data Files: 1
Entities: 12
Duration: 8s
════════════════════════════════════
```

---

**Remember:** SQL files = faster, easier, safer than database connections! ✨
