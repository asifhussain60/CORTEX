
# CORTEX Admin Dashboard Server
$Host.UI.RawUI.WindowTitle = "CORTEX Admin Dashboard - Port 8085"

Write-Host "🚀 CORTEX Admin Dashboard Server" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Add src to Python path and launch
$env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"

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
        print(f'✅ Dashboard running at: {result["url"]}')
        print(f'🔌 Port: {result["port"]}')
        print(f'📁 Directory: {result["directory"]}')
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
            result['server'].stop()
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
