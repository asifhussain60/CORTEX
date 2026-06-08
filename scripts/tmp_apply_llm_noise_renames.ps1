$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'

# Map: current full filename -> proposed base name (without extension)
$renameMap = @{
  'Big Tit Milf Jessica Jaymes Loves Getting Fucked Rough By Huge Young Coc.mp4' = 'Jessica Jaymes Loves Getting Fucked Rough By Huge Young Coc'
  'Episode 191 Alexis Armani John Plus.mp4' = 'Alexis Armani John Plus'
  'Fitness Babe Kendra Lust Loves Huge Black Cock.mp4' = 'Kendra Lust Loves Huge Black Cock'
  'Horny Model Meets And Gets Dominated.mp4' = 'Meets And Gets Dominated'
  'Mourning Widow Natasha Nice Has Intense Sex With Her New Neig.mp4' = 'Natasha Nice Has Intense Sex With Her New Neig'
  'Petite Stalker Lulu Chu Tempts Neighbor In Grief With Pussy.mp4' = 'Lulu Chu Tempts Neighbor In Grief With Pussy'
  'Wives Abigail Mac And August Ames Love Big Black Cock.mp4' = 'Abigail Mac And August Ames Love Big Black Cock'
}

function Get-UniquePath([string]$targetPath, [string]$currentPath) {
    if ($targetPath -ceq $currentPath) { return $targetPath }
    if ($targetPath -ieq $currentPath) {
        # Case-only rename path; still valid target
        return $targetPath
    }
    if (-not (Test-Path -LiteralPath $targetPath)) { return $targetPath }
    $dir = Split-Path -Parent $targetPath
    $name = [System.IO.Path]::GetFileNameWithoutExtension($targetPath)
    $ext = [System.IO.Path]::GetExtension($targetPath)
    $i = 2
    while ($true) {
        $candidate = Join-Path $dir ("$name ($i)$ext")
        if ($candidate -ceq $currentPath) { return $candidate }
        if (-not (Test-Path -LiteralPath $candidate)) { return $candidate }
        $i++
    }
}

function Rename-CaseAware([string]$oldPath, [string]$finalPath) {
    if ($oldPath -ceq $finalPath) { return }
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
    $name = $f.Name
    if (-not $renameMap.ContainsKey($name)) { continue }

    $newBase = $renameMap[$name]
    $ext = $f.Extension
    $newName = "$newBase$ext"
    $targetPath = Join-Path $f.DirectoryName $newName
    $finalPath = Get-UniquePath -targetPath $targetPath -currentPath $f.FullName

    if ($finalPath -cne $f.FullName) {
        Rename-CaseAware -oldPath $f.FullName -finalPath $finalPath
        $ops += [PSCustomObject]@{
            OldPath = $f.FullName
            NewPath = $finalPath
            Status = 'Renamed'
        }
    }
}

if ($ops.Count -eq 0) {
    '[NO_CHANGES]'
} else {
    $ops | Sort-Object NewPath | ConvertTo-Json -Depth 4
}
