$ErrorActionPreference = 'Stop'

$root = 'G:\Downloads'
$renameMap = @{
  'Natasha Nice Has Intense Sex With Her New Neig.mp4' = 'Natasha Nice Has Intense Sex With Her New Neighbor.mp4'
  'Jessica Jaymes Loves Getting Fucked Rough By Huge Young Coc.mp4' = 'Jessica Jaymes Loves Getting Fucked Rough By Huge Young Cock.mp4'
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
        if ($candidate -ceq $currentPath) { return $candidate }
        if (-not (Test-Path -LiteralPath $candidate)) { return $candidate }
        $i++
    }
}

$ops = @()
Get-ChildItem -Path $root -Recurse -File | ForEach-Object {
    if (-not $renameMap.ContainsKey($_.Name)) { return }
    $old = $_.FullName
    $new = Join-Path $_.DirectoryName $renameMap[$_.Name]
    $final = Get-UniquePath -targetPath $new -currentPath $old
    if ($final -cne $old) {
        Move-Item -LiteralPath $old -Destination $final
        $ops += [PSCustomObject]@{ OldPath = $old; NewPath = $final; Status = 'Renamed' }
    }
}

if ($ops.Count -eq 0) { '[NO_CHANGES]' } else { $ops | ConvertTo-Json -Depth 4 }
