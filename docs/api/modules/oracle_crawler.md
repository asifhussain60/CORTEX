# oracle_crawler

Oracle Database Schema Crawler for CORTEX Knowledge Extraction

This crawler connects to Oracle databases, extracts schema metadata (tables, columns,
relationships, indexes), and stores them as knowledge patterns in Tier 2 knowledge graph.

CORTEX Tier 2 Integration:
- Scope: 'application' (database schemas are application-specific)
- Namespace: Database name (e.g., ['KSESSIONS_DB'])
- Pattern Title: "Oracle: {table_name} schema"
- Confidence: 0.95 (high confidence from direct schema introspection)

Usage:
    crawler = OracleCrawler(connection_string="user/pass@host:port/service")
    patterns = crawler.extract_schema()
    crawler.store_patterns(patterns, knowledge_graph)


## Table of Contents

### Classes
- [OracleTable](#oracletable)
- [OracleColumn](#oraclecolumn)
- [OracleIndex](#oracleindex)
- [OracleConstraint](#oracleconstraint)
- [OracleCrawler](#oraclecrawler)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** dataclasses, json, oracledb, pathlib, src, sys, tier2, typing


## Classes

### OracleTable

```python
class OracleTable
```

**Decorators:** `dataclass`

Represents an Oracle table with metadata.


**Attributes:**

- `owner`: str
- `table_name`: str
- `tablespace_name`: Optional[str]
- `num_rows`: Optional[int]
- `comments`: Optional[str]
- `columns`: List['OracleColumn']
- `indexes`: List['OracleIndex']
- `constraints`: List['OracleConstraint']



---

### OracleColumn

```python
class OracleColumn
```

**Decorators:** `dataclass`

Represents a table column.


**Attributes:**

- `column_name`: str
- `data_type`: str
- `data_length`: Optional[int]
- `data_precision`: Optional[int]
- `data_scale`: Optional[int]
- `nullable`: str
- `default_value`: Optional[str]
- `comments`: Optional[str]



---

### OracleIndex

```python
class OracleIndex
```

**Decorators:** `dataclass`

Represents a table index.


**Attributes:**

- `index_name`: str
- `index_type`: str
- `uniqueness`: str
- `columns`: List[str]



---

### OracleConstraint

```python
class OracleConstraint
```

**Decorators:** `dataclass`

Represents a table constraint.


**Attributes:**

- `constraint_name`: str
- `constraint_type`: str
- `columns`: List[str]
- `r_owner`: Optional[str]
- `r_table`: Optional[str]
- `r_columns`: Optional[List[str]]



---

### OracleCrawler

```python
class OracleCrawler
```

Extracts schema metadata from Oracle databases.

Architecture:
- Uses oracledb (python-oracledb) for connectivity
- Queries data dictionary views (ALL_TABLES, ALL_TAB_COLUMNS, etc.)
- Converts metadata to CORTEX knowledge patterns
- Stores in Tier 2 with scope='application', namespace=[db_name]


**Methods:**

  #### `connect`

  ```python
  connect(self) -> None
  ```

  Establish connection to Oracle database.

  **Parameters:**

  - `self`


  **Returns:** None


  #### `disconnect`

  ```python
  disconnect(self) -> None
  ```

  Close Oracle connection.

  **Parameters:**

  - `self`


  **Returns:** None


  #### `extract_schema`

  ```python
  extract_schema(self, owners: Optional[List[str]], include_system: bool) -> List[OracleTable]
  ```

  Extract schema metadata from Oracle.

Args:
    owners: List of schema owners to extract (default: current user)
    include_system: Include Oracle system schemas (SYS, SYSTEM, etc.)

Returns:
    List of OracleTable objects with full metadata

  **Parameters:**

  - `self`
  - `owners` (Optional[List[str]]) = `None`: List of schema owners to extract (default: current user)
  - `include_system` (bool) = `False`: Include Oracle system schemas (SYS, SYSTEM, etc.)


  **Returns:** List[OracleTable]
    List of OracleTable objects with full metadata


  #### `table_to_pattern`

  ```python
  table_to_pattern(self, table: OracleTable) -> Dict[str, Any]
  ```

  Convert OracleTable to CORTEX knowledge pattern.

Pattern Structure:
- Title: "Oracle: {owner}.{table_name} schema"
- Content: Detailed JSON with columns, indexes, constraints
- Scope: 'application' (database-specific)
- Namespace: [database_name]
- Tags: ['oracle', 'database', 'schema', owner, table_name]
- Confidence: 0.95 (high - direct introspection)

  **Parameters:**

  - `self`
  - `table` (OracleTable)


  **Returns:** Dict[str, Any]


  #### `store_patterns`

  ```python
  store_patterns(self, tables: List[OracleTable], knowledge_graph: KnowledgeGraph) -> int
  ```

  Store extracted schema as knowledge patterns in Tier 2.

Args:
    tables: List of OracleTable objects from extract_schema()
    knowledge_graph: KnowledgeGraph instance for storage

Returns:
    Number of patterns stored

  **Parameters:**

  - `self`
  - `tables` (List[OracleTable]): List of OracleTable objects from extract_schema()
  - `knowledge_graph` (KnowledgeGraph): KnowledgeGraph instance for storage


  **Returns:** int
    Number of patterns stored



---
