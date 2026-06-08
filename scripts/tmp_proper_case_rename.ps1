$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'

function To-ProperCase([string]$s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return $s }
    $parts = $s -split ' '
    $out = foreach ($p in $parts) {
        if ([string]::IsNullOrWhiteSpace($p)) { continue }
        if ($p -match '^[A-Z0-9]{2,}$') {
            $p
        }
        elseif ($p.Length -gt 1) {
            $p.Substring(0,1).ToUpper() + $p.Substring(1).ToLower()
        }
        else {
            $p.ToUpper()
        }
    }
    return ($out -join ' ').Trim()
}

function Get-UniquePath([string]$targetPath, [string]$currentPath) {
    if ($targetPath -ceq $currentPath) { return $targetPath }
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

function Rename-CaseAware([string]$oldPath, [string]$finalPath) {
    if ($oldPath -ceq $finalPath) { return }

    # Case-only rename on Windows requires an intermediate filename.
    if ($oldPath -ieq $finalPath -and $oldPath -cne $finalPath) {
        $dir = Split-Path -Parent $oldPath
        $ext = [System.IO.Path]::GetExtension($oldPath)
        $tmpName = [System.IO.Path]::GetFileNameWithoutExtension($oldPath) + '__tmpcase__' + [Guid]::NewGuid().ToString('N').Substring(0, 8) + $ext
        $tmpPath = Join-Path $dir $tmpName
        Move-Item -LiteralPath $oldPath -Destination $tmpPath
        Move-Item -LiteralPath $tmpPath -Destination $finalPath
        return
    }

    Move-Item -LiteralPath $oldPath -Destination $finalPath
}

$ops = @()
$files = Get-ChildItem -Path $root -Recurse -File
foreach ($f in $files) {
    $oldPath = $f.FullName
    $dir = $f.DirectoryName
    $ext = $f.Extension
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)

    $cleanBase = ($base -replace '\s+', ' ').Trim()
    $proper = To-ProperCase $cleanBase

    $target = Join-Path $dir ("$proper$ext")
    $final = Get-UniquePath -targetPath $target -currentPath $oldPath

    if ($final -cne $oldPath) {
        Rename-CaseAware -oldPath $oldPath -finalPath $final
        $ops += [PSCustomObject]@{ OldPath = $oldPath; NewPath = $final; Status = 'Renamed' }
    }
}

if ($ops.Count -eq 0) {
    '[NO_CHANGES]'
} else {
    $ops | Sort-Object NewPath | ConvertTo-Json -Depth 4
}
