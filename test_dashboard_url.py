"""Quick test to check dashboard launcher URL generation"""
from src.orchestrators.dashboard_launcher import launch_dashboard

result = launch_dashboard(auto_open=False, source='luum-fresh', port=8080)
print(f"Success: {result['success']}")
print(f"URL: {result['url']}")
print(f"Message: {result['message']}")
if result['success']:
    result['server'].stop()
