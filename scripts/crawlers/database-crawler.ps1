<#
.SYNOPSIS
    Database Crawler - Discovers database schemas, connection strings, and data patterns

.DESCRIPTION
    Area-specific crawler for databases. Discovery priority:
    
    PRIORITY 1 (Fastest, Easiest): SQL Schema/Data Files
    - Scans for *schema*.sql, *ddl*.sql, *create*.sql (DDL/schema files)
    - Scans for *data*.sql, *dml*.sql, *insert*.sql, *seed*.sql (DML/data files)
    - Analyzes file contents (CREATE TABLE, INSERT INTO, etc.)
    - Brain can reference these files instead of connecting to live database
    
    PRIORITY 2: Configuration Discovery
    - Connection strings (from appsettings.json, web.config, .env files)
    - Database provider detection (SQL Server, PostgreSQL, MySQL, MongoDB, etc.)
    - Entity models and DbContext files
    - Migration files and version history
    
    PRIORITY 3 (Only if needed): Live Database Connection
    - Only attempts if: No SQL files found OR -ConnectAndCrawl explicitly specified
    - If no connection string found, prompts user and memorizes it for future use
    - Crawls actual schema from live database (tables, columns, relationships)
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root (e.g., "D:\PROJECTS\NOOR CANVAS")

.PARAMETER OutputPath
    Path where database-results.json will be written (default: KDS/cortex-brain/crawler-temp/database-results.json)

.PARAMETER ConnectAndCrawl
    If specified, attempts to connect to databases and crawl actual schema even if SQL files exist (default: false for security)

.OUTPUTS
    database-results.json - Structured JSON with database discoveries

.EXAMPLE
    .\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS"
    
    Scans for SQL files first. If found, uses those. If not found, looks for connection strings.
    
.EXAMPLE
    .\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS" -ConnectAndCrawl

    Forces live database connection even if SQL files exist.

.NOTES
    Version: 1.1.0
    Author: KDS Multi-Threaded Crawler System
    Performance Target: <30s for SQL file scan, <2 min for config discovery, <5 min with live DB crawl
    
    Priority Logic:
    1. Scan for SQL files (always, fast)
    2. If SQL files found → Use those, skip database connection (unless -ConnectAndCrawl)
    3. If no SQL files → Look for connection strings → Prompt if not found → Connect if available
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$ConnectAndCrawl
)

