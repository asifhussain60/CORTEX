"""Analyze SKULL rules from brain-protection-rules.yaml"""
import yaml
from pathlib import Path

skull_file = Path('cortex-brain/brain-protection-rules.yaml')
with open(skull_file, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print('SKULL Rules Inventory:')
print('=' * 60)

rules_found = []
if 'protection_layers' in data:
    for layer in data['protection_layers']:
        layer_name = layer.get('name', 'Unknown')
        print(f'\n[LAYER: {layer_name}]')
        for rule in layer.get('rules', []):
            rule_id = rule.get('rule_id')
            if rule_id:
                rules_found.append(rule_id)
                desc = rule.get('description', 'N/A')
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                severity = rule.get('severity', 'N/A')
                print(f'\n{rule_id}:')
                print(f'  Description: {desc}')
                print(f'  Severity: {severity}')

print(f'\n\n{"="*60}')
print(f'Total Rules Found: {len(rules_found)}')
