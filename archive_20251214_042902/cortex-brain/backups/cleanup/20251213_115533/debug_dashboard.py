#!/usr/bin/env python3
"""Debug dashboard locally to identify tab loading issues."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from orchestrators.dashboard_launcher import launch_dashboard

print('🔍 CORTEX Dashboard Debugger')
print('=' * 60)
print('')
print('Starting dashboard on port 8086...')
print('')

try:
    result = launch_dashboard(port=8086, auto_open=False, source='mock')
    
    if result['success']:
        print(f'✅ Dashboard running at: {result["url"]}')
        print(f'🔌 Port: {result["port"]}')
        print(f'📁 Directory: {result["directory"]}')
        print('')
        print('🌐 Open browser to: http://localhost:8086/ui/index.html?source=mock')
        print('')
        print('💡 Check browser console for JavaScript errors')
        print('🛑 Press Ctrl+C to stop')
        print('')
        print('⏳ Server running...')
        print('')
        
        # Keep running
        import time
        while True:
            time.sleep(1)
    else:
        print(f'❌ Failed to start: {result.get("error", "Unknown error")}')
        sys.exit(1)
        
except KeyboardInterrupt:
    print('')
    print('🛑 Shutting down...')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
