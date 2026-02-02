# Company Domain Template - FINANCIAL-SERVICES Example
# Copy this template and customize for your company domain
# Authority: AC-HYBRID-KNOWLEDGE-001
# Date: 2026-01-26

# INSTRUCTIONS:
# 1. Copy this file to company/domains/YOUR-DOMAIN/README.md
# 2. Create YAML files in company/domains/YOUR-DOMAIN/ for domain rules
# 3. Register domain in .knowledge-index.yaml under company_knowledge
# 4. Commit and push: `git add company/domains/` && `git push`
# 5. Team members will auto-sync on next `git pull`

## Domain Name
YOUR-DOMAIN (e.g., FINANCIAL-SERVICES, PRODUCT-ENGINEERING)

## Purpose
Define company-specific rules, patterns, and constraints for this domain.

## Example YAMLs in This Folder
Create YAML files following this structure:

### rules.yaml
```yaml
domain: YOUR-DOMAIN
metadata:
  version: "1.0"
  owner: "Your Team"
  
rules:
  - id: YOUR-DOMAIN-001
    name: "Rule Name"
    description: "What this rule enforces"
    applies_to: [IMPLEMENT, FIX]
    content: "Detailed rule content..."
```

### patterns.yaml
```yaml
domain: YOUR-DOMAIN
patterns:
  - name: "Pattern Name"
    description: "How to apply this pattern"
    applicable_when: "Specific conditions"
    implementation_guide: "Step-by-step instructions"
```

## Registration
Add to `.knowledge-index.yaml`:
```yaml
company_knowledge:
  domains:
    - name: YOUR-DOMAIN
      path: "company/domains/your-domain/"
      description: "Your domain description"
      owner: "Your Team"
      priority: HIGH  # or MEDIUM/LOW
      status: ACTIVE
```

## Composition Rules
Add to `.knowledge-synthesis-rules.yaml` if needed:
```yaml
synthesis_rules:
  - id: your-domain-synthesis
    name: "Your Domain Synthesis"
    cortex_domain: ARCHITECTURE  # or other CORTEX domain
    company_domains: [YOUR-DOMAIN]
    composition: overlay  # or merge
    priority: HIGH
    applicable_intents: [IMPLEMENT, FIX]
```

## Questions?
Refer to `.knowledge-index.yaml` and `.knowledge-synthesis-rules.yaml` for more examples.
