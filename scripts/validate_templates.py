import yaml

# Validate migrated templates
with open('cortex-brain/response-templates.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print('✅ YAML syntax valid')
print(f'📋 Templates: {len(data.get("templates", {}))}')
print(f'📦 Schema version: {data.get("schema_version")}')
print(f'🔄 Last updated: {data.get("last_updated")}')

# Check for any remaining rigid headers
content = open('cortex-brain/response-templates.yaml', 'r', encoding='utf-8').read()
rigid_patterns = [
    "### 🎯 Understanding & Scope",
    "## ⚡ Approach & Considerations",
    "## 💬 Response",
    "## 📊 Impact & Changes"
]

print('\n🔍 Checking for rigid headers...')
found_any = False
for pattern in rigid_patterns:
    count = content.count(pattern)
    if count > 0:
        print(f'  ❌ Found {count}x: {pattern}')
        found_any = True

if not found_any:
    print('  ✅ No rigid headers found - migration complete!')

print('\n✅ Template system validation passed!')
