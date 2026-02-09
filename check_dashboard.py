import json

with open('company/dashboards/repos/ksessions/dashboard-data.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Use cases: {len(data['use_cases'])}")

for i, uc in enumerate(data['use_cases'][:10], 1):
    print(f"{i}. {uc['title']} ({uc.get('category', 'N/A')})")
