# Launch MkDocs Documentation Server (Option 1)
# Runs in external terminal window without blocking VS Code workflow
# Usage: ./scripts/launch-mkdocs.ps1
# Result: MkDocs server runs at http://127.0.0.1:8000 in new window

param(
    [string]$PythonPath = "C:/Users/asifh/AppData/Local/Programs/Python/Python313/python.exe",
    [int]$Port = 8000,
    [switch]$NoLiveReload = $false
)

# Get project root (CORTEX directory)
$ScriptDir = Split-Path -Parent $PSScriptRoot  # scripts/ -> .
$ProjectRoot = $ScriptDir                       # Current dir is CORTEX root
Set-Location $ProjectRoot

# Verify mkdocs is installed
try {
    & $PythonPath -m mkdocs --version | Out-Null
} catch {
    Write-Error "mkdocs not found. Run: pip install -r requirements.txt"
    exit 1
}

# Build arguments
$Arguments = @("-m", "mkdocs", "serve", "--dev-addr", "127.0.0.1:$Port")
if ($NoLiveReload) {
    $Arguments += "--no-livereload"
}

# Launch in external PowerShell window (detached)
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "powershell.exe"
$ProcessInfo.Arguments = "-NoExit -Command `"Set-Location '$ProjectRoot'; & '$PythonPath' $($Arguments -join ' ')`""
$ProcessInfo.UseShellExecute = $true
$ProcessInfo.CreateNoWindow = $false

$Process = [System.Diagnostics.Process]::Start($ProcessInfo)

Write-Host "✅ MkDocs server launched in external window (PID: $($Process.Id))"
Write-Host "📖 Documentation available at: http://127.0.0.1:$Port"
Write-Host "💡 Press Ctrl+C in the new window to stop the server"
