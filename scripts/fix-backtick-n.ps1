# Fix backtick-n character in HTML files
# Removes PowerShell escape sequence that's being rendered as a character

$htmlFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\docs" -Filter "*.html" -Recurse

$fixedCount = 0
$totalFiles = $htmlFiles.Count

Write-Host "`n🔍 Scanning $totalFiles HTML files for backtick-n character..." -ForegroundColor Cyan

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    if ($content -match '`n') {
        $newContent = $content -replace '`n', "`n"
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        $fixedCount++
        Write-Host "✅ Fixed: $($file.FullName)" -ForegroundColor Green
    }
}

Write-Host "`n🎉 Complete! Fixed $fixedCount of $totalFiles files." -ForegroundColor Green
