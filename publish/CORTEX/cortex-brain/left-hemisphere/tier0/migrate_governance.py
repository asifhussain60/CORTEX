#!/usr/bin/env python3
"""
CORTEX Governance Migration Tool

Migrates governance rules from YAML and Markdown formats to SQLite database.
Handles both tier-0/rulebook.yaml and governance/rules.md formats.

Usage:
    python migrate_governance.py [--yaml FILE] [--md FILE] [--db FILE]
"""

import argparse
import yaml
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add tier0 to path
sys.path.insert(0, str(Path(__file__).parent))
from governance import GovernanceEngine


def parse_yaml_rules(yaml_path: Path) -> List[Dict[str, Any]]:
    """
    Parse YAML governance rules.
    
    Args:
        yaml_path: Path to YAML file
    
    Returns:
        List of rule dictionaries
    """
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    rules = []
    for idx, rule in enumerate(data.get('rules', []), start=1):
        if rule.get('id') == 'RESERVED':
            continue
        
        rules.append({
            'rule_id': rule.get('id', f'YAML_RULE_{idx}'),
            'rule_number': idx,
            'title': rule.get('id', '').replace('_', ' ').title(),
            'description': rule.get('description', '').strip(),
            'category': rule.get('category', 'OTHER').upper(),
            'severity': rule.get('severity', 'MEDIUM').upper(),
            'rationale': yaml.dump(rule.get('enforcement', {})),
            'examples': rule.get('validation', []),
            'immutable': rule.get('tier') == 0
        })
    
    return rules


def parse_markdown_rules(md_path: Path) -> List[Dict[str, Any]]:
    """
    Parse Markdown governance rules.
    
    Args:
        md_path: Path to rules.md file
    
    Returns:
        List of rule dictionaries
    """
    with open(md_path, 'r') as f:
        content = f.read()
    
    rules = []
    
    # Extract Tier 0 rules (immutable instincts)
    tier0_section = re.search(
        r'## 🎯 Tier 0 Rules.*?(?=##|$)',
        content,
        re.DOTALL
    )
    
    if tier0_section:
        tier0_rules = re.findall(
            r'- ✅ \*\*Rule #(\d+):\*\* (.+?)(?=\n|$)',
            tier0_section.group()
        )
        
        for num, title in tier0_rules:
            rules.append({
                'rule_id': f'TIER0_RULE_{num}',
                'rule_number': int(num),
                'title': title.strip(),
                'description': f'Tier 0 Rule: {title}',
                'category': 'ARCHITECTURE',
                'severity': 'CRITICAL',
                'rationale': 'Immutable instinct - cannot be overridden',
                'examples': [],
                'immutable': True
            })
    
    # Extract numbered rules
    rule_sections = re.finditer(
        r'## RULE #(\d+): (.+?)\n\n```yaml\n(.*?)\n```',
        content,
        re.DOTALL
    )
    
    for match in rule_sections:
        num, title, yaml_content = match.groups()
        rule_num = int(num)
        
        try:
            rule_data = yaml.safe_load(yaml_content)
            
            rules.append({
                'rule_id': rule_data.get('rule_id', f'RULE_{num}'),
                'rule_number': rule_num,
                'title': title.strip(),
                'description': str(rule_data.get('validation', {}) or rule_data.get('requirements', {})),
                'category': _categorize_rule(title, rule_data),
                'severity': rule_data.get('severity', 'MEDIUM').upper(),
                'rationale': str(rule_data.get('principles', {})),
                'examples': list(rule_data.get('examples', {}).values()) if isinstance(rule_data.get('examples'), dict) else rule_data.get('examples', []),
                'immutable': False
            })
        except yaml.YAMLError:
            print(f"Warning: Could not parse YAML for Rule #{num}")
            continue
    
    return rules


def _categorize_rule(title: str, rule_data: Dict) -> str:
    """Categorize a rule based on title and content."""
    title_lower = title.lower()
    
    if 'test' in title_lower or 'tdd' in title_lower:
        return 'TESTING'
    elif 'data' in title_lower or 'brain' in title_lower or 'database' in title_lower:
        return 'DATA'
    elif 'workflow' in title_lower or 'checkpoint' in title_lower:
        return 'WORKFLOW'
    elif 'communication' in title_lower or 'interface' in title_lower:
        return 'COMMUNICATION'
    elif 'architecture' in title_lower or 'design' in title_lower:
        return 'ARCHITECTURE'
    
    scope = rule_data.get('scope', '').lower()
    if 'test' in scope:
        return 'TESTING'
    elif 'brain' in scope or 'data' in scope:
        return 'DATA'
    
    return 'OTHER'


def migrate_to_database(rules: List[Dict[str, Any]], db_path: Path) -> None:
    """
    Migrate rules to SQLite database.
    
    Args:
        rules: List of rule dictionaries
        db_path: Path to database file
    """
    with GovernanceEngine(str(db_path)) as engine:
        for rule in rules:
            try:
                engine.add_rule(rule)
                print(f"✅ Migrated: Rule #{rule['rule_number']} - {rule['title']}")
            except sqlite3.IntegrityError:
                print(f"⚠️  Skipped (already exists): Rule #{rule['rule_number']}")


def main():
    parser = argparse.ArgumentParser(description='Migrate CORTEX governance rules to SQLite')
    parser.add_argument(
        '--yaml',
        type=Path,
        help='Path to YAML rulebook file'
    )
    parser.add_argument(
        '--md',
        type=Path,
        help='Path to Markdown rules file'
    )
    parser.add_argument(
        '--db',
        type=Path,
        default=Path('cortex-brain.db'),
        help='Path to output SQLite database (default: cortex-brain.db)'
    )
    
    args = parser.parse_args()
    
    all_rules = []
    
    if args.yaml:
        print(f"📖 Parsing YAML rules from: {args.yaml}")
        all_rules.extend(parse_yaml_rules(args.yaml))
    
    if args.md:
        print(f"📖 Parsing Markdown rules from: {args.md}")
        all_rules.extend(parse_markdown_rules(args.md))
    
    if not all_rules:
        print("❌ No rules found. Please specify --yaml or --md.")
        return 1
    
    print(f"\n📊 Found {len(all_rules)} rules to migrate")
    print(f"💾 Migrating to database: {args.db}\n")
    
    migrate_to_database(all_rules, args.db)
    
    print(f"\n✅ Migration complete! Rules stored in: {args.db}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
