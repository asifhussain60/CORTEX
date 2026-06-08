$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'
$registryPath = 'D:\PROJECTS\CORTEX\.github\prompts\filename-sanitizer.studios.json'
$registry = Get-Content -Raw -Path $registryPath | ConvertFrom-Json

function Get-StudioFolder([string]$textLower, $reg) {
    $pairs = @()
    foreach ($studio in $reg.studios) {
        foreach ($alias in $studio.aliases) {
            $pairs += [PSCustomObject]@{ Folder = $studio.folder; Alias = $alias.ToLowerInvariant(); Len = $alias.Length }
        }
    }
    foreach ($p in ($pairs | Sort-Object Len -Descending)) {
        if ($textLower -match [regex]::Escape($p.Alias)) { return $p.Folder }
    }
    return $reg.fallbackFolder
}

function To-TitleSmart([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $s }
    $smallWords = @('and','or','for','on','in','of','to','with','by','at','from','into','over','under')
    $parts = $s -split ' '
    $out = for ($i = 0; $i -lt $parts.Count; $i++) {
        $p = $parts[$i]
        $pl = $p.ToLowerInvariant()
        if ($p -match '^[A-Z0-9]{2,}$') { $p }
        elseif ($i -gt 0 -and $smallWords -contains $pl) { $pl }
        elseif ($p.Length -gt 1) { $p.Substring(0,1).ToUpper() + $p.Substring(1).ToLower() }
        else { $p.ToUpper() }
    }
    return ($out -join ' ').Trim()
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

function Clean-BaseName([string]$base, [string[]]$studioAliases) {
    $noise = @('xvideos','hd','bbc','1080p','720p','2160p','4k','uhd') + $studioAliases
    $noise = $noise | Select-Object -Unique
    $noisePattern = '(?i)\b(?:' + (($noise | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')\b'
    $fillerPattern = '(?i)\b(?:the|a|an|very|really)\b'

    $s = $base
    $s = $s -replace '\s*\(\d+\)$', ''
    $s = $s -replace '[_\.]', ' '
    $s = $s -replace '\s+', ' '
    $s = [regex]::Replace($s, $noisePattern, ' ')
    $s = [regex]::Replace($s, $fillerPattern, ' ')
    $s = $s -replace '\s+', ' '

    $s = Remove-AdjacentDuplicates $s
    $s = $s.Trim(' ', '-', '_', '.', ',')

    # Remove single-letter leftovers created by token removal.
    $s = ($s -split ' ' | Where-Object { $_.Length -gt 1 -or $_ -match '^[0-9]+$' }) -join ' '
    $s = ($s -replace '\s+', ' ').Trim()

    $s = To-TitleSmart $s

    if ($s.Length -gt 60 -and $s -match ' - ') {
        $s = ($s -split ' - ')[0].Trim()
    }
    if ($s.Length -gt 80) {
        $t = $s.Substring(0,80)
        if ($t -match '^(.*)\s+\S+$') { $t = $matches[1] }
        $s = $t.Trim()
    }

    return $s
}

function Get-UniquePath([string]$targetPath, [string]$currentPath) {
    if ($targetPath -ieq $currentPath) { return $targetPath }
    if (-not (Test-Path -LiteralPath $targetPath)) { return $targetPath }
    $dir = Split-Path -Parent $targetPath
    $name = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
    $ext = [System.IO.Path]::GetExtension($targetPath)
    $i = 2
    while ($true) {
        $candidate = Join-Path $dir ("$name ($i)$ext")
        if ($candidate -ieq $currentPath) { return $candidate }
        if (-not (Test-Path -LiteralPath $candidate)) { return $candidate }
        $i++
    }
}

$allAliases = @()
foreach ($s in $registry.studios) { $allAliases += $s.aliases }

$ops = @()
$files = Get-ChildItem -Path $root -Recurse -File
foreach ($f in $files) {
    $oldPath = $f.FullName
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $ext = $f.Extension

    $detectedFolder = Get-StudioFolder -textLower $base.ToLowerInvariant() -reg $registry

    # Keep file in known parent folder when parent is already a canonical studio.
    $parent = Split-Path -Leaf (Split-Path -Parent $oldPath)
    $canonicalFolders = @($registry.studios | ForEach-Object { $_.folder }) + @($registry.fallbackFolder)
    if ($canonicalFolders -contains $parent) {
        $destFolderName = $parent
    } else {
        $destFolderName = $detectedFolder
    }

    $cleanBase = Clean-BaseName -base $base -studioAliases $allAliases
    if ([string]::IsNullOrWhiteSpace($cleanBase)) {
        $fallback = ($base -replace '[_\.]',' ' -replace '\s+',' ').Trim()
        $cleanBase = To-TitleSmart $fallback
    }

    $destDir = Join-Path $root $destFolderName
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir | Out-Null
    }

    $destPath = Join-Path $destDir ("$cleanBase$ext")
    $finalPath = Get-UniquePath -targetPath $destPath -currentPath $oldPath

    if ($finalPath -ne $oldPath) {
        Move-Item -LiteralPath $oldPath -Destination $finalPath
        $ops += [PSCustomObject]@{
            OldPath = $oldPath
            NewPath = $finalPath
            Status = 'Renamed/Relocated'
        }
    }
}

$ops | Sort-Object NewPath | ConvertTo-Json -Depth 4
