#!/usr/bin/env python3
"""Launch CORTEX Admin Dashboard in separate PowerShell window."""

import sys
import subprocess
from pathlib import Path

def create_dashboard_script():
    """Create PowerShell script to launch dashboard in new window."""
    script_content = '''
# CORTEX Admin Dashboard Server
$Host.UI.RawUI.WindowTitle = "CORTEX Admin Dashboard - Port 8086"

Write-Host "🚀 CORTEX Admin Dashboard Server" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Kill only dashboard processes (check port 8086)
Write-Host "🧹 Cleaning up existing dashboard on port 8086..." -ForegroundColor Yellow
try {
    $netstat = netstat -ano | Select-String ":8086" | Select-String "LISTENING"
    if ($netstat) {
        $pid = ($netstat -split '\\s+')[-1]
        if ($pid -match '^\\d+$') {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Write-Host "  ✅ Port 8086 freed" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✅ Port 8086 is available" -ForegroundColor Green
    }
} catch {
    Write-Host "  ℹ️  Cleanup skipped" -ForegroundColor Gray
}
Write-Host ""

# Add src to Python path and launch
$env:PYTHONPATH = "$PWD\\src;$env:PYTHONPATH"

python -c @"
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from orchestrators.dashboard_launcher import launch_dashboard

print('🌐 Starting dashboard server on port 8086...')
print('')

# Launch on fixed port 8086
result = launch_dashboard(port=8086, auto_open=True, source='mock')

if result['success']:
    dashboard_url = result['url']
    dashboard_port = result['port']
    dashboard_dir = result['directory']
    server_instance = result['server']
    
    print(f'✅ Dashboard running at: {dashboard_url}')
    print(f'🔌 Port: {dashboard_port}')
    print(f'📁 Directory: {dashboard_dir}')
    print('')
    print('💡 Dashboard opened in your browser')
    print('🛑 Press Ctrl+C to stop server')
    print('')
    print('⏳ Server running...')
    
    # Keep server running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
        print('🛑 Shutting down server...')
        server_instance.stop()
        print('✅ Server stopped')
else:
    print(f'❌ Failed to start dashboard: {result.get(\"error\", \"Unknown error\")}')
    input('Press Enter to close...')
    sys.exit(1)
"@

Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'''
    
    script_path = Path('launch_dashboard_server.ps1')
    script_path.write_text(script_content, encoding='utf-8')
    return script_path

# Main execution
print('🚀 CORTEX Admin Dashboard Launcher')
print('=' * 60)
print('')

# Create dashboard script
print('📝 Creating launch script...')
script_path = create_dashboard_script()
print(f'  ✅ Script created: {script_path}')
print('')

# Launch in new PowerShell window
print('🪟  Opening dashboard in new PowerShell window...')
try:
    subprocess.Popen(
        ['powershell', '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', str(script_path)],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print('  ✅ Dashboard server started in separate window')
    print('')
    print('💡 Tips:')
    print('  - Dashboard will open automatically in your browser')
    print('  - Close the PowerShell window to stop the server')
    print('  - Server runs on port 8086')
    print('')
except Exception as e:
    print(f'  ❌ Failed to launch: {e}')
    sys.exit(1)

print('✅ Launch complete - dashboard is running independently')
print('')
