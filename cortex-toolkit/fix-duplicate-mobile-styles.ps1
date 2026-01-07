# ============================================================================
# CORTEX Toolkit - Fix Duplicate Mobile Optimization Styles
# ============================================================================
# Purpose: Remove duplicate mobile optimization style blocks from <body>
# Author: Asif Hussain
# Version: 1.0.0
# Created: January 3, 2026
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$DocsPath = "docs",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowDetails
)

function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }

Write-Info "🔧 CORTEX Duplicate Mobile Styles Fixer v1.0.0"
Write-Host ""

$htmlFiles = Get-ChildItem -Path $DocsPath -Filter "*.html" -Recurse
$affectedFiles = @()
$fixedFiles = 0

Write-Info "Scanning $($htmlFiles.Count) HTML files for duplicate mobile styles..."
Write-Host ""

# Pattern to detect style blocks in body (after </head>)
$duplicatePattern = @'
</head>
<body>
    <!-- Glass Header Navigation -->
    <header class="glass-header">
<style>
/\* Mobile font optimization \*/
html {
    -webkit-text-size-adjust: 100%;
    -moz-text-size-adjust: 100%;
    text-size-adjust: 100%;
}
</style>
<style>
/\* Touch target optimization \*/
a, button, \[role="button"\] {
    min-width: 44px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
</style>
<style>
/\* Mobile touch optimization \*/
button, a, input, select, textarea, \[role="button"\] {
    touch-action: manipulation;
    -webkit-tap-highlight-color: rgba\(0,0,0,0\);
}
</style>
        <div class="header-content">
'@

$replacement = @'
</head>
<body>
    <!-- Glass Header Navigation -->
    <header class="glass-header">
        <div class="header-content">
'@

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Check if file has duplicate styles in body
    if ($content -match '(?s)</head>.*?<body>.*?<header class="glass-header">\s*<style>') {
        $affectedFiles += $file
        
        if (-not $DryRun) {
            # Remove style blocks between <header> and <div class="header-content">
            $newContent = $content -replace '(<header class="glass-header">)\s*<style>[\s\S]*?</style>\s*<style>[\s\S]*?</style>\s*<style>[\s\S]*?</style>\s*(<div class="header-content">)', '$1`n        $2'
            
            if ($newContent -ne $content) {
                Set-Content -Path $file.FullName -Value $newContent -NoNewline
                $fixedFiles++
                
                if ($ShowDetails) {
                    Write-Success "Fixed: $($file.FullName.Replace((Get-Location).Path, '').TrimStart('\'))"
                }
            }
        }
        else {
            Write-Warning "Would fix: $($file.FullName.Replace((Get-Location).Path, '').TrimStart('\'))"
        }
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📊 RESULTS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

if ($affectedFiles.Count -eq 0) {
    Write-Success "No duplicate mobile styles found!"
    exit 0
}

Write-Info "Files with duplicate styles: $($affectedFiles.Count)"

if ($DryRun) {
    Write-Warning "DRY RUN MODE - No changes made"
    Write-Info "Run without -DryRun to apply fixes"
}
else {
    Write-Success "Fixed $fixedFiles files"
}

Write-Host ""
exit 0
