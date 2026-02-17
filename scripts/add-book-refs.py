#!/usr/bin/env python3
"""Add book_reference field to all CORE rules in core-rules.yaml"""

import yaml
from pathlib import Path

# Book reference mappings
BOOK_REFS = {
    "CORE-001": "Good to Great by Jim Collins",
    "CORE-002": "Essentialism: The Disciplined Pursuit of Less by Greg McKeown",
    "CORE-004": "The Elements of Style by Strunk & White",
    "CORE-005": "The Pragmatic Programmer by Andrew Hunt & David Thomas",
    "CORE-006": "The Lean Startup by Eric Ries",
    "CORE-008": "Test Driven Development: By Example by Kent Beck",
    "CORE-011": "Domain Modeling Made Functional by Scott Wlaschin",
    "CORE-012": "Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin",
    "CORE-013": "Release It!: Design and Deploy Production-Ready Software by Michael Nygard",
    "CORE-017": "Good to Great by Jim Collins",
    "CORE-018": "Building Microservices by Sam Newman",
    "CORE-019": "The Pragmatic Programmer by Andrew Hunt & David Thomas",
    "CORE-020": "Clean Architecture by Robert C. Martin",
    "CORE-024": "The Rails Way by Obie Fernandez",
    "CORE-025": "The Pragmatic Programmer by Andrew Hunt & David Thomas",
    "CORE-026": "Site Reliability Engineering by Google (Betsy Beyer et al.)",
    "CORE-027": "Principles: Life and Work by Ray Dalio",
    "CORE-028": "The Pragmatic Programmer by Andrew Hunt & David Thomas",
    "CORE-029": "The DevOps Handbook by Gene Kim, Jez Humble, Patrick Debois, John Willis",
    "CORE-030": "Good to Great by Jim Collins",
    "CORE-032": "Good to Great by Jim Collins",
    "CORE-034": "Measure What Matters by John Doerr",
    "CORE-035": "The Phoenix Project: A Novel About IT, DevOps, and Helping Your Business Win by Gene Kim",
    "CORE-038": "Domain-Driven Design by Eric Evans",
    "CORE-039": "The Lean Startup by Eric Ries",
    "CORE-040": "Building Evolutionary Architectures by Neal Ford, Rebecca Parsons, Patrick Kua",
    "CORE-041": "Release It!: Design and Deploy Production-Ready Software by Michael Nygard",
    "CORE-042": "The Goal: A Process of Ongoing Improvement by Eliyahu Goldratt",
    "AC-PERMANENT-FIX-006": "Lean Software Development by Mary & Tom Poppendieck",
}

def main():
    yaml_file = Path("cortex_intelligence/tier0/governance/core-rules.yaml")
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    updated = 0
    for rule in data['rules']:
        rule_id = rule.get('rule_id', '')
        if rule_id in BOOK_REFS and 'book_reference' not in rule:
            # Insert book_reference after principle
            rule['book_reference'] = BOOK_REFS[rule_id]
            updated += 1
            print(f"✅ Added book reference to {rule_id}")
    
    # Write back with proper formatting
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print(f"\n✅ Updated {updated} rules with book references")

if __name__ == "__main__":
    main()
