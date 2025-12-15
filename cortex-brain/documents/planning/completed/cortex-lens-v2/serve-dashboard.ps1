# CORTEX Lens V2 - Local HTTP Server
# Purpose: Serve dashboard locally for iterative refinement
# Author: Asif Hussain
# Version: 1.0

param(
    [int]$Port = 8080,
    [string]$OutputPath = "d:\PROJECTS\CORTEX\cortex-lens-output"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORTEX Lens V2 Dashboard Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Validate output folder exists
if (-not (Test-Path $OutputPath)) {
    Write-Host "[ERROR] Output folder not found: $OutputPath" -ForegroundColor Red
    Write-Host "[ERROR] Generate dashboard first with: cortex-lens analyze <repo> --mock-data" -ForegroundColor Red
    exit 1
}

# Check if index.html exists
$indexPath = Join-Path $OutputPath "index.html"
if (-not (Test-Path $indexPath)) {
    Write-Host "[WARNING] index.html not found in output folder" -ForegroundColor Yellow
    Write-Host "[WARNING] Dashboard may not load correctly" -ForegroundColor Yellow
}

Write-Host "[INFO] Output Folder: $OutputPath" -ForegroundColor Green
Write-Host "[INFO] Port: $Port" -ForegroundColor Green
Write-Host ""

# Try Python HTTP server first (recommended)
$pythonAvailable = Get-Command python -ErrorAction SilentlyContinue
if ($pythonAvailable) {
    Write-Host "[SERVER] Starting Python HTTP server..." -ForegroundColor Green
    Write-Host "[SERVER] Dashboard available at: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "[SERVER] Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location $OutputPath
    python -m http.server $Port
} else {
    # Fallback to PowerShell HTTP server
    Write-Host "[WARNING] Python not found, using PowerShell HTTP server" -ForegroundColor Yellow
    Write-Host "[SERVER] Starting PowerShell HTTP server..." -ForegroundColor Green
    Write-Host "[SERVER] Dashboard available at: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "[SERVER] Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    $listener = New-Object System.Net.HttpListener
    $listener.Prefixes.Add("http://localhost:$Port/")
    
    try {
        $listener.Start()
        
        while ($listener.IsListening) {
            $context = $listener.GetContext()
            $request = $context.Request
            $response = $context.Response
            
            # Build file path
            $requestedPath = $request.Url.LocalPath.TrimStart('/')
            if ([string]::IsNullOrEmpty($requestedPath)) {
                $requestedPath = "index.html"
            }
            $filePath = Join-Path $OutputPath $requestedPath
            
            # Serve file or 404
            if (Test-Path $filePath) {
                try {
                    $content = [System.IO.File]::ReadAllBytes($filePath)
                    
                    # Set content type based on extension
                    $extension = [System.IO.Path]::GetExtension($filePath)
                    $contentType = switch ($extension) {
                        ".html" { "text/html" }
                        ".css"  { "text/css" }
                        ".js"   { "application/javascript" }
                        ".json" { "application/json" }
                        ".png"  { "image/png" }
                        ".jpg"  { "image/jpeg" }
                        ".svg"  { "image/svg+xml" }
                        default { "application/octet-stream" }
                    }
                    
                    $response.ContentType = $contentType
                    $response.ContentLength64 = $content.Length
                    $response.StatusCode = 200
                    $response.OutputStream.Write($content, 0, $content.Length)
                    
                    Write-Host "[200] $requestedPath" -ForegroundColor Green
                } catch {
                    Write-Host "[ERROR] Failed to read file: $filePath" -ForegroundColor Red
                    $response.StatusCode = 500
                }
            } else {
                Write-Host "[404] $requestedPath" -ForegroundColor Red
                $response.StatusCode = 404
                $notFoundContent = [System.Text.Encoding]::UTF8.GetBytes("404 - File Not Found: $requestedPath")
                $response.OutputStream.Write($notFoundContent, 0, $notFoundContent.Length)
            }
            
            $response.Close()
        }
    } catch {
        Write-Host "[ERROR] Server error: $_" -ForegroundColor Red
    } finally {
        if ($listener.IsListening) {
            $listener.Stop()
        }
        $listener.Close()
        Write-Host ""
        Write-Host "[SERVER] Stopped" -ForegroundColor Yellow
    }
}