# Default output path if not provided
if (-not $OutputPath) {
    # Normalize workspace root and detect KDS location
    $normalizedRoot = $WorkspaceRoot.TrimEnd('\')
    if ($normalizedRoot -match '\\KDS$') {
        # Workspace IS KDS
        $OutputPath = "$normalizedRoot\cortex-brain\crawler-temp\database-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\cortex-brain\crawler-temp\database-results.json"
    }
}

# Start timer
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "🗄️  Database Crawler Started" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor Gray
Write-Host "Output: $OutputPath" -ForegroundColor Gray
Write-Host "Connect Mode: $($ConnectAndCrawl.IsPresent)" -ForegroundColor Gray

# Configuration
$configPatterns = @(
    "appsettings*.json",
    "web.config",
    "app.config",
    ".env",
    "database.yml",
    "database.json",
    "knexfile.js",
    "ormconfig.json"
)
$dbContextPatterns = @("*DbContext.cs", "*Context.cs", "*DbContext.ts", "*Repository.cs")
$migrationPatterns = @("*Migration.cs", "migrations/*.sql", "migrations/*.js", "alembic/versions/*.py")

# SQL schema/data file patterns (NEW - Priority discovery)
$sqlSchemaPatterns = @("*schema*.sql", "*ddl*.sql", "*create*.sql", "*structure*.sql")
$sqlDataPatterns = @("*data*.sql", "*dml*.sql", "*insert*.sql", "*seed*.sql")

$excludeDirs = @("node_modules", "bin", "obj", "dist", "build", ".next", "out", "vendor")

# Initialize result structure
$result = @{
    area = "Database"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    sql_schema_files = @()      # NEW
    sql_data_files = @()        # NEW
    connection_strings = @()
    providers = @()
    entities = @()
    migrations = @()
    statistics = @{
        total_sql_schema_files = 0    # NEW
        total_sql_data_files = 0      # NEW
        total_connections = 0
        total_entities = 0
        total_migrations = 0
        total_relationships = 0
    }
}

# Helper: Parse connection string to extract provider and details
function Get-ConnectionStringInfo {
    param([string]$ConnectionString, [string]$SourceFile)
    
    $info = @{
        raw = $ConnectionString
        provider = "unknown"
        server = $null
        database = $null
        authentication = "unknown"
        source_file = $SourceFile
    }
    
    # SQL Server patterns
    if ($ConnectionString -match 'Data Source=([^;]+)|Server=([^;]+)') {
        $info.provider = "SQL Server"
        $info.server = if ($Matches[1]) { $Matches[1] } else { $Matches[2] }
    }
    
    if ($ConnectionString -match 'Initial Catalog=([^;]+)|Database=([^;]+)') {
        $info.database = if ($Matches[1]) { $Matches[1] } else { $Matches[2] }
    }
    
    # PostgreSQL
    if ($ConnectionString -match 'Host=([^;]+)' -or $ConnectionString -match 'postgres://') {
        $info.provider = "PostgreSQL"
        if ($Matches[1]) { $info.server = $Matches[1] }
        
        # Parse postgres:// URL format
        if ($ConnectionString -match 'postgres://[^@]+@([^/]+)/(\w+)') {
            $info.server = $Matches[1]
            $info.database = $Matches[2]
        }
    }
    
    # MySQL
    if ($ConnectionString -match 'mysql://') {
        $info.provider = "MySQL"
        if ($ConnectionString -match 'mysql://[^@]+@([^/]+)/(\w+)') {
            $info.server = $Matches[1]
            $info.database = $Matches[2]
        }
    }
    
    # MongoDB
    if ($ConnectionString -match 'mongodb(\+srv)?://') {
        $info.provider = "MongoDB"
        if ($ConnectionString -match 'mongodb[^/]*//[^/]+/(\w+)') {
            $info.database = $Matches[1]
        }
    }
    
    # SQLite
    if ($ConnectionString -match 'Data Source=.*\.db|.*\.sqlite') {
        $info.provider = "SQLite"
        if ($ConnectionString -match 'Data Source=([^;]+)') {
            $info.database = $Matches[1]
        }
    }
    
    # Authentication type
    if ($ConnectionString -match 'Integrated Security=true|Trusted_Connection=true') {
        $info.authentication = "Windows Authentication"
    } elseif ($ConnectionString -match 'User ID=|User=|Username=') {
        $info.authentication = "SQL Authentication"
    }
    
    return $info
}

# Helper: Analyze SQL file content to determine type and extract metadata
function Get-SqlFileInfo {
    param([string]$FilePath, [string]$Content)
    
    $info = @{
        file = $FilePath
        type = "unknown"  # schema, data, mixed, unknown
        tables_referenced = @()
        statement_counts = @{
            create_table = 0
            alter_table = 0
            drop_table = 0
            insert = 0
            update = 0
            delete = 0
            select = 0
            create_index = 0
            create_view = 0
            create_procedure = 0
            create_function = 0
        }
        estimated_lines = 0
        file_size_kb = 0
    }
    
    # Get file size
    $fileItem = Get-Item -Path (Join-Path $script:WorkspaceRoot $FilePath) -ErrorAction SilentlyContinue
    if ($fileItem) {
        $info.file_size_kb = [math]::Round($fileItem.Length / 1KB, 2)
    }
    
    # Count lines
    $lines = $Content -split "`n"
    $info.estimated_lines = $lines.Count
    
    # Count statement types (case-insensitive)
    $info.statement_counts.create_table = ([regex]::Matches($Content, '\bCREATE\s+TABLE\b', 'IgnoreCase')).Count
    $info.statement_counts.alter_table = ([regex]::Matches($Content, '\bALTER\s+TABLE\b', 'IgnoreCase')).Count
    $info.statement_counts.drop_table = ([regex]::Matches($Content, '\bDROP\s+TABLE\b', 'IgnoreCase')).Count
    $info.statement_counts.create_index = ([regex]::Matches($Content, '\bCREATE\s+(?:UNIQUE\s+)?INDEX\b', 'IgnoreCase')).Count
    $info.statement_counts.create_view = ([regex]::Matches($Content, '\bCREATE\s+VIEW\b', 'IgnoreCase')).Count
    $info.statement_counts.create_procedure = ([regex]::Matches($Content, '\bCREATE\s+(?:OR\s+(?:ALTER|REPLACE)\s+)?PROC(?:EDURE)?\b', 'IgnoreCase')).Count
    $info.statement_counts.create_function = ([regex]::Matches($Content, '\bCREATE\s+(?:OR\s+(?:ALTER|REPLACE)\s+)?FUNCTION\b', 'IgnoreCase')).Count
    $info.statement_counts.insert = ([regex]::Matches($Content, '\bINSERT\s+INTO\b', 'IgnoreCase')).Count
    $info.statement_counts.update = ([regex]::Matches($Content, '\bUPDATE\s+\w+\s+SET\b', 'IgnoreCase')).Count
    $info.statement_counts.delete = ([regex]::Matches($Content, '\bDELETE\s+FROM\b', 'IgnoreCase')).Count
    $info.statement_counts.select = ([regex]::Matches($Content, '\bSELECT\s+', 'IgnoreCase')).Count
    
    # Determine file type based on statement distribution
    $ddlCount = $info.statement_counts.create_table + 
                $info.statement_counts.alter_table + 
                $info.statement_counts.create_index + 
                $info.statement_counts.create_view +
                $info.statement_counts.create_procedure +
                $info.statement_counts.create_function
    
    $dmlCount = $info.statement_counts.insert + 
                $info.statement_counts.update + 
                $info.statement_counts.delete
    
    if ($ddlCount -gt 0 -and $dmlCount -eq 0) {
        $info.type = "schema"  # Pure DDL
    } elseif ($dmlCount -gt 0 -and $ddlCount -eq 0) {
        $info.type = "data"    # Pure DML
    } elseif ($ddlCount -gt 0 -and $dmlCount -gt 0) {
        $info.type = "mixed"   # Both DDL and DML
    }
    
    # Extract table names (approximate - captures table names from various SQL statements)
    $tableMatches = [regex]::Matches($Content, '\b(?:FROM|INTO|TABLE|UPDATE|JOIN)\s+(?:\[?(\w+)\]?\.)?(?:\[?(\w+)\]?)', 'IgnoreCase')
    
    $tables = @{}
    foreach ($match in $tableMatches) {
        # Get the actual table name (could be schema.table or just table)
        $tableName = if ($match.Groups[2].Value) { 
            $match.Groups[2].Value 
        } else { 
            $match.Groups[1].Value 
        }
        
        # Filter out common SQL keywords that aren't table names
        $keywords = @('SELECT', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'UNION', 'INTERSECT', 'EXCEPT', 'VALUES', 'DEFAULT', 'NULL', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AS', 'ON')
        
        if ($tableName -and $tableName.Length -gt 0 -and $keywords -notcontains $tableName.ToUpper()) {
            $tables[$tableName] = $true
        }
    }
    
    $info.tables_referenced = @($tables.Keys)
    
    return $info
}

# Helper: Parse connection string to extract provider and details
function Get-ConnectionStringInfo {
    param([string]$ConnectionString, [string]$SourceFile)
    
    $info = @{
        raw = $ConnectionString
        provider = "unknown"
        server = $null
        database = $null
        authentication = "unknown"
        source_file = $SourceFile
    }
    
    # SQL Server patterns
    if ($ConnectionString -match 'Data Source=([^;]+)|Server=([^;]+)') {
        $info.provider = "SQL Server"
        $info.server = if ($Matches[1]) { $Matches[1] } else { $Matches[2] }
    }
    
    if ($ConnectionString -match 'Initial Catalog=([^;]+)|Database=([^;]+)') {
        $info.database = if ($Matches[1]) { $Matches[1] } else { $Matches[2] }
    }
    
    # PostgreSQL
    if ($ConnectionString -match 'Host=([^;]+)' -or $ConnectionString -match 'postgres://') {
        $info.provider = "PostgreSQL"
        if ($Matches[1]) { $info.server = $Matches[1] }
        
        # Parse postgres:// URL format
        if ($ConnectionString -match 'postgres://[^@]+@([^/]+)/(\w+)') {
            $info.server = $Matches[1]
            $info.database = $Matches[2]
        }
    }
    
    # MySQL
    if ($ConnectionString -match 'mysql://') {
        $info.provider = "MySQL"
        if ($ConnectionString -match 'mysql://[^@]+@([^/]+)/(\w+)') {
            $info.server = $Matches[1]
            $info.database = $Matches[2]
        }
    }
    
    # MongoDB
    if ($ConnectionString -match 'mongodb(\+srv)?://') {
        $info.provider = "MongoDB"
        if ($ConnectionString -match 'mongodb[^/]*//[^/]+/(\w+)') {
            $info.database = $Matches[1]
        }
    }
    
    # SQLite
    if ($ConnectionString -match 'Data Source=.*\.db|.*\.sqlite') {
        $info.provider = "SQLite"
        if ($ConnectionString -match 'Data Source=([^;]+)') {
            $info.database = $Matches[1]
        }
    }
    
    # Authentication type
    if ($ConnectionString -match 'Integrated Security=true|Trusted_Connection=true') {
        $info.authentication = "Windows Authentication"
    } elseif ($ConnectionString -match 'User ID=|User=|Username=') {
        $info.authentication = "SQL Authentication"
    }
    
    return $info
}

# Helper: Extract entities from DbContext file
function Get-EntitiesFromDbContext {
    param([string]$FilePath, [string]$Content)
    
    $entities = @()
    
    # Extract DbSet<T> properties (C#)
    $dbSetMatches = [regex]::Matches($Content, 'public\s+(?:virtual\s+)?DbSet<(\w+)>\s+(\w+)\s*\{')
    
    foreach ($match in $dbSetMatches) {
        $entityType = $match.Groups[1].Value
        $dbSetName = $match.Groups[2].Value
        
        $entity = @{
            name = $entityType
            dbset_name = $dbSetName
            file = $FilePath
            properties = @()
            relationships = @()
        }
        
        # Try to find the entity class definition
        $entityPattern = "class\s+$entityType[\s\S]*?\{([\s\S]*?)\n\s*\}"
        if ($Content -match $entityPattern) {
            $entityBody = $Matches[1]
            
            # Extract properties
            $propMatches = [regex]::Matches($entityBody, 'public\s+(\w+(?:<\w+>)?)\s+(\w+)\s*\{')
            foreach ($propMatch in $propMatches) {
                $propType = $propMatch.Groups[1].Value
                $propName = $propMatch.Groups[2].Value
                
                # Skip navigation properties (collections)
                if ($propType -notmatch 'ICollection|List|IEnumerable') {
                    $entity.properties += @{
                        name = $propName
                        type = $propType
                    }
                }
            }
            
            # Extract relationships (navigation properties)
            $navMatches = [regex]::Matches($entityBody, 'public\s+(?:virtual\s+)?(?:ICollection<(\w+)>|List<(\w+)>|(\w+))\s+(\w+)')
            
            foreach ($navMatch in $navMatches) {
                $targetType = $null
                $isCollection = $false
                
                if ($navMatch.Groups[1].Value) {
                    $targetType = $navMatch.Groups[1].Value
                    $isCollection = $true
                } elseif ($navMatch.Groups[2].Value) {
                    $targetType = $navMatch.Groups[2].Value
                    $isCollection = $true
                } else {
                    $targetType = $navMatch.Groups[3].Value
                }
                
                $navProp = $navMatch.Groups[4].Value
                
                # Only add if target type looks like an entity (PascalCase, not primitive)
                if ($targetType -match '^[A-Z]' -and $targetType -notmatch '^(String|Int|Bool|DateTime|Guid|Decimal)') {
                    $entity.relationships += @{
                        type = if ($isCollection) { "one-to-many" } else { "many-to-one" }
                        target = $targetType
                        property = $navProp
                    }
                }
            }
        }
        
        $entities += $entity
    }
    
    return $entities
}

# Helper: Extract migrations info
function Get-MigrationInfo {
    param([string]$FilePath, [string]$Content)
    
    $info = @{
        file = $FilePath
        name = $null
        timestamp = $null
        operations = @()
    }
    
    # Extract migration name from filename or class
    if ($FilePath -match '(\d{14})_(\w+)') {
        $info.timestamp = $Matches[1]
        $info.name = $Matches[2]
    } elseif ($Content -match 'public\s+class\s+(\w+)\s*:\s*Migration') {
        $info.name = $Matches[1]
    }
    
    # Detect operation types
    if ($Content -match 'CreateTable|CreateTableAsync') {
        $info.operations += "CreateTable"
    }
    if ($Content -match 'DropTable|DropTableAsync') {
        $info.operations += "DropTable"
    }
    if ($Content -match 'AddColumn|AddColumnAsync') {
        $info.operations += "AddColumn"
    }
    if ($Content -match 'DropColumn|DropColumnAsync') {
        $info.operations += "DropColumn"
    }
    if ($Content -match 'CreateIndex|CreateIndexAsync') {
        $info.operations += "CreateIndex"
    }
    
    return $info
}

# Step 1: Discover SQL schema and data files (PRIORITY - Easier than full DB crawl)
Write-Host "`n[1/6] 🔍 Discovering SQL schema and data files (PRIORITY)..." -ForegroundColor Yellow
Write-Host "  📄 Scanning for *schema*.sql, *data*.sql, *ddl*.sql, *dml*.sql..." -ForegroundColor Gray

$sqlSchemaFiles = @()
$sqlDataFiles = @()

# Scan for schema files
foreach ($pattern in $sqlSchemaPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $sqlSchemaFiles += $files
}

# Scan for data files
foreach ($pattern in $sqlDataPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $sqlDataFiles += $files
}

Write-Host "  Found $($sqlSchemaFiles.Count) schema files, $($sqlDataFiles.Count) data files" -ForegroundColor Cyan

# Parse schema files
$parsedSchemaFiles = @()
foreach ($file in $sqlSchemaFiles) {
    Write-Host "  📋 Analyzing schema: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $fileInfo = Get-SqlFileInfo -FilePath $relativePath -Content $content
        $parsedSchemaFiles += $fileInfo
        
        Write-Host "    ✓ Type: $($fileInfo.type), Tables: $($fileInfo.tables_referenced.Count), Size: $($fileInfo.file_size_kb) KB" -ForegroundColor Green
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

# Parse data files
$parsedDataFiles = @()
foreach ($file in $sqlDataFiles) {
    Write-Host "  📊 Analyzing data: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $fileInfo = Get-SqlFileInfo -FilePath $relativePath -Content $content
        $parsedDataFiles += $fileInfo
        
        Write-Host "    ✓ Type: $($fileInfo.type), Tables: $($fileInfo.tables_referenced.Count), Inserts: $($fileInfo.statement_counts.insert)" -ForegroundColor Green
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

$result.sql_schema_files = $parsedSchemaFiles
$result.sql_data_files = $parsedDataFiles
$result.statistics.total_sql_schema_files = $parsedSchemaFiles.Count
$result.statistics.total_sql_data_files = $parsedDataFiles.Count

if ($parsedSchemaFiles.Count -gt 0 -or $parsedDataFiles.Count -gt 0) {
    Write-Host "`n  ✅ Found SQL files! Brain can reference these instead of connecting to database." -ForegroundColor Green
    
    # Extract unique tables across all SQL files
    $allTables = @()
    foreach ($file in ($parsedSchemaFiles + $parsedDataFiles)) {
        $allTables += $file.tables_referenced
    }
    $uniqueTables = $allTables | Select-Object -Unique | Sort-Object
    
    Write-Host "  📊 Total unique tables referenced: $($uniqueTables.Count)" -ForegroundColor Cyan
    if ($uniqueTables.Count -le 20) {
        Write-Host "  Tables: $($uniqueTables -join ', ')" -ForegroundColor Gray
    }
} else {
    Write-Host "`n  ⚠️  No SQL schema/data files found. Will attempt database connection if configured." -ForegroundColor Yellow
}

# Step 2: Discover configuration files
Write-Host "`n[2/6] Discovering database configuration files..." -ForegroundColor Yellow

$configFiles = @()
foreach ($pattern in $configPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $configFiles += $files
}

Write-Host "  Found $($configFiles.Count) configuration files" -ForegroundColor Green

# Step 3: Extract connection strings
Write-Host "`n[3/6] Extracting connection strings..." -ForegroundColor Yellow

$connectionStrings = @()

foreach ($file in $configFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        # appsettings.json
        if ($file.Name -match '^appsettings.*\.json$') {
            $json = $content | ConvertFrom-Json
            if ($json.ConnectionStrings) {
                foreach ($prop in $json.ConnectionStrings.PSObject.Properties) {
                    $connInfo = Get-ConnectionStringInfo -ConnectionString $prop.Value -SourceFile $relativePath
                    $connInfo.name = $prop.Name
                    $connInfo.environment = if ($file.Name -match 'Development') { "Development" } 
                                           elseif ($file.Name -match 'Production') { "Production" }
                                           else { "Default" }
                    $connectionStrings += $connInfo
                }
            }
        }
        
        # web.config / app.config
        if ($file.Name -match '\.(web|app)\.config$') {
            $xmlMatches = [regex]::Matches($content, '<add\s+name="([^"]+)"\s+connectionString="([^"]+)"')
            foreach ($match in $xmlMatches) {
                $connInfo = Get-ConnectionStringInfo -ConnectionString $match.Groups[2].Value -SourceFile $relativePath
                $connInfo.name = $match.Groups[1].Value
                $connInfo.environment = "Default"
                $connectionStrings += $connInfo
            }
        }
        
        # .env files
        if ($file.Name -eq '.env') {
            $envMatches = [regex]::Matches($content, '(DATABASE_URL|DB_CONNECTION|CONNECTION_STRING|MONGO_URI)=(.+)')
            foreach ($match in $envMatches) {
                $connInfo = Get-ConnectionStringInfo -ConnectionString $match.Groups[2].Value.Trim() -SourceFile $relativePath
                $connInfo.name = $match.Groups[1].Value
                $connInfo.environment = "Environment Variable"
                $connectionStrings += $connInfo
            }
        }
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

$result.connection_strings = $connectionStrings
$result.statistics.total_connections = $connectionStrings.Count
$result.providers = $connectionStrings | Select-Object -ExpandProperty provider -Unique

Write-Host "  Found $($connectionStrings.Count) connection strings" -ForegroundColor Green
Write-Host "  Providers: $($result.providers -join ', ')" -ForegroundColor Cyan

# Step 4: Discover entities from DbContext files
Write-Host "`n[4/6] Discovering entity models..." -ForegroundColor Yellow

$dbContextFiles = @()
foreach ($pattern in $dbContextPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $dbContextFiles += $files
}

Write-Host "  Found $($dbContextFiles.Count) DbContext/Repository files" -ForegroundColor Green

$allEntities = @()
$totalRelationships = 0

foreach ($file in $dbContextFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $entities = Get-EntitiesFromDbContext -FilePath $relativePath -Content $content
        
        foreach ($entity in $entities) {
            $allEntities += $entity
            $totalRelationships += $entity.relationships.Count
        }
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

$result.entities = $allEntities
$result.statistics.total_entities = $allEntities.Count
$result.statistics.total_relationships = $totalRelationships

Write-Host "  Found $($allEntities.Count) entities with $totalRelationships relationships" -ForegroundColor Green

# Step 5: Discover migrations
Write-Host "`n[5/6] Discovering database migrations..." -ForegroundColor Yellow

$migrationFiles = @()
foreach ($pattern in $migrationPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $migrationFiles += $files
}

Write-Host "  Found $($migrationFiles.Count) migration files" -ForegroundColor Green

$migrations = @()
foreach ($file in $migrationFiles) {
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $migInfo = Get-MigrationInfo -FilePath $relativePath -Content $content
        $migrations += $migInfo
        
    } catch {
        Write-Warning "  Failed to parse migration $($file.Name): $_"
    }
}

$result.migrations = $migrations | Sort-Object -Property timestamp
$result.statistics.total_migrations = $migrations.Count

$result.migrations = $migrations | Sort-Object -Property timestamp
$result.statistics.total_migrations = $migrations.Count

# Step 6: Connect and crawl (ONLY if no SQL files found OR explicitly requested)
$shouldConnectToDB = $ConnectAndCrawl.IsPresent -or ($result.statistics.total_sql_schema_files -eq 0 -and $connectionStrings.Count -gt 0)

if ($shouldConnectToDB) {
    if ($result.statistics.total_sql_schema_files -eq 0) {
        Write-Host "`n[6/6] No SQL files found - attempting database connection..." -ForegroundColor Yellow
    } else {
        Write-Host "`n[6/6] Connecting to databases (explicit request via -ConnectAndCrawl)..." -ForegroundColor Yellow
    }
    
    if ($connectionStrings.Count -eq 0) {
        Write-Host "  ⚠️  No connection strings found. Please provide connection string." -ForegroundColor Yellow
        Write-Host "  💡 You can:" -ForegroundColor Cyan
        Write-Host "     1. Add to appsettings.json (ConnectionStrings section)" -ForegroundColor Gray
        Write-Host "     2. Add to .env file (DATABASE_URL=...)" -ForegroundColor Gray
        Write-Host "     3. Provide manually when prompted" -ForegroundColor Gray
        
        # Prompt for connection string
        $manualConnString = Read-Host "`n  Enter connection string (or press Enter to skip)"
        
        if ($manualConnString -and $manualConnString.Trim().Length -gt 0) {
            Write-Host "  💾 Memorizing connection string for future use..." -ForegroundColor Cyan
            
            # Store in KDS brain for future reference
            $connStringFile = Join-Path $WorkspaceRoot "KDS\cortex-brain\database-connection.txt"
            $manualConnString | Set-Content -Path $connStringFile -Encoding UTF8
            
            Write-Host "  ✅ Connection string saved to: KDS\cortex-brain\database-connection.txt" -ForegroundColor Green
            
            # Parse and add to connection strings
            $connInfo = Get-ConnectionStringInfo -ConnectionString $manualConnString -SourceFile "manual-input"
            $connInfo.name = "ManualConnection"
            $connInfo.environment = "Default"
            $connectionStrings += $connInfo
            
            $result.connection_strings += $connInfo
        } else {
            Write-Host "  ℹ️  Skipping database connection (no connection string provided)" -ForegroundColor Gray
        }
    }
    
    if ($connectionStrings.Count -gt 0) {
        Write-Host "  ⚠️  Live database crawling is EXPERIMENTAL" -ForegroundColor Yellow
    
    $result.live_schema = @()
    
    foreach ($conn in $connectionStrings | Where-Object { $_.provider -eq "SQL Server" }) {
        Write-Host "  Attempting connection to: $($conn.database)" -ForegroundColor Cyan
        
        try {
            # Only attempt if SQL Server module is available
            if (Get-Module -ListAvailable -Name SqlServer) {
                Import-Module SqlServer -ErrorAction Stop
                
                $query = "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                         FROM INFORMATION_SCHEMA.COLUMNS 
                         ORDER BY TABLE_NAME, ORDINAL_POSITION"
                
                $sqlConn = New-Object System.Data.SqlClient.SqlConnection($conn.raw)
                $sqlConn.Open()
                
                $cmd = New-Object System.Data.SqlClient.SqlCommand($query, $sqlConn)
                $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($cmd)
                $dataset = New-Object System.Data.DataSet
                $adapter.Fill($dataset) | Out-Null
                
                $sqlConn.Close()
                
                $result.live_schema += @{
                    connection = $conn.name
                    database = $conn.database
                    tables_found = $dataset.Tables[0].Rows.Count
                    schema = $dataset.Tables[0] | Select-Object TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                }
                
                Write-Host "  ✅ Successfully crawled: $($conn.database)" -ForegroundColor Green
                
            } else {
                Write-Host "  ⚠️  SqlServer module not available - skipping live crawl" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Warning "  Failed to connect to $($conn.database): $_"
        }
    }
    }
} else {
    if ($result.statistics.total_sql_schema_files -gt 0) {
        Write-Host "`n[6/6] Skipping database connection (SQL files found - brain can use those!)" -ForegroundColor Green
        Write-Host "  ✅ Brain has $($result.statistics.total_sql_schema_files) schema files and $($result.statistics.total_sql_data_files) data files" -ForegroundColor Cyan
    } else {
        Write-Host "`n[6/6] Skipping live database crawl (use -ConnectAndCrawl to enable)" -ForegroundColor Gray
    }
}

# Step 6: Write output
Write-Host "`n✅ Database Crawler Complete!" -ForegroundColor Green

$stopwatch.Stop()
$result.duration_seconds = [int]$stopwatch.Elapsed.TotalSeconds

# Ensure output directory exists
$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

# Write JSON
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "════════════════════════════════════" -ForegroundColor Cyan
Write-Host "SQL Schema Files: $($result.statistics.total_sql_schema_files)" -ForegroundColor White
Write-Host "SQL Data Files: $($result.statistics.total_sql_data_files)" -ForegroundColor White
Write-Host "Connection strings: $($result.statistics.total_connections)" -ForegroundColor White
Write-Host "Providers: $($result.providers -join ', ')" -ForegroundColor White
Write-Host "Entities: $($result.statistics.total_entities)" -ForegroundColor White
Write-Host "Relationships: $($result.statistics.total_relationships)" -ForegroundColor White
Write-Host "Migrations: $($result.statistics.total_migrations)" -ForegroundColor White
Write-Host "Duration: $($result.duration_seconds)s" -ForegroundColor White
Write-Host "Output: $OutputPath" -ForegroundColor Gray
Write-Host "════════════════════════════════════" -ForegroundColor Cyan

# Return result object for orchestrator
return $result
