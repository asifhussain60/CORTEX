#!/usr/bin/env python3
"""Launch CORTEX Admin Dashboard in current terminal."""

import sys
import subprocess
from pathlib import Path

# Main execution
print('🚀 CORTEX Admin Dashboard Launcher')
print('=' * 60)
print('')

# Kill any process using port 8086
print('🧹 Cleaning up port 8086...')
try:
    result = subprocess.run(
        ['powershell', '-Command', 
         "(Get-NetTCPConnection -LocalPort 8086 -ErrorAction SilentlyContinue).OwningProcess | Get-Process | Stop-Process -Force -ErrorAction SilentlyContinue"],
        capture_output=True,
        timeout=3
    )
    print('  ✅ Port 8086 freed\n')
except Exception as e:
    print(f'  ℹ️  Port check skipped: {e}\n')

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from orchestrators.dashboard_launcher import launch_dashboard

print('🌐 Starting dashboard server on port 8086...')
print('')

# Launch dashboard
result = launch_dashboard(port=8086, auto_open=True, source='mock')

if result['success']:
    print(f'✅ Dashboard running at: {result["url"]}')
    print(f'🔌 Port: {result["port"]}')
    print(f'📁 Directory: {result["directory"]}')
    print('')
    print('💡 Dashboard opened in your browser')
    print('🛑 Press Ctrl+C to stop server')
    print('')
    print('⏳ Server running...')
    print('')
    
    # Keep server running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
        print('🛑 Shutting down server...')
        result['server'].stop()
        print('✅ Server stopped')
        print('')
else:
    print(f'❌ Failed to start dashboard: {result.get("error", "Unknown error")}')
    sys.exit(1)

