import yaml
import sys

files = [
    'cortex-brain/response-base-components.yaml',
    'cortex-brain/response-template-definitions.yaml',
    'cortex-brain/response-profile-variants.yaml',
    'cortex-brain/response-routing-rules.yaml'
]

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(f'{file}: ✅ Valid ({len(data)} keys)')
    except Exception as e:
        print(f'{file}: ❌ Error - {str(e)}')
        sys.exit(1)

print('\n✅ All YAML files are valid!')
