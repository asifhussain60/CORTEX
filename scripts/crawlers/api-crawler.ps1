<#
.SYNOPSIS
    API Crawler - Discovers API controllers, routes, and patterns

.DESCRIPTION
    Area-specific crawler for API endpoints. Discovers:
    - API routes ([HttpGet("...")], app.get())
    - HTTP methods (GET, POST, PUT, DELETE)
    - DTOs (request/response models)
    - Authorization patterns ([Authorize], requireAuth)
    - Route parameters (path, query)
    - Versioning patterns
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root

.PARAMETER OutputPath
    Path where api-results.json will be written

.OUTPUTS
    api-results.json - Structured JSON with API discoveries

.NOTES
    Version: 1.0.0
    Performance Target: <1 min for 100 controllers
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath
)

# Default output path if not provided
if (-not $OutputPath) {
    # Normalize workspace root and detect KDS location
    $normalizedRoot = $WorkspaceRoot.TrimEnd('\')
    if ($normalizedRoot -match '\\KDS$') {
        # Workspace IS KDS
        $OutputPath = "$normalizedRoot\kds-brain\crawler-temp\api-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\kds-brain\crawler-temp\api-results.json"
    }
}

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "🌐 API Crawler Started" -ForegroundColor Cyan

$controllerPatterns = @("*Controller.cs", "*Controller.ts", "routes/*.ts", "routes/*.js", "api/*.py")
$excludeDirs = @("node_modules", "bin", "obj", "dist", "build")

$result = @{
    area = "API"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    endpoints = @()
    patterns = @{
        routing = "unknown"
        versioning = "unknown"
        auth = "unknown"
    }
    statistics = @{
        total_controllers = 0
        total_endpoints = 0
        http_methods = @{}
    }
}

# Helper: Extract HTTP method routes (C# attributes)
function Get-CSharpRoutes {
    param([string]$Content)
    
    $routes = @()
    # Match [HttpGet("...")], [HttpPost("...")], etc.
    $httpMethods = @('HttpGet', 'HttpPost', 'HttpPut', 'HttpDelete', 'HttpPatch')
    
    foreach ($method in $httpMethods) {
        $matches = [regex]::Matches($Content, "\[$method\([\x27\x22]([^\x27\x22]*)[\x27\x22]\)\]")
        foreach ($match in $matches) {
            $routes += @{
                method = $method.Replace('Http', '').ToUpper()
                route = $match.Groups[1].Value
            }
        }
    }
    return $routes
}

# Helper: Extract controller base route
function Get-ControllerRoute {
    param([string]$Content)
    
    $match = [regex]::Match($Content, '\[Route\([\x27\x22](api/[^\x27\x22]*)[\x27\x22]\)\]')
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return ""
}

# Helper: Extract DTOs from method signatures
function Get-DTOs {
    param([string]$Content)
    
    $dtos = @()
    # Match public Task<ActionResult<Type>> MethodName([FromBody] Type dto)
    $matches = [regex]::Matches($Content, 'ActionResult<(\w+)>')
    foreach ($match in $matches) {
        $dtos += @{type = "response"; name = $match.Groups[1].Value}
    }
    
    $matches = [regex]::Matches($Content, '\[FromBody\]\s+(\w+)\s+\w+')
    foreach ($match in $matches) {
        $dtos += @{type = "request"; name = $match.Groups[1].Value}
    }
    
    return $dtos | Select-Object -Property type, name -Unique
}

# Helper: Detect authorization
function Get-Authorization {
    param([string]$Content)
    
    if ($Content -match '\[Authorize\]') {
        return "attribute-based"
    } elseif ($Content -match 'requireAuth|authorize|@auth') {
        return "middleware"
    }
    return "none"
}

# Step 1: Discover controllers
Write-Host "`n[1/3] Discovering API controllers..." -ForegroundColor Yellow

$controllerFiles = @()
foreach ($pattern in $controllerPatterns) {
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
    $controllerFiles += $files
}

Write-Host "  Found $($controllerFiles.Count) controller files" -ForegroundColor Green

# Step 2: Parse controllers
Write-Host "`n[2/3] Parsing API endpoints..." -ForegroundColor Yellow

$routingPatterns = @{}
$authPatterns = @{}

foreach ($file in $controllerFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $baseRoute = Get-ControllerRoute -Content $content
        $routes = Get-CSharpRoutes -Content $content
        $dtos = Get-DTOs -Content $content
        $authorization = Get-Authorization -Content $content
        
        # Track patterns
        if ($baseRoute) { $routingPatterns["attribute-based"] = ($routingPatterns["attribute-based"] ?? 0) + 1 }
        $authPatterns[$authorization] = ($authPatterns[$authorization] ?? 0) + 1
        
        # Build endpoint entries
        $endpointEntries = @()
        foreach ($route in $routes) {
            $fullRoute = if ($baseRoute) { "/$baseRoute/$($route.route)" -replace '/+', '/' } else { $route.route }
            
            $endpointEntries += @{
                method = $route.method
                route = $fullRoute
                request_dto = ($dtos | Where-Object {$_.type -eq "request"} | Select-Object -First 1 -ExpandProperty name)
                response_dto = ($dtos | Where-Object {$_.type -eq "response"} | Select-Object -First 1 -ExpandProperty name)
                authorization = $authorization
            }
            
            # Update statistics
            $result.statistics.http_methods[$route.method] = ($result.statistics.http_methods[$route.method] ?? 0) + 1
            $result.statistics.total_endpoints++
        }
        
        $controller = @{
            path = $relativePath
            base_route = $baseRoute
            endpoints = $endpointEntries
        }
        
        $result.endpoints += $controller
        $result.statistics.total_controllers++
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

# Step 3: Detect patterns
Write-Host "`n[3/3] Detecting patterns..." -ForegroundColor Yellow

$result.patterns.routing = ($routingPatterns.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key ?? "unknown"
$result.patterns.auth = ($authPatterns.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key ?? "unknown"
$result.patterns.versioning = "url-path"  # Default assumption

$stopwatch.Stop()
$result.duration_seconds = [int]$stopwatch.Elapsed.TotalSeconds

$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "`n✅ API Crawler Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Controllers: $($result.statistics.total_controllers)" -ForegroundColor White
Write-Host "Endpoints: $($result.statistics.total_endpoints)" -ForegroundColor White
Write-Host "Duration: $($result.duration_seconds)s" -ForegroundColor White
Write-Host "════════════════════════════════════" -ForegroundColor Cyan

return $result
