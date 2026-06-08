$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'
$registryPath = 'D:\PROJECTS\CORTEX\.github\prompts\filename-sanitizer.studios.json'
$registry = Get-Content -Raw -Path $registryPath | ConvertFrom-Json

function Get-StudioFolder([string]$baseNameLower, $reg) {
    foreach ($studio in $reg.studios) {
        foreach ($alias in $studio.aliases) {
            if ($baseNameLower -match [regex]::Escape($alias.ToLowerInvariant())) {
                return $studio.folder
            }
        }
    }
    return $reg.fallbackFolder
}

function To-TitleSmart([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $s }
    $parts = $s -split ' '
    $result = foreach ($p in $parts) {
        if ($p -match '^[A-Z0-9]{2,}$') { $p }
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

$noiseTokens = @('xvideos', 'belessa', 'bellesa', 'hd', 'bbc', 'blacked', 'blackedraw', 'pure taboo', 'pure_taboo', 'vixen', 'deeper')
$noisePattern = '(?i)\b(?:' + (($noiseTokens | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')\b'
$fillerPattern = '(?i)\b(?:the|a|an|very|really)\b'

$results = @()
$files = Get-ChildItem -Path $root -File

foreach ($f in $files) {
    $oldPath = $f.FullName
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $ext = $f.Extension
    $studioFolder = Get-StudioFolder -baseNameLower $base.ToLowerInvariant() -reg $registry

    $s = $base -replace '[_\.]', ' '
    $s = $s -replace '\s+', ' '
    $s = [regex]::Replace($s, $noisePattern, ' ')
    $s = [regex]::Replace($s, $fillerPattern, ' ')
    $s = $s -replace '\s+', ' '
    $s = Remove-AdjacentDuplicates $s
    $s = $s.Trim(' ', '-', '_', '.')
    $s = To-TitleSmart $s

    if ($s.Length -gt 60 -and $s -match ' - ') {
        $s = ($s -split ' - ')[0].Trim()
    }
    if ($s.Length -gt 80) {
        $trim = $s.Substring(0, 80)
        if ($trim -match '^(.*)\s+\S+$') { $trim = $matches[1] }
        $s = $trim.Trim()
    }
    if ([string]::IsNullOrWhiteSpace($s)) {
        $fallback = ($base -replace '[_\.]', ' ' -replace '\s+', ' ').Trim()
        $s = To-TitleSmart $fallback
    }

    $destDir = Join-Path $root $studioFolder
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir | Out-Null
    }

    $destName = "$s$ext"
    $destPath = Join-Path $destDir $destName
    $finalPath = Get-UniquePath $destPath

    Move-Item -LiteralPath $oldPath -Destination $finalPath

    $results += [PSCustomObject]@{
        OldPath = $oldPath
        NewPath = $finalPath
        Status = 'Moved'
    }
}

$results | Sort-Object NewPath | Format-Table -AutoSize | Out-String -Width 320
