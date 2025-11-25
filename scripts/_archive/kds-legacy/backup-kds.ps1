<#
.SYNOPSIS
    KDS Backup and Rollback Utility

.DESCRIPTION
    Creates timestamped backups of the entire KDS directory structure.
    Supports full backup, restoration, and verification.
    
    Part of KDS Independence Project safety nets.

.PARAMETER Action
    Action to perform: Backup, Restore, List, Verify

.PARAMETER BackupName
    Optional custom backup name (default: auto-generated timestamp)

.PARAMETER RestoreFrom
    Backup name to restore from (required for Restore action)

.PARAMETER OutputPath
    Custom path for backup storage (default: KDS/backups/)

.PARAMETER Compress
    Use ZIP compression (slower but smaller)

.PARAMETER VerifyIntegrity
    Verify backup integrity after creation

.EXAMPLE
    .\backup-kds.ps1 -Action Backup
    .\backup-kds.ps1 -Action Backup -BackupName "pre-phase1" -Compress
    .\backup-kds.ps1 -Action Restore -RestoreFrom "backup-20251104-090000"
    .\backup-kds.ps1 -Action List
    .\backup-kds.ps1 -Action Verify -RestoreFrom "backup-20251104-090000"

.NOTES
    Created: November 4, 2025
    Part of: KDS Independence Project - Phase 0.4
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Backup', 'Restore', 'List', 'Verify')]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$RestoreFrom = "",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Compress,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerifyIntegrity
)

# ============================================================================
# Configuration
# ============================================================================

$script:KdsRoot = Split-Path -Parent $PSScriptRoot
$script:DefaultBackupDir = Join-Path $script:KdsRoot 'backups'
$script:BackupDir = if ($OutputPath) { $OutputPath } else { $script:DefaultBackupDir }

# Items to exclude from backup
$script:ExcludePatterns = @(
    '.git',
    'node_modules',
    'bin',
    'obj',
    '*.cache',
    'backups'  # Don't backup backups!
)

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host $Message -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "⏳ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Get-FormattedSize {
    param([long]$Bytes)
    
    if ($Bytes -gt 1GB) {
        return "{0:N2} GB" -f ($Bytes / 1GB)
    }
    elseif ($Bytes -gt 1MB) {
        return "{0:N2} MB" -f ($Bytes / 1MB)
    }
    elseif ($Bytes -gt 1KB) {
        return "{0:N2} KB" -f ($Bytes / 1KB)
    }
    else {
        return "$Bytes bytes"
    }
}

function Test-ShouldExclude {
    param([string]$Path)
    
    foreach ($pattern in $script:ExcludePatterns) {
        if ($Path -like "*\$pattern\*" -or $Path -like "*/$pattern/*" -or $Path -like "*\$pattern") {
            return $true
        }
    }
    return $false
}

# ============================================================================
# Backup Functions
# ============================================================================

