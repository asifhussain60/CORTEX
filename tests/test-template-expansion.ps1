#!/usr/bin/env pwsh
# Test script for template expansion

# Dot-source the workspace resolver first (required dependency)
. "$PSScriptRoot/../scripts/lib/workspace-resolver.ps1"

# Dot-source the config template engine
. "$PSScriptRoot/../scripts/lib/config-template-engine.ps1"

# Test 1: Expand cortex.config.template.json
Write-Host "Testing cortex.config.template.json expansion..." -ForegroundColor Cyan
Expand-ConfigTemplate `
    -TemplatePath "$PSScriptRoot/../cortex.config.template.json" `
    -OutputPath "$PSScriptRoot/../cortex.config.test.json" `
    -Force

if (Test-Path "$PSScriptRoot/../cortex.config.test.json") {
    Write-Host "✅ cortex.config.test.json generated successfully" -ForegroundColor Green
    
    # Validate JSON syntax
    try {
        $json = Get-Content "$PSScriptRoot/../cortex.config.test.json" -Raw | ConvertFrom-Json
        Write-Host "✅ JSON syntax valid" -ForegroundColor Green
        Write-Host "   PROJECT_NAME: $($json.application.name)" -ForegroundColor Gray
        Write-Host "   PROJECT_ROOT: $($json.application.rootPath)" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ JSON syntax invalid: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "❌ Failed to generate cortex.config.test.json" -ForegroundColor Red
}

Write-Host ""

# Test 2: Expand tooling-inventory.template.json
Write-Host "Testing tooling-inventory.template.json expansion..." -ForegroundColor Cyan
Expand-ConfigTemplate `
    -TemplatePath "$PSScriptRoot/../tooling/tooling-inventory.template.json" `
    -OutputPath "$PSScriptRoot/../tooling/tooling-inventory.test.json" `
    -Force

if (Test-Path "$PSScriptRoot/../tooling/tooling-inventory.test.json") {
    Write-Host "✅ tooling-inventory.test.json generated successfully" -ForegroundColor Green
    
    # Validate JSON syntax
    try {
        $json = Get-Content "$PSScriptRoot/../tooling/tooling-inventory.test.json" -Raw | ConvertFrom-Json
        Write-Host "✅ JSON syntax valid" -ForegroundColor Green
        Write-Host "   PROJECT_NAME: $($json.project_name)" -ForegroundColor Gray
        Write-Host "   PROJECT_ROOT: $($json.project_root)" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ JSON syntax invalid: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "❌ Failed to generate tooling-inventory.test.json" -ForegroundColor Red
}

Write-Host ""

# Test 3: Expand dashboard.template.html
Write-Host "Testing dashboard.template.html expansion..." -ForegroundColor Cyan
Expand-ConfigTemplate `
    -TemplatePath "$PSScriptRoot/../reports/monitoring/dashboard.template.html" `
    -OutputPath "$PSScriptRoot/../reports/monitoring/dashboard.test.html" `
    -Force

if (Test-Path "$PSScriptRoot/../reports/monitoring/dashboard.test.html") {
    Write-Host "✅ dashboard.test.html generated successfully" -ForegroundColor Green
    
    # Validate HTML has no template variables left
    $content = Get-Content "$PSScriptRoot/../reports/monitoring/dashboard.test.html" -Raw
    if ($content -match '\{\{[A-Z_]+(?::[^}]+)?\}\}') {
        Write-Host "⚠️  Warning: Template variables still present" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ All template variables expanded" -ForegroundColor Green
    }
}
else {
    Write-Host "❌ Failed to generate dashboard.test.html" -ForegroundColor Red
}

Write-Host ""
Write-Host "Template expansion tests complete!" -ForegroundColor Green
