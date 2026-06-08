$ErrorActionPreference = 'Stop'

$source = 'G:\Downloads'
$noisePattern = '(?i)\b(?:xvideos|belessa|bellesa|hd|bbc|blacked)\b'
$fillerPattern = '(?i)\b(?:the|a|an|very|really)\b'

function Get-Studio([string]$name) {
    $n = $name.ToLowerInvariant()
    if ($n -match 'blackedraw') { return 'BlackedRaw' }
    elseif ($n -match 'blacked') { return 'Blacked' }
    elseif ($n -match 'deeper') { return 'Deeper' }
    elseif ($n -match 'pure[ _]?taboo') { return 'PureTaboo' }
    elseif ($n -match 'vixen') { return 'Vixen' }
    elseif ($n -match 'bellesa|belessa|bellesa plus') { return 'Belessa' }
    else { return 'UnknownStudio' }
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

$rows = foreach ($f in (Get-ChildItem -Path $source -File)) {
    $origBase = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $ext = $f.Extension
    $studio = Get-Studio $origBase

    $s = $origBase -replace '[_\.]', ' '
    $s = $s -replace '\s+', ' '
    $s = [regex]::Replace($s, $noisePattern, ' ')
    $s = $s -replace '\s+', ' '

    $tokens = @()
    foreach ($w in ($s.Trim() -split ' ')) {
        if ($tokens.Count -eq 0 -or $tokens[-1].ToLowerInvariant() -ne $w.ToLowerInvariant()) {
            $tokens += $w
        }
    }
    $s = ($tokens -join ' ')
    $s = $s.Trim(' ', '-', '_', '.')

    $s = [regex]::Replace($s, $fillerPattern, ' ')
    $s = $s -replace '\s+', ' '
    $s = $s.Trim()
    $s = To-TitleSmart $s

    if ($s.Length -gt 60 -and $s -match ' - ') {
        $s = ($s -split ' - ')[0].Trim()
    }

    if ($s.Length -gt 80) {
        $trim = $s.Substring(0, 80)
        if ($trim -match '^(.*)\s+\S+$') {
            $trim = $matches[1]
        }
        $s = $trim.Trim()
    }

    if ([string]::IsNullOrWhiteSpace($s)) {
        $s = To-TitleSmart $origBase
    }

    [PSCustomObject]@{
        Studio = $studio
        CurrentName = $f.Name
        ProposedName = "$s$ext"
        TargetFolder = "G:\Downloads\$studio\"
        Action = 'Preview only'
    }
}

$rows | Sort-Object Studio, ProposedName | ConvertTo-Json -Depth 4