function New-KdsBackup {
    Write-Header "🗄️  KDS Backup"
    
    # Generate backup name
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backupName = if ($BackupName) { $BackupName } else { "backup-$timestamp" }
    $backupPath = Join-Path $script:BackupDir $backupName
    
    Write-Host "Backup Name: $backupName" -ForegroundColor Gray
    Write-Host "Source: $script:KdsRoot" -ForegroundColor Gray
    Write-Host "Destination: $backupPath" -ForegroundColor Gray
    Write-Host ""
    
    # Ensure backup directory exists
    if (-not (Test-Path $script:BackupDir)) {
        Write-Step "Creating backup directory..."
        New-Item -ItemType Directory -Path $script:BackupDir -Force | Out-Null
        Write-Success "Backup directory created"
    }
    
    # Check if backup already exists
    if (Test-Path $backupPath) {
        Write-Error-Custom "Backup '$backupName' already exists!"
        Write-Host "Use a different name or delete the existing backup." -ForegroundColor Yellow
        return $null
    }
    
    # Start backup
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    Write-Step "Scanning files..."
    
    # Get all files to backup
    $allFiles = Get-ChildItem -Path $script:KdsRoot -Recurse -File | 
                Where-Object { -not (Test-ShouldExclude $_.FullName) }
    
    $fileCount = $allFiles.Count
    $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
    
    Write-Host "  Files to backup: $fileCount" -ForegroundColor Cyan
    Write-Host "  Total size: $(Get-FormattedSize $totalSize)" -ForegroundColor Cyan
    Write-Host ""
    
    # Create backup directory
    Write-Step "Creating backup structure..."
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    
    # Copy files
    Write-Step "Copying files..."
    $copiedCount = 0
    $copiedSize = 0
    
    foreach ($file in $allFiles) {
        $relativePath = $file.FullName.Replace($script:KdsRoot, '').TrimStart('\', '/')
        $destPath = Join-Path $backupPath $relativePath
        $destDir = Split-Path -Parent $destPath
        
        # Create directory structure
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Copy file
        Copy-Item -Path $file.FullName -Destination $destPath -Force
        
        $copiedCount++
        $copiedSize += $file.Length
        
        # Progress indicator
        if ($copiedCount % 50 -eq 0) {
            $percentComplete = [Math]::Round(($copiedCount / $fileCount) * 100, 1)
            Write-Host "  [$copiedCount/$fileCount] $percentComplete% - $(Get-FormattedSize $copiedSize)" -ForegroundColor Gray
        }
    }
    
    Write-Success "Files copied: $copiedCount"
    
    # Create manifest
    Write-Step "Creating backup manifest..."
    $manifest = @{
        BackupName = $backupName
        CreatedAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        SourcePath = $script:KdsRoot
        FileCount = $fileCount
        TotalSize = $totalSize
        FormattedSize = Get-FormattedSize $totalSize
        KdsVersion = "v6.0"
        Purpose = "KDS Independence Project - Phase 0.4"
    }
    
    $manifestPath = Join-Path $backupPath 'backup-manifest.json'
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    Write-Success "Manifest created"
    
    # Optional: Compress to ZIP
    if ($Compress) {
        Write-Step "Compressing backup to ZIP..."
        $zipPath = "$backupPath.zip"
        
        try {
            Compress-Archive -Path $backupPath -DestinationPath $zipPath -CompressionLevel Optimal
            $zipSize = (Get-Item $zipPath).Length
            $compressionRatio = [Math]::Round((1 - ($zipSize / $totalSize)) * 100, 1)
            
            Write-Success "Compressed to ZIP ($(Get-FormattedSize $zipSize), $compressionRatio% reduction)"
            
            # Remove uncompressed backup
            Write-Step "Removing uncompressed backup..."
            Remove-Item -Path $backupPath -Recurse -Force
            Write-Success "Uncompressed backup removed"
            
            $backupPath = $zipPath
        }
        catch {
            Write-Error-Custom "Compression failed: $_"
        }
    }
    
    # Optional: Verify integrity
    if ($VerifyIntegrity) {
        Write-Step "Verifying backup integrity..."
        $verification = Test-BackupIntegrity -BackupPath $backupPath
        if ($verification) {
            Write-Success "Backup integrity verified"
        }
        else {
            Write-Error-Custom "Backup integrity check failed!"
        }
    }
    
    $stopwatch.Stop()
    $duration = $stopwatch.Elapsed.TotalSeconds
    
    Write-Host ""
    Write-Header "✅ Backup Complete!"
    Write-Host "Backup Name: $backupName" -ForegroundColor Green
    Write-Host "Location: $backupPath" -ForegroundColor Green
    Write-Host "Files: $fileCount" -ForegroundColor Green
    Write-Host "Size: $(Get-FormattedSize $totalSize)" -ForegroundColor Green
    Write-Host "Duration: $([Math]::Round($duration, 2))s" -ForegroundColor Green
    Write-Host ""
    Write-Host "To restore this backup, run:" -ForegroundColor Cyan
    Write-Host "  .\backup-kds.ps1 -Action Restore -RestoreFrom '$backupName'" -ForegroundColor Gray
    Write-Host ""
    
    return @{
        BackupName = $backupName
        Path = $backupPath
        FileCount = $fileCount
        Size = $totalSize
        Duration = $duration
    }
}

# ============================================================================
# Restore Functions
# ============================================================================

function Restore-KdsBackup {
    Write-Header "🔄 KDS Restore"
    
    if ([string]::IsNullOrWhiteSpace($RestoreFrom)) {
        Write-Error-Custom "RestoreFrom parameter is required for Restore action"
        Write-Host "Example: .\backup-kds.ps1 -Action Restore -RestoreFrom 'backup-20251104-090000'" -ForegroundColor Gray
        return $null
    }
    
    # Find backup
    $backupPath = Join-Path $script:BackupDir $RestoreFrom
    $zipPath = "$backupPath.zip"
    
    $isZip = $false
    if (Test-Path $zipPath) {
        $backupPath = $zipPath
        $isZip = $true
    }
    elseif (-not (Test-Path $backupPath)) {
        Write-Error-Custom "Backup '$RestoreFrom' not found in $script:BackupDir"
        Write-Host "Available backups:" -ForegroundColor Yellow
        Show-AvailableBackups
        return $null
    }
    
    Write-Host "Backup: $RestoreFrom" -ForegroundColor Gray
    Write-Host "Source: $backupPath" -ForegroundColor Gray
    Write-Host "Destination: $script:KdsRoot" -ForegroundColor Gray
    Write-Host ""
    
    # Warning
    Write-Host "⚠️  WARNING: This will OVERWRITE current KDS files!" -ForegroundColor Red
    Write-Host ""
    $confirm = Read-Host "Type 'RESTORE' to confirm"
    
    if ($confirm -ne 'RESTORE') {
        Write-Host "Restore cancelled." -ForegroundColor Yellow
        return $null
    }
    
    Write-Host ""
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Extract if ZIP
    if ($isZip) {
        Write-Step "Extracting ZIP backup..."
        $tempExtractPath = Join-Path $script:BackupDir "temp-extract-$([Guid]::NewGuid())"
        
        try {
            Expand-Archive -Path $backupPath -DestinationPath $tempExtractPath -Force
            $backupPath = $tempExtractPath
            Write-Success "ZIP extracted"
        }
        catch {
            Write-Error-Custom "Failed to extract ZIP: $_"
            return $null
        }
    }
    
    # Read manifest
    $manifestPath = Join-Path $backupPath 'backup-manifest.json'
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath | ConvertFrom-Json
        Write-Host "Backup Info:" -ForegroundColor Cyan
        Write-Host "  Created: $($manifest.CreatedAt)" -ForegroundColor Gray
        Write-Host "  Files: $($manifest.FileCount)" -ForegroundColor Gray
        Write-Host "  Size: $($manifest.FormattedSize)" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Restore files
    Write-Step "Restoring files..."
    $allFiles = Get-ChildItem -Path $backupPath -Recurse -File | 
                Where-Object { $_.Name -ne 'backup-manifest.json' }
    
    $restoredCount = 0
    foreach ($file in $allFiles) {
        $relativePath = $file.FullName.Replace($backupPath, '').TrimStart('\', '/')
        $destPath = Join-Path $script:KdsRoot $relativePath
        $destDir = Split-Path -Parent $destPath
        
        # Create directory structure
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Copy file
        Copy-Item -Path $file.FullName -Destination $destPath -Force
        $restoredCount++
        
        # Progress indicator
        if ($restoredCount % 50 -eq 0) {
            Write-Host "  Restored: $restoredCount files" -ForegroundColor Gray
        }
    }
    
    Write-Success "Files restored: $restoredCount"
    
    # Cleanup temp extract
    if ($isZip -and (Test-Path $tempExtractPath)) {
        Write-Step "Cleaning up temporary files..."
        Remove-Item -Path $tempExtractPath -Recurse -Force
        Write-Success "Cleanup complete"
    }
    
    $stopwatch.Stop()
    $duration = $stopwatch.Elapsed.TotalSeconds
    
    Write-Host ""
    Write-Header "✅ Restore Complete!"
    Write-Host "Restored from: $RestoreFrom" -ForegroundColor Green
    Write-Host "Files: $restoredCount" -ForegroundColor Green
    Write-Host "Duration: $([Math]::Round($duration, 2))s" -ForegroundColor Green
    Write-Host ""
    Write-Host "KDS has been restored to the backed-up state." -ForegroundColor Cyan
    Write-Host ""
    
    return @{
        BackupName = $RestoreFrom
        RestoredFiles = $restoredCount
        Duration = $duration
    }
}

# ============================================================================
# List Functions
# ============================================================================

function Show-AvailableBackups {
    Write-Header "📋 Available Backups"
    
    if (-not (Test-Path $script:BackupDir)) {
        Write-Host "No backups found. Backup directory doesn't exist." -ForegroundColor Yellow
        return
    }
    
    # Find all backups (folders and ZIPs)
    $backupFolders = Get-ChildItem -Path $script:BackupDir -Directory | 
                     Where-Object { $_.Name -like 'backup-*' }
    $backupZips = Get-ChildItem -Path $script:BackupDir -Filter '*.zip' | 
                  Where-Object { $_.BaseName -like 'backup-*' }
    
    $allBackups = @()
    
    foreach ($folder in $backupFolders) {
        $manifestPath = Join-Path $folder.FullName 'backup-manifest.json'
        $manifest = if (Test-Path $manifestPath) { 
            Get-Content $manifestPath | ConvertFrom-Json 
        } else { $null }
        
        $size = (Get-ChildItem -Path $folder.FullName -Recurse -File | 
                 Measure-Object -Property Length -Sum).Sum
        
        $allBackups += @{
            Name = $folder.Name
            Type = "Folder"
            Created = $folder.CreationTime
            Size = $size
            FileCount = if ($manifest) { $manifest.FileCount } else { "Unknown" }
        }
    }
    
    foreach ($zip in $backupZips) {
        $allBackups += @{
            Name = $zip.BaseName
            Type = "ZIP"
            Created = $zip.CreationTime
            Size = $zip.Length
            FileCount = "Compressed"
        }
    }
    
    if ($allBackups.Count -eq 0) {
        Write-Host "No backups found in $script:BackupDir" -ForegroundColor Yellow
        return
    }
    
    # Sort by creation time (newest first)
    $allBackups = $allBackups | Sort-Object -Property { $_.Created } -Descending
    
    Write-Host "Backup Directory: $script:BackupDir" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Available Backups:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($backup in $allBackups) {
        $createdStr = $backup.Created.ToString('yyyy-MM-dd HH:mm:ss')
        $sizeStr = Get-FormattedSize $backup.Size
        $typeIcon = if ($backup.Type -eq "ZIP") { "📦" } else { "📁" }
        
        Write-Host "$typeIcon " -NoNewline -ForegroundColor Yellow
        Write-Host "$($backup.Name)" -ForegroundColor White
        Write-Host "    Created: $createdStr" -ForegroundColor Gray
        Write-Host "    Size: $sizeStr" -ForegroundColor Gray
        Write-Host "    Files: $($backup.FileCount)" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "To restore a backup, run:" -ForegroundColor Cyan
    Write-Host "  .\backup-kds.ps1 -Action Restore -RestoreFrom '<backup-name>'" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# Verification Functions
# ============================================================================

function Test-BackupIntegrity {
    param([string]$BackupPath)
    
    Write-Header "🔍 Backup Verification"
    
    if ([string]::IsNullOrWhiteSpace($BackupPath)) {
        if ([string]::IsNullOrWhiteSpace($RestoreFrom)) {
            Write-Error-Custom "RestoreFrom parameter is required for Verify action"
            return $false
        }
        
        $BackupPath = Join-Path $script:BackupDir $RestoreFrom
        if (-not (Test-Path $BackupPath)) {
            $BackupPath = "$BackupPath.zip"
        }
    }
    
    if (-not (Test-Path $BackupPath)) {
        Write-Error-Custom "Backup not found: $BackupPath"
        return $false
    }
    
    Write-Host "Verifying: $BackupPath" -ForegroundColor Gray
    Write-Host ""
    
    $isZip = $BackupPath -like '*.zip'
    
    if ($isZip) {
        Write-Step "Testing ZIP integrity..."
        try {
            # Try to read ZIP contents
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $zip = [System.IO.Compression.ZipFile]::OpenRead($BackupPath)
            $entryCount = $zip.Entries.Count
            $zip.Dispose()
            
            Write-Success "ZIP is valid ($entryCount entries)"
            return $true
        }
        catch {
            Write-Error-Custom "ZIP is corrupted: $_"
            return $false
        }
    }
    else {
        Write-Step "Verifying backup structure..."
        
        # Check manifest
        $manifestPath = Join-Path $BackupPath 'backup-manifest.json'
        if (-not (Test-Path $manifestPath)) {
            Write-Error-Custom "Backup manifest not found!"
            return $false
        }
        
        try {
            $manifest = Get-Content $manifestPath | ConvertFrom-Json
            Write-Success "Manifest is valid"
            
            # Count files
            $fileCount = (Get-ChildItem -Path $BackupPath -Recurse -File | 
                         Where-Object { $_.Name -ne 'backup-manifest.json' }).Count
            
            if ($fileCount -eq $manifest.FileCount) {
                Write-Success "File count matches manifest ($fileCount files)"
                return $true
            }
            else {
                Write-Error-Custom "File count mismatch! Expected: $($manifest.FileCount), Found: $fileCount"
                return $false
            }
        }
        catch {
            Write-Error-Custom "Failed to read manifest: $_"
            return $false
        }
    }
}

# ============================================================================
# Main Execution
# ============================================================================

try {
    switch ($Action) {
        'Backup' {
            $result = New-KdsBackup
            exit $(if ($result) { 0 } else { 1 })
        }
        
        'Restore' {
            $result = Restore-KdsBackup
            exit $(if ($result) { 0 } else { 1 })
        }
        
        'List' {
            Show-AvailableBackups
            exit 0
        }
        
        'Verify' {
            $isValid = Test-BackupIntegrity
            exit $(if ($isValid) { 0 } else { 1 })
        }
    }
}
catch {
    Write-Host ""
    Write-Error-Custom "Operation failed: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
