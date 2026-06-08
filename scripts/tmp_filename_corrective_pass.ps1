$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'
$registryPath = 'D:\PROJECTS\CORTEX\.github\prompts\filename-sanitizer.studios.json'
$registry = Get-Content -Raw -Path $registryPath | ConvertFrom-Json

function Get-StudioFolder([string]$textLower, $reg) {
    # Prefer longer aliases first (e.g., blackedraw before blacked)
    $pairs = @()
    foreach ($studio in $reg.studios) {
        foreach ($alias in $studio.aliases) {
            $pairs += [PSCustomObject]@{ StudioFolder = $studio.folder; Alias = $alias.ToLowerInvariant(); Len = $alias.Length }
        }
    }
    foreach ($p in ($pairs | Sort-Object Len -Descending)) {
        if ($textLower -match [regex]::Escape($p.Alias)) { return $p.StudioFolder }
    }
    return $reg.fallbackFolder
}

function To-TitleSmart([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $s }
    $smallWords = @('and','or','for','on','in','of','to','with','by','at')
    $parts = $s -split ' '
    $result = for ($i = 0; $i -lt $parts.Count; $i++) {
        $p = $parts[$i]
        $pl = $p.ToLowerInvariant()
        if ($p -match '^[A-Z0-9]{2,}$') { $p }
        elseif ($i -gt 0 -and $smallWords -contains $pl) { $pl }
        elseif ($p.Length -gt 1) { $p.Substring(0, 1).ToUpper() + $p.Substring(1).ToLower() }
        else { $p.ToUpper() }
    }
    return ($result -join ' ').Trim()
}

function Remove-AdjacentDuplicates([string]$s) {
    $tokens = @()
    foreach ($w in ($s -split ' ')) {
        if ([string]::IsNullOrWhiteSpace($w)) { continue }
        if ($tokens.Count -eq 0 -or $tokens[-1].ToLowerInvariant() -ne $w.ToLowerInvariant()) {
            $tokens += $w
        }
    }
    return ($tokens -join ' ')
}

function Get-UniquePath([string]$targetPath) {
    if (-not (Test-Path -LiteralPath $targetPath)) { return $targetPath }
    $dir = Split-Path -Parent $targetPath
    $name = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
    $ext = [System.IO.Path]::GetExtension($targetPath)
    $i = 2
    while ($true) {
        $candidate = Join-Path $dir ("$name ($i)$ext")
        if (-not (Test-Path -LiteralPath $candidate)) { return $candidate }
        $i++
    }
}

$aliasNoise = @()
foreach ($studio in $registry.studios) { $aliasNoise += $studio.aliases }
$fixedNoise = @('xvideos','hd','bbc')
$noiseTokens = ($aliasNoise + $fixedNoise | Select-Object -Unique)
$noisePattern = '(?i)\\b(?:' + (($noiseTokens | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')\\b'
$fillerPattern = '(?i)\\b(?:the|a|an|very|really)\\b'

$ops = @()
$allFiles = Get-ChildItem -Path $root -Recurse -File

foreach ($f in $allFiles) {
    $oldPath = $f.FullName
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $ext = $f.Extension

    $studioFolder = Get-StudioFolder -textLower $base.ToLowerInvariant() -reg $registry

    $s = $base -replace '[_\.]', ' '
    $s = $s -replace '\\s+', ' '
    $s = [regex]::Replace($s, $noisePattern, ' ')
    $s = [regex]::Replace($s, $fillerPattern, ' ')
    $s = $s -replace '\\s+', ' '
    $s = Remove-AdjacentDuplicates $s
    $s = $s.Trim(' ', '-', '_', '.', ',')

    # Clean dangling single-letter artifacts from token stripping (e.g., "S")
    $s = ($s -split ' ' | Where-Object { $_.Length -gt 1 -or $_ -match '^[0-9]+$' }) -join ' '
    $s = $s -replace '\\s+', ' '
    $s = $s.Trim()

    $s = To-TitleSmart $s

    if ($s.Length -gt 60 -and $s -match ' - ') {
        $s = ($s -split ' - ')[0].Trim()
    }
    if ($s.Length -gt 80) {
        $trim = $s.Substring(0, 80)
        if ($trim -match '^(.*)\\s+\\S+$') { $trim = $matches[1] }
        $s = $trim.Trim()
    }

    if ([string]::IsNullOrWhiteSpace($s)) {
        $fallback = ($base -replace '[_\.]', ' ' -replace '\\s+', ' ').Trim()
        $s = To-TitleSmart $fallback
    }

    $destDir = Join-Path $root $studioFolder
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir | Out-Null
    }

    $destName = "$s$ext"
    $destPath = Join-Path $destDir $destName
    $finalPath = Get-UniquePath $destPath

    if ($oldPath -ne $finalPath) {
        Move-Item -LiteralPath $oldPath -Destination $finalPath
        $ops += [PSCustomObject]@{ OldPath = $oldPath; NewPath = $finalPath; Status = 'Moved' }
    }
}

$ops | Sort-Object NewPath | ConvertTo-Json -Depth 4
