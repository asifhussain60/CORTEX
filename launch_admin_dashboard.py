#!/usr/bin/env python3
"""Launch CORTEX Admin Dashboard in separate PowerShell window."""

import sys
import subprocess
import time
from pathlib import Path

def kill_python_processes():
    """Kill other Python processes to free ports."""
    print('🧹 Cleaning up Python processes...')
    try:
        import os
        current_pid = os.getpid()
        subprocess.run(
            ['powershell', '-Command', 
             f'Get-Process python -ErrorAction SilentlyContinue | Where-Object {{$_.Id -ne {current_pid}}} | Stop-Process -Force'],
            capture_output=True,
            timeout=3
        )
        print('  ✅ Cleanup complete\n')
        time.sleep(1)
    except Exception as e:
        print(f'  ⚠️  Cleanup skipped: {e}\n')

def create_dashboard_script():
    """Create temporary PowerShell script to launch dashboard."""
    script_content = '''
# CORTEX Admin Dashboard Server
$Host.UI.RawUI.WindowTitle = "CORTEX Admin Dashboard - Port 8085"

Write-Host "🚀 CORTEX Admin Dashboard Server" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Add src to Python path and launch
$env:PYTHONPATH = "$PWD\\src;$env:PYTHONPATH"

python -c @"
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from orchestrators.dashboard_launcher import launch_dashboard

print('🌐 Starting dashboard server...')
print('')

# Launch on first available port 8085-8089
for port in range(8085, 8090):
    result = launch_dashboard(port=port, auto_open=True, source='mock')
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
        break
    else:
        if port < 8089:
            print(f'⚠️  Port {port} unavailable, trying next...')
        else:
            print(f'❌ All ports 8085-8089 are in use')
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

# Kill existing Python processes
kill_python_processes()

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
    print('  - Server runs on port 8085 (or next available)')
    print('')
except Exception as e:
    print(f'  ❌ Failed to launch: {e}')
    sys.exit(1)

print('✅ Launch complete - dashboard is running independently')
print('')
