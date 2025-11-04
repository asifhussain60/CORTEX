<#
.SYNOPSIS
    Database Crawler - Discovers database schemas, connection strings, and data patterns

.DESCRIPTION
    Area-specific crawler for databases. Discovers:
    - Connection strings (from appsettings.json, web.config, .env files)
    - Database provider (SQL Server, PostgreSQL, MySQL, MongoDB, etc.)
    - Schema information (tables, columns, relationships)
    - Entity models and DbContext files
    - Migration files and version history
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root (e.g., "D:\PROJECTS\NOOR CANVAS")

.PARAMETER OutputPath
    Path where database-results.json will be written (default: KDS/kds-brain/crawler-temp/database-results.json)

.PARAMETER ConnectAndCrawl
    If specified, attempts to connect to databases and crawl actual schema (default: false for security)

.OUTPUTS
    database-results.json - Structured JSON with database discoveries

.EXAMPLE
    .\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS"
    
.EXAMPLE
    .\database-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS" -ConnectAndCrawl

.NOTES
    Version: 1.0.0
    Author: KDS Multi-Threaded Crawler System
    Performance Target: <2 min for config discovery, <5 min with live DB crawl
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
        $OutputPath = "$normalizedRoot\kds-brain\crawler-temp\database-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\kds-brain\crawler-temp\database-results.json"
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
$excludeDirs = @("node_modules", "bin", "obj", "dist", "build", ".next", "out", "vendor")

# Initialize result structure
$result = @{
    area = "Database"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    connection_strings = @()
    providers = @()
    entities = @()
    migrations = @()
    statistics = @{
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

# Step 1: Discover configuration files
Write-Host "`n[1/5] Discovering database configuration files..." -ForegroundColor Yellow

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

# Step 2: Extract connection strings
Write-Host "`n[2/5] Extracting connection strings..." -ForegroundColor Yellow

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

# Step 3: Discover entities from DbContext files
Write-Host "`n[3/5] Discovering entity models..." -ForegroundColor Yellow

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

# Step 4: Discover migrations
Write-Host "`n[4/5] Discovering database migrations..." -ForegroundColor Yellow

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

# Step 5: Connect and crawl (if requested)
if ($ConnectAndCrawl) {
    Write-Host "`n[5/5] Connecting to databases and crawling schema..." -ForegroundColor Yellow
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
} else {
    Write-Host "`n[5/5] Skipping live database crawl (use -ConnectAndCrawl to enable)" -ForegroundColor Gray
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
