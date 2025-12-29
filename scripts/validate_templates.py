import yaml

# Validate CORTEX 4.0 templates
with open('cortex-brain/response-templates-v4.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print('✅ YAML syntax valid')
print(f' Schema version: {data.get("schema_version")}')
print(f'🔄 Last updated: {data.get("last_updated")}')
print(f'🏗️  Architecture: {data.get("architecture")}')

# Check for CORTEX 4.0 adaptive format compliance
content = open('cortex-brain/response-templates-v4.yaml', 'r', encoding='utf-8').read()

print('\n🔍 Validating CORTEX 4.0 adaptive minimalism...')
checks = {
    'routing': 'routing' in data,
    'sections': 'sections' in data,
    'tier1_instant': 'tier1_instant' in data.get('routing', {}),
    'tier2_focused': 'tier2_focused' in data.get('routing', {}),
    'tier3_structured': 'tier3_structured' in data.get('routing', {}),
    'tier4_comprehensive': 'tier4_comprehensive' in data.get('routing', {})
}

all_passed = True
for check, passed in checks.items():
    status = '✅' if passed else '❌'
    print(f'  {status} {check}')
    if not passed:
        all_passed = False

if all_passed:
    print('\n✅ CORTEX 4.0 template system validation passed!')
else:
    print('\n❌ CORTEX 4.0 validation failed - missing required components')
    exit(1)
